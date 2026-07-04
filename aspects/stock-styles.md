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

## Rules

- One style per film. Mixing WARMONO and NATGEO plates in one edit breaks
  the single-photographer illusion.
- In vox-explainer, generated plates additionally pass the newsprint launder
  (`vf_treatment`) AND are `source: ai` — sidecar disclosure required
  (SKILL.md provenance rules). The style prompt does not exempt the slot.
- These are STILL styles. i2v prompts inherit the look from the seed frame —
  do not restate the style in motion prompts.
