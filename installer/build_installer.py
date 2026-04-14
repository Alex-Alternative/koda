"""
Build Koda installer.

Steps:
  1. Build Koda.exe via PyInstaller (if not already built)
  2. Compile installer via Inno Setup

Prerequisites:
  - Inno Setup 6 installed: https://jrsoftware.org/isdl.php
  - Python venv with all deps
  - Run from the installer/ directory or project root

Output: dist/KodaSetup-{version}.exe
"""

import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DIST_DIR = os.path.join(PROJECT_DIR, "dist")
KODA_EXE = os.path.join(DIST_DIR, "Koda.exe")
ISS_FILE = os.path.join(SCRIPT_DIR, "koda.iss")

# Common Inno Setup install locations
ISCC_PATHS = [
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe"),
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
    r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
]


def find_iscc():
    for path in ISCC_PATHS:
        if os.path.exists(path):
            return path
    return None


def main():
    print("=== Koda Installer Builder ===\n")

    # Step 1: Check for Koda.exe
    if not os.path.exists(KODA_EXE):
        print("Koda.exe not found. Building it first...\n")
        build_script = os.path.join(PROJECT_DIR, "build_exe.py")
        result = subprocess.run(
            [sys.executable, build_script],
            cwd=PROJECT_DIR,
        )
        if result.returncode != 0:
            print("ERROR: Failed to build Koda.exe")
            sys.exit(1)
    else:
        size_mb = os.path.getsize(KODA_EXE) / (1024 * 1024)
        print(f"Found Koda.exe ({size_mb:.0f} MB)")

    # Step 2: Find Inno Setup
    iscc = find_iscc()
    if not iscc:
        print("\nERROR: Inno Setup not found!")
        print("Install it from: https://jrsoftware.org/isdl.php")
        print("(Free, ~5MB download, takes 2 minutes)")
        print("\nAfter installing, run this script again.")
        sys.exit(1)

    print(f"Found Inno Setup: {iscc}")

    # Step 3: Compile installer
    print(f"\nCompiling installer from {ISS_FILE}...")
    result = subprocess.run([iscc, ISS_FILE], cwd=SCRIPT_DIR)

    if result.returncode != 0:
        print("ERROR: Installer compilation failed")
        sys.exit(1)

    # Find the output
    for f in os.listdir(DIST_DIR):
        if f.startswith("KodaSetup") and f.endswith(".exe"):
            setup_path = os.path.join(DIST_DIR, f)
            size_mb = os.path.getsize(setup_path) / (1024 * 1024)
            print(f"\nInstaller built successfully!")
            print(f"  Output: {setup_path}")
            print(f"  Size: {size_mb:.0f} MB")
            print(f"\nShare this file — users double-click to install.")
            break

    # Clean up intermediate Koda.exe — only the installer is needed
    if os.path.exists(KODA_EXE):
        os.remove(KODA_EXE)
        print("Cleaned up intermediate Koda.exe from dist/")


if __name__ == "__main__":
    main()
