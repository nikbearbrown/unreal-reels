# Decision table — evidence-grounded media selection

The matrix the router applies. Grounded in CTML (Mayer) + Cognitive Load Theory
(Sweller) and the animation / realism / signaling literatures. **Effect sizes here are
the *independent* meta-analytic estimates, not Mayer's in-house numbers** — his lab runs
roughly 3× larger and have declined ~0.01/year for 33 years (Cromley & Chen, 2025), so
treat the in-house d ≈ 0.86–1.10 figures as upper bounds and use these instead.

Context this is tuned for: 1–4 min audio-first explainers, ~5–15 s beats,
university-level STEM (biology, cancer biology, physics).

---

## 1 · Process or mechanism
*DNA replication fork, electron transport chain, metastasis cascade, signal transduction.*

- **Default: Manim.** Confidence **Moderate** (not high — see below).
- **Rationale.** Mechanisms are dynamic (temporal order, causal sequence), which fits
  Tversky & Morrison's *congruence* principle, and a schematic build enforces temporal
  contiguity + segmenting ("one element per spoken idea"). Manim is schematic
  (low seductive-detail), pixel-precise, and controllable.
- **Honest caveat.** Animation's advantage over well-designed static graphics is small
  (Höffler & Leutner 2007, d = 0.37; Berney & Bétrancourt 2016, g = 0.226) and is
  *reliable only when the features of change — direction, speed, trajectory, sequence —
  are themselves the learning target* (Ploetzner et al. 2020, 194-study review).
  Sequential static frames often tie animation (Hegarty, Kriz & Cate 2003); learners
  mentally animate static diagrams, so animation mainly compensates for low spatial
  ability (Hegarty 2004). Progressive *drawing* has modest support for novices
  (Fiorella & Mayer 2016, transfer d ≈ 0.4–0.6; the benefit is the pacing, not a
  visible hand — Zhang et al. 2024).
- **Why Manim is still the default:** control + accuracy + schematic register + cheap
  "one element per idea" — it at least ties static while dodging seductive-detail and
  AI-accuracy traps. Defend it on *production* grounds, not "animation teaches better."
- **Override → Remotion sequential stills** if the mechanism is ≤3 discrete states or is
  really about labeled anatomy (evidence-equivalent, cheaper). **Override → T2V** only
  for genuine macro/motor-procedural motion (hands, physical manipulation; Höffler &
  Leutner procedural-motor d = 1.06).
- **Never T2V/T2I** for invisible/molecular mechanisms (confabulation → false schema).

## 2 · Equation or quantitative relationship
*F = ma, Nernst equation, rate laws, a derivation.*

- **Default: Manim.** Confidence **High**.
- **Rationale.** Requires pixel-precise notation (LaTeX) and benefits from animating the
  *derivation* — the worked-example effect is among CLT's most robust findings
  (Sweller & Cooper 1985; Barbieri et al. 2023 meta, g = 0.48). Color-coding changing
  terms adds signaling cheaply (Schneider et al. 2018: retention g = 0.53, transfer
  g = 0.33; Ozcelik et al. 2009 halved search time).
- **Override → Remotion static (permanent on screen)** for long, multi-step derivations
  that need backward cross-reference. A complex equation narrated and then replaced
  triggers the *transient information effect* and working-memory collapse (Leahy &
  Sweller 2011; Wong et al. 2012) — keep it permanent or segment it across held frames.
- **Never T2V/T2I** — they hallucinate subscripts, operators, symbols.

## 3 · Static labeled structure or diagram
*Cell organelle map, anatomical cross-section, circuit, crystal lattice.*

- **Default: Remotion compositing a *vetted* illustration**, with animated labels /
  progressive reveal. Confidence **Moderate**.
- **Rationale.** Purpose is spatial, not temporal; animation adds little over a
  well-labeled static (Ploetzner 2020; three anatomy studies found no animation
  advantage). What helps: spatial contiguity of labels to referents (Schroeder & Cenkci
  2018, g = 0.63) and signaling. Remotion gives precise label placement + Ken-Burns
  cueing in sync with narration.
- **Accuracy red flag (load-bearing).** AI image generators distort scientific structure
  badly — gross anatomical errors are the norm, ~50% of generated human figures show
  severe distortion. A **non-expert author cannot vet these.** "Vetted T2I" means
  genuinely expert-reviewed, or use a pre-existing reviewed illustration. Otherwise
  build a schematic to spec.
