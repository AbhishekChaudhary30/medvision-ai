"""Evaluation metrics for binary classification."""

from typing import Dict, List, Union

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def calculate_metrics(
    y_true: Union[List[int], np.ndarray],
    y_pred: Union[List[int], np.ndarray],
    y_prob: Union[List[float], np.ndarray]
) -> Dict[str, float]:
    """Calculate binary classification metrics.
    
    Args:
        y_true: True labels (0 or 1).
        y_pred: Predicted labels (0 or 1).
        y_prob: Predicted probabilities for class 1 (PNEUMONIA).
        
    Returns:
        Dictionary of metrics.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_prob = np.array(y_prob)

    # Basic metrics
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    # Probabilistic metrics
    try:
        roc_auc = roc_auc_score(y_true, y_prob)
    except ValueError:
        # Happens if only one class is present in y_true
        roc_auc = 0.5
        
    try:
        pr_auc = average_precision_score(y_true, y_prob)
    except ValueError:
        pr_auc = 0.0

    # Confusion matrix based metrics
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    else:
        specificity = 0.0
        
    # Accuracy calculation manually for safety
    accuracy = (y_pred == y_true).mean()
    
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),       # aka sensitivity
        "specificity": float(specificity),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
    }
