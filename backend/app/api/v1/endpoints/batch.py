from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
import json

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.ml_service import process_and_predict, save_upload_file
from app.models.analysis import Analysis, AnalysisArtifact

router = APIRouter()

# Simple in-memory dict for prototype batch tracking (use Redis in full prod)
BATCH_JOBS = {}

def process_batch_background(batch_id: str, files: List[UploadFile], user_id: str, db: Session):
    success = 0
    failed = 0
    results = []

    for file in files:
        try:
            saved_path = save_upload_file(file)
            result_dict = process_and_predict(saved_path, str(user_id))
            
            # Persist
            analysis = Analysis(user_id=user_id, **result_dict)
            db.add(analysis)
            
            artifact = AnalysisArtifact(
                analysis=analysis, artifact_type="original_image", file_path=str(saved_path.as_posix()), content_type=file.content_type
            )
            db.add(artifact)
            db.commit()
            
            success += 1
            results.append({"filename": file.filename, "status": "SUCCESS", "analysis_id": str(analysis.id)})
        except Exception as e:
            failed += 1
            results.append({"filename": file.filename, "status": "FAILED", "error": str(e)})

    BATCH_JOBS[batch_id]["status"] = "COMPLETED"
    BATCH_JOBS[batch_id]["processed"] = len(files)
    BATCH_JOBS[batch_id]["success"] = success
    BATCH_JOBS[batch_id]["failed"] = failed
    BATCH_JOBS[batch_id]["results"] = results


@router.post("")
def submit_batch_analysis(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a batch of images for analysis."""
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided.")
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 files per batch.")
        
    batch_id = str(uuid4())
    
    BATCH_JOBS[batch_id] = {
        "status": "PROCESSING",
        "total_images": len(files),
        "processed": 0,
        "success": 0,
        "failed": 0,
        "results": []
    }
    
    background_tasks.add_task(process_batch_background, batch_id, files, current_user.id, db)
    
    return {
        "batch_id": batch_id,
        "status": "PROCESSING",
        "total_images": len(files),
        "message": "Batch submitted successfully and is processing in the background."
    }

@router.get("/{batch_id}")
def get_batch_status(batch_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get status of a batch job."""
    if batch_id not in BATCH_JOBS:
        raise HTTPException(status_code=404, detail="Batch job not found.")
        
    return BATCH_JOBS[batch_id]