- **Override → Manim** if the structure is *geometric/abstract* (crystallography unit
  cells, graph-theory structures, Venn/set diagrams) — Manim is native there.

## 4 · Data or quantities
*Dose-response curve, survival curve, scatter, bar chart of results, time-series.*

- **Default: Remotion** (data viz), progressively revealed. Confidence **High**.
- **Rationale.** Axes/labels must be exact (never T2V/T2I). Reveal data in narrated order
  (temporal contiguity + signaling). Use position-on-common-scale encodings (bars, not
  pie; Cleveland & McGill 1984) and a **descriptive title stating the relationship** —
  titles are the single strongest predictor of chart recall (Borkin et al. 2013).
- **Avoid animated trends for analysis.** Animated bubble/Gapminder-style charts are
  *worse* than static small-multiples for accuracy (Robertson et al. 2008; replicated
  Brehmer et al. 2019) — viewers feel more confident but are less accurate.
- **Override → Manim** for an analytically-defined curve (sine, exponential decay,
  normal) being built from a formula.
- **Caveat:** ~⅓ of adults have low graph literacy (Galesic & Garcia-Retamero 2011) —
  for general audiences, narrate the takeaway; don't assume the chart speaks for itself.

## 5 · Real-world or human context
*"What a biopsy looks like," a clinical scene, scale of a virus, motivational framing.*

- **Default: Text-to-image** (Ken-Burns in Remotion). T2V **only** when the motion
  itself is the instructional content. Confidence **Low–Moderate** (thin evidence).
- **Rationale.** The one beat type where photorealism can serve learning — establishing
  *why* the content matters and anchoring it to a real referent — *but only when the
  perceptual features of the real object are what's being taught.* Realism can act as a
  retrieval cue **only when encoding and test formats match** (Skulmowski & Rey 2021);
  otherwise it's just load, and learner *preference* for realism does not predict
  learning (naive-realism dissociation).
- **Seductive-detail gate.** If the image/clip doesn't serve *this beat's* objective,
  it's a seductive detail and harms learning (Sundararajan & Adesope 2020 meta,
  g ≈ −0.37 to −0.41; worst when it appears early). Prefer T2I over T2V (lower
  uncontrolled complexity, higher control).
- **Never** for precise molecular/mechanistic/anatomical accuracy — generative video
  introduces physical impossibilities and reinforces misconceptions.

## 6 · Definitional, title, or typographic
*Term introduction, takeaway restatement, section title.*

- **Default: Remotion**, key term only. Confidence **High**.
- **Rationale.** Cue the key term visually as it's spoken (signaling, temporal
  contiguity) — but **≤2–3 words**, a label/anchor, not a transcript. Full on-screen
  sentences duplicating narration trigger the redundancy effect.
- **Redundancy nuance.** The lab redundancy harm is *contested in real multi-minute
  academic video*, where captions help focus, accessibility, and non-native speakers.
  Resolve it by channel: a **toggleable caption track** (off by default) is fine;
  **burned-in verbatim text** in the composition is the violation.
- **Override → Manim** only if the term carries math notation needing LaTeX (Kd, ΔG).

---

## Global fallback (no usable content type)

**Remotion, static schematic diagram with focused labels.** Lowest cognitive risk:
information permanence (no transience), self-paced label↔structure saccades, minimal
seductive detail. Never fall back to a generative-video / photoreal default.

## Confidence & contested ground (don't paper over these)

- **Strong / well-replicated:** seductive details harm learning; signaling helps
  (g ≈ 0.33–0.53); spatial contiguity helps (g ≈ 0.63); worked examples help novices
  (g ≈ 0.48); transient-information effect; overall animation edge is *small*
  (g ≈ 0.23–0.37). Engagement ≠ learning (animated-vs-talking-head null; "like it,
  don't learn from it"; illusion of understanding for slick math animation).
- **Moderate / judgment calls:** Manim-for-mechanisms over sequential statics (rests on
  control + temporal-contiguity rationale, not a strong head-to-head); optimal realism
  level for STEM structure beats; T2I-vs-T2V for context (no direct RCT).
- **Thin / open:** no RCT compares Manim vs. Remotion vs. T2I vs. T2V on STEM learning
  outcomes — the biggest gap. Generative video has *no* peer-reviewed learning benefit
  and comes out null on transfer so far. Revisit as evidence accumulates.
- **Effect-size health warning:** prefer independent estimates over Mayer-corpus
  in-house numbers (Cromley & Chen 2025).
