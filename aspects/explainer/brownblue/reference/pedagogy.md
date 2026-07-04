# Brown Blue — the pedagogical constitution

The 3Blue1Brown template, operationalized. Sanderson's stated principles
(concrete-before-abstract, open with the key exercise, story over utility,
"inventing math," the density trade-off, explain-not-educate) converted into
gates the `script` and `beats` commands enforce. This file is the reason the
skill exists; the look in style.md is downstream of it.

## §1 The sequencing checklist (Gate 1 — hard requirements)

A script fails Gate 1 unless all five hold:

1. **The key exercise/key case is identified and named** in one line at the
   top of the script draft (not in the video): the concrete puzzle,
   computation, anomaly, or before/after contrast that motivates everything.
   - *Problem topics*: the puzzle itself (it supplies its own start and end).
   - *Expository topics*: a key case — a representative event, an anomaly, or
     a fact-that-should-predict-but-doesn't (same DNA, different disease).
2. **The video opens with it, unsolved.** No vocabulary, no notation, no
   "today we'll cover" before the viewer has felt the problem.
3. **Concrete instances precede every abstraction.** At least two
   parametrized instances of the phenomenon are *shown moving* before the
   general statement is made. (Manim makes instances cheap — vary the
   parameter, replay the transformation. Use that.)
4. **Definitions are endpoints.** A term or symbol is introduced only after
   the viewer has enough concrete structure to *want* a name for it. The
   test: could the narration say "this thing we keep pointing at deserves a
   name" and have it feel overdue? If not, the definition is too early.
5. **No premature completeness.** Nothing is included "for completeness."
   Edge cases, generalizations, and caveats that don't serve THIS video's one
   insight are cut or deferred to a follow-up video (log them in the script
   draft under "deferred").

The failure mode being guarded: sequencing the material the way an expert
stores it (general → examples) instead of the way a first-time learner can
receive it (example → felt need → name). Rigor-ordering splits the audience;
concrete-ordering carries it.

## §2 Mystery framing, not utility framing (Gate 1)

The opener is **mystery-framed**: a specific tension the viewer needs
resolved. Utility framing is banned as an opener (it may appear near the end,
briefly, if at all).

- Utility (banned as opener): "Understanding X is critical for Y. Today
  we'll cover how X works." — gives away the use case, generates no pull.
- Mystery (required): state the fact that *should* predict an outcome, then
  the case where it doesn't. "Two identical twins, identical DNA. One
  develops the disease. The other never does." The abstraction later arrives
  as the *answer* to this tension.

The generalizable move: **find the gap between what the rules predict and
what actually happens.** That gap is the video.

## §3 Discovery narration ("inventing math")

Narrate as re-invention, not transmission. The viewer should feel walked
through reasoning that *could plausibly have led* to the discovery — not
handed the polished, discovery-erased final form.

- Voice moves: "what if we tried—", "notice what just happened", "so we're
  stuck — unless—", "you might guess... and you'd be almost right."
- Wrong turns are allowed and valuable when they're the *natural* wrong turn
  (the one the viewer would take), shown briefly and corrected on screen.
- Never "it can be shown that." If it can be shown, show it; if showing it is
  out of scope, say so plainly and point to where (the boundary beat, §7).

## §4 Beat roles (Gate 2 — the beat sheet is audited against this arc)

Every beat gets a role; the roles must appear in this partial order:

```
HOOK        the key exercise/case, unsolved (opens the video)
INSTANCE    a concrete parametrized example, shown moving   (≥2 before any ABSTRACTION)
TRANSFORM   the same object morphing — the intuition carrier
ABSTRACTION the general statement/definition — arrives as an ENDPOINT
PAYOFF      the hook resolved by the abstraction; optionally one scale-shift
BOUNDARY    what this video did NOT teach + the viewer's exercise (fused with OUTRO)
```

Audit rule: walking the beat sheet top to bottom, an `ABSTRACTION` beat with
fewer than two prior `INSTANCE` beats *for that abstraction* is a Gate-2
rejection. The PAYOFF must reference the HOOK explicitly (same object back on
screen — persistent objects, not a re-draw).

(Schema mapping: these roles ride in the shared bears-doodles schema —
`beat_type` keeps its ACCUMULATE/CUT/HOLD/ZOOM mechanics; the role is recorded
in the beat's `new_visual_element`/notes so the audit can read it.)

## §5 The length procedure (run at `script`, report at Gate 1)

Length is **derived**, never chosen. Compute it:

1. Count the arc: 1 HOOK + N INSTANCEs (usually 2–4 per abstraction) +
   A ABSTRACTIONs (usually 1, sometimes 2) + 1 PAYOFF + 1 BOUNDARY/OUTRO.
2. Each beat is one sentence ≈ 5–9 s of narration at Bear-voice pace.
3. Add hold time: a built-up idea gets the seconds it needs to be looked at
   (HOLD beats are legitimate; silence over a finished picture is teaching).

Tiers this produces:

| Tier | Arc | Typical runtime |
|---|---|---|
| **Single-insight** | 1 abstraction, 2 instances | 2–4 min |
| **Standard** | 1–2 abstractions, an act break | 4–8 min |
| **Multi-act** | 2+ abstractions, each with its own mini-hook | 8–15 min — needs explicit user approval at Gate 1 |

Two prohibitions: **never pad** (no filler beats to reach a "good YouTube
length") and **never rush** (no cutting an INSTANCE to hit a duration — cut
scope instead: fewer abstractions, deferred follow-up video).

## §6 The density rule (applies at `script`, again at `beats`)

Err toward more detail *in the draft*, then cut **during scripting, never
during animation**. For every anticipated viewer question, three options:

1. Answer it inline if the answer fits in ≤2 beats and serves the one insight.
2. Defer it — name it in the BOUNDARY beat ("why this works for complex
   numbers too is its own video").
3. Cut it silently.

If a detour needs >2 beats, it is by definition a deferral or a cut. The
Gate-1 audit table lists every detour and which of the three it got.

## §7 The boundary — explain, don't educate

An explainer is the intuition half. It does not replace practice, assessment,
or procedural fluency, and it must not pretend to.

- Every video ends with a **BOUNDARY beat** (fused with the outro): one
  sentence naming what was deliberately not taught, and **one concrete
  exercise the viewer can do** with what they now have. The exercise is the
  handoff from explanation to instruction.
- Scope discipline follows: brownblue videos accompany a chapter/course; when
  the source is a book chapter, the packaged YouTube description links the
  chapter as the practice surface.
- Never claim the video "teaches you X." It shows why X is true and what it
  feels like; the viewer still has to go do X.

## §8 Gate-1 audit table (the `script` command shows this, filled)

| Check | Ref | Pass? |
|---|---|---|
| Key exercise / key case named | §1.1 | |
| Opens unsolved, zero vocabulary before the felt problem | §1.2, §2 | |
| ≥2 moving instances before each abstraction | §1.3 | |
| Every definition arrives as an endpoint | §1.4 | |
| Nothing included "for completeness"; deferrals logged | §1.5, §6 | |
| Mystery-framed opener (utility framing absent) | §2 | |
| Discovery voice; no "it can be shown that" | §3 | |
| Length derived + tier reported; no pad, no rush | §5 | |
| Boundary beat: not-taught + viewer exercise | §7 | |
