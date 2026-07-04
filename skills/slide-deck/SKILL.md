---
name: slide-deck
description: >
  Stage 2 of the lecture pipeline: turn a textbook chapter + its asset pool into a
  brutalist .dc.html slide deck that SELECTS from the pool and feeds deck-lecture.
  Emits the exact deck-stage.js dialect (one data-label/data-speaker-notes section
  per slide, KaTeX data-tex equations, live D3 data-chart drawers, red/ink/gray
  palette) that deck-lecture's extract_slides.py consumes. Phase-gated: a reviewable
  deck_plan.json is authored and approved BEFORE any HTML is emitted. Use when the
  user types `slide-deck`, `build deck`, `chapter to deck`, or asks to turn a chapter
  (+ assets) into a .dc.html lecture deck. Orchestrates the nine slide archetypes and
  the lecture-assets drawer contract.
metadata:
  tags: deck, slides, dc-html, chapter-to-deck, brutalist, d3, katex, lecture-pipeline, phase-gated
---

# Slide Deck — chapter + asset pool → brutalist .dc.html deck

Pipeline: **chapter.md → [lecture-assets] → [this skill] → deck-lecture → narrated mp4.**
This stage is the missing middle: it composes a finished HTML deck from the chapter
and the candidate pool, and hands a stage-3-ready `.dc.html` to `deck-lecture`.

## The one rule

**The plan is approved before the HTML exists.** A `deck_plan.json` — ordered
slides, each with an archetype, its content, and (critically) its
`data-speaker-notes` seed — is the single human gate. Emitting 900 lines of HTML is
mechanical; deciding the structure and the speaker-notes is the work. Fix it in the
plan, not the deck.

## The other rule — the output is a contract, not "a deck"

The emitted file is the *exact* dialect `deck-stage.js` renders and
`deck-lecture/scripts/extract_slides.py` parses: top-level
`<section data-label="…" data-speaker-notes="…" style="…brutalist inline…">`, KaTeX
in `<div data-tex data-display>`, live D3 in `<div data-chart="NAME">` + a folded
drawer registry, `.rise/.rise2/.rise3` entry motion, color only via `--nu-*` tokens.
Two attributes are load-bearing and never placeholders: `data-label` (beat identity)
and `data-speaker-notes` (the seed the whole narration expands from — a blank note
is a silent slide).

## Inputs

- `chapter.md` (the textbook chapter).
- Its asset pool at `lectures/<chapter>/assets/` (`assets.json`, `charts/*.drawer.js`,
  `svg/`, `book/`) — produced by the **lecture-assets** skill (stage 1).
- A known-good source deck folder to copy the runtime from (`support.js`,
  `deck-stage.js`, `_ds/…/colors_and_type.css`) — set as `metadata.runtime_from`.

Everything for one deck lives beside the emitted `.dc.html`, with `deck_plan.json`
as the source of truth every phase reads.

## Phase-gated pipeline

**Phase 0 — Plan (the gate).** Slice the chapter into an ordered slide plan and seed
each slide's `speaker_notes` from the prose. Output is a *starter* to rewrite, not a
finished deck — a regex cuts slides, it cannot summarize or motivate. **GATE — the
user reviews/rewrites the plan (especially speaker-notes) before emit.**
→ `python scripts/build_plan.py <chapter.md> <assets/assets.json> -o <folder>/deck_plan.json`

**Phase 1 — Bind (advisory report, no stop).** Match `chart`/`figure` slides to pool
assets; print what's bound, what's missing, and what pool candidates went unused, so
gaps route back to lecture-assets instead of getting faked.
→ `python scripts/bind_assets.py <folder>/deck_plan.json`

**Phase 2 — Emit.** Render the plan through the nine archetype templates; copy the
runtime + `_ds/`; fold each chart's `charts/<name>.drawer.js` into the deck's
`<script data-dc-script>` registry (live D3, zero iframes); copy figure assets and
rewrite their `src`.
→ `python scripts/emit_deck.py <folder>/deck_plan.json -o <folder>/<chapter-slug>.dc.html`
  (name the deck kebab-case to match the chapter slug, e.g. `01-the-skeptics-toolkit.dc.html` — **no spaces**, so no shell quoting and clean tab-completion)

**Phase 3 — Verify (the verification step).** Static audit: every slide parses via
`extract_slides.py` and has non-empty speaker-notes; no blue anywhere; every
`data-chart` resolves to a registered drawer; every `data-tex` has balanced braces;
runtime + `_ds/` present. The pixel audit (screenshot every slide) needs a browser
and is handed off, not faked.
→ `python scripts/verify_deck.py <folder>/<chapter-slug>.dc.html`
→ then hand to deck-lecture: `python ../deck-lecture/scripts/extract_slides.py <deck> -o <folder>`

