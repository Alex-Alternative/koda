---
session: 42
date: 2026-04-21
scope: koda
resumes-from: alex-session-41-work-pc-handover.md
continues-work-from: null
projects-touched: [koda]
skills-activated: [forge-handover]
---

# Work-PC Session 42 Handover — 2026-04-21

Short session. Continued from session 41. Real-world bug report surfaced mid-session; root-cause diagnosed but fix parked pending a fresh brain. No source changes committed.

## Branch
`master` at `25bcc94`. Working tree clean. Up to date with `origin/master`.

Note on starting state: session 41 handover claimed master was at `9b33c50` with PR #25 still open. That was stale — PR #25 had merged on 2026-04-20T22:35:19Z as `25bcc94`. Fast-forwarded local at session start to sync.

## TL;DR

1. Diagnosed a production Whisper bug — transcription drops the literal word "dash" (e.g. "language dash font" → "language font"). Confirmed the loss is at the ASR layer, not in Koda's post-processing pipeline.
2. Proposed `initial_prompt` biasing as the fix. **Alex rejected** — wants a deterministic mechanism, not a heuristic. Decision parked.
3. Saved durable memory (`project_dash_word_dropout.md`) so the next session does not re-propose the rejected approach.
4. No commits, no pushes, no code edits. Master unchanged from session 41's final state (apart from the pre-existing PR #25 merge we fast-forwarded).
5. PR #24 (session 41 handover) still open; PR #25 (Node 24 CI bump) already merged contrary to session 41's writeup.

## What Was Built This Session

Nothing. This was a diagnostic + decision-deferral session.

## Decisions Made

### Park the "dash" dropout fix until Alex can decide fresh

Alex's verbatim response when I proposed the `initial_prompt` approach:

> "i don't like the initial prompt bullshit rule. we need a better fix for that. maybe a rule or something. i don't know. i can't think right now. i'm burnt out."

Interpretation: he doesn't want a heuristic / prompt-injection style fix for this class of problem. He wants something more deterministic — "a rule or something". He was clear he didn't have the bandwidth to decide between alternatives tonight, so the correct response was to stop pushing, save the context, and end the session cleanly.

No code written. No PR opened. Decision deferred to a future session.

## User Feedback & Corrections

### "Initial prompt biasing is brittle" — rejected as general Whisper fix strategy

Quote above. Captured in `project_dash_word_dropout.md` under "Options NOT to propose again" so the next session does not waste cycles re-suggesting it.

**Pattern watch (not yet durable feedback, just a single data point):** Alex appears to prefer deterministic mechanisms over hand-wavy heuristics when facing ASR / text-processing bugs. If this reappears on a second unrelated problem, promote it to a feedback memory entry. One data point is not enough.

### Burnout is a stop signal, not a debugging prompt

Alex stated he was burnt out. Correct response was to stop all further analysis, save state, offer to close the session — not to pile on alternative technical options. Confirmed as the right move when he replied "yes" to the handover offer.

## Dead Ends Explored

### `initial_prompt` Whisper biasing — rejected

**Considered:** Set a default `initial_prompt` at `voice.py:778` containing a short sentence that uses "dash" literally (e.g. `"Use the dash key, underscore, plus, minus literally."`) to prime Whisper to keep the word. Stack on top of existing `custom_vocabulary`-based prompt when present.

**Why rejected:** Alex explicitly called it "bullshit" and wants a deterministic fix. Prompt biasing is probabilistic — it nudges the decoder distribution but gives no guarantee the target word will appear. Fair objection for a user-facing dictation tool where consistent behavior matters more than mean-case correctness.

**Discussed around:** fourth assistant turn of the session (the "Plan" proposal).

### Suggesting the user add `"dash": "dash"` to custom vocabulary — rejected by implication

**Considered:** Tell Alex to work around the bug via the Settings → Custom Vocabulary UI, which routes the word through the same `initial_prompt` pathway without needing a code change.

**Why rejected:** This is equivalent to the `initial_prompt` fix internally — same probabilistic biasing mechanism. Alex's rejection applies. Captured in the memory note so it is not re-proposed.

## Options Still Open for the Dash-Dropout Fix

Captured in `project_dash_word_dropout.md`, reproduced here for handover continuity:

- `suppress_tokens=[hyphen_token_id]` — deterministic at the decoder level. Regresses hyphenated compounds ("long-term" → "long term"). Tradeoff analysis needed.
- Upgrade default Whisper model from `small` to `medium` / `large-v3` — the quirk weakens on bigger models. Cost: compute + latency on Intel UHD 770 (no CUDA).
- `word_timestamps=True` + gap detection → targeted second-pass transcription of gaps. Complex, probably disproportionate to the bug size.
- A combined "literal words" config: deterministic token suppression + post-process hyphen restoration for compound-word contexts. Most promising if the simple suppress-tokens regression on compounds is acceptable in narrow form.

Do NOT build any of these without Alex's direction — the whole point of parking was that the decision belongs to him when he is not burnt out.

## Skills Activated This Session

- **forge-handover** — this invocation. User asked "yes" to running it after confirming nothing was uncommitted. Outcome: this handover file + inline new-session prompt. Report path: N/A (this skill does not produce a run-directory).

No other forge-* skills ran.

## Memory Updates

Written mid-session (already on disk):

