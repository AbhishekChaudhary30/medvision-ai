import spaces
import os
import sys

# Ensure the backend directory itself is in the python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

import gradio as gr
import uvicorn
from app.main import app

@spaces.GPU
def dummy_gpu_function(name: str):
    return f"Hello {name}"

demo = gr.Interface(fn=dummy_gpu_function, inputs="text", outputs="text")
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
