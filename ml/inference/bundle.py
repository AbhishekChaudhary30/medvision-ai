"""Model loading and artifact bundling for inference."""

import json
import logging
from pathlib import Path

import torch
import torch.nn as nn

from ml.models.architectures.factory import create_model

logger = logging.getLogger(__name__)


class ModelBundle:
    """Manages loading and validating a trained model and its metadata."""

    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir
        self.model_path = checkpoint_dir / "best_model.pth"
        self.metadata_path = checkpoint_dir / "model_metadata.json"

        self.metadata: dict = {}
        self.model: nn.Module = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load(self, strict: bool = True) -> nn.Module:
        """Load the model and metadata.

        Args:
            strict: If True, raises exceptions when files are missing.
                   If False, allows falling back to dummy models for testing.
        """
        if not self.metadata_path.exists():
            if strict:
                raise FileNotFoundError(f"Metadata not found at {self.metadata_path}")
            else:
                logger.warning("Metadata missing. Using fallback metadata for testing.")
                self.metadata = {"architecture": "custom_cnn", "batch_size": 32, "learning_rate": 0.001}
        else:
            with open(self.metadata_path) as f:
                self.metadata = json.load(f)

        architecture = self.metadata.get("architecture", "custom_cnn")

        # Instantiate the architecture
        self.model = create_model(architecture, num_classes=2, pretrained=False)

        if not self.model_path.exists():
            if strict:
                raise FileNotFoundError(f"Model checkpoint not found at {self.model_path}")
            else:
                logger.warning("Checkpoint missing. Using uninitialized model for testing.")
        else:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            logger.info("Successfully loaded model state dict.")

        self.model.to(self.device)
        self.model.eval()
        return self.model

    def get_architecture(self) -> str:
        return self.metadata.get("architecture", "custom_cnn")
