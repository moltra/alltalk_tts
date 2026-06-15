# GPU Statistics Feature

## Overview

GPU statistics monitoring has been added to AllTalk TTS, allowing you to monitor your GPU's performance in real-time through the Gradio UI.

## Features

The GPU stats display includes:

- **GPU Device Information**: Name and ID of your GPU(s)
- **Memory Usage**: Current memory usage (used/total in GB and percentage)
- **GPU Utilization**: Real-time GPU usage percentage (requires pynvml)
- **Memory Controller Utilization**: Memory bandwidth usage (requires pynvml)
- **Temperature**: GPU temperature in Celsius (requires pynvml)
- **Power Usage**: Current power draw and limit in Watts (requires pynvml)

## Location in UI

The GPU Statistics tab is located in:
**Global Settings → GPU Statistics**

## Requirements

### Basic Functionality (Memory Usage Only)
- CUDA-capable NVIDIA GPU
- PyTorch with CUDA support (already required by AllTalk)

### Full Functionality (All Stats)
For complete GPU monitoring including utilization, temperature, and power stats, install pynvml:

```bash
pip install pynvml
```

Or:

```bash
pip install nvidia-ml-py
```

## API Endpoint

GPU stats are also available via REST API:

**Endpoint**: `GET /api/gpustats`

**Response Format**:
```json
{
  "gpu_stats": [
    {
      "id": 0,
      "name": "NVIDIA GeForce RTX 3090",
      "memory_used_gb": 8.5,
      "memory_total_gb": 24.0,
      "memory_percent": 35.4,
      "gpu_utilization": 45,
      "memory_utilization": 30,
      "temperature": 65,
      "power_watts": 250.5,
      "power_limit_watts": 350.0,
      "power_percent": 71.6
    }
  ]
}
```

## Usage

1. **In Gradio UI**:
   - Navigate to **Global Settings** tab
   - Click on **GPU Statistics** sub-tab
   - Click **🔄 Refresh GPU Stats** button to update stats
   - Optionally enable **Auto-refresh every 2 seconds** for continuous monitoring

2. **Via API**:
   ```bash
   curl http://localhost:7851/api/gpustats
   ```

3. **Programmatically**:
   ```python
   from system.gpu_monitor import get_gpu_monitor
   
   monitor = get_gpu_monitor()
   stats = monitor.get_gpu_stats()
   print(monitor.get_summary())
   ```

## Multi-GPU Support

The system automatically detects all available CUDA GPUs. The primary GPU (GPU 0) stats are displayed in detail, with additional GPUs listed in the "Power Utilization %" field.

## Troubleshooting

### "No GPU detected"
- Ensure you have a CUDA-capable NVIDIA GPU
- Verify PyTorch is installed with CUDA support
- Check that CUDA drivers are properly installed

### Stats showing "N/A"
- Install pynvml: `pip install pynvml`
- Ensure NVIDIA drivers are up to date
- Check that nvidia-smi command works in terminal

### Permission Issues
On Linux, you may need to run with appropriate permissions to access GPU stats. If you encounter permission errors, try:
```bash
sudo usermod -a -G video $USER
```
Then log out and log back in.

## Files Added/Modified

### New Files:
- `system/gpu_monitor.py` - GPU monitoring module
- `system/gradio_pages/gpu_stats.py` - Gradio UI page
- `test_gpu_stats.py` - Test script for GPU monitoring

### Modified Files:
- `tts_server.py` - Added `/api/gpustats` endpoint
- `script.py` - Integrated GPU stats page into Gradio UI

## Performance Impact

The GPU monitoring has minimal performance impact:
- Memory stats use PyTorch's built-in CUDA functions (negligible overhead)
- pynvml queries are lightweight and cached
- Stats are only updated on-demand (manual refresh or auto-refresh)

## Notes

- GPU stats are read-only and do not affect GPU operation
- Auto-refresh can be disabled to reduce overhead
- The feature gracefully degrades if pynvml is not installed (shows memory only)
- Works with single or multi-GPU setups
