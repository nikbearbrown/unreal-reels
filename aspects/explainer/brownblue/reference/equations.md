# Brown Blue — the equation tangent (a fixed template)

The brownblue port of the lecture equation rule (`brutalist/EQUATIONS.md`).
**Every time a finished equation lands on screen, the video takes a short
tangent (~30–45s) to unpack it before moving on.** It is a repeatable beat
pattern that fires every time, so explanation quality never depends on
improvising. A tangent **explains — it never derives.**

## Reconciling with the 3b1b arc (read this first)

brownblue already *earns* the equation by motion: the `ABSTRACTION` beat is the
symbol arriving as an endpoint of the moving instances (pedagogy §1.4, §4). That
arrival is the derivation, and it stays — "transform, don't cut" (style.md).

The tangent is **not** a second derivation. It fires **immediately after** the
`ABSTRACTION` beat, with the finished equation already on screen, and does the
*unpacking* the arrival glossed over: which side means what, what each symbol
is, and one concrete number run through it. Derivation = the ABSTRACTION beat
(motion). Explanation = the tangent (these five zones). Keep them distinct.

## The five zones (a fixed master, not ad-hoc beats)

The equation is rendered once in `MathTex` and **persists** in the MAIN region.
Each zone writes-on into the SIDE band (the `energy-levels-arent-evenly-spaced`
MAIN/SIDE `band()` split — see SKILL.md `manim`), one zone per narration line.
Never re-draw the equation per zone; reveal beside it.

1. **Symbolic form** — the equation, large, isolated, high contrast, real
   `MathTex` (Computer Modern). This is the just-arrived ABSTRACTION beat; the
   tangent opens with it already on screen.
2. **LHS / RHS as sentences + the sign as a claim** — translate each side into
   ONE plain sentence **before** naming any symbol, then a third sentence that
   reads the *relation symbol itself as a claim about the world* — not
   punctuation. `=` "must be exactly equal," `≤` "can be no bigger than," `≈`
   "is close to," `∝` "grows in lockstep with," `:=` "is defined as," `argmax`
   "is the choice that maximizes." Audiences parse the claim type faster than
   the notation.
3. **Glossary with a Role column** — every symbol gets: `Symbol | Role | Plain
   meaning | Domain/Range`. The **Role** column is the one most explainers skip
   and audiences most need — distinguish *variable* vs *fixed constant/label*
   vs *index* vs *operator* (`ψ` the function vs its value at a point; `n` the
   quantum number vs a specific `n = 1`). Symbols in `MathTex`, plain-meaning in
   EB Garamond, any standalone number in JetBrains Mono.
4. **Worked example that holds or breaks** — one concrete scenario with real
   numbers: plug into each side, show the comparison explicitly
   (`E₂ = 4E₁`, not "scales with n²"), and one sentence on what the result
   *means physically for the system*. Let them feel it, don't just describe it.
   Numbers in mono.
