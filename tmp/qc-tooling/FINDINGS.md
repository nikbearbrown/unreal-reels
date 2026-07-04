# Video Visual-QC Tooling — Findings

_Search run 2026-07-03. Scope: `~/Documents/Cowork` (the only tree mounted for this session — see "Coverage limits" at the end)._

## TL;DR

Your visual-QC tool exists and is real. It is **`manim_layout_audit.py`** — a deterministic, OCR-free layout checker that asks Manim for the exact bounding box of every on-screen `Text` object and flags **text-on-text overlap**, **out-of-frame / out-of-safe-area** text, and (in the newest version) **text struck by a curve/stroke**. With `--png` it saves annotated frames at each flagged moment (the per-beat contact-sheet behavior you remembered).

There are **two generations** of it plus a **render-free companion**:

- **Newest, 515-line** `manim_layout_audit.py` (adds the TEXT/CURVE check, `--portrait`, `--curve-strict`) — modified **2026-07-03**. This is the most complete.
- **Older, 426-line** `manim_layout_audit.py` — 2026-06-24/25.
- **`static_scene_check.py`** (779 lines) — a Manim-free static smoke + distinctness + in-frame check for machines without a working Manim/pangocairo install. Companion, not a replacement.

**The catch you were worried about is real:** the newest 515-line version is **untracked (never committed)** in `quantum-mechanics-vol1`. The good news: an **identical copy is committed AND pushed** inside the `unreal-reels` repo, so the code itself is not lost. `static_scene_check.py` is **committed but NOT pushed** (sitting in a large unpushed commit in the `Manim` repo).

I copied the best files, unmodified, into `~/Documents/Cowork/qc-tooling-found/`.

---

## 1. Ranked list of QC scripts found

### Rank 1 — `manim_layout_audit.py` (newest, 515 lines) ⭐ most complete
Deterministic layout QA for Manim scenes. Hooks the scene at every steady-state moment (each `wait`, end of each `play`) and asks Manim for exact `Text` bounding boxes — no pixels, no OCR, font-agnostic. Flags: (1) **TEXT-ON-TEXT** overlap, (2) **OUT-OF-FRAME** text leaving the safe area (WARN) or the visible frame (ERROR), (3) **TEXT/CURVE** — a label struck by a stroke/connector (WARN, or ERROR with `--curve-strict`). Emits `layout_audit.json`, `layout_audit.md`, and with `--png` an annotated `layout_audit_frames/` PNG per flagged moment. Exit 0 clean / 1 warn / 2 error. Advisory — never edits the scene.

- **Locations (identical, md5 `1212c624…`):**
  - `quantum-mechanics-vol1/youtube/scripts/manim_layout_audit.py` — **UNTRACKED (never committed)**, mtime **2026-07-03 12:15**
  - `unreal-reels/aspects/explainer/bears-doodles/scripts/manim_layout_audit.py` — **tracked, committed, pushed** (clean, 0 ahead/0 behind), mtime 2026-07-03 00:46
- **Copied to:** `qc-tooling-found/manim_layout_audit.py`

### Rank 2 — `static_scene_check.py` (779 lines) — render-free companion
Manim-free static QA. Executes a scene's `construct()` against a lightweight geometry **stub** so it runs with no Manim install. Catches the four things that actually broke the Codex-authored biology scenes: (1) **RUNS AT ALL** (no Python error), (2) **NO GENERIC ART** (file doesn't contain the `generic_art` template that produced one identical drawing for a whole video), (3) **DISTINCT PER BEAT** (on-screen shapes actually change across beats — reported as a distinct-states ratio), (4) **IN FRAME** (explicit coordinates stay inside the 16:9 frame ±7.1x/±4.0y). Exit 0/1/2. Advisory. Explicitly *not* a pixel-perfect replacement for the real render.

- **Location:** `Manim/tools/scripts/static_scene_check.py` — **tracked, committed, but in an UNPUSHED commit**, mtime 2026-06-25 19:54
- **Copied to:** `qc-tooling-found/static_scene_check.py`

### Rank 3 — `manim_layout_audit.py` (older, 426 lines)
The previous generation of Rank 1 — same TEXT-ON-TEXT and OUT-OF-FRAME checks, but **without** the TEXT/CURVE detection, `--portrait`, or `--curve-strict`. Superseded; listed for provenance.

- **Locations (identical, md5 `2b6b2150…`):**
  - `Manim/tools/scripts/manim_layout_audit.py` — **tracked, committed, pushed**, mtime 2026-06-25 11:48
  - `bears-doodles/scripts/manim_layout_audit.py` — loose working copy, **not in any git repo**, mtime 2026-06-24 12:33
- **Copied to:** `qc-tooling-found/manim_layout_audit_v426_older.py` (for reference)

### Adjacent / related (found, but NOT the visual-QC tool)
These turned up in the same searches and share vocabulary, but check text/scripts/production plumbing rather than rendered-frame layout:

- `slide-deck/scripts/verify_deck.py` — static audit of an emitted `.dc.html` deck (every beat has speaker-notes; palette/blue-ban rules). Text/HTML, not video frames.
- `deck-lecture/scripts/script_guard.py` — flags narration that *reads* the slide (Jaccard overlap of narration vs on-slide text).
- `deck-lecture/scripts/tts_audit.py` — flags TTS pronunciation risks before spending render budget.
- `lyric-match/scripts/extract_frames.sh` + `pick_stills.py` — extract frames from an mp4 and pick the sharpest per beat (Laplacian variance). This is the closest thing to frame-extraction / contact-sheet plumbing, but it's for **lyric-match production**, not QC.
- `greybox/scripts/greybox.py` — zero-cost previz (blockout), not QC.
- `make_short.py` — 16:9 → 9:16 reframe, production.
- `verify_extras.py` (QM + Manim) — read-only **YouTube** caption/playlist check, unrelated to visual layout.
- `shared/pacing/pace_check.py`, `shared/grounding/grounding_check.py` — script-level pacing/grounding, not frame layout.

