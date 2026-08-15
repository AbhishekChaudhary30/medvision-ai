# Model Card: MedVision AI - Chest X-Ray Classifier

## Model Details
- **Architecture**: ResNet50 / DenseNet121 / EfficientNetB0 (Benchmark champion)
- **Task**: Binary Classification (Pneumonia vs Normal/Other)
- **Framework**: PyTorch
- **Version**: v1.0
- **Intended Use**: Research and educational clinical decision-support prototype.
- **Out of Scope**: Not a certified medical device. Not intended for automated diagnosis or primary screening without human review.

## Training Data
- **Dataset**: RSNA Pneumonia Detection Challenge Dataset
- **Modality**: Chest X-Ray (DICOM)
- **Splitting**: Patient-level split to prevent data leakage (70% Train, 15% Val, 15% Test)

## Preprocessing & Normalization
- **Resize**: 224x224
- **Normalization**: ImageNet standard mean and std (or specific dataset norm)
- **Augmentation**: Rotation (±5°), Scaling (0.95-1.05), Color Jitter.

## Evaluation
- **Metrics Evaluated**: AUROC, AUPRC, F1-Score, Sensitivity, Specificity, Accuracy.
- **Reliability Checks**: 
  - Platt Scaling for confidence calibration.
  - OOD Detection using entropy and confidence thresholds.
  - Image Quality Gates (brightness, contrast, resolution).

## Limitations
- **Generalization**: The model has only been trained on the RSNA dataset, which primarily contains adult anterior-posterior (AP) radiographs. Performance on pediatric patients or lateral views may be significantly degraded.
- **Domain Shift**: Performance may drop when applied to X-rays from different institutions or scanners with different acquisition protocols.
- **Explainability**: Grad-CAM heatmaps highlight regions of high activation but do not definitively prove causality. They are provided as supportive visual context, not absolute medical evidence.
