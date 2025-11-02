from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.application import Application, ApplicationStatus
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatusUpdate,
    ApplicationResponse,
    ApplicationListResponse
)
from app.services.kafka_producer import kafka_producer
from app.schemas.ai_analysis import AIAnalysisResponse

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new job application"""
    new_application = Application(
        user_id=current_user.id,
        company_name=data.company_name,
        job_title=data.job_title,
        job_url=data.job_url,
        job_description=data.job_description,
        location=data.location,
        salary_range=data.salary_range,
        date_applied=data.date_applied,
        notes=data.notes,
        status=ApplicationStatus.applied
    )
    
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    
    # TODO: Publish Kafka event for AI analysis
    kafka_producer.publish_event("application-created", {
        "application_id": str(new_application.id),
        "user_id": str(current_user.id),
        "company_name": new_application.company_name,
        "job_title": new_application.job_title,
        "job_description": new_application.job_description,
        "event_type": "application_created"
    })
    
    return new_application

@router.get("", response_model=List[ApplicationListResponse])
def list_applications(
    status_filter: ApplicationStatus | None = Query(None, alias="status"),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all applications for current user with optional filters"""
    query = db.query(Application).filter(Application.user_id == current_user.id)
    
    # Apply filters
    if status_filter:
        query = query.filter(Application.status == status_filter)
    if date_from:
        query = query.filter(Application.date_applied >= date_from)
    if date_to:
        query = query.filter(Application.date_applied <= date_to)
    
    applications = query.order_by(Application.date_applied.desc()).all()
    return applications

@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single application by ID"""
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application

@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: UUID,
    data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an application"""
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update fields if provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    
    return application

@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: UUID,
    data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update only the status of an application"""
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    application.status = data.status
    db.commit()
    db.refresh(application)
    
    return application

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an application"""
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    db.delete(application)
    db.commit()
    
    return None

@router.get("/{application_id}/analysis", response_model=AIAnalysisResponse)
def get_application_analysis(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI analysis for an application"""
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if not application.ai_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not yet available"
        )
    
    return application.ai_analysis