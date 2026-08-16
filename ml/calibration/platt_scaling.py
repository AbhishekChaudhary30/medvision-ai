import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class PlattScaler(nn.Module):
    """
    Implements Platt Scaling (Temperature Scaling for multi-class, or simple Logistic Regression for binary)
    to calibrate the confidence probabilities of the model outputs.
    """
    def __init__(self):
        super().__init__()
        # We learn a single temperature parameter
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)

    def forward(self, logits):
        return logits / self.temperature

    def fit(self, model: nn.Module, val_loader: DataLoader, device: torch.device, lr: float = 0.01, max_iter: int = 50):
        """
        Fit the temperature using a validation set.
        The model should be frozen.
        """
        model.eval()
        nll_criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.LBFGS([self.temperature], lr=lr, max_iter=max_iter)
        
        logits_list = []
        labels_list = []
        
        logger.info("Extracting logits for calibration...")
        with torch.no_grad():
            for inputs, targets in tqdm(val_loader, desc="Calibration"):
                inputs = inputs.to(device)
                logits = model(inputs)
                logits_list.append(logits)
                labels_list.append(targets)
                
        logits = torch.cat(logits_list).to(device)
        labels = torch.cat(labels_list).to(device)
        
        # Calculate NLL before calibration
        before_calibration_nll = nll_criterion(logits, labels).item()
        logger.info(f"NLL before calibration: {before_calibration_nll:.4f}")
        
        def eval_fn():
            optimizer.zero_grad()
            loss = nll_criterion(self.forward(logits), labels)
            loss.backward()
            return loss
            
        optimizer.step(eval_fn)
        
        # Calculate NLL after calibration
        after_calibration_nll = nll_criterion(self.forward(logits), labels).item()
        logger.info(f"Optimal temperature: {self.temperature.item():.4f}")
        logger.info(f"NLL after calibration: {after_calibration_nll:.4f}")
        
        return self.temperature.item()
