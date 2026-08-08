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
    
    artifacts: list[AnalysisArtifactResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class AnalysisListResponse(BaseModel):
    """Paginated list of analyses."""
    items: list[AnalysisResponse]
    total: int
    limit: int
    offset: int
