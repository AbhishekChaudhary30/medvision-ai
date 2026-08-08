"""Model factory for creating architectures."""

import torch
import torch.nn as nn
import torchvision.models as models


def create_custom_cnn(num_classes: int = 2) -> nn.Module:
    """Create a simple custom CNN baseline."""
    model = nn.Sequential(
        nn.Conv2d(3, 16, kernel_size=3, padding=1),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(2, 2),
        nn.Conv2d(16, 32, kernel_size=3, padding=1),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(2, 2),
        nn.Conv2d(32, 64, kernel_size=3, padding=1),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(2, 2),
        nn.AdaptiveAvgPool2d((1, 1)),
        nn.Flatten(),
        nn.Linear(64, num_classes)
    )
    return model


def create_model(
    architecture: str,
    num_classes: int = 2,
    pretrained: bool = True,
    freeze_backbone: bool = False
) -> nn.Module:
    """Factory function to instantiate models.
    
    Args:
        architecture: 'custom_cnn', 'resnet50', 'densenet121', or 'efficientnet_b0'
        num_classes: Number of output classes
        pretrained: Whether to load ImageNet weights (for transfer learning)
        freeze_backbone: Whether to freeze feature layers
        
    Returns:
        PyTorch nn.Module
    """
    if architecture == "custom_cnn":
        return create_custom_cnn(num_classes)
        
    elif architecture == "resnet50":
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        model = models.resnet50(weights=weights)
        if freeze_backbone:
            for param in model.parameters():
                param.requires_grad = False
        # Replace head
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
        return model
        
    elif architecture == "densenet121":
        weights = models.DenseNet121_Weights.DEFAULT if pretrained else None
        model = models.densenet121(weights=weights)
        if freeze_backbone:
            for param in model.parameters():
                param.requires_grad = False
        num_ftrs = model.classifier.in_features
        model.classifier = nn.Linear(num_ftrs, num_classes)
        return model
        
    elif architecture == "efficientnet_b0":
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b0(weights=weights)
        if freeze_backbone:
            for param in model.parameters():
                param.requires_grad = False
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_ftrs, num_classes)
        return model
        
    else:
        raise ValueError(f"Unsupported architecture: {architecture}")
