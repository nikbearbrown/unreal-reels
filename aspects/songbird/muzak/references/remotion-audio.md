# Remotion Audio APIs — and the traps

Read this before writing any visualizer or audio-reactive component. Remotion
renders by capturing **deterministic frames**: every frame is a pure function of
`useCurrentFrame()`. There is no audio context, no `requestAnimationFrame`, no
event listeners at render time. All reactivity must be computed from frame number
and pre-loaded audio data. This single fact explains every rule below.

## Packages

Install: `@remotion/media-utils` alongside `remotion`. Reference audio (and any
media) with `staticFile('<slug>/audio.wav')` from `public/`.

## Loading audio data

- `useAudioData(src)` — loads the **entire** file into memory as waveform data.
  Fine for short clips; a 3-minute stereo 44.1 kHz track is millions of samples
  and gets slow at render. Use for snippets or when you need the whole waveform.
- `useWindowedAudioData({ src, frame, fps, windowInSeconds })` — loads only the
  audio **around the current frame** via HTTP Range requests. Prefer this for full
  songs. Works in Remotion Studio out of the box; on Lambda, set CORS so range
  requests succeed. Takes an **object** (not positional args) and returns
  `{ audioData, dataOffsetInSeconds }` — keep that offset, you need it. (Available
  from v4.0.240; supports non-WAV from v4.0.383.)

Both are async. Any component that calls them **must** gate rendering:

```tsx
const [handle] = useState(() => delayRender("audio"));
const audioData = useAudioData(src);            // or useWindowedAudioData(...)
useEffect(() => {
  if (audioData) continueRender(handle);
}, [audioData, handle]);
if (!audioData) return null;
```

Skip this and frames get captured before data is ready — the visualizer renders
against `null`, no error is thrown, and you get a silently corrupt render. This is
the #1 cause of "looked fine in Studio, blank in the MP4."

## Two ways to react to audio

### A) Real-time FFT — `visualizeAudio(...)`
Returns instantaneous **frequency-domain** energy for the current frame. Drive
spectrum bars, bass pulses, EQ glows.

```tsx
const { audioData, dataOffsetInSeconds } = useWindowedAudioData({ src, frame, fps, windowInSeconds: 10 });
// pass dataOffsetInSeconds through so the FFT lines up with the loaded window
const spectrum = visualizeAudio({ audioData, frame, fps, numberOfSamples: 64, dataOffsetInSeconds });
```

- `numberOfSamples` **must be a power of two** (16, 32, 64, 128, 256, 512).
  Anything else produces garbage. Low counts (16–32) = coarse bass/mid/high
  buckets, good for driving background pulse/scale. High counts (128–512) = a
  bar chart.
- The raw output is **linear**, which front-loads all visible energy into the
  bass and looks flat. **Always log-scale for music:**
  `const v = Math.pow(raw, 0.5);` (or `Math.log`-based). This is not optional.
- FFT gives energy, **not beat timestamps**. For cuts/flashes use the pre-analyzed
  `beatFrames` from `beat_data.json`, not the FFT.

### B) Pre-analyzed beat data — `beat_data.json`
The deterministic, musically-correct timing. Produced offline by
`scripts/analyze_audio.py`. Use it for everything event-like: cuts on downbeats,
beat flashes, spring thuds, lyric hits, energy→color. See
`beat-data-schema.md` and the recipes in `motion-patterns.md`.

The division of labor: **FFT for continuous texture (bars dancing), beat data for
discrete events (things happening on the beat).** Mixing them up — trying to detect
beats from the FFT — gives noisy, imprecise sync.

### Waveform display — `visualizeAudioWaveform` + `createSmoothSvgPath`
Time-domain window around the current frame; good for sparse/vocal passages.

```tsx
const wave = visualizeAudioWaveform({
  audioData, frame, fps, numberOfSamples: 256, windowInSeconds: 1 / fps,
  dataOffsetInSeconds, // when using useWindowedAudioData; no `channel` arg exists
});
// values are -1..1; map them around a vertical midpoint
const d = createSmoothSvgPath({ points: wave.map((y, x) => ({ x, y })) });
// <path d={d as string} stroke={theme.accent} fill="none" />
```

`getWaveformPortion({ audioData, startTimeInSeconds, durationInSeconds, numberOfSamples })`
extracts a trimmed slice — useful for a static "overview" waveform scrubber.

## The frame-offset traps (subtle sync drift)

1. **Trimmed audio.** With `<Audio startFrom={30} />`, the frame you pass to
   `visualizeAudio` must be `frame - 30`. Forget it and the whole visualization is
   offset.
2. **Windowed audio offset.** With `useWindowedAudioData`, pass the hook's
   `dataOffsetInSeconds` straight into `visualizeAudio` / `visualizeAudioWaveform`
   as `dataOffsetInSeconds`. Omit it and you get slow drift over the song. (The
   param is named `dataOffsetInSeconds`, not `audioOffsetInSeconds`.)

## Hard rules

- **No CSS transitions or `@keyframes` animations.** They work in the live preview
  and fail in headless render (frames are captured statically). Use `interpolate`
  for opacity/position/color and `spring` for physical motion. Nothing else.
- **`spring` for "thuds" and bounces; `interpolate` for everything else.**
- **Power-of-two `numberOfSamples`. Log-scale music FFT. Gate every async load.**
- All assets in `public/`, referenced via `staticFile`.

## Reference repos worth copying patterns from

- `remotion-dev/template-music-visualization` — official starting point.
- `satelllte/remotion-audio-visualizer` — clean spectrum-bar structure.
- `marcusstenbeck/remotion-audio-visualizers` — several visualizer styles.
- `reactvideoeditor/remotion-templates` — many ready transition/text components.
