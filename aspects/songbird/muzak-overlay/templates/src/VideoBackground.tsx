// VideoBackground.tsx — the existing finished video, full-frame, as the bottom
// layer everything else overlays on.
//
// This is the overlay pipeline's replacement for muzak's per-block BackgroundMedia:
// instead of stitching generated clips per beat, we play ONE source video for the
// whole timeline. It is MUTED — the composition's own <Audio> (the same audio
// extracted from this video) carries the sound, which keeps the waveform analysis
// and playback perfectly in sync.
//
// On top of the video sits a soft scrim: a vertical gradient that darkens a
// horizontal band centered on theme.waveformMid, so the white karaoke text and
// waveform read cleanly over bright or busy footage without hiding the video.

import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { theme } from "./theme";

const SLUG = "__SLUG__";
const VIDEO_SRC = staticFile(`${SLUG}/source.mp4`);

const Scrim: React.FC = () => {
  // Band center (%) and half-height (%) from the theme.
  const mid = theme.waveformMid * 100;
  const half = (theme.scrimHeight * 100) / 2;
  const top = Math.max(mid - half, 0);
  const bot = Math.min(mid + half, 100);
  const o = theme.scrimOpacity;
  // transparent -> dark at band edges -> dark across the band -> transparent.
  const gradient =
    `linear-gradient(to bottom,` +
    ` rgba(0,0,0,0) ${top}%,` +
    ` rgba(0,0,0,${o}) ${mid}%,` +
    ` rgba(0,0,0,0) ${bot}%)`;
  return <AbsoluteFill style={{ background: gradient }} />;
};

export const VideoBackground: React.FC = () => {
  const cover: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  };
  return (
    <AbsoluteFill>
      <OffthreadVideo src={VIDEO_SRC} muted style={cover} />
      <Scrim />
    </AbsoluteFill>
  );
};
