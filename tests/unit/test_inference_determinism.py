import torch
from pathlib import Path
from PIL import Image
from ml.models.architectures.factory import create_model
from ml.data.preprocessing.transforms import get_test_transforms

def test_inference_determinism():
    """
    Ensures that for a given model, weights, and image, the preprocessing
    and forward pass are fully deterministic (same image -> same output).
    """
    model = create_model("custom_cnn", num_classes=2, pretrained=False)
    model.eval()
    
    # Use a real image if possible
    images_dir = Path("data/raw/stage_2_train_images")
    if images_dir.exists():
        dcm_path = list(images_dir.glob("*.dcm"))[0]
        import pydicom
        import numpy as np
        dicom = pydicom.dcmread(dcm_path)
        pixel_array = dicom.pixel_array
        if pixel_array.max() > 255:
            pixel_array = (pixel_array / pixel_array.max() * 255).astype(np.uint8)
        elif pixel_array.dtype != np.uint8:
            pixel_array = pixel_array.astype(np.uint8)
        img = Image.fromarray(pixel_array).convert("RGB")
    else:
        # Fallback
        import numpy as np
        np.random.seed(42)
        dummy_img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        img = Image.fromarray(dummy_img_array)
    
    preprocess = get_test_transforms()
    
    tensor1 = preprocess(img).unsqueeze(0)
    tensor2 = preprocess(img).unsqueeze(0)
    
    assert torch.allclose(tensor1, tensor2), "Preprocessing is non-deterministic"
    
    with torch.no_grad():
        out1 = model(tensor1)
        out2 = model(tensor2)
        
    assert torch.allclose(out1, out2), "Forward pass is non-deterministic"
