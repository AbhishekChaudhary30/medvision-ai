import logging
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.model_registry import ModelVersion

logger = logging.getLogger(__name__)

class ModelService:
    """Service to handle model registry operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def get_production_model(self) -> ModelVersion | None:
        """Fetch the currently active production model."""
        stmt = select(ModelVersion).where(ModelVersion.is_active_production == True)
        return self.db.scalars(stmt).first()

    def get_model_by_version(self, version_tag: str) -> ModelVersion | None:
        """Fetch a specific model version."""
        stmt = select(ModelVersion).where(ModelVersion.version_tag == version_tag)
        return self.db.scalars(stmt).first()

    def register_model(self, version_tag: str, architecture: str, artifact_path: str, metrics: dict = None, **kwargs) -> ModelVersion:
        """Register a new model version."""
        if self.get_model_by_version(version_tag):
            raise ValueError(f"Model version {version_tag} already exists.")
            
        model_version = ModelVersion(
            version_tag=version_tag,
            architecture=architecture,
            artifact_path=artifact_path,
            val_loss=metrics.get("val_loss") if metrics else None,
            val_accuracy=metrics.get("val_accuracy") if metrics else None,
            val_auroc=metrics.get("val_auroc") if metrics else None,
            val_f1=metrics.get("val_f1") if metrics else None,
            **kwargs
        )
        self.db.add(model_version)
        self.db.commit()
        self.db.refresh(model_version)
        logger.info(f"Registered new model version: {version_tag}")
        return model_version

    def promote_to_production(self, version_tag: str) -> ModelVersion:
        """Promote a model to production, demoting the previous one."""
        new_prod_model = self.get_model_by_version(version_tag)
        if not new_prod_model:
            raise ValueError(f"Model version {version_tag} not found.")
            
        if new_prod_model.status not in ["VALIDATED", "STAGING", "PRODUCTION"]:
            logger.warning(f"Promoting {version_tag} to production without prior validation.")
            
        # Demote current production models
        current_prods = self.db.scalars(select(ModelVersion).where(ModelVersion.is_active_production == True)).all()
        for prod in current_prods:
            prod.is_active_production = False
            prod.status = "RETIRED"
            
        # Promote new
        new_prod_model.is_active_production = True
        new_prod_model.status = "PRODUCTION"
        
        self.db.commit()
        self.db.refresh(new_prod_model)
        logger.info(f"Promoted {version_tag} to PRODUCTION.")
        return new_prod_model
