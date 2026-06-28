// MusicVideo.tsx — the composition. Layer order, bottom to top:
//   background (energy->color) ▸ visualizer (per section) ▸ media slots ▸
//   beat layer (flash) ▸ lyric layer ▸ title card ▸ the single <Audio>.
//
// `build` fills SECTION_VISUALIZERS (from the plan) and MEDIA_SLOTS (the sparing
// custom-media asks). Anything code-generated needs no slot. Missing media files
// render a labeled placeholder so the project always runs.

import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { theme } from "./theme";
import { SpectrumBars, Waveform } from "./AudioVisualizer";
import { BackgroundMedia } from "./BackgroundMedia";
import { BeatLayer } from "./BeatLayer";
import { LyricLayer } from "./LyricLayer";
import { useBeatData } from "./useBeatData";
import type { BeatData, Lyrics } from "./useBeatData";

import beatData from "./beat_data.json";
import lyrics from "./lyrics.json";
import manifest from "./media-manifest.json";

// slug from the manifest; title prefers the lyrics' TITLE: line, else the slug.
const SLUG = manifest.slug;
const TITLE =
  (lyrics as { title?: string }).title ??
  SLUG.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
const AUDIO_SRC = staticFile(`${SLUG}/audio.wav`);

// Which visualizer dominates each section (spectrum through the build, waveform
// through the climax/collapse). Unlisted sections fall back to the theme default.
const SECTION_VISUALIZERS: Record<string, "spectrum" | "waveform" | "none"> = {
  section_1: "spectrum", section_2: "spectrum", section_3: "spectrum", section_4: "spectrum",
  section_5: "waveform", section_6: "waveform", section_7: "waveform", section_8: "waveform",
};
// The sparing custom-media moments. Leave empty if the video is all code.
type MediaSlot = { file: string; startFrame: number; durationInFrames: number };
const MEDIA_SLOTS: MediaSlot[] = [
  // { file: "hero.jpg", startFrame: 1554, durationInFrames: 240 },
];
// Set true only for files the user has actually delivered into public/<slug>/media/.
const PRESENT_MEDIA = new Set<string>([]);

// --- Background: energy breathes the hue -----------------------------------
const Background: React.FC = () => {
  const beat = useBeatData(beatData as BeatData);
  const hue = interpolate(beat.energy, [0, 1], theme.bgHueRange);
  const lum = interpolate(beat.energy, [0, 1], theme.bgLumRange);
  return (
    <AbsoluteFill
      style={{ backgroundColor: `hsl(${hue}, ${theme.bgSat}%, ${lum}%)` }}
    />
  );
};

// --- Visualizer chosen per current section ---------------------------------
// "audiogram" is a GLOBAL look: the dense oscilloscope waveform for the whole
// video, ignoring the per-section map. Otherwise fall back to the per-section
// choice ("waveform" => smooth line, anything else => spectrum bars).
const AUDIOGRAM = theme.visualizerType === "audiogram";
const themeDefault: "spectrum" | "waveform" =
  theme.visualizerType === "waveform" ? "waveform" : "spectrum";

const SectionVisualizer: React.FC = () => {
  const beat = useBeatData(beatData as BeatData);
  if (AUDIOGRAM) return <Waveform src={AUDIO_SRC} />;
  const label = beat.sectionAt?.label ?? "";
  const kind = SECTION_VISUALIZERS[label] ?? themeDefault;
  if (kind === "spectrum") return <SpectrumBars src={AUDIO_SRC} />;
  if (kind === "waveform") return <Waveform src={AUDIO_SRC} />;
  return null;
};

const Placeholder: React.FC<{ label: string }> = ({ label }) => (
  <AbsoluteFill
    style={{
      justifyContent: "center",
      alignItems: "center",
      border: `4px dashed ${theme.accent}`,
      color: theme.accent,
      fontFamily: theme.fontFamily,
      fontSize: 40,
      opacity: 0.5,
    }}
  >
    media: {label}
  </AbsoluteFill>
);

// --- Title card over the first ~2s -----------------------------------------
const TitleCard: React.FC<{ title: string }> = ({ title }) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [10, 40, 75, 105], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          fontFamily: theme.fontFamily,
          fontWeight: theme.fontWeight,
          fontSize: theme.hookSize,
          color: theme.textColor,
          opacity: op,
        }}
      >
        {title}
      </div>
    </AbsoluteFill>
  );
};

export const MusicVideo: React.FC = () => {
  const bd = beatData as BeatData;
  const ly = lyrics as Lyrics;
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {/* layers, bottom -> top: gradient -> generated media -> waveform -> beat -> lyrics */}
      <Background />
      <BackgroundMedia />
      <SectionVisualizer />

      {MEDIA_SLOTS.map((m, i) => (
        <Sequence key={i} from={m.startFrame} durationInFrames={m.durationInFrames}>
          {PRESENT_MEDIA.has(m.file) ? (
            <Img src={staticFile(`${SLUG}/media/${m.file}`)} />
          ) : (
            <Placeholder label={`${m.file} @ f${m.startFrame}`} />
          )}
        </Sequence>
      ))}

      <BeatLayer beatData={bd} />
      <LyricLayer beatData={bd} lyrics={ly} />
      <TitleCard title={TITLE} />

      <Audio src={AUDIO_SRC} />
    </AbsoluteFill>
  );
};
