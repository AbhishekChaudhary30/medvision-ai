"""Data structures for inference and explainability results."""

from dataclasses import dataclass


@dataclass
class ExplanationResult:
    """Encapsulates explainability outputs (Grad-CAM)."""

    heatmap: list[list[float]]  # 2D array of normalized floats [0, 1]
    overlay_image_base64: str  # Base64 encoded JPEG/PNG for frontend
    method: str  # e.g., "gradcam" or "gradcam++"
    target_layer: str


@dataclass
class InferenceResult:
    """Encapsulates the final prediction and uncertainty metrics."""

    sample_id: str
    class_name: str
    class_index: int
    probability: float
    confidence_score: float  # Could be max probability or calibrated confidence
    entropy: float  # Predictive entropy (uncertainty indicator)
    margin: float  # Difference between top 2 class probabilities
    explanation: ExplanationResult | None = None
    processing_time_ms: float = 0.0
