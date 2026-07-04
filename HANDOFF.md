# HANDOFF — unreal-reels: the vox-explainer skill and first two Vox reels

**The repository is the source of truth.** Verify everything below against the
files (read, grep, run with `--help` or `--dry-run`) before acting — including
this handoff. Where a claim and the files disagree, the files win.

Repo root: `/Users/bear/Documents/CoWork/bear-textbooks/books/unreal-reels`
(a clone of `github.com/nikbearbrown/unreal-reels`). A second working copy
lives on the other Mac at `/Users/nik/Documents/Cowork/unreal-reels`.

## What this is

This session built **vox-explainer**: a production compositing pipeline for
Vox-style mixed-media explainers (editorial newsprint collage — desaturated
archival plates, isotype square grids, serif labels with hairline underlines,
one hand-drawn annotation per graphic). Voiceover or music is the master
clock; the film is a composite of Manim fragments, Ken Burns stills,
archival/AI media, assembled per beat. It was tested end-to-end on two reels:
a recreation of Vox's Electoral College video, and a conversion of an existing
physics doodle video (the ultraviolet catastrophe), which Bear judged
"looking good."

## The architecture (settled)

- **Two-axis shot system.** Every beat carries `shot.type`
  (STILL / FOOTAGE / DOCUMENT / GRAPHIC / COMPOSITE / CARD — the presentation
  form, locked at plan time) and `shot.source` (`archive` / `ai` / `own` —
  provenance, late-bound and swappable). Full spec:
  `/Users/bear/Documents/CoWork/bear-textbooks/books/unreal-reels/aspects/explainer/vox-explainer/SKILL.md`.
- **Slot contract.** Every beat compiles to a conformed per-beat mp4 in
  `clips/` (machine-owned). Inputs resolve by precedence
  `media/<beat>.mp4` > `manim/<beat>.mp4` > `media/<beat>.png` (Ken Burns or
  hold) > slate. Slates say in terracotta whose job the slot is (YOU vs
  PIPELINE). Rebuilds recompile only slots whose input hash changed.
- **Audio.** `scripts/generate_audio.py` (ElevenLabs, Bear's voice
  `TyW6NH39JcFb5M3xdIIk`) writes mp3s + measured durations back into
  `beat_sheet.json`; the compiler muxes per-beat mp3s automatically when they
  exist. For conversions, narration is per-beat `keep` (reuse audio) or
  `rewrite` (regenerate only those beats with `--only`). The API key was
  hardened against whitespace/CR in `.env` values; the key now lives in
  `~/.zshrc`, and handed-off commands no longer source `.env`.
- **QC gates are wired into the runner.** Gate A: `static_scene_check.py`
  (render-free) on every pending scene before any render — the scenes file is
  checked from an isolated copy because the checker's repeated-animation
  heuristic assumes whole-video scenes, not per-beat fragments. Gate B:
  `manim_layout_audit.py --png` (pixel-true text-overlap/overflow audit) after
  each render; errors refuse to slot the mp4. Skip with `VOX_QC=0`. The tools
  live in `tmp/qc-tooling/` (consolidated from both machines and pushed; see
  its README and FINDINGS). The compiler also writes `qc-sheet.png` (mid-frame
  of every beat, tiled) on every `--review` build.
- **Greybox is dead for this aspect.** An earlier attempt built the test on
  the greybox previz renderer and was rejected ("a video is collaged" — the
  target is a production pipeline, not a renderer imitating one). The
  vox-explainer SKILL.md contains no greybox stage; a leftover `greybox/`
  folder in the electoral-college reel can be deleted.

## The engine files (all new/modified this session, mostly UNCOMMITTED)

- `/Users/bear/Documents/CoWork/bear-textbooks/books/unreal-reels/aspects/explainer/vox-explainer/SKILL.md` — the skill.
- `.../aspects/explainer/vox-explainer/manim/vox_graphics.py` — Manim library
  (IsotypeGrid with count-up, SerifLabel, LabelChip, StateCard with fit-to-card
  guard, HandRing, quote scenes) + the electoral-college fixture scenes. Has a
  BOLD guard for stub environments.
- `.../scripts/vox_compile.py` — slot compiler + assembler (conform ladder,
  treatment, Ken Burns via zoompan, incremental manifest, PIL slates/labels so
  it works on ffmpeg builds without drawtext, review burn-ins, QC sheet).
- `.../scripts/vox_run.sh` — one command: Gate A → render pending scenes →
  Gate B → slot → compile. Uses a reel's own `vox_scenes.py` if present, else
  the aspect library.
