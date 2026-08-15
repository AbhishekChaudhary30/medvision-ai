import torch
import numpy as np
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class OODDetector:
    """
    Out-Of-Distribution (OOD) Detector.
    Uses confidence thresholds or feature-space statistics (Mahalanobis) to reject inputs
    that are wildly outside the training distribution (e.g. non-medical images).
    
    This is a simplified Confidence-based baseline.
    For more advanced usage, one would fit a GMM or compute Mahalanobis distance on the penultimate layer.
    """
    def __init__(self, confidence_threshold: float = 0.65, entropy_threshold: float = 0.8):
        self.confidence_threshold = confidence_threshold
        self.entropy_threshold = entropy_threshold

    def is_ood(self, probs: torch.Tensor) -> bool:
        """
        Check if the prediction indicates OOD.
        Args:
            probs: Tensor of shape (1, num_classes) containing probabilities.
        Returns:
            bool: True if OOD, False if in-distribution.
        """
        probs_np = probs.cpu().numpy().flatten()
        max_prob = np.max(probs_np)
        
        # Compute entropy
        entropy = -np.sum(probs_np * np.log(probs_np + 1e-10))
        
        if max_prob < self.confidence_threshold or entropy > self.entropy_threshold:
            logger.warning(f"OOD detected: max_prob={max_prob:.4f}, entropy={entropy:.4f}")
            return True
            
        return False
