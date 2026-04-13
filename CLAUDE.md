# Koda — Project Context

@../_shared/owner-profile.md
@../_shared/build-standards.md

## What Koda Is
Push-to-talk voice-to-text Windows system tray app. Personal productivity tool for Alexi — captures speech and pastes transcribed text into any active window (Claude, ChatGPT, Slack, email, etc.).

## Repo & Working Directory
- **Repo:** github.com/Moonhawk80/koda
- **Local path:** `C:\Users\alexi\Projects\koda`
- **Run from source:** `cmd //c "C:\Users\alexi\Projects\koda\start.bat"` — do NOT build/install exe during dev
- **Tests:** `venv/Scripts/python -m pytest test_features.py` (96 tests passing)

## Tech Stack
- Python 3.14, venv at `C:\Users\alexi\Projects\koda\venv`
- No NVIDIA GPU — Intel UHD 770 only. CUDA not available.
- test_stress.py runs standalone only (not via pytest normally)

## Known Issues / Environment Quirks
- `configure.py` fails with UnicodeEncodeError in bash (cp1252 console) — cosmetic only, config.json already present
- GPU Power Mode feature built but untestable on this machine

## Current Status
See memory file for session-by-session state: `C:\Users\alexi\.claude\projects\C--Users-alexi\memory\project_koda.md`
