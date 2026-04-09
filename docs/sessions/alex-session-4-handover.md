# Alex Session 4 Handover — 2026-04-09

## Branch
`master` — pushed to `origin/master`, up to date. No uncommitted changes.

## Repo
**https://github.com/Alex-Alternative/koda** — Working dir: `C:\Users\alex\Projects\koda`

## What Was Built This Session

### Phase 2 — All 4 features complete (commit 4620f7f)

1. **Floating status overlay** (`overlay.py` — NEW)
   - Always-on-top draggable transparent widget using tkinter
   - Shows recording state (Ready/Recording/Transcribing/Reading/Listening) with color-coded dot
   - Live streaming text preview during recording
   - Semi-transparent when idle, full opacity when active
   - Toggleable from tray menu and settings GUI
   - Right-click to hide, remembers drag position

2. **Auto-formatting rules** (`text_processing.py`)
   - Spoken numbers → digits: "one hundred twenty three" → "123" (only when scale word like hundred/thousand present, to avoid mangling times like "two thirty")
   - Spoken dates → formatted: "january fifth twenty twenty six" → "January 5, 2026"
   - Smart punctuation: "em dash" → —, "dot dot dot" → ..., "exclamation point" → !
   - Fixed stutter removal to not eat number words ("twenty twenty" preserved)
   - Fixed processing order: smart punctuation runs before filler removal
   - Fixed ellipsis "..." not being collapsed by period cleanup regex
   - Dollar and percent suffix handling: "five hundred dollars" → "$500"
   - Toggleable via `post_processing.auto_format` config key

3. **Per-app profiles** (`profiles.py`, `profiles.json` — both NEW)
   - Background thread polls active window every 1 second using ctypes (no extra deps)
   - Detects process name and window title via Windows API
   - Matches against configurable profiles in `profiles.json`
   - Deep-merges profile settings over base config
   - Default profiles: VS Code (code vocab on), Terminal (code vocab on), Slack, Outlook, Notepad
   - Users can add custom profiles matching by process name or title regex
   - Tray menu shows current profile, toggle on/off
   - "Edit app profiles" opens profiles.json in default editor

4. **Audio file transcription** (`transcribe_file.py` — NEW)
   - GUI window with file browser for .wav/.mp3/.m4a/.flac/.ogg/.webm/.wma
   - Language selection and optional timestamps
   - Results displayed in text area with copy-to-clipboard and save-as-txt
   - Accessible from tray menu → "Transcribe audio file"
   - Uses the already-loaded Whisper model (beam_size=5, vad_filter=True for files)

### Phase 3 — 3 of 4 features complete (commits 1f75dad, 745aacb)

5. **Voice editing commands** (`voice_commands.py` — NEW)
   - 30+ spoken commands: select all, undo, redo, delete that, new line, new paragraph, go to end, select word, delete line, save, find, bold, italic, etc.
   - Pattern matching with regex: full-utterance commands, prefix commands, suffix commands
   - Commands stripped from text output — they control the editor, not the text
   - Logged to history as `[cmd: Select all text]` etc.
   - Fixed regex grouping bug where `|` alternatives weren't wrapped in `(?:...)`
   - Toggleable via `voice_commands` config key

6. **Real-time translation** (in `voice.py`)
   - Two modes:
     - **Any language → English**: Uses Whisper's native `task="translate"` parameter (fast, no extra deps)
     - **Any language → other language**: Whisper transcribes, then Ollama LLM translates (requires Ollama running)
   - Tray submenu with radio buttons: Off, → English, → Spanish, → French, → German, → Portuguese, → Japanese, → Korean, → Chinese, → Italian, → Russian
   - Settings GUI has translation section with enable checkbox and target language dropdown
   - Config: `translation.enabled` and `translation.target_language`

