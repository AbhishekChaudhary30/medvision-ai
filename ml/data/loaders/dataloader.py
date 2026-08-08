"""DataLoader factory functions."""

from pathlib import Path

from torch.utils.data import DataLoader

from ml.data.loaders.dataset import ChestXRayDataset
from ml.data.preprocessing.transforms import (
    get_test_transforms,
    get_train_transforms,
    get_val_transforms,
)


def get_dataloaders(manifest_path: Path, batch_size: int = 32, num_workers: int = 4, pin_memory: bool = True) -> dict[str, DataLoader]:
    """Create DataLoaders for train, val, and test splits.

    Args:
        manifest_path: Path to the processed dataset_manifest.csv
        batch_size: Number of images per batch
        num_workers: Number of subprocesses for data loading
        pin_memory: Whether to copy tensors into CUDA pinned memory

    Returns:
        Dictionary containing 'train', 'val', and 'test' DataLoaders.
    """
    train_dataset = ChestXRayDataset(manifest_path=manifest_path, split="train", transform=get_train_transforms())
    val_dataset = ChestXRayDataset(manifest_path=manifest_path, split="val", transform=get_val_transforms())
    test_dataset = ChestXRayDataset(manifest_path=manifest_path, split="test", transform=get_test_transforms())

    # Shuffle only for training
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=True,
        persistent_workers=(num_workers > 0),
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=False,
        persistent_workers=(num_workers > 0),
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=False,
        persistent_workers=(num_workers > 0),
    )

    return {"train": train_loader, "val": val_loader, "test": test_loader}
