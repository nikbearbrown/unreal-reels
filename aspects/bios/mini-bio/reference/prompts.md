# mini-bio — Higgsfield clip prompts

Three kinds of clip beat. Keep every clip ~5s, 16:9, ending with `no text, no captions`.
This works for any figure — a scientist, a writer, an artist, a leader, or a fictional
character. (For fictional characters the Soul ID *is* the character design; for real people
it's an invented, copyright-safe likeness in period-appropriate dress.)

## soul-id (the figure)
Attach the figure's trained Higgsfield **Soul ID** ref — one ref serves every soul-id beat
for that figure, so the face is identical across the opening, any interior beats, and the
closing shot. Describe wardrobe, setting, camera, mood — the ref locks the likeness; don't
over-describe the face. Make it era/world-appropriate: tweed and a dim study for an
Edwardian physicist; an empire-waist gown by a window for a Regency novelist; gingham and a
Kansas farmhouse for Dorothy Gale.

Pattern:
```
Cinematic <era/world> portrait of <figure>, <wardrobe>, <setting>, <lighting>,
shallow depth of field, <slow camera move>, <period/world film look>, <mood>, 5 seconds, no text
```
Opening beat = contemplative push-in that introduces them. Interior beats (longer bios) =
a fresh setting/wardrobe that fits the section. Closing beat = calm, a faint smile, soft
light dimming, a gentle fade toward darkness at the very end (reads well into a fade-out).

## world (the milieu the story lives in)
No Soul ref. The place, era, or phenomenon the story is *about* — for a scientist the
real-world effect (a furnace glowing white-hot, a diffraction pattern, a star); for a
novelist a candlelit Regency ballroom; for Dorothy a Kansas prairie under a darkening,
spinning sky. High-contrast, cinematic, slow move.
```
<the world / scene / phenomenon, vividly described>, cinematic, high-contrast, slow dolly-in,
5 seconds, no text
```
(Omit "no people" when the world is social — a ballroom, a crowd, a court.)

## legacy (what endures)
No Soul ref. What the figure left behind — the technology a discovery enabled, shelves of
well-worn novels still in print, monuments, a cultural icon, the adaptations a character
still inspires. Clean and evocative, often warm or cool light, shallow focus, slow drift.
```
<the legacy, vividly described>, fine detail, <warm or cool> light, slow rack-focus drift,
cinematic, 5 seconds, no text
```

## Tips
- Run `higgsfield generate cost` before a batch; video models cost more than stills.
- Generate at ~5s; the bio scene trims each clip to its beat length and freezes the last
  frame only if a clip is shorter than its narration (so favour clips ≥ the spoken line).
- Name the files in clip-beat order (`B1_…`, `B2_…`, …) so `ingest_clips.py` maps them.
- One Soul ID per figure. Longer bios use more soul-id beats — train the figure's ref once
  and reuse it for the opening, the interior anchors, and the close.
- Dialogue bios (two figures): one Soul ID per speaker; give each their own soul-id beats.
