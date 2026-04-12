# Alex Session 13 Handover — 2026-04-12

## Branch
`master` — all work committed and pushed to origin.
No uncommitted changes. `.claude/` and `CLAUDE.md` are untracked (intentional).
Ahead of `origin/master` by 0 — fully pushed.

## What Was Built This Session

### 1. Phase 10 Complete — Custom Vocabulary Fully Wired (commit `68ce846`)

All 4 steps from the session 12 plan executed and passing.

**Step 1 — `text_processing.py:561`**
Added `apply_custom_vocabulary()` as the final step in `process_text()`. Reads from
`config.get("custom_vocabulary", {})` — runs after `auto_capitalize` so user corrections
win over every other pipeline step.

**Step 2 — `voice.py`**
- `_load_custom_words()` now called once in `main()` at startup: `config["custom_vocabulary"] = _load_custom_words()`
- Removed per-transcription `_load_custom_words()` call (was line 609 — file read on every dictation)
- Removed manual `apply_custom_vocabulary()` call after transcription (now handled by `process_text`)
- `light_config` (dictation mode) gets `"custom_vocabulary": custom_vocab` at top level so it flows through
- Prompt mode: applies vocab manually before `refine_prompt()` since prompt mode doesn't use `process_text`
- Initial Whisper `initial_prompt` now reads from `config.get("custom_vocabulary", {})` instead of fresh file load

**Step 3 — `settings_gui.py`**
- Replaced "Edit custom_words.json" Notepad button with inline Treeview manager
- Treeview: two columns (Misheard | Correct), 5 rows visible, scrollable
- Buttons: Add, Edit, Remove, Import (JSON), Export (JSON)
- Add/Edit use a small Toplevel dialog with two Entry fields
- `save()` now calls `_save_custom_words_data()` — vocab changes persist on Save/Save & Restart
- Window height increased from 1020 → 1120 to accommodate the Treeview
- "Edit profiles.json" button moved to its own row below the vocab manager

**Step 4 — `test_features.py`**
Added `TestCustomVocabularyPipeline` class with 15 tests covering:
- Basic wiring: vocab applied via process_text, applied last after capitalize, multi-word key, case-insensitive, word boundary
- Edge cases: empty dict, missing key, no match, multiple entries same sentence
- Pipeline interaction: vocab + filler removal, vocab + number formatting, vocab in light_config, vocab with no post_processing key, full pipeline survival, empty text

**Result: 121 → 136 tests passing** (all 136 pass, 1.06s)

## Decisions Made

### 1. Koda Distribution at Work — Exe Only, Not Repo
Alexi confirmed: personal GitHub (Moonhawk80) must NOT be shared with or accessed from work PC.
No git clone at work. No personal credentials on work machine.
Decision: build a standalone `.exe` at home, share it to work. This requires Phase 13 (installer).
The exe is the clean boundary — work only ever sees a double-click app, never the source.

### 2. Phase 13 Is the Right Home for the Installer
Auto-update infrastructure is already built in `updater.py` — it checks GitHub Releases API,
detects newer versions, notifies via tray, and knows to look for `KodaSetup*.exe` assets.
What's missing: actual download/install step + built exe + GitHub Release with asset.
Decision: don't build the installer now. It belongs in Phase 13 alongside the feature gates
and license key system. Phase 13 cannot ship before Phases 11 and 12.

### 3. Phase 9 Hardware Tests Unblocked — Mic Arrived
USB mic arrived today (2026-04-12). Phase 9 (beta stability / mic disconnect tests) is now
unblocked. Should run this session or next session alongside Phase 11.

### 4. Phase Sequence Confirmed
10 (done) → 11 (per-app profiles) → 12 (filler/snippets GUI) → 13 (storefront + installer)
Do not skip to Phase 13 before 11 and 12 — feature gates require knowing what's free vs. paid,
and custom vocab + per-app profiles are the features that justify $49 over free Windows Voice Access.

## User Feedback & Corrections

1. **"remember I moved this to Moonhawk profile because I don't want work to have anything to do with developing this"** — Koda is Alexi's personal proprietary project. Work and personal are kept completely separate. Never suggest sharing the repo with work or using work credentials for Koda.

2. **"I don't want personal shit to hit my work PC"** — Reinforced separation. No git clone at work. Exe-only distribution is the correct answer.

