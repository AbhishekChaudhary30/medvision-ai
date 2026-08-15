# Model Card: MedVision-v1

## Model Details
* **Developer**: MedVision AI Team
* **Model Date**: August 2026
* **Model Version**: v1
* **Model Type**: Convolutional Neural Network (ResNet50 / DenseNet121)
* **Intended Use**: AI-assisted medical imaging research and decision-support prototype.
* **Non-Intended Use**: Autonomous medical diagnosis. This model is NOT a certified medical device and must not be used as a replacement for clinical judgment.

## Intended Use
Primary task: Binary classification of Chest X-Rays to predict `NORMAL` or `PNEUMONIA`.
Target Population: Adult patients undergoing Chest X-Ray examinations.

## Factors
The model was evaluated across various demographic and acquisition protocol subgroups where metadata was available.
Special care was taken to prevent data leakage and evaluate robustness across different hospitals and scanners.

## Metrics
* **Accuracy**: [Pending Final Evaluation]
* **Sensitivity**: [Pending Final Evaluation]
* **Specificity**: [Pending Final Evaluation]
* **AUROC**: [Pending Final Evaluation]
* **AUPRC**: [Pending Final Evaluation]
* **Calibration**: Platt Scaling implemented.

## Training Data
Dataset: Public Chest X-Ray Dataset (e.g. RSNA Pneumonia Detection Challenge / ChestX-ray14).
See the [Data Card](../data-card/ChestXRay.md) for full details.

## Evaluation Data
Patient-level split: 70% Train, 15% Validation, 15% Test.

## Ethical Considerations
* **Bias**: Potential bias due to underrepresentation of certain demographic groups in the training data.
* **Safety**: Includes Out-Of-Distribution (OOD) detection to prevent confident predictions on unsupported images.

## Caveats and Recommendations
This model should be used with human oversight. Explainability artifacts (Grad-CAM) are provided to assist in the interpretation of results but do not represent definitive causal links to pathology.
