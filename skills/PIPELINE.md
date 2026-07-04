# The lecture-video pipeline — chapter in, narrated video out

```
chapter.md
   │
   ▼  STAGE 1 · lecture-assets      builds a POOL of candidate visuals
   │                                (over-generate, tag, force nothing)
   ▼  STAGE 2 · slide-deck          SELECTS from the pool → a brutalist .dc.html deck
   │                                (human gate on the plan)
   ▼  STAGE 3 · deck-lecture        deck → narrated video (your voice) + captions
   │
   ▼
lecture.mp4
```

One book chapter (a Markdown file) goes in the left. A finished, narrated,
captioned lecture video comes out the right. Three skills, run in order. Each
stage writes files to disk that the next stage reads — nothing is re-explained
between stages.

---

## Stage 1 — `lecture-assets`: build the visual pool

**In:** `chapter.md` (+ any figures the book already ships).
**Out:** `lectures/<chapter>/assets/` — an over-generated pool, nothing forced.

What it produces:

- `book/` — the book's own figures, imported first (pre-vetted).
- `svg/` — colorblind-safe static figures (Venn, partitions, diagrams) via **cajal**.
- `charts/<name>.drawer.js` (+ a standalone `.html`) — live D3 charts, one per
  quantitative claim, via `new_chart.py`.
- `doodles/` — candidate sketch moments (for stage 3 to animate later).
- `assets.json` — the manifest: every asset tagged `candidate`.

The rule: **breadth now, selection later.** A figure that never reaches a slide
isn't waste — it's inventory (reusable in articles, Substack, social).

---

## Stage 2 — `slide-deck`: chapter + pool → a deck  *(the new middle piece)*

**In:** `chapter.md` + the stage-1 `assets/` pool.
**Out:** `Chapter NN - Title.dc.html` — a brutalist slide deck, ready for stage 3.

Four phases, one human gate:

1. **Plan** (`build_plan.py`) — slices the chapter into an ordered slide plan
   (`deck_plan.json`) and seeds each slide's speaker-notes from the prose.
   → **GATE: you review/rewrite the plan** — especially the speaker-notes, since
   those become the narration. This is the cheapest place to fix everything.
2. **Bind** (`bind_assets.py`) — matches chart/figure slides to pool assets and
   prints a gap report (what's missing routes back to stage 1). Advisory, no stop.
3. **Emit** (`emit_deck.py`) — renders the plan through the **nine slide
   archetypes**, copies the runtime + design system, and folds each chart's
   `drawer.js` into the deck as live D3 (no iframes).
4. **Verify** (`verify_deck.py`) — audits palette (no blue), speaker-notes on every
   slide, KaTeX validity, chart resolution. Fails loudly if anything's off.

The nine archetypes: `title · section · statement · concept · equation · example ·
chart · figure · close`.

---

## Stage 3 — `deck-lecture`: deck → narrated video

**In:** the stage-2 `.dc.html` deck.
**Out:** `lecture.mp4` — one slide = one narrated beat, karaoke-captioned.

The through-line: **audio is the master clock.** Narration is generated and
measured first; every slide's on-screen time is its real spoken duration.

- **Extract** — deck → `beat_sheet.json`, one beat per slide.
- **Script** — expand each slide's speaker-notes into spoken teaching voice
  (*discuss the slide, don't read it*). **GATE: approve scripts before spending audio.**
- **Audio** — ElevenLabs voice clone, one MP3 per beat, real durations measured.
- **Captions** — forced alignment snaps each word to when it's spoken.
- **Visuals** — each talky slide gets a doodle or auto-bullets so you're not staring
  at static text for 30s; chart slides stay live; equations get a ~40s tangent.
- **Render** — Remotion assembles deck + visuals + voice + captions → the `.mp4`.

---

## Who does what

| | Automated | Human decides |
|---|---|---|
| Stage 1 | figure/chart/doodle generation, manifest | which candidates are strong |
| Stage 2 | plan skeleton, HTML emit, audit | **the plan + speaker-notes** (the one gate) |
| Stage 3 | audio, captions, visuals, render | script approval, final pick |

Two things carry the whole pipeline and are never placeholders: each slide's
**`data-label`** (beat identity) and **`data-speaker-notes`** (the seed the entire
narration grows from). A blank note is a silent slide.

**Status:** all three stages built. Stage 2 was the missing middle — now done and
regression-tested by re-deriving the Chapter 7 fairness deck. The Chapter 7 lecture
itself is rendered and on YouTube.
