#!/usr/bin/env python3
"""
Quick test script for GPU stats monitoring
"""

import sys
from pathlib import Path

# Add the project root to the path
this_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(this_dir))

from system.gpu_monitor import get_gpu_monitor

def test_gpu_monitor():
    """Test the GPU monitoring functionality"""
    print("=" * 60)
    print("GPU Stats Monitoring Test")
    print("=" * 60)
    
    monitor = get_gpu_monitor()
    
    print(f"\nCUDA Available: {monitor.cuda_available}")
    print(f"NVML Available: {monitor.nvml_available}")
    
    if not monitor.cuda_available:
        print("\n⚠️  No CUDA-capable GPU detected")
        print("GPU stats will not be available")
        return
    
    print("\n" + "=" * 60)
    print("GPU Statistics:")
    print("=" * 60)
    
    stats = monitor.get_gpu_stats()
    
    if not stats:
        print("No GPU stats available")
        return
    
    for gpu in stats:
        print(f"\nGPU {gpu['id']}: {gpu['name']}")
        print(f"  Memory: {gpu['memory_used_gb']:.2f} GB / {gpu['memory_total_gb']:.2f} GB ({gpu['memory_percent']:.1f}%)")
        
        if gpu.get('gpu_utilization') is not None:
            print(f"  GPU Utilization: {gpu['gpu_utilization']}%")
        else:
            print(f"  GPU Utilization: N/A (install pynvml for this metric)")
        
        if gpu.get('temperature') is not None:
            print(f"  Temperature: {gpu['temperature']}°C")
        else:
            print(f"  Temperature: N/A (install pynvml for this metric)")
        
        if gpu.get('power_watts') is not None:
            print(f"  Power: {gpu['power_watts']:.1f}W / {gpu['power_limit_watts']:.1f}W ({gpu['power_percent']:.1f}%)")
        else:
            print(f"  Power: N/A (install pynvml for this metric)")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(monitor.get_summary())
    
    if not monitor.nvml_available:
        print("\n" + "=" * 60)
        print("💡 Tip: Install pynvml for more detailed GPU stats")
        print("   pip install pynvml")
        print("=" * 60)

if __name__ == "__main__":
    test_gpu_monitor()
