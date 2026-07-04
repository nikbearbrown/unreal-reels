# Why Schrödinger's Cat Is Not About Cats — Manim Render Plan (Gate 4)

*Audio approved: 23 clips, 99.96s total. This plan describes the Manim master before rendering.*

## Deliverable

Render a 16:9 Manim master with:

- intro title card and outro text
- narration audio baked in via `self.add_sound`
- exact Manim visuals for quantum/mechanism beats
- dashed placeholder boxes for doodle beats
- no imported doodle mp4s; final doodle overlay happens manually in Rush/Premiere

Output target after render:

```text
/Users/nik/Documents/Cowork/Manim/why-schrodingers-cat-is-not-about-cats/media/videos/why_schrodingers_cat_is_not_about_cats/1080p60/BearsDoodlesVideo.mp4
```

## Beat Split

| Type | Beats | Count |
|---|---|---:|
| Intro/outro text | INTRO, OUTRO | 2 |
| Doodle placeholders | A00, A01, A05, A20 | 4 |
| Manim scenes | A02-A04, A06-A19 | 17 |

## Scenes

### INTRO

Show `Bear's Doodles`, title, and a small bear-marker placeholder. Duration comes from `mp3/timings.json`.

### Doodle Placeholder 1 — A00

Narration: Schrödinger helped invent quantum mechanics and used a cat to expose the weird claim.

Visual in master: dashed placeholder labeled:

```text
[doodle A00: Schrödinger + cat]
```

### Doodle Placeholder 2 — A01

Narration: cat in sealed box with random quantum trigger.

Visual in master: dashed placeholder labeled:

```text
[doodle A01: sealed box + trigger]
```

### Scene 3 — Cat-State Cards, A02-A04

Manim elements:

1. Two rounded state cards labeled `ALIVE` and `DEAD`.
2. Cards slide into a single central `superposition` card.
3. A box-open arrow selects one definite outcome.

Style:

- no harmed animal drawing
- `DEAD` is just an abstract card label
- `ALIVE` and `DEAD` in ink
- superposition card in accent `#5A5653`
- collapse/selection arrow in forbidden red `#C0392B`

### Doodle Placeholder 3 — A05

Narration: Schrödinger meant the picture to feel absurd.

Visual in master:

```text
[doodle A05: puzzled Schrödinger]
```

### Scene 5 — Real Superposition And Wavelength, A06-A10

Manim elements:

1. Small particle with ghosted possible positions.
2. Position line with spread-out wave packet.
3. Narrow packet linked to fan of many wavelengths.
4. Large-object scale comparison.
5. Cat / atom / tiny wavelength scale line.

Style:

- particle and axes in ink
- wave packet in accent
- tiny wavelength tick in forbidden red for contrast
- keep all labels inside safe area

### Scene 6 — Double Slit, A11-A14

Manim elements:

1. Electron source, two-slit barrier, detector screen, one dot.
2. Many dots accumulate into interference fringes.
3. One slit becomes blocked and fringes vanish into a single-slit spread.
4. Possibility wave splits through both slits, then lands as one dot.

Style:

- barrier/screen in ink
- wave in accent
- block marker in forbidden red
- dots deterministic using a seeded random generator

### Scene 7 — Materials And Transistors, A15-A19

Manim elements:

1. Electron cloud shared across atom dots.
2. Two atoms labeled `A` and `B` joined by shared electron cloud.
3. Atom lattice morphs into energy bands.
4. Band gap diagram becomes transistor symbol.
5. Transistor grid becomes a simple chip icon.

Style:

- atoms in ink
- electron cloud and bands in accent
- forbidden gap in red
- chip grid stays simple and centered

### Doodle Placeholder 4 — A20

Narration: internet cat videos depend on Schrödinger's imaginary cat.

Visual in master:

```text
[doodle A20: laptop cat video + sealed box]
```

### OUTRO

Keep final state or a clean ending frame, then show:

- title in upper safe margin
- `youtube.com/@NikBearBrown` in lower safe margin

## Implementation Notes

Create:

```text
why_schrodingers_cat_is_not_about_cats.py
```

Use existing Cowork patterns:

- read `mp3/timings.json`
- call `self.add_sound(...)` at beat start
- use `Text(..., font="Shadows Into Light")`
- use a fixed random seed for double-slit dots
- render with:

```bash
/Users/nik/ai/bin/python -m manim --flush_cache --disable_caching -qh why_schrodingers_cat_is_not_about_cats.py BearsDoodlesVideo
```

## Approval Gate

Approve this render plan to create and render the Manim master.
