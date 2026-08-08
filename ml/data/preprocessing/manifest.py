"""Dataset manifest generation and validation."""

import hashlib
import logging
import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd
from PIL import Image, UnidentifiedImageError
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class DataSettings(BaseSettings):
    """Configuration for data processing."""
    raw_data_dir: Path = Path("data/raw")
    interim_data_dir: Path = Path("data/interim")
    manifest_name: str = "dataset_manifest.csv"
    supported_extensions: set[str] = {".jpg", ".jpeg", ".png"}

    class Config:
        env_file = ".env"
        env_prefix = "MEDVISION_"


def extract_patient_id(filename: str) -> str:
    """Extract patient ID from filename based on Kermany dataset conventions.
    
    Examples:
    - person1000_bacteria_2931.jpeg -> "person1000"
    - IM-0115-0001.jpeg -> "IM-0115"
    - NORMAL2-IM-1427-0001.jpeg -> "NORMAL2-IM-1427"
    """
    # Pattern 1: personXXX_...
    match = re.match(r"(person\d+)_", filename)
    if match:
        return match.group(1)
        
    # Pattern 2: IM-XXXX... or NORMAL-IM-XXXX...
    match = re.search(r"((?:NORMAL\d*-)?IM-\d+)", filename)
    if match:
        return match.group(1)
        
    return "UNKNOWN"


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def process_image(filepath: Path) -> Dict:
    """Process a single image and return its metadata."""
    record = {
        "original_path": str(filepath.as_posix()),
        "file_extension": filepath.suffix.lower(),
        "file_size_bytes": filepath.stat().st_size,
        "sample_id": filepath.stem,
        "patient_id": extract_patient_id(filepath.name),
        "file_hash": compute_file_hash(filepath),
        "validation_status": "VALID",
        "width": -1,
        "height": -1,
        "channels": -1,
        "mode": "UNKNOWN",
        "image_format": "UNKNOWN"
    }

    try:
        with Image.open(filepath) as img:
            img.verify()  # Verify it's an intact image
            record["width"], record["height"] = img.size
            record["mode"] = img.mode
            record["image_format"] = img.format
            record["channels"] = len(img.getbands())
    except (UnidentifiedImageError, IOError, SyntaxError) as e:
        record["validation_status"] = f"INVALID: {str(e)}"
        logger.warning("Invalid image found: %s", filepath)

    return record


def generate_manifest(settings: DataSettings) -> None:
    """Traverse the raw dataset and generate a metadata manifest."""
    raw_dir = settings.raw_data_dir
    if not raw_dir.exists():
        logger.error("Raw data directory %s does not exist.", raw_dir)
        return

    # Check for the nested chest_xray folder
    search_dir = raw_dir
    if (raw_dir / "chest_xray").exists():
        search_dir = raw_dir / "chest_xray"

    records = []
    
    # Expected structure: search_dir / split / class / file.jpg
    # E.g., chest_xray/train/PNEUMONIA/person1000_...
    for split_dir in search_dir.iterdir():
        if not split_dir.is_dir() or split_dir.name not in ["train", "val", "test"]:
            continue
            
        split_name = split_dir.name
        
        for class_dir in split_dir.iterdir():
            if not class_dir.is_dir() or class_dir.name not in ["NORMAL", "PNEUMONIA"]:
                continue
                
            class_name = class_dir.name
            class_index = 0 if class_name == "NORMAL" else 1
            
            for filepath in class_dir.iterdir():
                if filepath.is_file() and filepath.suffix.lower() in settings.supported_extensions:
                    record = process_image(filepath)
                    record["split_source"] = split_name
                    record["class_name"] = class_name
                    record["class_index"] = class_index
                    records.append(record)

    if not records:
        logger.warning("No valid images found in %s.", search_dir)
        return

    df = pd.DataFrame(records)
    
    # Leakage and duplicate checks
    duplicates = df.duplicated(subset=["file_hash"], keep=False)
    if duplicates.any():
        logger.warning("Found %d duplicate file hashes.", duplicates.sum())
        df.loc[duplicates, "validation_status"] = "INVALID: DUPLICATE_HASH"
        
    # Validation summary
    logger.info("Total images processed: %d", len(df))
    logger.info("Validation status counts:\n%s", df["validation_status"].value_counts())
    
    settings.interim_data_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = settings.interim_data_dir / settings.manifest_name
    df.to_csv(manifest_path, index=False)
    logger.info("Manifest saved to %s", manifest_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    generate_manifest(DataSettings())
