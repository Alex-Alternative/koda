# Prompt Assist v2 — Design Doc

*Date: 2026-04-23. Status: decisions locked, ready to build MVP.*

## What we're building

Press `ctrl+f9` → Koda speaks an opening question in a user-chosen voice → short slot-filling Q&A → assembles a structured prompt → shows + speaks it for confirmation → user confirms, refines, or adds → pastes into the focused app. Target platform detected from the active window; LLM refinement backend picked at install time.

Replaces today's silent one-shot `refine_prompt()` path with a conversational elicitation flow.

## Product strategy

- **Beta ships ungated, default ON.** All users get the feature. Dogfood free.
- **Paywall wraps after beta validation.** Once qualitative sentiment is positive, a ~2-line license check gates the conversational branch + install-wizard LLM picker. Free tier falls back to the existing silent `refine_prompt()`.
- **Beta testers grandfathered into free tier 2** as a thank-you — they keep paid features at no cost when licensing ships.
- Tier definitions and licensing mechanism are Phase 16 work and block the paywall wrap but NOT the build.

## Market context

Research (2026-04-23) confirms no shipped product does voice-first + conversational + prompt-as-artifact + OS-paste:

- **Wispr Flow / Superwhisper** — one-shot dictation, reformat to text, no elicitation
- **PromptPerfect / Promptable / PromptFolk** — text-only prompt builders, no voice, no paste
- **ChatGPT Voice / Gemini Live** — conversational but generate *answers*, don't hand back a reusable prompt
- **Pipecat / LiveKit Agents / Vocode** — frameworks, not products; closest building blocks but nobody has shipped a prompt-builder on top

The wedge is real. Closest prior art is Alexa's slot-filling dialog model — this design borrows from it.

## Design principles (from research)

1. **Slot-filling, not open conversation.** Each turn asks for exactly one dimension.
2. **3-turn ceiling, hard cap at 4.** Every extra turn doubles abandonment (NN/g, Voice UX Design Institute). Total interaction ≤30 seconds.
3. **Explicit end-of-turn signal.** Short audio cue ("ding") when Koda starts listening.
4. **One-word early-exit.** User can say "go" / "done" / "that's enough" to skip to confirmation.
5. **Don't narrate.** Never say "I'll now ask you three questions" — just ask.
6. **Confirm before paste, always.** Overlay window shows the full assembled prompt + Koda speaks a short summary. User has real agency at the final gate.

## The three slots

Collapsing Anthropic / OpenAI / CO-STAR / RTF frameworks, three dimensions capture ~80% of the quality gain:

1. **Task** — "What do you want the AI to do?" *Required.*
2. **Context** — "What does it need to know that it doesn't already?" *Highest-leverage per Anthropic's context-engineering work.*
3. **Format** — "What should the answer look like?" *Forecloses rambling.*

**Target platform is NOT a slot** — auto-detected from the active window (see Platform detection below). Asked only if detection fails.

Skipped deliberately on turn 1: role, tone, audience, examples. Inferred from task + pulled by the existing `_extract_details()` machinery in `prompt_assist.py`.

## Platform detection — hybrid

At hotkey press, read the foreground window (`win32gui.GetForegroundWindow` + `GetWindowText` + process name via `psutil` or `win32process`). Map to a known platform:

| Detection signal | Platform | Template tweak |
|---|---|---|
| `claude.exe`, tab title contains "Claude" | Claude | XML tags, `<thinking>` scaffold, explicit reasoning request |
| `chrome.exe` / `msedge.exe` + title "ChatGPT" | ChatGPT | Markdown, role prompt, numbered steps |
| `chrome.exe` / `msedge.exe` + title "Gemini" | Gemini | Direct instruction, structured output hints |
| `cursor.exe`, `code.exe` | Cursor / VS Code | File-context-first, code-fenced output |
| Anything else | generic | CO-STAR framework fallback |

If detection returns `generic` AND the user's answers don't imply a target, ask as a mandatory 4th slot: "Paste this into Claude, ChatGPT, or somewhere else?"

## State machine

