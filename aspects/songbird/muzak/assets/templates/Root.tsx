// Root.tsx — composition registration.
//
// `build` fills width/height/fps from song.json and durationInFrames from
// beat_data.json so the video ends exactly with the audio. There is one
// composition: "MusicVideo".

import { Composition } from "remotion";
import { MusicVideo } from "./MusicVideo";
import beatData from "./beat_data.json";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="MusicVideo"
      component={MusicVideo}
      durationInFrames={beatData.durationInFrames}
      fps={beatData.fps}
      width={1920}
      height={1080}
    />
  );
};
