# Alex Session 14 Handover — 2026-04-12

## Branch
`master` — all work committed and pushed to origin.
No uncommitted changes. `.claude/` and `CLAUDE.md` are untracked (intentional).
Ahead of `origin/master` by 0 — fully pushed.

## What Was Built This Session

### 1. Phase 11 Complete — Per-App Profiles GUI Manager (commit `cd9d3c8`)

**Step 3 — `settings_gui.py`**
Replaced the single "Edit profiles.json" button in the CUSTOM WORDS section with a
full `PER-APP PROFILES` section containing:
- `ttk.Treeview` with 3 columns: Profile | Matches | Overrides (4 rows visible, scrollable)
- Treeview displays live summary of each profile's match rule and override settings
- **Add** button: opens profile dialog, creates new profile
- **Edit** button: opens profile dialog pre-filled with selected profile's values
- **Remove** button: deletes selected profile
- **Edit profiles.json** button kept as fallback for power users
- Profile dialog (`_profile_dialog`): 440×300 Toplevel with:
  - Profile name entry
  - Match process entry (e.g., `code.exe`) 
  - Match title regex entry (optional, e.g., `Chrome|Firefox`)
  - 4 Comboboxes for overrides: code_vocabulary, remove_filler_words, auto_capitalize, auto_format
  - Each combobox has 3 values: `inherit` (don't override), `on` (True), `off` (False)
  - Validation: name required, cannot start with `_`; at least one match rule required
- `save()` now calls `self._save_profiles_data()` — profiles persist on Save/Save & Restart
- Window height increased from `520x1120` → `520x1300`
- `__init__` loads `self._profiles_data = self._load_profiles_data()` at startup

New methods added:
- `_load_profiles_data()` — delegates to `profiles.load_profiles()`
- `_save_profiles_data()` — delegates to `profiles.save_profiles()`
- `_profile_summary(profile)` — returns (match_str, overrides_str) for Treeview display
- `_refresh_profile_tree()` — repopulates Treeview from `_profiles_data`
- `_profile_dialog(title, name, profile)` — Add/Edit dialog
- `_add_profile()` — Add button handler
- `_edit_profile()` — Edit button handler
- `_remove_profile()` — Remove button handler

**Step 4 — `test_features.py`**
Added `import json` at top (needed for `TestProfileLoadSave`).
Added 3 new test classes — 20 new tests total:

`TestDeepMerge` extended (+5 tests):
- `test_empty_override` — empty override returns copy of base
- `test_empty_base` — empty base with override returns override
- `test_non_dict_override_replaces_dict` — scalar override replaces nested dict
- `test_three_levels_deep` — 3-level deep merge preserves untouched keys
- `test_new_key_added` — new keys from override appear in result

`TestProfileMatchEdgeCases` (9 new tests):
- `test_process_match_case_insensitive` — stored `CHROME.EXE` matches `chrome.exe` via `.lower()`
- `test_title_only_match` — profile with only `title` rule matches correctly
- `test_process_takes_priority_over_title` — process match works even if title doesn't match
- `test_title_match_with_process_rule_present` — title regex matches even when process rule also exists
- `test_invalid_regex_does_not_crash` — bad regex in title rule caught, no exception raised
- `test_first_match_wins` — when two profiles match same process, first one in dict wins
- `test_empty_profiles_dict` — empty dict returns (None, {})
- `test_profile_missing_match_key_skipped` — profile without `match` key is skipped cleanly
- `test_match_returns_empty_settings_when_no_settings_key` — profile with no `settings` key returns `{}`

`TestProfileLoadSave` (6 new tests using temp files + patching `profiles.PROFILES_PATH`):
- `test_save_writes_valid_json` — `save_profiles()` writes parseable JSON
- `test_load_reads_existing_file` — `load_profiles()` reads an existing profiles.json
- `test_load_creates_default_when_missing` — creates `profiles.json` from `DEFAULT_PROFILES` if missing
- `test_round_trip` — save then load returns same data
- `test_load_corrupt_json_falls_back_to_defaults` — corrupt JSON → falls back to defaults
- `test_default_profiles_has_expected_apps` — VS Code, Slack, Outlook present in defaults

**Result: 136 → 156 tests passing** (all 156 pass, 0.82s)

## Decisions Made

### 1. Steps 1 & 2 Were Already Done
`profiles.py` was discovered to be fully built from a prior session, including:
- `get_active_window_info()` — Win32 foreground window detection
- `match_profile()` — process name + title regex matching
- `deep_merge()` — deep merges config overrides over base config
- `ProfileMonitor` — background thread, polls every 1s, calls `_on_profile_change` callback
- `load_profiles()` / `save_profiles()` / `DEFAULT_PROFILES`

`voice.py` was also already fully wired:
- `ProfileMonitor` started in `run_setup()` with `base_config`
- `_on_profile_change(profile_name, merged_config)` swaps `config` live
- `toggle_profiles()` in tray menu
- Current profile name shown in tray menu label

Only the GUI manager (Step 3) and tests (Step 4) were missing.

### 2. "Edit profiles.json" Button Kept as Fallback
Decision: keep the raw JSON editor button alongside the new GUI manager.
Reason: power users may want to add match rules or overrides not exposed in the GUI.
It's a safety valve — doesn't hurt to have both.

### 3. Phase 9 Hardware Tests Still Pending
Phase 9 hardware tests were discussed but NOT run this session — that work was deferred
to next session. USB mic is confirmed present (arrived 2026-04-12). These are manual tests:
- Unplug/replug USB mic → expect tray notification and auto-recovery
- Sleep/wake soak → check `debug.log` for "Sleep/wake detected" and "Full recovery complete"
- RDP hotkey test → connect via RDP, verify hotkeys fire

### 4. Question Left Open at Session End
Alexi asked whether to add to the handover document an explanation of what the code
does in each Phase 9 hardware test scenario — i.e., what to watch for while testing.
Answer (captured here for next session):

- **Unplug/replug:** `voice.py` uses `sounddevice` with a stream error callback. When the
  device disappears, the callback fires, sets a recovery flag, notifies via tray, and
  restarts the stream. Watch for the tray notification within ~3s of unplugging, and
  confirm dictation works after replug.
- **Sleep/wake:** `voice.py` registers a Windows power broadcast listener
  (`WM_POWERBROADCAST`). On resume from sleep, it fires a full recovery: closes stream,
  re-enumerates devices, reopens stream. Check `debug.log` for the log lines
  "Sleep/wake detected" and "Full recovery complete". If both lines appear, the feature works.
- **RDP:** RDP sessions sometimes suppress global keyboard hooks. Koda uses a subprocess
  hotkey listener (`hotkey_service.py`) that re-registers hooks inside the subprocess.
  Verify the tray icon is visible over RDP and that the dictation hotkey (Ctrl+Space) fires.

## User Feedback & Corrections

1. **"we need to run handover skill when you are done we are close to 50% context"** —
   User flagged context usage proactively. Good practice going forward: run `/handover`
   earlier in sessions, especially after a major phase completes.

2. **"and add that last question to it"** — Alexi asked about Phase 9 test behavior
   (what to watch for), wanted that explanation included in the handover rather than
   answered inline. Captured in Decisions section above.

## Waiting On

1. **Phase 9 hardware tests (manual)** — mic is here, run these next session:
   - Launch Koda → unplug USB mic → expect tray notification within ~3s → replug →
     expect "Microphone recovered automatically" → dictation resumes
   - Sleep/wake soak: sleep machine, wake, check `debug.log`
   - RDP: connect via RDP, verify hotkeys work

2. **Phase 12** — filler words and snippets GUI (not started)

3. **Phase 13** — installer/distribution (blocked until 11 and 12 complete)

4. **Phase 9 VAD gap** — `SileroVADModel` uses wrong API, wastes RAM. On backlog,
   not addressed.

## Next Session Priorities

1. **Phase 9 hardware tests** — run all three manually (mic, sleep/wake, RDP)
2. **Phase 12, Step 1** — snippets: define snippet format in config, trigger on voice command
3. **Phase 12, Step 2** — filler words GUI: inline Treeview editor for filler word list
4. **Phase 12, Step 3** — settings GUI for snippets CRUD
5. **Phase 12, Step 4** — tests, target 176+ passing

## Files Changed This Session

| File | Change | Commit |
|---|---|---|
| `settings_gui.py` | Full profile manager GUI: Treeview + CRUD dialog + save wiring; height 1120→1300 | `cd9d3c8` |
| `test_features.py` | +20 tests: TestDeepMerge extended, TestProfileMatchEdgeCases, TestProfileLoadSave | `cd9d3c8` |
| `docs/sessions/alex-session-14-handover.md` | This file | committed separately |

## Key Reminders

- **Kill ALL python/pythonw before restarting Koda:** `taskkill //f //im pythonw.exe` AND `taskkill //f //im python.exe`
- **Run from source:** `cmd //c "C:\Users\alexi\Projects\koda\start.bat"` — no installer builds during dev
- **Tests:** `venv/Scripts/python -m pytest test_features.py` — 156 passing. Do NOT use plain `python -m pytest`
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
- **USB mic ARRIVED 2026-04-12** — Phase 9 hardware tests unblocked but NOT yet run
- **Owner full name: Alexis Concepcion** — use in legal/copyright contexts
- **Koda is personal/proprietary** — never suggest sharing repo or using personal GitHub from work PC
- **Distribution to work PC = exe only** (Phase 13) — no git clone, no personal credentials on work machine
- **Run /handover earlier** — at ~40% context, not 50%; user flagged this

## Migration Status
None — no database changes ever in this project.

## Test Status
- **156 tests passing** (`test_features.py`) — up from 136 at session start (+20 Phase 11 profile tests)
- `test_stress.py` — 17/17 standalone (from session 10, unchanged)
- All Phase 11 GUI CRUD logic covered by new tests (load/save/match/merge edge cases)

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
    "auto_capitalize": true
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
  "overlay_enabled": true
}
```
