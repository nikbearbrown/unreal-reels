// BackgroundMedia.tsx — the generated per-block clips/stills, one slot each.
//
// This is the layer the wave + lyrics overlay on top of. Each block (B01, B02, ...)
// occupies `chunkSeconds` of the timeline; B07 starts at frame (7-1)*chunk. The
// component reads `media-manifest.json`, which lists ONLY the files you've actually
// generated — any block you haven't made yet simply falls through to the energy
// gradient behind it, so the project always renders.
//
// Generate prompts with scripts/media_prompts.py, drop results in
// public/<slug>/media/<id>.mp4 (or .jpg), then add them to media-manifest.json:
//   { "slug": "fishermans-wife", "chunkSeconds": 5,
//     "blocks": { "B03": "B03.mp4", "B07": "B07.jpg" } }

import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  Sequence,
  staticFile,
  useVideoConfig,
} from "remotion";
import manifest from "./media-manifest.json";

const isVideo = (f: string) => /\.(mp4|mov|webm|m4v)$/i.test(f);

export const BackgroundMedia: React.FC = () => {
  const { fps } = useVideoConfig();
  const chunk = Math.round((manifest.chunkSeconds ?? 5) * fps);
  const slug = manifest.slug;
  const blocks = (manifest.blocks ?? {}) as Record<string, string>;

  return (
    <AbsoluteFill>
      {Object.entries(blocks).map(([id, file]) => {
        const n = parseInt(id.replace(/[^0-9]/g, ""), 10); // "B07" -> 7
        if (!n) return null;
        const from = (n - 1) * chunk;
        const src = staticFile(`${slug}/media/${file}`);
        const cover: React.CSSProperties = {
          width: "100%",
          height: "100%",
          objectFit: "cover",
        };
        return (
          <Sequence key={id} from={from} durationInFrames={chunk} name={id}>
            {isVideo(file) ? (
              // muted: the composition's own <Audio> carries the music.
              <OffthreadVideo src={src} muted style={cover} />
            ) : (
              <Img src={src} style={cover} />
            )}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
