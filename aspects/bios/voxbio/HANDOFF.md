# HANDOFF — voxbio (Vox-style mixed-media bio pipeline)

**The repository is the source of truth.** Verify everything below against the
files (read, grep, run `--help`) before acting — including this handoff. Where
a claim and the files disagree, the files win.

## What this is

Bear wants 3–5 minute Vox-style biography videos (six pilots listed below):
the editorial collage of the 2015–2019 Vox explainers — desaturated archival
photos on newsprint, isotype dot-grids, serif labels with hairline underlines,
flat annotation planes, golden highlighter bars, everything timed to
narration. The distilled style spec and the design decisions from a long
working session live in `/Users/nik/Documents/Cowork/vox-mix-thoughts.md` —
read it before building anything.

## The correction that ended the last session (important)

Two attempts were rejected, and the reason is the heart of this handoff:

The previous session kept building the look inside **greybox** — a free,
deterministic PIL+ffmpeg previz renderer. The second attempt got visually
close (archival-treated stills, cream islands, title/equation/date cards,
real narration muxed: see
`/Users/nik/Documents/Cowork/Manim/bio-planck/greybox/bio-max-planck-greybox.mp4`)
— but Bear rejected it: **"a video is collaged."** The target is a
**production pipeline, not a renderer imitating one**: ElevenLabs generates
the narration (master clock), Higgsfield / nano-banana / FLUX generate the
archival plates, portraits and footage, **Manim renders the graphics layer as
per-beat mp4/transparent fragments** (isotype grids, labels, underlines,
color blocks — the style spec is explicitly Manim-native), and **Remotion (or
ffmpeg overlay) collages those layers** into the final video, with reveals
keyed to word timestamps. Generation cost is low and approved. The PIL
renderer is previz only — useful for blocking before spend, never the
deliverable.

## Current state on disk

- **greybox skill (previz — built, works):**
  `/Users/nik/Documents/Cowork/unreal-reels/aspects/explainer/greybox/`
  (SKILL.md + `scripts/greybox.py`; verified copy at
  `/Users/nik/Documents/Cowork/quantum-mechanics-vol1/youtube/scripts/greybox.py`).
  Capabilities, all deterministic/free: journal + voxpaper skins; shared
  beat-sheet schema in; scrap-ID system (3-char Midjourney-mappable ids,
  `greybox-scraps.md` order sheets); provenance sidecar
  (`scraps/sources.json`) with derived STAND-IN X on generated/unsourced
  images of real people; clip slots (`slots/<beat>/clip.mp4`) with the
  conform ladder (retime ±5% → trim head → freeze tail → refuse >15%);
  isotype `viz` blocks with audio-window-derived dot stagger; portrait
  detection from narration; scratch-TTS/click/silent audio ladder;
  4-frame paper texture loop. None of this renders the final product.
- **voxbio skill doc (needs revision):**
  `/Users/nik/Documents/Cowork/unreal-reels/aspects/bios/voxbio/SKILL.md` —
  written before the correction; it wrongly frames `greybox --skin voxpaper`
  as the renderer at every fidelity. The workflow, inheritance from mini-bio,
  restraint rules, and archival policy sections remain valid.
- **Design record:** `/Users/nik/Documents/Cowork/vox-mix-thoughts.md` —
  slot/fidelity architecture, audio-first inversions of the style spec's
  timing math, clip-span quantization (spans of 1–3 beats, never across scene
  boundaries), placeholder-X provenance policy, restraint-as-guard rules.
  These decisions stand; only the renderer choice was wrong.
- **Six pilot bios** in `/Users/nik/Documents/Cowork/Manim/`: `bio-bose`,
  `bio-dorothy-gale`, `bio-jane-austen`, `bio-lift-every-voice`,
  `bio-planck`, `bio-shurpanakha`. These are finished ~30s mini-bios (skill:
  `/Users/nik/Documents/Cowork/unreal-reels/aspects/bios/mini-bio/SKILL.md`)
  with measured ElevenLabs mp3s, beat sheets with `card` blocks
  (title/quote/equation/date), and Higgsfield footage in `clips/`. Real
  people (Bose, Planck, Austen, the Johnson brothers) require real archival
  portraits; fictional (Dorothy, Shurpanakha) are Soul-ID generated.