```
IDLE
  └── [hotkey_press] ──> DETECT_PLATFORM ──> SPEAKING_OPENING
                                               │
                                               └── [tts_done] ──> LISTENING_TASK
                                                                    │
                                                                    ├── [silence] ──> ASSESSING_TASK
                                                                    ├── ["go"/"done"] ──> SHORT_CIRCUIT
                                                                    ├── ["cancel"] ──> CANCELLED
                                                                    └── [hotkey re-press] ──> CANCELLED

ASSESSING_TASK
  ├── [slot 1 answer is complete] ──> CONFIRMING   (short-circuit — user packed full prompt in)
  ├── [task captured, incomplete] ──> SPEAKING_CONTEXT_Q
  └── [task empty] ──> SPEAKING_TASK_RETRY (once, then assemble with what we have)

SPEAKING_CONTEXT_Q ──> LISTENING_CONTEXT ──> ASSESSING_CONTEXT ──> SPEAKING_FORMAT_Q
SPEAKING_FORMAT_Q ──> LISTENING_FORMAT ──> ASSEMBLING

SHORT_CIRCUIT ──> ASSEMBLING ──> CONFIRMING

CONFIRMING  (overlay window shows full prompt + TTS speaks short summary)
  ├── ["send" / "go"] ──> REFINING_VIA_LLM (if backend != none) ──> PASTING ──> IDLE
  ├── ["refine"] ──> REFINING_VIA_LLM ──> CONFIRMING  (loop back, show refined version)
  ├── ["add X"] ──> APPENDING + ASSEMBLING ──> CONFIRMING
  ├── ["explain" / "read it back"] ──> TTS_SPEAKS_FULL_PROMPT ──> CONFIRMING
  ├── ["cancel"] ──> CANCELLED
  ├── [Escape / hotkey re-press] ──> CANCELLED
  └── [15s silence] ──> CANCELLED (conservative — no auto-send)

CANCELLED ──> IDLE  (tray shows brief "Cancelled" badge)
```

**Cancel works three ways at any state** — spoken "cancel" / "never mind", Escape key, hotkey re-press.

**Completeness detection for short-circuit** — user is "done on slot 1" if:
- Response length > 40 words, AND
- `detect_intent(answer)` returns something other than `"general"` (so we have a recognized task type), AND
- At least one technical detail was extracted by `_extract_details()` (tech, language, file path, or quantity)

If only 1-2 of those conditions hit, still ask slot 2. Err on the side of asking; short-circuit is the fast-path for expert users.

## Confirmation step — interaction details

When `ASSEMBLING` completes:
1. Render the full assembled prompt in the **overlay window** (reuse `overlay.py` with a larger text mode — new `overlay.show_prompt_preview(text)` method).
2. **Speak a short summary** via TTS — NOT the full prompt (too long). Examples:
   - "Got a Python debug prompt with file context and JSON output. Send?"
   - "Drafted a Claude prompt about app-launch error handling. Ready?"
3. Listen for one of: `send` / `go` / `refine` / `add` / `explain` / `cancel`.
4. Route per the state machine above.

If the user says `"add"` followed by more speech ("add that it should be async"), capture the trailing speech and append to the prompt as a constraint, then re-assemble.

## Architecture fit

**New module: `prompt_conversation.py`.** Owns the state machine, slot recording, confirmation loop, LLM-backend routing, and platform detection. `prompt_assist.py` stays untouched — still the final template-assembly engine called by the state machine.

**Integration point — `voice.py:1230`:**

```python
elif event == "prompt_press":
    if config["prompt_assist"].get("conversational", True):   # default ON for beta
        from prompt_conversation import run_conversation
        threading.Thread(target=run_conversation, daemon=True).start()
    else:
        start_recording("prompt")   # existing silent one-shot path
```

**Overlay integration.** `overlay.py` extended with `show_prompt_preview(text, on_confirm, on_refine, on_add, on_cancel)` — a larger-mode overlay with the full prompt + callback handles for each response. Reuses existing window infrastructure.

**TTS integration.** Reuses `_get_tts()` at `voice.py:1061`. Warm at Koda startup to avoid cold-start latency on first hotkey press.

