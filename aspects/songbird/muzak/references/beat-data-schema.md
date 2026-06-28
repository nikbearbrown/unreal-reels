# beat_data.json — the timing contract

Produced by `scripts/analyze_audio.py`, consumed by `useBeatData.ts` and
`align_lyrics.py`. It is the single source of truth for timing. Never hand-edit it;
re-run `analyze` if the audio changes.

```jsonc
{
  "version": 1,
  "fps": 30,                      // video frame rate the frame fields are in
  "bpm": 122.0,                   // global tempo estimate
  "durationInSeconds": 184.3,
  "durationInFrames": 5529,       // set the composition durationInFrames to THIS

  "beatTimestamps":     [0.51, 1.0, 1.49, ...],   // every beat, seconds
  "downbeatTimestamps": [0.51, 2.47, 4.43, ...],  // bar starts (best-effort 4/4)

  "beatFrames":     [15, 30, 45, ...],            // same beats, rounded to frames
  "downbeatFrames": [15, 74, 133, ...],

  "energyPerFrame": [0.02, 0.05, 0.41, ...],      // length == durationInFrames, 0..1
                                                   // onset strength per video frame

  "sections": [                                    // structural segmentation
    {"start": 0.0,  "end": 22.1, "startFrame": 0,   "endFrame": 663,  "label": "section_1"},
    {"start": 22.1, "end": 51.8, "startFrame": 663, "endFrame": 1554, "label": "section_2"}
  ],

  "features": {                                    // design signals (not timing)
    "brightness": 0.42,                            // 0=dark/warm, 1=bright/cool (centroid)
    "mean_spectral_centroid_hz": 2110.5,
    "dynamic_range_db": 9.3,                       // <6 compressed, >12 wide (beat-hit cap)
    "key": "F", "mode": "minor",                   // Krumhansl-Schmuckler
    "mode_confidence": 0.14                         // margin over runner-up; gate at ~0.05
  }
}
```

## Field notes

- **`fps`** — every `*Frames` field is in these units. The Remotion composition must
  use the same fps (carried in `song.json`).
- **`durationInFrames`** — use directly as the composition length so the video ends
  exactly with the audio.
- **`beatFrames` vs `downbeatFrames`** — beats are every pulse; downbeats are bar
  starts. Use downbeats for calmer, structural events (cuts, bar flashes) and beats
  for busy, per-pulse reactions. Downbeats assume 4/4; for 3/4 or 6/8, regenerate or
  let a design doc override the grouping.
- **`energyPerFrame`** — normalized 0..1 onset strength, one value per frame, ready to
  map to color/opacity/scale. Index it directly by `frame`.
- **`sections`** — boundaries only, unnamed (`section_1`, `section_2`, ...). Naming
  (verse/chorus/drop) comes from the lyrics + judgment during `design`/`plan`. Section
  count scales ~one per 20s, clamped 2–8.
- **`features`** — timbre/harmony signals consumed by `design` (not by timing):
  `brightness` → color temperature + visualizer form; `dynamic_range_db` → beat-hit
  caps; `key`/`mode`/`mode_confidence` → a weak palette warm/cool bias. See
  `design-inference.md` for the mapping. `align_lyrics.py` adds a parallel `density`
  block to `lyrics.json` (words/sec → class) that constrains lyric animation style.

## Consuming it

`useBeatData(beatData, lyrics)` (the bundled hook) precomputes, for the current
frame:

- `energy` — `energyPerFrame[frame]`
- `isBeat` — true within ±1 frame of a beat
- `isDownbeat` — same for downbeats
- `lastBeatFrame` / `lastDownbeatFrame` — for spring/flash timing
- `sectionAt` — the section object containing `frame`
- `activeLyric` — the lyric line whose `[startFrame, endFrame]` spans `frame`

Keep all timing reads going through the hook so components stay declarative and the
power-of-two / offset rules from `remotion-audio.md` are enforced in one place.
