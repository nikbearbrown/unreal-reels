// Root.tsx — composition registration for the Strange Brothers overlay.
//
// width/height match the SOURCE video (__WIDTH__x__HEIGHT__) so there is no rescale; fps and
// durationInFrames come from beat_data.json so the timeline ends exactly with the
// track. Default composition "MusicVideo" is lyrics-only (no audiogram); opt into
// the waveform with "MusicVideo-Wave".

import { Composition } from "remotion";
import { MusicVideo } from "./MusicVideo";
import beatData from "./beat_data.json";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* default look: karaoke lyrics only, no waveform */}
      <Composition
        id="MusicVideo"
        component={MusicVideo}
        durationInFrames={beatData.durationInFrames}
        fps={beatData.fps}
        width={__WIDTH__}
        height={__HEIGHT__}
        defaultProps={{ showWaveform: false }}
      />
      {/* opt-in variant: same timing + the audiogram waveform */}
      <Composition
        id="MusicVideo-Wave"
        component={MusicVideo}
        durationInFrames={beatData.durationInFrames}
        fps={beatData.fps}
        width={__WIDTH__}
        height={__HEIGHT__}
        defaultProps={{ showWaveform: true }}
      />
    </>
  );
};
