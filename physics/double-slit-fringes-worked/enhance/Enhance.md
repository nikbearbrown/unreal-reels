# Enhance — The Double Slit: How Far Apart Are the Stripes? (Worked Example)

> **OPTIONAL. Suggestions only.** This pass generates nothing, edits no scene, and forces nothing. The flat-doodle Manim base and the style-locked doodle library are unchanged. Enhance assets are the *quarantined, photoreal-allowed exception* — they live only in this `enhance/` folder. Pick the few that help; ignore the rest.

**Decision rule:** does the narration name a real thing the viewer must *recognize* (a scientist, a physical/biological object)? If yes, a real-looking asset may beat geometry. If it's a concept, process, or relationship — keep it Manim.

**Soul-ID note:** for a recurring invented character (an on-brand, copyright-safe "scientist" who stays the same person across shots), train a Soul ref once (`higgsfield soul-id --help`) and attach it to the commands below (the ref flag is shown by `higgsfield generate create --help`). Check cost first with `higgsfield generate cost`; video models cost more than stills.

## 5 suggestion(s)  ·  2 scientist · 0 object · 3 hook

### Scientist shout-out: De Broglie  ·  beats M02
> "A particle's wavelength is de Broglie's — lambda equals h over p."

- **Why:** the narration names **De Broglie** — a 3–5s Soul-ID character moment (or a still) lands the human behind the idea. Appears at: M02 — one Soul ref covers every placement.
- **Suggested:** Soul-ID still **or** ~4–5s clip of an invented period-scientist character. Photoreal is fine here (quarantined).
- **Still:** `enhance/de-broglie.png`
  ```
  higgsfield generate create text2image_soul_v2 --prompt "portrait of De Broglie, an early-20th-century scientist, in a tweed suit and round wire glasses, standing at a chalkboard covered in equations, natural light, period documentary photograph, consistent character, shallow depth of field"  # + your Soul ref flag
  ```
- **Clip (~5s):** `enhance/de-broglie.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "De Broglie, an early-20th-century scientist in a tweed suit and round glasses, writing equations on a university chalkboard, subtle natural movement, period documentary look, 5 seconds"  # + your Soul ref flag
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### Scientist shout-out: Tonomura  ·  beats P02
> "This is exactly what Tonomura saw in 1989 — dots, one by one, building the fringes."

- **Why:** the narration names **Tonomura** — a 3–5s Soul-ID character moment (or a still) lands the human behind the idea. Appears at: P02 — one Soul ref covers every placement.
- **Suggested:** Soul-ID still **or** ~4–5s clip of an invented period-scientist character. Photoreal is fine here (quarantined).
- **Still:** `enhance/tonomura.png`
  ```
  higgsfield generate create text2image_soul_v2 --prompt "portrait of Tonomura, an early-20th-century scientist, in a tweed suit and round wire glasses, standing at a chalkboard covered in equations, natural light, period documentary photograph, consistent character, shallow depth of field"  # + your Soul ref flag
  ```
- **Clip (~5s):** `enhance/tonomura.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "Tonomura, an early-20th-century scientist in a tweed suit and round glasses, writing equations on a university chalkboard, subtle natural movement, period documentary look, 5 seconds"  # + your Soul ref flag
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### INTRO — hook beat (optional scene-setter)
> "Bear's Notes  The Double Slit: How Far Apart Are the Stripes?"

- **Why:** a hook beat — a quick hand-drawn moment can set the scene better than a text card. Lowest priority; skip freely.
- **Suggested:** a short doodle clip overlaid at this beat by `composite_doodles.py`.
- **Clip:** `enhance/INTRO-hook.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "a short hand-drawn scene-setter: Bear's Notes  The Double Slit: How Far Apart Are the Stripes?, minimal, bold ink lines on white, 3 seconds"
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### H01 — hook beat (optional scene-setter)
> "One electron at a time still piles up into stripes — interference with itself."

- **Why:** a hook beat — a quick hand-drawn moment can set the scene better than a text card. Lowest priority; skip freely.
- **Suggested:** a short doodle clip overlaid at this beat by `composite_doodles.py`.
- **Clip:** `enhance/H01-hook.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "a short hand-drawn scene-setter: One electron at a time still piles up into stripes — interference with itself., minimal, bold ink lines on white, 3 seconds"
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### H02 — hook beat (optional scene-setter)
> "And the spacing of those stripes is something we can predict."

- **Why:** a hook beat — a quick hand-drawn moment can set the scene better than a text card. Lowest priority; skip freely.
- **Suggested:** a short doodle clip overlaid at this beat by `composite_doodles.py`.
- **Clip:** `enhance/H02-hook.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "a short hand-drawn scene-setter: And the spacing of those stripes is something we can predict., minimal, bold ink lines on white, 3 seconds"
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

---

### How an asset wires back in (only once you've made and vetted it)

- **Still (PNG):** drop in `enhance/`, load in the scene with `ImageMobject("enhance/<file>.png")` at that beat (animate move/scale/fade). Transparent or white background; must survive a move/scale/fade test.
- **Clip (MP4):** name it for its beat and let `composite_doodles.py` overlay it at that beat's window — same path the optional doodle overlays already use. Manim never ingests mp4.
- Nothing here is required to ship: the `assemble` master is already complete.

