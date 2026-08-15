from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.services.model_service import ModelService

router = APIRouter()

@router.get("")
def list_models(db: Session = Depends(get_db)):
    """List all registered models. Available to all authenticated users."""
    model_service = ModelService(db)
    # Simple direct query for MVP
    from app.models.model_registry import ModelVersion
    from sqlalchemy import select
    models = db.scalars(select(ModelVersion).order_by(ModelVersion.created_at.desc())).all()
    return models

@router.get("/production")
def get_production_model(db: Session = Depends(get_db)):
    """Get the active production model."""
    model_service = ModelService(db)
    model = model_service.get_production_model()
    if not model:
        raise HTTPException(status_code=404, detail="No production model active.")
    return model

@router.get("/{version_tag}")
def get_model(version_tag: str, db: Session = Depends(get_db)):
    """Get specific model version."""
    model_service = ModelService(db)
    model = model_service.get_model_by_version(version_tag)
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found.")
    return model

@router.post("/{version_tag}/promote", status_code=status.HTTP_200_OK)
def promote_model(
    version_tag: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Promote a model to production (Admins only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can promote models.")
        
    model_service = ModelService(db)
    try:
        model = model_service.promote_to_production(version_tag)
        return model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
