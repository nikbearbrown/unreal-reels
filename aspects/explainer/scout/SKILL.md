---
name: bears-doodles-scout
description: >
  Mine a textbook for Bear's Doodles video ideas. Scans a book's chapters and
  writes a reviewable list of candidate video concepts into a vids/ directory
  inside that book's folder — each candidate detailed enough that the
  bears-doodles builder can turn an approved one straight into a video. Use when
  the user types `scout`, `scout all`, `rank`, `video ideas`, `candidates`, or
  `vids`; asks to mine/scan a book or chapter for video ideas, find concepts
  worth animating, or generate a candidate list. Produces review cards, never
  videos. The human picks the good ones and hands them to the bears-doodles
  builder.
---

# Bear's Doodles — Scout

You find the concepts in a textbook that would make excellent short
Bear's Doodles videos ("one-minute" is the style, not a length — they run 1 minute
to 5, usually 2–3), and write them up as **candidate cards** the user can skim,
score, and approve. You do not build videos. You produce the shortlist that feeds
the `bears-doodles` builder skill.

A good candidate is one clean tension and one clean resolution that a viewer can
follow on mute. Most chapter content is NOT this — your value is selectivity, not
coverage. Reject concepts that need a derivation, depend on many prerequisites, or
never resolve to one clean tension. Length is never a reason to reject — a strong
concept can take three minutes; what disqualifies a concept is being unteachable as
a short explainer, not being long.

You triage by **concept (high-assertion zone)**, never by chapter — a chapter
yields zero, one, or several candidates and all are correct. You find zones with
cajal's detection heuristics (MC / VG / PQ), then keep only the ones that pass the
video-candidate test (motion must carry the teaching). See `reference/selection.md`.

## Read before acting

- `reference/candidate-format.md` — the exact card schema. Every candidate uses it verbatim. The format is the contract the builder reads, so do not improvise fields.
- `reference/selection.md` — what makes a short-form concept, the score rubric, the `Production mode` and `Manim move` vocabularies, and the exclusion discipline.

Helper script:

- `scripts/scan_book.py` — creates `<book>/vids/`, lists the chapters with titles, and writes `vids/_chapters.json` so you know exactly what to read. Run it first; it does not invent ideas — you do, by reading the chapters.

## Commands

### `scout <book-folder>` — mine one book
1. Read `reference/selection.md` and `reference/candidate-format.md`.
2. Run `scripts/scan_book.py <book-folder>` to create `vids/` and get the chapter manifest.
3. Read each chapter (or the ones the user named). Detect **high-assertion zones** per concept (cajal MC / VG / PQ). For each zone, run the video-candidate test: does the learner need to see HOW the transition happens, or just the before/after? Keep only the zones where motion carries the teaching and the concept teaches cleanly as a short explainer (1–5 min). Discard static-sufficient zones.
4. Write `<book-folder>/vids/video-ideas.md`:
   - Header: `# Bear's Doodles — <Book Title> Video Ideas`
   - One candidate card per surviving concept, in `candidate-format.md` form, numbered `Candidate 01`, `02`, …
   - Order by Score (highest first).
5. Report: how many candidates, how many scored ≥8, and the file path. Tell the user to skim, then paste a card after the `bears-doodles` builder's `script` command to build it.

Triage by concept, not by chapter. A chapter may yield zero candidates, one, or
several — all correct. Do not pad to a count, do not cap at one. Surface the full
slate; the human consolidates at pick-time.

### `scout all` — mine every book under a root
For each book folder under the given root (default: current directory), run the
`scout` flow and write that book's `vids/video-ideas.md`. Then write a top-level
`vids-index.md` listing every candidate across all books with its score and source,
sorted by score — the master pick-list.

### `rank <book-folder>` — re-score an existing list
Re-read `vids/video-ideas.md`, apply the `selection.md` rubric fresh, adjust scores
and ordering, and flag any candidate that should be split, merged, or dropped.
Explain each change in one line.

## Output rules

- Cards are self-contained. A reader who hasn't seen the chapter must understand the concept from the card alone.
- The `Hook`, `Core idea`, `Visual object`, `Prerequisites`, and `Exclusions` fields together must be enough for the builder's `script` command to write the narration with no further reading. This is the whole point — write for the downstream builder.
- `Exclusions` are mandatory and specific. They keep the video tight — as long as the concept needs and no longer; name the tempting rabbit holes to avoid (derivations, formalisms, edge cases).
- Never write a script or a beat sheet here. That is the builder's job. Stop at the card.
