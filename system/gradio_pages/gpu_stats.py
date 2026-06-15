"""
GPU Statistics Gradio Page for AllTalk TTS

Displays real-time GPU statistics including:
- GPU utilization
- Memory usage
- Temperature
- Power consumption
"""

from pathlib import Path

import gradio as gr

this_dir = Path(__file__).parent.resolve()
main_dir = this_dir.parent.parent.resolve()


def get_gpu_stats():
    """Fetch GPU statistics from the monitoring module"""
    try:
        import sys
        sys.path.insert(0, str(main_dir))
        from system.gpu_monitor import get_gpu_monitor
        
        gpu_monitor = get_gpu_monitor()
        gpu_stats = gpu_monitor.get_gpu_stats()
        
        if not gpu_stats:
            return (
                "No GPU detected",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            )
        
        # For now, display stats for the first GPU
        # Can be extended to support multiple GPUs
        gpu = gpu_stats[0]
        
        gpu_name = f"{gpu['name']} (GPU {gpu['id']})"
        memory_info = f"{gpu['memory_used_gb']:.2f} GB / {gpu['memory_total_gb']:.2f} GB"
        memory_percent = f"{gpu['memory_percent']:.1f}%"
        
        gpu_util = f"{gpu.get('gpu_utilization', 'N/A')}%" if gpu.get('gpu_utilization') is not None else "N/A"
        mem_util = f"{gpu.get('memory_utilization', 'N/A')}%" if gpu.get('memory_utilization') is not None else "N/A"
        temp = f"{gpu.get('temperature', 'N/A')}°C" if gpu.get('temperature') is not None else "N/A"
        
        power = "N/A"
        power_percent = "N/A"
        if gpu.get('power_watts') is not None:
            power = f"{gpu['power_watts']:.1f}W / {gpu['power_limit_watts']:.1f}W"
            power_percent = f"{gpu['power_percent']:.1f}%"
        
        # Additional GPUs info
        additional_info = ""
        if len(gpu_stats) > 1:
            additional_info = f"\n\nAdditional GPUs detected: {len(gpu_stats) - 1}"
            for i, extra_gpu in enumerate(gpu_stats[1:], start=1):
                additional_info += f"\nGPU {extra_gpu['id']}: {extra_gpu['name']} - {extra_gpu['memory_used_gb']:.2f}/{extra_gpu['memory_total_gb']:.2f} GB"
        
        return (
            gpu_name,
            memory_info,
            memory_percent,
            gpu_util,
            mem_util,
            temp,
            power,
            power_percent + additional_info,
        )
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        return (
            error_msg,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        )


def gpu_stats_page():
    """Create the GPU stats Gradio interface"""
    with gr.Tab("GPU Statistics"):
        gr.Markdown("### Real-time GPU Monitoring")
        gr.Markdown("Monitor your GPU's performance, memory usage, temperature, and power consumption.")
        
        with gr.Row():
            with gr.Column():
                gpu_name = gr.Textbox(label="GPU Device", interactive=False)
                memory_info = gr.Textbox(label="Memory Usage", interactive=False)
                memory_percent = gr.Textbox(label="Memory Utilization %", interactive=False)
                gpu_util = gr.Textbox(label="GPU Utilization %", interactive=False)
            
            with gr.Column():
                mem_util = gr.Textbox(label="Memory Controller Utilization %", interactive=False)
                temp = gr.Textbox(label="Temperature", interactive=False)
                power = gr.Textbox(label="Power Usage", interactive=False)
                power_percent = gr.Textbox(label="Power Utilization %", interactive=False)
        
        with gr.Row():
            refresh_button = gr.Button("🔄 Refresh GPU Stats", variant="primary")
            auto_refresh = gr.Checkbox(label="Auto-refresh every 2 seconds", value=False)
        
        # Status message
        status = gr.Markdown("")
        
        # Define refresh action
        refresh_button.click(
            get_gpu_stats,
            outputs=[
                gpu_name,
                memory_info,
                memory_percent,
                gpu_util,
                mem_util,
                temp,
                power,
                power_percent,
            ],
        )
        
        # Auto-refresh functionality
        def auto_refresh_stats():
            import time
            while True:
                time.sleep(2)
                yield get_gpu_stats()
        
        # Load initial stats on page load
        refresh_button.click(lambda: "Stats refreshed!", outputs=status)
        
        gr.Markdown("""
        ---
        **Note:** 
        - GPU Utilization, Temperature, and Power stats require `pynvml` library (NVIDIA GPUs only)
        - Install with: `pip install pynvml` or `pip install nvidia-ml-py`
        - Memory usage is always available when CUDA is detected
        """)


def get_gpu_stats_interface():
    """Return the GPU stats page function"""
    return gpu_stats_page


# Example usage in the main script
if __name__ == "__main__":
    app = gr.Blocks()
    with app:
        gpu_stats_page()
    
    app.launch()
