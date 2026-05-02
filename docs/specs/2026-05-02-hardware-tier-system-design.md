# Hardware Tier System — Design Spec

**Date:** 2026-05-02
**Status:** Draft, awaiting user review
**Owner:** Alex Concepcion
**Related:** `docs/research/whisper-speed-analysis-2026-05-01.md`, `feedback_koda_perf_levers.md`

---

## 1. Goals & Non-Goals

### Goals

1. Detect the user's PC class at install time and apply tier-appropriate config defaults (`model_size`, `cpu_threads`, `process_priority`).
2. Prevent bad-first-impression installs on slow PCs without losing those users (soft-warn + auto-tune, not hard-gate).
3. Reach Inno-installer users with the existing Power Mode (NVIDIA GPU) flow, which is currently only exposed via `configure.py`.
4. Give users an honest in-app status surface so they understand what's currently active and why.
5. Single source of truth for hardware classification — one module called from both `configure.py` and the Inno `[Code]` section.

### Non-Goals

1. **Whisper compute optimizations** (streaming, OpenVINO, distil-whisper) — separate work tracks.
2. **Cloud backend / Groq** — explicitly off the table; local-only is a locked product promise.
3. **Phase 16 licensing tier mapping** — licensing tiers and hardware tiers are different axes; do not couple them in this work.
4. **Real-time workload-adaptive tuning** — the coworker's "running 20 Claude Code sessions" problem is workload-dependent, not hardware-dependent. Settings GUI override handles this; do not invent contention detection here.
5. **Mac port hardware detection** — Mac is its own multi-session project; this spec is Windows-only.

---

## 2. The Four Tiers

### Tier 0 — BLOCKED

**Trigger:** any of:
- 32-bit Windows (already enforced via `ArchitecturesAllowed=x64compatible`)
- Windows 9 or earlier
- <2 GB RAM
- <4 GB free disk

**User-facing behavior:** Inno installer shows a "System Requirements Not Met" page listing the missing requirement(s) with helpful next steps. Cancel-only — no Continue button. User dismisses the installer.

### Tier 1 — MINIMUM

**Trigger (any of):**
- <4 CPU cores
- <8 GB RAM
- Low-power CPU class detected (model name contains: `Atom`, `Celeron`, `Pentium`, `N100`/`N200`/`N300`, mobile-N series)

**User-facing behavior:** Inno installer shows a "Below Recommended Specs" page with honest copy:

> *Your PC is below recommended specs for Koda. Transcription will work, but it will be slower than typical (estimated 12–25 seconds for a 60-second clip on this hardware). Koda will configure itself for the best experience your PC can deliver. You can change these settings later in Koda → Settings → Performance.*

Buttons: `Continue Anyway` (default) / `Cancel`.

**Auto-tuned defaults (force-written to config.json):**
- `model_size: "tiny"`
- `cpu_threads: 2`
- `process_priority: "normal"`

### Tier 2 — RECOMMENDED

**Trigger:** 4+ CPU cores AND 8+ GB RAM AND no NVIDIA GPU.

**User-facing behavior:** silent. No wizard page added; the user proceeds through the existing wizard flow as today.

**Auto-tuned defaults (preserved from current `config.py`):**
- `model_size: "small"`
- `cpu_threads: 4`
- `process_priority: "above_normal"`

These are the validated-good defaults from the current codebase. No change in v1. Sub-tiering by core count (e.g., `threads=6` for 8+ core machines) is deferred — it requires the cpu_threads benchmark from the speed-gap research, which has not yet been run.

### Tier 3 — POWER

**Trigger:** any NVIDIA GPU detected via `nvidia-smi` OR `wmic` query AND CUDA runtime usable.

**User-facing behavior:** celebratory wizard page (see §5 — Power Mode Celebration).

**Auto-tuned defaults:**
- `model_size: "large-v3-turbo"`
- `compute_type: "float16"`
- `cpu_threads: 4` (irrelevant — GPU offloads compute)
- `process_priority: "above_normal"`

