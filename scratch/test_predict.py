import sys
import os
from pathlib import Path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from app.services.ml_service import process_and_predict

import PIL.Image
img = PIL.Image.new("RGB", (224, 224), color="black")
img.save("dummy_test.jpg")

try:
    print("Testing chest-xray...")
    result = process_and_predict(Path("dummy_test.jpg"), sample_id="test", modality="chest-xray")
    print("Result:", result)
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    print("\nTesting brain-mri...")
    result = process_and_predict(Path("dummy_test.jpg"), sample_id="test", modality="brain-mri")
    print("Result:", result)
except Exception as e:
    import traceback
    traceback.print_exc()
