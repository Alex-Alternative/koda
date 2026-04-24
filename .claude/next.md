# NEXT:

- [x] Merge PR #33 (prompt-assist v2 design doc) once Alex reviews — `https://github.com/Moonhawk80/koda/pull/33`
- [ ] Runtime-test `feat/voice-app-launch` (PR #28): golden path ("open word"), prefix invariant ("please open word" must NOT fire), error fallback ("open gibberish"). Do FIRST — validates the shared voice.py hot path before v2 builds on it.
- [x] **Prompt-assist v2 MVP** — built on `feat/prompt-assist-v2` (commit ffc400b, pushed origin, 421 tests). Pre-push gate ran clean (forge-deslop H1 + forge-review N1 closed). Live mic test deferred to next session.
- [ ] **Live mic test of `feat/prompt-assist-v2`** — kill installed v4.3.1, run from source via start.bat, press Ctrl+F9 in any AI app: validate TTS opener, 3-slot Q&A, overlay preview (Send/Refine/Add/Cancel + Escape), paste into original window. Smoke + edge cases (cancel mid-flow, short-circuit on long answer, confirmation 15s timeout). DO FIRST next session.
- [ ] **Fix statusline-command.sh** to render `.claude/next.md` first uncompleted `- [ ]` item — currently only shows model + context bar. Read `workspace.current_dir` from input JSON, find `.claude/next.md`, append first NEXT item truncated.
- [x] Voice-driven confirmation at CONFIRMING state (shipped 2026-04-24 commit `75e5366` on `feat/prompt-assist-v2`) — listener runs in parallel with overlay buttons, both route through same callbacks, 300ms bounded join on exit. Pre-push gate clean (forge-deslop 0, forge-review 0). 428/428 tests. Needs live mic validation.
- [ ] Re-add cancel-via-hotkey-repress for prompt-assist v2 — `cancel_slot_record` API was removed by forge-deslop tonight (no producer); add cleanly when prompt_press-during-active-conversation needs to cancel.
- [ ] Phase 16 licensing — blocks prompt-assist v2 paywall wrap (not the build itself). Decisions needed: tier count, subscription vs one-time, offline activation, durable "beta tester" marker (signed config / first-N installs / timestamp). Beta testers grandfather into free tier 2.
- [ ] Decide signing approach (Azure Trusted Signing $10/mo recommended) and wire into `.github/workflows/build-release.yml`
- [ ] Pick direction for Whisper "dash" dropout fix — read `project_dash_word_dropout.md` memory before proposing
- [x] Home-PC smoke test of public v4.3.1 installer (carried from session 41) — installed fresh from KodaSetup-4.3.1.exe tonight, 3 processes running confirmed.
- [ ] Wake word decision: train custom "hey koda" via openwakeword OR rip feature (currently detects "Alexa" behind the label)
- [ ] Phase 9 RDP test (pending since session 35)
- [ ] V2 app-launch: chaining ("open powershell and type git status"), window-ready check, "switch to X" for existing windows

## Waiting / Blocked

- **Coworker re-test of v4.3.1 mic-hotplug + music-bleed** — needs installer re-share first
