"""Unit tests for Phase 3 training and evaluation components."""

import numpy as np
import pytest
import torch
import torch.nn as nn

from ml.evaluation.metrics import calculate_metrics
from ml.models.architectures.factory import create_model


def test_create_model():
    """Test model factory instantiation and head replacement."""
    model = create_model("custom_cnn", num_classes=2)
    assert isinstance(model, nn.Module)
    
    # Test a forward pass with dummy data
    dummy_input = torch.randn(2, 3, 224, 224)
    out = model(dummy_input)
    assert out.shape == (2, 2)
    
    # Try another architecture (fast check, disable pretrained to avoid downloads)
    model = create_model("resnet50", num_classes=2, pretrained=False)
    out = model(dummy_input)
    assert out.shape == (2, 2)


def test_calculate_metrics():
    """Test metrics calculation logic."""
    y_true = [0, 1, 1, 0, 1]
    y_pred = [0, 1, 0, 0, 1]
    y_prob = [0.1, 0.9, 0.4, 0.2, 0.8]
    
    metrics = calculate_metrics(y_true, y_pred, y_prob)
    
    assert "accuracy" in metrics
    assert "roc_auc" in metrics
    assert "precision" in metrics
    assert metrics["accuracy"] == 0.8  # 4 out of 5 correct
    assert metrics["precision"] == 1.0  # 2 TP, 0 FP
    assert metrics["recall"] == 2/3  # 2 TP out of 3 total positives