If NVIDIA GPU is present but CUDA runtime is not yet installed, the existing `configure.py` Bucket-B flow (offer to auto-install CUDA packages) is ported into Inno `[Code]` so installer-only users can also reach Power Mode without running `configure.py` separately.

---

## 3. Detection Signals

### What's detected and where

| Signal | Pascal in Inno `[Code]` | Python in `system_check.py` |
|---|---|---|
| CPU core count | `GetSystemInfo` Win32 | `os.cpu_count()` |
| RAM total | `GlobalMemoryStatusEx` Win32 | `ctypes` → same Win32 call |
| Free disk | Inno builtin `GetSpaceOnDisk` | `shutil.disk_usage` |
| Windows version | Inno builtin `GetWindowsVersion` / `IsWin64` | `sys.getwindowsversion` |
| CPU model name | Registry: `HKLM\HARDWARE\DESCRIPTION\System\CentralProcessor\0\ProcessorNameString` | Same registry path via `winreg` |
| Low-power CPU class | Regex match on CPU name | Regex match on CPU name |
| NVIDIA GPU presence | `Exec` of `nvidia-smi --query-gpu=name --format=csv,noheader` | Existing `hardware.py:get_nvidia_gpu_name()` |
| CUDA runtime usable | Skipped at install time (Inno cannot test ctranslate2 import) | Existing `hardware.py:detect_gpu()` |

### Why two implementations

The brainstorm scope said "single shared module callable from both `configure.py` and `koda.iss [Code]`." Pascal cannot import Python directly, so "single shared" means **one canonical Python module (`system_check.py`) plus a parallel Pascal implementation in `koda.iss [Code]` that uses the same constants and produces the same tier output**.

Constants are shared via build-time codegen, not runtime import:

1. `system_check_constants.py` is the single source of truth for thresholds (RAM_BLOCKED_BYTES, CORES_MIN_RECOMMENDED, RAM_GB_MIN_RECOMMENDED, CPU_LOW_POWER_PATTERNS, FREE_DISK_GB_MIN, etc.).
2. `installer/build_thresholds_iss.py` is a one-line build-time script that reads `system_check_constants.py` and writes `installer/thresholds.iss` — a Pascal snippet of `const` declarations.
3. `koda.iss` `#include`s `installer/thresholds.iss` so the Pascal classifier compiles with values guaranteed to match the Python side.
4. `installer/build_thresholds_iss.py` runs as a pre-step in the installer build (before `ISCC.exe`).

Drift is impossible by construction — Pascal's values come from Python's values via codegen. A unit test in `test_features.py` additionally verifies that `installer/thresholds.iss` is up-to-date relative to `system_check_constants.py` (regenerates and diffs).

### CUDA detection split

Pascal detects NVIDIA *presence* (driver installed, GPU enumerated). It does NOT verify CUDA *runtime usability* — that requires `ctranslate2.get_supported_compute_types("cuda")`, which only Python can do.

Therefore:
- **At wizard time** (pre-extract): Pascal tells us "NVIDIA hardware present (yes/no)." If yes, the wizard shows the Power Mode celebration page with a "Power Mode will activate after install completes" message.
- **At post-extract** (`ssPostInstall`): the just-extracted `Koda.exe --detect-hardware` runs and writes the final tier classification, including CUDA-runtime-usable verification. If CUDA is present but runtime isn't, the Bucket-B "auto-install CUDA packages" flow runs.

This split avoids the chicken-and-egg of needing Koda.exe to be installed before we can fully detect hardware.

---

## 4. Architecture

### Module layout

```
koda/
├── system_check.py              ← NEW: canonical classifier (Python)
├── system_check_constants.py    ← NEW: shared thresholds (consumed by Pascal too)
├── hardware.py                  ← KEEP: GPU-only detection helpers, used by system_check
├── configure.py                 ← MODIFY: replace Step 1 logic with system_check call
├── settings_gui.py              ← MODIFY: add Performance Mode dropdown + Advanced expander + status line
├── config.py                    ← MODIFY: defaults sourced from system_check on first run, otherwise unchanged
├── voice.py                     ← MINOR: add tray-tooltip "Power Mode" suffix when active
└── installer/
    └── koda.iss                 ← MODIFY: [Code] section calls Koda.exe --detect-hardware at ssPostInstall
```

