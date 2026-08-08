"""Training loop and model checkpointing."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from ml.evaluation.metrics import calculate_metrics

logger = logging.getLogger(__name__)


class Trainer:
    """Handles the training loop, evaluation, and checkpointing."""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        device: torch.device,
        checkpoint_dir: Path = Path("ml/models/checkpoints"),
        patience: int = 5,
        use_amp: bool = False
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.checkpoint_dir = checkpoint_dir
        self.patience = patience
        self.use_amp = use_amp
        
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.scaler = torch.cuda.amp.GradScaler(enabled=self.use_amp)
        self.best_val_loss = float("inf")
        self.epochs_no_improve = 0

    def _train_epoch(self) -> float:
        """Run one training epoch."""
        self.model.train()
        running_loss = 0.0
        
        pbar = tqdm(self.train_loader, desc="Training")
        for inputs, targets in pbar:
            inputs = inputs.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            
            self.optimizer.zero_grad(set_to_none=True)
            
            with torch.cuda.amp.autocast(enabled=self.use_amp):
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()
            
            running_loss += loss.item() * inputs.size(0)
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})
            
        return running_loss / len(self.train_loader.dataset)

    @torch.no_grad()
    def _validate_epoch(self) -> Tuple[float, Dict]:
        """Run validation for one epoch."""
        self.model.eval()
        running_loss = 0.0
        
        all_targets = []
        all_probs = []
        all_preds = []
        
        pbar = tqdm(self.val_loader, desc="Validation")
        for inputs, targets in pbar:
            inputs = inputs.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            
            with torch.cuda.amp.autocast(enabled=self.use_amp):
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                
            running_loss += loss.item() * inputs.size(0)
            
            probs = torch.softmax(outputs, dim=1)[:, 1]
            preds = torch.argmax(outputs, dim=1)
            
            all_targets.extend(targets.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())
            
        epoch_loss = running_loss / len(self.val_loader.dataset)
        metrics = calculate_metrics(all_targets, all_preds, all_probs)
        return epoch_loss, metrics

    def save_checkpoint(
        self,
        epoch: int,
        metrics: Dict,
        is_best: bool = False,
        metadata: Optional[Dict] = None
    ) -> None:
        """Save a model checkpoint."""
        checkpoint_path = self.checkpoint_dir / "latest_model.pth"
        best_path = self.checkpoint_dir / "best_model.pth"
        metadata_path = self.checkpoint_dir / "model_metadata.json"
        
        state = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "metrics": metrics,
        }
        
        torch.save(state, checkpoint_path)
        logger.info("Saved latest checkpoint to %s", checkpoint_path)
        
        if is_best:
            torch.save(state, best_path)
            logger.info("Saved new best checkpoint to %s", best_path)
            
            if metadata:
                metadata["best_epoch"] = epoch
                metadata["metrics"] = metrics
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=4)
                logger.info("Saved metadata to %s", metadata_path)

    def fit(self, num_epochs: int, mlflow_run=None, metadata: Optional[Dict] = None) -> Dict:
        """Execute the full training loop."""
        logger.info("Starting training for %d epochs on device: %s", num_epochs, self.device)
        
        best_metrics = {}
        
        for epoch in range(1, num_epochs + 1):
            logger.info("Epoch %d/%d", epoch, num_epochs)
            
            train_loss = self._train_epoch()
            val_loss, val_metrics = self._validate_epoch()
            
            logger.info("Train Loss: %.4f | Val Loss: %.4f", train_loss, val_loss)
            logger.info("Val Metrics: %s", val_metrics)
            
            if mlflow_run:
                import mlflow
                mlflow.log_metric("train_loss", train_loss, step=epoch)
                mlflow.log_metric("val_loss", val_loss, step=epoch)
                for k, v in val_metrics.items():
                    mlflow.log_metric(f"val_{k}", v, step=epoch)
            
            is_best = val_loss < self.best_val_loss
            if is_best:
                self.best_val_loss = val_loss
                self.epochs_no_improve = 0
                best_metrics = val_metrics
            else:
                self.epochs_no_improve += 1
                
            self.save_checkpoint(epoch, val_metrics, is_best, metadata)
            
            if self.epochs_no_improve >= self.patience:
                logger.info("Early stopping triggered after %d epochs without improvement.", epoch)
                break
                
        return best_metrics
