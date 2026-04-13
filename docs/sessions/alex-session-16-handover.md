# Alex Session 16 Handover — 2026-04-12

## Branch
`master` — all Phase 12 work was already committed. Session 16 changes are **uncommitted**:
- `voice.py` — mic disconnect detection rewrite
- `settings_gui.py` — scrollable settings window
- `STATUS.md` — new compact session-start file (untracked)
- `filler_words.json` — created by Alexi saving Settings (untracked)
- `config.json` — minor changes (untracked)

**Nothing pushed this session.** Commit before next session.

---

## What Was Built This Session

### 1. STATUS.md — Compact Session Start File (NEW)
`STATUS.md` created in project root. ~50 lines. Replaces reading the full handover doc at session start.
Contains: phase status table, next session actions, non-obvious reminders, key file sizes.
Memory updated: `MEMORY.md` now points to STATUS.md as the session start document.
Memory file created: `project_koda.md` in `.claude/projects/.../memory/`.

### 2. Settings Window — Scrollable Canvas (settings_gui.py)
**Problem:** Settings window was fixed at 1750px tall with no scrollbar. On 1080p screens, the bottom half
(Filler Words, Snippets, Per-App Profiles) was cut off and unreachable.

**Fix:**
- Removed `self.geometry("520x1750")` and `self.resizable(False, False)`
- Added a `tk.Canvas` + `ttk.Scrollbar` wrapping the content frame
- Window now sizes to `min(screen_height - 80, 900)` at startup
- Mouse wheel scrolling bound via `canvas.bind_all("<MouseWheel>", ...)`
- Content frame width tracks canvas width via `<Configure>` event

**Result:** Settings window is now scrollable, fits any screen, all sections accessible.
Window opens slightly narrow — Alexi noted it and said we'll fix sizing in a later session.

### 3. Exe Build — dist/Koda.exe (525 MB)
Built `dist/Koda.exe` using existing `build_exe.py`. Bundles:
- All Python modules (voice.py, settings_gui.py, text_processing.py, etc.)
- Whisper small model (~150MB)
- sounds/ and plugins/ directories
- koda.ico

**PyInstaller** was not previously installed — installed it in venv first.
Build took ~80 seconds. Output: `C:\Users\alexi\Projects\koda\dist\Koda.exe` — 525 MB.

Files to bring to work PC (all in same folder):
- `dist/Koda.exe`
- `config.json`
- `filler_words.json`

No Python, no install, no internet required at work. First launch may take 5–10 seconds to unpack.
Windows Defender may require "More info → Run anyway" (unsigned exe).

### 4. Mic Disconnect Detection — Phase 9 Test 1 (voice.py)
**Problem:** When USB mic unplugged, sounddevice's stream would die briefly, then immediately "recover"
using Windows' fallback audio device (built-in mic, HDMI audio, etc.). Koda showed "Microphone recovered
automatically" even though the USB mic was still unplugged — a false recovery.

**Root cause:** `mic_device = null` means sounddevice uses whatever Windows considers the default input
device. When USB mic is unplugged, Windows switches default to another device, and the stream restart
succeeds on the wrong device.

**Fix implemented:**
- Added `_mic_disconnected` (bool) and `_input_device_count` (int) globals
- Added `_count_input_devices()` — uses `ctypes.windll.winmm.waveInGetNumDevs()` (Windows WinMM API)
  to count input devices WITHOUT touching PortAudio or the running stream
- Watchdog initializes baseline count at startup: `_input_device_count = _count_input_devices()`
- Fast path: when stream dies, compare current device count to baseline:
  - Count dropped → physical disconnect → show "Microphone disconnected. Plug it back in." once,
    set `_mic_disconnected = True`, do NOT restart (avoid false recovery on wrong device)
  - Count same/higher → safe to restart (non-disconnect failure or mic came back) → restart,
    show "Microphone recovered automatically." only if `_mic_disconnected` was True
- Tray goes red on disconnect, green on recovery

