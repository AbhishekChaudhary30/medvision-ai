"""Benchmarking script to evaluate candidate models."""

import argparse
import logging
from pathlib import Path
import torch
import torch.nn as nn
import mlflow

from ml.models.architectures.factory import create_model
from ml.training.trainer import Trainer
from ml.data.loaders.dataloader import get_dataloaders
from scripts.train import set_seed

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def run_benchmark(manifest_path: Path, batch_size: int, epochs: int, device: str):
    logger.info("Starting model benchmarking suite...")
    set_seed(42)
    
    if not manifest_path.exists():
        logger.error(f"Manifest file {manifest_path} not found. Run prepare_data.py first.")
        return

    device_obj = torch.device(device)
    
    logger.info("Loading DataLoaders...")
    loaders = get_dataloaders(
        manifest_path=manifest_path,
        batch_size=batch_size,
        num_workers=4 if device == "cuda" else 0,
        pin_memory=(device == "cuda")
    )
    
    train_loader = loaders["train"]
    val_loader = loaders["val"]

    architectures = ["resnet50", "densenet121", "efficientnet_b0"]
    criterion = nn.CrossEntropyLoss()

    mlflow.set_experiment("MedVision_Benchmarking")

    for arch in architectures:
        logger.info(f"--- Benchmarking {arch} ---")
        with mlflow.start_run(run_name=arch) as run:
            model = create_model(arch, num_classes=2, pretrained=True)
            optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

            mlflow.log_params({
                "architecture": arch,
                "batch_size": batch_size,
                "learning_rate": 1e-4,
                "pretrained": True
            })

            trainer = Trainer(
                model=model,
                train_loader=train_loader,
                val_loader=val_loader,
                criterion=criterion,
                optimizer=optimizer,
                device=device_obj,
                checkpoint_dir=Path(f"ml/models/checkpoints/{arch}"),
                use_amp=True if device == "cuda" else False,
                patience=3  # Shorter patience for benchmarking
            )

            best_metrics = trainer.fit(num_epochs=epochs, mlflow_run=True, metadata={"architecture": arch})
            logger.info(f"Finished {arch}. Best metrics: {best_metrics}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-path", type=str, default="data/processed/split_manifest.csv")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    
    args = parser.parse_args()
    run_benchmark(Path(args.manifest_path), args.batch_size, args.epochs, args.device)
