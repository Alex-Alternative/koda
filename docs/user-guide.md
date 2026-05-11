# Koda User Guide
**Version 4.4.0-beta1**

---

## What is Koda?

Koda is a push-to-talk voice transcription tool for Windows. Press a hotkey, speak, and your words are instantly typed into whatever you're working in — emails, Slack, Word, Excel, ChatGPT, Claude, anything.

No clicking a mic button. No switching apps. Just talk.

---

## Installation

1. Double-click **KodaSetup-4.4.0-beta1.exe**
2. If Windows shows a "protected your PC" warning, click **More info → Run anyway**
3. Follow the installer wizard
4. Koda launches automatically when installation completes

Koda appears as a small icon in your **system tray** (bottom-right corner of your screen, near the clock). That's how you know it's running.

### Hardware check during install

The installer runs a quick hardware check and picks defaults that match your machine — speech model size, CPU threads, process priority. You don't need to know what any of that means. Most users see one of these:

- **Recommended** — typical laptop or desktop, balanced speed and accuracy
- **Minimum** — older or low-RAM machine, lighter model for responsiveness
- **Power Mode** — NVIDIA GPU detected (RTX or similar), unlocks near-instant transcription with a larger, more accurate model. You'll see a short celebration page in the installer if this applies to you.

You can change any of this later in **Settings → Performance** if you want to tune it manually.

---

## Basic Usage

### Dictation — type by speaking

| Action | What to do |
|--------|-----------|
| Start recording | Hold **Ctrl + Space** |
| Speak | Talk naturally while holding |
| Paste transcription | Release **Ctrl + Space** |

Your words appear in whatever app or field was active when you pressed the hotkey.

**Tips:**
- Speak at a normal pace — no need to slow down
- Works in emails, Slack, Word, Excel, browsers, chat apps — anything
- A quiet room gives better accuracy than a great microphone
- Built-in laptop mic works fine. A USB headset is better.

---

## Hotkey Reference

| Hotkey | What it does |
|--------|-------------|
| **Ctrl + Space** | Hold to dictate, release to paste. In a terminal, spoken symbols are converted automatically (see Terminal Mode below) |
| **Ctrl + F9** | In Excel or Google Sheets — Formula Mode (speak a formula or navigate). Everywhere else — Prompt Assist (voice Q&A → structured prompt for ChatGPT or Claude) |
| **F8** | Voice command mode — speak editing commands like "select all", "undo", "bold" |
| **F7** | Correction — undoes your last paste and starts a new recording so you can try again |
| **F6** | Read back — Koda reads your last transcription aloud |
| **F5** | Read back the text you currently have selected |

---

## Prompt Assist — Talk to an AI without typing

Press **Ctrl + F9** anywhere outside Excel or Google Sheets. Koda starts a quick voice conversation that turns your spoken idea into a clean, structured prompt for ChatGPT, Claude, or any other AI tool.

### How it works

1. **You press Ctrl + F9.** Koda speaks the opener: *"What are we working on with AI today?"*
2. **You answer with the task.** Hold **Ctrl + F9** again and say what you want — "draft a follow-up email", "write a Python script that…", "explain this code".
3. **Koda asks for context.** Release the hotkey, and Koda asks one short follow-up to fill in any background — "What's the context?" or similar.
4. **You answer with context.** Hold **Ctrl + F9** again and speak the details.
5. **Koda previews the assembled prompt.** A small Atlas Navy overlay appears showing the final structured prompt.
6. **Confirm or cancel.** Say **"send"** (or press the listed hotkey) to paste it into your active window. Say **"cancel"** to discard.

The whole exchange is voice-only — you never touch the keyboard between hotkey presses.

### When it's useful

- Drafting prompts at the start of a long AI session, when you want the model to understand the task properly
- When you have a half-formed idea and want it cleaned up before sending
- Hands-free workflow on a long call or while reading reference material

If you don't want the voice Q&A and prefer to just dictate text directly into the chat window, use **Ctrl + Space** instead.

---

## Polish — clean up dictation with AI

"Polish" is an optional pass that fixes filler words, run-on sentences, and grammar in your transcribed text using a local AI model. It is **off by default** and requires a one-time setup.

### Two ways to use it

- **In Prompt Assist (Ctrl + F9)** — Polish is built into the flow. Your raw answers are turned into a tidy structured prompt automatically.
- **In regular dictation (Ctrl + Space)** — Off by default. Turn it on under **Settings → Advanced → Polish** if you want every transcription cleaned up before paste.

### Setup

