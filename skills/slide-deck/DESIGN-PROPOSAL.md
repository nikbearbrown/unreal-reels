# slide-deck skill — design proposal (stage 2)

> **STATUS: BUILT.** Decisions A/B/C locked (see §9). Skill lives in
> `unreal-reels/skills/slide-deck/`; regression-tested on Chapter 7
> (`lectures/07-fairness-regen/`). This doc is kept as the design record.

`chapter.md` + `assets/assets.json` → a brutalist `.dc.html` deck that **selects
from the asset pool** and hands off to `deck-lecture`. This is the missing middle
of the pipeline:

```
chapter.md → [lecture-assets ✓] → [slide-deck ← THIS] → [deck-lecture ✓] → narrated mp4
```

---

## 1. The contract (grounded in the fairness deck I just read)

**Output is not "a deck."** It is the *exact* `.dc.html` dialect that
`deck-lecture/scripts/extract_slides.py` parses and `deck-stage.js` renders.
Concretely, from `Chapter 7 - Fairness Metrics.dc.html`:

- `<x-dc>` root → `<helmet>` (loads `_ds/…/colors_and_type.css`, KaTeX, d3) →
  `<x-import component-from-global-scope="deck-stage" … width="1920" height="1080">`.
- One `<section data-label="…" data-speaker-notes="…" style="…inline brutalist…">`
  per slide. **39 sections = 39 beats.**
- Color only via `var(--nu-red | --nu-black | --nu-white | --nu-neutral-N | --nu-red-tint)`.
- Entry motion via `.rise / .rise2 / .rise3` (gated on `[data-deck-active]`).
- Equations: `<div data-tex data-display>…KaTeX…</div>`.
- Live charts: `<div data-chart="NAME">` + one `<script type="text/x-dc" data-dc-script>`
  block registering `this._drawers['NAME'] = function(c,w,h){…d3…}`.
- Deck ships beside three runtime files it must copy: `support.js`, `deck-stage.js`,
  and the `_ds/neu-…/colors_and_type.css` design-system folder.

**Two attributes are load-bearing for stage 3 and cannot be placeholders:**

- `data-label` — deck-lecture's `slide_index`/beat identity.
- `data-speaker-notes` — **the entire narration is expanded from this.** A deck with
  weak notes produces a weak lecture. So authoring the notes *is* the skill's main
  intellectual work, not decoration.

---

## 2. Slide archetypes — the templates the emitter fills

The 39-slide deck is not freeform; it's ~9 recurring archetypes. I'd encode each as
one template function (plan entry → HTML string), so the deck is *composed*, never
hand-written slide by slide. Derived directly from the fairness deck's labels:

| # | archetype | look (from the real deck) | when the planner emits it |
|---|---|---|---|
| 1 | `title` | black, red top bar, eyebrow → h1 → rule → subtitle | chapter open |
| 2 | `section` | **red** bg, "Part N" + big h2 | each major part boundary |
| 3 | `statement` | black, one large claim, no bullets | a load-bearing thesis/theorem |
| 4 | `concept` | white, eyebrow + h2 + `.rise2` red-marker bullet list | explain a definition/idea |
| 5 | `equation` | white, "Metric NN · Equation", dark `data-tex` box, **plain-terms + values-claim** two-column | every equation (ties to EQUATIONS.md) |
| 6 | `example` | white, left red bar, big h2 + prose paragraphs | the worked/real-world instance |
| 7 | `chart` | `data-chart` div + registered D3 drawer | a quantitative claim with a pool chart |
| 8 | `figure` | white, eyebrow + h2 + centered SVG/img | a pool SVG or book figure earns a slide |
| 9 | `close` | black closing card | chapter close |

Numbers always wrapped mono (`--font-mono`), per DESIGN.md. Archetypes 5 and 7 are
the only ones with real complexity; 1–4, 6, 8, 9 are near-static shells.

---

## 3. Phase-gated pipeline (matches the rest of the repo's philosophy)

**Phase 0 — Outline → `deck_plan.json` (the gate that matters).**
Parse `chapter.md` (headings, equations, the chapter's own `## Prompts`/figure list,
key claims) + read `assets.json`. Emit an ordered `deck_plan.json`: a list of slide
entries `{archetype, label, speaker_notes, fields{…}, asset_ref?, equation?}`.
**GATE — user reviews the outline before any HTML exists.** This is the cheapest
place to fix structure, ordering, and (critically) the speaker-notes seed.
→ `scripts/build_plan.py <chapter.md> <assets_dir> -o <lecture_folder>`

