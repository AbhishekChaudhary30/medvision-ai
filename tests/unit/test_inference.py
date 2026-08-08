"""Unit tests for inference bundle and engine."""

from pathlib import Path

import pytest
import torch
from PIL import Image

from ml.inference.bundle import ModelBundle
from ml.inference.engine import InferenceEngine


def test_model_bundle_strict_fails(tmp_path: Path):
    """Test that strict loading fails when files are missing."""
    bundle = ModelBundle(tmp_path)
    with pytest.raises(FileNotFoundError):
        bundle.load(strict=True)


def test_model_bundle_fallback(tmp_path: Path):
    """Test that fallback loading works for testing."""
    bundle = ModelBundle(tmp_path)
    model = bundle.load(strict=False)
    
    assert model is not None
    assert bundle.get_architecture() == "custom_cnn"
    assert next(model.parameters()).device == bundle.device


def test_inference_engine_predict(tmp_path: Path):
    """Test the complete inference flow without Grad-CAM."""
    bundle = ModelBundle(tmp_path)
    # We use strict=False to bypass missing files for unit testing
    engine = InferenceEngine(bundle, strict=False)
    
    # Create dummy image
    dummy_img = Image.new("RGB", (224, 224), color="white")
    
    result = engine.predict(
        image=dummy_img,
        sample_id="test_sample_1",
        explain=False
    )
    
    assert result.sample_id == "test_sample_1"
    assert result.class_name in ["NORMAL", "PNEUMONIA"]
    assert 0.0 <= result.probability <= 1.0
    assert result.explanation is None
    assert result.processing_time_ms > 0
    assert result.entropy >= 0
    assert result.margin >= 0
