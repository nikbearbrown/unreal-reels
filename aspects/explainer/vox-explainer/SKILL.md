---
name: vox-explainer
description: >
  Vox-style mixed-media explainer videos — a PRODUCTION COMPOSITING PIPELINE,
  not a previz renderer. Voiceover (ElevenLabs) or a music bed is the master
  clock; the film is a composite of Manim motion-graphics fragments, Ken Burns
  animation over stills (archival or FLUX/nano-banana), AI video clips
  (Higgsfield/Hailuo/Seedance), public-domain footage, and a Remotion
  annotation/caption plane — all unified by the editorial newsprint treatment
  and assembled per beat. Two-axis shot system (type × source), slot contract
  (swap media/<beat>.png|.mp4 by filename, rebuild recompiles only changed
  slots). Use when the user types `vox`, `vox-explainer`, `vox style`, or asks
  for a Vox-style / editorial-collage / isotype explainer. Audio-first,
  phase-gated; generation costs are LOW and expected (FLUX/nano-banana stills,
  ElevenLabs VO) — ask per step, then spend.
metadata:
  tags: vox, isotype, explainer, mixed-media, compositing, manim, remotion, kenburns, elevenlabs, higgsfield
---

# vox-explainer — mixed-media editorial explainers (production pipeline)

The Vox explainer grammar (Electoral College, Borders era) as a compositing
pipeline. Reference frames: `vox/` at repo root — ground design decisions in
those frames, not memory. **This skill produces the finished video by
compositing; there is no scrapbook previz stage.** The first watchable pass IS
the production pipeline running with slates in unfilled slots.

## What Vox actually is

Not a style — a *laundering function*. Any source (archival photo, FLUX still,
PD film, AI clip, Manim fragment) passes through one treatment (desaturate
~80%, contrast 1.15, seated on a real newsprint scan) and lands on one flat
annotation plane. Sources never match; the treatment does. That is why mixed
media reads as one film — and why compositing found + generated + programmatic
media is EASIER here than one visual style.

## The clock

1. **Voiceover films:** script → beats → ElevenLabs mp3 per beat
   (`scripts/generate_audio.py`, Bear's voice default) → measured
   `actual_duration_s` + word timestamps. GATE 0: audio lock. Credits are
   cheap and available — ask, then generate. Runs on the user's machine.
2. **Music films:** librosa beat grid on the track (songbird machinery);
   downbeat-aligned segments become the beats.
3. **Recreations:** the source's transcript timestamps are the clock (the
   test fixture works this way — no TTS needed to validate timing).

Never estimate from word count. Reveals inside a beat key to word timestamps.

## Design tokens (from the `vox/` frames)

Cream ground `#F3EBDD` over a real newspaper scan (Chronicling America), full
plane. Charcoal serif `#2F2A26`, never pure black. Data pair: crimson
`#BF3339` vs dusty navy `#3D5A80`; general pair: dusty blue `#5B7B9C` vs
terracotta `#D35F43`. One editor's-pen voice per graphic: golden highlighter
`#F5D061` bar OR hand-drawn ring/ellipse/X in terracotta or yellow. Slate-teal
`#3E5559` entity cards with white serif labels. Isotype marks: squares or dots
— one choice per film. Label chips: accent block, white serif text. Serif
labels carry 1.5px hairline underlines in their accent.

## THE TWO-AXIS SHOT SYSTEM

`shot.type` = presentation form, locked at the plan gate, never changes when
media swaps. `shot.source` = provenance (`archive` | `ai` | `own`), late-bound,
swappable. Collapsing them makes every swap a re-edit; separating them makes
swaps free.

| type | is | produced by |
|---|---|---|
| STILL | treated image, `hold` or `kenburns` | archive download / FLUX / nano-banana → compile animates |
| FOOTAGE | moving clip fills the beat | PD film / Higgsfield i2v from the slot's still (key action early — tail trims) |
| DOCUMENT | scan/quote, annotation-driven motion | archive scan + Remotion highlight/underline/zoom keyed to words |
| GRAPHIC | isotype grid, bars, map, cards | **Manim fragment** (`manim/vox_graphics.py`) rendered to the beat's measured duration |
| COMPOSITE | treated plate + annotation collage | plate like STILL; annotation on the Remotion plane |
| CARD | title/section/end | Remotion typography, design system only |

Rhythm lint: shot-type histogram; flag >2 consecutive same-type beats.

## The motion pantry (`MOTION.md` — doctrine)