**Phase 1 — Bind assets to slides.**
Match `chart`/`figure` slides to pool assets by concept (assets.json `concept` +
`status`). Only `status:"candidate"` assets are eligible — the ch02 `placeholder`
stubs are correctly skipped. Report gaps ("slide wants a heavy-tail chart; pool has
none") so they route back to lecture-assets rather than getting faked. GATE.
→ `scripts/bind_assets.py <lecture_folder>`

**Phase 2 — Emit `.dc.html`.**
Render `deck_plan.json` through the archetype templates; copy `support.js`,
`deck-stage.js`, `_ds/`; inline equations as `data-tex`; fold selected charts into
the `data-dc-script` drawer registry (see §4).
→ `scripts/emit_deck.py <lecture_folder> -o "<Chapter NN - Title>.dc.html"`

**Phase 3 — Verify (the required verification step).**
Load the deck headless, screenshot each slide, run the DESIGN.md audit
(palette/one-red/no-blue, numbers-are-mono, every section has non-empty
`data-speaker-notes`, KaTeX compiles, drawer names resolve). Then it's ready for
`extract_slides.py`. GATE → hand to deck-lecture.
→ `scripts/verify_deck.py "<deck>.dc.html"` (reuses deck-lecture's
`prerender_deck.py` for the screenshots).

---

## 4. The one genuinely hard problem — chart integration

`deck-stage.js` wants each chart as a **drawer function body** in the
`data-dc-script` registry: `this._drawers['compas'] = function(c,w,h){ …d3… }`.
But `lecture-assets` emits charts as **standalone `charts/*.html`** (self-contained,
for article/social reuse). Those two shapes don't match, and the pipeline warns
repeatedly that nested iframes are heavy (deck-lecture keeps only D3 chart slides
live for exactly this reason). So iframing the pool chart into a slide is the wrong
default.

Three ways to reconcile, in my order of preference:

1. **Add a drawer contract to the pool (recommended).** Have `lecture-assets`
   *also* emit `charts/<name>.drawer.js` exporting `function(container,W,H){…}`.
   `emit_deck.py` concatenates those verbatim into the `data-dc-script` block →
   the chart is genuinely live in both the deck and the stage-3 render, zero
   iframes. One chart, two artifacts (`.html` for reuse, `.drawer.js` for the deck).
   Cost: a small addition to the *already-built* lecture-assets skill.
2. **Extraction adapter (fallback for charts that already exist as `.html`).**
   `emit_deck.py` pulls the D3 body out of an existing standalone `charts/*.html`
   into a drawer. Brittle (depends on how the html was authored) — offer only as a
   migration path for ch02's existing charts.
3. **Rasterize to SVG/PNG and place as a `figure` slide.** Loses interactivity/entry
   animation but bulletproof. The honest fallback when a chart won't cleanly become
   a drawer.

I'd build **1 as the path forward + 3 as the guaranteed fallback**, and only reach
for 2 to migrate existing pool charts. This is decision **A** below.

---

## 5. Where doodles go (a deliberate non-feature)

`assets.json` doodle candidates are **not** placed in the deck. In deck-lecture,
"doodle" is a *render-time visual tier* chosen per text slide (Phase 3.5), not deck
content. So slide-deck's only job is to **pass the doodle candidates through**
(leave them in `assets/doodles/` and note in `deck_plan.json` which slide each maps
to) so stage 3 can pick them up. Building doodles here would duplicate stage 3.

---

## 6. Equation slides ↔ EQUATIONS.md tangents

Every `equation` archetype slide carries, in `deck_plan.json`, the structured tangent
data from EQUATIONS.md's authoring schema (`lhs`, `rhs`, `claim`, `glossary[]`,
`example{}`, `values_claim`, `reentry`). The *slide* shows zones 1/2-short/5 (the
dark box + plain-terms + values-claim columns — exactly the fairness deck's layout);
the *tangent* (stage 3's `S05T`-style beats) consumes the rest. Emitting this data at
plan time is what makes the open Chapter-7 tangent beats (`S05T S07T …`) reproducible
instead of hand-authored. This is where stage 2 and stage 3 actually interlock.

---

## 7. Honest risks / what I will *not* pretend to solve

- **The `_ds/` design system is a hard dependency.** The deck's brand tokens live in
  `_ds/neu-…/colors_and_type.css`, authored elsewhere. slide-deck copies it; it does
  not regenerate it. New book → needs its own `_ds/` or a shared one. I'll document
  this, not fake it.
- **Speaker-notes quality is the ceiling on the whole lecture.** A regex can slice a
  chapter into slides but cannot write a good teaching note. The planner drafts notes;
  they still deserve the Phase-0 human gate. I won't oversell auto-notes.
- **Chart authorship stays partly manual.** Turning a quantitative claim into an
  *honest* encoding (zero baseline, `scaleSqrt`, one red) is a design act. slide-deck
  places and wires charts; it leans on lecture-assets/the chart grammar to author them.
- **KaTeX/`data-tex` must be validated, not trusted.** Bad TeX renders as red error
  text on a live slide. Phase 3 compiles every equation and fails loudly.

---

## 8. Proposed file layout

```
unreal-reels/skills/slide-deck/
  SKILL.md
  scripts/
    build_plan.py      # chapter.md + assets.json -> deck_plan.json   (Phase 0)
    bind_assets.py     # match slides <-> pool assets, report gaps     (Phase 1)
    emit_deck.py       # deck_plan.json -> .dc.html (+ copy runtime)   (Phase 2)
    verify_deck.py     # headless audit: palette, mono, notes, KaTeX   (Phase 3)
  templates/
    archetypes.py      # the 9 slide template functions
    deck_shell.html    # <x-dc>/<helmet>/<x-import> wrapper
  reference/
    archetypes.md      # the taxonomy above, with the source-deck line refs
```

---

## 9. Decisions — LOCKED

- **A. Chart integration → `charts/<name>.drawer.js` contract + SVG-raster
  fallback.** Added `lecture-assets/scripts/new_chart.py`, which scaffolds the
  drawer (source of truth) and a synced standalone `.html`, and registers the asset.
  `emit_deck.py` folds each drawer verbatim into the deck's `data-dc-script`
  registry — live D3, zero iframes.
- **B. One gate at `deck_plan.json` (Phase 0).** `bind_assets.py` (Phase 1) prints
  an advisory gap report and never stops the pipeline.
- **C. Re-derive Chapter 7 as the regression target.** Extracted the deck's real
  `triangle` + `arithmetic` drawers into a pool, authored a `deck_plan.json`
  covering every archetype, emitted, verified (PASS), and confirmed deck-lecture's
  `extract_slides.py` parses all slides with correct labels + live/doodle
  classification + speaker-notes. Artifact: `lectures/07-fairness-regen/`.
