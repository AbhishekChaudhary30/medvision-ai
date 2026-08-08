"""Inference Engine for MedVision AI."""

import logging
import time
from pathlib import Path
from typing import Optional

import torch
import torch.nn.functional as F
from PIL import Image

from ml.data.preprocessing.transforms import get_test_transforms
from ml.explainability.gradcam import ExplainabilityService
from ml.inference.bundle import ModelBundle
from ml.inference.schemas import InferenceResult

logger = logging.getLogger(__name__)

CLASS_NAMES = {0: "NORMAL", 1: "PNEUMONIA"}


class InferenceEngine:
    """Production-ready inference engine for single-image classification."""
    
    def __init__(self, bundle: ModelBundle, strict: bool = True):
        self.bundle = bundle
        self.model = self.bundle.load(strict=strict)
        self.device = self.bundle.device
        
        self.architecture = self.bundle.get_architecture()
        self.explainability_svc = ExplainabilityService(
            model=self.model,
            architecture=self.architecture,
            use_cuda=(self.device.type == "cuda")
        )
        
        # We reuse the deterministic Phase 2 validation/test transforms
        self.transform = get_test_transforms()

    def _calculate_entropy(self, probs: torch.Tensor) -> float:
        """Calculate predictive entropy as an epistemic uncertainty indicator."""
        # probs: [num_classes]
        entropy = -torch.sum(probs * torch.log(probs + 1e-10))
        return float(entropy.item())
        
    def _calculate_margin(self, probs: torch.Tensor) -> float:
        """Calculate prediction margin (difference between top 2 class probabilities)."""
        sorted_probs, _ = torch.sort(probs, descending=True)
        if len(sorted_probs) >= 2:
            return float((sorted_probs[0] - sorted_probs[1]).item())
        return 0.0

    def predict(
        self,
        image: Image.Image,
        sample_id: str = "unknown",
        explain: bool = False,
        explain_method: str = "gradcam"
    ) -> InferenceResult:
        """Run inference on a single image.
        
        Args:
            image: PIL Image
            sample_id: Identifier for the sample
            explain: Whether to generate Grad-CAM explainability artifacts
            explain_method: 'gradcam' or 'gradcam++'
            
        Returns:
            InferenceResult
        """
        start_time = time.time()
        
        # 1. Preprocessing (deterministic)
        image_rgb = image.convert("RGB")
        input_tensor = self.transform(image_rgb).unsqueeze(0).to(self.device)
        
        # 2. Forward pass
        with torch.inference_mode():
            logits = self.model(input_tensor)
            probs = F.softmax(logits, dim=1)[0]
            
        # 3. Decision
        class_index = int(torch.argmax(probs).item())
        class_name = CLASS_NAMES.get(class_index, "UNKNOWN")
        probability = float(probs[class_index].item())
        
        # 4. Uncertainty indicators
        entropy = self._calculate_entropy(probs)
        margin = self._calculate_margin(probs)
        
        # 5. Explainability (requires gradient computation, so we step out of inference_mode)
        explanation = None
        if explain:
            # Re-enable gradients for the explainability forward/backward pass
            with torch.enable_grad():
                input_tensor_explain = input_tensor.clone().requires_grad_(True)
                explanation = self.explainability_svc.generate_explanation(
                    input_tensor=input_tensor_explain,
                    original_image=image_rgb,
                    target_class=class_index,
                    method=explain_method
                )
                
        processing_time_ms = (time.time() - start_time) * 1000
        
        return InferenceResult(
            sample_id=sample_id,
            class_name=class_name,
            class_index=class_index,
            probability=probability,
            confidence_score=probability,
            entropy=entropy,
            margin=margin,
            explanation=explanation,
            processing_time_ms=processing_time_ms
        )
