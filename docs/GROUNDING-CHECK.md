# The grounding check — wiring the spine's fidelity gate to facts.json

*How the lecture spine's top quality bar (fidelity to source, per THE-SPINE.md) plugs
into the shared fact commons (`facts/`). Two paths: query-and-flag (read) and
correction-writeback (write). Both reuse `facts/extract-facts.py` bookkeeping so there is
one source of truth for matching and consensus. Built and smoke-tested against
`facts/physics/facts.json` (4,686 facts).*

---

## The whole loop in one picture

```
        ┌──────────────── facts/<domain>/facts.json (shared commons) ─────────────────┐
        │  deterministically-extracted defs  +  expert corrections (signed)           │
        └──────────────▲────────────────────────────────────────────┬────────────────┘
          READ (query) │                                             │ WRITE (correction)
                       │                                             │
  beat_sheet.json ─► grounding_check.py ─► grounding.json ─► professor triages flags
   (narration)         (Tier A + Tier B)     (flags list)      in Cowork/Codex/Claude Code
                                                                     │  "that def is wrong, it's X"
                                                                     ▼
                                                            record_correction.py ─► signed fact
```

The spine reads the commons to catch its own errors; the professor's fixes flow back as
signed evidence. The 150 experts making 150 books their own become, as a byproduct, the
human-verification layer of a cross-referenced fact commons.

## Path 1 — query-and-flag (`grounding_check.py`)

Runs after narration is written, before render. For each beat it extracts the
claim-bearing sentences and grades each on two tiers:

**Tier A — fidelity to *this* chapter (anti-hallucination).** Is the claim supported by
the source `chapter.md` the lecture was built from? A claim in the chapter is safe; a
claim *not* in the chapter is a candidate fabrication. This is the gate that matters most
— it catches the narration inventing something the book never said.

**Tier B — corroboration by the commons.** Match the claim against
`facts/<domain>/facts.json` (and the glossary in `terms.json`) and read its *earned*
status — never re-deciding it:

| Commons says | Meaning | Spine verdict |
|---|---|---|
| `verified` / `agreement` | corroborated by 2+ independent sources / a human | safe (even a not-in-chapter claim becomes a sanctioned `elaboration`) |
| `unverified` | single-source candidate | weak — noted, not trusted |
| `conflict` | commons already knows this is contested | **FLAG `contested`** — expert must adjudicate |
| no match | commons is silent | fall back to Tier A |

The interesting cell: **in the chapter but `conflict` in the commons** → the *book itself*
may be wrong or dated. Surface it; don't resolve it.

Output `grounding.json` carries a per-claim verdict table and — the thing the professor
actually opens — a **flags list**: `{beat_id, sentence, verdict, flag, match}`. That is
the triage list. A 10-minute lecture yields a handful of flags, not a transcript to
re-read. This is what makes the human phase gate cheap enough for 150 volunteers.

Feeds `qc_report.json` as the **fidelity axis**, weighted above watchability:
`{unverifiable, contested, review, grounded}` counts. A chapter with unverifiable or
contested claims is not "watchable-draft" no matter how clean the render.

**Smoke test (real physics commons):** three synthetic beats — two textbook definitions
and one fabricated "warp fields exceed lightspeed" claim. Result: the two definitions
matched real facts at score 1.0 → `grounded`; the fabrication scored 0.27, was absent from
the chapter, and was flagged `unverifiable — possible hallucination`. All three verdicts
fired correctly.

## Path 2 — correction-writeback (`record_correction.py`)

When the professor fixes a claim during refinement, the edit is not just local text — it
is **trusted-tier, human-authored evidence**. Two cases, both via the facts helpers:

- **Corrects an existing fact** → append a `REFUTES` evidence record to the old fact (→
  recompute → `conflict`, review queue) and `make_fact()` the corrected canonical as a
  trusted candidate.
- **Novel claim the commons lacked** → `make_fact()` straight from the book, expert as the
  source.

Because a *human* authored it, it can be **signed**: `verified=true` with a SHA-256 over
the exact canonical (the facts/ sign-off mechanism). Edit the fact later and the hash no
longer matches — the signature auto-invalidates, so a professor's name never rides on
content they didn't approve. Every writeback records provenance: expert id, book, chapter,
and the **`beat_id` that triggered it**, so any fact traces back to the lecture edit that
produced it.

The model is never allowed down this path. It may propose (low tier) and flag; only a
human refutes, corrects, and signs — by construction, not by policy.

## Where the model is allowed (same rule as facts/)

Matching a paraphrase to a fact is paraphrase-*recall*, which lexical similarity
under-recalls (facts/README defers embeddings for exactly this reason). So the deterministic
pass here does the cheap, high-precision work and emits a **near-miss band** (`0.45 ≤ score
< 0.62`) for an *optional* LLM adjudicator that **flags, never decides or verifies**. The
claim extractor is likewise recall-first: a missed claim is a missed hallucination, so it
over-collects declaratives and lets Tier A absorb the non-claims. The robust version of
claim extraction is an LLM pass — also low-tier, also flag-only.

## Honest limits

- **Domain mapping.** Each book/chapter must name its `facts/` subdomain (skepticism has no
  commons yet; physics/biology/chemistry do). A `domain` field in `deck_plan.json` metadata
  is the clean place for it.
- **Tier-A grounding is lexical.** Token-overlap + prefix windows catch verbatim and light
  paraphrase; heavy rewording of a true chapter claim can still flag as `review`. That is
  the safe failure direction (false-positive flag, not false-negative miss), and the
  near-miss band routes it to adjudication.
- **Commons coverage is uneven.** Physics is deep (4,686 facts); many domains are thin, so
  Tier B is often silent and Tier A carries the check. That is fine — Tier A is the
  anti-hallucination gate; Tier B is corroboration on top.
- **Not yet wired into `silent_run.py`.** It runs standalone today. The integration is one
  stage after `script`/narration, writing the fidelity axis into `qc_report.json`. Small,
  and next.

## How to run

```bash
# query-and-flag
python skills/shared/grounding/scripts/grounding_check.py <lecture_folder> \
    --facts-dir /path/to/facts --domain physics --chapter /path/to/chapter.md

# correction-writeback (human sign-off)
python skills/shared/grounding/scripts/record_correction.py \
    --facts-dir /path/to/facts --domain physics \
    --refutes "old wrong claim" --corrected "the correct claim" \
    --expert "Prof. X <x@uni.edu>" --book anatomy-2e --chapter m45985 --beat S07 \
    --verbatim "supporting passage" --sign
```
