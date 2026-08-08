"""ML Service adapter bridging Phase 4 engine with API layer."""

import logging
import shutil
import uuid
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from ml.inference.bundle import ModelBundle
from ml.inference.engine import InferenceEngine

logger = logging.getLogger(__name__)

# Singleton instance of the engine
_engine: InferenceEngine | None = None

UPLOAD_DIR = Path("data/uploads")
ARTIFACT_DIR = Path("data/artifacts")

def initialize_engine(checkpoint_dir: str = "models/checkpoints", strict: bool = True):
    """Load the ML engine once at application startup."""
    global _engine
    if _engine is None:
        logger.info("Initializing ML Inference Engine from %s...", checkpoint_dir)
        checkpoint_path = Path(checkpoint_dir)
        bundle = ModelBundle(checkpoint_path)
        _engine = InferenceEngine(bundle, strict=strict)
        
        # Ensure directories exist
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info("ML Engine initialized successfully.")


def get_engine() -> InferenceEngine:
    """Get the initialized engine."""
    if _engine is None:
        # Fallback for local tests/development
        initialize_engine(strict=False)
    return _engine


def process_and_predict(file_path: Path, sample_id: str) -> dict:
    """Run prediction on the given image file using Phase 4 engine."""
    engine = get_engine()
    
    try:
        image = Image.open(file_path)
        # Ensure it's fully loaded and validated
        image.verify()
        image = Image.open(file_path) # Reload after verify
    except UnidentifiedImageError:
        raise ValueError("Invalid image file format") from None
        
    result = engine.predict(image=image, sample_id=sample_id, explain=False)
    
    return {
        "model_version": engine.bundle.metadata.get("version", "v1.0"),
        "model_architecture": engine.architecture,
        "predicted_class": result.class_name,
        "predicted_class_index": result.class_index,
        "probability_normal": 1.0 - result.probability if result.class_index == 1 else result.probability,
        "probability_pneumonia": result.probability if result.class_index == 1 else 1.0 - result.probability,
        "confidence": result.confidence_score,
        "threshold": 0.5, # Default binary threshold
        "uncertainty_status": "HIGH" if result.entropy > 0.5 else "LOW",
        "entropy": result.entropy,
        "margin": result.margin,
        "calibration_status": "UNAVAILABLE",
        "inference_time": result.processing_time_ms,
    }


def process_explainability(file_path: Path, target_class: int, method: str = "gradcam") -> dict | None:
    """Run explainability on the image."""
    engine = get_engine()
    
    try:
        image = Image.open(file_path)
        image = image.convert("RGB")  # type: ignore
    except UnidentifiedImageError:
        raise ValueError("Invalid image file format") from None
        
    # We call predict with explain=True
    result = engine.predict(image=image, sample_id="explain", explain=True, explain_method=method)
    
    if result.explanation is None:
        return None
        
    return {
        "heatmap": result.explanation.heatmap,
        "overlay_image_base64": result.explanation.overlay_image_base64,
        "method": result.explanation.method,
        "target_layer": result.explanation.target_layer
    }


def save_upload_file(upload_file) -> Path:
    """Save an uploaded file securely to disk."""
    ext = Path(upload_file.filename).suffix
    safe_filename = f"{uuid.uuid4()}{ext}"
    dest_path = UPLOAD_DIR / safe_filename
    
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    return dest_path
