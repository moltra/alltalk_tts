"""
Model Download UI Module for Gradio Interface

Provides UI components for downloading TTS models through the Gradio interface.
"""

import os
import subprocess
import threading
from pathlib import Path

this_dir = Path(__file__).parent.parent.resolve()


def check_model_status(engine: str) -> tuple[bool, str]:
    """Check if a model is downloaded for the given engine."""
    models_dir = this_dir / "models" / engine
    
    if not models_dir.exists():
        return False, f"❌ No models found for {engine}"
    
    # Check for model files
    model_files = (
        list(models_dir.rglob("*.pth")) +
        list(models_dir.rglob("*.onnx")) +
        list(models_dir.rglob("*.json")) +
        list(models_dir.rglob("*.bin"))
    )
    
    if model_files:
        file_count = len(model_files)
        total_size = sum(f.stat().st_size for f in model_files if f.exists()) / (1024 * 1024)  # MB
        return True, f"✅ {file_count} model files found ({total_size:.1f} MB)"
    
    return False, f"⚠️ Directory exists but no model files found"


def download_model_async(engine: str, progress_callback=None) -> str:
    """Download a model asynchronously using the CLI script."""
    try:
        # Use the download_model.py CLI script
        script_path = this_dir / "download_model.py"
        
        if progress_callback:
            progress_callback(f"🚀 Starting download for {engine}...")
        
        # Run the download script
        result = subprocess.run(
            ["python", str(script_path), "--model", engine, "--force"],
            capture_output=True,
            text=True,
            cwd=str(this_dir)
        )
        
        if result.returncode == 0:
            return f"✅ Successfully downloaded {engine} model!\n\n{result.stdout}"
        else:
            return f"❌ Failed to download {engine} model\n\nError:\n{result.stderr}\n\nOutput:\n{result.stdout}"
    
    except Exception as e:
        return f"❌ Error during download: {str(e)}"


def get_model_info(engine: str) -> str:
    """Get information about available models for an engine."""
    available_models_path = this_dir / "system" / "tts_engines" / engine / "available_models.json"
    
    if not available_models_path.exists():
        return f"ℹ️ No automatic download available for {engine}.\nModels must be downloaded manually."
    
    try:
        import json
        with open(available_models_path) as f:
            data = json.load(f)
            info = f"📦 **{engine.upper()} Models**\n\n"
            info += f"Default model: {data.get('first_start_model', 'N/A')}\n\n"
            info += "Available models:\n"
            for model in data.get("models", []):
                info += f"• {model.get('model_name', 'Unknown')}\n"
            return info
    except Exception as e:
        return f"❌ Error reading model info: {str(e)}"


def create_model_download_tab():
    """Create the model download tab for Gradio UI."""
    import gradio as gr
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📥 Download TTS Models")
            gr.Markdown(
                "Download models on-demand to keep your Docker image small. "
                "Only download the models you need!"
            )
            
            engine_dropdown = gr.Dropdown(
                choices=["xtts", "piper", "vits", "f5tts", "parler"],
                label="Select TTS Engine",
                value="xtts"
            )
            
            with gr.Row():
                check_btn = gr.Button("🔍 Check Status", variant="secondary")
                download_btn = gr.Button("📥 Download Model", variant="primary")
            
            status_output = gr.Textbox(
                label="Status",
                lines=3,
                interactive=False
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### ℹ️ Model Information")
            info_output = gr.Markdown("Select an engine to see available models")
    
    # Event handlers
    def on_engine_change(engine):
        status_exists, status_msg = check_model_status(engine)
        info = get_model_info(engine)
        return status_msg, info
    
    def on_check_status(engine):
        _, status_msg = check_model_status(engine)
        return status_msg
    
    def on_download(engine):
        return download_model_async(engine)
    
    engine_dropdown.change(
        fn=on_engine_change,
        inputs=[engine_dropdown],
        outputs=[status_output, info_output]
    )
    
    check_btn.click(
        fn=on_check_status,
        inputs=[engine_dropdown],
        outputs=[status_output]
    )
    
    download_btn.click(
        fn=on_download,
        inputs=[engine_dropdown],
        outputs=[status_output]
    )
    
    # Initialize with default engine
    engine_dropdown.change(
        fn=on_engine_change,
        inputs=[engine_dropdown],
        outputs=[status_output, info_output]
    )
