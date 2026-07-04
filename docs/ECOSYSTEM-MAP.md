# The ecosystem: AI+1, facts, Unreal Reels — one governed factory

*How the pieces we've been touching this session actually compose. Written after reading
`ai1-cli` (AI+1, the book generator), `facts/` (the shared fact commons), and building the
silent-mode lecture spine + grounding check in `unreal-reels`. The point: these are not
three projects. They are one system with one philosophy, and our silent-mode work should
align to its conventions rather than reinvent them.*

---

## The one philosophy, stated once

Every part obeys the same three rules:

1. **The human ("+1") is load-bearing and is the only authority.** The AI executes;
   the human decides what the thing *is*, makes it theirs, and signs every gate. In AI+1
   this is literally the name: one human **+1** the AI. GATE 3 (Human Rewrite) can never
   be signed by an agent.
2. **Generation is the fallback, not the default.** Before producing anything, check for a
   *verified* artifact and reuse it. Nothing authoritative is ever silently regenerated.
3. **Everything carries its provenance.** Facts carry evidence; artifacts carry a
   `.verified.json` sidecar; gates are signed in `STATUS.md`; the trail is committed.

Deterministic where possible, model as a low-tier proposer, human as sole authority. That
is the same sentence I wrote about `facts/`, about the grounding check, and about the
lecture spine — because it is the whole ecosystem's sentence.

## The four systems and how they chain

```
   AI+1 (ai1-cli)                    facts/                 Unreal Reels
   ─────────────                     ──────                 ────────────
   writes the BOOK                   the shared TRUTH       makes the VIDEOS
   7 gated phases:                   cross-book fact        from the book:
   Blueprint→Research→Draft→         dictionary, tiered     explainers, full
   Human-Rewrite→FactCheck→          sources, derived       lectures, kids'
   Images→Check-Images               consensus, human       music videos
        │                            sign-off                    ▲
        │  chapter.md (GATE-4 fact-checked, GATE-6 figures)       │
        └─────────────────────────────┬──────────────────────────┘
                                       │  higgsfield/ + vids/_chapters.json
                                       │  (FIELD: which chapters/topics deserve a video)
                                       ▼
                          lecture-assets → slide-deck → deck-lecture
                          (the spine we've been building)
```

- **AI+1 produces the book** through seven human-gated phases and emits a `.verified.json`
  sidecar for every artifact. By the time a chapter exists, it has passed **Fact Check
  (GATE 4)** and **figure audit (GATE 6)**.
- **`facts/` is the shared spine of truth** — the same code lives standalone *and* synced
  into every AI+1 book (`facts/facts.py`, `extract-facts.py`, `facts-sources.yaml`). Phase 1
  populates it; Phase 4 queries it before any web lookup.
- **Unreal Reels consumes finished chapters** and turns them into videos. `higgsfield/`
  is the bridge: it topic-scans chapters (the **FIELD** framework — Focus, Image,
  Exclusions, Load, Drive) and `vids/_chapters.json` records which chapters/topics are
  video candidates and in which mode (Manim, lecture, reel).

## The realization that matters for our work

**The lecture spine sits downstream of a book that has already passed fact-check.** That
changes the accuracy burden completely:

- We are *not* fact-checking a video against the world. We are checking that the narration
  stayed **faithful to an already-verified chapter**. Truth was established at AI+1 GATE 4;
  the video's job is fidelity, not truth. That is a far smaller, far more checkable task —
  and it's exactly what the grounding check's **Tier A** does.
- The grounding check's **Tier B** (query `facts.json`) is not a new invention — it is
  **AI+1's Phase 4 logic applied to narration**, and it correctly reuses the same
  `facts/` helpers. Good: one matcher, one consensus rule, one commons.

## Where silent-mode should align (not reinvent)

Building in `unreal-reels`, I introduced some parallel machinery. AI+1 already solved the
same problems; the spine should adopt its conventions so a lecture becomes a first-class
AI+1 artifact instead of a side pipeline:

| I built (unreal-reels) | AI+1 already has | Alignment move | Status |
|---|---|---|---|
| `decision_log.json` (per-gate choices + reasons) | `.verified.json` sidecars + `STATUS.md` gate table | Emit sidecars in AI+1's format; keep the decision log as the *reasoning* attachment. | **DONE** — `silent_run` now stubs `<artifact>.verified.json` (AI+1 shape), gates on sidecar state (verified→use, unverified→stop, stale→re-block via sha256), writes a lecture-local `STATUS.md` gate table, and keeps `decision_log.json` as the reasoning trail. |
| silent auto-policies at each gate | the three **MODES** (Agent / API / Handoff) with identical deterministic bookkeeping | Make `silent_run` mode-aware: the two LLM slots run in whichever mode the operator picks. | **DONE** — `--mode {agent,api,handoff}`. The two gates (plan, narration) emit the slot as `.md` / `.request.json` / `.prompt.md`; bookkeeping identical across modes. This *is* the fleet-LLM fork, answered AI+1's way. |
| grounding check querying facts.json | `facts/facts.py lookup` + Phase-4 record-back | Wire the writeback through `facts.py record` so lectures feed the same commons. | Partial — `grounding_check.py`/`record_correction.py` reuse the `facts/` helpers; still standalone (not yet a `silent_run` stage). |
| batch_run over 150 books | `SOURCE-MANIFEST.md` canonical/seed/protected + `sync-to-book.sh` | Ship silent-mode + grounding as **canonical** tooling in `ai1-cli`, then `sync-to-book.sh` propagates them to all 150 books. | Next — the fleet-deployment mechanism, not yet wired. |

### Verified behavior (this session)

`silent_run.py` now enforces the AI+1 gate contract, tested on Ch.2:
- **signed** `deck_plan.json` → decision `verified` → proceeds, no regeneration;
- **edited after signing** → sha256 mismatch → `awaiting-signoff` → hard stop (a silent edit cannot pass a gate);
- **no artifact** → builds the starter, emits the mode-appropriate authoring slot, stubs a `verified:false` sidecar, stops.

The agent authors the plan/narration but **never signs** — a human runs
`verify.py sign` (or the book's own copy), exactly as GATE 3 is human-only. The
lecture spine is now a first-class AI+1 artifact.

## The "two physics profs" vision, located in the machinery

The professor's conversational refinement — *"change this, re-voice that"* — already has
its home: AI+1's **`voices/`** system (Wonder, Socratic, Pragmatist, Sardonic, Narrative,
Generic) rewrites `chapters/` into a register without touching the originals, and
**Human-Rewrite (GATE 3)** is the human-only phase where a book becomes *theirs*. Two
physics profs diverging from one base is `voices/` + GATE 3 + the lecture spine, applied to
the same fact-checked chapter. The spine is what makes that divergence start from a
watchable, accurate draft instead of a blank page.

## Honest tensions worth naming

- **facts/ exists twice** — standalone and synced-into-each-book. That is by design (books
  stay self-contained) but means "the commons" is really many copies that must reconcile.
  A merge/reconcile story across book copies is unspecified.
- **Two gate systems risk drift.** If the lecture spine keeps its own `decision_log`/QC
  and AI+1 keeps `.verified.json`/`STATUS`, they will diverge. Pick AI+1's as canonical and
  make the spine emit into it.
- **The video bridge is thin.** `higgsfield/` + `vids/_chapters.json` identify candidates,
  but the handoff from "candidate topic" to "silent_run builds the lecture" is not yet one
  command. That seam is the natural next integration.
