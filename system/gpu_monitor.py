"""
GPU Monitoring Module for AllTalk TTS

This module provides GPU statistics monitoring including:
- GPU utilization
- Memory usage (used/total)
- Temperature
- Power usage

Supports both pynvml (NVIDIA Management Library) and fallback to torch.cuda
"""

import time
from typing import Dict, List, Optional

import torch


class GPUMonitor:
    """Monitor GPU statistics using pynvml or torch.cuda as fallback"""

    def __init__(self):
        self.nvml_available = False
        self.cuda_available = torch.cuda.is_available()
        
        if self.cuda_available:
            try:
                import pynvml
                pynvml.nvmlInit()
                self.nvml_available = True
                self.pynvml = pynvml
            except (ImportError, Exception):
                self.nvml_available = False

    def get_gpu_stats(self) -> List[Dict[str, any]]:
        """
        Get statistics for all available GPUs
        
        Returns:
            List of dictionaries containing GPU stats for each device
        """
        if not self.cuda_available:
            return []
        
        gpu_stats = []
        device_count = torch.cuda.device_count()
        
        for i in range(device_count):
            stats = self._get_single_gpu_stats(i)
            if stats:
                gpu_stats.append(stats)
        
        return gpu_stats

    def _get_single_gpu_stats(self, device_id: int) -> Optional[Dict[str, any]]:
        """Get stats for a single GPU device"""
        try:
            stats = {
                "id": device_id,
                "name": torch.cuda.get_device_name(device_id),
            }
            
            # Get memory info from torch
            mem_info = torch.cuda.mem_get_info(device_id)
            free_memory = mem_info[0] / (1024**3)  # Convert to GB
            total_memory = mem_info[1] / (1024**3)
            used_memory = total_memory - free_memory
            
            stats["memory_used_gb"] = round(used_memory, 2)
            stats["memory_total_gb"] = round(total_memory, 2)
            stats["memory_percent"] = round((used_memory / total_memory) * 100, 1)
            
            # Try to get additional stats from pynvml
            if self.nvml_available:
                try:
                    handle = self.pynvml.nvmlDeviceGetHandleByIndex(device_id)
                    
                    # GPU utilization
                    try:
                        util = self.pynvml.nvmlDeviceGetUtilizationRates(handle)
                        stats["gpu_utilization"] = util.gpu
                        stats["memory_utilization"] = util.memory
                    except Exception:
                        stats["gpu_utilization"] = None
                        stats["memory_utilization"] = None
                    
                    # Temperature
                    try:
                        temp = self.pynvml.nvmlDeviceGetTemperature(
                            handle, self.pynvml.NVML_TEMPERATURE_GPU
                        )
                        stats["temperature"] = temp
                    except Exception:
                        stats["temperature"] = None
                    
                    # Power usage
                    try:
                        power = self.pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                        power_limit = self.pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000.0
                        stats["power_watts"] = round(power, 1)
                        stats["power_limit_watts"] = round(power_limit, 1)
                        stats["power_percent"] = round((power / power_limit) * 100, 1)
                    except Exception:
                        stats["power_watts"] = None
                        stats["power_limit_watts"] = None
                        stats["power_percent"] = None
                        
                except Exception:
                    pass
            
            return stats
            
        except Exception as e:
            print(f"Error getting GPU stats for device {device_id}: {e}")
            return None

    def get_summary(self) -> str:
        """Get a formatted summary of GPU stats"""
        gpu_stats = self.get_gpu_stats()
        
        if not gpu_stats:
            return "No GPU detected or CUDA not available"
        
        summary_lines = []
        for gpu in gpu_stats:
            lines = [
                f"GPU {gpu['id']}: {gpu['name']}",
                f"  Memory: {gpu['memory_used_gb']:.2f} GB / {gpu['memory_total_gb']:.2f} GB ({gpu['memory_percent']:.1f}%)",
            ]
            
            if gpu.get("gpu_utilization") is not None:
                lines.append(f"  GPU Utilization: {gpu['gpu_utilization']}%")
            
            if gpu.get("temperature") is not None:
                lines.append(f"  Temperature: {gpu['temperature']}°C")
            
            if gpu.get("power_watts") is not None:
                lines.append(f"  Power: {gpu['power_watts']:.1f}W / {gpu['power_limit_watts']:.1f}W ({gpu['power_percent']:.1f}%)")
            
            summary_lines.append("\n".join(lines))
        
        return "\n\n".join(summary_lines)

    def __del__(self):
        """Cleanup NVML on deletion"""
        if self.nvml_available:
            try:
                self.pynvml.nvmlShutdown()
            except Exception:
                pass


# Global instance
_gpu_monitor = None


def get_gpu_monitor() -> GPUMonitor:
    """Get or create the global GPU monitor instance"""
    global _gpu_monitor
    if _gpu_monitor is None:
        _gpu_monitor = GPUMonitor()
    return _gpu_monitor
