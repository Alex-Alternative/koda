# NEXT:

- [x] Merge open PRs: #24 (session 41 handover), #26 (perf), #27 (session 42 handover), #28 (app-launch MVP), #29 (pre-push gate rule), #30 (session 43 handover), #31 (session 43 addendum)
- [ ] Runtime-test `feat/voice-app-launch` (PR #28): golden path ("open word"), prefix invariant ("please open word" must NOT fire), error fallback ("open gibberish")
- [ ] Prompt-assist v2 MVP — conversational Q&A + confirmation + platform detection + install-wizard LLM picker. Full design at `C:\Users\alex\Projects\koda\docs\prompt-assist-v2-design.md`. All 6 open questions resolved. Build on `feat/prompt-assist-v2`. Est. ~3.5 sessions. Paired: voice picker + LLM refinement picker in `configure.py`.
- [ ] Phase 16 licensing — now blocking prompt-assist v2 paywall wrap. Beta testers must be grandfathered into free tier 2. Need: tier structure, subscription vs one-time, offline activation, durable "beta tester" marker (signed config / first-N installs / timestamp-based).
- [ ] Decide signing approach (Azure Trusted Signing $10/mo recommended) and wire into `.github/workflows/build-release.yml`
- [ ] Pick direction for Whisper "dash" dropout fix — read `project_dash_word_dropout.md` memory before proposing
- [ ] Home-PC smoke test of public v4.3.1 installer (carried from session 41)
- [ ] Wake word decision: train custom "hey koda" via openwakeword OR rip feature (currently detects "Alexa" behind the label)
- [ ] Phase 9 RDP test (pending since session 35)
- [ ] Phase 16 license-system decisions — tier count, subscription vs one-time, offline activation
- [ ] V2 app-launch: chaining ("open powershell and type git status"), window-ready check, "switch to X" for existing windows

## Waiting / Blocked

- **Coworker re-test of v4.3.1 mic-hotplug + music-bleed** — needs installer re-share first