_(The `madison/` tree also matched `audit`/`quality-check`/`visualization`, but that's the brandguide.ai brand-audit app — a different domain — and was excluded from the deep pass.)_

---

## 2. Exact invocation commands

**Rank 1 — `manim_layout_audit.py` (needs a working Manim / pangocairo install):**

```bash
ai            # your env activator
cd ~/Documents/Cowork/Manim/energy-levels-arent-evenly-spaced
python ~/Documents/Cowork/qc-tooling-found/manim_layout_audit.py energy_levels_arent_evenly_spaced.py
```

Common flags:

```bash
# default: reads the only non-helper .py in the current folder
python manim_layout_audit.py                     # scene arg optional
python manim_layout_audit.py scene.py --png       # + annotated frames at flagged moments
python manim_layout_audit.py scene.py --portrait  # 9:16 safe area
python manim_layout_audit.py scene.py --curve-strict   # TEXT/CURVE becomes an ERROR
python manim_layout_audit.py scene.py --class BearsDoodlesVideo \
       --safe-w 6.3 --safe-h 3.4 --min-overlap 0.12
```

Outputs (written next to the scene): `layout_audit.json`, `layout_audit.md`, `layout_audit_frames/` (only with `--png`). Exit code **0** clean / **1** warnings / **2** errors.

**Rank 2 — `static_scene_check.py` (no Manim needed):**

```bash
python ~/Documents/Cowork/qc-tooling-found/static_scene_check.py scene.py     # one scene
python static_scene_check.py <folder>              # finds the scene in a folder
python static_scene_check.py --all                 # every why-* folder
python static_scene_check.py --all --json out.json
```

Exit **0** clean / **1** warnings / **2** errors.

---

## 3. Unpushed / uncommitted git state

| Repo | Remote | Branch | Relevant QC state |
|---|---|---|---|
| `quantum-mechanics-vol1` | `github.com/nikbearbrown/quantum-mechanics-vol1` | main | **Newest `manim_layout_audit.py` is UNTRACKED (`??`) — never committed here.** Also `greybox.py`, `verify_extras.py` untracked. Repo is **1 commit ahead** of `origin/HEAD` (unpushed). |
| `Manim` | `github.com/nikbearbrown/quantum-mechanics-videos` | main | `static_scene_check.py` (779-line) and the older 426-line `manim_layout_audit.py` are **tracked**. `static_scene_check.py` sits in an **UNPUSHED commit** `520bad1` ("rename TIKTOC->BLUEPRINT; add BLUEPRINT.md…"), repo is **1 commit ahead** of origin. That commit is huge (~42k files, incl. rendered `layout_audit.json/.md` outputs). `verify_extras.py` untracked. |
| `unreal-reels` | `github.com/nikbearbrown/unreal-reels` | main | Newest `manim_layout_audit.py` is **tracked, committed, and pushed** (clean, 0 ahead / 0 behind). ✅ The code is safe here. |
| `bears-doodles` | — (no `.git`) | — | Loose working copy of the **older** 426-line `manim_layout_audit.py`. Not under version control at all. |

**Bottom line on git:** the newest layout auditor is **safely pushed inside `unreal-reels`**, even though its copy in `quantum-mechanics-vol1` was never committed. The render-free `static_scene_check.py` is **committed but not yet pushed** (in `Manim`'s unpushed commit `520bad1`) — that one is the only piece of QC code whose latest form exists **only locally**. Consider pushing `Manim` (or at least cherry-picking `static_scene_check.py`) to back it up.

_Nothing was modified, staged, committed, or deleted during this search._

---

## 4. Recommendation — which one is most complete

**Use the newest 515-line `manim_layout_audit.py` as your primary visual-QC tool.** It is the most complete: it does everything the older version does (text-on-text overlap, out-of-frame/safe-area) **plus** the TEXT/CURVE strike check, portrait-mode safe area, and `--curve-strict`, and it produces both machine-readable (`layout_audit.json`) and human-readable (`layout_audit.md`) reports with optional annotated PNGs. It's the true "checks Manim output for layout problems — overlapping text, labels overflowing the frame, legibility" tool you described.

Pair it with **`static_scene_check.py`** as the fast pre-flight on any machine where Manim/pangocairo isn't installed — it won't catch pixel-level layout, but it catches the crash / generic-art / repeated-animation / out-of-bounds-coordinate classes cheaply before you spend render time.

I copied all three (newest, render-free companion, and the older one for reference) unmodified into:

```
~/Documents/Cowork/qc-tooling-found/
├── manim_layout_audit.py            # Rank 1 — newest, 515 lines (md5 1212c624…)
├── static_scene_check.py            # Rank 2 — render-free companion (md5 3afa5002…)
└── manim_layout_audit_v426_older.py # Rank 3 — older 426-line, for provenance (md5 2b6b2150…)
```

---

## Coverage limits

This session could only reach the **`~/Documents/Cowork`** tree. I was **not** able to scan `~/Documents/` outside Cowork or the rest of the machine (e.g. `bio-*` or `lecture` folders that might live elsewhere), because only the Cowork folder is mounted here. If your QC code also has copies outside Cowork, point me at that folder (or run the same filename/content search there) and I'll fold the results in. Within Cowork, the search covered filenames **and** file contents (`contact sheet`, `extract_frames`, `drawtext`, `overlap`, `bounding`, `qc`, `verify_`, `legib`, etc.) across every `*.py` and `*.sh`.
