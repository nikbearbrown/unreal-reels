# Motion patterns — the reusable recipes

These are the moves `build` assembles. Each is a small, composable idea driven by
either `beat_data.json` (discrete events) or the FFT (continuous texture). All
colors/sizes come from the `theme` object (see the design seam) so they restyle
cleanly. All examples assume `const frame = useCurrentFrame()`.

## Choosing a visualizer per section

`plan` assigns one dominant visualizer per section. Match the visualizer to what
the section *is*, not to novelty — a visualizer that doesn't track something
audible is noise. Rough chooser:

| Section feel | Energy signature | Visualizer |
|---|---|---|
| Drop / dense instrumental / loud chorus | high, sustained `energyPerFrame` | **Spectrum bars** (64–128 samples), log-scaled |
| Vocal verse / sparse / intimate | low–mid, spiky | **Smooth waveform** path, thin stroke |
| Bass-led / rhythmic build | strong low band | **Bass pulse** — radius/scale from 16-sample FFT bin 0–1 |
| Quiet intro / outro / breakdown | low, flat | **Minimal** — energy→background only, maybe a slow line |
| Beat-forward bridge | clear downbeats | **Beat grid** — shapes punching on `downbeatFrames` |

You can layer a subtle continuous visualizer under a discrete one, but keep one
**dominant** read per section so the eye knows where to look.

## Energy → background color (continuous)

```tsx
const energy = beat.energy; // energyPerFrame[frame], 0..1, from useBeatData
const hue = interpolate(energy, [0, 1], theme.bgHueRange);   // e.g. [220, 280]
const lum = interpolate(energy, [0, 1], [8, 16]);            // subtle breathing
const bg = `hsl(${hue}, ${theme.bgSat}%, ${lum}%)`;
```

Keep luminance shifts small; the background should breathe, not strobe.

## Beat flash (discrete)

```tsx
const sinceBeat = frame - beat.lastBeatFrame;       // frames since last beat
const flash = interpolate(sinceBeat, [0, 6], [theme.flashMax, 0],
  { extrapolateRight: "clamp" });
// <AbsoluteFill style={{ background: theme.flashColor, opacity: flash }} />
```

Use `downbeatFrames` instead of `beatFrames` for a calmer, bar-level flash.

## Spring "thud" on beat (discrete, physical)

The signature beat reaction: an element punches up on the beat and springs back.

```tsx
const scale = spring({
  frame: frame - beat.lastBeatFrame,
  fps,
  from: 1.18, to: 1.0,
  config: { damping: 9, stiffness: 200, mass: 1 },
});
```

Lower `damping` = more bounce; higher `stiffness` = snappier attack. Drive logo
scale, lyric pop, a shape's size. Reach for `spring` (not `interpolate`) whenever
motion should feel physical.

## Spectrum bars (continuous FFT)

```tsx
const N = 64; // power of two
const spectrum = visualizeAudio({ audioData, frame, fps, numberOfSamples: N });
const bars = spectrum.map((raw) => Math.pow(raw, 0.6)); // log-ish scaling
// render N rects; height = bars[i] * maxHeight; mirror around center for symmetry
```

Center at the lower third, or mirror vertically for a "mouth" shape. Color bars by
index for a gradient, or hold a single `theme.accent`.

## Smooth waveform (continuous, vocal sections)

See `remotion-audio.md` for `visualizeAudioWaveform` + `createSmoothSvgPath`. Thin
stroke, centered, low opacity over the background. Reads as "the voice" — best when
lyrics are the focus.

## Scene cuts on the beat (discrete structure)

Hard-cut between background "scenes" on downbeats so structure changes land
musically:

```tsx
{downbeatFrames.map((f, i) => (
  <Sequence key={i} from={f}
    durationInFrames={(downbeatFrames[i + 1] ?? durationInFrames) - f}>
    <Scene variant={i % sceneVariants.length} />
  </Sequence>
))}
```

Don't cut on *every* beat for a whole song — it's exhausting. Cut on section
boundaries and selected downbeats called out in the plan.

## Kinetic / timed lyrics (discrete, from lyrics.json)

`useBeatData` exposes `activeLyric` (the line whose `[startFrame, endFrame]`
contains `frame`). The **timing** is fixed here; the **style** is the theme's job:

```tsx
const ly = beat.activeLyric;
if (!ly) return null;
const local = frame - ly.startFrame;
const inOp = interpolate(local, [0, 8], [0, 1], { extrapolateRight: "clamp" });
// theme.lyricStyle decides: fade, slide, per-word pop, scale-on-beat, etc.
```

A future design doc supplies `theme.lyricStyle`; until then `default-look.md`'s
baseline (fade + gentle beat-scale) applies. Hooks/choruses can get bigger type —
read `ly.tag` to branch.

## Music-under-voice ducking (if a VO/stinger is layered)

Most muzak videos are music-only, but if a spoken layer exists, duck the music
volume with `interpolate` on the `<Audio volume>` prop:

```tsx
<Audio src={music} volume={(f) =>
  interpolate(f, [vStart - 5, vStart, vEnd, vEnd + 5], [1, 0.25, 0.25, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
```

## Drawing-in SVG on beat (doodle aesthetic)

For hand-drawn assets, animate `stroke-dashoffset` from `frame` so a path "draws
itself," and tie the speed to the beat for a synced reveal — pairs well with media
borrowed from the doodle/cajal pipelines.

## Media slots (the sparing custom-media moments)

For each asset the plan asked the user to supply, wrap it in a `<Sequence>` at the
planned frame. If the file is missing, render a labeled placeholder (filename +
target) so the project still runs and the gap is obvious:

```tsx
<Sequence from={startFrame} durationInFrames={dur}>
  {fileExists
    ? <Img src={staticFile(`${slug}/media/${file}`)} />
    : <Placeholder label={`${file} @ f${startFrame}`} />}
</Sequence>
```

Never block the whole build on media that hasn't arrived.
