// AudioVisualizer.tsx — spectrum bars + smooth waveform.
//
// Uses useAudioData (loads the whole file ONCE) rather than useWindowedAudioData.
// Windowed loading re-fetches every window and stalls Studio playback (the audio
// "hiccups" at each boundary); for a song-length file, load-once is smooth and the
// memory cost is fine. No dataOffsetInSeconds needed when the whole file is loaded.

import { useEffect, useState } from "react";
import {
  AbsoluteFill,
  continueRender,
  delayRender,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  useAudioData,
  visualizeAudio,
  visualizeAudioWaveform,
  createSmoothSvgPath,
} from "@remotion/media-utils";
import { theme } from "./theme";

// --- Spectrum bars (loud / dense sections) ---------------------------------
export const SpectrumBars: React.FC<{ src: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const [handle] = useState(() => delayRender("spectrum-audio"));
  const audioData = useAudioData(src);
  useEffect(() => {
    if (audioData) continueRender(handle);
  }, [audioData, handle]);
  if (!audioData) return null;

  const N = theme.spectrumSamples; // power of two
  const raw = visualizeAudio({ audioData, frame, fps, numberOfSamples: N });
  const bars = raw.map((v) => Math.pow(v, 0.6)); // log-ish scaling

  const barW = width / N;
  const cy = height * 0.82; // bottom band
  return (
    <AbsoluteFill>
      <svg width={width} height={height}>
        {bars.map((v, i) => {
          const h = v * theme.spectrumMaxHeight;
          const x = i * barW;
          return (
            <rect
              key={i}
              x={x + barW * 0.15}
              y={cy - h}
              width={barW * 0.7}
              height={h * 2}
              rx={barW * 0.2}
              fill={theme.accent}
              opacity={0.85}
            />
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

// --- Smooth waveform (sparse / vocal sections) -----------------------------
export const Waveform: React.FC<{ src: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const [handle] = useState(() => delayRender("waveform-audio"));
  const audioData = useAudioData(src);
  useEffect(() => {
    if (audioData) continueRender(handle);
  }, [audioData, handle]);
  if (!audioData) return null;

  const samples = visualizeAudioWaveform({
    audioData,
    frame,
    fps,
    numberOfSamples: 512, // dense, like the reference voiceprint
    windowInSeconds: 2.5, // multi-second window => full-width busy waveform (not a 1-frame sliver)
    normalize: true,
  });

  // band centerline + height come from the theme so the lyrics center on it
  const mid = height * theme.waveformMid;
  const amp = height * theme.waveformAmp;
  const points = samples.map((y, i) => ({
    x: (i / (samples.length - 1)) * width,
    y: mid + y * amp, // samples are -1..1
  }));
  const d = createSmoothSvgPath({ points });
  return (
    <AbsoluteFill>
      <svg width={width} height={height}>
        <path
          d={d as string}
          stroke={theme.accent}
          strokeWidth={theme.waveformStroke}
          fill="none"
          opacity={0.8}
        />
      </svg>
    </AbsoluteFill>
  );
};
