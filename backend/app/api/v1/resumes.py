from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import PyPDF2
import io
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeListResponse
from app.services.redis_service import redis_service

router = APIRouter(prefix="/resumes", tags=["Resumes"])

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload resume PDF and extract text"""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Read file
    pdf_content = await file.read()
    
    # Check file size (5MB limit)
    if len(pdf_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum 5MB allowed"
        )
    
    # Extract text from PDF
    resume_text = extract_text_from_pdf(pdf_content)
    
    if not resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from PDF. Please ensure it's a valid PDF with readable text"
        )
    
    # Deactivate all other resumes
    db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_active": False})
    
    # Create new resume
    new_resume = Resume(
        user_id=current_user.id,
        content=resume_text,
        file_url=file.filename,  # Store filename for now
        is_active=True
    )
    
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    redis_service.invalidate_user_resume_cache(str(current_user.id))
    
    return new_resume

@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def create_resume(
    data: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create/upload a resume"""
    # Deactivate all other resumes
    db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_active": False})
    
    new_resume = Resume(
        user_id=current_user.id,
        content=data.content,
        file_url=data.file_url,
        is_active=True
    )
    
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    redis_service.invalidate_user_resume_cache(str(current_user.id))
    
    return new_resume

@router.get("", response_model=List[ResumeListResponse])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all resumes for current user"""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    return resumes

@router.get("/active", response_model=ResumeResponse)
def get_active_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current active resume"""
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active resume found"
        )
    
    return resume

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    db.delete(resume)
    db.commit()
    
    return None