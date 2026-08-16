import torch
from ml.inference.ood_detector import OODDetector

def test_ood_detector():
    detector = OODDetector(confidence_threshold=0.65, entropy_threshold=0.8)
    
    # High confidence -> not OOD
    probs_in = torch.tensor([[0.9, 0.1]])
    assert not detector.is_ood(probs_in), "High confidence should not be OOD"
    
    # Low confidence -> OOD
    probs_ood = torch.tensor([[0.51, 0.49]])
    assert detector.is_ood(probs_ood), "Low confidence should be OOD"
