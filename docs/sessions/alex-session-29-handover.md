# Alex Session 29 Handover — 2026-04-14

## Branch
`master` — fully pushed to origin. Latest commit: `a55a0e7`

---

## What Was Built This Session

### 1. Merged PR #5 — Formula Mode Overhaul + Tray Menu + Settings Redesign

This machine (home PC) was at session 23. PR #5 (`session-28-formula-mode-tray-settings`) contained all work from sessions 24–28. Merged and pulled master, bringing home PC fully current.

**What the PR contained (sessions 24–28 work):**
- `formula_mode.py` — new file: phonetic letter normalization, whole-column range parsing, leading garbage-word strip (Whisper hallucinations), IF operator expansion, SUM/AVERAGE/MAX/MIN natural-language prefixes
- `voice.py` — formula mode wired to F9 auto-detect; tray menu restored (voice/speed/translation/output submenus); UnboundLocalError silent crash fixed
- `settings_gui.py` — window 680px height; General tab reduced to 5 checkboxes; Advanced tab gets Behavior section; formula mode toggle removed
- `config.json` — `overlay_enabled: false`
- 233 tests passing after merge

### 2. Hotkey Conflict Fix — F9 → ctrl+f9 (`a55a0e7`)

**Problem:** F9 was the default `hotkey_prompt` (Prompt Assist / Formula mode trigger). Alienware Command Center (and other OEM performance utilities) intercept bare F9 at the OS level via `RegisterHotKey`, which silently wins over Koda's registration. Result: pressing F9 showed "High Performance Mode enabled/disabled" popup instead of triggering Koda.

**Fix:** Changed default `hotkey_prompt` from `f9` to `ctrl+f9` in four places:
- `config.py` — added `"hotkey_prompt": "ctrl+f9"` to `DEFAULT_CONFIG` (was missing entirely)
- `config.json` — updated dev config
- `voice.py` — two fallback defaults (`_build_hotkey_config` and `run_setup` welcome message)
- `settings_gui.py` — Prompt Assist dropdown now uses `PROMPT_OPTIONS` = `ctrl+f1..f12` + bare F-keys (was bare F-keys only); default changed to `ctrl+f9`

**Why ctrl+f9:** OEM utilities only intercept bare function keys. `ctrl+f9` is not used by Alienware Command Center. `RegisterHotKey` at the OS level captures it before Excel sees it, so no Excel shortcut conflict.

**233 tests still passing** after this change. Committed and pushed.

---

## Decisions Made

### Remap hotkey_prompt for all users, not just Alexi
**Decision:** Change the default globally — not a personal workaround.
**Why:** Alienware Command Center is common on gaming PCs. Any Koda user with Alienware/Dell hardware would hit this same silent conflict. The fix protects everyone without breaking anyone who has already manually configured a different hotkey (their config.json overrides the default).

---

## User Feedback & Corrections

- **"f9 is not working did you update the local koda it keeps giving me the high performance mode enabled and disabled pop up"** — F9 conflict with Alienware Command Center. Three Koda.exe instances were running simultaneously (likely leftover from before the restart). Killed all three, then fixed the hotkey default.
- **"we would need to remap in case anyone else has this issue"** — Confirmed: fix the default for all users, not just add a personal workaround.
- **"alienware command center is the f9 for high performance off and on toggle"** — Confirmed root cause.

---

## Waiting On

- **Formula mode end-to-end test** — Koda was restarted from source with `ctrl+f9`. User hasn't tested yet (going to sleep). Need to test: IF, AVERAGE, TODAY in Excel with `ctrl+f9`.
- **Installer wizard test** — `dist/KodaSetup-4.2.0.exe` not yet tested on a fresh machine. Verify 4 wizard pages and `%APPDATA%\Koda\config.json` written correctly.
- **Coworker follow-up** — Did session 25 model mismatch fix resolve their install issue?
- **GitHub Release v4.2.0** — blocked on installer wizard test + coworker confirmation.
- **RDP test** — Phase 9 Test 3 (work PC → home PC via RDP, Ctrl+Space) still pending.
- **Prompt Coach research** — separate product, needs dedicated deep research session. Not Koda, not Lode.

---

## Next Session Priorities

1. **Formula mode test in Excel** — hold `ctrl+f9`, say "if B1 is greater than 10 then yes else no", "average of column B", "today" — verify formulas paste correctly
2. **Installer wizard test** — run `dist/KodaSetup-4.2.0.exe`, verify all 4 pages, check `%APPDATA%\Koda\config.json` after install
3. **Coworker confirmation** — did their install work after session 25 model mismatch fix?
4. **GitHub Release v4.2.0** — publish once 2 + 3 pass
5. **RDP test** — Phase 9 Test 3

---

## Files Changed This Session

| File | Change | Commit |
|------|--------|--------|
| `config.py` | Added `"hotkey_prompt": "ctrl+f9"` to DEFAULT_CONFIG (was missing) | `a55a0e7` |
| `config.json` | `hotkey_prompt` changed from `f9` → `ctrl+f9` | `a55a0e7` |
| `voice.py` | Two fallback defaults updated: `"f9"` → `"ctrl+f9"` | `a55a0e7` |
| `settings_gui.py` | Prompt Assist dropdown uses PROMPT_OPTIONS (ctrl+f1..f12 + bare F-keys); default `ctrl+f9` | `a55a0e7` |

**Also merged this session (PR #5 → master):**
`formula_mode.py`, `voice.py`, `settings_gui.py`, `config.json`, `custom_words.json`, `docs/sessions/alex-session-27-handover.md`, `docs/sessions/alex-session-28-handover.md`, `docs/user-guide.html`, `docs/user-guide.md`, and others.

---

## Key Reminders

- **Formula mode hotkey is now `ctrl+f9`** — NOT bare F9. This is the new default. Existing users with a custom hotkey in their config.json are unaffected.
- **Bare F9 = Alienware Command Center conflict** — do not revert to f9 as default. Any OEM gaming PC utility can own bare function keys.
- **Three Koda.exe instances were running** — probably from before the PC restart. Always kill all before restart: `cmd //c "taskkill /F /IM Koda.exe /IM python.exe /IM pythonw.exe"`
- **Formula mode = ctrl+f9 in Excel/Sheets only** — Ctrl+Space in Excel = plain dictation (unchanged). ctrl+f9 outside Excel = Prompt Assist.
- **APPDATA\Koda\ is exe data dir** — `config.json`, `debug.log`, `.koda_initialized` live there when running as installed exe. Source runs use project root config.json.
- **KodaSetup-4.2.0.exe is NOT uploaded to GitHub Release** — still pending installer wizard test
- **New pricing: $79 Personal / $149 Pro / $29/yr updates** — not yet in code
- **Phase 13 feature gates** (free/Personal/Pro tiers, license keys, LemonSqueezy) — not started
- **Prompt Coach = NEW standalone product** — do not build into Koda or Lode
- **233 tests passing** — `venv/Scripts/python -m pytest test_features.py test_e2e.py -q`
- **No CUDA on home PC** — Intel UHD 770 only

---

## Migration Status

None this session.

---

## Test Status

| Suite | Count | Status |
|-------|-------|--------|
| `test_features.py` | 212 | ✅ All passing |
| `test_e2e.py` | 21 | ✅ All passing |
| **Total** | **233** | **✅** |
