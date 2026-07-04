# Slide archetypes — the deck grammar

Nine recurring slide shapes, derived from the 39-slide fairness deck
(`lectures/fairness-metrics-and-impossible-choices/Chapter 7 - Fairness Metrics.dc.html`).
`templates/archetypes.py` emits each one verbatim in that deck's brutalist dialect.
Color only via `--nu-*` tokens; type via `--font-sans` (Lato); data numbers via
`--font-mono`.

Every slide is a top-level `<section data-label="…" data-speaker-notes="…"
style="…inline…">`. Two attributes are load-bearing and never optional:
`data-label` (beat identity for deck-lecture) and `data-speaker-notes` (the seed
the whole narration expands from — a blank note = a silent slide).

| archetype | ground | signature elements | plan fields |
|---|---|---|---|
| `title` | black, 10px red bar | eyebrow → h1(104) → rule → subtitle | eyebrow, headline, subtitle |
| `section` | **red** | "Part N" eyebrow → h2(108) → subtitle | part, headline, subtitle |
| `statement` | black | eyebrow → h2(72) → body | eyebrow, headline, body |
| `concept` | white | eyebrow → h2(66) → rule → red-marker bullets | eyebrow, headline, bullets[] |
| `equation` | white | eyebrow "Metric NN · Equation" → h2 → subhead → dark `data-tex` box → plain-terms + values-claim cols | eyebrow, headline, subhead, tex \| texs[]+tex_labels[], plain, values_claim, tangent{} |
| `example` | white, left red bar | eyebrow → h2(62) → 1–2 prose paragraphs | eyebrow, headline, paragraphs[] |
| `chart` | white | eyebrow → h2(50) → `[data-chart="NAME"]` mount | eyebrow, headline, chart, chart_w/h |
| `figure` | white | eyebrow → h2 → centered `<img>` → caption | eyebrow, headline, src \| asset_ref, caption, alt |
| `close` | black, 10px red bar | eyebrow → h2(84) → rule → body → next | eyebrow, headline, body, next |

## Notes on specific archetypes

**equation** carries the EQUATIONS.md tangent data in `slide["tangent"]`
(`lhs`, `rhs`, `claim`, `glossary[]`, `example{}`, `values_claim`, `reentry`).
The *slide* renders zones 1 (dark TeX box), a short 2 (plain-terms), and 5
(values-claim). The *tangent* — deck-lecture's `S05T`-style beats — consumes the
rest (LHS/RHS split, Role glossary, worked example). Emitting this at plan time is
what makes the equation tangents reproducible instead of hand-authored.

Multi-equation slides (equalized odds has two): pass `texs: [...]` +
`tex_labels: [...]` instead of a single `tex`.

**chart** only places a `[data-chart="NAME"]` mount. The drawer for `NAME` is
`assets/charts/NAME.drawer.js` (the lecture-assets drawer contract), folded into
the deck's `data-dc-script` registry by `emit_deck.py`. The mount's presence is
exactly what makes `extract_slides.py` tag the beat `visual_mode=live`, so
deck-lecture keeps it live (no iframe, no doodle substitution).

**section** dividers are rendered natively by deck-lecture (SectionCard), so keep
them to a Part label + headline + one subtitle line.

**figure** vs **chart**: a figure is a static asset (SVG/PNG/JPG) placed as an
`<img>`; a chart is live D3. Prefer chart when the data should animate or the
encoding is the point; prefer figure for diagrams already rendered in the pool or
the book.

## Palette (enforced by verify_deck.py)

One red `#C8102E`, warm inks, grays. **No blue, ever.** Raw hex outside the
`--nu-*` set is flagged. Numbers in data contexts (equation worked examples,
metric tables) use `var(--font-mono)`; prose numbers stay Lato (a regex can't tell
a year from a data value, so mono is applied by the template only where a field is
known to be data, never blanket).