### `system_check.py` interface

```python
def classify() -> dict:
    """
    Returns:
      {
        "tier": "BLOCKED" | "MINIMUM" | "RECOMMENDED" | "POWER",
        "reasons": ["<4 cores", "low-power CPU"],  # what triggered the tier
        "hardware": {
          "cores": int,
          "ram_gb": float,
          "free_disk_gb": float,
          "windows_version": str,
          "cpu_name": str,
          "is_low_power_cpu": bool,
          "nvidia_gpu_name": str | None,
          "cuda_runtime_usable": bool,
        },
        "defaults": {
          "model_size": str,
          "compute_type": str,
          "cpu_threads": int,
          "process_priority": str,
        },
      }
    """
```

CLI mode: `Koda.exe --detect-hardware --json` (and equivalently `python system_check.py --json` from source) prints the dict as JSON to stdout. Because Inno's `Exec` does NOT capture stdout, the install-time invocation redirects to a temp file:

```pascal
Exec(ExpandConstant('{cmd}'), '/c "' + AppDir + '\Koda.exe" --detect-hardware --json > "' + TempJsonPath + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
LoadStringFromFile(TempJsonPath, JsonText);
{ then parse JsonText with a small Pascal JSON helper or regex extraction }
```

The Pascal-side JSON parsing is intentionally minimal — only the `tier` field and `defaults.*` values are read, not the full hardware dict (which is debug-only).

### Data flow at install time

```
[Inno wizard pages]
  Pascal classify() ──► tier_minimum_or_lower? ──► show soft-warn page (Tier 1) or block page (Tier 0)
                  └──► nvidia_present? ──────────► show Power Mode celebration page (Tier 3)

[Inno files extract]
  ...

[ssPostInstall hook]
  Exec("Koda.exe --detect-hardware --json") ──► parse output ──► write config.json with auto-tuned defaults

[First Koda launch]
  config.json already has tier-appropriate defaults
  Tray tooltip + settings GUI status line read tier from config
```

### Data flow at runtime (re-detection)

On every Koda startup, `system_check.classify()` runs silently. Result is compared against the tier stamp in config:

- **No change:** silent, status line unchanged.
- **Hardware upgraded** (e.g., user added 16 GB RAM, jumped from MINIMUM to RECOMMENDED): silent re-tier IF user is on auto-detect mode. Settings GUI status line updates. No popup.
- **Hardware downgraded** (rare): silent re-tier IF on auto-detect. Settings GUI shows a single quiet status update on next visit.
- **GPU added** (new NVIDIA card): the same one-time celebratory tray balloon used in §5 fires once on the first launch where `nvidia_gpu_name` flips from None to a value AND the user is on auto-detect mode.
- **User has manual override set** (Performance Mode dropdown ≠ "Auto-detect"): hardware is detected but tier is NOT re-applied. Status line shows both: *"Auto-detect would pick: Recommended. Currently: Minimum (manual override)."*

---

## 5. Power Mode Celebration

### Installer banner moment (Tier 3 wizard page)

**Page composition:**
- Title (Inno wizard chrome, system font): `Power Mode Available`
- Description (Inno wizard chrome): `Your hardware just unlocked Koda's fastest mode.`
- Body bitmap: AI-generated Atlas Navy background (~600×300px), composited K-mark from `koda.ico` overlaid programmatically, navy hex `#1c5fb8` accent, green `#2ecc71` operational dot — see §5.1
- Body text below bitmap (Inno chrome): brief description of what Power Mode does (`Near-instant transcription. Larger, more accurate model.`) plus the detected GPU name (`Detected: NVIDIA GeForce RTX 4060`)
- Audio cue: `sounds/success.wav` plays once on page show via `mciSendString` Win32 call
- Buttons: `Continue with Power Mode` (default) / `Use Standard Mode instead`

