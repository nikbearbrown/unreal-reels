# Enhance — Why an Atom and a Laser Quantize for the Same Reason (Worked Example)

> **OPTIONAL. Suggestions only.** This pass generates nothing, edits no scene, and forces nothing. The flat-doodle Manim base and the style-locked doodle library are unchanged. Enhance assets are the *quarantined, photoreal-allowed exception* — they live only in this `enhance/` folder. Pick the few that help; ignore the rest.

**Decision rule:** does the narration name a real thing the viewer must *recognize* (a scientist, a physical/biological object)? If yes, a real-looking asset may beat geometry. If it's a concept, process, or relationship — keep it Manim.

**Soul-ID note:** for a recurring invented character (an on-brand, copyright-safe "scientist" who stays the same person across shots), train a Soul ref once (`higgsfield soul-id --help`) and attach it to the commands below (the ref flag is shown by `higgsfield generate create --help`). Check cost first with `higgsfield generate cost`; video models cost more than stills.

## 3 suggestion(s)  ·  0 scientist · 0 object · 3 hook

### INTRO — hook beat (optional scene-setter)
> "Bear's Notes  Why an Atom and a Laser Quantize for the Same Reason"

- **Why:** a hook beat — a quick hand-drawn moment can set the scene better than a text card. Lowest priority; skip freely.
- **Suggested:** a short doodle clip overlaid at this beat by `composite_doodles.py`.
- **Clip:** `enhance/INTRO-hook.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "a short hand-drawn scene-setter: Bear's Notes  Why an Atom and a Laser Quantize for the Same Reason, minimal, bold ink lines on white, 3 seconds"
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### H01 — hook beat (optional scene-setter)
> "A laser shines in exact colours; an atom holds exact energies."

- **Why:** a hook beat — a quick hand-drawn moment can set the scene better than a text card. Lowest priority; skip freely.
- **Suggested:** a short doodle clip overlaid at this beat by `composite_doodles.py`.
- **Clip:** `enhance/H01-hook.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "a short hand-drawn scene-setter: A laser shines in exact colours; an atom holds exact energies., minimal, bold ink lines on white, 3 seconds"
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

### H02 — hook beat (optional scene-setter)
> "Both come from one rule — a wave has to fit between two walls."

- **Why:** a hook beat — a quick hand-drawn moment can set the scene better than a text card. Lowest priority; skip freely.
- **Suggested:** a short doodle clip overlaid at this beat by `composite_doodles.py`.
- **Clip:** `enhance/H02-hook.mp4`
  ```
  higgsfield generate create seedance_2_0 --prompt "a short hand-drawn scene-setter: Both come from one rule — a wave has to fit between two walls., minimal, bold ink lines on white, 3 seconds"
  ```

- **Bridge (optional):** to keep a photoreal insert from clashing with the flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the channel palette so it reads as intentional, not pasted-in.

---

### How an asset wires back in (only once you've made and vetted it)

- **Still (PNG):** drop in `enhance/`, load in the scene with `ImageMobject("enhance/<file>.png")` at that beat (animate move/scale/fade). Transparent or white background; must survive a move/scale/fade test.
- **Clip (MP4):** name it for its beat and let `composite_doodles.py` overlay it at that beat's window — same path the optional doodle overlays already use. Manim never ingests mp4.
- Nothing here is required to ship: the `assemble` master is already complete.