**Recording integration.** Per-slot bounded recordings with VAD-based end-detection (`vad.silence_timeout_ms` already exists, 1.5s default). Two consecutive silences or an explicit exit phrase advances.

## LLM refinement backend — install wizard

Install wizard step in `configure.py` (after voice picker, before hotkey setup):

```
How should Koda polish your prompts?

  1. None — template-only (recommended, zero setup)
  2. Local LLM via Ollama — free, private, ~2GB model download, install separately
  3. Your own API key — Claude or OpenAI, best quality, ~$0.01/prompt

Choose 1-3:
```

Default: 1 (None).

**Persistence:**
- Selection saved to `config["prompt_assist"]["refine_backend"]` = `"none" | "ollama" | "api"`.
- API key: NEVER stored in `config.json`. Use `win32crypt.CryptProtectData` or the `keyring` package (Windows backend = Credential Manager). Service name: `"koda-prompt-assist"`. Username per provider.
- Provider choice (Claude vs OpenAI) saved to `config["prompt_assist"]["api_provider"]`.

**Three code paths in `prompt_conversation.py`:**

```python
if mode == "none":
    final = refine_prompt(raw, config)   # template-only path, no LLM call
elif mode == "ollama":
    final = refine_prompt(raw, {**config, "prompt_assist": {..., "llm_refine": True}})
elif mode == "api":
    final = _api_refine(raw, config)     # reads credential from keyring at call time
```

**Offline fallback.** If `mode == "api"` and network fails, fall back to `"none"` silently with a one-time notification. Don't hang.

**Settings GUI** — add a dropdown in settings_gui.py for switching backends post-install.

## Voice selection — first-run picker (paired feature)

Sits in `configure.py:~625`, before the LLM picker:

```
Pick your Koda voice:
  1. [Zira]     "Hi, I'm Koda. Press F9 when you want to prompt AI."
  2. [Hazel]    "Hi, I'm Koda. Press F9 when you want to prompt AI."
  3. [David]    "Hi, I'm Koda. Press F9 when you want to prompt AI."

Choose 1-3:
```

Each option plays a sample line via new `voice.speak_with_voice(voice_id, sample_text)`. Selection saves to `config["tts"]["voice"]`. Existing `get_available_voices()` at `voice.py:1088` enumerates.

## TTS quality — Piper vs. pyttsx3

**MVP ships with pyttsx3 + SAPI5 (Zira default).** Robotic but zero new dependencies.

**V2 upgrade: Piper TTS via NaturalVoiceSAPIAdapter.** Offline, Windows-native, neural-quality, free, ~50-200ms synthesis. Piper voices surface through SAPI5 — existing pyttsx3 code keeps working, user installs the adapter once and picks a Piper voice in the first-run picker.

**Rejected:** Azure Neural (cloud dependency), ElevenLabs (metered cost), StyleTTS2/XTTS (GPU-heavy).

## MVP scope — what ships first

One feature branch: `feat/prompt-assist-v2`.

- [ ] `prompt_conversation.py` — state machine, 3 slots + confirmation, platform detection, early-exit phrases, cancel paths, LLM-backend router
- [ ] `voice.py` — conditional branch at `prompt_press`, TTS warm-start on init
- [ ] `config.py` — `"prompt_assist": {"conversational": True, "refine_backend": "none", "api_provider": null, "opener": "what are we building with AI today?"}`
- [ ] `configure.py` — voice picker + LLM refinement picker + API key capture flow with Credential Manager
- [ ] `overlay.py` — `show_prompt_preview()` larger-text mode with callback handles
- [ ] `settings_gui.py` — voice + LLM-backend dropdowns for post-install swap
- [ ] New helper for one-word intent detection ("go", "done", "cancel", "never mind", "send", "refine", "add", "explain") — probably in `text_processing.py`
- [ ] Audio cue — short "ding" on LISTENING state entry (reuse `sounds/start.wav` or new tone)
- [ ] Platform detection — `win32gui` + `win32process` / `psutil`, map to templates
- [ ] API-key storage via `keyring` package (add to requirements.txt)
- [ ] Platform-specific templates in `prompt_assist.py` (Claude / ChatGPT / Gemini / Cursor / generic)
- [ ] `test_features.py` — state-machine unit tests, mock TTS + recording, mock all three LLM backends

