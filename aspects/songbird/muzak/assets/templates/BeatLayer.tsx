// BeatLayer.tsx — discrete beat reactions: the flash and the spring "thud".
//
// Driven entirely by beat_data.json via useBeatData. By default the flash fires
// on DOWNBEATS (calmer, bar-level). Swap to beatFrames for a busier feel.
// The spring scaler is exported so other components can punch on the beat too.

import { AbsoluteFill, spring, interpolate, useVideoConfig } from "remotion";
import { theme } from "./theme";
import type { BeatData } from "./useBeatData";
import { useBeatData } from "./useBeatData";

export const BeatLayer: React.FC<{ beatData: BeatData }> = ({ beatData }) => {
  const beat = useBeatData(beatData);

  // White flash that decays over ~6 frames after each downbeat.
  const sinceDownbeat = beat.frame - beat.lastDownbeatFrame;
  const flash = interpolate(sinceDownbeat, [0, 6], [theme.flashMax, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{ backgroundColor: theme.flashColor, opacity: flash }}
      pointerEvents="none"
    />
  );
};

// Reusable "thud" — element punches up on the most recent beat and springs back.
// Use for logos, hook lyrics, any element that should feel the pulse.
export function useBeatThud(
  beatData: BeatData,
  opts: { from?: number; to?: number; useDownbeat?: boolean } = {}
): number {
  const { fps } = useVideoConfig();
  const beat = useBeatData(beatData);
  const anchor = opts.useDownbeat ? beat.lastDownbeatFrame : beat.lastBeatFrame;
  // "from" defaults to the design-derived scale cap, so a compressed track can't
  // punch harder than its dynamic range warrants. Easing comes from the BPM-derived
  // spring config in the theme.
  return spring({
    frame: beat.frame - anchor,
    fps,
    from: opts.from ?? theme.beatScalePulseMax,
    to: opts.to ?? 1.0,
    config: { damping: theme.springDamping, stiffness: theme.springStiffness, mass: 1 },
  });
}