7. **Windows Explorer context menu** (`context_menu.py` — NEW)
   - Right-click any audio file → "Transcribe with Koda"
   - Registry-based (HKEY_CURRENT_USER, no admin needed)
   - Supports 9 audio extensions: .wav, .mp3, .m4a, .flac, .ogg, .webm, .wma, .aac, .opus
   - Install/uninstall via CLI: `python context_menu.py install/uninstall`
   - Also installable from tray menu → "Install Explorer right-click menu"
   - Opens standalone transcription window with file pre-loaded
   - **Already installed** on this machine (registered during testing)

8. **Wake word via Porcupine** — BLOCKED (dedicated mic not arrived)

### Koda.exe Rebuild (commit 745aacb)

- Updated `build_exe.py` to bundle all 11 modules from Phase 1-3
- Rebuilt successfully: **276 MB** at `dist/Koda.exe`
- Includes bundled Whisper base model (zero-download install)
- All Phase 1, Session 3, Phase 2, and Phase 3 features included
- Version bumped to **3.0.0**

### Market Research Response: Phone App
- Discussed whether Koda should have a mobile app
- Conclusion: **No, stay desktop-focused.** iOS/Android built-in dictation is too deeply integrated to compete with. Koda's moat is desktop (Windows Dictation is limited/cloud-only). Potential future: companion app or audio-file-transcription-only mobile tool.

## Decisions Made

1. **Number conversion threshold**: Only convert spoken numbers when a scale word (hundred, thousand, million) is present. Prevents "two thirty" (time) and "twenty twenty" (year) from being mangled. Single number words like "one" are never converted.

2. **Processing pipeline order**: Smart punctuation → dates → numbers → filler removal → capitalize. Smart punctuation must run before filler removal so "dot dot dot" → "..." isn't eaten by the stutter remover.

3. **Stutter removal safe list**: Number words and common repeatable words ("the the" kept, "twenty twenty" kept) are excluded from stutter deduplication.

4. **Profile detection via ctypes**: Used Windows API directly (ctypes.windll.user32/kernel32) instead of pywin32 to avoid adding a dependency. Works for process name and window title detection.

5. **Translation architecture**: English target uses Whisper native translate (fast, reliable). Non-English targets use Ollama LLM (requires Ollama running, slower but works for any language pair).

6. **Context menu uses HKCU**: No admin elevation needed — writes to per-user registry keys under `Software\Classes\SystemFileAssociations`.

7. **Voice commands only match whole utterances or start/end**: Prevents false positives in the middle of natural speech. "Please select all the files" won't trigger "select all" — but "select all" by itself will.

## User Feedback & Corrections

1. **"Make it a big deal next time we have something overdue"** — The Koda.exe rebuild was stale since session 2. Alex wants overdue items flagged prominently at session start, not buried in lists. Saved as a feedback memory.

2. **Phone app question** — Alex asked about a mobile version. I gave honest analysis: not worth it now, desktop is the differentiator. Alex seemed satisfied with this assessment.

## Waiting On

- **Dedicated microphone** — ordered but not arrived. Wake word (Porcupine) is blocked on this.
- **Ollama** — must be running for translation to non-English languages and LLM polish. Currently at `C:\Users\alex\AppData\Local\Programs\Ollama\ollama.exe` with phi3:mini pulled.

## Next Session Priorities

### Phase 4 (from market research roadmap)
1. **Usage stats dashboard** — track words dictated, time saved, most-used commands, per-app usage
2. **Plugin/extension system** — allow third-party extensions for custom processing
3. **Product Hunt launch prep** — landing page, screenshots, demo video, pitch
4. **MSI installer for enterprise** — proper Windows installer instead of .exe + .bat

### Still pending from Phase 3
5. **Wake word via Porcupine** — blocked on dedicated mic hardware

### Maintenance
6. **README update** — needs to reflect Phase 2-3 features (overlay, profiles, voice commands, translation, context menu, file transcription)
7. **Test coverage** — no new tests written this session for Phase 2-3 features

## Files Changed This Session