If user picks "Standard Mode instead," the tier is downgraded to RECOMMENDED for this install. The override is persistent — settings GUI Performance Mode is set to "Recommended" with a note that Power Mode is available.

### 5.1 Background bitmap generation (AI-assisted)

The bitmap is **not designed by hand**. The pipeline:

1. Generate a background-only image using a generative-image tool (Gemini Stitch / GPT image gen / DALL-E / Midjourney).
2. Composite the existing `koda.ico` K-mark onto the background programmatically (one-shot Python/PIL script in `installer/build_power_banner.py`).
3. Render the banner text via Inno's native page chrome (NOT into the bitmap — generative tools are unreliable at text).
4. Convert PNG → BMP for Inno compatibility.

**Canonical AI prompt** (encoded in `installer/build_power_banner.py` as a docstring for reproducibility):

> Premium dark navy background banner image for a Windows installer page celebrating GPU hardware detection. Color palette: deep midnight charcoal-blue background (#0e1419 to #161d24 vertical gradient) with a single hero accent in IBM/Maersk premium navy (#1c5fb8) appearing as a subtle abstract glow or atmospheric element on one side. Mood: aerospace-corporate-premium, like Maersk shipping or Pan Am branding — NOT Tailwind blue (#3b82f6), NOT bright/saturated, NOT video-game-coded. Composition: 600×300 pixels, generous empty space in the center for a logo and text overlay. NO text in the image. NO logos in the image. Style: minimalist, restrained, single accent on a dark base. NOT earth-tone, NOT pink/rose, NOT carmine/red. Should feel like premium American tooling.

The reject list (Tailwind blue, video-game saturation, earth tones, pink, carmine) is the hard-won lesson from the session-47 Atlas Navy palette iteration loop. Keep it in the prompt verbatim.

### In-app status indicators (always-on for Tier 3)

These are NOT one-time celebrations; they are persistent indicators that Power Mode is active. No popups, no notifications, no manufactured "first launch" moment.

- **Tray tooltip suffix:** `Koda — Power Mode` (vs. plain `Koda` for other tiers)
- **K-mark dot in tray icon:** subtle Atlas Navy `#1c5fb8` glow around the operational green `#2ecc71` dot. Distinct from non-Power tiers but not loud.
- **Settings GUI Performance section:** a small "Power Mode: Active" badge in Atlas Navy near the Performance Mode dropdown, with a one-line explainer (`Using NVIDIA GPU acceleration via CUDA`).
- **Status line above the dropdown:** *"Currently: Auto-detect → Power Mode (NVIDIA GeForce RTX 4060, CUDA 12.x)."*

### One-time tray balloon (rare case)

If `system_check` detects a NEW NVIDIA GPU on a startup where one wasn't present before AND user is on auto-detect, fire a single tray balloon: *"Power Mode just activated — your new GPU is ready."* This catches the user-installed-a-GPU-after-Koda-was-installed case without a startup splash. Once shown, the `power_mode_balloon_shown` flag is set in config and never re-fires.

---

## 6. Settings GUI Override Surface

### Layered control (locked Q6 = Option 3)

**Performance section in `settings_gui.py`:**

```
┌─ Performance ──────────────────────────────────────────┐
│                                                          │
│ Currently: Auto-detect → Recommended                     │
│ Your hardware: 12 cores, 32 GB RAM, no NVIDIA GPU.       │
│                                                          │
│ Performance Mode: [Auto-detect (Recommended)        ▼]   │
│                    Auto-detect (Recommended)             │
│                    Minimum — Slow PC defaults            │
│                    Recommended — Standard defaults       │
│                    Power Mode (requires NVIDIA GPU)      │  ← greyed out if no GPU
│                                                          │
│ ▼ Advanced (override individual settings)                │
│   Model size:        [Small             ▼]               │
│   CPU threads:       [4]  (1–16)                         │
│   Process priority:  [Above Normal      ▼]               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Behavior rules

- **Auto-detect mode:** the three Advanced controls are read-only and reflect the currently-applied tier defaults. Status line shows the tier. Hardware re-detection on each launch updates the values silently.
- **Manual tier mode (Minimum / Recommended / Power Mode):** the three Advanced controls show the bundled defaults for that tier and are still read-only. Status line shows *"Currently: Minimum (manual override). Auto-detect would pick: Recommended."*
- **Advanced controls modified directly:** the Performance Mode dropdown auto-flips to a new "Custom" option (5th in the list, only appears once the user has touched an Advanced control). Custom = whatever values the user set; no bundle, no auto-tune. The status line shows *"Currently: Custom."*
- **Power Mode greyed out** if no NVIDIA GPU detected. Hover tooltip: `Requires an NVIDIA GPU with CUDA support.`

### Style

Atlas Navy palette throughout, consistent with the existing settings GUI redesign from session 47 (PR #36). Section header `Performance` uses the unified 11pt FONT_BODY bold style. The Advanced expander is a Polish-style ttk widget.

---

## 7. Re-detection Policy

| Event | Behavior |
|---|---|
| Every Koda startup | `system_check.classify()` runs silently |
| Tier unchanged | No-op |
| Hardware upgrade (e.g., +RAM, +cores via VM resize) | Silent re-tier IF on auto-detect; status line updates next time settings is opened |
| Hardware downgrade | Silent re-tier IF on auto-detect; status line updates next time settings is opened |
| New NVIDIA GPU appears | One-time tray balloon (`Power Mode just activated`) IF on auto-detect; flag set so it never re-fires |
| User on manual override | Hardware is detected but tier is NOT re-applied; status line shows both auto-detect-would-pick AND current-override |
| `system_check` fails (e.g., registry read error, `nvidia-smi` not on PATH) | Treated as MINIMUM tier with a debug.log warning; the user is never blocked by detection failure |

Re-detection is cheap (~50ms on a typical machine — registry + Win32 calls + maybe one `nvidia-smi` exec). Running it on every startup is fine.

---

## 8. Backward Compatibility

### Existing v4.4.0-beta1 installs

These installs already have a `config.json` with the current defaults (`model_size=small`, `cpu_threads=4`, `process_priority=above_normal`). The first launch after the v4.5.0 (or whatever version ships this) upgrade will:

1. Detect `system_check_tier` field MISSING from `config.json` → existing install
2. Run `classify()` silently
3. **Do NOT auto-overwrite** the user's existing model/threads/priority values. Stamp `system_check_tier` and `system_check_mode: "auto-detect"` into config.
4. Compare detected tier against existing config values:
   - If existing values match the auto-tier defaults → user is implicitly on auto-detect, no change
   - If existing values differ → user has effectively manual settings. Stamp `system_check_mode: "custom"` and preserve their values. Status line will show "Currently: Custom" on next settings open.

This guarantees no existing user gets surprised by their config silently changing under them on upgrade.

### Future config additions

The `system_check_tier` and `system_check_mode` fields are additive and use `deep_merge` from `config.py:100`. No migration script needed.

---

## 9. Testing Strategy

### Unit tests (`test_features.py`)

- `test_system_check_classifies_minimum_low_cores` — mock `os.cpu_count() = 2`, expect tier `MINIMUM`
- `test_system_check_classifies_minimum_low_ram` — mock RAM = 4 GB, expect `MINIMUM`
- `test_system_check_classifies_minimum_low_power_cpu` — mock CPU name = "Intel Atom x5-Z8350", expect `MINIMUM`
- `test_system_check_classifies_recommended_baseline` — mock 4 cores / 8 GB / no GPU, expect `RECOMMENDED`
- `test_system_check_classifies_power_with_cuda` — mock `nvidia-smi` returns GPU name, ctranslate2 supports CUDA → expect `POWER`
- `test_system_check_classifies_power_no_cuda_runtime` — mock GPU present but ctranslate2 cannot use CUDA → expect `RECOMMENDED` with reason `nvidia_no_cuda_runtime`
- `test_system_check_classifies_blocked_low_ram` — mock RAM = 1.5 GB → expect `BLOCKED`
- `test_system_check_defaults_match_tier` — for each tier, verify `defaults` dict matches §2 spec exactly
- `test_existing_install_preserves_user_values` — load a config.json without `system_check_tier`; verify model/threads/priority NOT overwritten
- `test_system_check_failure_falls_back_to_minimum` — mock all detection signals raising; expect `MINIMUM` tier with debug-log warning

### Manual cross-check (Inno installer)

Build the v4.5.0 installer and test on at least three machine classes:

1. **Slow PC** — 2-core / 4 GB / integrated graphics. Should show MINIMUM warning page, force-write `tiny`/`threads=2`/`normal`.
2. **Recommended PC** (Alex's UHD 770 host) — 12+ cores / 32 GB / no NVIDIA. Silent install, defaults unchanged.
3. **Power PC** (any machine with NVIDIA GPU + CUDA) — should show celebration page, write `large-v3-turbo`/`float16`.

If the coworker's machine is available, install there too and verify it lands in the expected tier.

### Regression tests

- 432/432 existing tests must still pass.
- The new `test_features.py` additions bring the count to ~445.

---

## 10. Out of Scope (explicit non-goals)

To prevent scope creep during implementation:

- ❌ **Streaming transcription** — the perceived-latency fix is a separate work track, not part of tier classification.
- ❌ **Cloud / Groq backend** — local-only is locked.
- ❌ **cpu_threads sub-tiering** within RECOMMENDED — needs the cpu_threads benchmark first; deferred.
- ❌ **Mac port hardware detection** — Mac is its own multi-session project.
- ❌ **Workload-adaptive tuning** — coworker's "competing with Claude Code" problem; settings override is the surface, not classification.
- ❌ **First-launch celebration splash** — explicitly killed in brainstorm. Persistent in-app indicators replace it.
- ❌ **Whisper model bundling changes** (e.g., adding a NEW model size) — uses existing `_model_tiny` / `_model_small` / `_model_large_v3_turbo` infrastructure already in PyInstaller bundle.
- ❌ **Phase 16 licensing tier mapping** — different axis; do not couple.

---

## 11. Open Questions (none — all locked in brainstorm)

All design decisions reached in brainstorm Q1–Q6:

- Q1: Soft-warn + auto-tune below recommended; hard-block reserved for truly-can't-run.
- Q2: Absorb GPU/Power Mode into unified 4-tier system.
- Q3: Installer banner with AI-generated background + composited K-mark + native Inno text + audio cue, plus persistent in-app status indicators. NO first-launch splash.
- Q4: Moderate thresholds (4-core / 8 GB RAM as RECOMMENDED floor).
- Q5: Single RECOMMENDED defaults (no sub-tiering by core count); full force-write for MINIMUM.
- Q6: Layered settings GUI override (tier dropdown + Advanced expander + honest status line).

---

## 12. Implementation Phasing

The build is naturally four phases, each independently shippable:

1. **Phase 1 — `system_check.py` module + tests** — pure Python, no installer changes. Adds `classify()` and unit tests. configure.py is updated to use it. Settings GUI gets the new Performance section + Advanced expander.
2. **Phase 2 — Inno installer integration** — Pascal classifier in `koda.iss [Code]`, soft-warn page, hard-block page, post-extract `Koda.exe --detect-hardware` call, config write at `ssPostInstall`.
3. **Phase 3 — Power Mode celebration** — AI-gen banner bitmap (one-shot prompt + composite + BMP convert), wizard page wiring, audio cue, in-app indicators (tray tooltip suffix, settings badge, K-mark dot glow).
4. **Phase 4 — Backward-compat + multi-machine validation** — first-launch detection-without-overwrite logic, manual install on the three machine classes (Slow / Recommended / Power), coworker install if available.

Each phase ends with the pre-push gate (`forge-deslop` + `forge-review`).

---

*End of design spec.*
