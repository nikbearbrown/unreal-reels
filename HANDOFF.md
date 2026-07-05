# HANDOFF — unreal-reels: the vox-explainer production pipeline, three films shipped

**The repository is the source of truth.** Verify everything below against the
files (read, grep, run with `--help`) before acting — including this handoff.
Where a claim and the files disagree, the files win.

Repo root: `/Users/bear/Documents/CoWork/bear-textbooks/books/unreal-reels`
(clone of `github.com/nikbearbrown/unreal-reels`, PUBLIC). A second working
copy lives on the other Mac at `/Users/nik/Documents/Cowork/unreal-reels`;
the two sync through origin and have occasionally diverged — check
`git status -sb` before assuming either is current.

## What this is

The vox-explainer skill
(`/Users/bear/Documents/CoWork/bear-textbooks/books/unreal-reels/aspects/explainer/vox-explainer/SKILL.md`)
is a production compositing pipeline for Vox-style editorial explainers.
This session it went from settled architecture to a working factory: THREE
complete films were built from Quantum Mechanics vol 1 chapters and published
to YouTube (playlist "Quantum Mechanics (Vox Style)", shorts to "Shorts"),
each as a 16:9 master plus a true 9:16 portrait Short:

- `reels/vox-ultraviolet-catastrophe/` — ch 1 concept 1 (Planck). Supersedes
  the older conversion test `reels/vox-the-ultraviolet-catastrophe/`.
- `reels/vox-photoelectric-effect/` — ch 1 concept 2 (Einstein 1905). Its
  Short ends ON the Einstein kicker (no endcard).
- `reels/vox-matter-waves/` — ch 2 (de Broglie). Its Short keeps the closing
  CARD, branded by the outro law with a vertical pool clip.

## The pipeline (each stage is a script; SKILL.md documents the workflow)

plan (script.md + beat_sheet.json + SHOTLIST.md, gate: human approves) →
factcheck (FACTCHECK.md per reel; `vox_run` REFUSES to render without it —
Gate F) → audio (`scripts/generate_audio.py`, ElevenLabs, Bear's voice
`TyW6NH39JcFb5M3xdIIk` in metadata.voice_id — REQUIRED or the API 404s) →
`scripts/vox_run.sh` (the full machine pass: Gate A static check → Manim
renders at the sheet's aspect → Gate B pixel audit `--curve-strict` → slot →
outro law → compile `--review`) → `pantry` (the COMMAND WORD: run
`scripts/vox_pantry.py` on the current reel — copies beat-prefixed media
from `pantry/`, strips audio, portrait clips auto-become `-916` overrides;
then reconcile source axis to `ai` + disclosure sidecars for generated
media) → `scripts/vox_short.py` (9:16 derivative; `--no-endcard` ends on the
last beat) → clean compiles (`vox_compile` without `--review` REFUSES
slates — the master law) → `scripts/vox_emit.py` (SRTs from beat sheets,
description with chapters/credits/AI-disclosure, mp4/ links) →
`aspects/explainer/bears-doodles/scripts/youtube_publish.py --no-pairs
--schedule-scope playlist --interval-hours 2 --floor-minutes 15`.

OAuth credentials live OUTSIDE all repos at
`/Users/bear/Documents/CoWork/bear-textbooks/publish-workspace/`
(client_secret.json, youtube_token.json, youtube_publish_ledger.json);
.gitignore blocks credential filenames anyway. Publishing runs on Bear's
Mac; the sandbox cannot push to GitHub or call paid APIs. All commands the
user runs use absolute paths, and `open <file>` commands accompany outputs.

## Doctrine written this session (each lives in its own file)

- Equation tangent (rule owner
  `aspects/explainer/brownblue/reference/equations.md`; vox rendering in
  SKILL.md + the `EquationTangent` kit in
  `aspects/explainer/vox-explainer/manim/vox_graphics.py`). Every landed
  equation fires a zones-2→3→4(→5) beat group; zone 5 = the physical
  commitment, mergeable into the sign-as-claim for simple equations.
- Motion pantry (`aspects/explainer/vox-explainer/MOTION.md`): seven motion
  languages, chef's-pantry discipline, 40% cap (compiler lints), captions
  are SIDECARS handed to the platform, never burn-ins, for explainers.
- "Who was X?" bio kicker: relevance-gated, end-of-film (SKILL.md).
- The pantry law + command word; the outro law (brands closing CARDs only,
  never writes through a derivative's symlinks; pool at
  `bearbrown/bearbrown-<ground>-<aspect>-NNN.mp4` — 17 light 9x16 + 6 light
  16x9 clips exist, legacy green-screen bears in `bearbrown/MP4/`); the
  Shorts law (derivative cut; 16:9 lays out SIDE BY SIDE, 9:16 stacks TOP
  AND BOTTOM; generated graphics are RE-LAID-OUT in the short's own
  `vox_scenes.py`, never cut; captured/generated media center-cuts
  focus-aware into inspectable `<beat>-916.*` files a human file always
  overrides); the master law (no slates in clean masters) — all in SKILL.md.
