# Max Planck — bio prototype (alternating cut)

A ~30s test of the **bio pipeline**: Bear (voice clone, `TyW6NH39JcFb5M3xdIIk`) narrates
throughout; visuals **alternate** between full-frame Higgsfield footage and clean dark
Manim cards. Not the doodle look — dark bg, Montserrat, crisp MathTex — so photoreal and
cards read as one documentary.

## The cut
| Beat | Visual | Narration |
|------|--------|-----------|
| B01 | **clip** · Soul-ID Planck portrait | "Max Planck didn't set out to start a revolution." |
| B02 | **card** · TITLE "MAX PLANCK / 1858–1947" | "A careful German physicist, he just wanted to explain the glow of hot objects." |
| B03 | **clip** · furnace glowing white-hot (phenomenon) | "Classical physics said that glow should blast out endless ultraviolet." |
| B04 | **card** · EQUATION E = hν | "Planck's fix: energy comes in discrete chunks — E equals h times frequency." |
| B05 | **clip** · silicon wafer macro (application) | "That one idea — energy in quanta — underlies every transistor and laser today." |
| B06 | **card** · DATE "1918 / Nobel Prize" | "It won him the Nobel Prize in 1918, and opened the quantum age." |
| B07 | **clip** · Soul-ID Planck closing portrait | "Max Planck — the reluctant father of the quantum." |

The clip beats are **not always the scientist** — B03 is the phenomenon, B05 is the
modern application his physics enabled. That's the point.

## Shot list → Higgsfield (generate these, drop in `clips/<BEAT>.mp4`)
- **B01** `clips/B01.mp4` — Max Planck (Soul-ID), period portrait in a dim study, round glasses, slow push-in, ~5s.
- **B03** `clips/B03.mp4` — open furnace door, white-hot glowing metal, heat shimmer, cinematic, ~5s.
- **B05** `clips/B05.mp4` — extreme macro of a silicon wafer, fine circuitry, cool blue light, slow drift, ~5s.
- **B07** `clips/B07.mp4` — Max Planck (Soul-ID), calm closing portrait, faint smile, fade to dark, ~5s.

(Full prompts live in `beat_sheet.json` per beat under `higgsfield_prompt`.)

## Build
1. Audio (Bear narrates all beats):
   ```
   python ../../bears-doodles/scripts/generate_audio.py .
   ```
2. Render the master (cards real; clip beats show labeled placeholders):
   ```
   manim -qh bio_max_planck.py BearsDoodlesVideo
   ```
3. Assemble to watch the **cut feel now** (placeholders in place):
   ```
   python ../../bears-doodles/scripts/assemble.py . --mode manim
   ```
4. Later — generate the 4 clips, drop them in `clips/`, then composite + assemble:
   ```
   python ../../bears-doodles/scripts/composite_clips.py .
   python ../../bears-doodles/scripts/assemble.py . --mode manim --manim-mp4 mp4/_composited.mp4
   ```

Footage is trimmed to each beat's length and scaled to cover the frame (no letterbox).
Missing clips just stay as placeholders, so you can composite as you go.
