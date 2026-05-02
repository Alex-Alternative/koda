# system_check_constants.py
"""
Shared thresholds for hardware tier classification.

This file is the single source of truth for tier boundaries. Both the
Python classifier (system_check.py) and the Pascal classifier in the Inno
installer ([Code] in koda.iss) read these values. The Pascal side gets
them via build-time codegen (installer/build_thresholds_iss.py reads this
file and writes installer/thresholds.iss).

DO NOT change values here without re-running:
    python installer/build_thresholds_iss.py

and committing the regenerated installer/thresholds.iss alongside.
"""

# Hard floor — install refused below these values.
RAM_BLOCKED_MIN_GB = 2
DISK_BLOCKED_MIN_FREE_GB = 4
WIN_BLOCKED_MIN_BUILD = 19041  # Windows 10 2004 (May 2020 update). Older = BLOCKED.

# Soft floor — install allowed but warned + auto-tuned to slowest defaults.
CORES_MIN_RECOMMENDED = 4
RAM_MIN_RECOMMENDED_GB = 8

# CPU model name patterns that flag low-power class regardless of core count.
# Match is case-insensitive substring on the registry CPU name string.
CPU_LOW_POWER_PATTERNS = (
    "atom",
    "celeron",
    "pentium silver",
    "pentium gold",
    "pentium n",
    " n100",
    " n200",
    " n300",
    " n4000",
    " n5000",
    " n6000",
    " n95",
    " n97",
)

# Per-tier defaults written to config.json on first install.
TIER_DEFAULTS = {
    "MINIMUM": {
        "model_size": "tiny",
        "compute_type": "int8",
        "cpu_threads": 2,
        "process_priority": "normal",
    },
    "RECOMMENDED": {
        "model_size": "small",
        "compute_type": "int8",
        "cpu_threads": 4,
        "process_priority": "above_normal",
    },
    "POWER": {
        "model_size": "large-v3-turbo",
        "compute_type": "float16",
        "cpu_threads": 4,
        "process_priority": "above_normal",
    },
}
