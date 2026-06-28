# Codex task — render & publish the deep video `energy-levels-n-squared-worked`

This is a **deep / long-form expand** (the funnel destination a Short links to). It is **16:9 ONLY** (no 9:16). The script and a complete, approved **`beat_sheet.json` are already written** — do **not** rewrite them. Your job is to build the Manim scene, render, audit, and publish if it's good. **Quality bar is high — this is a flagship; do not ship sloppy.**

Folder: `~/Documents/Cowork/Manim/energy-levels-n-squared-worked/`
Read first: `script.md` (the arc) and `beat_sheet.json` (the 32-beat contract). House rules: `bears-doodles/reference/style.md` and `bears-doodles/reference/reframing-16x9-to-9x16.md` (not needed here — 16:9 only).

## Hard rules
- **Scene class is `class BearsDoodlesVideo(Scene)`**, **silent** (no `add_sound` — `assemble.py` muxes audio). Reads `mp3/timings.json` for per-beat durations.
- **Text = Shadows Into Light; MATH = MathTex (LaTeX/MacTeX).** Every beat with a non-null `math_tex` field renders that exact LaTeX as `MathTex`. Prose/labels render as `Text(..., font="Shadows Into Light")`. Never fake math with Text.
- House colors: ink `#1a1a1a`, accent Warm Slate `#5A5653` (wave, rungs, boxed formula), red `#C0392B` (the n², the final answer, gap arrows). White background. Keep everything inside the ~8% safe area (±6.3 / ±3.4).
- **16:9 only.** Do not do a 9:16 pass. Do not import the portrait engine.
- Intro = infographic hero (brand + n²-ladder motif + title). Outro = a **separate cleared card** ("Thanks for watching" + title + youtube.com/@NikBearBrown).

## The scene, beat by beat
Follow `beat_sheet.json` exactly. Scene structure (by `scene_index`):
- **0 INTRO** title card. **1–2 H01/H02** narration-card hooks (even ladder → fanning ladder).
- **3 A01–A04** intuition recap: box + standing wave morphing n=1→4, energy axis with rungs 1/4/9/16, red gap arrows 3/5/7. (You may reuse the visual approach from the sibling `energy-levels-arent-evenly-spaced` scene.)
- **4 M01–M09** the derivation: keep one box+wave on the left; on the right `Write`/`TransformMatchingTex` the chain `λ_n = 2L/n` → `p = h/λ` → `E = p²/2m` → box `Eₙ = n²h²/8mL²`; `Indicate` the `n²` in red and trace it to `λ_n`.
- **5 W01–W08** worked example: carry the boxed formula to the top; substitute numbers one line at a time — `L = 1 nm`, `E₁ ≈ 0.38 eV`, `E₂ = 4E₁ ≈ 1.5 eV`, `ΔE ≈ 1.1 eV`, photon leaves, `λ = hc/ΔE ≈ 1100 nm`, place on a near-IR spectrum strip. Mark each energy on the ladder as it's computed.
- **6 P01–P04** prediction: a quantum dot (small box), `E ∝ 1/L²`, two dots (small=blue glow / large=red), formula callback.
- **7 R01–R03** recap (`E ~ p²`, half-waves, boxed formula one last time).
- **8 OUTRO** cleared thanks card.

Timing: pull each beat's run_time from `mp3/timings.json` (a `dur(beat_id)` helper, like the sibling scene). The scene is silent.

## Build, audit, assemble (16:9)
```
ai
cd ~/Documents/Cowork/Manim/energy-levels-n-squared-worked
python ../../bears-doodles/scripts/generate_audio.py .
manim -qh energy_levels_n_squared_worked.py BearsDoodlesVideo
python ../../bears-doodles/scripts/manim_layout_audit.py energy_levels_n_squared_worked.py
python ../../bears-doodles/scripts/assemble.py . --mode manim
open mp4/energy-levels-n-squared-worked.mp4
```
- Confirm MacTeX is installed (MathTex needs it): `brew install --cask mactex-no-gui` if a LaTeX error appears.
- Fix every `layout_audit.md` ERROR (MathTex blocks are wider than Text — watch for the formula colliding with the ladder; give the right column its own column).
- Verify the **numbers read correctly** and the formula is legible at mobile size.

## Publish IF good (only after you've watched it)
This is a deep 16:9-only video, so it is exempt from the both-formats publish gate — publish it on its own:
```
python ../../bears-doodles/scripts/youtube_publish.py . --which landscape --allow-partial --dry-run   # preview the slot
python ../../bears-doodles/scripts/youtube_publish.py . --which landscape --allow-partial             # schedule it
```
It uploads private with a scheduled `publishAt` (drip). **Do not publish if** the math is wrong, MathTex failed to render, the audit shows errors, or it just looks sloppy — fix first.

## After publish (manual, can't be automated)
- This deep video is a **funnel destination**, not a source — it does not need a Related Video link itself, but it should have an **end screen + card → the subject playlist**, and the matching 1-min **Short's** Related Video should point **here** (set in Studio). See `bears-doodles/reference/shorts-vs-longform-strategy.md`.

## Acceptance
- [ ] `BearsDoodlesVideo`, silent, 16:9, compiles and renders.
- [ ] Every `math_tex` beat is real MathTex; text is Shadows Into Light; colors per house style.
- [ ] Worked numbers correct (E₁≈0.38 eV, E₂≈1.5 eV, ΔE≈1.1 eV, λ≈1100 nm).
- [ ] `layout_audit.md` = 0 errors; formula never collides with the ladder.
- [ ] Master at `mp4/energy-levels-n-squared-worked.mp4`, audio synced, 1s tail.
- [ ] Published only after a human-quality watch.
