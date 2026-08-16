import os
import sys

# Ensure the backend module is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
