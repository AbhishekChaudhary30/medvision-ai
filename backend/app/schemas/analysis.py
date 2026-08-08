"""Analysis schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnalysisArtifactResponse(BaseModel):
    """Schema for associated artifacts like images or heatmaps."""

    id: UUID
    artifact_type: str
    file_path: str
    content_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExplanationRequest(BaseModel):
    """Schema for requesting explainability."""

    method: str = Field(default="gradcam", description="Method for explainability: gradcam or gradcam++")


class AnalysisResponse(BaseModel):
    """Schema for returning analysis results."""

    id: UUID
    user_id: UUID
    model_version: str
    model_architecture: str
    predicted_class: str
    predicted_class_index: int
    confidence: float
    probability_normal: float
    probability_pneumonia: float
    threshold: float
    uncertainty_status: str
    entropy: float
    margin: float
    calibration_status: str
    inference_time: float
    explanation_method: str | None = None
    created_at: datetime

    review_status: str
    reviewer_id: UUID | None = None
    reviewer_notes: str | None = None
    reviewed_at: datetime | None = None

    artifacts: list[AnalysisArtifactResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ReviewRequest(BaseModel):
    """Schema for submitting a review."""

    review_status: str = Field(..., description="Status of the review, e.g., REVIEWED, FLAGGED")
    reviewer_notes: str | None = Field(None, description="Optional notes from the reviewer")


class AnalysisListResponse(BaseModel):
    """Paginated list of analyses."""

    items: list[AnalysisResponse]
    total: int
    limit: int
    offset: int
