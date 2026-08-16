import os
from pathlib import Path
import pydicom
import torch
from torch.utils.data import Dataset
import pandas as pd
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)

class XRayDataset(Dataset):
    """
    Medical Image Dataset for Chest X-Ray classification.
    Supports both standard images (PNG, JPEG) and DICOM formats.
    """
    def __init__(self, metadata_df: pd.DataFrame, image_dir: Path | str, transform=None, is_dicom=True):
        self.metadata = metadata_df
        self.image_dir = Path(image_dir)
        self.transform = transform
        self.is_dicom = is_dicom
        
        # Verify dataset
        if 'patientId' not in self.metadata.columns or 'Target' not in self.metadata.columns:
            raise ValueError("Metadata must contain 'patientId' and 'Target' columns.")
            
    def __len__(self):
        return len(self.metadata)
        
    def __getitem__(self, idx):
        row = self.metadata.iloc[idx]
        patient_id = row['patientId']
        target = row['Target']
        
        # Resolve image path
        ext = ".dcm" if self.is_dicom else ".png"
        img_path = self.image_dir / f"{patient_id}{ext}"
        
        # Load image
        image = self._load_image(img_path)
        
        # Apply transforms
        if self.transform is not None:
            image = self.transform(image)
            
        # Target must be float tensor for BCEWithLogitsLoss
        target_tensor = torch.tensor(target, dtype=torch.float32).unsqueeze(0)
        
        return image, target_tensor
        
    def _load_image(self, img_path: Path):
        if not img_path.exists():
            # Sometimes dataset has nested folders, a more robust search could be added
            raise FileNotFoundError(f"Image not found at {img_path}")
            
        if self.is_dicom:
            try:
                dicom = pydicom.dcmread(img_path)
                # Convert pixel data to float32
                img_array = dicom.pixel_array.astype(np.float32)
                
                # Handle Photometric Interpretation
                if hasattr(dicom, 'PhotometricInterpretation') and dicom.PhotometricInterpretation == 'MONOCHROME1':
                    # Invert
                    img_array = np.max(img_array) - img_array
                    
                # Normalize to 0-255
                img_array = img_array - np.min(img_array)
                max_val = np.max(img_array)
                if max_val > 0:
                    img_array = img_array / max_val * 255.0
                    
                # Convert to PIL for standard torchvision transforms
                image = Image.fromarray(img_array.astype(np.uint8)).convert("RGB")
            except Exception as e:
                logger.error(f"Failed to read DICOM {img_path}: {e}")
                # Return blank image in case of catastrophic failure, or raise
                raise e
        else:
            image = Image.open(img_path).convert("RGB")
            
        return image
