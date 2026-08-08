"""Main entrypoint for model training."""

import argparse
import logging
from pathlib import Path

import torch
import torch.nn as nn

from ml.data.loaders.dataloader import get_dataloaders
from ml.models.architectures.factory import create_model
from ml.training.trainer import Trainer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Train a CNN for Chest X-Ray Classification.")

    parser.add_argument(
        "--architecture",
        type=str,
        default="custom_cnn",
        choices=["custom_cnn", "resnet50", "densenet121", "efficientnet_b0"],
        help="Model architecture to use.",
    )
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs.")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size.")
    parser.add_argument("--learning-rate", type=float, default=1e-4, help="Learning rate.")
    parser.add_argument("--manifest-path", type=Path, default=Path("data/processed/split_manifest.csv"), help="Path to the split manifest CSV.")
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("ml/models/checkpoints"), help="Directory to save model checkpoints.")
    parser.add_argument("--use-amp", action="store_true", help="Use Automatic Mixed Precision.")
    parser.add_argument("--mlflow-tracking", action="store_true", help="Enable MLflow logging.")

    return parser.parse_args()


def main() -> None:
    """Run the training process."""
    args = parse_args()

    # 1. Device configuration
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Using device: %s", device)

    if not args.manifest_path.exists():
        logger.error("Manifest path %s does not exist. Please run the data pipeline first.", args.manifest_path)
        return

    # 2. Data Loaders
    logger.info("Initializing DataLoaders...")
    loaders = get_dataloaders(
        manifest_path=args.manifest_path,
        batch_size=args.batch_size,
        num_workers=4 if device.type == "cuda" else 0,
        pin_memory=(device.type == "cuda"),
    )

    train_loader = loaders["train"]
    val_loader = loaders["val"]

    # 3. Model initialization
    logger.info("Initializing model: %s", args.architecture)
    model = create_model(architecture=args.architecture, num_classes=2, pretrained=True, freeze_backbone=False)

    # 4. Loss and Optimizer
    # PNEUMONIA vs NORMAL is often imbalanced. We could pass class weights here if needed.
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)

    # 5. Trainer initialization
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        device=device,
        checkpoint_dir=args.checkpoint_dir,
        patience=5,
        use_amp=args.use_amp,
    )

    metadata = {
        "architecture": args.architecture,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "use_amp": args.use_amp,
    }

    # 6. MLflow and Training
    if args.mlflow_tracking:
        import mlflow

        mlflow.set_experiment("medvision_chest_xray")
        with mlflow.start_run():
            mlflow.log_params(metadata)
            trainer.fit(num_epochs=args.epochs, mlflow_run=mlflow, metadata=metadata)
    else:
        trainer.fit(num_epochs=args.epochs, mlflow_run=None, metadata=metadata)

    logger.info("Training completed.")


if __name__ == "__main__":
    main()
