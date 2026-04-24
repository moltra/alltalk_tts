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
        total_size = sum(f.stat().st_size for f in model_files if f.exists()) / (1024 * 1024)  # MB
        
        # List actual model names based on directory structure
        if engine == "piper":
            # Piper models are stored as .onnx files directly in the directory
            onnx_files = list(models_dir.glob("*.onnx"))
            model_names = [f.stem for f in onnx_files]  # Remove .onnx extension
            if model_names:
                models_list = ", ".join(sorted(model_names))
                return True, f"✅ Downloaded: {models_list}\n📦 Total size: {total_size:.1f} MB"
            else:
                return True, f"✅ Model files found ({total_size:.1f} MB)"
        else:
            # For other engines, check for subdirectory with model version
            subdirs = [d for d in models_dir.iterdir() if d.is_dir()]
            if subdirs:
                # Use the subdirectory name as the model version
                model_version = subdirs[0].name
                return True, f"✅ {engine.upper()} model: {model_version} ({total_size:.1f} MB)"
            else:
                return True, f"✅ {engine.upper()} model downloaded ({total_size:.1f} MB)"
    
    return False, f"⚠️ Directory exists but no model files found"


def download_model_async(engine: str, model_name: str = None, progress=None) -> str:
    """Download a model by calling download_tts_model directly with real-time progress tracking."""
    try:
        # Import directly to avoid subprocess dependency issues
        from system.config.firstrun import download_tts_model, update_tts_engines
        
        def progress_callback(progress_val, desc):
            """Bridge between firstrun callback and Gradio progress."""
            if progress:
                try:
                    # Ensure progress_val is a float between 0 and 1
                    progress_val = float(progress_val)
                    progress_val = max(0.0, min(1.0, progress_val))
                    progress(progress_val, desc=desc)
                except Exception as e:
                    print(f"Progress update error: {e}")
        
        model_display = model_name if model_name else engine
        if progress:
            progress(0.01, desc=f"🚀 Starting download for {model_display}...")
        
        # Call download function with progress callback and specific model name
        success = download_tts_model(engine, model_name=model_name, progress_callback=progress_callback)
        
        if success:
            update_tts_engines(engine)
            if progress:
                progress(1.0, desc="✅ Download complete!")
            return f"✅ Successfully downloaded {model_display} model!\n\nModel location: {this_dir / 'models' / engine}"
        else:
            return f"❌ Failed to download {model_display} model\n\nPlease check the container logs for details."
    
    except Exception as e:
        return f"❌ Error during download: {str(e)}"


