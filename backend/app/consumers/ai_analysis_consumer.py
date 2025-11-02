from kafka import KafkaConsumer
import json
import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.application import Application
from app.models.resume import Resume
from app.models.ai_analysis import AIAnalysis, AnalysisStatus
from app.services.gemini_service import gemini_service
from app.services.redis_service import redis_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_application_created(event_data: dict, db: Session):
    """Process application-created event and run AI analysis"""
    try:
        application_id = event_data.get("application_id")
        user_id = event_data.get("user_id")
        
        logger.info(f"Processing application {application_id}")
        
        # Fetch application
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            logger.error(f"Application {application_id} not found")
            return
        
        # Check cache for active resume first
        cached_resume = redis_service.get_cached_active_resume(user_id)
        
        if cached_resume:
            resume_id = cached_resume.get('id')
            resume_content = cached_resume.get('content')
            logger.info(f"Using cached resume for user {user_id}")
        else:
            # Fetch from database
            resume = db.query(Resume).filter(
                Resume.user_id == user_id,
                Resume.is_active == True
            ).first()
            
            if not resume:
                logger.warning(f"No active resume found for user {user_id}")
                analysis = AIAnalysis(
                    application_id=application_id,
                    resume_id=None,
                    analysis_status=AnalysisStatus.failed,
                    error_message="No active resume found"
                )
                db.add(analysis)
                db.commit()
                return
            
            resume_id = str(resume.id)
            resume_content = resume.content
            
            # Cache the resume
            redis_service.cache_active_resume(user_id, {
                'id': resume_id,
                'content': resume_content
            })
        
        # Create pending analysis
        analysis = AIAnalysis(
            application_id=application_id,
            resume_id=resume_id,
            analysis_status=AnalysisStatus.pending
        )
        db.add(analysis)
        db.commit()
        
        # Check if job description exists
        if not application.job_description:
            logger.warning(f"No job description for application {application_id}")
            analysis.analysis_status = AnalysisStatus.failed
            analysis.error_message = "No job description provided"
            db.commit()
            return
        
        # Check cache for AI analysis
        cached_analysis = redis_service.get_cached_ai_analysis(resume_id, application.job_description)
        
        if cached_analysis:
            # Use cached analysis
            logger.info(f"Using cached AI analysis for application {application_id}")
            result = cached_analysis
        else:
            # Run AI analysis
            logger.info(f"Running AI analysis for application {application_id}")
            result = gemini_service.analyze_application(
                resume_text=resume_content,
                job_description=application.job_description,
                job_title=application.job_title,
                company_name=application.company_name
            )
            
            # Cache the result
            redis_service.cache_ai_analysis(resume_id, application.job_description, result)
        
        # Update analysis with results
        analysis.match_score = result.get("match_score")
        analysis.matching_skills = {"skills": result.get("matching_skills", [])}
        analysis.missing_skills = {"skills": result.get("missing_skills", [])}
        analysis.suggestions = result.get("suggestions")
        analysis.analysis_status = AnalysisStatus.completed
        
        from datetime import datetime
        analysis.analyzed_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Analysis completed for application {application_id}")
        
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        db.rollback()

def start_consumer():
    """Start Kafka consumer for AI analysis"""
    consumer = KafkaConsumer(
        'application-created',
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='ai-analysis-worker',
        auto_offset_reset='earliest'
    )
    
    logger.info("AI Analysis Consumer started. Listening for events...")
    
    for message in consumer:
        event_data = message.value
        logger.info(f"Received event: {event_data}")
        
        db = SessionLocal()
        try:
            process_application_created(event_data, db)
        finally:
            db.close()

if __name__ == "__main__":
    start_consumer()