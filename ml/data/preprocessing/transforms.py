"""Image transformations for training, validation, and testing."""

import torchvision.transforms.v2 as transforms

# Standard ImageNet normalization values
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Default target size for models like ResNet, DenseNet, EfficientNet
TARGET_SIZE = (224, 224)


def get_train_transforms(
    target_size: tuple[int, int] = TARGET_SIZE,
    mean: list[float] = IMAGENET_MEAN,
    std: list[float] = IMAGENET_STD,
) -> transforms.Compose:
    """Conservative data augmentation for medical images."""
    return transforms.Compose([
        # Convert grayscale to RGB if needed (done at Dataset level, but safe to enforce)
        transforms.Resize(target_size, antialias=True),
        transforms.RandomRotation(degrees=5),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToImage(),
        transforms.ToDtype(import_torch().float32, scale=True),
        transforms.Normalize(mean=mean, std=std),
    ])


def get_val_transforms(
    target_size: tuple[int, int] = TARGET_SIZE,
    mean: list[float] = IMAGENET_MEAN,
    std: list[float] = IMAGENET_STD,
) -> transforms.Compose:
    """Deterministic validation transformations."""
    return transforms.Compose([
        transforms.Resize(target_size, antialias=True),
        transforms.ToImage(),
        transforms.ToDtype(import_torch().float32, scale=True),
        transforms.Normalize(mean=mean, std=std),
    ])


def get_test_transforms(
    target_size: tuple[int, int] = TARGET_SIZE,
    mean: list[float] = IMAGENET_MEAN,
    std: list[float] = IMAGENET_STD,
) -> transforms.Compose:
    """Deterministic test transformations."""
    return transforms.Compose([
        transforms.Resize(target_size, antialias=True),
        transforms.ToImage(),
        transforms.ToDtype(import_torch().float32, scale=True),
        transforms.Normalize(mean=mean, std=std),
    ])


def import_torch():
    """Helper to lazy-import torch to avoid circular imports during setup."""
    import torch
    return torch
