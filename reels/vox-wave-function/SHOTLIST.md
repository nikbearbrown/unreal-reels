# SHOTLIST — vox-wave-function

Typed work order. `pantry` command applies: drop restored beat-prefixed assets
into `pantry/`, portrait clips auto-become `-916` overrides. Set `shot.focus`
per still after intake. GRAPHIC beats render from this reel's `vox_scenes.py`
after audio lock.

Shot-type histogram: GRAPHIC 7 · STILL 3 · CARD 2 · DOCUMENT 1 · COMPOSITE 1
(14 beats, GRAPHIC 50% — accepted; tangent + phase section are the evidence).
Rhythm note: T01–T03 + B06–B08 is a 6-beat GRAPHIC run — accepted like the
matter-waves evidence run; B05 DOCUMENT breaks the front, B09 COMPOSITE the
tail.

**REMOTION PLANE ACCEPTANCE TEST: B05 (document annotation), T01–T03
(word-keyed spotlights), B10 (kicker typography), credits block. Draft
authoring surface: `annotations.json` — every region is needs_review until
the B05 scan is in hand.**

---

## Archive / people slots (YOURS)

### B01 — STILL · Max Born, Göttingen 1926 (cold open)
- https://commons.wikimedia.org/w/index.php?search=Max+Born+physicist&title=Special:MediaSearch&type=image
- https://commons.wikimedia.org/wiki/Category:Max_Born

People prompt:
```
Hyper-realistic portrait of a 43-year-old Max Born, 1926, German physicist at his desk in Göttingen, wire-rimmed glasses, manuscript pages before him, in the style of Edward Burtynsky, hyper-realist photograph, clean sharp focus, clear facial features --ar 16:9
```

### B03 — STILL · Erwin Schrödinger, 1926
- https://commons.wikimedia.org/w/index.php?search=Erwin+Schr%C3%B6dinger&title=Special:MediaSearch&type=image

People prompt:
```
Hyper-realistic portrait of a 38-year-old Erwin Schrödinger, 1926, Austrian physicist, round glasses, chalk equations on a blackboard behind him, in the style of Edward Burtynsky, hyper-realist photograph, clean sharp focus, clear facial features --ar 16:9
```

### B05 — DOCUMENT · Born's 1926 paper, THE FOOTNOTE (archive scan — the plane beat)
The footnote ("Anmerkung bei der Korrektur") lives in the PRELIMINARY note:
Born, "Zur Quantenmechanik der Stoßvorgänge", Z. Phys. **37**, 863 (1926) —
not the fuller vol 38 paper the chapter cites. Get the page carrying the
footnote; reconcile the citation in FACTCHECK.md.
- https://archive.org/search?query=Zeitschrift+f%C3%BCr+Physik+37+1926
- https://www.digizeitschriften.de/ (Zeitschrift für Physik 37, 863)
- https://commons.wikimedia.org/w/index.php?search=Born+Quantenmechanik+Sto%C3%9Fvorg%C3%A4nge&title=Special:MediaSearch

Published 1926 → US public domain; `.source.txt` sidecar mandatory. After
download: crop per pantry law (title survives), then set the THREE regions in
`annotations.json` (draft-ψ phrase · footnote |ψ|² · push target) by eye —
they ship as needs_review placeholders.

### B09 — COMPOSITE·ai · detector plate (moral beat)
```
macro photograph of a dark laboratory detector plate with faint white dot impacts accumulating in soft bands, shallow depth of field, moody studio lighting, photoreal --ar 16:9
```
Chips ("NOT the particle / THE RULE for the odds") land at assembly on the
Remotion plane; degrades to clean plate.

### B10 — STILL · Born kicker (direct gaze)
People prompt:
```
Hyper-realistic portrait of a 43-year-old Max Born, 1926, German physicist, direct gaze, quiet half-smile, in the style of Edward Burtynsky, hyper-realist photograph, clean sharp focus, clear facial features --ar 16:9
```
Kicker typography (Max Born · 1882–1970 · "Einstein's dice letter was
addressed to him.") renders on the Remotion plane; degrades to serif label.

## GRAPHIC slots (PIPELINE — render after audio lock)

| beat | scene | what |
|---|---|---|
| B04 | B04_TheCurves | ch-0 simulation palette: blue \|ψ\|² filled, orange Re ψ, gray dashed Im ψ, drifting + spreading; '?' chip on 'mean' |
| T01–T03 | T01_EqSentences / T02_EqGlossary / T03_EqExample | tangent P = ∫ₐᵇ\|ψ\|²dx (spotlights P → ψ → \|ψ\|²; example: 1−e⁻² ≈ 86.5%, peak 2 nm⁻¹) |
| B06 | B06_TwoPackets | identical humps, k₀ = ±5 nm⁻¹, opposite drift; phase ripples tilt opposite; crimson/navy arrows |
| B07 | B07_TheStructuralI | iℏ∂ψ/∂t = Ĥψ card, hand-ring the i; Im ψ zeroed → one tick → springs back |
| B08 | B08_DotsBuildTheCurve | spreading envelope; dots land singly, histogram grows into \|ψ\|² (echo of film three's buildup) |

## CARD slots (PIPELINE)

B02 title, B11 next-tease (THE SCHRÖDINGER EQUATION) — copy in beat_sheet.

## VERIFY before render (all to be recomputed in FACTCHECK.md)

- Footnote paper: Z. Phys. 37, 863 (1926) preliminary note vs chapter's
  38, 803 citation — reconcile; draft P ∝ ψ, corrected ∝ |ψ|²
- 1 − e⁻² = 0.8647 → "eighty-six percent"; a = 0.5 nm → |ψ(0)|² = 2 nm⁻¹
- Gaussian: |ψ|² = A²e^(−x²/a²) — k₀ absent; Re/Im both carry k₀ (chapter)
- Real ψ ⇒ iℏ∂ₜψ imaginary vs Ĥψ real ⇒ contradiction (chapter)
- Einstein dice letter TO Born, 4 Dec 1926 (Born–Einstein Letters)
- Nobel 1954 = 28 years after 1926; Born 1882–1970, age 43 in mid-1926;
  Schrödinger b. 1887, age 38 in 1926
- Sim palette: |ψ|² blue filled, Re ψ orange, Im ψ gray dashed (ch 0 / ch 3)
