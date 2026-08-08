"""Script to download the Chest X-Ray (Pneumonia) dataset from Kaggle."""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

KAGGLE_DATASET = "paultimothymooney/chest-xray-pneumonia"


def check_kaggle_credentials() -> bool:
    """Check if Kaggle API credentials are present."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    if not kaggle_json.exists():
        logger.error(
            "Kaggle API credentials not found at %s. "
            "Please create an API token from your Kaggle account and place it there.",
            kaggle_json
        )
        return False
    return True


def download_dataset(output_dir: Path) -> None:
    """Download and extract the dataset using the kaggle CLI."""
    try:
        import kaggle  # noqa: F401
    except ImportError:
        logger.error("Kaggle Python package is not installed. Please install it.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Downloading dataset %s to %s...", KAGGLE_DATASET, output_dir)
    
    # Run the Kaggle API command
    try:
        subprocess.run(
            [
                "kaggle", "datasets", "download",
                "-d", KAGGLE_DATASET,
                "-p", str(output_dir),
                "--unzip"
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error("Failed to download the dataset: %s", e)
        sys.exit(1)
        
    logger.info("Dataset successfully downloaded and extracted to %s", output_dir)
    
    # The dataset often extracts into `chest_xray/chest_xray/` or similar.
    # We should normalize it to be just `data/raw/chest_xray`.
    chest_xray_dir = output_dir / "chest_xray"
    if chest_xray_dir.exists() and (chest_xray_dir / "chest_xray").exists():
        logger.info("Normalizing nested dataset directories...")
        nested_dir = chest_xray_dir / "chest_xray"
        
        # Move everything from nested to a temp dir, then replace
        temp_dir = output_dir / "temp_chest_xray"
        shutil.move(str(nested_dir), str(temp_dir))
        shutil.rmtree(str(chest_xray_dir))
        shutil.move(str(temp_dir), str(chest_xray_dir))
        
        logger.info("Normalization complete.")


def main() -> None:
    """Main entrypoint for data downloading."""
    parser = argparse.ArgumentParser(description="Download the MedVision AI raw dataset.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory to save the raw dataset"
    )
    args = parser.parse_args()

    if not check_kaggle_credentials():
        logger.warning(
            "Without Kaggle credentials, you must manually download the dataset from "
            "https://www.kaggle.com/datasets/%s and extract it to %s",
            KAGGLE_DATASET, args.output_dir
        )
        sys.exit(1)

    download_dataset(args.output_dir)


if __name__ == "__main__":
    main()
