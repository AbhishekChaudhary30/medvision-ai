import os
import sys

# Ensure the backend directory itself is in the python path
# so that `from app...` works correctly without finding THIS file
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

import spaces
import uvicorn
from app.main import app

# ZeroGPU spaces require at least one function decorated with @spaces.GPU
# otherwise they shut down immediately after startup.
@spaces.GPU
def dummy_gpu_function():
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
