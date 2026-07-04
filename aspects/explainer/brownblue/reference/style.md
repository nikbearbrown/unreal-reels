# Brown Blue — Series Identity & Setup

Locked defaults. A video may override a value in its `beat_sheet.json`
`metadata`, but these are the series standard. Design discipline is inherited
from the lecture constitution (`brutalist/DESIGN.md`) — every mark earns its
place, minimal tokens, one emphasis at a time — with the type system swapped
to **EB Garamond** and the palette swapped to the two hues the name promises.
Where that file says "no blue, ever," it is talking about lecture videos;
brownblue is the sanctioned exception, in its own sandbox.

## The typefaces

Exactly three, by role:

| Role | Typeface | Where |
|---|---|---|
| **Display + body** | **EB Garamond** | titles, labels, captions, on-screen prose — everywhere Lato/Inter serve in lectures |
| **Math** | LaTeX via `MathTex` (Computer Modern) | every equation — CM's serifs sit naturally beside Garamond |
| **Numbers / data** | **JetBrains Mono** | standalone numerals, %, ratios, axis ticks *outside* MathTex |

- EB Garamond: [fonts.google.com/specimen/EB+Garamond](https://fonts.google.com/specimen/EB+Garamond).
  Install locally AND drop `EBGaramond-Regular.ttf` + `EBGaramond-SemiBold.ttf`
  into each video's `fonts/` so `Text(..., font="EB Garamond")` resolves on any
  render machine. Never reference the font by name and hope — the Inter bug.
- Weights: Regular for body/labels, SemiBold for titles. No italic for
  emphasis on screen (color is the emphasis channel); italic is allowed for
  book/paper titles only.
- No handwriting font anywhere in this series.

## The two named styles

`metadata.style` selects one. Default is `dark`.

### `dark` (default — the 3b1b-native look)

```
--canvas:    #16161D   near-black with a breath of blue
--ink:       #ECE6D8   warm parchment off-white — body, labels, axes
--blue:      #58C4DD   THE OBJECT — the thing being studied
--brown:     #CD853F   THE CONTRAST — the second object, the before-state
--highlight: #F0E442   transient emphasis only — "look here," then gone
--secondary: #8A8780   dimmed labels, earlier states, scaffolding
--hairline:  #3A3A44   grid lines, faint rules
```

### `light` (white-canvas alternate)

```
--canvas:    #FFFFFF
--ink:       #2a1a0e   warm near-black (never pure #000)
--blue:      #0072B2   colorblind-safe dark blue — the object
--brown:     #8B5A2B   the contrast
--highlight: #0072B2   on white, blue doubles as emphasis (yellow fails on white)
--secondary: #545454
--hairline:  #D4D4D4
```

## Color roles (both styles — the roles ARE the palette)

- **Blue** = the mathematical/conceptual object under study. The vector, the
  function, the distribution. One blue thing at a time.
- **Brown** = its foil: the second series, the before-state, the comparison
  object. Never decoration.
- **Highlight** = transient. It appears on the element the narration is
  pointing at *right now* and fades when the sentence ends. Never two
  highlights at once.
- **Ink/secondary/hairline** = everything else. No red (that's the lecture
  brand), no green, no rainbow. Categorical data beyond two series is a sign
  the beat is overloaded — split the beat instead of adding a hue.

## Motion

- **Transform, don't cut.** Objects persist and morph
  (`Transform`, `ReplacementTransform`, `.animate.apply_matrix`, `ValueTracker`
  sweeps). A hard cut is allowed only at act boundaries (`CUT` beats).
- Easing: Manim's default `smooth` — no bounce, no overshoot, no
  scale-on-mount.
- Draw-on for new curves/axes (`Create`), write-on for text (`Write`), fade
  for exits. Camera zoom (`ZOOM` beats) reserved for scale-shift moments.
- Give a transformation the time the narration gives it: animation `run_time`
  comes from the beat's real MP3 duration, never a guess.

## Voice — Bear Brown

- ElevenLabs voice ID: **`TyW6NH39JcFb5M3xdIIk`** (the Bear Brown clone;
  override via `metadata.voice_id`).
- Settings: `eleven_multilingual_v2`, stability `0.80`, similarity_boost
  `0.75`, style `0.00`, speed `0.92`, output `mp3_44100_128`.
- Register: calm, unhurried, conversational — the discovery voice ("what if
  we tried...", "notice what just happened"), never lecture-hall.
- No background music.
- Key via `ELEVENLABS_API_KEY` env var — never in a file, never committed.

## Opening (every video)

First beat is `INTRO`. ElevenLabs narrates:

```
Bear's Notes

<title>
```

(paragraph break = short pause). Visually: canvas in the video's style,
title in EB Garamond SemiBold ink, a thin brown rule, a small blue accent
mark. No mascot, no logo animation — the restraint is the brand.

## Closing (every video)

Last beat is `OUTRO`, and it does double duty as the **boundary beat**
(pedagogy.md §7): the narration hands the viewer the one exercise or question
to try on their own, then:

```
Thanks for watching <title> — more at youtube dot com, slash, at Nik Bear Brown
```

Visually: the finished final scene stays on screen; title parks in the upper
margin band, ink at 70%. No channel URL on screen (it's in the narration and
description). Nothing else.

## Beat-sheet metadata block (paste into the skeleton after `new`)

```json
{
  "series": "Brown Blue",
  "channel_url": "youtube.com/@NikBearBrown",
  "voice_id": "TyW6NH39JcFb5M3xdIIk",
  "style": "dark",
  "text_font": "EB Garamond",
  "accent_color": "#58C4DD",
  "forbidden_color": "#C8102E"
}
```

(`forbidden_color` is the lecture red — it must never appear in a brownblue
frame; the layout audit can grep for it. For `style: light`, set
`accent_color` to `#0072B2`.)

## Aspect ratio

Both aspects always ship: 16:9 master + 9:16 Short from the same scene and
audio, via `bn_layout.py` (`is_portrait()` + a `LANDSCAPE`/`PORTRAIT` constant
set). No landscape-only scenes — that debt sank the Manim library once already.

## Audit before showing a render

1. Canvas, ink, blue, brown match the named style; **no red anywhere**; at
   most one highlight on screen at any instant.
2. All text is real EB Garamond loaded from `fonts/`; numbers outside MathTex
   are mono.
3. Every state change inside a scene is a morph, not a cut.
4. Text never overlaps or leaves frame (`manim_layout_audit.py` exit 0),
   both aspects.
5. Every label answers a question the viewer has *at that beat* — else cut.
6. **Curve labels sit in empty space, never on a plotted curve.** The layout
   audit now catches this: `manim_layout_audit.py` flags **TEXT/CURVE** — any
   label whose centerline is crossed by a stroked curve/line/axis (ported from
   ai1-cli's SVG `svg-layout-audit.mjs`). It is a warning by default; run
   `--curve-strict` to make it a hard error. Since brownblue curves are analytic
   (you know `f(x)`), place each curve label at a data point where both curves
   are far away, using the `_clear_label(x, y, text, ...)` pattern (place at
   `ax.c2p(x,y)`, clamp into the plot region). Between the numeric clearance
   check and the audit, no label should ship sitting on a graph.
