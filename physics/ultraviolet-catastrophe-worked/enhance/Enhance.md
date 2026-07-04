# Enhance — The Ultraviolet Catastrophe: Why Quantizing Energy Fixes It (Worked Example)

> **OPTIONAL. Suggestions only.** This pass generates nothing, edits no scene, and forces nothing. The flat-doodle Manim base and the style-locked doodle library are unchanged. Enhance assets are the *quarantined, photoreal-allowed exception* — they live only in this `enhance/` folder. Pick the few that help; ignore the rest.

**Decision rule:** does the narration name a real thing the viewer must *recognize* (a scientist, a physical/biological object)? If yes, a real-looking asset may beat geometry. If it's a concept, process, or relationship — keep it Manim.

**Soul-ID note:** for a recurring invented character (an on-brand, copyright-safe "scientist" who stays the same person across shots), train a Soul ref once (`higgsfield soul-id --help`) and attach it to the commands below (the ref flag is shown by `higgsfield generate create --help`). Check cost first with `higgsfield generate cost`; video models cost more than stills.

## 5 suggestion(s)  ·  2 scientist · 1 object · 2 hook

### Scientist shout-out: Planck  ·  beats H02, M04, M06
> "It doesn't — and the fix was Planck's idea that energy comes in chunks."

- **Why:** the narration names **Planck** — a 3–5s Soul-ID character moment (or a still) lands the human behind the idea. Appears at: H02, M04, M06 — one Soul ref covers every placement.
- **Suggested:** Soul-ID still **or** ~4–5s clip of an invented period-scientist character. Photoreal is fine here (quarantined).
- **Still:** `enhance/planck.png`
  ```
  higgsfield generate create text2image_soul_v2 --prompt "portrait of Planck, an early-20th-century scientist, in a tweed suit and round wire glasses, standing at a chalkboard covered in equations, natural light, period documentary photograph, consistent character, shallow depth of field"  # + your Soul ref flag
  ```
- **Clip (~5s):** `enhance/planck.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "Planck, an early-20th-century scientist in a tweed suit and round glasses, writing equations on a university chalkboard, subtle natural movement, period documentary look, 5 seconds"  # + your Soul ref flag
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### Scientist shout-out: Wien  ·  beats W05
> "The peak instead sits in the infrared — Wien's law, lambda-max equals b over T."

- **Why:** the narration names **Wien** — a 3–5s Soul-ID character moment (or a still) lands the human behind the idea. Appears at: W05 — one Soul ref covers every placement.
- **Suggested:** Soul-ID still **or** ~4–5s clip of an invented period-scientist character. Photoreal is fine here (quarantined).
- **Still:** `enhance/wien.png`
  ```
  higgsfield generate create text2image_soul_v2 --prompt "portrait of Wien, an early-20th-century scientist, in a tweed suit and round wire glasses, standing at a chalkboard covered in equations, natural light, period documentary photograph, consistent character, shallow depth of field"  # + your Soul ref flag
  ```
- **Clip (~5s):** `enhance/wien.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "Wien, an early-20th-century scientist in a tweed suit and round glasses, writing equations on a university chalkboard, subtle natural movement, period documentary look, 5 seconds"  # + your Soul ref flag
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### Nameable object: filament  ·  beats P01
> "Heat it hotter and the peak slides toward visible — a stove glows red, a filament white."

- **Why:** the narration names **filament** — something Manim can't draw convincingly and the viewer needs to recognize.
- **Suggested:** a clean still. For *biology*, prefer a diagrammatic style (Illustrae / Midjourney diagram mode) to stay closer to the doodle aesthetic; for *phenomena*, photoreal is fine (quarantined).
- **Still:** `enhance/filament.png`
  ```
  higgsfield generate create nano_banana_2 --prompt "a single filament, clean diagrammatic illustration, centered on a plain white background, clear and recognizable, soft shading"
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### INTRO — hook beat (optional scene-setter)
> "Bear's Notes  The Ultraviolet Catastrophe: Why Quantizing Energy Fixes It"

- **Why:** a hook beat — a quick hand-drawn moment can set the scene better than a text card. Lowest priority; skip freely.
- **Suggested:** a short doodle clip overlaid at this beat by `composite_doodles.py`.
- **Clip:** `enhance/INTRO-hook.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "a short hand-drawn scene-setter: Bear's Notes  The Ultraviolet Catastrophe: Why Quantizing Energy Fixes It, minimal, bold ink lines on white, 3 seconds"
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### H01 — hook beat (optional scene-setter)
> "Classical physics said a warm object's glow should blast you with ultraviolet."

- **Why:** a hook beat — a quick hand-drawn moment can set the scene better than a text card. Lowest priority; skip freely.
- **Suggested:** a short doodle clip overlaid at this beat by `composite_doodles.py`.
- **Clip:** `enhance/H01-hook.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "a short hand-drawn scene-setter: Classical physics said a warm object's glow should blast you with ultraviolet., minimal, bold ink lines on white, 3 seconds"
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

---

### How an asset wires back in (only once you've made and vetted it)

- **Still (PNG):** drop in `enhance/`, load in the scene with `ImageMobject("enhance/<file>.png")` at that beat (animate move/scale/fade). Transparent or white background; must survive a move/scale/fade test.
- **Clip (MP4):** name it for its beat and let `composite_doodles.py` overlay it at that beat's window — same path the optional doodle overlays already use. Manim never ingests mp4.
- Nothing here is required to ship: the `assemble` master is already complete.