## The nine archetypes

`title · section · statement · concept · equation · example · chart · figure · close`
— derived from the 39-slide fairness deck, emitted verbatim in its dialect by
`templates/archetypes.py`. Full grammar + plan fields in `reference/archetypes.md`.
Numbers in data contexts (equation worked examples) go mono (`--font-mono`); prose
numbers stay Lato (a regex can't tell a year from a data value).

Equation slides carry the EQUATIONS.md tangent data in `slide["tangent"]`
(`lhs/rhs/claim/glossary/example/values_claim/reentry`). The slide renders the dark
box + plain-terms + values-claim; the tangent (deck-lecture's `S05T`-style beats)
consumes the rest — which is what makes the equation tangents reproducible.

## Reuse map (build nothing that exists)

| Need | Reuse |
|---|---|
| Slide dialect / parser contract | `deck-lecture/scripts/extract_slides.py` (verify imports it) |
| Runtime (render + KaTeX + chart dispatch) | `support.js` + `deck-stage.js` from a source deck |
| Brand tokens | `_ds/…/colors_and_type.css` (copied, never regenerated) |
| Live-chart drawers | `lecture-assets/scripts/new_chart.py` → `charts/<name>.drawer.js` |
| Static figures / book figures | the pool's `svg/`, `book/` (via `assets.json`) |
| Palette / type / motion constitution | `unreal-reels/brutalist/DESIGN.md`, `EQUATIONS.md` |
| Pixel audit (screenshots) | `deck-lecture/scripts/prerender_deck.py` |

## Honesty / quality gate

- Every slide has a real `data-speaker-notes` (verify fails on blanks).
- No blue, ever; raw hex outside the `--nu-*` palette is flagged.
- Charts are drawers (live D3), not iframes; each `data-chart` resolves to a
  registered drawer; a missing drawer emits a visible placeholder, never silence.
- Equations are real KaTeX (`data-tex`), validated for balanced braces — never a
  screenshot.
- The `_ds/` design system is a hard dependency, copied per deck; a new book needs
  its own `_ds/`. The skill does not fake brand tokens.
- speaker-notes quality is the ceiling on the whole lecture — the Phase-0 gate is
  where that quality is set. `build_plan.py` only scaffolds.

## Not this skill's job

Building the asset pool (that's lecture-assets), authoring chart D3 (that's the pool
/ chart grammar), narration, doodles, or the render (all deck-lecture). Doodle
candidates in the pool are *passed through* — deck-lecture chooses the doodle tier at
render time; the deck does not embed them.

## Build status (honest)

**Working + regression-tested on Chapter 7:** the nine archetype templates; Phase 0
plan builder; Phase 1 bind report; Phase 2 emit (runtime + `_ds/` copy, `ds_css`
auto-discovery, drawer folding, figure copy); Phase 3 static verify. Round-trip
proven: an authored `deck_plan.json` → emit → `verify_deck` PASS → deck-lecture's
`extract_slides.py` parses all slides with correct labels, live-vs-doodle
classification (the two `data-chart` slides → `live`), and speaker-notes on every
beat. Worked artifact: `lectures/07-fairness-regen/`.
**Needs a browser to confirm:** the pixel audit (numbers-are-mono, real fonts,
motion) via `prerender_deck.py`, and live CSS-animation capture — same caveat as
deck-lecture.

## Worked example — regenerate Chapter 7

```
CH="/Users/nik/Documents/Cowork/computational-skepticism-for-ai/chapters/07-fairness-metrics-choosing-a-definition-and-defending-it.md"
ASSETS="/Users/nik/Documents/Cowork/computational-skepticism-for-ai/lectures/07-.../assets/assets.json"
FOLDER="/Users/nik/Documents/Cowork/unreal-reels/lectures/07-fairness-regen"

# 0. plan (STARTER) -> review/rewrite the speaker_notes -> GATE
python scripts/build_plan.py "$CH" "$ASSETS" -o "$FOLDER/deck_plan.json"

# 1. bind report (advisory)
python scripts/bind_assets.py "$FOLDER/deck_plan.json"

# 2. emit the deck (copies runtime + _ds, folds chart drawers)
python scripts/emit_deck.py "$FOLDER/deck_plan.json" -o "$FOLDER/07-fairness-metrics.dc.html"

# 3. verify, then hand to deck-lecture
python scripts/verify_deck.py "$FOLDER/07-fairness-metrics.dc.html"
python ../deck-lecture/scripts/extract_slides.py "$FOLDER/07-fairness-metrics.dc.html" -o "$FOLDER"
```
