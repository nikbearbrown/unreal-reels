// MusicVideo.tsx — the OVERLAY composition for "Strange Brothers".
//
// Layer order, bottom to top:
//   existing video (+ scrim) ▸ audiogram waveform ▸ karaoke lyric layer ▸ <Audio>
//
// Unlike the full muzak pipeline there is no energy-gradient background and no
// per-block generated media: the finished source.mp4 IS the background. The audio
// is the SAME track extracted from that video, so the waveform (which analyzes the
// audio) and the picture stay locked. The OffthreadVideo is muted; this <Audio> is
// the only sound source.

import { AbsoluteFill, Audio, staticFile } from "remotion";
import { Waveform, SpectrumBars } from "./AudioVisualizer";
import { VideoBackground } from "./VideoBackground";
import { LyricLayer } from "./LyricLayer";
import { theme } from "./theme";
import type { BeatData, Lyrics } from "./useBeatData";

import beatData from "./beat_data.json";
import lyrics from "./lyrics.json";

const SLUG = "__SLUG__";
const AUDIO_SRC = staticFile(`${SLUG}/audio.wav`);

// "audiogram" => the dense oscilloscope waveform across the whole video.
const Visualizer: React.FC = () =>
  theme.visualizerType === "audiogram" || theme.visualizerType === "waveform" ? (
    <Waveform src={AUDIO_SRC} />
  ) : (
    <SpectrumBars src={AUDIO_SRC} />
  );

// Lyrics-only by default; pass showWaveform to add the audiogram. Root.tsx registers
// both a no-wave ("MusicVideo") and a wave ("MusicVideo-Wave") composition.
export const MusicVideo: React.FC<{ showWaveform?: boolean }> = ({
  showWaveform = false,
}) => {
  const bd = beatData as BeatData;
  const ly = lyrics as Lyrics;
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <VideoBackground />
      {showWaveform ? <Visualizer /> : null}
      <LyricLayer beatData={bd} lyrics={ly} />
      <Audio src={AUDIO_SRC} />
    </AbsoluteFill>
  );
};
