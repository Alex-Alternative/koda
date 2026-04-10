# Alex Session 7 Handover — 2026-04-10

## Branch
`master` — fully pushed to origin. 0 unpushed commits.

## Repo
**https://github.com/Alex-Alternative/koda** — Working dir: `C:\Users\alex\Projects\koda`

## What Was Built This Session

### 1. Critical Hotkey Drop Fix (the big one)
- **Root cause identified**: Windows silently kills `WH_KEYBOARD_LL` hooks when the hook thread can't respond within ~300ms. Whisper transcription holds Python's GIL for seconds, starving the keyboard library's hook thread. The old watchdog checked `keyboard._hooks` count, but that count NEVER changes even after Windows removes the hooks — the Python objects persist while the OS hooks are dead.
- **Fix**: Created `hotkey_service.py` — a separate subprocess via `multiprocessing.Process` that runs all keyboard hooks. Has its own GIL, so hooks always respond instantly regardless of transcription load. Communicates with main process via `multiprocessing.Pipe`.
- **Watchdog updated**: Now monitors subprocess liveness + ping/pong health check every 60s. Auto-restarts on crash.
- **Files**: `hotkey_service.py` (NEW), `voice.py` (major refactor of hotkey section)

### 2. Prompt Assist Mode (new feature)
- **`prompt_assist.py`** (NEW) — transforms spoken thoughts into well-structured LLM prompts
- Detects intent: code, debug, explain, review, write, general (14/14 test accuracy)
- Applies structured templates with context extraction (language detection, etc.)
- Optional Ollama LLM refinement for higher quality
- **Hotkey**: F9 (hold to talk, release to get structured prompt)
- **Tested live**: User spoke naturally about building a web page, got a structured prompt pasted

### 3. Hotkey Overhaul — F-Key Layout
- **Problem**: Every modifier combo we tried conflicted with something:
  - `Ctrl+Shift+P` = command palette (VS Code, Chrome)
  - `Ctrl+Shift+Space` = Windows IME switcher
  - `Ctrl+backtick` = keyboard library can't match the key
  - `Ctrl+Alt+P` = print dialog
  - `Ctrl+Alt+Space` = accessibility tools
- **Solution**: F-keys for all secondary functions. Single key, zero conflicts.
- **Final layout**:
  - `Ctrl+Space` = Dictation (main, unchanged)
  - `F5` = Read selected text aloud
  - `F6` = Read back last transcription
  - `F7` = Correction (undo + re-record)
  - `F8` = Command mode
  - `F9` = Prompt Assist

### 4. Exe Size Reduction
- 576MB → 526MB by excluding unused transitive dependencies (scipy, sklearn, matplotlib, sympy, pytest, pygments, tkinter, fontTools, setuptools, pip)
- Remaining 526MB is 88% Whisper model (462MB) + 12% code/libs (64MB)

### 5. Installer & Build
- Installed Inno Setup 6 via winget
- Built `Koda.exe` (526MB) and `KodaSetup-4.1.0.exe` (527MB)
- Fixed ISCC path detection to include user-level install (`LOCALAPPDATA`)
- Added `hotkey_service.py` and `prompt_assist.py` to PyInstaller bundle

### 6. README Rewrite
- Complete rewrite reflecting v4.1.0: F-key hotkeys, Prompt Assist docs, updated architecture section, installer instructions, simplified structure

### 7. Setup Wizard Update
- All 6 hotkeys shown with plain-English descriptions
- Users can keep F-key defaults or customize each one
- Prompt Assist included in setup flow

### 8. Model Benchmarks
- No NVIDIA GPU (Intel UHD 770 only). CUDA not an option.
- tiny=0.06x RTF, base=0.19x, **small=0.34x (current, right choice)**, large-v3-turbo=2.02x (too slow on CPU)

## Decisions Made

