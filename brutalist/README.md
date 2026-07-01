# brutalist/ — lecture-video design system

The visual constitution for unreal-reels narrated lecture videos (the `deck-lecture`
skill). Read **[DESIGN.md](DESIGN.md)** before changing anything that touches how the
video looks — palette, the three typefaces (Lato / Inter / JetBrains Mono), motion
easing, and the three-tier slide model (live · doodle · bullets).

It is a slimmed, adapted mirror of the broader `ai1-cli/brutalist` system
(DESIGN.md, VIZ.md, SaulBass.md, SLIDES.md), keeping only what serves a moving,
narrated deck and swapping in our fonts.

Where the tokens live in code:
- `skills/deck-lecture/templates/remotion/src/tokens.ts` — colors, easing, durations, number regex
- `skills/deck-lecture/templates/remotion/src/fonts.ts` — local Inter (overlay) + mono fallback
- `skills/deck-lecture/templates/remotion/public/fonts/` — the bundled Inter files

Not yet mirrored (available in the source if wanted later): the Saul Bass title-card /
thumbnail style, and the SLIDES.md pedagogical authoring method for new decks.
