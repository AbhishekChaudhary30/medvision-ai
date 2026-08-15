import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def create_patient_level_splits(
    metadata_df: pd.DataFrame,
    patient_col: str = "patientId",
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Perform a patient-level split to prevent data leakage.
    Ensures that multiple images from the same patient stay in the same split.
    """
    if patient_col not in metadata_df.columns:
        raise ValueError(f"Patient column '{patient_col}' not found in metadata.")
        
    # First split: (Train + Val) vs Test
    gss_test = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_val_idx, test_idx = next(gss_test.split(metadata_df, groups=metadata_df[patient_col]))
    
    df_train_val = metadata_df.iloc[train_val_idx].reset_index(drop=True)
    df_test = metadata_df.iloc[test_idx].reset_index(drop=True)
    
    # Second split: Train vs Val (val_size is adjusted to be relative to the remaining train+val set)
    val_prop = val_size / (1.0 - test_size)
    gss_val = GroupShuffleSplit(n_splits=1, test_size=val_prop, random_state=random_state)
    train_idx, val_idx = next(gss_val.split(df_train_val, groups=df_train_val[patient_col]))
    
    df_train = df_train_val.iloc[train_idx].reset_index(drop=True)
    df_val = df_train_val.iloc[val_idx].reset_index(drop=True)
    
    logger.info("Splits generated: Train=%d, Val=%d, Test=%d", len(df_train), len(df_val), len(df_test))
    return df_train, df_val, df_test

def split_and_save_dataset(
    metadata_path: Path | str,
    output_dir: Path | str,
    patient_col: str = "patientId",
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42
):
    metadata_path = Path(metadata_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.read_csv(metadata_path)
    
    # Drop identical duplicates to avoid split skew (if they are exact duplicate rows)
    # This might depend on the specific dataset; for RSNA, multiple bounding boxes for the same patient exist.
    # We should aggregate them to unique patients for the split calculation if we want purely unique images,
    # but GroupShuffleSplit handles the grouping natively.
    
    df_train, df_val, df_test = create_patient_level_splits(
        metadata_df=df,
        patient_col=patient_col,
        test_size=test_size,
        val_size=val_size,
        random_state=random_state
    )
    
    df_train.to_csv(output_dir / "train_split.csv", index=False)
    df_val.to_csv(output_dir / "val_split.csv", index=False)
    df_test.to_csv(output_dir / "test_split.csv", index=False)
    
    return df_train, df_val, df_test
