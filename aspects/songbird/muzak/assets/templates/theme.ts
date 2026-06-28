// theme.ts — the single styling surface.
//
// NORMALLY this file is GENERATED from design.json by `infer_design.py`
// (--emit-theme) during the `design` phase, so the look is derived from the song.
// This committed version is the neutral FALLBACK (from references/default-look.md)
// used only if `design` was skipped. Either way, mechanical components read ONLY
// from this object — never hardcode palette/type/motion in a component, and never
// raise a cap (flashMax / beatScalePulseMax) for drama: those are fidelity limits
// computed from the track's dynamic range.

export const theme = {
  // palette
  background: "#15121F",
  accent: "#E8E6FF",
  accent2: "#7C6CFF",
  accentWarm: "#D9A066",
  textColor: "#FFFFFF",
  flashColor: "#FFFFFF",
  flashMax: 0.22, // HARD cap from dynamic range (design phase overwrites)
  beatScalePulseMax: 1.15, // HARD cap from dynamic range

  // motion vocabulary (from BPM)
  easingCharacter: "crisp" as "heavy" | "smooth" | "crisp" | "snappy",
  springDamping: 12,
  springStiffness: 160,

  // type
  fontFamily: "Inter, system-ui, sans-serif",
  lyricSize: 56,
  hookSize: 88,
  fontWeight: 700,
  lyricStyle: "karaoke" as
    | "karaoke"
    | "fade-beat"
    | "per-word-pop"
    | "character-spring"
    | "word-spring"
    | "word-by-word"
    | "line-wipe"
    | "instant",
  lyricInFrames: 8,
  lyricOutFrames: 8,
  readableHoldFrames: 18,

  // visualizer: "audiogram" = dense oscilloscope waveform for the whole video
  visualizerType: "audiogram" as "audiogram" | "bars" | "ring" | "waveform" | "hybrid" | "spectrum",
  spectrumSamples: 64, // power of two
  spectrumMaxHeight: 240,
  waveformStroke: 3,
  // audiogram band: vertical centerline + height (fractions of frame height).
  // Lyrics center ON this line so the wave oscillates around the words.
  waveformMid: 0.78,
  waveformAmp: 0.15,

  // background energy-breathing (kept for the animated gradient)
  bgHueRange: [222, 268] as [number, number],
  bgSat: 45,
  // background luminance range (energy 0..1). Dark default [8,16]; for the
  // "ink" look (stick figures: white bg, black ink) use e.g. [96, 99] + bgSat 0.
  bgLumRange: [8, 16] as [number, number],
};