**Failed approaches tried this session (don't retry):**
- `sd._terminate()` + `sd._initialize()` inside watchdog — kills the running stream (PaErrorCode -9988)
- `_mic_disconnected` flag without device count check — false recoveries still happened

**Test result: PASS** — Alexi confirmed:
- Unplug → "Microphone disconnected. Plug it back in — Koda will recover."
- Replug → "Microphone recovered automatically." + tray goes green

---

## Decisions Made

### 1. STATUS.md as session start document
Handover docs are verbose archives. STATUS.md is the compact (~50 line) live state file.
At session start: read STATUS.md only. Handover docs only for investigating past decisions.
How to apply: update STATUS.md at end of every session during /handover.

### 2. Windows WinMM API for device count
`ctypes.windll.winmm.waveInGetNumDevs()` — Windows-only but Koda is Windows-only.
Does not touch PortAudio session. Safe to call while stream is running.
Returns count of wave input devices; drops by 1+ when USB mic unplugged.

### 3. Don't restart stream on device-count drop
When a physical device is removed, attempting restart with `device=None` succeeds on wrong device.
Decision: detect count drop → show disconnect notification → wait for count to recover → then restart.
This prevents false "recovered" notifications.

### 4. Exe build uses existing build_exe.py
`build_exe.py` was already in the repo and fully configured. Not a new file.
Bundles Whisper model, all modules, sounds. Result: 525 MB single exe.
Distribution to work PC = exe + config.json + filler_words.json in same folder.

### 5. Domain: kodaspeak.com
User decided on `kodaspeak.com` after `koda.com` and `kodavoice.com` were both taken.
`getkoda.com` and `kodaapp.com` were also rejected by Alexi.

### 6. Settings window opens narrow
The `540x{win_h}` geometry fix works but the window opens slightly too narrow — user had to
move it to reach Save button. Deferred fix to a later session.

---

## User Feedback & Corrections

1. **"Mic test did not pass"** — Alexi correctly identified that "Microphone recovered automatically"
   appearing WITHOUT replugging = false recovery. This was a real bug. Fix implemented and confirmed.

2. **Settings window opens narrow** — noted but deferred. "I don't like the layout much but we can
   work on that on a later session."

3. **Too many tray menu options** — Alexi noted the right-click tray menu has too many items and
   "I can see how this can become confusing for an end user." Logged for Phase 13 UX cleanup.

4. **"I don't need Llama"** — confirmed. Ollama/LLM polish is off by default, not required.

5. **Domain preferences** — rejected: koda.com (taken), kodavoice.com (taken), getkoda.com,
   kodaapp.com. Chose: kodaspeak.com.

6. **Run /handover at 40% context** — Alexi called it at 50% again. Try to call it earlier.

---

## Waiting On

### Manual Tests Still Pending

1. **Phase 9 Test 2 — Sleep/wake** (NOT run this session)
   - Put PC to sleep (Start → Power → Sleep — NOT lock screen)
   - Wake it up
   - Verify Ctrl+Space still fires
   - Check debug.log for "Sleep/wake detected" + "Full recovery complete"

2. **Phase 9 Test 3 — RDP hotkey** (NOT run this session)
   - Connect to home PC via RDP
   - Verify Ctrl+Space fires inside RDP session

3. **Phase 12 smoke test** (NOT fully done)
   - Open Settings → scroll to Snippets → add a test snippet → Save → say trigger → confirm expansion pastes
   - Filler Words section was opened and Save was hit (creating filler_words.json) but snippet expansion was not verified

### Pending Items

4. **Uncommitted changes** — `voice.py`, `settings_gui.py` not committed. Commit at start of next session.

5. **Rebuild exe** — `dist/Koda.exe` was built BEFORE the mic disconnect fix. The exe at work will
   not have the correct mic behavior. Rebuild after committing the voice.py changes.

6. **Phase 13** — installer/distribution. Blocked until Phase 9 tests + Phase 12 smoke test pass.

7. **Settings window width** — opens narrow, user had to move window to reach Save. Fix sizing.

8. **Tray menu cleanup** — too many options for end users. Phase 13 UX item.

9. **Phase 9 VAD gap** — SileroVADModel uses wrong API, wastes RAM. Still on backlog.

---

## Next Session Priorities

1. **Commit session 16 changes** — voice.py + settings_gui.py (mic fix + scroll fix)
2. **Rebuild exe** — current dist/Koda.exe is missing the mic disconnect fix
3. **Phase 9 Test 2** — sleep/wake test (put PC to sleep, not lock screen)
4. **Phase 9 Test 3** — RDP hotkey test
5. **Phase 12 smoke test** — add snippet, save, say trigger, verify expansion pastes
6. **Phase 13** — installer/exe build for distribution (after above tests pass)

---

## Files Changed This Session

| File | Change | Status |
|------|--------|--------|
| `voice.py` | Mic disconnect detection: `_count_input_devices()`, `_mic_disconnected` flag, `_input_device_count` baseline, watchdog fast path rewrite | **UNCOMMITTED** |
| `settings_gui.py` | Scrollable canvas wrapping settings content; window sized to screen height | **UNCOMMITTED** |
| `STATUS.md` | New compact session-start file (created this session) | **UNTRACKED** |
| `filler_words.json` | Created by Alexi saving Settings | **UNTRACKED** |
| `dist/Koda.exe` | Built from source (525 MB, Whisper bundled) — does NOT include mic fix | **UNTRACKED** |
| `docs/sessions/alex-session-16-handover.md` | This file | **UNTRACKED** |
| `.claude/projects/.../memory/project_koda.md` | New memory: read STATUS.md at session start | **SAVED** |
| `.claude/projects/.../memory/MEMORY.md` | Updated index | **SAVED** |

---

## Key Reminders

- **Kill ALL python before restart:** `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **Run from source:** `cmd //c "C:\Users\alexi\Projects\koda\start.bat"`
- **Tests:** `venv/Scripts/python -m pytest test_features.py` — 176 passing
- **Exe rebuild needed** — current dist/Koda.exe predates mic disconnect fix
- **Sleep ≠ Lock screen** — Phase 9 Test 2 requires actual Sleep (Power → Sleep)
- **Domain chosen:** kodaspeak.com
- **Settings window opens narrow** — known issue, deferred
- **Tray menu has too many options** — noted by Alexi, Phase 13 UX item
- **DO NOT re-run market research** — saved in memory
- **DO NOT suggest Product Hunt**
- **DO NOT build exe during dev** — Phase 13 will formalize
- **No mid-task confirmation prompts**
- **GitHub CLI:** `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Moonhawk80`
- **Repo:** github.com/Moonhawk80/koda
- **Hotkeys:** ONLY `ctrl+alt+letter` or F-keys
- **Paste:** `keyboard.send("ctrl+v")` — NOT pyautogui
- **Sound:** `winsound` — NOT sounddevice
- **No NVIDIA GPU** — Intel UHD 770 only
- **Run /handover at ~40% context** — 50% is too late

---

## Migration Status
None — no database in this project.

---

## Test Status
- **176 tests passing** (`test_features.py`) — unchanged from session 15
- No new tests added this session (mic fix is in watchdog runtime, not unit-testable)
- `test_stress.py` — 17/17 standalone (unchanged)

---

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
  "hotkey_mode": "hold",
  "mic_device": null,
  "sound_effects": true,
  "notifications": false,
  "noise_reduction": false,
  "post_processing": {
    "remove_filler_words": true,
    "code_vocabulary": false,
    "auto_capitalize": true,
    "auto_format": true
  },
  "vad": {
    "enabled": true,
    "silence_timeout_ms": 1000
  },
  "wake_word": {
    "enabled": false,
    "phrase": "hey koda"
  },
  "llm_polish": {
    "enabled": false,
    "model": "phi3:mini"
  },
  "overlay_enabled": true,
  "snippets": {}
}
```