Seven motion languages; a pantry, not a recipe — a language enters a film
ONLY if it improves that beat, and most films use three or four. Per beat,
`shot.motion` ∈ `hold | kenburns | pan | parallax | isotype | drawon | map |
kinetic | annotate` (near-orthogonal to `shot.type`). Global rules: motion is
subordinate to information delivery; no language carries >~40% of a film's
beats (compiler prints the histogram and warns); reveals land on the spoken
word; constant velocity for documentary moves, easing only for UI-feeling
elements. Ken Burns beats may set `shot.focus: [fx, fy]` (0–1 image coords)
to motivate the zoom toward the sentence's subject. Kinetic-type beats carry
word-level `sub_beats` (captions generate from the same data); optional `sfx`
tag per beat for the subliminal beat-synced sound pass. Full constraints,
sequencing (which language, where in the film), and the built/pending status
of each language: `MOTION.md`.

## THE SLOT CONTRACT

```
reels/<slug>/
  beat_sheet.json     single source of truth
  audio/              per-beat mp3s + word timestamps (the clock)
  media/              YOURS — inputs: B07.png, B07.mp4, B07.source.txt
  manim/              rendered graphic fragments land here as <beat>.mov|mp4
  clips/              MACHINE'S — conformed per-beat mp4s. Never hand-edit.
  SHOTLIST.md         typed work order: prompts + archive links per slot
```

- Everything on the timeline is a per-beat conformed clip. Precedence at
  compile: `media/<beat>.mp4` > `manim/<beat>.mp4` > `media/<beat>.png`
  (animated per `shot.motion`) > **slate** (charcoal, beat id — a missing-media
  marker, standard production slate, so pass 1 is always watchable).
- Conform at ingest: scale/crop → duration ladder (retime ±5% → trim head →
  freeze tail → refuse >15%) → treatment per source. Rebuild recompiles ONLY
  slots whose input hash changed, then re-concats. `scripts/vox_compile.py`
  implements this.
- The png in a FOOTAGE slot is both the placeholder and the i2v seed; the mp4
  is the upgrade. Stills + Ken Burns carry most beats; AI video where motion
  earns it (~5s beats sit in the i2v sweet spot).
- Provenance sidecar (`<beat>.source.txt`: URL, license, credit) required on
  `archive` slots → auto-credits block. Real people/events → real archives.
- Annotations, captions, and the `--review` burn-in (global TC + beat id +
  beat-local clock + slot status) live on the assembly overlay — never baked
  into `clips/`. Clean master = same assembly, no flag.

## The Manim graphics library (`manim/vox_graphics.py`)

`IsotypeDotGrid` (count-up reveal, lag_ratio 0.003–0.01, duration = the
beat's audio window), `IsotypeFraction`, `StateCardPair` (slate-teal cards,
serif labels, figure lines), `QuoteCard` (highlighter sweep timed to words),
`LabelChip`, hand-drawn `AnnotationRing`/`StrikeX` strokes. Transparent or
newsprint-ground renders at beat duration:
`manim -qh --fps 24 vox_graphics.py <Scene> -o <beat>.mp4`. Counts are claims
— `viz.note` records what to verify before render.

## The equation tangent (doctrine: `brutalist/EQUATIONS.md`)

When an equation appears, the film takes a short tangent — the five-zone
template from `brutalist/EQUATIONS.md`, translated into Vox language. A
tangent explains; it never derives. **A tangent is a BEAT GROUP, not one long
beat** (Vox rhythm stays ~5–12s/beat): the equation card persists as the
anchor across the group while the zone below swaps per beat —
sentences → glossary → worked example → values claim. Re-entry is narration
only ("…and that's demographic parity. Back to …").

- Beats are GRAPHIC type with `viz.pattern: "equation_tangent"`; the group
  shares one `viz.tangent` block (the EQUATIONS.md authoring schema, plus
  `equation_tex` for real typesetting) and each beat names its `viz.zone`
  and optional `viz.spotlight` symbol.
- Translation table: one-red-moving → **crimson spotlight** (the symbol being
  named turns crimson in equation + glossary row + example value at once);
  pink values box → **terracotta-tinted panel**; white mechanics → newsprint
  ground + ink serif; KaTeX → **MathTex** (italic variables, roman operators;
  `_math()` falls back to italic serif where LaTeX is absent). Data numbers
  mono, never the equation.
- Components in `vox_graphics.py`: `EquationTangent` (+ `EquationCard`,
  `SentencePair`, `GlossaryTable`, `WorkedExample`, `ValuesClaim`); fixture
  scenes `EQT_*` carry the demographic-parity demo.