def get_model_info(engine: str) -> str:
    """Get information about available models for an engine."""
    available_models_path = this_dir / "system" / "tts_engines" / engine / "available_models.json"
    
    if not available_models_path.exists():
        # Provide helpful information even without JSON file
        model_info = f"📦 **{engine.upper()} Models**\n\n"
        model_info += f"ℹ️ The `available_models.json` file for {engine} is not present.\n\n"
        model_info += f"**Alternative download methods:**\n"
        model_info += f"• Use the CLI: `python download_model.py --tts_model {engine}`\n"
        model_info += f"• Use Docker CLI: `docker exec alltalk-dev python download_model.py --tts_model {engine}`\n"
        model_info += f"• Download models manually from the official repository\n\n"
        model_info += f"**Model sizes (approximate):**\n"
        if engine == "xtts":
            model_info += f"• XTTS v2.0.3: ~1.8GB\n"
        elif engine == "piper":
            model_info += f"• Piper models: ~50-100MB each\n"
        elif engine == "vits":
            model_info += f"• VITS models: ~100-200MB each\n"
        elif engine == "f5tts":
            model_info += f"• F5-TTS: ~500MB\n"
        elif engine == "parler":
            model_info += f"• Parler: ~1GB\n"
        return model_info
    
    try:
        import json
        with open(available_models_path) as f:
            data = json.load(f)
            info = f"📦 **{engine.upper()} Models**\n\n"
            info += f"Default model: `{data.get('first_start_model', 'N/A')}`\n\n"
            
            # Special formatting for Piper models
            if engine == "piper":
                models = data.get("models", [])
                # Group by language
                lang_groups = {}
                for model in models:
                    name = model.get('model_name', 'Unknown')
                    # Extract language code (e.g., "en_US" from "en_US-ljspeech-high")
                    parts = name.split('-')
                    if len(parts) >= 2:
                        lang_code = parts[0]
                        voice_name = parts[1]
                        quality = parts[2] if len(parts) > 2 else 'medium'
                        
                        if lang_code not in lang_groups:
                            lang_groups[lang_code] = []
                        
                        lang_groups[lang_code].append({
                            'name': name,
                            'voice': voice_name,
                            'quality': quality
                        })
                
                # Display grouped models with better alignment
                info += f"**Available models ({len(models)} total):**\n\n"
                
                # Find max name length for alignment
                max_name_len = max(len(m.get('model_name', '')) for m in models) if models else 0
                
                for lang_code in sorted(lang_groups.keys()):
                    models_list = sorted(lang_groups[lang_code], key=lambda x: (x['quality'], x['voice']))
                    info += f"**{lang_code}:**\n"
                    for m in models_list:
                        # Quality indicator
                        quality_emoji = {'x_low': '🔹', 'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(m['quality'], '⚪')
                        # Pad name for alignment
                        padded_name = m['name'].ljust(max_name_len)
                        info += f"  {quality_emoji} `{padded_name}` {m['quality']}\n"
                    info += "\n"
                
                info += f"**Quality legend:** 🔴 high  🟡 medium  🟢 low  🔹 x_low\n"
            else:
                # Default formatting for other engines
                info += "Available models:\n"
                for model in data.get("models", []):
                    info += f"• {model.get('model_name', 'Unknown')}\n"
            
            return info
    except Exception as e:
        return f"❌ Error reading model info: {str(e)}"


def get_available_models(engine: str) -> list:
    """Get list of available model names for an engine."""
    available_models_path = this_dir / "system" / "tts_engines" / engine / "available_models.json"
    
    if not available_models_path.exists():
        return []
    
    try:
        import json
        with open(available_models_path) as f:
            data = json.load(f)
            models = data.get("models", [])
            return [model.get('model_name', '') for model in models]
    except Exception:
        return []


def get_model_details(engine: str) -> list:
    """Get detailed model information for filtering."""
    available_models_path = this_dir / "system" / "tts_engines" / engine / "available_models.json"
    
    if not available_models_path.exists():
        return []
    
    try:
        import json
        with open(available_models_path) as f:
            data = json.load(f)
            models = data.get("models", [])
            details = []
            for model in models:
                name = model.get('model_name', '')
                parts = name.split('-')
                if len(parts) >= 2:
                    lang_code = parts[0]
                    quality = parts[2] if len(parts) > 2 else 'medium'
                    details.append({
                        'name': name,
                        'language': lang_code,
                        'quality': quality
                    })
            return details
    except Exception:
        return []


def sort_qualities(qualities: list) -> list:
    """Sort qualities from low to high instead of alphabetically."""
    quality_order = {'x_low': 0, 'low': 1, 'medium': 2, 'high': 3}
    return sorted(qualities, key=lambda q: quality_order.get(q, 999))


def filter_models(models: list, language_filter: str = "", quality_filter: str = "") -> list:
    """Filter models by language and quality."""
    filtered = models
    if language_filter:
        filtered = [m for m in filtered if m['language'] == language_filter]
    if quality_filter:
        filtered = [m for m in filtered if m['quality'] == quality_filter]
    return filtered


def create_model_download_tab():
    """Create the model download tab for Gradio UI."""
    import gradio as gr
    
    # Get initial values
    initial_status, initial_info = check_model_status("xtts"), get_model_info("xtts")
    initial_models = get_available_models("xtts")
    initial_details = get_model_details("xtts")
    
    # Extract unique languages and qualities for filters
    initial_languages = sorted(list(set(m['language'] for m in initial_details)))
    initial_qualities = sort_qualities(list(set(m['quality'] for m in initial_details)))
    
    # Filters are only enabled for Piper
    is_piper_initial = False
    
    with gr.Blocks():
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
                    language_filter = gr.Dropdown(
                        choices=[""] + initial_languages,
                        label="Filter by Language",
                        value="",
                        interactive=is_piper_initial
                    )
                    quality_filter = gr.Dropdown(
                        choices=[""] + initial_qualities,
                        label="Filter by Quality",
                        value="",
                        interactive=is_piper_initial
                    )
                
                model_dropdown = gr.CheckboxGroup(
                    choices=initial_models,
                    label="Select Models to Download",
                    value=[],
                    interactive=True
                )
                
                with gr.Row():
                    select_all_btn = gr.Button("✅ Select All", variant="secondary", size="sm")
                    clear_btn = gr.Button("🗑️ Clear Selection", variant="secondary", size="sm")
                
                with gr.Row():
                    check_btn = gr.Button("🔍 Check Status", variant="secondary")
                    download_btn = gr.Button("📥 Download Selected Models", variant="primary")
                
                status_output = gr.Textbox(
                    label="Status",
                    lines=3,
                    interactive=False,
                    value=initial_status[1]
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### ℹ️ Model Information")
                info_output = gr.Markdown(value=initial_info)
    
    # Event handlers
    def on_engine_change(engine):
        status_exists, status_msg = check_model_status(engine)
        info = get_model_info(engine)
        details = get_model_details(engine)
        models = [m['name'] for m in details]
        languages = sorted(list(set(m['language'] for m in details)))
        qualities = sort_qualities(list(set(m['quality'] for m in details)))
        
        # Only enable filters for Piper (which has language/quality structure)
        is_piper = engine == "piper"
        
        return (
            status_msg, 
            info,
            gr.Dropdown(choices=[""] + languages if is_piper else [""], value="", interactive=is_piper),
            gr.Dropdown(choices=[""] + qualities if is_piper else [""], value="", interactive=is_piper),
            gr.CheckboxGroup(choices=models, value=[])
        )
    
    def on_filter_change(engine, language, quality):
        details = get_model_details(engine)
        filtered = filter_models(details, language, quality)
        return gr.CheckboxGroup(choices=[m['name'] for m in filtered], value=[])
    
    def on_select_all(engine, language, quality):
        details = get_model_details(engine)
        filtered = filter_models(details, language, quality)
        return gr.CheckboxGroup(choices=[m['name'] for m in filtered], value=[m['name'] for m in filtered])
    
    def on_clear_selection():
        return gr.CheckboxGroup(value=[])
    
    def on_check_status(engine):
        _, status_msg = check_model_status(engine)
        return status_msg
    
    def on_download(engine, models, progress=gr.Progress()):
        # For non-Piper engines, download the default model without selection
        if not models and engine != "piper":
            if progress:
                progress(0.01, desc=f"Downloading {engine.upper()} model...")
            result = download_model_async(engine, None, progress)
            if progress:
                progress(1.0, desc="Download complete!")
            return result
        
        if not models:
            return "❌ No models selected. Please select at least one model to download."
        
        results = []
        total_models = len(models)
        
        for idx, model in enumerate(models):
            if progress:
                progress((idx / total_models), desc=f"Downloading model {idx + 1}/{total_models}: {model}")
            result = download_model_async(engine, model, progress)
            results.append(result)
        
        if progress:
            progress(1.0, desc="All downloads complete!")
        
        successful = sum(1 for r in results if "Successfully" in r)
        failed = total_models - successful
        
        return f"✅ Download complete!\n\nSuccessful: {successful}/{total_models}\nFailed: {failed}/{total_models}\n\n" + "\n".join(results)
    
    engine_dropdown.change(
        fn=on_engine_change,
        inputs=[engine_dropdown],
        outputs=[status_output, info_output, language_filter, quality_filter, model_dropdown]
    )
    
    language_filter.change(
        fn=on_filter_change,
        inputs=[engine_dropdown, language_filter, quality_filter],
        outputs=[model_dropdown]
    )
    
    quality_filter.change(
        fn=on_filter_change,
        inputs=[engine_dropdown, language_filter, quality_filter],
        outputs=[model_dropdown]
    )
    
    select_all_btn.click(
        fn=on_select_all,
        inputs=[engine_dropdown, language_filter, quality_filter],
        outputs=[model_dropdown]
    )
    
    clear_btn.click(
        fn=on_clear_selection,
        outputs=[model_dropdown]
    )
    
    check_btn.click(
        fn=on_check_status,
        inputs=[engine_dropdown],
        outputs=[status_output]
    )
    
    download_btn.click(
        fn=on_download,
        inputs=[engine_dropdown, model_dropdown],
        outputs=[status_output]
    )
