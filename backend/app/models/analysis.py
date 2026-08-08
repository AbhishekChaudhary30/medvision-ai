"""Analysis and AnalysisArtifact models."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String

if TYPE_CHECKING:
    from app.models.user import User
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Analysis(Base):
    """Represents a single image analysis request and its prediction."""
    
    __tablename__ = "analyses"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    model_architecture: Mapped[str] = mapped_column(String, nullable=False)
    
    predicted_class: Mapped[str] = mapped_column(String, nullable=False)
    predicted_class_index: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    probability_normal: Mapped[float] = mapped_column(Float, nullable=False)
    probability_pneumonia: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    
    uncertainty_status: Mapped[str] = mapped_column(String, nullable=False)
    entropy: Mapped[float] = mapped_column(Float, nullable=False)
    margin: Mapped[float] = mapped_column(Float, nullable=False)
    calibration_status: Mapped[str] = mapped_column(String, nullable=False)
    
    inference_time: Mapped[float] = mapped_column(Float, nullable=False)
    explanation_method: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Review fields
    review_status: Mapped[str] = mapped_column(String, default="NOT_REVIEWED", nullable=False)
    reviewer_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    reviewer_notes: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="analyses")
    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewer_id])
    artifacts: Mapped[list["AnalysisArtifact"]] = relationship(
        "AnalysisArtifact", back_populates="analysis", cascade="all, delete-orphan"
    )


class AnalysisArtifact(Base):
    """Represents file artifacts associated with an analysis (e.g., input image, heatmap)."""
    
    __tablename__ = "analysis_artifacts"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    analysis_id: Mapped[UUID] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), index=True, nullable=False)
    
    artifact_type: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "original_image", "gradcam_overlay"
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="artifacts")
