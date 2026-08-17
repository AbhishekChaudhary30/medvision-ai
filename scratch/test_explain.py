import sys
import os
from pathlib import Path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from app.services.ml_service import process_explainability
import PIL.Image

img = PIL.Image.new("RGB", (224, 224), color="black")
img.save("dummy_test.jpg")

try:
    print("Testing explainability...")
    # class 1 for chest-xray is Pneumonia
    result = process_explainability(Path("dummy_test.jpg"), target_class=1, method="gradcam", modality="chest-xray")
    if result:
        print("Success! Overlay length:", len(result["overlay_image_base64"]))
    else:
        print("Explainability returned None")
except Exception as e:
    import traceback
    traceback.print_exc()