1. **Subprocess for hotkeys, not pynput/ctypes** — multiprocessing.Process is the cleanest solution. Each process has its own GIL. The keyboard library works the same way in the subprocess. No new dependencies.
2. **F-keys for secondary hotkeys** — after testing ctrl+backtick (library can't match), ctrl+shift+space (IME), ctrl+alt+p (print), we learned: only use `ctrl+alt+letter` or F-keys. F-keys are simplest for users.
3. **small model is the right default** — 0.34x RTF (3x faster than real-time) on CPU. Tiny is too inaccurate, large-v3-turbo is 2x slower than real-time without GPU.
4. **No CUDA path** — machine has Intel UHD 770, no NVIDIA GPU. GPU acceleration is not available on this hardware.
5. **Prompt Assist uses templates, not just LLM** — works offline with intent detection + templates. LLM refinement is optional (requires Ollama).

## User Feedback & Corrections

1. **"ctrl shift p is terrible"** — opens command palette everywhere. Led to F-key solution.
2. **"ctrl shift space opened a menu on top"** — Windows IME switcher. Can't use space combos.
3. **"ctrl+' does not work it just types the symbol"** — keyboard library can't match backtick in combos.
4. **"less button pushes the better"** — user strongly prefers single-key hotkeys over modifier combos.
5. **"the more complex things we do with F keys"** — user wants F-keys for specialized features, Ctrl+Space only for main dictation.
6. **"you also have to rewrite installation guide and readme files"** — prompted README rewrite and configure.py update.
7. **"it has to have a description of the hotkeys so the user knows what those are"** — each hotkey in setup wizard now has a plain-English explanation.
8. **"an option for the user to choose from suggested keys"** — setup wizard now lets users customize each hotkey from safe F-key options.
9. **User's business context**: Alternative Funding Group, MCAs, 21 people, 10 years in business (mentioned while testing Prompt Assist).

## Waiting On

- **Hotkey fix soak test** — the subprocess fix needs to run for an extended session to confirm zero hook drops. Koda is currently running with v4.1.0 and F-key hotkeys.
- **No NVIDIA GPU** — can't do CUDA acceleration without hardware change.

## Next Session Priorities

### Phase 7 — Polish & Distribution
1. **Auto-update mechanism** — GitHub release check on startup, "new version available" notification
2. **Professional tray icon** — current one is code-generated, needs designed icon (flagged overdue since session 5)
3. **First-run experience** — welcome balloon or brief wizard showing hotkeys after install
4. **GitHub Releases** — tagged releases with changelogs and installer attached
5. **Settings GUI hotkey picker** — graphical version of the F-key customization (beyond the CLI wizard)

### Phase 8 — Hardening
6. **Extended soak test** — let Koda run for hours, verify hotkey service stays alive in debug.log
7. **Edge cases** — sleep/wake, lid close, RDP sessions, multi-monitor
8. **Prompt Assist improvements** — extract specific details from speech (company name, colors, etc.) instead of generic boilerplate templates

### Backlog
9. **Mac version** — possible but ~30% of voice.py is Windows-specific. Separate milestone.
10. **DO NOT suggest Product Hunt** — needs thorough testing first

## Files Changed This Session

| File | Change |
|---|---|
| `hotkey_service.py` | **NEW** — Subprocess for keyboard hooks, immune to GIL |
| `prompt_assist.py` | **NEW** — Intent detection + prompt structuring for LLMs |
| `voice.py` | Subprocess hotkey management, event dispatch, prompt mode, F-key defaults, v4.1.0 |
| `hotkey_service.py` | F-key defaults, prompt hotkey registration |
| `build_exe.py` | Added hotkey_service.py + prompt_assist.py to bundle, excluded unused deps |
| `config.json` | F-key hotkeys, prompt hotkey added |
| `configure.py` | All 6 hotkeys with descriptions, customization option, Prompt Assist in flow |
| `README.md` | Complete rewrite for v4.1.0 |
| `installer/build_installer.py` | Added LOCALAPPDATA to ISCC search paths |
| `installer/koda.iss` | Version bump to 4.1.0 |

## Current Config State
```json
{
  "model_size": "small",
  "language": "en",
  "hotkey_dictation": "ctrl+space",
  "hotkey_command": "f8",
  "hotkey_prompt": "f9",
  "hotkey_correction": "f7",
  "hotkey_readback": "f6",
  "hotkey_readback_selected": "f5",
  "hotkey_mode": "hold"
}
```

## Key Reminders

- **Kill ALL python/pythonw processes before restarting Koda** — `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **Hotkey rules**: ONLY use `ctrl+alt+letter` or F-keys. Backtick, space combos, Ctrl+Shift+P all fail.
- **Test hotkeys with physical keypresses** — `keyboard.send()` simulation doesn't reliably trigger `keyboard.add_hotkey()` callbacks
- **`keyboard._hooks` count is USELESS** for detecting dead hooks — Python objects persist even after Windows removes the actual hooks
- **Venv** at `C:\Users\alex\Projects\koda\venv`
- **Desktop** at `C:\Users\alex\OneDrive\Desktop`
- **GitHub CLI** at `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Alex-Alternative`
- **Python 3.14** — tflite-runtime has no wheels, openwakeword uses ONNX
- **mic_device = null** — don't hardcode indices
- **pyttsx3 COM threading** — must init lazily in the thread that uses it
- **Paste uses `keyboard.send("ctrl+v")`** NOT pyautogui
- **Sound uses winsound** NOT sounddevice
- **No NVIDIA GPU** — Intel UHD 770 only, CUDA not available
- **Flag overdue items loudly** — especially the tray icon
- **DO NOT suggest Product Hunt**

## Test Status
- 98 tests passing (77 unit + 21 e2e) — unchanged from session 6
- 14/14 prompt assist intent detection tests passing
- All existing tests unaffected by hotkey refactor and prompt assist addition
