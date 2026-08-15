import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def check_image_quality(image_path: str, min_resolution: tuple = (100, 100), max_resolution: tuple = (4000, 4000)) -> dict:
    """
    Basic Image Quality Assessment gate.
    Checks resolution, corrupted files, and extreme brightness/contrast.
    """
    result = {
        "status": "PASS",
        "reason": None
    }
    
    try:
        with Image.open(image_path) as img:
            # Check dimensions
            width, height = img.size
            if width < min_resolution[0] or height < min_resolution[1]:
                result["status"] = "REJECTED"
                result["reason"] = f"Resolution {width}x{height} too low (min {min_resolution})"
                return result
                
            if width > max_resolution[0] or height > max_resolution[1]:
                result["status"] = "REJECTED"
                result["reason"] = f"Resolution {width}x{height} too high (max {max_resolution})"
                return result
                
            # Convert to numpy for intensity checks
            img_np = np.array(img.convert("L"))
            mean_intensity = np.mean(img_np)
            std_intensity = np.std(img_np)
            
            # Too dark or too bright
            if mean_intensity < 10.0:
                result["status"] = "REJECTED"
                result["reason"] = "Image is too dark."
                return result
                
            if mean_intensity > 245.0:
                result["status"] = "REJECTED"
                result["reason"] = "Image is too bright / overexposed."
                return result
                
            # No contrast (blank image)
            if std_intensity < 5.0:
                result["status"] = "REJECTED"
                result["reason"] = "Image lacks contrast (potentially blank)."
                return result
                
    except Exception as e:
        logger.error(f"Failed to read image {image_path}: {e}")
        result["status"] = "REJECTED"
        result["reason"] = f"Corrupted or unsupported image file: {e}"
        
    return result