3. **"the mic arrived today"** — Phase 9 is now unblocked. Previous two handovers incorrectly said mic was here (session 11) or not here (session 12). Confirmed arrived 2026-04-12.

## Waiting On

1. **Phase 9 hardware tests** — mic is here, ready to run:
   - Launch Koda → unplug USB mic → expect tray notification within ~3s → replug → expect "Microphone recovered automatically" → dictation resumes
   - Sleep/wake soak: run Koda, sleep machine, wake, check `debug.log` for "Sleep/wake detected" and "Full recovery complete"
   - RDP test: connect via RDP, verify hotkeys work

2. **Phase 11 build** — per-app profiles (next session)

3. **Phase 9 VAD gap** — `SileroVADModel` uses wrong API, wastes RAM. Still on backlog, not addressed.

## Next Session Priorities

1. **Phase 9 hardware tests** — mic is here, do these first:
   - Unplug/replug USB mic test
   - Sleep/wake soak test
   - RDP hotkey test
2. **Phase 11, Step 1** — per-app profiles: detect foreground window (Win32 `GetForegroundWindow`), match against profile rules in config
3. **Phase 11, Step 2** — merge profile config over base at transcription time
4. **Phase 11, Step 3** — settings GUI: profile manager with app picker
5. **Phase 11, Step 4** — ~20 new tests, run suite, commit, push

## Files Changed This Session

| File | Change | Commit |
|---|---|---|
| `text_processing.py` | `apply_custom_vocabulary` wired as final step in `process_text()` | `68ce846` |
| `voice.py` | Load custom_words.json at startup; remove per-transcription load; light_config carries vocab | `68ce846` |
| `settings_gui.py` | Treeview vocab manager replaces Notepad button; save() persists vocab | `68ce846` |
| `test_features.py` | +15 TestCustomVocabularyPipeline tests (121 → 136) | `68ce846` |
| `docs/sessions/alex-session-13-handover.md` | This file | untracked until committed |

## Key Reminders

- **Kill ALL python/pythonw before restarting Koda:** `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **Run from source:** `cmd //c "C:\Users\alexi\Projects\koda\start.bat"` — no installer builds during dev
- **Tests:** `venv/Scripts/python -m pytest test_features.py` — 136 passing. Do NOT use plain `python -m pytest`
- **Venv:** `C:\Users\alexi\Projects\koda\venv` — use `venv/Scripts/python` directly
- **Hotkey rules:** ONLY `ctrl+alt+letter` or F-keys. No backtick, no Ctrl+Shift combos
- **Paste:** `keyboard.send("ctrl+v")` — NOT pyautogui
- **Sound:** `winsound` — NOT sounddevice
- **pyttsx3 COM threading:** init lazily in the thread that uses it
- **mic_device = null** — never hardcode device indices
- **No NVIDIA GPU** — Intel UHD 770 only; Power Mode untestable here
- **GitHub CLI:** `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Moonhawk80`
- **Repo:** github.com/Moonhawk80/koda
- **DO NOT suggest Product Hunt**
- **DO NOT build/install exe** — running from source until Phase 13
- **DO NOT re-run market research** — saved to memory at `memory/market_research.md`
- **Do not ask for mid-task confirmation** — user wants actions taken without approval prompts
- **Ollama NOT required** — core features work without it; LLM polish/translation are off-by-default extras
- **Wake word says "Alexa" not "Hey Koda"** — feature is off by default; don't enable
- **configure.py UnicodeEncodeError** — cosmetic in cp1252 terminal; config.json is already correct
- **test_stress.py** — run standalone only; NOT a pytest suite
- **USB mic ARRIVED 2026-04-12** — Phase 9 hardware tests unblocked
- **Owner full name: Alexis Concepcion** — use in legal/copyright contexts
- **Koda is personal/proprietary** — never suggest sharing repo or using personal GitHub from work PC
- **Distribution to work PC = exe only** (Phase 13) — no git clone, no personal credentials on work machine

## Migration Status
None — no database changes ever in this project.

## Test Status
- **136 tests passing** (`test_features.py`) — up from 121 at session start (+15 TestCustomVocabularyPipeline)
- `test_stress.py` — 17/17 standalone (from session 10, unchanged)
- All Phase 10 pipeline wiring covered by new tests

## Current Config State
```json
{
  "model_size": "small",
  "compute_type": "int8",
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
  "noise_reduction": false
}
```