- **A 16-beat voxbio draft sheet** (extended-Planck slice, unrendered
  by production tools): `/Users/nik/Documents/Cowork/Manim/bio-planck-vox/beat_sheet.json` —
  facts flagged for verification in `metadata.note`.
- **Also this session:** the `two-spots-not-a-smear-bb` Stern-Gerlach beat
  sheet + previz in
  `/Users/nik/Documents/Cowork/quantum-mechanics-vol1/youtube/`; a halted
  (harmless) lecture folder at
  `/Users/nik/Documents/Cowork/quantum-mechanics-vol1/lectures/01-why-classical-physics-failed/`.

## Existing machinery the production build reuses (do not reinvent)

- **Audio:** `generate_audio.py` (bears-doodles scripts, copies in
  `/Users/nik/Documents/Cowork/quantum-mechanics-vol1/youtube/scripts/`) —
  ElevenLabs per-beat mp3s, measured durations into the sheet.
- **Word timestamps:** `align_captions.py` (faster-whisper) → captions.json —
  this is what keys reveals to spoken words; `burn_captions.py` for karaoke.
- **Generation:** `/Users/nik/Documents/Cowork/unreal-reels/scripts/` —
  `generate_storyboard.sh` (Higgsfield Soul + nano_banana),
  `generate_composite_storyboard.sh` (FLUX multi-input compositing),
  `generate_stills_916.sh`, `generate_references.sh`, video via
  `generate_videos.sh` / seedance/hailuo variants. Keys live in Bear's shell
  env on his Mac; nothing generates from a sandbox.
- **Manim per-beat fragments:** the `manim_template.py` + `bn_layout.py`
  pattern (one draw function per beat); the style spec's `IsotypeDotGrid`
  Manim class is in the research doc inside
  `/Users/nik/Documents/Cowork/vox-mix-thoughts.md`'s source material.
- **Remotion assembly:** working projects in
  `/Users/nik/Documents/Cowork/Manim/Muzak/*/` and
  `/Users/nik/Documents/Cowork/unreal-reels/lectures/*/remotion/`, plus the
  deck-lecture skill's template
  (`/Users/nik/Documents/Cowork/unreal-reels/skills/deck-lecture/`).

## Settled constraints (from the session's discussion — details in vox-mix-thoughts.md)

Audio is the master clock; every visual conforms to measured mp3 durations,
clips via the conform ladder, isotype reveals via the audio-window stagger
with the 0.003–0.01 lag band as a pacing guard. Real people get real archive
images (LOC / Smithsonian OA / Wikimedia), recorded in `sources.json`;
generated stand-ins carry an un-strippable X until replaced. Restraint is
guard-enforced: 2 accents max (dusty blue `#5B7B9C` / terracotta `#D35F43`
family), cream ground, charcoal text, no gradients/glows/shadows, cream text
islands for WCAG contrast, cuts and quick fades only. Fictional characters
may be fully generated (Soul ID). Never commit keys or large media.

## Open items (the next session's work)

1. Rewrite `voxbio/SKILL.md` around the production pipeline: script →
   beat sheet (with `card`, `viz`, plate/portrait slots) → ElevenLabs audio →
   generation order sheet (Higgsfield/nano-banana/FLUX + archive hunts) →
   per-beat Manim graphic fragments → Remotion collage assembly with
   word-timed reveals → captions. greybox demoted to its previz role.
2. Build the assembler (the actual new machinery): a Remotion composition
   (or ffmpeg overlay chain) that stacks, per beat: newsprint ground →
   archival plate (still or footage) → Manim graphics fragment (transparent
   or luma-keyed mp4) → labels/highlight bars → narration track. Reuse the
   Muzak/deck-lecture Remotion scaffolds.
3. Prove it end-to-end on `bio-planck` (it has audio + footage today), then
   extend `/Users/nik/Documents/Cowork/Manim/bio-planck-vox/beat_sheet.json`
   to the full 3–5 min script and run the generation order sheet on Bear's
   Mac.
4. Then the remaining five pilots.

Bear runs render/generation commands on his Mac (full absolute paths, `ai`
env); the agent authors sheets, scenes, compositions, and order sheets.