| File | What changed |
|---|---|
| `overlay.py` | **NEW** — Floating status overlay widget (tkinter, always-on-top, draggable) |
| `profiles.py` | **NEW** — Per-app profile matching and monitoring (ctypes window detection) |
| `profiles.json` | **NEW** — Default app profiles (VS Code, Terminal, Slack, Outlook, Notepad) |
| `transcribe_file.py` | **NEW** — Audio file transcription GUI window |
| `voice_commands.py` | **NEW** — 30+ voice editing commands with regex pattern matching |
| `context_menu.py` | **NEW** — Windows Explorer context menu install/uninstall + standalone transcriber |
| `voice.py` | Integrated overlay, profiles, voice commands, translation, context menu, file transcription. Version → 3.0.0 |
| `config.py` | Added defaults: `auto_format`, `overlay_enabled`, `profiles_enabled`, `voice_commands`, `translation` |
| `config.json` | Updated with readback hotkeys, fixed mic_device=null, disabled wake_word/llm_polish |
| `settings_gui.py` | Added: auto-format toggle, overlay toggle, profiles toggle, voice commands toggle, translation section, edit profiles button |
| `text_processing.py` | Added: `format_spoken_numbers()`, `format_spoken_dates()`, `format_smart_punctuation()`, `_parse_spoken_year()`, fixed stutter removal |
| `build_exe.py` | Updated to bundle all 11 modules, prints size on completion |

## Current Config State
```json
{
  "model_size": "base",
  "language": "en",
  "output_mode": "auto_paste",
  "hotkey_dictation": "ctrl+space",
  "hotkey_command": "ctrl+shift+.",
  "hotkey_correction": "ctrl+shift+z",
  "hotkey_readback": "ctrl+shift+r",
  "hotkey_readback_selected": "ctrl+shift+t",
  "hotkey_mode": "hold",
  "mic_device": null,
  "sound_effects": true,
  "notifications": false,
  "noise_reduction": false,
  "streaming": true,
  "post_processing": {
    "remove_filler_words": true,
    "code_vocabulary": false,
    "auto_capitalize": true,
    "auto_format": true
  },
  "vad": { "enabled": true, "silence_timeout_ms": 1000 },
  "wake_word": { "enabled": false, "phrase": "hey koda" },
  "llm_polish": { "enabled": false, "model": "phi3:mini" },
  "tts": { "rate": "normal", "voice": "" },
  "overlay_enabled": true,
  "profiles_enabled": true,
  "voice_commands": true,
  "translation": { "enabled": false, "target_language": "English" }
}
```

## Key Reminders

- **Venv** at `C:\Users\alex\Projects\koda\venv` — all deps installed
- **Desktop** is at `C:\Users\alex\OneDrive\Desktop` (OneDrive sync)
- **GitHub CLI** at `"C:\Program Files\GitHub CLI\gh.exe"`, auth as `Alex-Alternative`
- **Ollama** at `C:\Users\alex\AppData\Local\Programs\Ollama\ollama.exe`, phi3:mini pulled
- **Python 3.14** — tflite-runtime has no wheels, openwakeword uses ONNX
- **mic_device = null** — don't hardcode indices, they shift
- **pyttsx3 COM threading** — must init lazily in the thread that uses it
- **LLM polish / translation** — disabled by default, Ollama must be running
- **Dedicated mic** ordered but not arrived — wake word blocked on this
- **Koda.exe** at `dist/Koda.exe` (276MB) — **REBUILT this session, fully up to date**
- **Context menu installed** on this machine — right-click audio files works
- **Flag overdue items loudly** — don't let stale builds or pending work slip quietly between sessions

## Migration Status
None this session.

## Test Status
- Existing tests from session 3 (`test_stress.py`, `test_wakeword.py`) unchanged
- Auto-formatting tested extensively via inline Python (numbers, dates, punctuation, edge cases)
- Voice command pattern matching tested via mock (12 test cases)
- Profile matching tested via mock (process name, window title, deep merge)
- **No new test files written this session** — coverage gap for Phase 2-3 features
