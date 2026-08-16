# Data Card: RSNA Pneumonia Detection Challenge

## Dataset Details
- **Source**: Kaggle (RSNA Pneumonia Detection Challenge)
- **License**: Publicly accessible subject to Kaggle competition rules and RSNA use policies.
- **Modality**: Chest X-Ray (DICOM format)

## Population and Statistics
- **Total Patients**: Approximately 26,684
- **Classes**:
  - `Normal` / `No Lung Opacity / Not Normal` (Class Index 0)
  - `Lung Opacity` (Pneumonia) (Class Index 1)

## Data Processing & Splitting
- **Patient-Level Separation**: Images are strictly split by `patientId` to ensure no patient overlaps across training, validation, and testing sets.
- **Split Ratio**: 70% Training, 15% Validation, 15% Testing.
- **Leakage Audit**: Verified using automated duplicate hash and patient ID overlap scripts.

## Privacy and Ethics
- **De-identification**: The dataset provided by RSNA is fully de-identified and stripped of Protected Health Information (PHI) prior to publication.
- **Ethical Use**: Used exclusively for non-commercial research and educational algorithm development.

## Known Limitations
- **Label Noise**: The labels are derived from expert annotations but may still contain inter-rater variability.
- **Class Imbalance**: The dataset is skewed towards normal/non-pneumonia cases.
- **Demographic Bias**: The dataset primarily represents the demographic distribution of the origin hospital system, which may not generalize universally.