- `~/.claude/projects/C--Users-alex-Projects-koda/memory/project_dash_word_dropout.md` (new) — full context on the Whisper dash-dropout bug, rejected approaches, and remaining options.
- `~/.claude/projects/C--Users-alex-Projects-koda/memory/MEMORY.md` — index entry appended.

No further memory writes in this handover step.

## Waiting On

- **Alex's decision** on the dash-dropout fix direction (one of the four open options above, or something else entirely he proposes when fresh).
- **Coworker** to re-test v4.3.1 with the mic-hotplug fix, per session 41 next-up list. No update this session.

## Next Session Priorities

1. **Merge PR #24** (session 41 handover doc) — still open on `Moonhawk80/koda`, mergeable, no checks required.
2. **Write a new PR for this handover** (session 42) once Alex reviews the file. Work-PC rule: no direct pushes to master.
3. **Alex decides the dash-dropout fix strategy** — read `project_dash_word_dropout.md` memory entry first so the rejected options are not re-proposed.
4. Re-share v4.3.1 installer with coworker and confirm mic-hotplug recovery works on his machine (carried from session 41).
5. Music-bleed follow-up — if `noise_reduction` toggle does not resolve the Whisper hallucinations during background music, tighten `no_speech_threshold` / `log_prob_threshold` in `voice.py:764-765` (carried from session 41).
6. Phase 9 RDP test (pending since session 35).
7. Phase 16 license-system decisions — still blocked on Alex's product calls (subscription vs. one-time, offline activation, tier count).
8. Home-PC smoke test of public 4.3.0 / 4.3.1 installer (carried from session 41).

## Files Changed

None tracked. Only memory writes at `~/.claude/projects/C--Users-alex-Projects-koda/memory/` (outside the git tree):

- `project_dash_word_dropout.md` (new)
- `MEMORY.md` (index entry appended)

## Key Reminders

- **Do not propose `initial_prompt` biasing as the fix for the dash-dropout bug.** Alex rejected it verbatim on 2026-04-21. Memory entry `project_dash_word_dropout.md` documents the rejection.
- **Whisper drops the literal word "dash"** on the `small` model — confirmed field bug, not a Koda post-processing issue. `code_vocabulary` is `False` in default mode (`voice.py:843`), so `text_processing.CODE_VOCAB["dash"] → "-"` does not fire; `format_smart_punctuation` only rewrites `"dash dash"`, not single `"dash"`; `"dash"` is not in `DEFAULT_FILLER_WORDS`.
- **Session 41 handover was stale on PR #25 state** — it claimed PR #25 was open awaiting merge, but PR #25 had merged as `25bcc94` on 2026-04-20T22:35:19Z. If a future handover seems to contradict remote reality, trust `gh pr view` over the doc.
- **Work-PC rule holds:** all changes to `Moonhawk80/koda` go through PRs. No direct pushes to master.
- **Koda does not use `.claude/next.md`** — the global rule now points every project at that pattern, but koda was not migrated this session. Run `/forge-checklist` when Alex is ready to adopt it.

## Migration Status

N/A — no DB, no schema changes this session.

## Test Status

Not run this session. Last known state: 96 tests passing (per session 41 handover, unchanged since no source edits occurred).

## Final State

- Local: clean working tree, master at `25bcc94`.
- Remote: same; PR #24 open, all others either merged or closed.
- Memory: synced.
- Handover: this file.

---

## New Session Prompt

```
cd C:\Users\alex\Projects\koda

Continue from work-PC session 42 handover (docs/sessions/alex-session-42-work-pc-handover.md).

## What we were working on
Short diagnostic session. Real field bug: Whisper drops the literal word "dash" in dictation (e.g. "language dash font" → "language font"). Traced root cause to the ASR layer, not Koda's post-processing. Proposed `initial_prompt` biasing as the fix; Alex rejected it explicitly ("i don't like the initial prompt bullshit rule") and wants a deterministic mechanism instead. Decision parked, memory saved, no code changed.

## Next up
1. Alex picks a direction for the dash-dropout fix — read `~/.claude/projects/C--Users-alex-Projects-koda/memory/project_dash_word_dropout.md` first to avoid re-proposing the rejected `initial_prompt` approach. Open options: `suppress_tokens` (deterministic but regresses compounds), upgrade default model, `word_timestamps` + gap detection, or a combined literal-words config.
2. Merge PR #24 (session 41 handover) — open, mergeable, no checks required.
3. Open a new PR for this session 42 handover doc after Alex reviews it (work-PC rule: no direct pushes to master).
4. Re-share v4.3.1 installer with the coworker and confirm mic-hotplug recovery works end-to-end.
5. Music-bleed follow-up if `noise_reduction` toggle doesn't resolve Whisper hallucinations during background music — tighten `no_speech_threshold` / `log_prob_threshold` in `voice.py:764-765`.

## Key context
- Master at `25bcc94`, working tree clean. PR #25 (Node 24 CI bump) already merged 2026-04-20 despite session 41 handover claiming otherwise.
- PR #24 still open (session 41 handover doc).
- Koda does NOT have `.claude/next.md` yet — global rule says every project should. Run `/forge-checklist` when Alex is ready to adopt.
- Carried from session 41: Phase 9 RDP test, Phase 16 license decisions, home-PC smoke test of public 4.3.0/4.3.1 installer.
```

Copy the block above into a new session to pick up where we left off.
