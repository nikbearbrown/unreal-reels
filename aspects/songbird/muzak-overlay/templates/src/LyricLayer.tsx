// LyricLayer.tsx — renders lyrics.json, frame by frame.
//
// TIMING is fixed (from lyrics.json / useBeatData.activeLyric). STYLE is the
// design seam's job: branch on theme.lyricStyle. A design doc adds new styles
// here WITHOUT touching timing. The baseline style is "fade-beat".

import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "./theme";
import type { BeatData, Lyrics } from "./useBeatData";
import { useBeatData } from "./useBeatData";

export const LyricLayer: React.FC<{ beatData: BeatData; lyrics: Lyrics }> = ({
  beatData,
  lyrics,
}) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const beat = useBeatData(beatData, lyrics);
  const ly = beat.activeLyric;
  if (!ly) return null;

  const local = frame - ly.startFrame;
  const remaining = ly.endFrame - frame;
  const isHook = !!ly.tag && /chorus|hook/i.test(ly.tag);

  // Guard zero-length fades (e.g. "instant" style sets lyricInFrames = 0, which
  // would make interpolate's input range non-monotonic and throw).
  const inOp =
    theme.lyricInFrames <= 0
      ? 1
      : interpolate(local, [0, theme.lyricInFrames], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
  const outOp =
    theme.lyricOutFrames <= 0
      ? 1
      : interpolate(remaining, [0, theme.lyricOutFrames], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
  const opacity = Math.min(inOp, outOp);

  // gentle scale pop on the most recent beat, capped by the design scale limit and
  // eased with the BPM-derived spring config from the theme.
  const popPeak = 1 + (theme.beatScalePulseMax - 1) * 0.4; // softer than the beat layer
  const pop = spring({
    frame: frame - beat.lastBeatFrame,
    fps,
    from: popPeak,
    to: 1.0,
    config: { damping: theme.springDamping, stiffness: theme.springStiffness, mass: 1 },
  });

  // --- style branch (design doc extends this) ---
  // Drop shadow keeps text legible over background media / the waveform.
  const baseStyle: React.CSSProperties = {
    fontFamily: theme.fontFamily,
    fontWeight: theme.fontWeight,
    fontSize: isHook ? theme.hookSize : theme.lyricSize,
    color: isHook ? theme.accent2 : theme.textColor,
    textAlign: "center",
    maxWidth: "82%",
    lineHeight: 1.15,
    opacity,
    transform: `scale(${pop})`,
    textShadow: "0 2px 18px rgba(0,0,0,0.55)",
  };

  let content = <div style={baseStyle}>{ly.text}</div>;

  if (
    theme.lyricStyle === "karaoke" ||
    theme.lyricStyle === "per-word-pop" ||
    theme.lyricStyle === "word-by-word"
  ) {
    // True karaoke when forced-aligned word frames exist (align_lyrics_audio.py):
    // each word lights at the frame it is actually sung. Without word frames we
    // fall back to an even stagger across the line.
    const hasReal = !!ly.words && ly.words.length > 0;
    const words = hasReal
      ? ly.words!.map((w) => ({ text: w.text, on: w.startFrame }))
      : ly.text.split(" ").map((t, i) => ({ text: t, on: ly.startFrame + i * 2 }));
    // current word = the last one whose onset has passed.
    let cur = -1;
    for (let i = 0; i < words.length; i++) if (words[i].on <= frame) cur = i;
    content = (
      <div style={{ ...baseStyle, transform: "none", display: "flex", gap: 18, flexWrap: "wrap", justifyContent: "center" }}>
        {words.map((w, i) => {
          // upcoming words sit dim; the current word is brightest ("a little
          // lighter"); already-sung words stay readable but recede.
          const state = i > cur ? "upcoming" : i === cur ? "current" : "sung";
          const wordOpacity =
            state === "upcoming" ? 0.5 : state === "current" ? 1 : 0.85;
          return (
            <span
              key={i}
              style={{
                opacity: Math.min(wordOpacity, outOp),
                color: state === "current" ? "#FFFFFF" : undefined,
                display: "inline-block",
                transition: "none",
              }}
            >
              {w.text}
            </span>
          );
        })}
      </div>
    );
  }

  // Center the lyrics ON the waveform centerline (theme.waveformMid), so the wave
  // oscillates around the words rather than sitting below them.
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: `${theme.waveformMid * 100}%`,
          transform: "translateY(-50%)",
          display: "flex",
          justifyContent: "center",
          padding: "0 80px",
        }}
      >
        {content}
      </div>
    </AbsoluteFill>
  );
};
