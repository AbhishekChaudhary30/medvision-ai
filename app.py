import gradio as gr
import spaces
import json
import logging
from pathlib import Path
from PIL import Image

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path so we can import services
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.services.ml_service import process_and_predict, process_explainability
from app.services.suggestions_service import generate_clinical_suggestions

theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
)

custom_css = """
body { background-color: #0f172a; color: #f8fafc; }
.gradio-container { max-width: 1200px !important; margin: auto; }
.glow-text { text-shadow: 0 0 10px rgba(59, 130, 246, 0.5); }
.stat-badge { background: #ef4444; color: white; padding: 4px 12px; border-radius: 99px; font-weight: bold; font-size: 0.8rem; box-shadow: 0 0 10px rgba(239, 68, 68, 0.8); animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
"""

# The inference function must be decorated with @spaces.GPU for ZeroGPU spaces
@spaces.GPU
def analyze_image(image, modality, age, gender, notes):
    if image is None:
        return "Please upload an image.", None, None, gr.update(visible=False)
        
    try:
        image_path = Path(image)
        
        # Run prediction
        result = process_and_predict(image_path, sample_id="demo", modality=modality)
        
        # Generate suggestions
        suggestions = generate_clinical_suggestions(
            modality=modality,
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
            patient_age=age,
            patient_gender=gender,
            clinical_notes=notes
        )
        
        # Run explainability
        explanation = process_explainability(
            file_path=image_path,
            target_class=result["predicted_class_index"],
            method="gradcam",
            modality=modality
        )
        
        # Format results
        predicted_class = result["predicted_class"]
        confidence = result["confidence"] * 100
        
        status_html = ""
        if "Malignant" in predicted_class or "Pneumonia" in predicted_class or "Adenomatous" in predicted_class or "Positive" in predicted_class:
            status_html = f"<div style='text-align:center'><span class='stat-badge'>STAT / CRITICAL FINDING</span></div>"
            
        summary = f"""
        {status_html}
        ### AI Prediction
        - **Modality:** {modality}
        - **Predicted Class:** {predicted_class}
        - **Confidence:** {confidence:.2f}%
        - **Uncertainty:** {result.get('uncertainty_status', 'LOW')}
        
        ### Clinical Suggestions
        {suggestions.get('ai_interpretation', '')}
        
        **Recommendations:**
        {chr(10).join(['- ' + r for r in suggestions.get('recommendations', [])])}
        """
        
        # Return heatmap if available
        heatmap_img = None
        if explanation and explanation.get("overlay_image_base64"):
            import base64
            from io import BytesIO
            img_data = base64.b64decode(explanation["overlay_image_base64"])
            heatmap_img = Image.open(BytesIO(img_data))
            
        return summary, heatmap_img, json.dumps(result, indent=2), gr.update(visible=True)
    except Exception as e:
        logger.exception("Error in analysis")
        return f"Error analyzing image: {str(e)}", None, None, gr.update(visible=False)

with gr.Blocks(theme=theme, css=custom_css) as app:
    gr.HTML("<h1 class='glow-text' style='text-align:center; font-size: 2.5rem; margin-bottom: 0;'>MedVision Enterprise PACS</h1>")
    gr.HTML("<p style='text-align:center; color: #94a3b8; margin-bottom: 2rem;'>AI-Powered Triage & Clinical Decision Support System</p>")
    
    with gr.Tabs():
        with gr.TabItem("Analysis Workspace"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 1. Patient Demographics & Modality")
                    modality = gr.Dropdown(
                        choices=["chest-xray", "brain-mri", "skin-lesion", "mammography", "colonoscopy"],
                        value="chest-xray",
                        label="Modality"
                    )
                    age = gr.Number(label="Patient Age", value=45)
                    gender = gr.Dropdown(choices=["Male", "Female", "Other"], value="Male", label="Patient Gender")
                    notes = gr.Textbox(label="Clinical Notes", lines=2)
                    
                    gr.Markdown("### 2. Medical Image")
                    image_input = gr.Image(type="filepath", label="Upload Scan (JPEG/PNG)")
                    
                    analyze_btn = gr.Button("Run AI Analysis", variant="primary")
                    
                with gr.Column(scale=1):
                    gr.Markdown("### AI Insights & Explainability")
                    summary_output = gr.Markdown("Upload an image and run analysis to see results here.")
                    heatmap_output = gr.Image(label="Grad-CAM Explainability (Heatmap)", type="pil", interactive=False)
                    
            with gr.Row(visible=False) as details_row:
                with gr.Accordion("Raw Diagnostic Data JSON", open=False):
                    json_output = gr.JSON()

    analyze_btn.click(
        fn=analyze_image,
        inputs=[image_input, modality, age, gender, notes],
        outputs=[summary_output, heatmap_output, json_output, details_row]
    )

if __name__ == "__main__":
    app.launch()
