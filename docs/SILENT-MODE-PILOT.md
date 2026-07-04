# Silent Mode — pilot log

*Started 2026-07-01. Pilot books: `computational-skepticism-for-ai` (argument-dense) and `biology-anatomy-physiology` (figure-dense, 407 figures). Goal: prove the silent orchestrator on two structurally opposite books before the 150-book fleet.*

---

## What's built and working

- **`scripts/silent_run.py`** — one chapter → rough lecture folder, no prompts. Runs the deterministic stages directly; at each former human gate it either applies an auto-policy (and logs the reason) or, for the two irreducibly-LLM gates, emits an authoring packet and halts cleanly.
- **`scripts/batch_run.py`** — fleet driver: loops chapters/books, rolls every `qc_report.json` + `decision_log.json` into one `fleet_manifest.json` ranked worst-first. On AICR this becomes one Slurm array task per chapter (chapters are embarrassingly parallel); the manifest is the same either way.
- **`--deck` path bug (F5) fixed** in `scaffold_remotion.py` and `prerender_deck.py` — a bare deck filename now resolves against the lecture folder. That footgun would have hit every one of 1,800 chapters.

Every run drops three review surfaces in the chapter folder: `decision_log.json` (what each gate decided + why), `qc_report.json` (0–100 score + itemized checks + verdict), and `packets/*.md` (the unfilled agent slots).

## Verified on both books

| | Skepticism Ch.2 | Biology Ch.1 |
|---|---|---|
| Runtime import | 3 files + `_ds/` copied, logged | (runtime not passed — logged as need) |
| Asset pool | 20 candidates auto-imported | 5 candidates |
| Plan starter | 72 slides | 33 slides |
| Halt | clean, at Agent Slot 1 | clean, at Agent Slot 1 |

The orchestrator is book-agnostic and halts exactly where a human/LLM judgement is required. The mechanical 80% runs unattended.

## First real finding (this is what the pilot is for)

**The plan starter over-generates on equation-dense chapters.** Skepticism Ch.2 produced **72 slides** — because `build_plan.py` emits one `equation` slide per `$$…$$` block, and the multiplication-rule section alone has ~10 inline derivation steps. Biology Ch.1, with prose + discrete figures, produced a sane 33. A 72-slide lecture from one chapter is not watchable; it's a wall.

This is an **auto-policy to add before the fleet**: consolidate consecutive equation blocks within a section into one equation slide (the derivation is a tangent, not ten slides), and cap slides-per-section. Exactly the kind of lesson the pilot exists to surface cheaply — on 2 books, not 150.

**Second signal:** ~296 TODOs to author per equation-dense chapter. Across 1,800 chapters, the LLM authoring of plans + narration is the real cost and time driver — which makes the fleet-LLM decision (below) the pivotal one, not the compute.

## The decision that gates the fleet: who fills the two agent slots?

Silent mode automates everything except two irreducibly-LLM gates: **authoring the plan** (headlines, speaker-notes, asset bindings) and **writing narration** (discuss-don't-read). For the pilot, Fable fills them interactively. For 1,800 chapters that can't be interactive. Three options:

1. **Claude Batch API** — programmatic, scales, cost-bounded, no babysitting. Best fit. Each packet becomes a batch request; results write `deck_plan.json` / `narration_text` back. Recommended.
2. **Headless Claude Code on the cluster** — one agent process per chapter. More capable per chapter, harder to operate at fleet scale and needs egress from compute nodes.
3. **Fable interactively** — fine for the pilot and for flagship chapters; impossible for the long tail.

The pilot should be finished with (3) to lock the quality bar, then (1) wired to hit it at scale.

## Next steps (in order)

1. Add the equation-consolidation + slides-per-section auto-policy to `build_plan.py` (or a silent post-pass). Re-run Ch.2; expect ~30–40 slides.
2. Fable authors Ch.2's plan + narration (Agent Slots 1 & 2) to set the quality bar; run through `qc` to get a real score.
3. On the user's Mac: `--only audio captions scaffold qc`, then Remotion Studio preview → first fully rough video. (Audio/captions/render need ElevenLabs + node + faster-whisper, which live on the Mac / cluster, not this sandbox.)
4. Repeat for 2–3 biology chapters; log which auto-decisions get overridden most — each frequent override becomes a better policy.
5. Only then: wire Agent Slots to the Batch API and run one full book unattended as the true fleet dry-run.

## For the 150 volunteers

The end state this enables: a volunteer opens a chapter folder that already has the deck, the SVGs/charts, the draft narration, the scaffolded Remotion project, and a QC score — and does only the human-only work (watch, note what's wrong, fix the flagged beats, approve the render). They start from a watchable rough draft, not a blank chapter. The decision log tells them what the machine chose and why, so their edits are surgical.
