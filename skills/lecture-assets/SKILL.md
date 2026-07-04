---
name: lecture-assets
description: >
  Stage 1 of the lecture pipeline: from a textbook chapter, compile a POOL of
  candidate visual assets — colorblind-safe SVG figures, live D3/HTML data
  visualizations, and doodle candidates — into lectures/[chapter]/assets/. The
  pool is deliberately over-generated and nothing is forced: the slide-deck skill
  (stage 2) picks from it, and unused assets are still useful elsewhere (articles,
  Substack, social). Use when the user types `assets`, `asset pool`, or asks to
  generate figures/charts/visuals for a chapter or lecture. Orchestrates cajal
  (figure intelligence + SVG), the ai-for-graphs / brutalist-d3 chart grammar, and
  scout (doodle candidates).
metadata:
  tags: assets, figures, dataviz, svg, d3, cajal, scout, lecture-pipeline
---

# Lecture Assets — build a candidate pool from a chapter

Pipeline: **chapter.md → [this skill] → slide-deck skill → deck-lecture video.**
This stage produces *possibilities*, not a finished set. Over-generate, tag, move
on. A figure that never reaches a slide is not waste — it is inventory.

## The one rule

**Nothing is forced.** Every asset is a `candidate` in the manifest. The deck skill
chooses; you never bend a chapter to use an asset, and you never require an asset
to appear. Breadth now, selection later.

## Where things go

```
<book>/lectures/<NN-chapter-slug>/assets/
  assets.json          single source of truth — every asset tagged
  cajal/               *-cajal.md figure-intelligence reports
  svg/                 colorblind-safe static figures (portable — reuse anywhere)
  charts/              live D3/HTML data visualizations (embed in a .dc.html deck, or rasterize)
  doodles/             doodle candidates (concept + one-line sketch note) for later animation
```

`assets.json` entry shape:

```jsonc
{ "id": "ch02-base-rate-icon-array",
  "kind": "figure|chart|doodle",       // figure=SVG, chart=live D3/HTML, doodle=candidate
  "concept": "base rates dominate positive tests",
  "source": "cajal | ai-for-graphs | scout | authored",
  "file": "svg/base-rate-icon-array.svg",   // or charts/… ; doodles carry a note instead
  "status": "candidate",
  "notes": "central chapter idea; icon array of 1000 people" }
```

## The moves (per chapter)

0. **Import the book's own figures first.** Many books already ship rendered
   per-chapter figures (SVG/PNG/JPG in an `images/` dir) — pre-vetted and on-brand.
   Pull them into the pool before generating anything new:
   → `scripts/import_book_figures.py <lecture_folder>` (copies `images/<chapter>-fig-*`
   into `assets/book/`, SVG preferred, titled from the chapter's "Figure N —" prompts).

1. **Read the chapter — and its own figure hints.** Many chapters already end with a
   `## Prompts` / figure list authored by the writer. Mine those first; they are
   pre-vetted candidates. Then add what the prose implies.
2. **Figure intelligence → SVG (cajal).** Run cajal's scan over the chapter → a
   `cajal/<chapter>-cajal.md` report of the figures that *should* exist (SCOPE +
   exclusions). Render the strong ones as static SVGs under `svg/`, following
   `reference/svg-style.md` (Okabe-Ito colorblind palette, 1pt strokes, white
   ground, zero-baseline charts, ARIA). Diagrams (Venn, partition, flow, cross-
   section, timelines) belong here.
3. **Data-viz → live D3 drawer (ai-for-graphs / brutalist-d3).** For every
   quantitative claim, pick the chart by the *data type and the question* (the
   ai-for-graphs chart-selection grammar), and author it as a **drawer** under
   `charts/`. Honest encodings only: zero baseline, `scaleSqrt` for radius, red =
   the one accent / primary series, grays as neutrals (per the brutalist DESIGN
   palette). No rainbow, no dual axes, no truncated bars.

   **The drawer contract (why: how stage 2 embeds live D3).** The slide-deck skill
   folds live charts into the deck's `<script data-dc-script>` registry as
   `this._drawers['<name>'] = (c)=>{…}` — no nested iframes (the deck-lecture
   render is already iframe-heavy). So the pool authors each chart as a drawer and
   derives the standalone page from it:
   → `scripts/new_chart.py <lecture_folder> --name <slug> --concept "…"` scaffolds
   `charts/<slug>.drawer.js` (the source of truth: a self-contained `(c)=>{…}` that
   draws into mount `c`, using `window.d3`) **and** `charts/<slug>.html` (a
   standalone page inlining the same drawer — for articles/social/rasterizing), and
   registers the asset. Edit the drawer, then `--sync` to regenerate the html.
   One chart, two artifacts, always in step. (Inside a deck the drawer also has the
   shared `_define()` helpers `RED, BLACK, N7…GOLD, D, FONT, clear, svgIn` in scope,
   but a self-contained drawer works in both places — prefer that.)
4. **Doodle candidates → scout.** Run scout over the chapter for
   progressive-disclosure sketch moments (the vivid scenes, the one-idea reveals).
   Record each as a `doodles/` candidate (concept + a one-line sketch note) the
   deck skill can later turn into a Doodle spec — don't animate here.

Write every produced (or proposed) asset into `assets.json` via `scripts/add_asset.py`.

## Reuse map (build nothing that exists)

| Need | Reuse |
|---|---|
| Figure intelligence + SVG style | `cajal` skill + its `svg-style.md` (mirrored in `reference/svg-style.md`) |
| Chart-by-data-type grammar, D3 patterns | `ai-for-graphs-a-practitioners-guide`, `brutalist-d3-x-claude` |
| Palette / typography / motion tokens | `unreal-reels/brutalist/DESIGN.md` |
| Doodle-worthy moment mining | `bears-doodles-scout` |
| Manifest | `scripts/add_asset.py` |
| Live-chart drawer + standalone page | `scripts/new_chart.py` (drawer contract for slide-deck stage 2) |

## Honesty / quality gate (before an asset joins the pool)

- Colorblind-safe (Okabe-Ito or red+grays); simulate protanopia/deuteranopia.
- Charts: zero baseline; proportional ink; `scaleSqrt` radii; one accent (red), grays otherwise.
- Every figure states one idea; the exclusion list is populated (cajal's rule).
- SVG carries `role="img"` + `<title>`/`<desc>`.
- Numbers set in mono (JetBrains Mono), matching the deck system.

## Not this skill's job

Selecting which assets make the lecture (that's the slide-deck skill), narration,
or animation. This skill only fills the pool.

## Worked target — chapter 02
`chapters/02-probability-uncertainty-and-the-confidence-illusion.md` →
`lectures/02-…/assets/` : base-rate icon array (figure), total-probability
partition (figure), calibration reliability curve (live D3 chart), plus doodle
candidates (the "99% accurate test that kills the patient", confidence that
doesn't move under shift).
