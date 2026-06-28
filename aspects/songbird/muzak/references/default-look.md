# Default look — the neutral fallback

This is the skin muzak ships **only when the `design` phase was skipped** and no
design doc exists. It is deliberately plain and legible so the *mechanics* read
clearly. Normally you don't end up here: the `design` phase infers a real look from
the song (see `design-inference.md`) and writes `theme.ts`. This baseline is the
floor, not the target.

## Precedence for the look (highest wins)

1. **A hand-written design doc** at `design/[slug].md` — a person who knows what they want.
2. **The inferred `design.json`** from the `design` phase (→ generated `theme.ts`).
3. **This neutral baseline** — only if `design` never ran.

Everything below is expressed as a single `theme` object so swapping looks is a
one-file change. The mechanical components (`AudioVisualizer`, `BeatLayer`,
`LyricLayer`, `MusicVideo`) read **only** from `theme` — they never hardcode a
color, font, or lyric style.

```ts
// src/theme.ts  (default baseline)
export const theme = {
  // --- color ---
  bgHueRange: [222, 268],     // energy 0..1 maps across this hue range
  bgSat: 45,                  // background saturation %
  accent: "#E8E6FF",          // bars / waveform stroke
  accent2: "#7C6CFF",         // secondary (gradients, hooks)
  textColor: "#FFFFFF",
  flashColor: "#FFFFFF",
  flashMax: 0.22,             // peak opacity of a beat flash (keep subtle)

  // --- type ---
  fontFamily: "Inter, system-ui, sans-serif",
  lyricSize: 72,              // px, body lyric lines
  hookSize: 120,              // px, lines tagged Chorus/Hook
  fontWeight: 700,

  // --- lyric motion (the design seam restyles THIS) ---
  lyricStyle: "fade-beat",    // baseline: fade in + gentle scale-on-beat
  lyricInFrames: 8,           // fade-in length
  lyricOutFrames: 8,          // fade-out length

  // --- visualizer defaults ---
  spectrumSamples: 64,        // power of two
  spectrumMaxHeight: 240,     // px
  waveformStroke: 3,          // px
};
```

## Baseline behavior the components implement

- **Background:** energy→hue across `bgHueRange`, low saturated luminance that
  breathes (no strobing).
- **Visualizer:** mirrored spectrum bars centered in the lower third for loud
  sections; a thin centered waveform for sparse/vocal sections. Chosen per the
  `plan`'s section map.
- **Beat reaction:** a subtle white `flashMax` flash on downbeats; spring "thud"
  available for any element that opts in.
- **Lyrics:** centered, fade in/out at the line's start/end frames, with a small
  `spring` scale pop on the nearest beat. Lines tagged `Chorus`/`Hook` render at
  `hookSize` in `accent2`.
- **Title card:** song title fades in over the first ~2s (60 frames) using
  `interpolate`, then out before the first vocal.

## How a design doc plugs in

A design doc (song-specific `design/[slug].md`, or global
`references/design-doc.md`) may:

1. Replace any `theme` value (palette, type, sizes, `flashMax`, hue range).
2. Define a new `lyricStyle` (e.g. `"per-word-pop"`, `"typewriter"`,
   `"slide-up-mask"`) — implement it as a branch in `LyricLayer`, keyed off
   `theme.lyricStyle`, **without changing lyric timing**.
3. Add scene backgrounds, textures, or transition language for `MusicVideo`.
4. Specify per-section visual treatments that refine the generic chooser in
   `motion-patterns.md`.

The contract the design doc relies on: **timing and structure are fixed by the
mechanics; the design doc only changes how things look and move, never when they
happen.** That separation is what lets the same analyzed song be re-skinned
without re-timing.
