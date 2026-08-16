import os
import sys

# Ensure the backend directory itself is in the python path
# so that `from app...` works correctly without finding THIS file
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

import spaces
import gradio as gr
import uvicorn
from app.main import app

# ZeroGPU spaces require at least one function decorated with @spaces.GPU
# and a mounted Gradio app if sdk: gradio is used.
@spaces.GPU
def dummy_gpu_function(name: str):
    return f"Hello {name}"

demo = gr.Interface(fn=dummy_gpu_function, inputs="text", outputs="text")
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
