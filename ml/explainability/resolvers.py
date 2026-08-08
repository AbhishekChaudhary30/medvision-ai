"""Target layer resolvers for different model architectures."""

import torch.nn as nn


def resolve_target_layer(model: nn.Module, architecture: str) -> list[nn.Module]:
    """Resolve the target convolutional layer for Grad-CAM.
    
    Grad-CAM needs the gradients and activations of the last spatial feature map.
    This dynamically locates it based on the architecture string.
    
    Args:
        model: The PyTorch model.
        architecture: String identifier (e.g., 'resnet50', 'densenet121').
        
    Returns:
        A list containing the target layer module.
    """
    if architecture == "custom_cnn":
        # The last conv layer in our Sequential model is at index 6
        # nn.Sequential: Conv, ReLU, MaxPool, Conv, ReLU, MaxPool, Conv(6)
        if isinstance(model, nn.Sequential) and len(model) > 6:
            return [model[6]]
        return [model]
        
    elif architecture == "resnet50":
        # The last block of layer4
        return [model.layer4[-1]]
        
    elif architecture == "densenet121":
        # The final denseblock's features
        return [model.features.denseblock4.denselayer16]
        
    elif architecture == "efficientnet_b0":
        # The final stage in the features sequential
        return [model.features[-1]]
        
    else:
        raise ValueError(f"Unknown architecture for target layer resolution: {architecture}")
