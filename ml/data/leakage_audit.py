import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def audit_leakage(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame, patient_col: str = "patientId"):
    """
    Audits the data splits for patient-level leakage.
    Returns a dictionary with the audit results.
    """
    train_patients = set(train_df[patient_col].unique())
    val_patients = set(val_df[patient_col].unique())
    test_patients = set(test_df[patient_col].unique())
    
    overlap_train_val = train_patients.intersection(val_patients)
    overlap_train_test = train_patients.intersection(test_patients)
    overlap_val_test = val_patients.intersection(test_patients)
    
    has_leakage = bool(overlap_train_val or overlap_train_test or overlap_val_test)
    
    report = {
        "total_train_patients": len(train_patients),
        "total_val_patients": len(val_patients),
        "total_test_patients": len(test_patients),
        "overlap_train_val": len(overlap_train_val),
        "overlap_train_test": len(overlap_train_test),
        "overlap_val_test": len(overlap_val_test),
        "has_leakage": has_leakage,
    }
    
    if has_leakage:
        logger.error("Data Leakage Detected! Cross-split patient overlap found.")
        logger.error(f"Train/Val Overlap: {len(overlap_train_val)} patients")
        logger.error(f"Train/Test Overlap: {len(overlap_train_test)} patients")
        logger.error(f"Val/Test Overlap: {len(overlap_val_test)} patients")
    else:
        logger.info("No patient-level leakage detected across splits.")
        
    return report

def generate_leakage_report(split_dir: Path | str, patient_col: str = "patientId"):
    split_dir = Path(split_dir)
    
    train_df = pd.read_csv(split_dir / "train_split.csv")
    val_df = pd.read_csv(split_dir / "val_split.csv")
    test_df = pd.read_csv(split_dir / "test_split.csv")
    
    report = audit_leakage(train_df, val_df, test_df, patient_col=patient_col)
    
    # Save text report
    report_path = split_dir / "leakage_report.txt"
    with open(report_path, "w") as f:
        f.write("=== Data Leakage Audit Report ===\n")
        f.write(f"Train Patients: {report['total_train_patients']}\n")
        f.write(f"Val Patients:   {report['total_val_patients']}\n")
        f.write(f"Test Patients:  {report['total_test_patients']}\n")
        f.write("\n--- Overlaps ---\n")
        f.write(f"Train/Val Overlap:  {report['overlap_train_val']}\n")
        f.write(f"Train/Test Overlap: {report['overlap_train_test']}\n")
        f.write(f"Val/Test Overlap:   {report['overlap_val_test']}\n")
        f.write("\nStatus: ")
        f.write("FAILED (Leakage Detected)\n" if report['has_leakage'] else "PASS (No Leakage)\n")
        
    return report
