# Explainer — learning & explainer videos

The teaching aspect. Turns a **concept, chapter, or topic** into a short explainer — built from
clear visual beats, progressive disclosure, and label-free figures/doodles with text added as
crisp overlays (never baked into the image).

## What's different from the base engine

- **Clarity over spectacle.** Cognitive-load discipline: one idea per beat, build complex ideas
  in steps, give a built-up idea the time it needs (a step can run longer than a story beat).
- **Labels, arrows, equations are overlays, not image content** — image models render text as
  gibberish, so figures are generated label-free and annotated in Remotion on top.
- **Two visual modes:** a minimal **doodle/sketch** look (a trained style LoRA) for animatics and
  STEM icons, or photoreal/diagrammatic for richer explainers. Look is a swappable preset.

## Authoring → `beat_sheet.json`

Concept → scope (what deserves a video) → ordered explanatory beats (hook → mechanism → synthesis),
each with a label-free `image_prompt` and the overlay text kept in a separate field for Remotion.
Then the shared stages run, with the overlay stage adding labels/arrows/equations.

## The two explainer skills

- **`bears-doodles/`** — MinutePhysics template: progressive-disclosure line art on white,
  Shadows Into Light, 1–5 min, optional SVG/doodle overlays.
- **`brownblue/`** — 3Blue1Brown template: pure Manim (no overlays, ever), EB Garamond,
  blue+brown palette (dark canvas default), Bear Brown voice, length derived from the
  pedagogical arc (concrete-before-abstract, mystery openings, transform-don't-cut).
  Reuses the bears-doodles pipeline scripts; its own constitution lives in
  `brownblue/reference/pedagogy.md` + `style.md`.

## Source skills to fold in

From the existing work: **`bears-doodles`** (MinutePhysics-style progressive-disclosure sketch
animation; its `generate_audio.py` is the shared audio stage), **`bears-doodles-scout`** (mine a
textbook for video candidates), and **`cajal-video-tutorial`** / **`cajal`** (figure intelligence —
which figures should exist, colorblind-safe SVG/diagram rendering). Style-LoRA training (a doodle
look) lives with the optional fal.ai path.

> _Mapping to confirm/adjust:_ Bear to decide whether the doodle-LoRA training tools and the
> figure/SVG rendering (cajal) live here under Explainer or in a shared `scripts/` style module.
