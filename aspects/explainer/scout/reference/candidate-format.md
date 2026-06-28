# Candidate Card Format

Every candidate uses this exact schema. The builder skill (`bears-doodles`) reads
these fields, so do not rename, reorder, or drop any. One blank line between cards.

## Template

```
## Candidate NN — <Title as a "Why ..." or surprising statement>
- Source: `<book>/chapters/<file>.md`
- Production mode: <Manim visualization | Doodle | Mixed>
- Hook: <one sentence — the tension/paradox, no visual required>
- Core idea: <one sentence — the mechanism that resolves the hook>
- Visual object: <the single thing on screen the whole video orbits>
- Manim move: <one verb from the move vocabulary in selection.md>
- Short-form fit: <Strong | Medium | Weak>
- Prerequisites: <comma-separated concepts the viewer must already have>
- Exclusions: <specific rabbit holes to NOT include — derivations, formalisms, edge cases>
- Score: <N>/10
```

## File header (top of vids/video-ideas.md)

```
# Bear's Doodles — <Book Title> Video Ideas
```

## Worked example (the standard to match)

```
## Candidate 01 — Why a Particle in a Box Cannot Sit Still
- Source: `quantum-mechanics-vol1/chapters/05-the-infinite-square-well.md`
- Production mode: Manim visualization
- Hook: The bottom of the box is not stillness.
- Core idea: Boundary conditions force the wavefunction to curve, and curvature means kinetic energy.
- Visual object: Standing half-wave trapped between two walls
- Manim move: compare
- Short-form fit: Strong
- Prerequisites: wave, boundary condition, energy
- Exclusions: no full derivation, no normalization, no Fourier expansion
- Score: 9/10
```

## Field notes

- **Title** — phrase as a "Why …" question or a counterintuitive claim. It is the video's spine and often the thumbnail line. Avoid textbook-section names.
- **Source** — exact relative path, backtick-wrapped, so the builder can open the chapter if it wants more.
- **Production mode** — `Manim` when geometry/curves/boundary conditions/equations must be exact (most QM diagram concepts). `Doodle` when the point is a metaphor or character (a balance scale, a sun, a stick figure). `Mixed` when a precise Manim core needs a doodle intro or metaphor cutaway. See selection.md.
- **Hook** — the line the narrator opens on. No visual. Creates curiosity in one breath.
- **Core idea** — the mechanism. Cause → effect, in the right order. This becomes the spine of the accumulation beats.
- **Visual object** — name the ONE thing. If you need two unrelated objects, it is probably two videos.
- **Manim move** — the dominant animation verb (see selection.md vocabulary). Signals the builder how the object behaves.
- **Short-form fit** — how cleanly it teaches as a short explainer, not how long it runs. Strong = one tension, one resolution, obvious visual (~1–2 min). Medium = needs setup or a few scenes (~2–3 min). Weak = don't build yet. "One-minute" is the style, not a cap; the builder sizes runtime to the concept (1 min floor, usually 2–3, up to 5).
- **Prerequisites** — what the viewer must already know. Long lists mean the concept is too deep for a self-contained short explainer (not merely too long).
- **Exclusions** — the discipline field. Specific, not generic. "no transmission-coefficient derivation, no WKB" beats "keep it simple."
- **Score** — integer /10 per the selection.md rubric. Order cards by this, highest first.
