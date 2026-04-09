# Koda

Push-to-talk voice input for any app. Speak into your microphone and your words get transcribed and pasted directly into Claude Code, ChatGPT, Google Chat, Slack, email — any active window.

Runs locally using [Whisper](https://github.com/openai/whisper) — no cloud API, no cost, fully offline after initial setup.

---

## Features

- **Push-to-talk** — Hold a hotkey to record, release to transcribe and paste
- **Two modes** — Dictation (light cleanup) and Command (full cleanup for coding)
- **Filler word removal** — Strips "um", "uh", "you know", "basically"
- **Code vocabulary** — Say "open paren" and get `(`, "camel case user name" → `userName`
- **Read-back** — Koda reads your last transcription or selected text aloud
- **Correction mode** — Undo last paste and re-record
- **LLM polish** — Optional local AI cleanup via Ollama (free, no API costs)
- **Sound effects** — Audio chimes for recording start/stop/success
- **System tray app** — Runs silently with a color-coded status icon
- **Hold-to-talk or Toggle** — Hold the key, or press once and it auto-stops via VAD
- **Noise reduction** — Optional background noise filtering
- **Offline** — All processing happens locally
- **Auto-start** — Optional Windows startup integration

---

## Requirements

- **Windows 10 or 11**
- **Python 3.10 or newer** — [Download here](https://www.python.org/downloads/)
  - During installation, **check "Add Python to PATH"**
- **A microphone** (USB, headset, or built-in)
- **~500MB disk space** (for packages + Whisper model)
- **Ollama** (optional, for LLM polish) — [Download here](https://ollama.com/download)

---

## Installation

### Step 1: Download

```
git clone https://github.com/Alex-Alternative/koda.git
cd koda
```

Or click **Code → Download ZIP** on GitHub, extract to a folder like `C:\koda`.

### Step 2: Run the installer

1. Open the folder in File Explorer
2. **Double-click `install.bat`**
3. Follow the setup wizard (picks your mic, hotkeys, preferences)

### Step 3: Verify (optional)

Double-click **`test.bat`** to run the stress test.

---

## Usage

### Starting Koda

**Double-click `start.bat`**

A microphone icon appears in your system tray (bottom-right, near the clock). Click the **^** arrow if hidden.

| Icon Color | Status |
|---|---|
| Gray | Loading model (~10 seconds) |
| Green | Ready |
| Red | Recording |
| Orange | Transcribing |
| Purple | Reading aloud |

### Hotkey Reference

| Hotkey | Action |
|---|---|
| **Ctrl+Space** | Dictation — hold to talk, release to paste (light cleanup) |
| **Ctrl+Shift+Period** | Command mode — hold to talk (full cleanup + code vocab) |
| **Ctrl+Shift+Z** | Correction — undo last paste and re-record |
| **Ctrl+Shift+R** | Read back — reads last transcription aloud |
| **Ctrl+Shift+T** | Read selected — reads highlighted text aloud |

All hotkeys are configurable in `config.json` or via the setup wizard (`configure.bat`).

### Right-click tray menu

- Toggle sound effects, filler removal, code vocabulary, noise reduction, LLM polish
- Switch between Hold and Toggle mode
- Open settings file
- Quit

---

## Configuration

All settings are in `config.json` (created on first run). Edit directly or use the tray menu.

### Key settings

| Setting | Default | Description |
|---|---|---|
| `hotkey_dictation` | `"ctrl+space"` | Dictation mode hotkey |
| `hotkey_command` | `"ctrl+shift+."` | Command mode hotkey |
| `hotkey_correction` | `"ctrl+shift+z"` | Undo and re-record |
| `hotkey_readback` | `"ctrl+shift+r"` | Read last transcription aloud |
| `hotkey_readback_selected` | `"ctrl+shift+t"` | Read selected text aloud |
| `hotkey_mode` | `"hold"` | `"hold"` or `"toggle"` (auto-stops on silence) |
| `model_size` | `"base"` | `tiny`, `base`, `small`, `medium`, `large-v3` |
| `language` | `"en"` | Speech language |
| `mic_device` | `null` | Mic device index or `null` for system default |
| `sound_effects` | `true` | Play chimes on record/stop/paste |
| `noise_reduction` | `false` | Filter background noise (slower) |
| `remove_filler_words` | `true` | Strip "um", "uh", etc. |
| `code_vocabulary` | `false` | Expand "open paren" → `(` in command mode |
| `llm_polish.enabled` | `false` | AI cleanup via Ollama |
| `llm_polish.model` | `"phi3:mini"` | Ollama model to use |

### Whisper model sizes

| Model | Download | Speed | Accuracy |
|---|---|---|---|
| `tiny` | ~75MB | Fastest | Lower |
| `base` | ~150MB | Fast | Good — **recommended** |
| `small` | ~500MB | Medium | Better |
| `medium` | ~1.5GB | Slower | High |
| `large-v3` | ~3GB | Slowest | Highest |

---

## LLM Prompt Polish (Optional)

Command mode can use a local AI model to clean up your speech into clear instructions.

**Setup:**
1. Install Ollama: https://ollama.com/download
2. Open a terminal and run: `ollama pull phi3:mini`
3. Enable in config: set `"llm_polish": {"enabled": true, "model": "phi3:mini"}`
4. Make sure Ollama is running before using command mode

**Example:**
- You say: *"uh can you like go into the database and um fix that thing where the dates are wrong"*
- Pasted: *"Fix the date formatting issue in the database"*

---

## Code Vocabulary (Command Mode)

When enabled, these spoken words expand in command mode:

| You say | You get |
|---|---|
| "open paren" / "close paren" | `(` / `)` |
| "open bracket" / "close bracket" | `[` / `]` |
| "open brace" / "close brace" | `{` / `}` |
| "semicolon" | `;` |
| "equals" / "double equals" | `=` / `==` |
| "arrow" / "fat arrow" | `->` / `=>` |
| "new line" | actual line break |
| "hash" | `#` |
| "pipe" | `\|` |

### Case formatting

| You say | You get |
|---|---|
| "camel case user name" | `userName` |
| "snake case get user data" | `get_user_data` |
| "pascal case my component" | `MyComponent` |
| "kebab case page title" | `page-title` |
| "screaming snake max retries" | `MAX_RETRIES` |

---

## Auto-Start with Windows

Double-click **`install_startup.bat`** to start Koda on login.

Double-click **`uninstall_startup.bat`** to remove.

---

## Troubleshooting

### Short phrases not transcribing
- Hold the key a beat longer before and after speaking
- The Whisper model needs at least ~1 second of audio

### No sound effects
- Check your Windows audio output device
- Sounds play through the system default output

### Transcription is slow
- Use the `tiny` or `base` model in config
- Close CPU-heavy applications

### Wrong microphone
- Set `mic_device` to `null` in config (uses system default)
- Or change your default mic in Windows: Settings → System → Sound → Input

### LLM polish not working
- Make sure Ollama is running: open a terminal, run `ollama serve`
- Make sure the model is downloaded: `ollama pull phi3:mini`

### App stops pasting after read-back
- Restart Koda (right-click tray → Quit, then double-click start.bat)

---

## Files

| File | Purpose |
|---|---|
| `voice.py` | Main application |
| `config.py` | Configuration management |
| `text_processing.py` | Filler removal, code vocab, case formatting |
| `config.json` | Your settings (auto-created) |
| `configure.py` | Interactive setup wizard |
| `configure.bat` | Re-run setup wizard |
| `install.bat` | One-time installer |
| `start.bat` | Launch Koda |
| `test.bat` | Run stress tests |
| `test_stress.py` | Stress test suite |
| `install_startup.bat` | Add to Windows startup |
| `uninstall_startup.bat` | Remove from startup |
| `generate_sounds.py` | Generate sound effect .wav files |
| `build_exe.py` | Build standalone Koda.exe |
| `requirements.txt` | Python dependencies |

---

## Building the .exe (for distribution without Python)

```
cd koda
venv\Scripts\activate
python build_exe.py
```

Output: `dist\Koda.exe` (~150MB). Users still need to download the Whisper model on first run.

---

## License

MIT
