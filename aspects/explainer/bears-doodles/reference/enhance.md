# Enhance — the optional photoreal/asset layer

`enhance` is an **optional, suggest-only** pass. It never generates, never edits a
scene or beat sheet, and never forces an asset into a video. Most beats stay pure
Manim. It exists for the few moments where a real-looking asset teaches better than
flat-doodle geometry — and it keeps those assets quarantined so the house style
stays intact.

Run it with `scripts/enhance_suggest.py <video-folder>`. It writes one file —
`<folder>/enhance/Enhance.md` — listing each candidate beat, why it was flagged, the
suggested asset, a ready-to-paste Higgsfield command, and the target filename in
`enhance/`. The human reads it, generates what helps (Higgsfield / Midjourney /
Illustrae), vets it, and drops the asset into `enhance/`. Even rough generations are
useful for ideation.

## The base architecture (unchanged)

Bear's Notes videos are narration-driven Manim animations. Voiceover is generated
first (ElevenLabs, cloned voice); every visual beat is timed to its audio duration.
Manim renders the silent scene; `assemble.py` muxes the audio in afterward. The base
visual layer is **always** Manim — geometry, text, arrows, color-coded dots, in the
doodle aesthetic (white background, bold strokes, `Shadows Into Light` font, muted
palette).

## When other assets get mixed in

Not every beat is a geometric abstraction. Some narration names a recognizable
physical thing the viewer must identify — a neuron, a bacteriophage, a satellite, or
the human behind an idea (Planck, Gödel). Manim can't draw these convincingly, and a
bad schematic undermines the teaching. Three asset types fill the gap:

1. **PNG still** — loaded in Manim via `ImageMobject`. For a named physical object
   that must look like itself. Bio objects read best in a diagrammatic style
   (Illustrae / Midjourney diagram mode); phenomena can be photoreal.
2. **Short clip (MP4 overlay)** — overlaid on the Manim render at a beat's timestamp
   by `composite_doodles.py`. For hook beats and short scene-setters (e.g. ~4–5s of
   an invented period-scientist at a chalkboard).
3. **Pure Manim geometry (default)** — handles every conceptual/relational beat:
   process, relationship, comparison, quantity. Color carries meaning; colorblind-safe
   pairs enforced.

## The decision rule

```
Does the narration name a real thing the viewer must RECOGNIZE
(a physical/biological object, or a named scientist)?
  YES → enhance suggests an asset (still / clip / Soul-ID character moment)
        human generates → vets against the style/quarantine rules → drops in enhance/
  NO  → draw it in Manim geometry
        is it a hook beat? → optional scene-setter doodle clip at assemble time
```

## Soul ID — copyright-safe scientists

For a recurring scientist, train a Higgsfield **Soul ID** once (an invented but
*consistent* face — `higgsfield soul-id`). It dodges the three failure modes of a
photoreal real person at once: no real-likeness/copyright murk, no uncanny "wrong
face," and the same character can recur across shots (a still here, a 5s chalkboard
clip there). Attach the Soul ref to the `generate create` commands in `Enhance.md`
(the exact ref flag is shown by `higgsfield generate create --help`). Check cost
first (`higgsfield generate cost`); video models cost more than stills.

## The quarantine amendment to the style contract

The base **doodle library** stays style-locked: white/transparent background, bold
black outline, flat muted color, no photorealism. Assets that fail that check are
rejected from the library regardless of accuracy.

**Enhance assets are the explicit exception.** They are allowed to be photoreal, and
they live *only* in each video's `enhance/` folder — never in the shared doodle
library. To keep a photoreal insert from clashing with the flat-ink doodles, give it
a bridging treatment: a hand-drawn frame and/or a duotone in the channel palette, so
it reads as intentional rather than pasted-in. This is a suggestion per asset, not an
enforced transform.

## How an asset wires back in (after it's made and vetted)

- **Still (PNG):** `ImageMobject("enhance/<file>.png")` at the beat; animate
  move/scale/fade. Transparent or white background; must survive a move/scale/fade test.
- **Clip (MP4):** name it for its beat; `composite_doodles.py` overlays it at that
  beat's window — the same path the optional doodle overlays already use. Manim never
  ingests mp4.
- Nothing here is required to ship: the `assemble` master is complete on its own.
