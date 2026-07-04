# bio-bose — the Bios worked example

A finished **mini-bio** of **Satyendra Nath Bose** (1894–1974), ~30s, rendered in both
16:9 and a 9:16 Short. This is the canonical **Bios aspect** example — copy it as the
template for a new bio.

## What's here (a complete reel)

- `beat_sheet.json` — the authored beat sheet in the mini-bio schema (`render: clip|manim`,
  `higgsfield_prompt`, `card`, `soul_ref`, measured `actual_duration_s`). 7 beats, opens and
  closes on a Soul-ID portrait; cards carry the title, the Bose–Einstein equation, and the 1995 date.
- `bio-bose-youtube.md` — packaging: titles, description, tags, hashtags, separate #Shorts block.
- `bio_bose.py`, `bn_layout.py`, `fonts/` — the Manim scene + layout that renders the cards.
- `mp3/` — per-beat narration + `timings.json` (the real per-beat durations = the master clock).
- `clips/` — the ingested Higgsfield footage (audio stripped), one per clip beat.
- `mp4/bio-bose.mp4` (16:9) and `mp4/bio-bose-short.mp4` (9:16) — the finished cuts.

## The story arc it demonstrates (who → why → impact)

Open on Bose (Soul-ID) → title card → the idea (rederiving Planck's law) → the equation card →
the payoff (bosons / condensate footage) → the 1995 date → close on Bose, "never won a Nobel."
Every beat's on-screen time equals its narration length — length is an output, not a target.

## To make your own bio from this template

1. Copy this folder to a new slug: `reels/<your-slug>/`.
2. Rewrite `beat_sheet.json` for the new figure (keep the alternating clip/card rhythm, open+close
   on Soul-ID). See `aspects/bios/mini-bio/SKILL.md`.
3. A fresh figure needs assets generated: ElevenLabs (narration) + Higgsfield (Soul-ID + clips).
   Set keys first (`docs/setup.md`); Bose already has its assets, a new figure won't.

> Source: ported from `Manim/bio-bose/` (excluding `media/` manim scratch and `__pycache__`).
> Heavy output (`mp3/`, `clips/`, `mp4/`) is kept locally and git-ignored per repo convention.
