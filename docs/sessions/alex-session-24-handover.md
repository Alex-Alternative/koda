# Alex Session 24 Handover — 2026-04-14

## Branch
`master` — clean, up to date with `origin/master`. All changes pushed.

---

## What Was Built This Session

### 1. Fix: False hotkey-staleness restarts every 15 minutes (`hotkey_service.py`)

**Problem:** Koda was showing "Hotkeys recovered automatically. You're good to go."
every ~15 minutes. The debug.log showed the pattern: warnings at 10 min
("No key events for 615s") then a restart at 15 min ("silent hook death detected").

**Root cause:** The RegisterHotKey rewrite (sessions 20–21) only calls `_touch()`
when a registered hotkey actually fires (WM_HOTKEY). If the user doesn't press
Ctrl+Space / F8 / F9 for 15 minutes, `_last_key[0]` stays at the value it had
at process start. Voice.py's staleness watchdog gets back an old timestamp in
every pong and eventually restarts the service.

**Fix:** Call `_touch()` in the ping handler before reading `_last_key[0]`.
Pings arrive every ~30s from voice.py, so the pong now always carries a
timestamp within 30s of the current time. The staleness check effectively
measures "is the message loop alive?" — the correct invariant for RegisterHotKey.
1 line added to `hotkey_service.py`. No changes to `voice.py`.

**Merged:** PR #3 (Moonhawk80/koda#3) — `fix/hotkey-staleness-false-restart`

### 2. Work PC sync — pulled sessions 20–23

Work PC (`C:\Users\alex\Projects\koda`) was at session 19. Sessions 20–23
were all done on the home PC (`C:\Users\alexi\Projects\koda`) and pushed to
GitHub. Pulled all of it:

- Session 20: RegisterHotKey rewrite (`3ecc1b8`) + GetAsyncKeyState polling (`05ae675`)
- Session 21: Installer branding (`659e033`), keyboard-hook regression guard (`516bdb3`),
  ctrl+shift+. VK fix (`8218e59`)
- Session 22: Session docs, STATUS.md
- Session 23: Exe runtime fixes — VAD assets bundled, config/log paths use `%APPDATA%\Koda\`
  when frozen, logprob_threshold typo fixed

### 3. Work PC install test — IN PROGRESS

Alex installed `KodaSetup-4.2.0.exe` on the work PC and ran it. The exe was
showing the staleness restart bug (above) — that was the first real bug caught
by the work PC install test. Fixed and running from source now.

**Exe status:** The `KodaSetup-4.2.0.exe` in Downloads does NOT have the
staleness fix. A rebuild is needed before calling the work PC test "done."

### 4. CLAUDE.md situation on work PC

During `git pull --rebase`, the local (work PC) untracked `CLAUDE.md` blocked
the rebase. We moved it to `CLAUDE.md.bak`, pulled, and the remote `CLAUDE.md`
(home PC specific, paths reference `C:\Users\alexi\`) was merged in.

`CLAUDE.md.bak` is still an untracked file in the project root. It's the old
work PC CLAUDE.md. Can be deleted — the remote CLAUDE.md is authoritative.

---

## Decisions Made

### Staleness check measures message loop liveness, not hotkey frequency
With RegisterHotKey, "time since last key event" as a health signal is wrong —
the OS delivers hotkeys reliably, but only when the user presses them. The right
signal is "is the message loop still processing messages?" Pings prove this.
Calling `_touch()` on ping makes the staleness threshold a liveness timeout,
not a hotkey-frequency timeout.

### Work PC runs from source, not exe, for active dev
During Phase 13 testing, source runs are preferred so fixes apply immediately
without rebuilding. Once the work PC test is formally complete, rebuild exe.

---

## User Feedback & Corrections

- **"at home the repo is on my personal git you know this"** — Work PC was behind
  by sessions 20–23. User was correct — we had to fetch/pull from GitHub to sync.
  The confusion was that git status showed clean (no local edits) but we were
  missing many commits from the home PC sessions.
- **"I did all the changes you suggested and fix a lot of bugs and did all sorts
  of tests does it not show?"** / **"are you looking in the right git?"** —
  Prompted the `git fetch origin` that revealed sessions 20–23 on GitHub.
- **"the app is not listed on the apps list"** — The exe was run directly from
  Downloads (`Koda Files/Koda new/Koda.exe`), not via Inno Setup installer.
  No uninstall entry = not installed. User can just delete the folder.
- **"after you finish I want to run the new exe"** — Currently running from source.
  To get a fixed exe, rebuild is needed on the home PC.

---

## Waiting On

- **Exe rebuild with staleness fix** — needs to happen on home PC (alexi), then
  copied to work PC for the formal install test
- **Work PC install test (formal)** — install rebuilt `KodaSetup-4.2.0.exe`,
  verify wizard branding + hotkeys + transcription, no false restart notifications
- **RDP test** — Phase 9 Test 3 still pending; connect from work PC → home PC via RDP
- **Prompt Coach research session** — separate session, separate repo
- **Phase 13 feature gates** — free/Personal/Pro tier in code, license keys, LemonSqueezy
- **GitHub Release** — `KodaSetup-4.2.0.exe` not published; waiting on work PC test passing

---

## Next Session Priorities

1. **Rebuild exe on home PC** — pull master (has staleness fix), run `build_exe.py`,
   test Ctrl+Space in the new exe before declaring done
2. **Work PC install test (formal)** — copy rebuilt exe to work PC, install, verify
3. **RDP test** — Phase 9 Test 3
4. **Prompt Coach research** — dedicated session with deep research

---

## Files Changed

| File | Change |
|------|--------|
| `hotkey_service.py` | Added `_touch()` call in ping handler — staleness fix |
| `docs/sessions/home-pc-session-prompt.md` | Updated during session with RegisterHotKey spec detail (now obsolete — remote version is current) |

**Untracked (cleanup needed):**
- `CLAUDE.md.bak` — old work PC CLAUDE.md, can be deleted

---

## Key Reminders

- **Staleness fix is in source but NOT in the exe** — rebuild needed before the
  formal work PC install test
- **Exe data dir is `%APPDATA%\Koda\`** — config.json, debug.log, .koda_initialized
  all live there when running frozen. Source runs use project root.
- **Work PC exe** — user was running it from `C:\Users\alex\Downloads\Koda Files\Koda new\`
  (not installed). To install properly: run the rebuilt KodaSetup exe.
- **taskkill on work PC bash:** `cmd //c "taskkill /F /IM Koda.exe /IM pythonw.exe /IM python.exe"`
- **Run from source on work PC:** `cd C:\Users\alex\Projects\koda && venv\Scripts\python voice.py`
  (or `pythonw` to free the terminal)
- **Full test suite:** `venv/Scripts/python -m pytest test_features.py test_e2e.py -q` (208 tests)
- **Prompt Coach is a new standalone project** — not in Koda, not in Lode
- **CLAUDE.md in repo has home PC paths (alexi)** — correct on home PC, misleading on work PC
- **sessions 20–23 all on home PC** — work PC was unaware until this session

---

## Migration Status

None this session.

---

## Test Status

| Suite | Count | Status |
|-------|-------|--------|
| `test_features.py` | 187 | ✅ Unchanged |
| `test_e2e.py` | 21 | ✅ Unchanged |
| **Total** | **208** | **✅** |

No new tests added this session. The staleness fix is runtime behavior in the
subprocess message loop — not unit-testable without mocking Win32 APIs.
