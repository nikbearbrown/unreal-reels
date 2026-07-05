---
name: vox-explainer
description: >
  Vox-style mixed-media explainer videos — a PRODUCTION COMPOSITING PIPELINE,
  not a previz renderer. Voiceover (ElevenLabs) or a music bed is the master
  clock; the film is a composite of Manim motion-graphics fragments, Ken Burns
  animation over stills (archival or FLUX/nano-banana), AI video clips
  (Higgsfield/Hailuo/Seedance), public-domain footage, and a Remotion
  annotation plane (REMOTION.md) — all unified by the editorial newsprint treatment
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
   `actual_duration_s`; then `scripts/vox_align.py` (REMOTION.md) writes the
   word clock `mp3/words.json`. GATE 0: audio lock. Credits are
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
- Conform at ingest: scale/crop → duration ladder (retime ±5% exact; SHORT
  clips SLOW to fit — never freeze, i2v motion is usually too fast anyway,
  loud warning past 3× — LONG clips trim the tail, so key action goes early)
  → treatment per source. Rebuild recompiles ONLY slots whose input hash
  changed, then re-concats. `scripts/vox_compile.py` implements this.
- The png in a FOOTAGE slot is both the placeholder and the i2v seed; the mp4
  is the upgrade. Stills + Ken Burns carry most beats; AI video where motion
  earns it (~5s beats sit in the i2v sweet spot).
- Provenance sidecar (`<beat>.source.txt`: URL, license, credit) required on
  `archive` slots → auto-credits block. Real people/events → real archives.
- Annotations, captions, and the `--review` burn-in (global TC + beat id +
  beat-local clock + slot status) live on the assembly overlay — never baked
  into `clips/`. Clean master = same assembly, no flag.

## The pantry law (`scripts/vox_pantry.py`)

**THE COMMAND WORD: when the user says `pantry`, run the intake on the
current reel immediately** — copy pantry/ media to where it belongs, strip
any audio, rename to slot names for compositing (length conforms to the beat
at compile: the slow-to-fit ladder). Then reconcile the source axis (generated
media of real people → `source: ai` + disclosure sidecar) and report.

Raw finds never go straight into `media/`. They land in `reels/<slug>/pantry/`,
prefixed with their beat id, already RESTORED: nanobanana (via Higgsfield)
restoration pass — WARMONO for period images, NATGEO for modern ones
(`aspects/stock-styles.md`) — and upscaled to survive the Ken Burns crop.
Then one command does the mechanical rest:
`python3 scripts/vox_pantry.py reels/<slug>` — strips audio from video
(narration is the only voice on the timeline), crops non-16:9 DOCUMENT scans
to 16:9 anchored so the title survives (verify by eye), renames everything to
`media/<beat>.png|.mp4`, and writes sidecar stubs (ai/Higgsfield assets get
the disclosure line). It warns on clips shorter than their beat, undersized
stills, and source-axis contradictions. After intake: set `shot.focus` per
still, fill the sidecars, rerun `vox_run`.

## The Manim graphics library (`manim/vox_graphics.py`)

`IsotypeDotGrid` (count-up reveal, lag_ratio 0.003–0.01, duration = the
beat's audio window), `IsotypeFraction`, `StateCardPair` (slate-teal cards,
serif labels, figure lines), `QuoteCard` (highlighter sweep timed to words),
`LabelChip`, hand-drawn `AnnotationRing`/`StrikeX` strokes. Transparent or
newsprint-ground renders at beat duration:
`manim -qh --fps 24 vox_graphics.py <Scene> -o <beat>.mp4`. Counts are claims
— `viz.note` records what to verify before render.

## The equation tangent (rule owner: `aspects/explainer/brownblue/reference/equations.md`; lecture rendering: `brutalist/EQUATIONS.md`)

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
- Zone 5 is the claim the equation COMMITS you to: a contestable value
  judgment for value-laden equations, the physical commitment for physics
  ("energy comes only in these steps"). Optional only for pure bookkeeping;
  simple equations may merge it into zone 2's sign-as-claim (the owner's
  merge rule), but the commitment must be spoken somewhere in the bracket.
- The bracket's narration ends with a re-entry cue handing back to the main
  argument — or the immediately following beat's opening line does that work
  explicitly.
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
2. `factcheck` — BEFORE any money or rendering: every factual claim in
   narration, viz data, and card copy gets verified — against the source
   chapter, primary sources, and independent computation of every number —
   and written to the reel's `FACTCHECK.md`: claim | verdict (✓ / minor /
   WRONG) | source/derivation | fix if needed. Editorial flourishes are
   labeled as such, simplifications defended or reworded. vox_run REFUSES
   to render without FACTCHECK.md (Gate F; `VOX_FACTS=0` for previz only).
   Regenerate whenever narration or viz data changes. **GATE: claims hold.**
3. `audio` — ElevenLabs per beat, measure, lock. **GATE: hear it.**
4. `run` — `bash scripts/vox_run.sh reels/<slug>` — THE FULL MACHINE PASS,
   one command, free/local: Gate A (static check) → render every pending
   Manim scene to the measured durations → Gate B (pixel layout audit) →
   slot → outro law (branded closing card) → compile `--review`. The result
   is ALWAYS a full watchable video: motion graphics and outro finished,
   slates ONLY in slots that are yours (archive/ai media per SHOTLIST).
   **GATE: watch the cut — timing, pacing, beat-to-visual map.**
5. `stills` — FLUX / nano-banana plates for ai slots (cheap — batch with
   per-step go-ahead); download archive picks for archive slots (free) with
   `.source.txt` sidecars; set `shot.focus` per still. Rerun `vox_run` —
   only changed slots recompile.
6. `video` — Higgsfield i2v only for beats where the still + audio demand
   motion (the expensive step, last, per-beat approval).
7. `assemble` — Remotion annotation plane keyed to word timestamps +
   auto-credits from sidecars → clean master. **GATE: ship.** Spec and rule
   owner: `REMOTION.md` (this folder). Captions are NOT plane scope —
   sidecars per the caption policy; karaoke is a separate human-invoked
   derivative (`vox_karaoke.py`, spec'd in REMOTION.md). (Not yet built —
   until it lands, DOCUMENT/COMPOSITE annotation beats degrade gracefully
   to clean plates.)

Swaps at any later date: drop the new file in `media/`, rerun compile —
only that slot recompiles.

## The Shorts law (`scripts/vox_short.py`)

A 9:16 Short is a DERIVATIVE CUT, never a re-edit: drop the beats that don't
earn vertical time (documents, the bear outro — the bear belongs to the 16:9
master), end on a SILENT branded card the viewer reads (@handle, terracotta
hairline, the Next: line inherited from the dropped outro), stay under the
3:00 Shorts cap.

THE COMPOSITION LOGIC: 16:9 lays out SIDE BY SIDE; 9:16 stacks TOP AND
BOTTOM. Portrait relayouts re-band the same content vertically — they never
merely scale the landscape composition down. (Machinery note: vox_graphics
syncs frame_width to the real pixel aspect at import — Manim CE does not —
so portrait scenes truly get the 4.5×8 frame they compose for.) `python3 scripts/vox_short.py reels/<slug> --drop B14 B16`
writes `short/` with symlinked slots (nothing re-renders), the endcard, and
a 9:16 `fit: pad` sheet — the film letterboxes on the newsprint ground, so
graphics beats read as native portrait layouts. Then compile `short/` with
`--height 1920`. Playlist metadata: `playlist` names the style series
("Quantum Mechanics (Vox Style)" — viewers choose their register),
`playlist_short` is "Shorts".

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
