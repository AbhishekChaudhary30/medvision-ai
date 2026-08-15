"""ML Service adapter bridging Phase 4 engine with API layer."""

import logging
import shutil
import uuid
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from ml.inference.bundle import ModelBundle
from ml.inference.engine import InferenceEngine

from ml.inference.registry import ModalityRegistry

logger = logging.getLogger(__name__)

# Cache of engines per modality
_engines: dict[str, InferenceEngine] = {}

UPLOAD_DIR = Path("data/uploads")
ARTIFACT_DIR = Path("data/artifacts")


def initialize_engine(checkpoint_dir: str = "ml/models/checkpoints", strict: bool = True, modality: str = "chest-xray"):
    """Load the ML engine for a specific modality."""
    global _engines
    if modality not in _engines:
        logger.info("Initializing ML Inference Engine for modality %s...", modality)
        
        model, architecture, class_names = ModalityRegistry.load_model(modality, strict=strict)
        
        if model is None:
            # It's a bundle-based model (e.g. chest-xray)
            checkpoint_path = Path(checkpoint_dir)
            bundle = ModelBundle(checkpoint_path)
            _engines[modality] = InferenceEngine(bundle=bundle, strict=strict)
        else:
            # It's a registry-provided model (e.g. brain-mri, skin-lesion)
            _engines[modality] = InferenceEngine(model=model, architecture=architecture, class_names=class_names)

        # Ensure directories exist
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("ML Engine for %s initialized successfully.", modality)


def get_engine(modality: str = "chest-xray") -> InferenceEngine:
    """Get the initialized engine for the modality."""
    if modality not in _engines:
        # Fallback for local tests/development or lazy load
        initialize_engine(strict=False, modality=modality)
    return _engines[modality]


def process_and_predict(file_path: Path, sample_id: str, modality: str = "chest-xray") -> dict:
    """Run prediction on the given image file using Phase 4 engine."""
    engine = get_engine(modality)

    try:
        image = Image.open(file_path)
        # Ensure it's fully loaded and validated
        image.verify()
        image = Image.open(file_path)  # Reload after verify
    except UnidentifiedImageError:
        raise ValueError("Invalid image file format") from None

    result = engine.predict(image=image, sample_id=sample_id, explain=False)
    
    # Generic probability mapping (assuming class index 1 is the 'positive' or anomaly case for all)
    prob_normal = 1.0 - result.probability if result.class_index == 1 else result.probability
    prob_anomaly = result.probability if result.class_index == 1 else 1.0 - result.probability

    return {
        "modality": modality,
        "model_version": getattr(engine.bundle, "metadata", {}).get("version", "v1.0") if engine.bundle else "v1.0",
        "model_architecture": engine.architecture,
        "predicted_class": result.class_name,
        "predicted_class_index": result.class_index,
        "probability_normal": prob_normal,
        "probability_pneumonia": prob_anomaly, # reusing this column for 'anomaly probability' temporarily
        "confidence": result.confidence_score,
        "threshold": 0.5,  # Default binary threshold
        "uncertainty_status": "HIGH" if result.entropy > 0.5 else "LOW",
        "entropy": result.entropy,
        "margin": result.margin,
        "calibration_status": "UNAVAILABLE",
        "inference_time": result.processing_time_ms,
    }


def process_explainability(file_path: Path, target_class: int, method: str = "gradcam", modality: str = "chest-xray") -> dict | None:
    """Run explainability on the image."""
    engine = get_engine(modality)

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
        "target_layer": result.explanation.target_layer,
    }


def save_upload_file(upload_file) -> Path:
    """Save an uploaded file securely to disk."""
    ext = Path(upload_file.filename).suffix
    safe_filename = f"{uuid.uuid4()}{ext}"
    dest_path = UPLOAD_DIR / safe_filename

    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return dest_path