**Deferred to V2:**
- Piper TTS upgrade
- Follow-up questions within a slot ("you said Python — async?")
- Session memory ("same as last time but shorter")
- Prompt history playback

## Open questions — all resolved

1. ~~Default on or off?~~ **ON for everyone during beta.** Gates to paid later.
2. ~~Speak back / confirm?~~ **Required. Overlay + TTS summary.** User says send/refine/add/explain.
3. ~~Cancel ergonomics?~~ **All three paths work** — spoken "cancel" / "never mind", Escape, hotkey re-press.
4. ~~Short-circuit?~~ **Yes** — if slot 1 answer is complete (>40 words + recognized intent + ≥1 extracted detail), skip to confirmation.
5. ~~LLM backend?~~ **Install wizard: Ollama / BYO API / None, default None.**
6. ~~Paid-tier gating?~~ **Build ungated first, gate after beta, grandfather beta testers into free tier 2.**

## Risk / mitigations

- **TTS cold-start latency** (~300-800ms). *Mitigate: warm TTS at Koda startup with a zero-length say().*
- **Overlay confusion** during slot progression. *Mitigate: compact slot state indicator ("1/3 Task" → "2/3 Context" → "3/3 Format" → "Confirm").*
- **VAD false-triggers** (user pauses mid-sentence, Koda advances). *Mitigate: 1.5s silence threshold, advance only on 2 consecutive silences or explicit exit phrase.*
- **Robotic voice kills vibe on day 1.** *Mitigate: voice picker (3 options) at install, prioritize Piper V2 upgrade if feedback confirms.*
- **API key leakage.** *Mitigate: Credential Manager only, never config.json, never logged, pulled fresh per call.*
- **Network fragility on API mode.** *Mitigate: silent fallback to "none" with one-time notification, don't hang.*
- **Feature creep in `prompt_conversation.py`.** *Mitigate: hard line — MVP ships exactly this scope. Every other dimension waits for V2.*

## Work estimate

- State machine + slot flow + confirmation step: ~1.0 session
- Platform detection via active window: ~0.25 session
- Install wizard (voice + LLM + API key): ~0.75 session
- Credential Manager integration: ~0.25 session
- Settings GUI post-install swap UI: ~0.25 session
- Overlay preview mode: ~0.25 session
- Unit tests across three LLM backends + mocks: ~0.5 session
- E2E runtime test (golden path + short-circuit + cancel + each LLM backend + platform detection): ~0.25 session

**Total: ~3.5 sessions.** Bumped from the original 1.5-session estimate because of Option C (install wizard + Credential Manager + three backends + confirmation step).

## Next steps

1. Alex reads this doc.
2. Approve opener text ("what are we building with AI today?") and exit phrases (go / done / cancel / send / refine / add / explain) — or propose tweaks.
3. Confirm MVP scope is right.
4. Build on `feat/prompt-assist-v2`, runtime-test each branch of the state machine, PR.

## References

- Anthropic — [Prompt-engineering best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Anthropic — [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Alexa Skills Kit — [Dialog Management / Slot Filling](https://developer.amazon.com/en-US/docs/alexa/custom-skills/define-the-dialog-to-collect-and-confirm-required-information.html)
- NN/g — [Intelligent Assistants Have Poor Usability](https://www.nngroup.com/articles/intelligent-assistant-usability/)
- Google Design — [Speaking the Same Language (VUI)](https://design.google/library/speaking-the-same-language-vui)
- Piper TTS — [rhasspy/piper VOICES.md](https://github.com/rhasspy/piper/blob/master/VOICES.md)
- NaturalVoiceSAPIAdapter — [gexgd0419/NaturalVoiceSAPIAdapter](https://github.com/gexgd0419/NaturalVoiceSAPIAdapter)
- CO-STAR framework — [portkey.ai/blog/what-is-costar-prompt-engineering/](https://portkey.ai/blog/what-is-costar-prompt-engineering/)
- Python `keyring` package — [github.com/jaraco/keyring](https://github.com/jaraco/keyring)
