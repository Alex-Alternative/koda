# Alex Session 17 Handover — 2026-04-13

## Branch
`master` — all work committed and pushed to https://github.com/Moonhawk80/koda
0 unpushed commits.

## Repo
**https://github.com/Moonhawk80/koda** (transferred from Alex-Alternative in session 16)

## Context
Cross-PC continuation. Work PC session focused on fixing the broken installer that
session 16 produced, and clarifying the dev-vs-distribution workflow. User will
continue at home PC.

## What Was Built This Session

### 1. Diagnosed and Fixed Broken .exe Install
- **Symptom**: User installed `KodaSetup-4.2.0.exe`, saw overlay green but tray
  icon missing and hotkeys not working
- **Investigation**: Found two zombie `Koda.exe` processes (PIDs 61728, 9460)
  in `C:\Users\alex\AppData\Local\Programs\Koda\`. Found PyInstaller temp dir
  `_MEI617282/debug.log` showing the actual error
- **Root cause**: Whisper model load failed at startup
  - Bundled config.json had `model_size: "base"` (default) at install time
  - Whisper tried to load `base` from `~/.cache/huggingface/hub/...base` — file corrupt/missing
  - Process zombied: overlay started BEFORE model load (so showed green/ready),
    but tray icon, watchdog, hotkey service all came AFTER and never initialized
- **Fix**: User uninstalled the .exe, switched back to running from source. Confirmed working.

### 2. Publisher Name Fix
- Installer publisher was `"Alex Alternative"` (the work brand)
- Changed to `"Alex Concepcion"` (real name from git config) for personal project
- Commit `1c3abdf`. User can change to "Moonhawk80" or other label if preferred.

### 3. Reinforced Dev Workflow
- Confirmed: **run from source** (`pythonw voice.py`) for active development
- The installer is for END-USER distribution, not the developer
- Every code change → no rebuild needed → just kill+restart pythonw

## Decisions Made

1. **Source > installer for the developer** — installer is for shipping to others.
   Saves rebuild/reinstall cycle on every change. Documented in updated home PC prompt.
2. **Publisher = "Alex Concepcion"** (real name from git) — chose over "Moonhawk80" handle
   because installer publisher field shows to end users; real name reads more professional.
   Reversible if user prefers handle.
3. **Don't auto-modify the handover skill** to add commit/push — safety system blocked it
   in session 16. Pending explicit user approval. Still a real pain point that costs work.

## User Feedback & Corrections

1. **"Why is my Koda off on the tray but the desktop icon shows green?"** — Confused
   tray icon (system notification area) with floating overlay (KodaOverlay window).
   They're independent; overlay started before crash, tray died with crash.
2. **"Would it make better sense to uninstall and run it like before from my personal git?"** —
   YES, exactly right. The installer is for distribution, not development. User got there
   intuitively, which is the right instinct.
3. **"The author of the app when installed it says Alex Alternative we need to fix that"** —
   Done. Now reads "Alex Concepcion" in the installer publisher field.
4. **"I uninstalled and it and its working now"** — Confirmed source-mode is healthy.

## Waiting On

- **Home PC needs to pull** (`git pull origin master`) to get tkinter fix + publisher name fix
- **Soak test sleep/wake recovery** from session 8 — still not verified through real cycles
- **User approval to update handover skill** to auto-commit/push (safety system blocked this
  in session 16)
- **Upload `KodaSetup-4.2.0.exe` to GitHub Release v4.2.0** — for end users, not needed
  for personal use

## Next Session Priorities

### Immediate (home PC)
1. **`git pull origin master`** — get tkinter fix + publisher name change
2. **Run from source** for active dev: `pythonw voice.py` (DON'T install the .exe)
3. **Check `git status`** for any uncommitted Sunday-night work and commit if found

### Phase 8 — Hardening (still pending)
4. **Soak test sleep/wake recovery** — sleep machine, wake, verify auto-recovery
5. **Edge cases** — RDP, multi-monitor, Bluetooth/USB mic hot-swap
6. **Extended runtime stability** — hours-long sessions, memory profile

### Polish & Distribution
7. **Decide publisher name finally** — Alex Concepcion vs Moonhawk80 vs other
8. **Upload installer to GitHub Release** when ready to share with others
9. **Real-world daily use** for a week before declaring "done"

### Backlog
10. **Update handover skill to auto-commit/push** when user says "yes"
11. **Mac version** — separate milestone, ~30% of code is Windows-specific

## Files Changed This Session

| File | Change | Commit |
|---|---|---|
| `installer/koda.iss` | Publisher: "Alex Alternative" → "Alex Concepcion" | `1c3abdf` |
| `docs/sessions/alex-session-17-handover.md` | This file | (current) |

## Test Status
- **176 tests passing** (unchanged from session 16)
- No new tests this session (diagnosis + config work only)

## Key Reminders

- **GitHub URL is https://github.com/Moonhawk80/koda** — old Alex-Alternative redirects
- **The installer is for END USERS, not the developer** — run from source for dev work
- **If you install the .exe and it crashes**: check `%TEMP%\_MEIxxx\debug.log` for the real error
- **Always commit + push at end of session** — handover skill should do this but doesn't yet
- **Always pull at start of session on either PC** — keeps both machines in sync
- **Kill ALL python/pythonw/Koda processes before restarting** — `taskkill //f //im pythonw.exe`
  AND `taskkill //f //im Koda.exe`
