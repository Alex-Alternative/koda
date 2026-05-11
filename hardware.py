"""
GPU detection for Koda.
Detects NVIDIA GPU and CUDA availability to determine if Power Mode is available.
"""

import subprocess
import sys


def get_nvidia_gpu_name():
    """Return the GPU model name string, or None if not found."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass
    return None


def try_install_cuda_packages():
    """
    Attempt to pip install NVIDIA CUDA runtime packages.
    Returns True if install succeeded and CUDA is now usable by ctranslate2.
    """
    packages = [
        "nvidia-cuda-runtime-cu12",
        "nvidia-cublas-cu12",
        "nvidia-cudnn-cu9",
    ]
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install"] + packages,
            capture_output=True, timeout=600,
        )
        if result.returncode != 0:
            return False
        # Re-test: reimport ctranslate2 to pick up new DLLs
        import importlib
        import ctranslate2
        importlib.reload(ctranslate2)
        types = ctranslate2.get_supported_compute_types("cuda")
        return bool(types)
    except Exception:
        return False
