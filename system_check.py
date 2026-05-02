# system_check.py
"""
Hardware classification for Koda. Determines which tier a PC falls into
(BLOCKED / MINIMUM / RECOMMENDED / POWER) and returns the matching config
defaults. Called from configure.py at first run, from settings_gui at
settings open, and from the Inno installer at ssPostInstall via
`Koda.exe --detect-hardware --json`.

See docs/specs/2026-05-02-hardware-tier-system-design.md for full design.
"""

import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import winreg

from system_check_constants import (
    RAM_BLOCKED_MIN_GB,
    DISK_BLOCKED_MIN_FREE_GB,
    WIN_BLOCKED_MIN_BUILD,
    CORES_MIN_RECOMMENDED,
    RAM_MIN_RECOMMENDED_GB,
    CPU_LOW_POWER_PATTERNS,
    TIER_DEFAULTS,
)


# ─── detection helpers (each can be patched in tests) ───────────────

class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_uint32),
        ("dwMemoryLoad", ctypes.c_uint32),
        ("ullTotalPhys", ctypes.c_uint64),
        ("ullAvailPhys", ctypes.c_uint64),
        ("ullTotalPageFile", ctypes.c_uint64),
        ("ullAvailPageFile", ctypes.c_uint64),
        ("ullTotalVirtual", ctypes.c_uint64),
        ("ullAvailVirtual", ctypes.c_uint64),
        ("ullAvailExtendedVirtual", ctypes.c_uint64),
    ]


def _detect_ram_gb() -> float:
    """Total physical RAM in GB."""
    stat = _MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(stat)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    return stat.ullTotalPhys / (1024 ** 3)


def _detect_cores() -> int:
    """Logical CPU core count."""
    return os.cpu_count() or 1


def _detect_free_disk_gb() -> float:
    """Free space on the install drive (default: C:\\) in GB."""
    drive = os.path.splitdrive(sys.prefix)[0] or "C:"
    return shutil.disk_usage(drive + "\\").free / (1024 ** 3)


def _detect_win_build() -> int:
    """Windows build number (e.g. 22000 for Win11). Returns 0 if not on Windows."""
    if sys.platform != "win32":
        return 0
    return sys.getwindowsversion().build


def _detect_cpu_name() -> str:
    """CPU model name from registry. Returns empty string on failure."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
        )
        name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        winreg.CloseKey(key)
        return name.strip()
    except Exception:
        return ""


def _detect_nvidia_gpu() -> str | None:
    """Returns the NVIDIA GPU name if detected, else None.
    Wraps the existing hardware.get_nvidia_gpu_name() but isolated for testability.
    """
    try:
        from hardware import get_nvidia_gpu_name
        return get_nvidia_gpu_name()
    except Exception:
        return None


def _detect_cuda_runtime() -> bool:
    """True if ctranslate2 reports usable CUDA compute types right now."""
    try:
        import ctranslate2
        return bool(ctranslate2.get_supported_compute_types("cuda"))
    except Exception:
        return False


def _is_low_power_cpu(cpu_name: str) -> bool:
    """Match the CPU name string against the low-power pattern list."""
    name_lower = cpu_name.lower()
    return any(pattern in name_lower for pattern in CPU_LOW_POWER_PATTERNS)


# ─── classifier ─────────────────────────────────────────────────────

def classify() -> dict:
    """
    Classify the running machine into a hardware tier and return the
    matching config defaults.

    Returns a dict with shape:
      {
        "tier": "BLOCKED" | "MINIMUM" | "RECOMMENDED" | "POWER",
        "reasons": [str, ...],
        "hardware": {...},
        "defaults": {...},
      }

    Detection failure (any helper raises) → MINIMUM tier with a debug
    breadcrumb in `reasons`. The user is never blocked by detection error.
    """
    try:
        ram_gb = _detect_ram_gb()
        cores = _detect_cores()
        free_disk_gb = _detect_free_disk_gb()
        win_build = _detect_win_build()
        cpu_name = _detect_cpu_name()
        nvidia_name = _detect_nvidia_gpu()
        is_low_power = _is_low_power_cpu(cpu_name)
    except Exception as e:
        return {
            "tier": "MINIMUM",
            "reasons": [f"detection_failed:{type(e).__name__}"],
            "hardware": {},
            "defaults": dict(TIER_DEFAULTS["MINIMUM"]),
        }

    hardware = {
        "cores": cores,
        "ram_gb": round(ram_gb, 1),
        "free_disk_gb": round(free_disk_gb, 1),
        "windows_build": win_build,
        "cpu_name": cpu_name,
        "is_low_power_cpu": is_low_power,
        "nvidia_gpu_name": nvidia_name,
        "cuda_runtime_usable": False,  # filled in below if relevant
    }

    # ─── BLOCKED checks (any one trips it) ─────────────
    block_reasons = []
    if ram_gb < RAM_BLOCKED_MIN_GB:
        block_reasons.append("ram_below_minimum")
    if free_disk_gb < DISK_BLOCKED_MIN_FREE_GB:
        block_reasons.append("disk_below_minimum")
    if 0 < win_build < WIN_BLOCKED_MIN_BUILD:
        block_reasons.append("windows_too_old")

    if block_reasons:
        return {
            "tier": "BLOCKED",
            "reasons": block_reasons,
            "hardware": hardware,
            "defaults": {},
        }

    # ─── POWER tier (NVIDIA + CUDA usable) ─────────────
    if nvidia_name:
        cuda_ok = _detect_cuda_runtime()
        hardware["cuda_runtime_usable"] = cuda_ok
        if cuda_ok:
            return {
                "tier": "POWER",
                "reasons": ["nvidia_gpu_with_cuda"],
                "hardware": hardware,
                "defaults": dict(TIER_DEFAULTS["POWER"]),
            }
        # NVIDIA present but CUDA not usable → fall through to CPU tiers
        # (configure.py Bucket-B flow can offer to install CUDA packages)

    # ─── MINIMUM checks (any one trips it) ─────────────
    min_reasons = []
    if cores < CORES_MIN_RECOMMENDED:
        min_reasons.append("cores_below_recommended")
    if ram_gb < RAM_MIN_RECOMMENDED_GB:
        min_reasons.append("ram_below_recommended")
    if is_low_power:
        min_reasons.append("low_power_cpu_class")

    if min_reasons:
        return {
            "tier": "MINIMUM",
            "reasons": min_reasons,
            "hardware": hardware,
            "defaults": dict(TIER_DEFAULTS["MINIMUM"]),
        }

    # ─── RECOMMENDED (default) ─────────────────────────
    return {
        "tier": "RECOMMENDED",
        "reasons": [],
        "hardware": hardware,
        "defaults": dict(TIER_DEFAULTS["RECOMMENDED"]),
    }


# ─── CLI entry point (used by Inno installer) ───────────────────────

def _main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    args = parser.parse_args()
    result = classify()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Tier: {result['tier']}")
        print(f"Reasons: {result['reasons']}")
        print(f"Hardware: {result['hardware']}")
        print(f"Defaults: {result['defaults']}")


if __name__ == "__main__":
    _main()