- Stock styles (`aspects/stock-styles.md`): WARMONO, NATGEO, and the
  PORTRAIT people-prompt template (ages COMPUTED from birth years, never
  guessed). Every person slot in a SHOTLIST carries a filled PORTRAIT
  prompt; generated portrayals of real people are always `source: ai` +
  disclosure sidecar, surfacing in the YouTube credits block via vox_emit.
- `arcads-collage-motion/` — a separate Arcads ads skill, UNTRACKED, not
  yet committed (user's call pending).

## Key machinery facts

- Manim CE does NOT recompute frame_width from `-r W,H`; `vox_graphics.py`
  syncs it at import (portrait frame = 4.5×8 units, safe area ±1.95/±3.4).
- Conform ladder: short clips SLOW to fit (never freeze; loud warn >3×);
  long clips trim tails. Per-beat `shot.treatment: light|none` relaxes the
  newsprint launder (used when color IS the information, e.g. forge glow).
- QC: `tmp/qc-tooling/` — Gate A render-free, Gate B pixel-true; annotation
  strokes declare `mob._qc_intentional = True` to exempt intentional
  strike-throughs/rings; text-on-text errors at ≥25% overlap.
- youtube_publish captions: retry over processing latency (9 attempts over
  ~14.5 min) — an earlier "Shorts refuse caption tracks" diagnosis was
  WRONG and was corrected in this copy and the book-repo copy. Shorts
  published before the fix may lack caption tracks; `--backfill-extras`
  retrofits them (per-surface SRTs).

## Current state (verified against the repo at handoff time)

HEAD `62a3df1` on main, **ahead of origin by 19 commits — needs
`git push origin main` from a Mac terminal** (the sandbox cannot push).
Working tree: modified `reels/vox-photoelectric-effect/SHOTLIST.md` (user
edits; stray prompt fragments sit at the top of the photoelectric and
matter-waves SHOTLISTs — unresolved whether to fold into people prompts or
delete), untracked `arcads-collage-motion/` plus regenerable per-reel audit
artifacts.

All three films: masters compiled, emitted, published via the ledger-driven
publisher (private-with-publishAt — they flip public automatically on their
drip slots). The caption backfill command for the pre-fix Shorts was handed
to the user; whether it was run is not recorded here — check the ledger and
YouTube Studio.

## Open items

1. **Authoring preflight** — highest value next build: Gate B caught 5+
   layout errors only after paid renders this session. A render-free check
   measuring declared text with real font metrics (PIL) against safe areas
   and declared strokes would catch these before any render command goes to
   the user.
2. **Remotion assembly plane** — specified in SKILL.md, never built:
   word-timestamp annotations (kiln arcs, document highlight sweeps, kicker
   name/dates), karaoke captions where wanted, auto-credits from sidecars.
3. **Film four** — matter-waves' outro promises THE WAVE FUNCTION (ch 3:
   `/Users/bear/Documents/CoWork/bear-textbooks/books/quantum-mechanics-vol1/chapters/03-the-wave-function.md`).
   The cycle is fully patterned; the three existing reels are the template.
4. Dark-ground outro pool (`bearbrown-dark-*`) not yet populated; dark-
   seeded reels fall back to the legacy keyed bear.
5. UV film book erratum candidate: "h within one percent" is strictly 1.15%
   (the chapter's own claim; noted in that reel's FACTCHECK.md).

## Key files

- Skill/doctrine: `aspects/explainer/vox-explainer/{SKILL.md, MOTION.md}`,
  `aspects/stock-styles.md`, `brutalist/EQUATIONS.md`,
  `aspects/explainer/brownblue/reference/equations.md`
- Scripts: `scripts/{vox_run.sh, vox_compile.py, vox_pantry.py,
  vox_short.py, vox_outro.py, vox_emit.py, vox_convert.py,
  generate_audio.py}`; publisher at
  `aspects/explainer/bears-doodles/scripts/youtube_publish.py`
- Manim library: `aspects/explainer/vox-explainer/manim/vox_graphics.py`;
  per-reel scenes in `reels/<slug>/vox_scenes.py` and
  `reels/<slug>/short/vox_scenes.py`
- QC: `tmp/qc-tooling/{static_scene_check.py, manim_layout_audit.py}`
- Each reel: beat_sheet.json (single source of truth), SHOTLIST.md,
  FACTCHECK.md, script.md, pantry/, media/ (+ `.source.txt` sidecars),
  manim/, clips/ (machine-owned), short/
