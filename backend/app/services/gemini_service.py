import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def analyze_application(self, resume_text: str, job_description: str, job_title: str, company_name: str) -> dict:
        """
        Analyze resume against job description using Gemini
        Returns: {match_score, matching_skills, missing_skills, suggestions}
        """
        prompt = f"""
You are an expert career advisor. Analyze this resume against the job description and provide insights.

**Job Title:** {job_title}
**Company:** {company_name}

**Job Description:**
{job_description}

**Resume:**
{resume_text}

Provide your analysis in this EXACT JSON format (no markdown, just raw JSON):
{{
  "match_score": <number between 0-100>,
  "matching_skills": ["skill1", "skill2", "skill3"],
  "missing_skills": ["skill1", "skill2", "skill3"],
  "suggestions": "Brief paragraph with 3-4 specific actionable suggestions to improve the resume for this role."
}}

Be specific and practical. Focus on technical skills, experience alignment, and resume improvements.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            result_text = result_text.strip()
            
            # Parse JSON
            import json
            analysis = json.loads(result_text)
            
            logger.info(f"AI analysis completed for {company_name} - {job_title}")
            return analysis
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                "match_score": 0,
                "matching_skills": [],
                "missing_skills": [],
                "suggestions": f"Analysis failed: {str(e)}"
            }

gemini_service = GeminiService()