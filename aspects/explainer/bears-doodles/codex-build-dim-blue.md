# Codex task — produce the full publish pair for `dim-blue-beats-blinding-red` (v1.01)

Concept: the photoelectric effect — "Why a Dim Blue Lamp Beats a Blinding Red One." Source chapter: `quantum-mechanics-vol1/chapters/01-why-classical-physics-failed.md`. Take this concept all the way to **two publish-ready videos** + a post kit:

1. the existing 1-min → its **9:16 Short** (portrait-convert + render)
2. a new **deep 2–5 min 16:9** worked-example
3. final passes + YouTube post kit

**Reference implementation for BOTH steps: `energy-levels` — copy its structure.** Read `~/Documents/Cowork/Manim/energy-levels-arent-evenly-spaced/energy_levels_arent_evenly_spaced.py` (portrait pattern) and `~/Documents/Cowork/Manim/energy-levels-n-squared-worked/` (deep pattern). House rules: `bears-doodles/reference/style.md`, `reframing-16x9-to-9x16.md`, `shorts-vs-longform-strategy.md`. Quality bar is high — this is a flagship; do not ship sloppy.

## ⚠️ Gotchas (these will bite — they already did once)
- **Portrait render = `manim -r 1080,1920 --fps 60 --disable_caching --flush_cache …`**, NOT `-qh` (`-qh` forces 1920×1080 and silently renders landscape). Confirm the log prints `mode=PORTRAIT … frame=4.50x8.00`.
- **MathTex needs MacTeX** (`brew install --cask mactex-no-gui` if a LaTeX error appears). Text = Shadows Into Light; math = MathTex.
- Scene class is always `class BearsDoodlesVideo(Scene)`, **silent** (assemble muxes audio). Use `LaggedStart(*[Create(m) for m in grp])`, never `LaggedStartMap` (broken in this Manim build).
- Copy `bears-doodles/scripts/bn_layout.py` next to any scene that imports it.

---

## PART A — portrait-convert the 1-min → 9:16 Short
Folder: `~/Documents/Cowork/Manim/dim-blue-beats-blinding-red/`, scene `dim_blue_beats_blinding_red.py` (beats INTRO/H01/H02/A01–A08/OUTRO, photoelectric).

1. Copy `bn_layout.py` into the folder. Make the scene orientation-aware exactly like energy-levels: `import bn_layout`, pick `LANDSCAPE`/`_portrait_L()` via `is_portrait()`, drive geometry from the active constant set, use `bn_layout.fit`/`fit_text` so content **fills** the 9:16 band (no floating; stack any side-by-side layout top/bottom; keep out of the bottom ~24% / right rail). Landscape layout must stay unchanged.
2. Use `bn_layout.outro(self, TITLE, CHANNEL, dur("OUTRO"), teaser_tex=_DEEP_TEX, font=FONT, ink=INK, accent=ACCENT)` for the outro, reading `_DEEP_TEX` from `metadata.deep_teaser_tex` (set in Part C).
3. Render + audit + assemble the Short:
   ```
   manim -r 1080,1920 --fps 60 --disable_caching --flush_cache dim_blue_beats_blinding_red.py BearsDoodlesVideo
   python ../../bears-doodles/scripts/manim_layout_audit.py dim_blue_beats_blinding_red.py
   python ../../bears-doodles/scripts/assemble.py . --mode manim --portrait
   ```
   Fix every audit ERROR before moving on.

---

## PART B — author + build the deep 16:9 (photoelectric worked example)
New folder `~/Documents/Cowork/Manim/photoelectric-effect-worked/`, slug `photoelectric-effect-worked`, `metadata.tier="deep"`, `metadata.depth_of="dim-blue-beats-blinding-red"`, `aspect_ratio "16:9"`, voice/colors/font same as house. **16:9 only.**

Arc (reuse intuition → idea→math → worked example → predicts → recap), one sentence = one beat:
- **Reuse:** light comes in packets; each packet's energy is set by colour; freeing an electron needs one packet with enough energy.
- **Idea→math (MathTex):** packet energy `E = hf = \frac{hc}{\lambda}`; freeing an electron costs the work function `\phi`; the leftover is kinetic energy: **`K_{\max} = hf - \phi`**; below the threshold `f_0 = \phi/h` (i.e. `\lambda_0 = hc/\phi`) nothing comes off.
- **Worked example (use THESE verified numbers exactly):** sodium, `\phi = 2.28\ \text{eV}`. Blue 450 nm → `E = hc/\lambda = 2.76\ \text{eV}` → `K_{\max} = 0.48\ \text{eV}` → ejects. Red 700 nm → `E = 1.77\ \text{eV} < \phi` → **no ejection, at any brightness**. Threshold `\lambda_0 = hc/\phi \approx 544\ \text{nm}`. (eV·nm: `hc = 1240`.)
- **Predicts:** brightness adds more photons, not more energy per photon, so a blinding red lamp never frees an electron while a dim blue one does instantly — the result that forced light to be quantized (Einstein, 1905).
- **Recap:** `K_{\max} = hf - \phi` — colour (frequency) sets the energy per hit, brightness only sets how many hits.

Build it like the energy-levels deep: `beat_sheet.json` with a `math_tex` field per math beat, then the scene (left panel = metal plate + photons of two colours hitting it / an electron ejecting; right column = the formula chain assembling to a boxed `K_{\max}=hf-\phi`; worked numbers slotting in beside a tiny "ejects / doesn't" indicator). Then:
```
cd ~/Documents/Cowork/Manim/photoelectric-effect-worked
python ../../bears-doodles/scripts/generate_audio.py .
manim -qh photoelectric_effect_worked.py BearsDoodlesVideo
python ../../bears-doodles/scripts/manim_layout_audit.py photoelectric_effect_worked.py
python ../../bears-doodles/scripts/assemble.py . --mode manim
```

---

## PART C — wire the funnel (tier-aware outro)
Write into the **1-min** `dim-blue-beats-blinding-red/beat_sheet.json` metadata:
- `deep_slug`: `"photoelectric-effect-worked"`
- `deep_teaser_tex`: `"K_{\\max} = hf - \\phi"`

Then re-render the 1-min's 9:16 Short (Part A render commands) so its outro now points to "the full worked example" and flashes `K_max = hf − φ`.

---

## PART D — final passes + post kit
1. **Visual pass:** `manim_layout_audit.py` on BOTH renders → 0 errors.
2. **Scientific pass (do not skip):** verify every formula and number against the verified set above (E=2.76/1.77 eV, φ=2.28, K_max=0.48, λ₀≈544 nm, the "no ejection at any brightness" claim). This is the gate that catches a wrong sign or denominator.
3. **Post kit:** `python ~/Documents/Cowork/bears-doodles/scripts/bn_pipeline.py run dim-blue-beats-blinding-red --render` — renders both, audits, and writes `dim-blue-beats-blinding-red/PUBLISH-KIT.md` (titles, descriptions, chapters, hashtags, Related-Video → deep, FACTCHECK sign-off).

## Acceptance
- [ ] 1-min 9:16 Short renders (log `mode=PORTRAIT frame=4.50x8.00`), content fills the frame, audit clean.
- [ ] Deep 16:9 renders, MathTex correct, audit clean, numbers match the verified set.
- [ ] 1-min outro teases the deep (`K_max=hf−φ`) after Part C.
- [ ] `PUBLISH-KIT.md` written; scientific factcheck signed off.
- [ ] Do NOT publish — Bear reviews both videos first, then we fix or move to the next concept.
