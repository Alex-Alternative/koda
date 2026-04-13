# Alex Session 16 Handover — 2026-04-13

## Branch
`master` — all work committed and pushed to origin (https://github.com/Moonhawk80/koda).
0 unpushed commits.

## Repo
**https://github.com/Moonhawk80/koda** (transferred this session from Alex-Alternative/koda)

## Context
Cross-PC session. Alex is splitting work between two machines:
- **Work PC**: `C:\Users\alex\Projects\koda` — where this session ran
- **Home PC**: `~/Projects/koda` — where session 15 ran (Phases 11 & 12)

Work was synced via git pull/rebase mid-session. Both PCs now in sync.

## What Was Built This Session

### 1. Repo Transfer (Alex-Alternative → Moonhawk80)
- User initiated GitHub repo transfer to personal account
- Updated repo URL references in: `updater.py` (line 16), `README.md`, `installer/koda.iss`
- Old session handover docs left as historical record (still reference Alex-Alternative)
- GitHub now redirects old URL → new URL automatically

### 2. Sound Files Committed
- `sounds/start.wav`, `stop.wav`, `success.wav`, `error.wav` were previously gitignored
- Force-added to repo so a fresh clone has everything to run Koda
- Only `wakeword.wav` was in git before
- Eliminates need to run `generate_sounds.py` after clone

### 3. Critical Build Fix — tkinter Missing in Koda.exe
- **Bug**: User installed v4.2.0 from `KodaSetup-4.2.0.exe`, got crash on launch:
  `ModuleNotFoundError: No module named 'tkinter'` (overlay.py:10)
- **Root cause**: `build_exe.py` had `--exclude-module=tkinter` and `--exclude-module=_tkinter`
  to save space, but `overlay.py`, `settings_gui.py`, and `stats_gui.py` ALL require it
- **Fix**: Removed the excludes, added explicit hidden imports for tkinter, tkinter.ttk,
  tkinter.messagebox, tkinter.filedialog
- **Rebuilt**: `dist/Koda.exe` (529MB, was 526MB) and `dist/KodaSetup-4.2.0.exe` (530MB)
- Commit `25cffaa`

### 4. Cross-PC Sync via Git
- Work PC pulled in 4 commits from home PC: Phase 11 (per-app profile GUI),
  Phase 12 (snippets + filler words GUI), session 14 + 15 handovers
- Test count went from 117 → 176 (59 new tests from home PC work)
- Rebased work PC's tkinter fix on top of home PC commits — clean fast-forward

## Decisions Made

1. **Use git pull/rebase for cross-PC sync** — not file copying. The repo on GitHub is
   the single source of truth. Both PCs sync through it.
2. **Sound files now in git** — small (<100KB total), worth the cleaner clone experience.
3. **Don't auto-modify the handover skill** — user mentioned wanting it to auto-commit/push,
   but safety system blocked the edit. User needs to explicitly approve the change.
4. **Don't install Vercel plugin on home PC for Koda** — it's a Python desktop app, not a
   web app. Vercel false-positives on keywords like "deploy" and "phase".
5. **Personal GitHub: Moonhawk80** — repo permanently lives there now. Old Alex-Alternative
   URL redirects automatically but should be updated in tools/configs.

## User Feedback & Corrections

1. **"Why is Koda not working again!"** — Old v4.1.0 was still running, needed kill+restart
   to pick up v4.2.0 code. Common pattern when running from source.
2. **"Why is she off again I have been using the PC but not Koda"** — Hooks died silently
   while subprocess stayed alive. Led to hook-level health check fix in session 8.
3. **"I always forget committing maybe it is a point to add to handover skill"** — Confirmed
   pain point. Skill update was attempted but blocked by safety system. Pending user approval.
4. **"Are you sure you have all the files for everything I built at home?"** — Yes, after
   git pull. The .exe is irrelevant — source code on GitHub is the truth.
5. **"It is on my personal github now silly goose"** — User playful but real point: don't
   reference old URLs.

## Waiting On

- **User approval to update handover skill** to auto-commit/push (safety system blocked
  the edit; user needs to explicitly say "yes update it")
- **Home PC needs to pull** to get the tkinter fix and updated repo URLs
- **Home PC needs to rebuild Koda.exe and reinstall** — broken installer is what user has now
- **Soak test the sleep/wake recovery + hook hardening** from session 8 — not yet verified
  through real sleep cycles
- **Upload `KodaSetup-4.2.0.exe` to GitHub Release v4.2.0** — would let auto-update flow
  work end-to-end and home PC could just download instead of rebuild

## Next Session Priorities

### Immediate (home PC)
1. **Pull latest from origin** — get tkinter fix + repo URL updates
2. **Commit any uncommitted Sunday night work** if `git status` shows changes
3. **Rebuild Koda.exe and installer** with the tkinter fix
4. **Uninstall broken Koda, install fixed v4.2.0**, verify launch works

### Phase 8 — Hardening (still pending)
5. **Soak test sleep/wake recovery** — let Koda run, sleep machine, verify auto-recovery
6. **Edge cases** — RDP, multi-monitor, Bluetooth/USB mic hot-swap
7. **Extended runtime stability** — hours-long sessions, memory profile

### Ship It
8. **Upload installer to GitHub Release** — `gh release upload v4.2.0 dist/KodaSetup-4.2.0.exe`
9. **Real-world daily use** for a week before declaring "done"

### Backlog
10. **Update handover skill to auto-commit/push** (when user approves)
11. **Update GitHub CLI auth on home PC** if needed
12. **Mac version** — separate milestone, ~30% of code is Windows-specific

## Files Changed This Session

| File | Change |
|---|---|
| `build_exe.py` | Removed tkinter excludes, added tkinter hidden imports |
| `updater.py` | GITHUB_REPO updated to Moonhawk80/koda |
| `README.md` | Repo URL references updated to Moonhawk80 |
| `installer/koda.iss` | Repo URL updated |
| `sounds/start.wav` | Added to git (was gitignored) |
| `sounds/stop.wav` | Added to git |
| `sounds/success.wav` | Added to git |
| `sounds/error.wav` | Added to git |
| `dist/Koda.exe` | Rebuilt with tkinter (529MB) — not in git |
| `dist/KodaSetup-4.2.0.exe` | Rebuilt installer (530MB) — not in git |

## Current Test Status
- **176 tests passing** (from session 15)
- No new tests this session (build/transfer work only)

## Key Reminders

- **GitHub URL is now https://github.com/Moonhawk80/koda** — old Alex-Alternative URL redirects
- **Always commit + push at end of session** — handover skill should do this but doesn't yet
- **Always pull at start of session on either PC** — keeps both machines in sync
- **Kill ALL python/pythonw processes before restarting Koda** — `taskkill //f //im pythonw.exe`
- **Hotkey rules**: ONLY use `ctrl+alt+letter` or F-keys. Backtick, space combos, Ctrl+Shift+P all fail.
- **Test hotkeys with physical keypresses** — `keyboard.send()` simulation doesn't work
- **`keyboard._hooks` count is USELESS** for detecting dead hooks
- **Venv** at `C:\Users\alex\Projects\koda\venv` (work) or `~/Projects/koda/venv` (home)
- **GitHub CLI** at `"C:\Program Files\GitHub CLI\gh.exe"` on work PC
- **Python 3.14** — tflite-runtime has no wheels, openwakeword uses ONNX
- **mic_device = null** — don't hardcode indices
- **pyttsx3 COM threading** — must init lazily in the thread that uses it
- **Paste uses `keyboard.send("ctrl+v")`** NOT pyautogui
- **No NVIDIA GPU** — Intel UHD 770 only, CUDA not available
- **DO NOT suggest Product Hunt** — needs thorough testing first
- **tkinter is REQUIRED in build_exe.py** — overlay/settings/stats GUIs depend on it. Don't exclude it again.
- **Vercel plugin auto-suggests for Koda — ignore it.** Koda is a Python desktop app, not a web app.

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

**If you get a merge/rebase conflict on pull**: STOP and ask Claude to help. Don't force anything.

## Quick Resume Block

Copy this into a new session to pick up where we left off:

```
cd ~/Projects/koda  (home) OR C:\Users\alex\Projects\koda (work)

git pull origin master

Read docs/sessions/alex-session-16-handover.md for full context. Koda — push-to-talk
voice-to-text Windows tray app. Repo: github.com/Moonhawk80/koda.

Continue from session 16. v4.2.0 source is current. 176 tests passing.

Session 16 shipped: tkinter build fix (was crashing v4.2.0 .exe), repo transfer to
Moonhawk80, sound files committed to repo, cross-PC sync via git pull/rebase.

Next up:
1. (Home PC) Rebuild Koda.exe + installer with tkinter fix, reinstall fixed v4.2.0
2. Phase 8 hardening: soak test sleep/wake recovery, edge cases (RDP, multi-monitor, mic hot-swap)
3. Upload KodaSetup-4.2.0.exe to GitHub Release v4.2.0 (`gh release upload v4.2.0 dist/KodaSetup-4.2.0.exe`)
4. Update handover skill to auto-commit/push (pending explicit user approval)

Key context:
- Hotkeys: Ctrl+Space=dictation, F5-F9=everything else.
- ALWAYS git pull at start, git push at end. Cross-PC sync depends on it.
- Kill ALL python/pythonw processes before restarting Koda.
- 176 tests passing.
- DO NOT suggest Product Hunt.
- tkinter is REQUIRED in build_exe.py — don't re-exclude it.
- Repo is at Moonhawk80/koda, not Alex-Alternative anymore.
```
