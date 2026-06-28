# mini-bio — locked visual style

Documentary, not doodle. Photoreal footage and typographic cards share one look.

## Palette
- Background: **`#0E0E12`** (near-black).
- Primary text + divider rules: **`#F2F0EC`** (white).
- Secondary text (dates, labels under a card): **`#8A8780`** (grey).
- **No accent colour.** No blue, no brand hue. White lines on black. (This replaced an
  earlier blue accent — keep it gone.)

## Type
- **Montserrat** throughout (static TTFs in `fonts/`, registered via manimpango).
- Name / year: Montserrat **Bold**, all caps, lightly tracked (`tracked(..., 0.22)`).
- Equations: **MathTex** (LaTeX), white, large.
- Labels (under cards): Montserrat Medium, **uppercase**, grey.
- Dates line on the title card: Montserrat Light, grey.

## Card kinds
- `title` — big tracked NAME, a thin white rule beneath, grey `dates` below (for a fictional
  figure, `dates` can be the origin work + year, e.g. `THE WIZARD OF OZ · 1900`).
- `quote` — small grey uppercase `label` on top, a white `text` signature line centered
  (wraps to fit). The general "key line" card for any figure.
- `equation` — small grey uppercase `label` on top, big white `tex` centered. Only when the
  key idea IS an equation (scientists, mathematicians); use `quote` otherwise.
- `date` — big tracked year, thin white rule, grey uppercase `label` below.

## Clip placeholder (pre-footage)
A dashed grey frame + white "FOOTAGE" + film-sprocket squares + the shot description +
`[clip_source]`. It's only a stand-in; composite replaces it with the real clip. It also
doubles as the shot list when you watch the placeholder cut.

## Motion
Restrained. FadeIn / Write / a drawn rule. No bounce, no spin. The footage carries the
energy; the cards are calm.

## Timing contract
Every beat's total on-screen time (including its 0.35–0.4s fade-out) equals the beat's
narration length. The scene computes the hold as `t - (intro anims) - fade`, so the master
timeline matches the audio exactly — which is what keeps composited footage on its cuts.
Never add animation time beyond a beat's `dur`.

Because beat time = narration length, **total runtime is story-driven, not a target.** Size
each beat to its content (see `duration.md`); the film is however long the beats sum to —
~30s for a simple figure, up to ~5 min for a layered life. Don't compress a beat below its
consolidation floor to hit a number, and don't pad to reach one.