5. **The claim it commits you to** — state what the equation *asserts about the
   world*, phrased so someone could question it, not as neutral fact. For a
   value-laden equation (fairness, economics) this is the contestable value
   judgment. For a physics equation it is the **physical commitment** — the
   assumption you are buying ("energy comes only in these steps — no in-between
   values exist"). Optional only when the equation is pure bookkeeping.

**Division of labor:** the ABSTRACTION beat already shows zone 1 and gestures at
2. The **tangent supplies what the arrival skipped: the LHS/RHS sentence split,
the Role glossary, and the worked example.** Don't repeat the arrival — extend
it.

## Color: the moving spotlight (one highlight, not a rainbow)

Couple a symbol across the equation, its glossary row, and its value in the
worked example so the eye tracks one symbol instead of scanning — but do it
**within the one-emphasis rule** (style.md). The symbol *currently being
explained* turns `--highlight` in all three places at once, advancing with the
narration line; everything not spotlighted stays ink/secondary. Same coupling
benefit, one accent, and never two highlights at once. Blue stays THE OBJECT,
brown stays its foil — the spotlight is the transient highlight channel, never a
new hue. **No red, ever** (`forbidden_color` — that's the lecture brand).

## Typesetting

- The symbolic form is **real math** — italic variables (Roman + Greek), roman
  operators/numbers/functions (`log`, `max`, `sin`). `MathTex`, never a
  screenshot. JetBrains Mono is reserved for the worked example's *data numbers*,
  not the equation.
- Proper minus (`−`), true Greek glyphs (`ψ`, `ℏ`, `Δ`), hats/bars in the
  `MathTex` (`\hat{H}`, `\bar{\psi}`); spell them out ("psi", "h-bar",
  "delta x") only in narration / `tts_normalized_text`, per the shared symbol
  normalization (bears-doodles storyboard.md).

## Entry & re-entry (don't lose the throughline)

- **Entry marker:** a small EB Garamond eyebrow label on the SIDE band
  (`<CONCEPT> · equation`) + a thin brown rule, so the viewer recognizes "we've
  branched to unpack this symbol" — a recurring, legible feature.
- **Re-entry cue:** the narration ends by handing back to the main argument —
  *"…and that's why the levels go as n squared. Now, back to the well."* Always
  return the viewer to where the tangent branched (this is the discovery voice,
  pedagogy §3, not "it can be shown that").

## How it lives in the beat sheet (brownblue has no tangents.json)

deck-lecture stores the tangent as data in `tangents.json` and renders it with a
Remotion component. **brownblue has neither** — it is one Manim scene — so the
tangent is authored as a **bracket of ordinary beats** in `beat_sheet.json`,
each `render: manim`, each carrying the role note `TANGENT` in
`new_visual_element`, sitting immediately after the `ABSTRACTION` beat:

```
ABSTRACTION   the equation arrives (MAIN region, MathTex, persists)
TANGENT       LHS sentence · RHS sentence · the sign-as-claim        (zone 2)
TANGENT       glossary rows write on, Role column                    (zone 3)
TANGENT       worked example: numbers plug in, comparison holds/breaks (zone 4)
TANGENT       the claim it commits you to                            (zone 5, opt.)
TANGENT       re-entry — hand back to the main argument
```

Zones may merge into fewer beats when the equation is simple (a two-symbol
relation needs no four-row glossary), but the **order** 2→3→4→(5)→re-entry is
fixed, the equation **persists** across all of them, and the whole bracket is
**≤ ~45s of audio** (real MP3 duration — one sentence per beat, ≤ ~40 words,
glossary excepted). Each spoken beat keeps both `narration_text` (symbols, for
captions) and `tts_normalized_text` (spoken form).

## Pedagogy (why this order) + lineage

- **Words → symbols → number** is the worked-example effect: one concrete
  instantiation teaches more than restating the definition twice (Sweller &
  Cooper, 1985).
- **Reveal one zone at a time beside a persistent equation** = split-attention +
  spatial-contiguity + segmenting (Mayer); the moving spotlight is signaling.
- **Sentence-before-symbol** follows the 3Blue1Brown / Strogatz model: state the
  claim type before decomposing notation — the same instinct as the rest of this
  skill.
- One example, numbers in mono, ≤ ~45s, **never derive** (the derivation was the
  ABSTRACTION beat).

## Audit (per equation — run at `beats`, re-check at `manim`)

1. A TANGENT bracket exists after **every** equation that lands on screen.
2. Sentences before symbols; the relation sign stated as a claim.
3. Glossary has the Role column; variable ≠ value, function ≠ its value kept
   distinct.
4. Worked example shows a real comparison that **holds or breaks**, with a
   physical/consequential meaning line; numbers in mono.
5. The equation persists (one `MathTex`, transformed/kept — not re-drawn per
   zone); spotlight is the single `--highlight`, no red, one emphasis at a time.
6. Entry eyebrow present; narration ends with a re-entry cue.
7. Whole bracket ≤ ~45s of measured audio; no second derivation.
