import os
import numpy as np
import pandas as pd
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import UID
import datetime

def generate_synthetic_dicom(output_path, patient_id, class_index):
    # Create empty dataset
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = UID('1.2.840.10008.5.1.4.1.1.7') # Secondary Capture
    file_meta.MediaStorageSOPInstanceUID = UID('1.2.3')
    file_meta.ImplementationClassUID = UID('1.2.3.4')
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    
    ds = FileDataset(output_path, {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    # Add minimal required DICOM attributes
    ds.PatientName = f"Synthetic^{patient_id}"
    ds.PatientID = patient_id
    ds.StudyInstanceUID = "1.2.3.4.5"
    ds.SeriesInstanceUID = "1.2.3.4.5.6"
    ds.SOPInstanceUID = "1.2.3.4.5.6.7"
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    
    ds.Modality = "CR" # Computed Radiography
    
    # Generate image data (224x224)
    np.random.seed(hash(patient_id) % (2**32))
    
    if class_index == 1:
        # PNEUMONIA: brighter cloudy regions
        base = np.random.normal(120, 20, (224, 224)).astype(np.float32)
        # Add a "cloud"
        y, x = np.ogrid[-112:112, -112:112]
        mask = x**2 + y**2 <= 50**2
        base[mask] += 60
    else:
        # NORMAL: standard noise
        base = np.random.normal(80, 15, (224, 224)).astype(np.float32)
        
    pixel_array = np.clip(base, 0, 255).astype(np.uint8)
    
    ds.Rows = pixel_array.shape[0]
    ds.Columns = pixel_array.shape[1]
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.PixelData = pixel_array.tobytes()
    
    ds.is_little_endian = True
    ds.is_implicit_VR = True
    
    ds.save_as(output_path)

def main():
    raw_dir = "data/raw"
    images_dir = os.path.join(raw_dir, "stage_2_train_images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Generate 100 synthetic patients
    data = []
    print("Generating synthetic DICOM images...")
    for i in range(100):
        patient_id = f"SYNTH_{i:04d}"
        target = np.random.choice([0, 1], p=[0.7, 0.3]) # 30% pneumonia
        
        output_path = os.path.join(images_dir, f"{patient_id}.dcm")
        generate_synthetic_dicom(output_path, patient_id, target)
        
        # Add to labels
        data.append({
            "patientId": patient_id,
            "x": "", "y": "", "width": "", "height": "",
            "Target": target
        })
    
    labels_df = pd.DataFrame(data)
    labels_path = os.path.join(raw_dir, "stage_2_train_labels.csv")
    labels_df.to_csv(labels_path, index=False)
    print(f"Generated {len(data)} images and labels at {labels_path}")

if __name__ == "__main__":
    main()