- **Hotkey rules**: ONLY use `ctrl+alt+letter` or F-keys. Backtick, space combos all fail.
- **Test hotkeys with physical keypresses** — `keyboard.send()` simulation doesn't work
- **`keyboard._hooks` count is USELESS** for detecting dead hooks
- **Venv** at `~/Projects/koda/venv` (home) or `C:\Users\alex\Projects\koda\venv` (work)
- **Python 3.14** — tflite-runtime has no wheels, openwakeword uses ONNX
- **mic_device = null** — don't hardcode indices
- **pyttsx3 COM threading** — must init lazily in the thread that uses it
- **Paste uses `keyboard.send("ctrl+v")`** NOT pyautogui
- **No NVIDIA GPU** on work PC — Intel UHD 770 only, CUDA not available
- **DO NOT suggest Product Hunt** — needs thorough testing first
- **tkinter is REQUIRED in build_exe.py** — overlay/settings/stats GUIs depend on it (fixed in session 16)
- **Vercel plugin auto-suggests for Koda — ignore it.** Koda is a Python desktop app, not web.

## Cross-PC Workflow

**Before stopping work on either PC:**
```
git add -A
git commit -m "wip" (or descriptive message)
git push
```

**Starting work on either PC:**
```
git pull
```

If you get a merge/rebase conflict on pull: STOP and ask Claude to help.

## Quick Resume Block

Copy this into a new session on your HOME PC to pick up where we left off:

```
cd ~/Projects/koda

git pull origin master
git status

I need to continue work on Koda from session 17 (docs/sessions/alex-session-17-handover.md).

## Where we left off
Work PC fixed two issues this session:
1. The .exe install was crashing because Whisper couldn't find the bundled model
   when config defaulted to "base". Switched to running from source — works perfectly.
2. Installer publisher name changed from "Alex Alternative" to "Alex Concepcion".

## My setup at home
Run from source for development:
  ./venv/Scripts/activate
  pythonw voice.py

DO NOT install the .exe for personal use — it's only for distribution to others.

## Next up
1. Verify Koda runs from source on home PC (Ctrl+Space test)
2. Phase 8 hardening: soak test sleep/wake recovery, RDP/multi-monitor/mic edge cases
3. Decide on final publisher name (Alex Concepcion vs Moonhawk80 vs other)
4. Update handover skill to auto-commit/push (need to explicitly tell Claude "yes update it")

## Key context
- Koda = push-to-talk voice-to-text Windows tray app
- Repo: github.com/Moonhawk80/koda — 176 tests passing — v4.2.0
- Hotkeys: Ctrl+Space=dictation, F8=command, F9=prompt assist, F7=correction, F6=read back, F5=read selected
- ALWAYS git pull at start, git push at end. Cross-PC sync depends on it.
- Kill ALL pythonw + Koda.exe processes before restarting
- DO NOT suggest Product Hunt
- tkinter MUST be in build_exe.py — don't re-exclude it
- Repo is at Moonhawk80/koda, not Alex-Alternative anymore
```
