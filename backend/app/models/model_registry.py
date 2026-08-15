from datetime import UTC, datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, Float, Integer, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class ModelVersion(Base):
    """Represents a trained model version in the registry."""
    __tablename__ = "model_versions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    version_tag: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    architecture: Mapped[str] = mapped_column(String, nullable=False)
    
    # Status can be EXPERIMENTAL, VALIDATED, STAGING, PRODUCTION, RETIRED
    status: Mapped[str] = mapped_column(String, default="EXPERIMENTAL", nullable=False)
    is_active_production: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metrics
    val_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    val_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    val_auroc: Mapped[float | None] = mapped_column(Float, nullable=True)
    val_f1: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Metadata and configurations
    hyperparameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    calibration_temp: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # File references
    artifact_path: Mapped[str] = mapped_column(String, nullable=False)
    mlflow_run_id: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
