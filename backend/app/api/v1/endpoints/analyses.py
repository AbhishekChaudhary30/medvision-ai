"""Analyses and Prediction endpoints."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.analysis import Analysis, AnalysisArtifact
from app.models.user import User, UserRole
from app.schemas.analysis import (
    AnalysisListResponse,
    AnalysisResponse,
    ExplanationRequest,
    ReviewRequest,
)
from app.services.ml_service import process_and_predict, process_explainability, save_upload_file
from app.services.report_service import generate_analysis_report

router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def submit_analysis(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload an image and run the ML prediction (No explainability yet)."""
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only JPEG and PNG are allowed."
        )
        
    # We can't strictly enforce max size easily in pure FastAPI without reading, 
    # but we can rely on standard middleware or web server limits for production.
    
    # Save the file securely via the ML service
    saved_path = save_upload_file(file)
    
    try:
        # Run inference via ML service
        result_dict = process_and_predict(saved_path, str(current_user.id))
    except ValueError as e:
        # Clean up file on failure
        saved_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference engine failed"
        ) from None
        
    # Persist the analysis
    analysis = Analysis(
        user_id=current_user.id,
        **result_dict
    )
    db.add(analysis)
    
    # Persist the artifact reference
    artifact = AnalysisArtifact(
        analysis=analysis,
        artifact_type="original_image",
        file_path=str(saved_path.as_posix()),
        content_type=file.content_type
    )
    db.add(artifact)
    
    db.commit()
    db.refresh(analysis)
    
    return analysis


@router.get("", response_model=AnalysisListResponse)
def list_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    """List analyses history. Users see own, Admins/Reviewers can see all."""
    query = db.query(Analysis)
    
    if current_user.role == UserRole.USER:
        query = query.filter(Analysis.user_id == current_user.id)
        
    total = query.count()
    items = query.order_by(Analysis.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": skip
    }


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific analysis detail."""
    analysis = db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    # Object-level authorization
    if current_user.role == UserRole.USER and analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this analysis")
        
    return analysis


@router.post("/{analysis_id}/explain", response_model=AnalysisResponse)
def explain_analysis(
    analysis_id: UUID,
    request: ExplanationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate explainability artifacts for a previous analysis."""
    analysis = db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    if current_user.role == UserRole.USER and analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this analysis")
        
    # Find original image
    original_artifact = next((a for a in analysis.artifacts if a.artifact_type == "original_image"), None)
    if not original_artifact:
        raise HTTPException(status_code=404, detail="Original image artifact not found")
        
    try:
        explanation_result = process_explainability(
            file_path=Path(original_artifact.file_path),
            target_class=analysis.predicted_class_index,
            method=request.method
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Explainability engine failed") from None
        
    if not explanation_result:
        raise HTTPException(status_code=500, detail="Explainability method returned None")
        
    # Update analysis record
    analysis.explanation_method = explanation_result["method"]
    
    # Add new artifact for the overlay
    overlay_artifact = AnalysisArtifact(
        analysis=analysis,
        artifact_type="gradcam_overlay",
        file_path=f"base64:{explanation_result['overlay_image_base64'][:20]}...", # Just store a reference or base64 marker
        content_type="image/jpeg"
    )
    db.add(overlay_artifact)
    db.commit()
    db.refresh(analysis)
    
    # We don't return the giant base64 blob in the normal response by default 
    # to keep it lightweight, unless specifically requested. But we could include 
    # it in a custom response if needed. For now we just return the updated analysis.
    return analysis


@router.post("/{analysis_id}/review", response_model=AnalysisResponse)
def review_analysis(
    analysis_id: UUID,
    request: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a human review for an analysis. Requires REVIEWER or ADMIN role."""
    if current_user.role not in [UserRole.REVIEWER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to perform reviews")
        
    analysis = db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    analysis.review_status = request.review_status
    analysis.reviewer_notes = request.reviewer_notes
    analysis.reviewer_id = current_user.id
    analysis.reviewed_at = datetime.now(UTC)
    
    db.commit()
    db.refresh(analysis)
    
    return analysis


@router.get("/{analysis_id}/report")
def download_analysis_report(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download a PDF report for a given analysis."""
    analysis = db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    if current_user.role == UserRole.USER and analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this analysis report")
        
    pdf_bytes = generate_analysis_report(analysis)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=analysis_{analysis_id}.pdf"
        }
    )
