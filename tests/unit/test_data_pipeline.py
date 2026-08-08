"""Unit tests for Phase 2 data pipeline."""

from pathlib import Path

import pandas as pd

from ml.data.preprocessing.manifest import extract_patient_id
from ml.data.preprocessing.split import create_splits


def test_extract_patient_id():
    """Test patient ID extraction based on Kermany format."""
    assert extract_patient_id("person1000_bacteria_2931.jpeg") == "person1000"
    assert extract_patient_id("IM-0115-0001.jpeg") == "IM-0115"
    assert extract_patient_id("NORMAL2-IM-1427-0001.jpeg") == "NORMAL2-IM-1427"
    assert extract_patient_id("random_file.jpg") == "UNKNOWN"


def test_split_logic(tmp_path: Path):
    """Test that patient-aware split maintains patients and ratios."""
    # Create a fake manifest
    manifest_path = tmp_path / "dataset_manifest.csv"
    output_path = tmp_path / "split_manifest.csv"

    df = pd.DataFrame(
        {
            "sample_id": [f"img{i}" for i in range(10)],
            "original_path": [f"path/img{i}.jpg" for i in range(10)],
            "split_source": ["train"] * 8 + ["test"] * 2,
            "class_name": ["NORMAL", "PNEUMONIA"] * 5,
            "class_index": [0, 1] * 5,
            "patient_id": ["person1", "person1", "person2", "person2", "person3", "person3", "person4", "person4", "test_p1", "test_p2"],
            "validation_status": ["VALID"] * 10,
        }
    )
    df.to_csv(manifest_path, index=False)

    create_splits(manifest_path, output_path, val_size=0.25)

    out_df = pd.read_csv(output_path)

    # Check test set wasn't modified
    test_splits = out_df[out_df["split_source"] == "test"]
    assert all(test_splits["split"] == "test")

    # Check patient separation (a patient cannot be in both train and val)
    train_patients = set(out_df[out_df["split"] == "train"]["patient_id"])
    val_patients = set(out_df[out_df["split"] == "val"]["patient_id"])
    assert len(train_patients.intersection(val_patients)) == 0