You need one of:

- **[Ollama](https://ollama.com)** — free, local, no cloud. Install it, then run `ollama pull llama3.2:1b` in a terminal once. Koda will detect it automatically.
- **An API key** — bring your own OpenAI or Anthropic key. Add it under Settings → Advanced → Polish → API key.

Without one of these set up, Polish stays off and dictation pastes your raw transcription.

---

## System Tray Menu

Right-click the Koda tray icon for options:

- **Settings** — change hotkeys, microphone, performance tier, Polish, and more
- **History** — see your recent transcriptions
- **Stats** — usage stats (words transcribed, sessions, time saved)
- **Pause / Resume** — temporarily disable Koda
- **Quit** — close Koda

GPU users see a **Power Mode** badge in the tooltip when you hover over the tray icon.

---

## Settings

Open Settings by right-clicking the tray icon → **Settings**.

| Section | What's in it |
|---------|-------------|
| **Hotkeys** | Remap Ctrl+Space, Ctrl+F9, F6, F7, F8, F5. Switch between Hold and Toggle modes. |
| **Audio** | Microphone selection, VAD silence timeout, RMS threshold (for noisy environments). |
| **Performance** | Hardware tier dropdown — Auto-detect (default), Custom, Minimum, Recommended, Power. Advanced expander shows the underlying model size, CPU threads, process priority, compute type. |
| **Polish** | Turn AI polish on/off for regular dictation. Pick Ollama or BYO API provider. Manage saved API keys. |
| **Voice** | TTS voice and speech rate (used for Prompt Assist opener and read-back). |
| **Profiles** | Switch between dictation profiles (e.g. "Code", "Email") with different post-processing rules. |
| **Custom Words** | Words Whisper gets wrong consistently — add corrections here. |

### Performance tier — what each one means

| Tier | Use it for | What it picks |
|------|-----------|---------------|
| **Auto-detect** | Most users | Re-runs the hardware check each time Koda starts. If you upgrade your machine, Koda picks it up automatically. |
| **Custom** | You've tuned values manually and don't want them overwritten | Whatever you've set; Koda won't change them. |
| **Minimum** | Older / low-RAM machine | `tiny` model, 2 threads, normal priority. Fast but less accurate. |
| **Recommended** | Typical modern PC | `small` model, 4 threads, above-normal priority. Balanced. |
| **Power** | NVIDIA GPU (RTX-class) | `large-v3-turbo` model on CUDA float16, near-instant transcription. Auto-downloads the model on first use (~1.5 GB, one-time). |

---

## Microphone Tips

You don't need an expensive mic. Here's what to expect:

| Microphone | Quality | Notes |
|-----------|---------|-------|
| Built-in laptop mic | Good | Works well in a quiet room |
| USB headset / earbuds | Better | Recommended (~$20–40) |
| Dedicated USB mic | Best | Blue Yeti, HyperX (~$60–100) |

**The biggest factor is a quiet environment** — background noise matters more than mic quality.

Make sure your microphone is set as the **default recording device** in Windows:
> Right-click the speaker icon → Sound settings → Choose your input device

If background noise is a chronic problem, lower the **VAD RMS threshold** in Settings → Audio so Koda doesn't cut off mid-sentence.

---

## Formula Mode (Excel & Google Sheets)

Koda automatically detects when Excel or Google Sheets is your active window. No setup or toggle needed — just press **Ctrl + F9** and describe the formula you want.

### How to use it

1. **Click the cell** where you want the formula
2. **Hold Ctrl + F9** and speak your formula description
3. **Release** — Koda types the formula directly into the cell

That's it. You never need to know the exact formula syntax.

### What you can say

**Adding up numbers**

| What you say | What Koda types |
|---|---|
| sum B2 to B10 | `=SUM(B2:B10)` |
| sum column C | `=SUM(C:C)` |
| total of A1 to A20 | `=SUM(A1:A20)` |
| what's the sum of column B | `=SUM(B:B)` |

**Averages, max, min**

| What you say | What Koda types |
|---|---|
| average of column B | `=AVERAGE(B:B)` |
| average A1 to A20 | `=AVERAGE(A1:A20)` |
| maximum value in B2 to B10 | `=MAX(B2:B10)` |
| top of column C | `=MAX(C:C)` |
| minimum of A1 to A10 | `=MIN(A1:A10)` |

**Counting**

| What you say | What Koda types |
|---|---|
| count B2 to B10 | `=COUNT(B2:B10)` |
| how many items in column A | `=COUNT(A:A)` |
| count non-empty cells in column C | `=COUNTA(C:C)` |

**Today's date**

| What you say | What Koda types |
|---|---|
| today | `=TODAY()` |
| today's date | `=TODAY()` |

**IF statements — "if this, then that"**

| What you say | What Koda types |
|---|---|
| if A1 is greater than 10 then yes else no | `=IF(A1>10,"yes","no")` |
| if B1 is more than 100 then high else low | `=IF(B1>100,"high","low")` |
| if C1 is less than 50 then below target | `=IF(C1<50,"below target","")` |
| if A1 equals done then complete else pending | `=IF(A1="done","complete","pending")` |
| if B2 is at least 1000 then yes else no | `=IF(B2>=1000,"yes","no")` |

Words like *more than, bigger than, above, over* all mean `>`. Words like *at least, no less than* mean `>=`. You don't need to remember which symbol — just say it naturally.

**VLOOKUP — looking up a value in a table**

| What you say | What Koda types |
|---|---|
| vlookup A1 in B1 to D10 column 2 | `=VLOOKUP(A1,B1:D10,2,0)` |

### Tips

- **Whole columns work** — say "column C" instead of a range like C1:C100
- **No Excel knowledge needed** — describe what you want in plain English
- **Regular dictation still works** — if Koda doesn't recognize a formula pattern, it pastes your words as normal text, so nothing is lost
- **Ctrl + Space in Excel = plain dictation** — use this when you want to type notes or text, not formulas

### Excel navigation by voice

You can also navigate your spreadsheet with Ctrl + F9:

| What you say | What happens |
|---|---|
| go to B5 | Selects cell B5 |
| go to column C | Selects entire column C |
| go to row 5 | Selects entire row 5 |
| go home | Jumps to cell A1 |
| go to last row | Jumps to the last row with data |
| select all | Selects entire used range |

### Create tables by voice

| What you say | What happens |
|---|---|
| make a table | Converts your current selection into an Excel Table with auto-filter |
| create a table with columns Name Date Amount Status | Writes those headers at the active cell and creates the table |

### For complex formulas

If you need nested formulas or advanced logic, install [Ollama](https://ollama.com) (free, runs locally) and enable **Polish** in Settings → Advanced. Run `ollama pull llama3.2:1b` once to set it up. Koda will use the AI model to handle anything its built-in parser can't.

---

## Terminal Mode (Command Line)

When you use **Ctrl + Space** inside a terminal (Windows Terminal, PowerShell, Command Prompt, Git Bash, WSL), Koda automatically converts spoken symbols into shell syntax. No setup needed — it activates whenever a terminal is the active window.

### How to use it

Hold **Ctrl + Space**, speak your command naturally using words for symbols, then release.

### What you can say

| What you say | What Koda types |
|---|---|
| cd slash users slash alex slash projects | `cd /users/alex/projects` |
| cd backslash users backslash alex backslash projects | `cd \users\alex\projects` |
| tilde slash projects slash koda | `~/projects/koda` |
| git double dash version | `git --version` |
| npm install double dash save dev | `npm install --save dev` |
| ls dash l | `ls -l` |
| dot dot slash src | `../src` |
| cat file dot txt pipe grep error | `cat file.txt \| grep error` |
| echo hello greater than output dot txt | `echo hello > output.txt` |
| cd slash tmp and and ls | `cd /tmp && ls` |

### Symbol reference

| Say | Gets |
|---|---|
| slash / forward slash | `/` |
| backslash / back slash | `\` |
| tilde | `~` |
| double dash | `--` (use "double dash" not "dash dash" — Whisper compresses "dash dash" semantically) |
| dash + letter (e.g. "dash v") | `-v` |
| pipe | `\|` |
| greater than | `>` |
| double greater than | `>>` |
| and and / double ampersand | `&&` |
| star / asterisk | `*` |
| dollar / dollar sign | `$` |
| dot + extension (e.g. "dot txt") | `.txt` |
| dot dot | `..` |
| dot slash | `./` |
| dot dot slash | `../` |

**Auto-capitalize is disabled in terminal mode** — "cd /users" stays lowercase, not "Cd /users".

> **Windows paths use backslash** — say "backslash" for `\`. Unix paths (WSL, Git Bash) use "slash" for `/`.

---

## Transcribe Audio Files (Right-Click Menu)

Koda can transcribe existing audio files — voice memos, meeting recordings, podcast clips, anything. Right-click the file in Windows Explorer → **Transcribe with Koda**. A small window opens, runs the transcription, and shows the text with a Copy button.

Supported formats: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.webm`, `.wma`, `.aac`, `.opus`.

The installer registers this entry automatically. No setup needed.

### Windows 11 — "Show more options"

Windows 11 hides most custom right-click entries under a secondary menu. If you right-click an audio file and don't see **Transcribe with Koda**:

- Click **Show more options** at the bottom of the right-click menu, **or**
- Hold **Shift** while right-clicking to skip straight to the full menu

The entry will be in the expanded menu.

---

## Undoing a Paste

If Koda pastes something wrong, you have three options:

| How | What it does |
|---|---|
| Press **F7** | Undoes the last paste and starts a new recording so you can try again |
| Hold **Ctrl + Space**, say **"undo"** | Sends Ctrl+Z — just undoes, no re-recording |
| Hold **Ctrl + Space**, say **"delete that"** | Backspaces over the last paste |

---

## Voice Editing Commands

While holding **Ctrl + Space** (or F8 for command mode), speak these commands to control your editor without typing:

| Say | Action |
|---|---|
| undo | Ctrl+Z |
| redo | Ctrl+Y |
| select all | Ctrl+A |
| copy | Ctrl+C |
| cut | Ctrl+X |
| paste | Ctrl+V |
| save | Ctrl+S |
| delete that | Backspace |
| delete the word | Ctrl+Backspace |
| new line | Enter |
| new paragraph | Enter + Enter |
| bold | Ctrl+B |
| italic | Ctrl+I |
| go to the end | Ctrl+End |
| go home | Ctrl+Home |

### Voice-controlled app launching

Say "**open** _appname_" or "**launch** _appname_" during a Ctrl+Space dictation and Koda will open that program. Works for common apps (Word, Excel, Chrome, Notepad, Calculator, Spotify, Discord, Slack, Teams, plus anything in your Start Menu).

The prefix matters — "**please** open Word" will *not* fire. The first word has to be `open` or `launch`.

### In a terminal window

Terminal shortcuts are different from text editor shortcuts — Koda automatically uses the right ones when a terminal is the active window:

| Say | Terminal action | Why it's different |
|---|---|---|
| undo | Clears the current input line | PSReadLine doesn't undo synthetic pastes via Ctrl+Z — Escape (RevertLine) clears what was just pasted |
| delete / delete that | Clears the current input line | Same as undo — Escape reverts the line |
| delete the word | `Ctrl+W` — readline word delete | `Ctrl+Backspace` is less reliable in terminals |
| select all | `Ctrl+A` — moves cursor to start of line | No reliable keystroke selects just the current input line with a visual highlight |
| new line | Enter (runs the command) | Same as GUI |

**Suffix commands in terminal:** You can append a command at the end of your dictation. Koda pastes your text first, then fires the command — so "hello world new line" pastes `Hello world` and then hits Enter.

---

## Troubleshooting

**Koda isn't pasting anything**
- Make sure you're clicking into the text field first before pressing the hotkey
- Check the tray icon is green (running), not paused

**Hotkeys stopped working**
- Right-click tray icon → Quit, then relaunch Koda
- This is rare — Koda automatically recovers from most hotkey issues

**Transcription is inaccurate**
- Try a higher tier under **Settings → Performance** (Recommended → Power if you have a GPU)
- Reduce background noise
- Speak closer to the mic
- Add chronically misheard words to **Settings → Custom Words**

**Transcription is slow**
- Check **Settings → Performance** — Auto-detect should pick the right tier
- On older machines, try **Minimum** for snappier response (less accurate)
- On GPUs, confirm **Power** is selected — first launch downloads the turbo model (~1.5 GB)

**"No microphone detected"**
- Plug in your mic before launching Koda
- Set it as the default recording device in Windows Sound Settings

**Power Mode crashed on first launch (GPU users)**
- Older builds without cuDNN bundled would crash the first time CUDA initialized. This is fixed in v4.4.0-beta1 onward. If you're hitting this, you're on an old installer — reinstall from the latest `KodaSetup-*.exe`.

**Prompt Assist gets stuck on the opener**
- Make sure Polish is configured (Ollama running, or an API key set). Without one, Prompt Assist can't assemble the final prompt.
- Try **Quit** from the tray and relaunch.

---

## Uninstalling

Go to **Windows Settings → Apps → Installed apps**, find **Koda**, and click **Uninstall**.

Re-running the installer over an existing install also works — it'll close the running Koda, swap the exe, and relaunch automatically.

---

## Need Help?

Contact: alex@kodaspeak.com
