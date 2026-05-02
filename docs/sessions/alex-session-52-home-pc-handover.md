---
session: 52
date: 2026-05-02
scope: koda
resumes-from: alex-session-51-home-pc-handover.md
continues-work-from: null
projects-touched: [koda]
skills-activated: [forge-resume, brainstorming, writing-plans, forge-deslop, forge-review, forge-handover]
---

# Home-PC Session 52 Handover — 2026-05-02

Saturday afternoon, home PC (Alexi user). Picked up after PRs #35 + #36
landed earlier that morning. Started with `/forge-resume` to get oriented,
then pivoted into a major architecture build off the back of the Whisper
speed-gap research from session 51.

The session shipped 2 of 4 phases of a brand new hardware tier system —
the install-time classifier that determines a PC's tier (BLOCKED /
MINIMUM / RECOMMENDED / POWER) and applies tier-appropriate config
defaults. Both PRs (#37, #38) merged to master in this session; Phases
3 and 4 deferred to future sessions.

Sub-plot: the system_check.classify() output revealed a stale CLAUDE.md
note — home PC actually has an NVIDIA RTX 4060 Laptop GPU with usable
CUDA, not "Intel UHD 770 only" as the project doc claims. Power Mode has
been available on this machine all along; Koda has just been running
CPU-only because nothing was checking.

## Branch
`master` at `cf6f780` (post-merge of PR #38). Working tree dirty:
`M config.json` (carried local state per session 45 rule, intentionally
NOT committed) + `?? dev_test_overlay.py` (decision deferred from
session 47 — still pending).

## TL;DR

1. **Whisper speed-gap pivot** — session 51 research recommended Lever #1
   (Groq cloud backend) as the only lever that closes the gap to Wispr
   Flow. Alex killed it: privacy ("local-only is a brand promise") +
   cost ("we don't want recurring fees"). Streaming would compete with
   Claude Code for CPU. Cpu_threads A/B was 5-min free data. Pivoted to
   a deeper question: should the installer have minimum-system-
   requirement checks?
2. **Hardware tier system designed** — full forge-brainstorm walked Q1
   through Q6, locked: soft-warn + auto-tune below recommended (not
   hard-gate); 4-tier shape (BLOCKED / MINIMUM / RECOMMENDED / POWER)
   absorbing the existing GPU/Power Mode flow into the same system;
   AI-generated Atlas Navy installer banner + composited K-mark +
   in-app status indicators (no first-launch splash); moderate
   thresholds (4-core / 8GB RAM as RECOMMENDED floor); single
   RECOMMENDED defaults (no sub-tiering by core count); layered settings
   GUI override (tier dropdown + Advanced expander + honest status
   line).
3. **Spec written** — 12 sections, 408 lines:
   `docs/specs/2026-05-02-hardware-tier-system-design.md` (commit
   `c50fbff`).
4. **Plan written** — 24 tasks across 4 phases, bite-sized steps with
   full code blocks: `docs/plans/2026-05-02-hardware-tier-system.md`
   (commit `a4dacdd`).
5. **Phase 1 shipped** — Python classifier + tests + configure.py wiring
   + settings GUI Performance section. 9 commits on
   `feat/hardware-tier-system-phase-1`. PR #37 merged at
   2026-05-02 20:35 UTC. Tests 432 → 447 (+15 new).
6. **Phase 2 shipped** — Inno installer integration: Pascal classifier
   mirror, build-time codegen for shared thresholds, BLOCKED + MINIMUM
   wizard pages, `--detect-hardware --json` CLI flag on Koda.exe,
   ssPostInstall tier-aware config write. 7 commits on
   `feat/hardware-tier-system-phase-2`. PR #38 merged at
   2026-05-02 20:36 UTC. Tests 447 → 448 (+1 drift-guard).
7. **Real-machine finding** — `Koda.exe --detect-hardware --json` ran on
   home PC, returned: i7-13650HX / 20 cores / 15.7GB RAM / NVIDIA RTX
   4060 Laptop GPU / CUDA usable / **POWER tier**. CLAUDE.md's "Intel
   UHD 770 only" note is STALE.
8. **Workflow confirmation** — used Claude's Agent tool for fresh-
   subagent-per-task dispatch (no superpowers plugin in loadout).
   Worked cleanly across 14 task dispatches. Subagents caught real
   issues: a duplicate Performance section in settings_gui that
   forge-deslop flagged in Task 8; a logic bug in the drift-guard test
   from Task 9 that forge-deslop caught in Task 14; a half-dozen
   PascalScript dialect restrictions the spec didn't anticipate.

## What Was Built This Session

### A. Brainstorm — locked tier system shape (Q1-Q6)

Started by deep-reasoning whether the speed-gap research path was even
right, given Alex's local-only product promise. Concluded:

- Lever #1 (Groq cloud) is **dead** — violates local-only brand promise,
  introduces recurring cost, requires per-user API key onboarding for
  the coworker.
- Streaming (research's Lever #c) was tempting BUT would create
  sustained CPU load during recording (vs. current spike at hotkey
  release), which is exactly the load pattern that triggered the
  coworker complaint in session 49. Trades one problem for another.
- Lever #2 (cpu_threads A/B) is NOT actually blocked — `transcribe_file.py`
  exists; benchmark could run offline against a recorded WAV, no mic
  flow needed.
- Lever #3 (Speed mode small→tiny per mode) is a tactical band-aid
  that doesn't solve the long-form prompt-assist case (LLM amplifies
  misheard tiny-model words).

This is when Alex asked: "for people with older PCs or slower
processors does the installer check for compatibility and adjusts the
install accordingly?" — and the conversation pivoted from "pick a speed
lever" to "build install-time hardware tier system."

The 6 brainstorm questions and locks:

- **Q1 — User-facing behavior below recommended specs:** B (soft-warn +
  auto-tune; hard-block reserved for truly-can't-run).
- **Q2 — Power Mode integration:** A (absorb GPU/Power Mode into a
  unified 4-tier system rather than keeping it as a separate
  configure.py-only flow).
- **Q3 — Graphical celebration approach:** D (installer banner +
  in-app status indicators, AI-generated Atlas Navy background. NO
  first-launch splash — Alex's verbatim: "the user doesnt open it
  until tomorrow and then the flag makes it look dumb and cheap").
- **Q4 — Tier thresholds:** B (moderate — 4-core / 8GB RAM floor for
  RECOMMENDED).
- **Q5 — Per-tier defaults:** "single RECOMMENDED defaults + full
  force-write for MINIMUM" (originally labeled α + γ, switched to plain
  English after Alex flagged "I dont know that symbol").
- **Q6 — Settings GUI override surface:** Option 3 (layered — tier
  dropdown + Advanced expander + honest status line).

Total brainstorm length: 6 questions, ~20 message exchanges. Skill
ran successfully without scope creep — kept locked decisions out of
implementation territory.

### B. Spec written and committed

`docs/specs/2026-05-02-hardware-tier-system-design.md` (commit `c50fbff`,
408 lines, 12 sections):

1. Goals & Non-Goals (with explicit non-goals to prevent scope creep)
2. The Four Tiers (definitions, thresholds, defaults, user-facing
   behavior per tier)
3. Detection Signals (table of what's detected and where — Pascal
   side vs Python side)
4. Architecture (module layout, system_check.py interface, install-
   time + runtime data flow)
5. Power Mode Celebration (banner pipeline, AI prompt baked in for
   reproducibility, in-app indicators spec)
6. Settings GUI Override (layered control wireframe, behavior rules)
7. Re-detection Policy (table of every event and its behavior)
8. Backward Compatibility (existing v4.4.0-beta1 install handling)
9. Testing Strategy (unit tests + manual three-machine cross-check)
10. Out of Scope
11. Open Questions (none — all locked in brainstorm)
12. Implementation Phasing (4 independently-shippable phases)

Self-review caught and fixed two ambiguities inline: the constants-
sharing approach was originally vague ("(or equivalent)"), changed to
a concrete build-time codegen pipeline; the Inno-side JSON parsing
needed explicit treatment because Pascal `Exec` doesn't capture
stdout (must redirect to a temp file then `LoadStringFromFile`).

### C. Plan written and committed

`docs/plans/2026-05-02-hardware-tier-system.md` (commit `a4dacdd`,
~2500 lines, 24 tasks):

- File map (new files + modified files with exact paths)
- Phase 1: 8 tasks (constants → BLOCKED → MINIMUM/RECOMMENDED → POWER
  → fallback/CLI → configure.py wire → settings GUI → pre-push gate)
- Phase 2: 6 tasks (codegen → Pascal classifier → koda.iss tier pages
  → CLI flag → ssPostInstall → pre-push gate)
- Phase 3: 6 tasks (AI banner gen → composite script → wizard page →
  audio cue → in-app indicators → tray balloon → pre-push gate)
- Phase 4: 4 tasks (backward-compat → re-detection → multi-machine
  validation → final gate)

Each task has bite-sized steps (2-5 min each), full code blocks where
critical, and exact verification commands. No placeholders.

### D. Phase 1 build (8 tasks, 9 commits, PR #37 merged)

Branch: `feat/hardware-tier-system-phase-1` (off master).

**Commits in merge order:**

- `0738daa` — `system_check_constants.py`: shared threshold constants
  (RAM/disk/Win-build minimums, CORES_MIN_RECOMMENDED, RAM_MIN_GB,
  CPU_LOW_POWER_PATTERNS tuple of 13 substring patterns,
  TIER_DEFAULTS dict per tier).
- `404e8ce` — `system_check.py` (245 lines): Win32 + winreg detection
  helpers, `classify()` returning `{tier, reasons, hardware, defaults}`,
  `_main()` CLI entry. Plus `TestSystemCheckBlocked` × 3 tests.
- `b0f6c1a` — `TestSystemCheckMinimum` × 8 tests (low cores, low RAM,
  Atom/Celeron/N100 patterns, RECOMMENDED baseline, false-positive
  guards including Pentium Gold tripping correctly + Xeon NOT tripping).
- `398d524` — `TestSystemCheckPower` × 2 tests (NVIDIA + CUDA → POWER;
  NVIDIA + no-CUDA → RECOMMENDED fallback so configure.py Bucket-B
  can offer auto-install).
- `a590ee9` — `TestSystemCheckFallback` (detection error → MINIMUM,
  never blocks user) + `TestSystemCheckCli` (--json CLI mode emits
  parseable JSON).
- `60f2cf3` — `configure.py` `setup_performance` refactored to
  dispatch via `system_check.classify()`. Bucket-B (NVIDIA + no-CUDA
  auto-install offer) extracted into `_offer_cuda_install` helper.
- `d625d79` — `settings_gui.py` Performance section: tier dropdown,
  Advanced expander (model size / cpu threads / process priority),
  honest status line. ~150 LOC.
- `092da7a` — forge-deslop H1: removed duplicate Performance section
  + 4 orphan handlers (`_check_gpu`, `_enable_power_mode`,
  `_disable_power_mode`, `_open_cuda_url`) + `_perf_status_var`.
- `8e6b006` — forge-deslop H2: removed dead `webbrowser` import,
  `CUDA_DOWNLOAD_URL`, `_save_power_mode_instructions` from
  configure.py.

Pre-push gate: forge-deslop 3 HIGH (all applied), forge-review 0
BLOCKING / 0 NEEDS-FIX / 2 NIT (deferred). Tests 432 → 447 (+15).

PR #37 merged 2026-05-02 20:35 UTC.

### E. Phase 2 build (6 tasks, 7 commits, PR #38 merged)

Branch: `feat/hardware-tier-system-phase-2` (off Phase 1 tip; PR base
re-targeted to master before Phase 1 merge so PRs stacked cleanly).

**Commits in merge order:**

- `442d68a` — `installer/build_thresholds_iss.py` codegen +
  generated `installer/thresholds.iss` (Pascal `#define` block +
  pipe-delimited CPU pattern string for the dialect-restricted Pascal
  side) + `TestThresholdsIssUpToDate` drift-guard test.
- `637a735` — `installer/system_check.iss` (Pascal classifier mirror,
  164 lines): Win32 imports (GlobalMemoryStatusEx),
  `TMemoryStatusEx` record, 6 detection helpers + `IsLowPowerCpu` +
  `ClassifyTier`. Designed to be `#include`d inside koda.iss `[Code]`.
- `1fc8e33` — `installer/koda.iss` modifications: `#include`s for the
  new files, BLOCKED hard-stop wizard page, MINIMUM soft-warn page,
  `ShouldSkipPage` and `NextButtonClick` to halt at BLOCKED. **Six**
  PascalScript-dialect fixes required to make ISCC compile (see Dead
  Ends + Decisions).
- `7219b74` — `voice.py` `--detect-hardware --json` CLI flag at the
  top of `main()`. Used by the Inno installer at ssPostInstall.
- `829b032` — `installer/koda.iss` CurStepChanged rewrite: post-
  extract `Koda.exe --detect-hardware --json` redirected to temp
  file, parsed via minimal `ExtractTierFromJson` Pascal helper,
  written via `BuildTierAwareConfigJson`. Tier overrides user's
  wizard pick for POWER (force `large-v3-turbo`) and MINIMUM (force
  `tiny`); RECOMMENDED honors the wizard pick.
- `34c8c7c` — forge-deslop H1: rewrote the drift-guard test from
  Task 9 — original implementation read the file twice but never
  asserted non-drift. Verified by injecting artificial drift.
- `ba173cd` — forge-deslop M1: added `Log()` calls for non-zero exit
  and missing-exe cases on the Koda.exe --detect-hardware Exec call.
  SetupLogging=yes was already on.

Pre-push gate: forge-deslop 1 HIGH + 1 MEDIUM (both applied),
forge-review 0 BLOCKING / 0 NEEDS-FIX / 2 NIT (deferred). Tests 447
→ 448 (+1 drift-guard).

PR #38 merged 2026-05-02 20:36 UTC.

### F. Subagent-driven execution workflow

Used Claude's built-in Agent tool for fresh-subagent-per-task
dispatch (the canonical `superpowers:subagent-driven-development`
skill is not installed in Alex's loadout, so the pattern was done
manually). Workflow per task:

1. TaskUpdate the in_progress task tracker.
2. Agent dispatch with a self-contained prompt: read these files,
   follow plan task N, run these verification commands, commit with
   the plan's exact message, report back under N words.
3. Subagent returns a tight summary.
4. Quick verify (commit SHA, test count, file size).
5. TaskUpdate to completed with metadata.
6. Move to next task.

Worked cleanly across 14 dispatches (8 Phase 1 + 6 Phase 2). Subagents
caught real issues the conversation didn't anticipate: duplicate
Performance section on the Advanced tab, drift-guard test logic bug,
PascalScript dialect restrictions. The two-stage review pattern
(forge-deslop + forge-review) inside Task 8 and Task 14 hardened
both PRs before push.

## Decisions Made

### Memory: don't kill local-only privacy promise for cloud speed

Alex's verbatim: "well we dont want to pay more and we dont want one of
the selling points that their data is only local we cant kill that."
This single message killed Lever #1 (Groq cloud backend) entirely as a
direction. Local-only is a load-bearing brand promise — even opt-in
cloud breaks the pitch ("your data only leaves the machine if you flip
this toggle" is materially worse than "your data never leaves the
machine"). Documented in `feedback_avoid_ai_color_fingerprints.md`'s
sibling slot — actually documented in next.md and this handover only;
not memory-worthy on its own (already implicit in CLAUDE.md product
positioning).

### Streaming would compete with Claude Code for CPU

Considered streaming (research's Lever #c) as the privacy-preserving
answer. Rejected after Alex asked: "will it slow down the cpu for
people using claude code?" Yes. Streaming runs Whisper inference
continuously during recording — re-transcribing growing audio windows
every few seconds. Total compute is HIGHER than batched, distributed
across the whole recording window instead of one spike at hotkey
release. Coworker session 49 complaint was exactly this load pattern
(Koda taking too much CPU during heavy parallel work). Streaming
trades the spike-at-end problem for a sustained-load problem.

Lesson: the perceived-speed win from streaming isn't free on shared-CPU
boxes. Don't propose it for users who run Koda alongside heavy IDE/AI
workloads (which is most of Koda's actual user base, including the
coworker and Alex himself).

### Build a hardware tier system instead of picking a speed lever

After speed levers got rejected one by one, Alex asked "for people with
older PCs or slower processors does the installer check for
compatibility and adjusts the install accordingly?" That reframed the
whole problem. The answer was NO — installer hardcodes
`above_normal` priority, `cpu_threads=4`, `model_size=small`
regardless of hardware. Coworker complaint was exactly this — slow PC
got aggressive defaults, performed badly.

Decision: build a 4-tier classifier (BLOCKED / MINIMUM / RECOMMENDED /
POWER) that detects hardware at install time and applies tier-
appropriate defaults. Subsumes:

- Lever #3 (Speed mode small→tiny) — becomes the MINIMUM tier auto-tune
  + a settings GUI Advanced expander override.
- "Port v2 pickers to Inno Setup installer" (`.claude/next.md` item)
  — `system_check.py` becomes the shared module both wizards
  (configure.py + Inno installer) call.
- "Auto-detect" of GPU and Power Mode — POWER tier integration.
- Future paid-product readiness (Phase 16 licensing) — refund risk
  from slow-PC users mitigated by upfront soft-warn.

### Soft-warn over hard-gate (Q1 lock — option B)

Hard gates either block users whose machines actually work fine, or
let through machines that'll deliver a bad first impression. Soft warn
+ auto-tune to slowest tier defaults sets honest expectations without
losing installs. Reserved hard-block (option A) only for truly-can't-
run cases (32-bit, Win 7, <2GB RAM, <4GB free disk) — the correctness
floor.

### Absorb GPU/Power Mode into the same tier system (Q2 lock — option A)

Existing `hardware.py:detect_gpu()` flow is only called from
`configure.py`. Inno installer never invokes it. End users from the
.exe installer have been silently missing Power Mode entirely, even on
NVIDIA hardware. Absorbing makes one classifier the single source of
truth, reaches both wizards, and gives the settings GUI override one
clean surface.

Cost: more Pascal in koda.iss `[Code]` for GPU detection + auto-CUDA-
install offer. Bounded — translation of existing logic, not new logic.

### Power Mode celebration: installer banner + in-app indicators, NO first-launch splash (Q3 lock — option D)

Alex's verbatim rejection of the alternative I'd initially proposed:
"wait I hate what you said before the questions the user doesnt open
it until tomorrow and then the flag makes it look dumb and cheap."

A first-launch splash that fires hours/days after install feels
manufactured and reads as cheap shovelware. Real options are:

- A) installer wizard banner (in-moment but Inno can't render Atlas
  Navy fonts/animation properly)
- B) first-launch splash (rejected — see above)
- C) earned celebration on first real Power Mode transcription (clever
  but a notification has its own UX risk)
- **D) installer banner + persistent in-app indicators** (the lock —
  static AI-generated banner in Inno where the moment is contextually
  right, plus quality indicators in-app so the user always knows
  Power Mode is active)

The bitmap pipeline is AI-generated background only (gen tools are
bad at text/logos), composited K-mark from existing `koda.ico`,
text rendered by Inno's native chrome. Canonical AI prompt baked into
`installer/build_power_banner.py` for reproducibility. (Phase 3 — not
shipped yet.)

### Tier thresholds — moderate (Q4 lock — option B)

- BLOCKED: <2GB RAM, <4GB free disk, Win build <19041
- MINIMUM: <4 cores OR <8GB RAM OR low-power CPU class
- RECOMMENDED: 4+ cores AND 8+ GB RAM AND no NVIDIA
- POWER: any NVIDIA GPU + CUDA usable

Calibration anchor: Alex's home PC validated to work fine with current
defaults. Coworker's complaint pattern was a low-power class machine
that would now land in MINIMUM and auto-tune correctly. 4-core/8GB is
the natural Windows 11 floor — gating below as "below recommended" is
honest without being snobby.

Honest wobble named: coworker complaints have been workload-dependent
(competition with 20 Claude Code sessions), not pure-hardware-
dependent. Tier system gives him decent defaults; settings GUI override
is the surface for per-machine tuning. Don't over-engineer
contention detection into classification.

### Single RECOMMENDED defaults + full force-write for MINIMUM (Q5 lock)

Originally labeled "α + γ" — Alex pushed back on Greek symbols ("I
dont know that symbol"). Switched to plain English. Captured as a
durable preference in memory (`feedback_plain_english_options.md`).

The lock:
- RECOMMENDED tier keeps current defaults (model_size=small,
  cpu_threads=4, process_priority=above_normal). No sub-tiering by
  core count for v1 — that's a Lever #2 cpu_threads benchmark
  question, deferred.
- MINIMUM tier force-writes all three (model_size=tiny, cpu_threads=2,
  process_priority=normal) so slow PCs get a coherent slow-PC config,
  not a half-tuned one. Settings GUI override always available.

### Settings GUI override — layered (Q6 lock — option 3)

Tier dropdown (primary surface) + Advanced expander (per-value
controls for power users) + honest status line above ("Currently:
Auto-detect → Recommended. Your hardware: 12 cores, 32 GB RAM, no
NVIDIA GPU."). Touching an Advanced control auto-flips mode to
"Custom" — appears as a 5th dropdown option that only shows once
the user has done so.

### PRs stack — Phase 2 base re-targeted before Phase 1 merge

Phase 2 imports from Phase 1 (system_check.py, system_check_constants.py),
so the branch was created off Phase 1's tip. PR #38's base was
re-targeted from `feat/hardware-tier-system-phase-1` to `master`
*before* PR #37 merged so neither would orphan. Order: re-target →
merge #37 (delete branch) → merge #38 (delete branch). Worked cleanly.

### Subagent dispatch over inline execution

Plan offered two execution paths. Alex picked subagent-driven. The
canonical `superpowers:subagent-driven-development` skill is not in
Alex's loadout — used Claude's built-in Agent tool to do the same
pattern manually. Each task got a fresh subagent with a self-contained
prompt referencing the plan task spec, file paths, and verification
steps. Worked smoothly across 14 dispatches.

### Merged with line-ending noise

`installer/thresholds.iss` showed up as modified in working tree post-
build with empty diff (LF/CRLF normalization noise from autocrlf
config). Caused gh's local-merge-step checkout to fail. Resolved with
`git checkout -- installer/thresholds.iss` then re-ran `gh pr merge
38` — second invocation reported "already merged" because the merge
had succeeded on GitHub's side; local just needed to fast-forward.

## User Feedback & Corrections

### "well we dont want to pay more and we dont want one of the selling points that their data is only local we cant kill that"

The single most decision-shaping message of the session. Killed Lever
#1 (Groq cloud backend) entirely. Reframed the work from "pick a
speed lever" toward something that respects local-only as a
non-negotiable.

### "and what is point 2"

When I'd numbered the path 1, 2, 3 for Lever #1 + Lever #2 + Lever #3,
Alex asked for clarification on point 2. He hadn't tracked the lever
numbers; needed them in plain prose. Lesson: don't assume number
references survive across messages — restate the actual lever name.

### "like we should have minimum system requirement checks right?"

The pivot question. Triggered the whole hardware tier system arc.

### "yes run the brainstorm I am excited for this build lets goooo but do reason this make sure we are making the rght move I think you did already"

Authorization to invoke brainstorming skill, with an explicit ask:
pressure-test the path before launching. Pattern: Alex wants the
reasoning visible BEFORE the skill kicks off, not as a post-hoc
justification. Captured in handover; useful as durable feedback
("Always pressure-test the path before invoking a major skill,
especially when excitement is on the table").

### "B"

Q1 lock. One letter. Confidence in the framing.

### "I like A but I would love for it to do a grapghical part of it as well is that not possible?"

Q2 lock + Q3 setup. He wanted A (absorb GPU into tier system) AND he
wanted a graphical celebration moment, not just text. This led to the
exploration of what's actually possible in Inno Setup graphically.

### "wait I hate what you said before the questiosn the user doesnt open it until tomorrow and then the flag makes it look dumb and cheap"

Killed Q3 option B (first-launch splash) verbatim. Reframed Q3
toward installer-banner + persistent in-app indicators (option D).

### "D but I am not designing shit so we need to find a happy medium that we can use AI to design lol like gemini stich or chatgpt image generator with right prompt"

Locked Q3 option D AND constrained the design pipeline to AI-only
generation (no manual Photoshop/Figma work). Drove the spec's §5.1
section: AI generates background only, K-mark composited from existing
`koda.ico`, text rendered by Inno chrome (gen tools are unreliable at
text). Canonical prompt baked into `build_power_banner.py` docstring.

### "I dont know that symbol"

After I'd labeled options as α + γ. Alex pushed back. Captured as
durable feedback (`feedback_plain_english_options.md`): no Greek in
multiple-choice option labels — plain numbers (1/2/3) or Latin letters
(A/B/C/D).

### "jesus how many more questions"

Brainstorm impatience signal. Honest response: one more question (Q6)
and that was it — rest goes into the spec for review. The skill's
section-by-section approval flow was overkill for this user; he
preferred to review the doc as a whole.

### "do you need supapowers skills to do this?"

Mid-execution check on tooling. Honest answer: no, Agent tool does the
same thing. The dispatched-subagent pattern was working fine without
the canonical skill installed.

### "do phase to"

Authorization to start Phase 2 immediately after Phase 1 PR shipped.
Implicit confidence check that Phase 1 was solid before stacking.

### "b do the push as we are at home pc and I approve it and then commit and handover skill"

Session-end authorization. Translation: merge both PRs (since they're
already pushed and reviewed via the pre-push gates), commit any final
state, run forge-handover. Ambiguity around "push" vs "merge" resolved
by treating the merge as the explicit ship action, given his "I
approve it" clearly applied to both PRs.

## Dead Ends Explored

### Lever #1 — Groq cloud backend (`whisper-large-v3-turbo`)

Considered as the headline answer to closing the speed gap to Wispr
Flow. 216× real-time vs current 5-10×. Free tier covers personal
dictation volume. Rejected: violates Koda's local-only brand promise,
introduces recurring cost story (Groq pricing isn't ours to control),
adds per-user API key onboarding friction for the coworker. Killed
verbatim by Alex. Not revisitable in current product positioning.

### Streaming via `whisper_streaming` lib (Lever #c from research)

Considered as the privacy-preserving, no-recurring-cost alternative
to Groq. 3-5× perceived speedup on long clips by transcribing during
recording. Rejected: total CPU compute is HIGHER than batched
(overlapping window re-transcription is more work, not less), and
the load is sustained throughout the recording window — exactly when
the user is presumably still typing in Claude Code. Coworker session
49 complaint was this load pattern. Trades the spike-at-end problem
for a sustained-load problem.

### Hard-gate install for sub-recommended hardware (Q1 option A)

Considered as the simplest "minimum requirements check" interpretation.
Rejected — false-negative gating loses users whose machines actually
work fine. Soft-warn + auto-tune (option B) preserves install base
while setting honest expectations.

### Keep Power Mode separate from tier system (Q2 option B)

Considered as the lower-effort path. Rejected — Inno installer would
keep silently missing the Power Mode upgrade, and the settings GUI
would have two surfaces (CPU performance + separate Power Mode toggle).
Absorbing into one classifier is the right product shape.

### First-launch splash (Q3 option B)

Considered as the way to get a real animated Atlas Navy moment (the
overlay's existing fade-in + K-mark dot animation infrastructure is
in Tk, not Inno). Rejected by Alex verbatim — feels manufactured if
the user installs at 3pm and opens at noon the next day.

### Earned celebration on first real Power Mode transcription (Q3 option C)

Considered as the cleverest option — celebration tied to demonstrated
value instead of a startup popup. Rejected as over-engineering vs.
the straightforward installer-banner + persistent indicator pattern
in option D.

### Bundling Hubot Sans + JetBrains Mono in installer

Considered (carried from session 47) as the way to lock type identity
across all Windows versions. Deferred — Win 11 fallbacks (Segoe UI
Variable Display + Cascadia Mono) are visually approved, bundling
adds installer complexity for marginal gain.

### Inno animation via timer-driven bitmap swaps

Considered as a way to get animation in the Power Mode wizard page.
Rejected as janky — Inno's animation tooling is primitive. Atlas Navy
deserves the Tk-side polish, not a near-miss in Inno. Lock D's
in-app indicators carry the animation responsibility.

### cpu_threads sub-tiering inside RECOMMENDED (Q5 option β)

Considered as a "tune defaults to hardware headroom" extension. Tabled
— requires the cpu_threads benchmark from session 51's research
(Lever #2), which is offline-runnable via `transcribe_file.py` but
hasn't been done. Single RECOMMENDED defaults until benchmark data
exists.

### `superpowers:subagent-driven-development` skill

Brainstorming + writing-plans skills both reference this canonical
implementation skill. Not in Alex's installed loadout. Used Claude's
built-in Agent tool to do the same pattern manually — works equally
well, just one extra translation step from the skill's prescriptive
flow to the Agent tool's invocation.

## Skills Activated This Session

| Skill | Ask | Outcome | Report path |
|---|---|---|---|
| forge-resume | session-start orientation | Read session 51 handover, confirmed master clean, found 2 PRs from session 47 (#35 + #36) had merged that morning. Recommended next: tag v4.4.0-beta1 OR pursue speed-gap research. | n/a |
| brainstorming | "yes run the brainstorm I am excited for this build" | 6-question structured walk + spec doc at `docs/specs/2026-05-02-hardware-tier-system-design.md` (commit `c50fbff`). All 6 design decisions locked. | n/a (spec is the artifact) |
| writing-plans | post-spec hand-off | 24-task plan at `docs/plans/2026-05-02-hardware-tier-system.md` (commit `a4dacdd`). Bite-sized steps, full code blocks, no placeholders. Self-review caught 0 issues post-write. | n/a (plan is the artifact) |
| forge-deslop (Phase 1) | pre-push gate task 8 | 3 HIGH findings, all applied. H1+H2: duplicate Performance section + 4 orphan handlers in settings_gui.py. H3: dead webbrowser import + CUDA_DOWNLOAD_URL + _save_power_mode_instructions in configure.py. | (subagent-internal) |
| forge-review (Phase 1) | pre-push gate task 8 | 0 BLOCKING / 0 NEEDS-FIX / 2 NIT (deferred). All 6 layers pass. | (subagent-internal) |
| forge-deslop (Phase 2) | pre-push gate task 14 | 1 HIGH + 1 MEDIUM, both applied. H1: drift-guard test had a logic bug — read file twice, never asserted non-drift. M1: Exec failure on --detect-hardware wasn't logged. | (subagent-internal) |
| forge-review (Phase 2) | pre-push gate task 14 | 0 BLOCKING / 0 NEEDS-FIX / 2 NIT (deferred). | (subagent-internal) |
| forge-handover | session wrap-up (this) | This handover + next.md sync + 4 memory entries. | (this file) |

No forge-test, forge-clean, forge-migrate, forge-organize, forge-secrets,
forge-checklist, update-config this session.

## Memory Updates

Memory directory: `~/.claude/projects/C--Users-alexi/memory/`

**CREATED:**

- `feedback_pascalscript_restrictions.md` — Inno Setup's Pascal Script
  is a restricted dialect. Plan-Pascal that compiles in full Object
  Pascal often fails ISCC. Specific traps: typed array constants
  (use pipe-delimited string + parse at runtime instead), case
  statements with String selectors (use if/elseif chains), `MaxInt`
  is not a builtin (use a literal big number), `LoadStringFromFile`
  requires `AnsiString` not `String`, no forward type references
  (declare `type` blocks before they're used), `TSystemInfo` is not
  a built-in PascalScript type (declare locally + use
  `GetNativeSystemInfo`). Plan multi-attempt iteration via ISCC
  compile errors when writing Pascal for koda.iss.

- `feedback_plain_english_options.md` — Don't use Greek letters (α, β,
  γ, δ) in multiple-choice option labels. Use plain numbers (1/2/3)
  or Latin letters (A/B/C/D). User flagged "I dont know that symbol"
  during the brainstorm — visual confusion penalty outweighs any
  taxonomic clarity gain. Applies to all future skill prompts and
  chat-based design questions.

- `project_home_pc_hardware.md` — Home PC actual specs (detected via
  `Koda.exe --detect-hardware --json` session 52): 13th Gen Intel
  Core i7-13650HX, 20 logical cores, 15.7 GB RAM, NVIDIA GeForce RTX
  4060 Laptop GPU, CUDA runtime usable. POWER tier eligible. The
  CLAUDE.md note "No NVIDIA GPU — Intel UHD 770 only. CUDA not
  available." is STALE and pending update. Whisper has been running
  CPU-only on this machine despite Power Mode being available the
  whole time.

- `project_hardware_tier_system.md` — Major install-time hardware
  classifier system. 4 tiers (BLOCKED / MINIMUM / RECOMMENDED /
  POWER). Phases 1+2 shipped session 52 (PRs #37 + #38 merged to
  master at cf6f780). Phases 3+4 pending. Spec:
  `docs/specs/2026-05-02-hardware-tier-system-design.md`. Plan:
  `docs/plans/2026-05-02-hardware-tier-system.md`. Phase 3 is the
  Power Mode celebration UX (AI-generated Atlas Navy banner, PIL
  composite with K-mark, custom wizard page, audio cue, in-app
  indicators including tray tooltip suffix and settings badge,
  one-time GPU-appeared tray balloon). Phase 4 is backward-compat
  for existing v4.4.0-beta1 installs (detection without overwrite)
  + re-detection on every Koda startup + multi-machine validation
  (slow PC / recommended / power / blocked). Each phase
  independently shippable.

**UPDATED:** `MEMORY.md` index — appended 4 new entries.

No deletions. No memory entries pre-existed for any of the new content
(grep'd `MEMORY.md` first to avoid duplicates).

## Waiting On

- **Phase 3 + Phase 4 of hardware tier system** — pending future
  session. 10 tasks remaining.
- **CLAUDE.md hardware note update** — currently lists "Intel UHD 770
  only / CUDA not available", actually has RTX 4060 Laptop + CUDA
  usable. Alex's call when to update (it's a project-truth
  statement).
- **Live mic test of master overlay v2** — carried from sessions 47/51,
  still pending. Required for tagging v4.4.0-beta1.
- **`koda.iss` friction-free upgrade hardening** — `CloseApplications`,
  `RestartApplications`, `AppMutex` (carried from session 51).
- **Decide `dev_test_overlay.py` fate** — still untracked at project
  root, decision deferred from session 47.
- **Inno installer v2 setup pickers port** — SUBSUMED by hardware tier
  system. system_check is the shared module. Mark complete next.md.
- **v4.4.0-beta1 tag** — depends on live mic test.
- **Coworker re-test of v4.3.1 mic-hotplug + music-bleed** — carried
  from session 41.
- **Bundle Hubot Sans + JetBrains Mono in installer** — carried from
  session 47.

## Next Session Priorities

Per `.claude/next.md` after this session's check-offs and updates:

1. **Update CLAUDE.md hardware note** — RTX 4060 Laptop + CUDA usable,
   not "Intel UHD 770 only" (this should land first to prevent any
   future session operating on the wrong assumption).
2. **Hardware tier system Phase 3** — Power Mode celebration. AI banner
   gen + K-mark composite + wizard page + audio cue + in-app
   indicators + tray balloon. Plan tasks 15-20.
3. **Hardware tier system Phase 4** — backward-compat + re-detection +
   multi-machine validation. Plan tasks 21-24.
4. **Live mic test of master** — finally validate Atlas Navy overlay
   in real prompt-assist mic flow on home PC's POWER tier hardware.
5. **`koda.iss` friction-free upgrades** — 4-line `[Setup]` change +
   AppMutex. Trivial.
6. **Tag v4.4.0-beta1** after live test.
7. **Decide dev_test_overlay.py fate** — commit / delete / gitignore.
8. **Phase 16 licensing** — blocks paywall wrap.
9. **Azure Trusted Signing** ($10/mo) — wire into build-release.yml.
10. **Whisper "dash" dropout fix** — read `project_dash_word_dropout.md`
    memory first.
11. **Wake word decision** — train custom or rip.

## Files Changed

### Commits merged this session

#### PR #37 (`feat/hardware-tier-system-phase-1` → master)

- `0738daa` feat(system-check): shared tier threshold constants
  - `system_check_constants.py` (NEW, 64 lines)
- `404e8ce` feat(system-check): classify() + BLOCKED tier with tests
  - `system_check.py` (NEW, 245 lines)
  - `test_features.py` (+TestSystemCheckBlocked × 3)
- `b0f6c1a` test(system-check): MINIMUM and RECOMMENDED tier coverage
  - `test_features.py` (+TestSystemCheckMinimum × 8)
- `398d524` test(system-check): POWER tier coverage
  - `test_features.py` (+TestSystemCheckPower × 2)
- `a590ee9` test(system-check): failure fallback + CLI JSON mode
  - `test_features.py` (+TestSystemCheckFallback + TestSystemCheckCli × 2)
- `60f2cf3` refactor(configure): dispatch via system_check.classify()
  - `configure.py` (~100 lines refactored)
- `d625d79` feat(settings-gui): Performance section with tier override
  - `settings_gui.py` (~150 lines added)
- `092da7a` refactor(settings-gui): remove duplicate Performance section
  - `settings_gui.py` (forge-deslop H1)
- `8e6b006` refactor(configure): drop dead webbrowser/CUDA_DOWNLOAD_URL
  - `configure.py` (forge-deslop H2)

#### PR #38 (`feat/hardware-tier-system-phase-2` → master)

- `442d68a` feat(installer): codegen Pascal threshold include from Python
  - `installer/build_thresholds_iss.py` (NEW)
  - `installer/thresholds.iss` (NEW, generated)
  - `test_features.py` (+TestThresholdsIssUpToDate)
- `637a735` feat(installer): Pascal classifier mirrors system_check.classify
  - `installer/system_check.iss` (NEW, 164 lines)
- `1fc8e33` feat(installer): tier-classification wizard pages
  - `installer/koda.iss` (BLOCKED + MINIMUM pages, ShouldSkipPage)
  - 6 PascalScript-dialect fixes applied during ISCC iteration
- `7219b74` feat(voice): --detect-hardware --json CLI flag
  - `voice.py` (~12 lines at top of main())
- `829b032` feat(installer): ssPostInstall writes tier-aware config
  - `installer/koda.iss` (CurStepChanged rewrite + JSON parse helpers)
- `34c8c7c` refactor(forge-deslop): fix drift-guard test logic
  - `test_features.py` (forge-deslop H1)
- `ba173cd` refactor(forge-deslop): log Exec failure on --detect-hardware
  - `installer/koda.iss` (forge-deslop M1)

### Docs commits

- `c50fbff` docs(spec): hardware tier system design
  - `docs/specs/2026-05-02-hardware-tier-system-design.md` (NEW, 408 lines)
- `a4dacdd` docs(plan): hardware tier system implementation plan
  - `docs/plans/2026-05-02-hardware-tier-system.md` (NEW, ~2500 lines)

### Merge commits

- `ea764eb` Merge pull request #37 from Moonhawk80/feat/hardware-tier-system-phase-1
- `cf6f780` Merge pull request #38 from Moonhawk80/feat/hardware-tier-system-phase-2

### Not committed (intentional carries)

- `config.json` — modified pre-session, intentionally NOT committed
  per session 45 rule (carried local state, not authoritative defaults).
- `dev_test_overlay.py` — untracked dev tool, decision deferred from
  session 47. Still pending.

### Memory files (outside git)

5 files in `~/.claude/projects/C--Users-alexi/memory/`:
- `feedback_pascalscript_restrictions.md` (NEW)
- `feedback_plain_english_options.md` (NEW)
- `project_home_pc_hardware.md` (NEW)
- `project_hardware_tier_system.md` (NEW)
- `MEMORY.md` (UPDATE — 4 index entries appended)

### Report files (gitignored via `.forge-*` rules)

- 4 forge-deslop runs (Phase 1 task 8 × 1, Phase 2 task 14 × 1, plus
  the subagent-internal runs during cleanup commits)
- 2 forge-review runs (Phase 1 task 8, Phase 2 task 14)

## Key Reminders

- **Local-only is a brand promise, not a flag.** Do not propose cloud
  backends (Groq, OpenAI, AssemblyAI, etc.) for transcription. Even
  opt-in cloud breaks the pitch. Streaming is OK in principle but has
  real CPU cost during recording — don't propose for users running
  Koda alongside heavy parallel workloads (most of the actual user
  base, including the coworker and Alex).

- **Hardware tier system is now the canonical install-time decision
  surface.** When proposing changes that touch model_size /
  cpu_threads / process_priority defaults, route them through the
  tier classifier or the settings GUI Advanced expander, not by
  hardcoding new defaults in `config.py`. The tiers ARE the defaults.

- **PascalScript dialect restrictions matter.** When writing Pascal
  for `koda.iss [Code]` or `installer/system_check.iss`, plan
  multi-attempt iteration via ISCC compile errors. Don't assume Object
  Pascal features compile (typed array constants, case-on-string,
  MaxInt, forward type refs, etc.). See
  `feedback_pascalscript_restrictions.md`.

- **Plain English over Greek letters in option labels.** No α/β/γ/δ
  in multiple-choice questions. Use 1/2/3 or A/B/C/D. See
  `feedback_plain_english_options.md`.

- **Home PC has RTX 4060 Laptop + CUDA usable.** Not "Intel UHD 770
  only" as CLAUDE.md claims. Until CLAUDE.md is updated, future
  sessions should trust the system_check.classify() output over the
  doc note. See `project_home_pc_hardware.md`.

- **Plan-vs-reality drift on Pascal is real.** The implementation plan
  had several Pascal code blocks that didn't compile under PascalScript.
  Subagents had to fix on the fly. This is normal — write the plan
  with real-Pascal references when possible, but expect the dialect
  restrictions to surface during ISCC iterations.

- **Subagent-driven dispatch works without superpowers.** Claude's
  built-in Agent tool does the same fresh-agent-per-task pattern.
  Don't block on installing canonical superpowers skills.

- **Pre-push gate is mandatory** for code pushes (per global CLAUDE.md
  rule from session 43). This session followed it for both Phase 1
  and Phase 2 — both ran clean after deslop cleanup.

- **`config.json` is tracked but treated as local runtime state.**
  Don't commit Alex's voice/model picks or runtime UI state. See
  session 45 rule (still active).

- **PRs stack via base-branch re-targeting.** When phase N+1's branch
  is built off phase N's tip, re-target the PR base from phase-N to
  master *before* phase N merges so neither orphan. Worked cleanly
  this session.

- **Stale-file `git status` after build** can be pure line-ending
  noise (CRLF/LF). Check `git diff` first; empty diff means
  `git checkout -- <file>` is safe. Caught merge once this session.

## Migration Status

n/a — koda is a desktop app, no DB migrations.

## Test Status

- **Master after both PRs merged**: 448/448 tests passing.
- **Phase 1 contribution**: +15 new tests (TestSystemCheckBlocked × 3,
  TestSystemCheckMinimum × 8, TestSystemCheckPower × 2,
  TestSystemCheckFallback × 1, TestSystemCheckCli × 1).
- **Phase 2 contribution**: +1 new test (TestThresholdsIssUpToDate
  drift-guard).
- **Total**: 432 (start of session) → 448 (end). +16 tests.
- **Suite**: `venv/Scripts/python -m pytest test_features.py -q`.

## Resume pointer

```
cd C:/Users/alexi/Projects/koda
# then in Claude Code:
/forge-resume
```
