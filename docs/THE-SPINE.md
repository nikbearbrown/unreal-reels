# What we are building: the spine, not the product

*The north star for the silent-mode / lecture pipeline. Read this before the how-to docs.*

---

## The one sentence

We are not generating finished lecture videos. We are generating, for every chapter of
every book, a **high-quality, accurate, error-checked spine** that a domain expert opens
in Cowork / Codex / Claude Code and — conversationally, in an afternoon — makes their own.

## Why this is the opposite of "build me a physics course"

A single prompt like *"build me a physics course"* invents content from a model's priors.
Nothing anchors it, so it is slop by construction: plausible, generic, subtly wrong, and
soul-less. An expert reads two paragraphs and reaches for a blank page instead.

Our spine is different in one decisive way: **it is downstream of a real, authored book.**
The narration expands the chapter's own prose; the figures are the chapter's own figures;
the equations are the chapter's own equations. The quality of the book flows into the
spine. We are not asking a model to be a physicist — we are asking it to *faithfully
stage* a physicist's chapter as a lecture. That is a checkable task, not a creative one.

The test of success: **two physics professors, handed the same spine for the same chapter,
quickly diverge into two different courses that are each unmistakably theirs.** The spine
is a strong, opinionated starting point — not a blank scaffold (useless) and not a finished
product (nothing left to own). It is the 80% that is identical for everyone, done well, so
the expert spends all their energy on the 20% that is theirs alone.

## What the spine actually is (the whole addressable stack)

The video is the visible layer. The spine is everything under it, and every piece is
legible and editable:

- **`deck_plan.json`** — the pedagogical skeleton: which slides, in what order, each with a
  claim, a seeded note, and (where one fits) a bound figure. This is where an expert
  reshapes the *argument* of the lecture.
- **narration (`beat_sheet.json`)** — grounded spoken teaching voice, one beat per slide.
  Where an expert changes *how it's taught*.
- **figures / charts / SVGs** — the book's own, plus authored diagrams. Reusable inventory.
- **`decision_log.json`** — every automated choice and *why* ("made this a concept slide;
  bound figure-03 because its concept matched"). This is the expert's entry point: it turns
  "change this or that" into a precise conversation, because every choice is named.
- **the Remotion scaffold** — renders the current state to a watchable draft on demand.

Because these are separate, addressable files, refinement is conversational and surgical:
*"merge slides 4 and 5," "that definition is wrong, it's X," "cut the induction tangent,"
"re-voice beat 9"* — each touches one unit, and the master-clock law re-times the rest for
free.

## The three quality bars (in priority order)

1. **Accuracy / fidelity to the source.** The spine may never state something the chapter
   does not. Wrong equations, misattributed ideas, invented claims — these are the only
   truly disqualifying errors, because they are the ones an expert will not forgive and
   cannot cheaply fix by eye. This is the top bar.
2. **No obvious errors.** Broken KaTeX, an unresolved figure reference, an orphaned TODO, a
   slide that says "TODO: a sharp claim." Mechanical, fully machine-checkable, zero excuse.
3. **Watchability.** Progressive disclosure, no static wall of text, sane slide count,
   audio that lands. Important — but an expert forgives a rough visual. They do not forgive
   a false statement. Watchability is the third bar, not the first.

The QC score must weight these in this order. (As of this writing it weights only bars 2
and 3 — see the gap below.)

## The human phase gate: cheap and sharp, never eliminated

At 1,800 chapters, no human reads every line. The system's job is not to remove the expert
gate — it is to make it **cheap and sharp**: surface every machine-checkable error
automatically, *flag every claim the machine cannot verify*, and route the expert's
attention to exactly those. The expert signs off on **triaged risk** — "here are the 4
unverifiable claims and 2 equation mismatches in this chapter" — not on raw output. A gate
that reviews 6 flagged items per chapter is a gate 150 volunteers can actually staff.

## The design consequence I owe you (an honest gap)

The QC harness I built scores *completeness* (deck emitted, beats narrated, audio present,
it renders). Under this vision that is the wrong primary axis. Two things are missing and
should be built next:

1. **A grounding check.** For each narration beat, flag any sentence that makes a factual
   claim, cites a number, or names an entity **not present in or derivable from the source
   `chapter.md`.** The discuss-don't-read guard is a weak shadow of this (it checks overlap
   with the *slide*, not fidelity to the *chapter*). This is the accuracy gate, and it is
   mostly checkable — a second-model verification pass ("list every claim in this narration
   not supported by this chapter") is the right tool, and a strong use of a verification
   subagent.
2. **An accuracy axis in `qc_report.json`**, weighted above watchability: KaTeX validity
   (already partly in verify_deck), every figure `src` resolves, every equation `tex`
   parses, zero residual TODOs, and the grounding-check flag count. The verdict should read
   "fidelity: N unverified claims, M mechanical errors" — the professor's actual triage
   list — not just "watchable-draft."

Until those exist, the pipeline produces watchable spines whose *accuracy* is asserted, not
verified. For this vision, verified accuracy is the whole point.
