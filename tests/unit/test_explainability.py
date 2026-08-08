"""Unit tests for explainability components."""

from pathlib import Path

import torch.nn as nn
from PIL import Image

from ml.explainability.resolvers import resolve_target_layer
from ml.inference.bundle import ModelBundle
from ml.inference.engine import InferenceEngine
from ml.models.architectures.factory import create_model


def test_resolve_target_layer_custom_cnn():
    """Test that target layer resolver works for Custom CNN."""
    model = create_model("custom_cnn", num_classes=2)
    layers = resolve_target_layer(model, "custom_cnn")

    assert len(layers) == 1
    assert isinstance(layers[0], nn.Conv2d)


def test_resolve_target_layer_resnet50():
    """Test that target layer resolver works for ResNet50."""
    model = create_model("resnet50", num_classes=2, pretrained=False)
    layers = resolve_target_layer(model, "resnet50")

    assert len(layers) == 1
    # Check that it's a Bottleneck layer
    assert layers[0].__class__.__name__ == "Bottleneck"


def test_explainability_service_generation(tmp_path: Path):
    """Test that the inference engine can generate a Grad-CAM result."""
    bundle = ModelBundle(tmp_path)
    engine = InferenceEngine(bundle, strict=False)

    dummy_img = Image.new("RGB", (224, 224), color="white")

    result = engine.predict(image=dummy_img, sample_id="test_explain", explain=True, explain_method="gradcam")

    assert result.explanation is not None
    assert result.explanation.method == "gradcam"
    assert result.explanation.overlay_image_base64.startswith("/9j/") or len(result.explanation.overlay_image_base64) > 100

    heatmap = result.explanation.heatmap
    assert len(heatmap) == 224
    assert len(heatmap[0]) == 224
