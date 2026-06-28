# Lyrics → scene — how to author the per-block scenes

`media_prompts.py` only assembles `scene + style → prompt`. The **scene** is the
creative work, and it must be *authored*, not sliced from the lyric. A lyric line is
inert until interpreted: "you call his way / One wish granted" is not a picture. This
file is the method for turning a block's lyrics into a scene worth generating.

## The one rule

**Never echo the lyric.** Do not illustrate the words literally unless the literal
image is already metaphorically rich. Translate, don't restate. If your scene could be
reconstructed by reading the lyric back, it's wrong.

## Decompose before you write (the interpretation stack)

For each block, resolve these layers *in your head*, then write one dense scene line:

1. **Literal** — what's named (a fisherman, a fish, a castle).
2. **Emotional register** — one word (dread, awe, greed, resignation).
3. **Metaphor** — what the moment *stands for* (the sea darkening = mounting greed).
4. **Kinetic** — still / slow / building / violent. Instrumental + pause blocks are
   their own beat: hold a frame, let stillness speak.
5. **Visual (shot grammar)** — the tokens an image/video model actually uses:
   - **Framing**: extreme wide / wide / medium / close-up / extreme close-up / aerial / low-angle / POV
   - **Camera move**: static / slow push-in / pull-back / tilt / crane / handheld drift / whip-pan
   - **Light**: hard or soft, direction, a color temperature or accent (cold key, warm rim, underlight, backlit silhouette, god-rays)
   - **Palette accent**: the one color that carries the beat (a single gold glow against black water)
6. **Continuity** — does this block CONTINUE the prior look or deliberately BREAK it?
   Keep one world; break the look only at real turns (e.g. the storm climax).

## Flatten to ONE line

Output a single comma-separated clause in this shape (this is what feeds the tool):

```
<framing>, <subject doing something specific in space>, <light>, <palette accent>, <camera move>
```

The global look (artist style, grade, aspect, profile) lives in `--style`, appended to
every prompt — don't repeat it per scene. Example flatten:

- weak (echoes lyric): `the fisherman caught a magic fish`
- strong (authored scene): `extreme close-up, a weathered hand lifting a faintly-glowing
  fish from dull shallow water, hard cold side-light, a single warm rim on the fish
  against steel-grey, slow push-in`

## Literal vs abstract

- **Literal lyric** (objects, places): shoot the *subtext*. The object is a symbol —
  ask why this object, and frame that.
- **Abstract lyric** (states, concepts): anchor in ONE concrete physical image that
  embodies it and commit. Don't try to draw the concept; draw an instance of it.
- **Silence / instrumental**: stillness as its own beat — a held frame, a slow drift,
  the emotional aftertaste of the last line.

## Where this lives

Author scenes into `scenes.json` (`{"scenes": {"B01": "..."}}`), one per block, then run
`media_prompts.py --scenes scenes.json --style "<your look>"`. Edit `scenes.json` and
regenerate freely — it's the single source of the creative pass.

(Adapted from standard music-video interpretation grammar — Goodwin's
amplification/disjuncture/illustration triad, Vernallis on edit grammar — minus the
live-action production notes, which don't apply to generated media.)
