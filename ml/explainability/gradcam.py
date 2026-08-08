"""Grad-CAM service for generating explainability artifacts."""

import base64
import io
import logging
from typing import Optional

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from pytorch_grad_cam import GradCAM, GradCAMPlusPlus
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

from ml.explainability.resolvers import resolve_target_layer
from ml.inference.schemas import ExplanationResult

logger = logging.getLogger(__name__)


class ExplainabilityService:
    """Wrapper around pytorch-grad-cam to generate visual explanations."""
    
    def __init__(self, model: nn.Module, architecture: str, use_cuda: bool = False):
        self.model = model
        self.architecture = architecture
        self.use_cuda = use_cuda
        
        try:
            self.target_layers = resolve_target_layer(model, architecture)
        except ValueError as e:
            logger.warning("Could not resolve target layer: %s. Explainability disabled.", e)
            self.target_layers = None

    def generate_explanation(
        self,
        input_tensor: torch.Tensor,
        original_image: Image.Image,
        target_class: int,
        method: str = "gradcam"
    ) -> Optional[ExplanationResult]:
        """Generate a Grad-CAM explanation.
        
        Args:
            input_tensor: The preprocessed 1xCxHxW tensor passed to the model.
            original_image: The original PIL Image before tensor conversion (but after resizing).
            target_class: The class index to explain.
            method: 'gradcam' or 'gradcam++'
            
        Returns:
            ExplanationResult containing heatmap and base64 overlay, or None if failed.
        """
        if not self.target_layers:
            return None
            
        try:
            # Select the algorithm
            cam_algorithm = GradCAMPlusPlus if method.lower() == "gradcam++" else GradCAM
            
            with cam_algorithm(model=self.model, target_layers=self.target_layers) as cam:
                targets = [ClassifierOutputTarget(target_class)]
                
                # Generate heatmap (returns [batch_size, H, W], we take the first)
                grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0, :]
                
                # Ensure the grayscale_cam is valid
                if not np.isfinite(grayscale_cam).all():
                    logger.warning("Grad-CAM generated non-finite values.")
                    return None
                    
                # Resize original image to match tensor spatial dimensions (typically 224x224)
                img_array = np.array(original_image.resize((input_tensor.shape[3], input_tensor.shape[2])))
                
                # Convert to float [0, 1] for show_cam_on_image
                img_float = np.float32(img_array) / 255.0
                
                # Create overlay
                visualization = show_cam_on_image(img_float, grayscale_cam, use_rgb=True)
                
                # Convert overlay to base64 for frontend consumption
                overlay_pil = Image.fromarray(visualization)
                buffered = io.BytesIO()
                overlay_pil.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                return ExplanationResult(
                    heatmap=grayscale_cam.tolist(),
                    overlay_image_base64=img_str,
                    method=method,
                    target_layer=self.target_layers[0].__class__.__name__
                )
        except Exception as e:
            logger.error("Failed to generate Grad-CAM explanation: %s", e)
            return None
