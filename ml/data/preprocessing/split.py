"""Patient-aware stratified splitting of the dataset."""

import logging
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

logger = logging.getLogger(__name__)


def create_splits(manifest_path: Path, output_path: Path, val_size: float = 0.2, random_seed: int = 42) -> None:
    """Create train/val/test splits keeping patients separate and test set untouched."""
    if not manifest_path.exists():
        logger.error("Manifest file %s not found.", manifest_path)
        return

    df = pd.read_csv(manifest_path)

    # Filter out invalid images
    valid_df = df[df["validation_status"] == "VALID"].copy()
    logger.info("Found %d valid images out of %d total.", len(valid_df), len(df))

    # The official test set is kept as 'test'
    test_mask = valid_df["split_source"] == "test"
    test_df = valid_df[test_mask].copy()
    test_df["split"] = "test"

    # The rest is our development pool (train + original val)
    dev_df = valid_df[~test_mask].copy()

    # Check if we have reliable patient IDs
    unknown_patients = (dev_df["patient_id"] == "UNKNOWN").sum()
    if unknown_patients / len(dev_df) < 0.5:
        logger.info("Using patient-aware GroupShuffleSplit.")
        # If we have mostly known patient IDs, use GroupShuffleSplit
        gss = GroupShuffleSplit(n_splits=1, test_size=val_size, random_state=random_seed)
        train_idx, val_idx = next(gss.split(dev_df, dev_df["class_index"], dev_df["patient_id"]))

        dev_df["split"] = "UNKNOWN"
        dev_df.iloc[train_idx, dev_df.columns.get_loc("split")] = "train"
        dev_df.iloc[val_idx, dev_df.columns.get_loc("split")] = "val"
    else:
        logger.info("Reliable patient IDs not found. Falling back to stratified image-level split.")
        # Fallback to StratifiedShuffleSplit if patient IDs are not reliable
        from sklearn.model_selection import StratifiedShuffleSplit

        sss = StratifiedShuffleSplit(n_splits=1, test_size=val_size, random_state=random_seed)
        train_idx, val_idx = next(sss.split(dev_df, dev_df["class_index"]))

        dev_df["split"] = "UNKNOWN"
        dev_df.iloc[train_idx, dev_df.columns.get_loc("split")] = "train"
        dev_df.iloc[val_idx, dev_df.columns.get_loc("split")] = "val"

    # Combine back
    final_df = pd.concat([dev_df, test_df], ignore_index=True)

    # Print statistics
    split_counts = final_df["split"].value_counts()
    logger.info("Final split counts:\n%s", split_counts)

    for split_name in ["train", "val", "test"]:
        class_counts = final_df[final_df["split"] == split_name]["class_name"].value_counts()
        logger.info("Class distribution in %s:\n%s", split_name, class_counts)

    # Save processed manifest
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)
    logger.info("Split manifest saved to %s", output_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    create_splits(manifest_path=Path("data/interim/dataset_manifest.csv"), output_path=Path("data/processed/split_manifest.csv"))