- `.../scripts/vox_convert.py` — converts a `physics/<slug>` doodle/brownblue
  folder into a vox reel: narration + durations carried, every visual
  re-planned (heuristic types, all `needs_review`), typed SHOTLIST with
  archive query URLs, `vox_scenes.py` scaffold.
- `.../scripts/generate_audio.py` — modified: strips whitespace/quotes/CR from
  the API key.

## The two reels

**`reels/vox-electoral-college/`** — ~133s excerpt recreation (transcript
timestamps as clock, then real ElevenLabs narration generated; 22 beats, every
shot type). 16 Manim slots rendered and slotted; `media/` holds B06/B21 stills
and a synthetic B02 test clip (replace with real news footage). Open archive
slots per its SHOTLIST: B02, B03 footage; B06, B15, B21 images. Reference
frames from the real Vox video are in `vox/` at repo root; full transcript in
the session record only.

**`reels/vox-the-ultraviolet-catastrophe/`** — converted from
`physics/the-ultraviolet-catastrophe`, editorial pass DONE: 4 beats rewritten
into Vox register (INTRO cold open, H02 infinite-UV prediction, A08 Planck
paper DOCUMENT, A12 Planck portrait kicker), 11 kept; audio regenerated (mp3/
exists); 12 scenes in its `vox_scenes.py` (single continuous chart arc:
axes → wave patterns → equal shares isotype → crimson Rayleigh–Jeans runaway →
navy Planck curve → chunk staircase → grey-out → runaway transforms into the
real curve); review mp4 + layout audit artifacts present. Open: 3 archive
images per its SHOTLIST (H01 foundry glow, A08 paper scan, A12 portrait — the
A12_Fuse scene renders as fallback until the portrait lands), and H02's
annotation-plane runaway (needs the Remotion assembly stage).

## Not yet built

The **Remotion assembly stage** (word-timestamp-keyed annotations: strike-X,
hand-rings on cue, highlighter sweeps, karaoke captions, credits from
`.source.txt` sidecars) is specified in SKILL.md but not implemented — beats
that depend on it (electoral-college B04; UV H02) slate or approximate until
then. Real map geometry for choropleths (PD shapefiles via SVGMobject) is also
pending; the 1948/2016 maps currently use tile-grid or legend-only stand-ins,
and B11/B12/B13 electoral data are approximations flagged VERIFY in
`vox_graphics.py`.

## Git state (needs a minute of attention)

`git log` shows HEAD at `60e7657` while an earlier `git pull` reported
fast-forwarding `60e7657..8dc88d9` and printed a stale-lock warning ("may have
crashed... remove the file manually"). All pulled `physics/` files show as
staged adds in `git status`. So the fast-forward appears half-applied: working
tree and index have the new content, HEAD may not have moved. Before
committing session work, check `git status`, remove any stale `.git/*.lock`,
and re-run `git pull origin main` (should no-op or complete cleanly). The
session's engine files (vox-explainer aspect, the three vox scripts, the
generate_audio fix) are engine code and were intended to be committed and
pushed; `reels/` content follows the repo's usual commit policy (definitions
yes, heavy media no — see `.gitignore` and README).

## Environment facts (this Mac)

ffmpeg 8.1.2 via Homebrew, built WITHOUT freetype — no drawtext filter; the
compiler auto-detects and uses PIL overlays instead (labels carry time ranges
in review builds; no running timecode). Do not swap ffmpeg for the tap build —
brew's manim links against this one. Manim CE 0.20.1 works (brew, plus a pip
copy in the `~/ai` venv). The venv was created with a pre-parenthesized prompt
(`'(ai) '`), which rendered `((ai) )`; the sed fix for
`~/ai/bin/activate` and `~/ai/pyvenv.cfg` was provided at session end — verify
it was applied. ElevenLabs credits ~1.37M remain; FLUX/nano-banana on
Higgsfield are cheap and approved-in-principle, but every paid call still gets
per-step user approval (AGENTS.md rule 6).

## Key files

- Skill: `aspects/explainer/vox-explainer/SKILL.md`
- Scripts: `scripts/vox_compile.py`, `scripts/vox_run.sh`, `scripts/vox_convert.py`
- Manim: `aspects/explainer/vox-explainer/manim/vox_graphics.py`, `reels/vox-the-ultraviolet-catastrophe/vox_scenes.py`
- QC: `tmp/qc-tooling/` (README + FINDINGS), per-reel `qc-sheet.png`, `layout_audit.md`
- Work orders: each reel's `SHOTLIST.md`
- Reference frames: `vox/` (Vox Electoral College screenshots, visual ground truth)
- Sibling prior art: `aspects/bios/voxbio/` (same collage language for bios), `physics/` (37 source videos, 29 with layout audits — conversion candidates; convert FIRST, audit after, since conversion drops scenes)
