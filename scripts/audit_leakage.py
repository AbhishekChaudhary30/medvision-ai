"""Leakage audit script to verify dataset splits."""

import argparse
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def audit_leakage(manifest_path: Path, report_path: Path) -> None:
    """Audit the split manifest for patient leakage across splits."""
    if not manifest_path.exists():
        logger.error(f"Manifest not found at {manifest_path}. Cannot perform audit.")
        return

    logger.info(f"Auditing manifest: {manifest_path}")
    df = pd.read_csv(manifest_path)

    if "patientId" not in df.columns or "split" not in df.columns:
        logger.error("Manifest missing required columns 'patientId' or 'split'.")
        return

    # Check for duplicate images (assuming original_path is unique per image)
    if "original_path" in df.columns:
        duplicate_images = df["original_path"].duplicated().sum()
    else:
        duplicate_images = 0

    # Get sets of patients in each split
    train_patients = set(df[df["split"] == "train"]["patientId"])
    val_patients = set(df[df["split"] == "val"]["patientId"])
    test_patients = set(df[df["split"] == "test"]["patientId"])

    # Calculate intersections
    train_val_overlap = train_patients.intersection(val_patients)
    train_test_overlap = train_patients.intersection(test_patients)
    val_test_overlap = val_patients.intersection(test_patients)

    total_overlap = len(train_val_overlap) + len(train_test_overlap) + len(val_test_overlap)

    # Generate Report
    report = [
        "==============================",
        "DATASET LEAKAGE AUDIT REPORT",
        "==============================",
        f"Manifest: {manifest_path}",
        f"Total Patients: {df['patientId'].nunique()}",
        "",
        "Splits:",
        f"  Train: {len(train_patients)} patients",
        f"  Val:   {len(val_patients)} patients",
        f"  Test:  {len(test_patients)} patients",
        "",
        "Leakage Analysis:",
        f"  Duplicate Images: {duplicate_images}",
        f"  Train/Val Overlap: {len(train_val_overlap)} patients",
        f"  Train/Test Overlap: {len(train_test_overlap)} patients",
        f"  Val/Test Overlap: {len(val_test_overlap)} patients",
        "",
        f"Overall Status: {'FAIL' if total_overlap > 0 or duplicate_images > 0 else 'PASS'}",
        "==============================",
    ]

    report_content = "\n".join(report)
    logger.info("\n" + report_content)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_content)
    logger.info(f"Leakage report written to {report_path}")

    if total_overlap > 0 or duplicate_images > 0:
        logger.error("DATA LEAKAGE DETECTED! Do not proceed with training.")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit dataset for leakage.")
    parser.add_argument("--manifest", type=Path, default=Path("data/processed/split_manifest.csv"), help="Path to manifest")
    parser.add_argument("--report", type=Path, default=Path("docs/evaluation/leakage_report.txt"), help="Output report path")
    args = parser.parse_args()
    
    audit_leakage(args.manifest, args.report)
