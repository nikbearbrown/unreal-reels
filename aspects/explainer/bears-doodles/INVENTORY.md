# Bear's Notes — inventory & publish-readiness (Cowork/Manim)

Health check of the hand-built set, scored against the locked **two-video model**: each concept publishes a **1-min 9:16 Short** + a **2–5 min deep 16:9**. (Codex's ~275 rough-batch set is not in this mount — inventory it separately.)

## Baseline health — all green
- 25 folders, **all scenes compile**, **all have audio** (`mp3/timings.json`).
- 24 have a 16:9 master rendered. **1 missing render:** `why-lasers-make-photons-march-together` (no 16:9).

## Publish-readiness (the part that matters before posting)

| Concept | 1-min 16:9 | 9:16 Short | deep 16:9 | portrait-ready | **Publish-ready?** |
|---|---|---|---|---|---|
| energy-levels-arent-evenly-spaced (+ -n-squared-worked) | ✅ | ✅ | ✅ | ✅ | **YES** (verify deep render) |
| the other 24 (1-min) | ✅ | — | — | — | **No** — need 9:16 + deep |

**Bottom line: 1 of 25 concepts is publish-ready under the two-video model.** The 24 existing 1-min 16:9 masters are *intermediates*, not posts — the published surfaces are the 9:16 Short and the deep 16:9, and only energy-levels has both.

## What each of the 24 needs (the remaining work)
1. **Portrait conversion → 9:16 Short.** Only energy-levels imports `bn_layout`; the other 24 are landscape-only and would render broken at 9:16. Each needs its bespoke panel-stacking pass (the `bn_layout` engine + per-scene `_portrait_L`).
2. **`expand` → deep 16:9.** A 2–5 min worked-example version (idea→math→worked example→predicts). None exist yet except energy-levels.

So the gate for the whole library is the two rollouts we've only proven on energy-levels.

## The full concept list vs what's built
The ~70-concept master list (Waves/Uncertainty, Tunneling, Atoms/Spin/Light, Measurement, Quantum Information, Solids/Scattering) is the *intended* library. **25 exist here in Cowork**; the rest live in the Codex batch (not in this mount) and are unverified ("fast but sloppy").

## Recommended path
1. **Verify the energy-levels deep render** (the one true pair) → post it as the first concept. This proves the full two-video pipeline end to end on YouTube.
2. Pick the **next 2–3 strongest concepts**, run them through: portrait conversion (9:16 Short) + `expand` (deep 16:9) → publish-ready pairs.
3. Only then scale. The publish script already refuses anything not fully paired, so nothing half-built can leak out.

## Anomalies to fix
- `why-lasers-make-photons-march-together`: render its 16:9 (then portrait + deep like the rest).
