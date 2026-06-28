# Selection: What Makes a Bear's Doodles Video

The scout's job is judgment. Most chapter material does not belong in a short
explainer. Keep only concepts that pass the bar below.

**On length:** "one-minute" is the *style* (MinutePhysics), not a duration. A
Bear's Doodles video runs from 1 minute to 5, usually 2–3. Teaching the concept
clearly always outranks hitting a target length — never reject or cram a concept to
fit 60 seconds. Length follows the concept; the bar below is about teachability, not
runtime.

## The unit is the concept, not the chapter

Triage by **concept (high-assertion zone)**, never by chapter. A chapter yields
zero, one, or several candidates — all are correct outputs. Do not pad a thin
chapter to hit a count, and do not cap a rich chapter at one. The scout surfaces
every qualifying concept; **consolidation is the human's job at pick-time**, not
the scout's at detection-time. (This is cajal's Triage Unit Rule. Cajal's
"one video per chapter" is a downstream *production budget*, not a detection rule —
do not apply it here.)

## Step 1 — Find the high-assertion zones (cajal heuristics)

Read each chapter and flag the concepts where a claim is made that the prose alone
cannot make a reader *see*. Three detectors, applied per concept:

- **MC — Mechanism / process complexity:** a described process with 3+ interdependent steps or interacting parts (a cascade, a sequence, a feedback loop). The text asserts *how something works*.
- **VG — Verification gap:** a structural, spatial, or hierarchical claim you cannot verify from text alone (a shape, a configuration, a before/after, a nesting). The text asserts *how something is arranged*.
- **PQ — Proportional / quantitative:** percentages, ratios, magnitudes, distributions. The text asserts *how much*.

A high-assertion zone is a candidate *figure*. It becomes a Bear's Doodles *video*
candidate only if it also passes Step 2.

## Step 2 — Video-candidate test (does motion carry the teaching?)

The operative question for every zone: **does the learner need to understand HOW
the transition happens — the mechanism of change itself — or just the before/after
states?** If the mechanism, it's a video. If the states, a static figure is as good
or better (and self-paced) — drop it from the slate.

Flag as a video candidate if any apply:

1. **Transition mechanism is the learning target** — the student must see the change unfold, not just the endpoints. (A wavefunction curving; a packet spreading.)
2. **Three or more sequential causal stages** that build in a direction that matters.
3. **Cyclical process where return-to-start is the concept**, not just the states within it.
4. **Transformation below direct observation** — too fast, slow, or small to watch; the viewer would otherwise have to mentally simulate it.

Do **not** flag a concept just because it has a time element, is complex, or looks
impressive in motion. Motion that adds no instructional meaning adds cognitive
load, not learning — that concept is static-sufficient and is not a candidate.

## The bar: one tension, one resolution

A keeper has:

1. **A single tension** — a paradox, a "that can't be right", a violated intuition. Statable in one sentence with no visual. (This becomes the Hook.)
2. **A single resolution** — one mechanism that dissolves the tension. (This becomes the Core idea and the accumulation arc.)
3. **One visual object** the whole video orbits. (The Visual object.)
4. **≤6 elements per scene** (not per video). A 1-minute idea is one or two scenes; a 3-minute idea is several. The cap is on simultaneous on-screen clutter, never on total length.
5. **Self-containment** — understandable without the chapter and without prior videos.

If a concept needs a derivation, three prerequisites you must first teach, or two
unrelated objects, it is too big. Either narrow it (pick the one surprising slice)
or reject it.

## Short-form fit

How cleanly the concept teaches as a short explainer — independent of exact runtime.

| Rating | Meaning | Typical length |
|---|---|---|
| **Strong** | One tension, one resolution, an obvious visual, ≤3 prerequisites the viewer plausibly has. Build it. | ~1–2 min |
| **Medium** | Needs a little setup, or one prerequisite is shaky, or it takes a few scenes to land. Buildable; tighten first. | ~2–3 min |
| **Weak** | Multi-part with no single spine, derivation-dependent, or no clean visual. Do not build yet; note why. | — |

A Strong rating does not mean "short" and a Medium does not mean "too long." It
measures whether the concept resolves cleanly, not how many minutes it runs.

## Score rubric (/10)

Add the points; cap at 10.

- **Surprise / "aha" (0–3)** — how counterintuitive the hook is. A genuine "wait, what?" scores 3.
- **Visual obviousness (0–3)** — how directly the idea maps to one drawable object that moves. If you can see the animation immediately, 3.
- **Self-containment (0–2)** — can it stand alone as a short explainer with common prerequisites? Fully, 2.
- **Pedagogical payoff (0–2)** — does landing it fix a common misconception or unlock later material? Big payoff, 2.

8–10 = build soon. 6–7 = build after tightening. ≤5 = shelve.

## Production mode

- **Manim** — geometry, curves, boundary conditions, energy levels, probability densities, equations as labels. Anything where being *exactly right* is the teaching. Default for QM diagram concepts. Free to render, pixel-precise.
- **Doodle** — the teaching is a metaphor or a character: a balance scale for a tradeoff, a sun drawing itself in, two electrons refusing to share a seat. Loose, intuitive, napkin-art.
- **Mixed** — a precise Manim core with a doodle intro or a metaphor cutaway (e.g. a doodle "ball vs. wall" cold open, then a Manim wavefunction). Mark Mixed only when both registers genuinely earn their place.

When unsure between Manim and Doodle: if a wrong curve would teach the wrong physics, it's Manim. If the shape is just a vibe, it's Doodle.

## Manim move vocabulary

The dominant animation verb for the visual object. Pick the closest one.

| Move | The object… |
|---|---|
| `compare` | two states shown side by side, one right / one forbidden |
| `scan` | a value sweeps across a region (energy, position, time) |
| `rotate` | spins / orbits / turns on an axis (Bloch sphere, vector) |
| `accumulate` | dots or pieces pile up into a pattern (interference fringes) |
| `morph` | one shape continuously becomes another (orbit → cloud) |
| `split` | one thing separates into two (level splitting, antisymmetry) |
| `transform` | a quantity sharpens while its partner blurs (uncertainty gauges) |
| `slosh` / `spread` | a packet widens, disperses, or oscillates |
| `duplicate` | a copy is created matching the original (stimulated emission) |
| `collapse` | a superposition / coherence decays to one outcome |
| `decay` | amplitude falls off exponentially (tunneling tail) |
| `trace` | a path or curve is drawn out over time |

If none fit, name the verb plainly — the list is a guide, not a cage.

## Exclusion discipline

The `Exclusions` field is what protects the runtime — it keeps the video as long as
the concept needs and no longer. For each candidate,
name the specific things a well-meaning builder would be tempted to add and must
not — the derivation, the formalism, the second example, the historical aside.
Generic ("keep it simple") is useless; specific ("no transmission-coefficient
derivation, no WKB") is the whole value. This field tells the builder exactly where
the cliff edges are.
