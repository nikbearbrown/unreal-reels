# DESIGN.md — Lecture-Video Visual Constitution

*Design system for unreal-reels narrated lecture videos (the `deck-lecture` skill).
Adapted from the `ai1-cli/brutalist` constitution — kept only what serves a moving,
narrated deck. When this file and a component disagree, this file wins.*

## Governing principle

Every mark earns its place by serving the spoken point. Typography and motion do the
work; color does not. **One red. White canvas. Grays are the only other neutral.**
Nothing is decorative until it has a reason to speak.

## The three typefaces

This project uses exactly three, by role:

| Role | Typeface | Where | Loaded |
|---|---|---|---|
| **Display** | **Lato** | the live HTML deck slides (titles, body) | by the deck's own CSS, inside its iframe |
| **Overlay / UI** | **Inter** | bullets, doodle labels, captions — everything we draw on top | local file `public/fonts/Inter-*.ttf` via FontFace (`src/fonts.ts`) |
| **Numbers / data** | **JetBrains Mono** | every numeral, %, decimal, ratio (60%, 0.8, 0.6/0.3) | family string w/ real OS-mono fallback (`MONO_FONT`) |

Rules: never reference a font by name only and hope it loads — load the file or use a
guaranteed fallback chain (the bug that made Inter render as generic `sans-serif`).
No handwriting font (no Shadows Into Light / Caveat). Numbers always go mono so data
reads as data.

## Color tokens

Six values. The complete palette. (Matches the deck's Northeastern red.)

```
--white:     #FFFFFF   canvas / slide background
--ink:       #2a1a0e   body, headings, marks (warm near-black, not pure black, never blue)
--red:       #C8102E   the one accent: brand, emphasis, the primary/“highlighted” data
--secondary: #545454   captions, dimmed/earlier bullets, axis + tick labels
--border:    #D4D4D4   hairlines only
--ochre:     #C8860E   decorative accent only (a rule/underline) — never body text
```

Role rules:
- **Red** = brand + the one data point of interest (the filled dots, the punchline bullet). It is *never* "danger/negative," never decorative, never a second series.
- **Grays** (`--ink`, `--secondary`) are the only neutral series. No second hue.
- **No blue, ever.** No rainbow chart palettes. (The blue dots were a bug — now red.)
- Live-slide D3 charts already follow the deck's brand; we don't override them.

## Motion

Tokens in `src/tokens.ts`. The whole video shares one easing.

- **Easing:** `Easing.bezier(0.2, 0.8, 0.2, 1)` — ease-out-quart. No bounce, no overshoot, **no scale-on-mount**.
- **Element entrance** (`ENTER`): ~10 frames (~320ms @30fps) — fade + small (≤36px) translate.
- **Stroke draw-on** (`DRAW`): ~16 frames — `pathLength=1` + `strokeDashoffset` 1→0.
- Captions: per-word karaoke, timed by forced alignment (not eased per word).

## The three-tier slide model

Each slide holds the live deck ~3.5s (read time), then shows one of:

1. **live** — slide has a D3 chart (`data-chart`): stays live the whole slide.
2. **doodle** — authored line-art sketch (red highlight, ink strokes), one element per narration line. `src/Doodle.tsx`.
3. **bullets** — auto-condensed headline takeaway + summary bullets, current emphasized, numbers in mono. `src/Bullets.tsx`.

Priority: doodle > bullets > live. Title slide, "Part N" dividers, and the close stay live.

## What this system never does

- No font referenced by name without a real load or mono fallback.
- No blue / no second accent hue / no rainbow series.
- No bounce, no scale-on-mount, no parallax.
- No handwriting font.
- No pure black (`#000`) for text — use `--ink`.
- No red for "danger/negative" in data.
- No ochre at body size.

## Audit before a render

1. Canvas `#FFFFFF`; text `--ink`; one red; grays as only neutrals; **no blue**.
2. Numbers are mono.
3. Overlays are real Inter (loaded from file), not a generic fallback.
4. Motion is ease-out-quart, fade + small translate only.
5. Every bullet/label answers a question the viewer has, or it's cut (annotation-removal test).
6. Doodle bars have a zero baseline; radius encodings use `scaleSqrt`.

*Source lineage: `~/Documents/Cowork/ai1-cli/brutalist/` (DESIGN.md, VIZ.md, SaulBass.md). This file keeps the parts that apply to narrated video and swaps the type system to Lato + Inter + JetBrains Mono.*
