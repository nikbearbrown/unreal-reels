# SHOTLIST — vox-electoral-college (test fixture)

Excerpt recreation of Vox's "The Electoral College, explained." Clock =
transcript timestamps (no TTS). Ground truth frames: `../../vox/`.
Swap rule: drop `media/<BEAT>.png` or `media/<BEAT>.mp4` (mp4 wins) + a
`<BEAT>.source.txt` sidecar for archive slots, then rebuild. Timeline: 22 beats,
~2:31 of coverage in six blocks (0:00, 1:12, 2:27, 4:55, 7:21).

## Shot-type histogram

GRAPHIC 10 · COMPOSITE 3 · DOCUMENT 3 · STILL 2 · FOOTAGE 2 · CARD 2
Rhythm lint: longest same-type run = 3 (B11–B13, all GRAPHIC) — flagged, acceptable
because the bar→map→bar morph is one continuous argument.

---

### B01 · CARD · 2.0s — title
Copy: "The Electoral College, explained" / sub "excerpt recreation — test fixture".
Design system only. No media slot.

### B02 · FOOTAGE · archive · 4.0s — news montage
Cue: "What do the national polls look like..."
FIND: https://archive.org/search?query=%22election+night%22+broadcast+2016+news
     https://commons.wikimedia.org/w/index.php?search=election+night+television+broadcast&title=Special:MediaSearch&type=video
AI fallback (i2v from B02.png): "two overlapping television-news still frames pinned
on a newsprint page, anchors at desks with election graphics, desaturated print look"
→ motion: "second panel drops onto the paper stack, settles flat, no camera move"
Sidecar required.

### B03 · FOOTAGE · archive · 2.0s — third news panel
Same sourcing as B02; one more panel joins the collage.

### B04 · COMPOSITE · archive · 4.0s — the strike-X
B02/B03 plate held; terracotta hand-drawn X strikes through on the word "don't."
Annotation plane only — no new media.

### B05 · DOCUMENT · 7.0s — "swing states" pull-quote
Serif quote on newsprint; golden highlighter sweeps "swing states" on the word.
No media slot (typography + design system).

### B06 · STILL · archive · 4.0s — Capitol photo, slow push-in
FIND: https://www.loc.gov/free-to-use/?q=united+states+capitol
     https://www.si.edu/openaccess?edan_q=capitol%20building%20photograph
AI fallback (t2i): "archival black-and-white photograph of the United States Capitol
dome, early 20th century, desaturated print reproduction on aged newsprint"
Sidecar required.

### B07 · GRAPHIC · 7.0s — House 435 / Senate 100 isotype
Manim `IsotypeDotGrid`, two blocks, charcoal squares, count-up timed to the
audio window. Verify: 435 / 100.

### B08 · GRAPHIC · 7.0s — Texas vs Vermont cards
Manim `StateCardPair`: slate-teal blocks, white serif names, silhouettes from PD
shapefiles (Census TIGER / Natural Earth). Ref: vox_frame_009520.

### B09 · GRAPHIC · 5.0s — 36 reps vs 1
`IsotypeDotGrid` under the cards, navy squares. Verify apportionment-era counts.

### B10 · GRAPHIC · 11.0s — +2 senators → 38 vs 3
Count-up continues; the two added squares land terracotta exactly on "plus two";
hairline underline under the phrase. Verify: TX 38, VT 3.

### B11 · GRAPHIC · 4.0s — 2016 stacked bars, 50 states
Manim `StackedBarByState`; data from FEC/MIT Election Lab 2016 returns.
Ref: vox_frame_004592. Crimson/navy/gray only.

### B12 · GRAPHIC · 5.0s — red/blue map
`ChoroplethUS` 2016. Ref: vox_frame_004816.

### B13 · GRAPHIC · 7.0s — morph back to bars + yellow ellipse
Map morphs back to bars (transform, don't cut); hand-drawn yellow ellipse sweeps
the mixed midsection on "no state." Ref: vox_frame_004928.

### B14 · COMPOSITE · 8.0s — winner-take-all region flood
Isotype square grid over newsprint; outlined red/blue regions flood solid on "ALL."
Ref: vox_frame_004368.

### B15 · DOCUMENT · archive · 4.0s — Constitution zoom + label chip
Zoom to Article I, Sec. 2; crimson chip "Three-fifths clause" (ref: vox_frame_009856).
FIND: https://catalog.archives.gov/search?q=constitution%20of%20the%20united%20states%20page%201
Sidecar required.

### B16 · COMPOSITE · 6.0s — three of five squares
`IsotypeFraction`: 5 squares, 3 fill charcoal. Nothing else on screen.

### B17 · GRAPHIC · 12.0s — VA vs PA, 1800 census figures
`StateCardPair` with serif figures; enslaved counts in terracotta.
Refs: vox_frame_009520, _009072. Verify 1800 census: 539k/601k free, 347k/1.7k enslaved.

### B18 · GRAPHIC · 7.0s — 21 vs 15 electoral votes
Flanking black-square grids; Virginia card ringed in the crimson three-fifths frame.
Ref: vox_frame_009072. Verify 1800: VA 21, PA 15.

### B19 · GRAPHIC · 5.0s — 1948 map + ring on New York
`ChoroplethUS` 1948; legend names underlined in candidate color (Truman navy,
Dewey crimson, Thurmond gold); terracotta hand-ring on NY on the words "New York."
Ref: vox_frame_013440.

### B20 · DOCUMENT · archive · 12.0s — Gossett quote
Full-frame serif quote, attribution + "Source: Alexander Keyssar."
Highlighter on "a hundred times as much." Ref: vox_frame_013888.

### B21 · STILL · archive · 6.0s — polling-place photo, slow pull-out
FIND: https://www.loc.gov/free-to-use/?q=voting+polling+place
     https://catalog.archives.gov/search?q=voters%20polling%20place%20photograph
AI fallback (t2i): "mid-20th-century archival photograph of American voters lined
up at a polling place, desaturated newsprint reproduction"
Sidecar required.

### B22 · CARD · 4.0s — endcard
"recreated as a vox-explainer test — not for publication."

---

## What YOU fill (everything else renders without you)

| Slot | Need | Path |
|---|---|---|
| B02, B03 | archive news clips (or AI fallback) | media/B02.mp4, media/B03.mp4 + sidecars |
| B06 | Capitol archival photo | media/B06.png + B06.source.txt |
| B15 | Constitution page scan | media/B15.png + B15.source.txt |
| B20 | (optional) higher-fidelity quote plate | typography renders without media |
| B21 | polling-place archival photo | media/B21.png + B21.source.txt |

All GRAPHIC/CARD/quote beats are Manim/design-system renders — no sourcing, no credits, no spend.
