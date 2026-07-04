---
name: voxbio
description: >
  3–5 minute Vox-style biography videos — editorial paper-collage look
  (archival plates, circled portraits with golden name bars, isotype
  dot-grids, serif labels with hairline underlines, flat annotation plane)
  built on the greybox chassis and the shared beat-sheet schema. Stills +
  flat animation carry most beats (cheap FLUX / nano-banana / Higgsfield
  compositions dropped into scraps/), video clips only where motion earns
  it (slots/<beat>/clip.mp4, conformed to measured audio). Use when the
  user types `voxbio`, `vox bio`, asks for a Vox-style bio/documentary of a
  person or character, or wants to extend a mini-bio into the editorial
  collage format. Audio-first, real-people archival rule enforced by the
  STAND-IN X.
---

# voxbio — editorial-collage biographies

Sibling of **mini-bio** (same three-act story law, same audio-first
pipeline) with a different visual economy: where mini-bio alternates
full-frame photoreal Higgsfield video with dark Manim cards, voxbio is a
**flat paper collage** — desaturated archival plates, portraits in circles
with golden highlight name bars, isotype dot-grids, serif type with
hairline underlines, everything on a cream ground (`#FDFBF7`), two accents
only (dusty blue `#5B7B9C`, terracotta `#D35F43`). Stills are the star;
motion is the annotation plane landing on the voice. That makes a 3–5 min
bio cheap: **billed generation is stills, not per-beat video.**

## What it inherits (do not re-decide)

- **The mini-bio story law:** who were they → why did they matter → what
  endures. Open and close on the figure. A draft that doesn't answer all
  three isn't done. Length is an output of the story, never a target —
  3–5 min is the *natural range* for a layered life, not a quota.
- **Audio is the master clock.** Script → beats → ElevenLabs mp3s →
  measured durations drive everything. Isotype reveals derive their dot
  stagger from the beat's audio window; clips conform via the greybox
  ladder (retime ±5% → trim head → freeze tail → refuse >15%).
- **The shared beat-sheet schema** (bears-doodles), plus two voxbio
  extensions: `viz` (isotype block: label, counts, colors, legend) and the
  greybox slot drop-dirs (`greybox/scraps/`, `greybox/slots/<beat>/`).
- **Real-people archival rule.** Portraits and event plates of real people
  come from real archives (LOC Free-to-Use, Smithsonian Open Access,
  Wikimedia, Chronicling America for newsprint textures), recorded in
  `scraps/sources.json`. Generated stand-ins are welcome while blocking and
  render with the ink X + STAND-IN plate; the X leaves only when the file
  is replaced by a sourced one. Fictional figures (Dorothy Gale,
  Shurpanakha) may be fully generated — a Soul ID *is* their archival
  record.

## The renderer

`greybox.py --skin voxpaper` (the explainer greybox script) is the
renderer at every fidelity:

- **Level 0 — free previz.** Placeholder plates + silhouette portraits +
  scratch/click audio. Approve pacing, coverage, and the beat-to-visual map
  here.
- **Level 1 — stills dropped in.** Generate the order sheet
  (`greybox-scraps.md` prompts: FLUX for scene compositions, nano-banana
  for objects/world, Higgsfield Soul for fictional figures; archives for
  real people). Drop files into `greybox/scraps/`; the renderer
  archival-treats them (desaturate 80%, contrast 1.15) and re-renders.
  Same command, near-final visuals, still 12 fps stepped — the stop-motion
  print look is a feature, per the style spec.
- **Level 2 — real audio + selective clips.** `generate_audio.py` mp3s
  re-time everything; drop motion-worthy beats' clips into
  `slots/<beat>/clip.mp4`. Karaoke captions come from the existing
  `align_captions.py` + `burn_captions.py` pass afterwards.

Whether level 2 ships as-is or feeds a Remotion assembler (word-timed
annotation reveals) is an open decision — the beat sheet contract is
identical either way.

## Workflow per bio

1. `new <figure>` — folder `Manim/<bio-slug>-vox/` (or extend an existing
   `bio-*` mini-bio; never overwrite its sheet — voxbio gets its own).
   Research the life; verify every date and quote; list them in
   `metadata.note` as Gate-1 checkables.
2. `script` — three acts, one sentence per beat, 6–20 words; quote beats
   carry real attributed quotes only; isotype beats carry honest, checkable
   counts (the grid is a claim — `viz.note` records what to verify).
3. `greybox --skin voxpaper` — free previz + order sheet. THE GATE: approve
   pacing and the visual map before any spend.
4. Generate stills from the order sheet; drop into `scraps/` with
   `sources.json` records; re-render. Replace every STAND-IN X on real
   people with archive files.
5. `audio` → re-render at true pace → selective clips → captions → ship.

## Restraint rules (the style dies without them)

Two accents max — a third category uses a pattern, never a color. No
gradients, no glows, no drop shadows on type. Highlighter bars are sharp
rectangles in `#F5D061`. Serif labels get 1.5px hairline underlines in
their accent. Isotype grids: one value per dot, reading order, count-up
reveal timed to the audio window (the report flags grids too large for
their narration). Camera mechanics only at page turns. When a choice reads
as decorative rather than informational, delete it.

## The six pilot bios

`bio-bose`, `bio-dorothy-gale`, `bio-jane-austen`, `bio-lift-every-voice`,
`bio-planck`, `bio-shurpanakha` (mini-bios in `Manim/`). Real people (Bose,
Planck, Austen, the Johnson brothers) → archival portraits mandatory.
Fictional (Dorothy, Shurpanakha) → Soul ID generation throughout.
`bio-planck-vox/` is the built demo slice — extend its sheet to the full
three-act 3–5 min script as step 2.