- Audit per tangent: sentences before symbols and the relation read as a
  claim; glossary has the Role column; example holds-or-breaks and ends on
  the human cost; values claim in the tinted panel; eyebrow on entry,
  re-entry cue in the narration; ≤ ~45s across the group; no derivation.
- Word-keyed spotlight advancement (crimson moving with the narration line)
  upgrades automatically when the Remotion assembly stage lands; until then
  each beat sets one static spotlight.
- If the equation's author gets a "Who was X?" kicker (below), the tangent
  stays on the math — the kicker owns the person. Never teach either twice.

## The "Who was X?" kicker (bio tangent — RELEVANCE-GATED)

Most explainers do NOT get one. Include it ONLY when the person is
load-bearing — their idea is the film's turn, not a passing citation. If the
film merely uses an equation, the credits line suffices. When it earns its
place:

- **Placement: the kicker.** After the argument resolves, usually the
  penultimate or final beat — never interrupting the argument mid-film.
  (Fixture: the UV catastrophe reel's A12 Planck portrait beat.)
- **Size: 1–2 beats.** A face, a name, dates, and ONE human line that
  reframes the film just watched ("He thought it was a mathematical trick.
  It was quantum mechanics."). A life story is a different film — hand it
  to `aspects/bios/voxbio`.
- **Division of labor, never twice:** the equation tangent teaches the MATH;
  the bio kicker teaches the PERSON; the mini-bio/voxbio teaches the LIFE.
  If a mini-bio of X exists and covers the equation, the explainer's kicker
  skips the equation entirely and may end by pointing at the bio ("the
  Planck film"). Conversely a mini-bio never re-runs the explainer's tangent.
- **Form:** STILL — real archive portrait (provenance sidecar mandatory,
  real-people rule) + serif name with hairline underline + dates + the one
  line. No isotype, no chart, no second idea on screen.

## The outro law (`scripts/vox_outro.py`)

Every film ends the same way: `@nikbearbrown` (serif, terracotta hairline) on
top, a Bear Brown mascot variant dancing center frame (chroma-keyed from
`bearbrown/`, full color — the one deliberately loud brand element), the
beat's "Next:" line below. Ground is cream or ink and the mascot variant is
picked deterministically from the reel slug — random across reels,
reproducible within one. The outro may run past the narration; the silence
tail is padded INTO the beat's mp3 (audio stays the master clock), and
`actual_duration_s` updates to match. One command after audio lock:
`python3 scripts/vox_outro.py reels/<slug>` — then recompile; only the outro
slot rebuilds.

## Workflow (each gate is the user's)

1. `plan` — script → beats (≤~28 words), shot type × source, prompts, viz
   data, archive queries → `SHOTLIST.md`. **GATE: approve the plan.**
2. `audio` — ElevenLabs per beat, measure, lock. **GATE: hear it.**
3. `graphics` — render Manim fragments to measured durations (local, free).
4. `stills` — FLUX / nano-banana plates for ai slots (cheap — batch with
   per-step go-ahead); download archive picks for archive slots (free).
5. `compile` — `python scripts/vox_compile.py reels/<slug> --review` →
   watchable cut, slates where media is missing. **GATE: timing + content.**
6. `video` — Higgsfield i2v only for beats where the still + audio demand
   motion (the expensive step, last, per-beat approval).
7. `assemble` — Remotion annotation/caption plane keyed to word timestamps,
   treatment pass, credits from sidecars → clean master. **GATE: ship.**

Swaps at any later date: drop the new file in `media/`, rerun compile —
only that slot recompiles.

## Converting an existing video (physics/ doodle & brownblue folders)

`python3 scripts/vox_convert.py physics/<slug>` → `reels/vox-<slug>/` with the
source narration, mp3 references, and measured durations carried per beat, every
visual re-planned: heuristic shot types (all `needs_review`), a conversion
SHOTLIST (old visual → assigned type), and a per-reel `vox_scenes.py` scaffold
that `vox_run.sh` picks up automatically. Old Manim scenes are NOT ported —
convert first, then let the QC gates audit only what survives. Narration is
per-beat `keep` (reuse mp3, free) or `rewrite` (Vox-register rewrites are
expected — regenerate only those beats with `generate_audio.py --only`).

## Test fixture

`reels/vox-electoral-college/` — ~133s excerpt recreation of Vox's Electoral
College explainer (transcript clock, `vox/` frames as ground truth), every
shot type exercised. Rerun `vox_compile.py` on it after changing this skill
or the scripts.
