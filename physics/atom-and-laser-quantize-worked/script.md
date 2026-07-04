# Why an Atom and a Laser Quantize for the Same Reason — Worked Example (deep / 16:9)

Deep expand of `atom-and-laser-quantize-for-same-reason` (Vol.1 Ch.4, Candidate 11).
Idea → math → worked example → prediction → recap. SILENT scene; ElevenLabs VO muxed by assemble.py.

## The one idea
A wave trapped between two walls must vanish at both ends. That happens only when a
whole number of half-wavelengths spans the gap:

    n·λ/2 = L   →   λ_n = 2L/n

Every quantized system in the chapter is this rule wearing a different coat.

## Two branches from the one rule
- **Laser cavity** — frequency f = c/λ, so the allowed colours are f_n = n·c/(2L),
  evenly spaced by Δf = c/(2L).
- **Electron in a box** — momentum p = h/λ and E = p²/2m, so the allowed energies are
  E_n = n²h²/(8mL²).

## Worked numbers
**Laser cavity, L = 0.30 m:**
- Mode spacing Δf = c/(2L) = (2.998×10⁸)/(0.60) = 4.997×10⁸ Hz ≈ **500 MHz**.
- Half-waves of red HeNe light (λ = 632.8 nm): n = 2L/λ = 0.60/632.8×10⁻⁹ ≈ **9.5×10⁵**.

**Electron in a box, L = 1 nm:**
- E₁ = h²/(8mL²) = (6.626×10⁻³⁴)²/(8·9.109×10⁻³¹·(10⁻⁹)²) = 6.03×10⁻²⁰ J ≈ **0.38 eV**.
- E₂ = 4·E₁ ≈ **1.5 eV** (first gap ΔE ≈ 1.1 eV).

## Prediction
Spacing falls as L grows (∝1/L for the cavity, ∝1/L² for the box): widen the box or
lengthen the cavity and the rungs crowd together. Same rule, two scales — modes you
hear as colour, modes you measure as energy.

## Beats
INTRO · H01 · H02 · A01–A02 (intuition) · M01–M04 (idea→math) · W01–W04 (worked) ·
P01–P02 (predicts) · R01–R02 (recap) · OUTRO.
