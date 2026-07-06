# stock-styles.md — house prompt styles for generated stills (Higgsfield/FLUX)

Two named looks. SHOTLIST prompts reference them by name and append the
subject; never restate the style ad hoc — the whole point is that every
generated plate in a film (and across films) shares one photographic voice.

## WARMONO — editorial war-portrait monochrome

> high-contrast digital black-and-white, aggressive micro-contrast, every
> pore, dirt streak, and sweat bead carved out, frontal gaze, shallow depth
> of field, studio-sculpted key light, cinematic poster grade, no grain

Documentary subject matter shot like a fashion campaign (Salgado/McCullin ×
Herb Ritts). Native register: music videos, unreal-reels cinematic preset,
poster/key art. Self-discloses as art.

## NATGEO — hyperrealist documentary color

> hyperrealist photography, in the style of National Geographic, natural
> skin, visible pores

Honest-light color documentary realism. Native register: explainer plates,
location/subject stills, texture-rich naturalism.

## PORTRAIT — hyper-realist historical portrait (people prompts)

> Hyper-realistic portrait of a [AGE]-year-old [NAME], [YEAR], [NATIONALITY]
> [FIELD], in the style of Edward Burtynsky, hyper-realist photograph, clean
> sharp focus, clear facial features --ar 16:9

Fill AGE from birth year vs the scene's YEAR (compute it — do not guess).
Use --ar 9:16 for portrait-frame variants. EVERY person slot in a SHOTLIST
carries one of these alongside its archive queries: the archive photo is
route one, the generated stand-in is route two — and a generated portrait of
a real person ALWAYS means `source: ai` + disclosure sidecar (provenance
rules; the credits block says so).

## Rules

- One style per film. Mixing WARMONO and NATGEO plates in one edit breaks
  the single-photographer illusion.
- In vox-explainer, generated plates additionally pass the newsprint launder
  (`vf_treatment`) AND are `source: ai` — sidecar disclosure required
  (SKILL.md provenance rules). The style prompt does not exempt the slot.
- These are STILL styles. i2v prompts inherit the look from the seed frame —
  do not restate the style in motion prompts.

## THE PROMPT LAW (generic subjects — lab equipment, apparatus, non-famous people)

A vague noun phrase returns thirty different images; a specified one
returns variations of the same image. For any generic subject, the prompt
NAMES ALL EIGHT: the object (count + what it is), its size, the geometry
(camera angle, tilt, fill-of-frame), the content distribution (where the
detail concentrates and where it is empty — this is usually the physics),
the material, the light source, the setting/ground, and the EXCLUSIONS
(no hands, no text, no labels, no reflections, no people).

Rationale: generation is seconds; hunting archives is minutes-to-hours.
A specified prompt makes generation the reliable FIRST pass — candidates
converge, the human picks, archives are for when generation is wrong in
kind, not in detail. (Fixture: vox-wave-function B09 — 'dark laboratory
detector plate' returned 30 different objects; the eight-part prompt
returned the same plate six ways, pick-and-ship.)

Selection criteria when judging candidates: content correctness first
(the distribution IS the argument), photographic realism second (straight
lines stay straight — wavering bands/edges are the AI tell), compositing
fitness third (calm regions for assembly-plane chips, survives the
launder).
