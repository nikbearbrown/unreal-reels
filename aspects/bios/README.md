# Bios — narrated mini-biographies

The biography aspect. Turns **any figure — real or fictional** into a short narrated life-story:
a single narrator carries the arc while the visuals alternate between the figure (one locked
identity) and the world/legacy around them.

## What's different from the base engine

- **One recurring figure**, identity-locked across the whole piece (their reference, recurring).
- **Narrator over B-roll** is the default; dialogue mode (a second voice / the figure's own) is
  optional, set per beat via `voice_id`.
- **Duration is an output, not a target** — the figure's story decides length (~30s to ~5 min).
- Beat content follows a who → why-they-mattered → legacy arc; opens and closes on the figure.

## Authoring → `beat_sheet.json`

Figure → research → narration beats (who / impact / legacy), each ≤~10s. Recurring "figure" beats
reuse the one reference; "world" and "legacy" beats are no-character scenes. Then the shared stages
run: audio → references → storyboard → video → overlay.

## Source skill to fold in

From the existing work: **`mini-bio`** — the beat schema, the audio-first timing contract, the
clip-prompt patterns (soul-id / world / legacy), and the packaging (`youtube.md`, tags). Its
`generate_audio.py` is already the shared engine's audio stage.

> _Mapping to confirm/adjust:_ mini-bio is the closest 1:1 to the base engine — mostly it just
> sets the authoring style (narrator arc) and the duration taxonomy.
