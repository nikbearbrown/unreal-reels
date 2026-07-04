# Expand — energy levels (deep / long-form)

**This is the 2–5 min 16:9 "expand" of the 1-minute explainer.** 16:9 only (no 9:16 — this is the funnel *destination*, the Short links here). Arc: reuse the 1-min intuition → map the idea to the math → worked example → what it predicts → recap.

- **Proposed slug:** `energy-levels-n-squared-worked`
- **Title options (search-keyworded, long-form):**
  - "Particle in a Box: Where the n² Energy Formula Comes From (Worked Example)"
  - "Why Quantum Energy Grows as n² — The Formula, Worked Through"
- **Est. length:** ~3 min (32 beats). **16:9 only.**
- **Funnel role:** the 1-min Short's Related Video points here.

Legend: **[reuse]** = carried from the 1-min (familiar on-ramp); **[NEW]** = depth the Short never showed; `[CUT]` = scene change.

---

### A — Intuition on-ramp  [reuse, condensed]
1. *(INTRO)* Bear's Notes — Why quantum energy levels grow as n².
2. You'd expect a ladder of energy rungs to be evenly spaced, like a normal ladder. `[reuse]`
3. But a quantum box's rungs fan apart the higher you climb. `[reuse]`
4. A particle trapped in a box can only be the standing waves that fit exactly. `[reuse]`
5. The lowest fits half a wave; the next a full wave; then one and a half. `[reuse]`
6. Its energy climbs as one, four, nine, sixteen — the squares. `[reuse]`
7. The gaps — three, five, seven — keep widening. `[reuse]`

### B — Idea → math (the bridge)  `[CUT]` [NEW]
8. Let's turn that picture into a formula.
9. Level n fits n half-waves across a box of width L.
10. So its wavelength is lambda-n equals two L over n.
11. More half-waves means a shorter wavelength.
12. A shorter wavelength means more momentum: p equals h over lambda.
13. And kinetic energy grows as momentum squared — E equals p-squared over two m.
14. Substitute, and the n lands upstairs, squared.
15. E-n equals n-squared times h-squared over eight m L-squared.
16. The n-squared isn't a coincidence — it's the wavelength, in the denominator, squared.

### C — Worked example (the spine)  `[CUT]` [NEW]
17. Now let's put real numbers on it.
18. Take an electron in a box one nanometer wide.
19. Plug in: the ground state, E-one, is about zero point three eight electron-volts.
20. The second level is four times that — about one point five electron-volts.
21. So the jump from level one to level two costs about one point one electron-volts.
22. That energy leaves as a single photon.
23. Its wavelength is h c over E — about eleven hundred nanometers.
24. Near-infrared light, set entirely by the size of the box.

### D — What it predicts (real-world tie)  `[CUT]` [NEW]
25. This is exactly how a quantum dot works.
26. Shrink the box and every energy scales up as one over L squared.
27. Smaller dots jump higher and glow bluer; larger dots glow redder.
28. A quantum dot's color is just this formula, made visible.

### E — Recap + outro  `[CUT]`
29. So the rungs fan out as n-squared because energy lives in the square of the momentum.
30. And momentum climbs with every half-wave you add to the box.
31. Same picture as the short — now with the numbers behind it. `[reuse callback]`
32. *(OUTRO)* Thanks for watching — find more Bear's Notes at youtube.com/@NikBearBrown.

---

### Physics check (numbers are sound)
E_n = n²h²/(8mL²). Electron, L = 1 nm → **E₁ ≈ 0.38 eV**, E₂ = 4E₁ ≈ 1.50 eV, **gap ≈ 1.13 eV**, photon λ = hc/E = 1240 eV·nm ÷ 1.13 eV ≈ **1097 nm** (near-IR). Quantum-dot color ∝ 1/L² is the standard particle-in-a-box result. All verifiable.

### What Manim animates (new beats)
- **B (idea→math):** the standing wave morphs while `λ = 2L/n`, then `p = h/λ`, then `E = p²/2m` assemble into `Eₙ = n²·h²/8mL²` — each substitution written as the prior picture transforms. (MathTex.)
- **C (worked example):** the formula stays on screen; real numbers slot into L, n; E₁, E₂, the gap, and λ compute one line at a time. A photon arrow leaves at 1100 nm.
- **D (predicts):** two boxes, small vs large; the small one's rungs higher, its glow bluer.
