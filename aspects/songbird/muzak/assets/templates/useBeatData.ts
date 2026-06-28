// useBeatData.ts — the single place timing is read.
//
// Every component pulls frame-indexed timing from here so the power-of-two /
// offset rules live in one spot and components stay declarative. Drop
// beat_data.json and lyrics.json into src/ (or import via staticFile + fetch)
// and pass them in from the composition.

import { useCurrentFrame } from "remotion";

export type Section = {
  start: number;
  end: number;
  startFrame: number;
  endFrame: number;
  label: string;
};

export type BeatData = {
  version: number;
  fps: number;
  bpm: number;
  durationInSeconds: number;
  durationInFrames: number;
  beatTimestamps: number[];
  downbeatTimestamps: number[];
  beatFrames: number[];
  downbeatFrames: number[];
  energyPerFrame: number[];
  sections: Section[];
};

export type LyricWord = { text: string; startFrame: number; endFrame: number };

export type LyricLine = {
  index: number;
  text: string;
  section: string;
  tag: string | null;
  startFrame: number;
  endFrame: number;
  // present only when lyrics were forced-aligned (align_lyrics_audio.py).
  // Enables true word-by-word / karaoke timing instead of an even guess.
  words?: LyricWord[];
};

export type Lyrics = { version: number; fps: number; lines: LyricLine[] };

function lastAtOrBefore(frames: number[], frame: number): number {
  // frames is sorted ascending; return the largest <= frame, or 0.
  let lo = 0,
    hi = frames.length - 1,
    ans = 0;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (frames[mid] <= frame) {
      ans = frames[mid];
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  return ans;
}

function near(frames: number[], frame: number, tol = 1): boolean {
  // true if any beat is within tol frames of the current frame.
  for (const f of frames) {
    if (Math.abs(f - frame) <= tol) return true;
    if (f - frame > tol) break; // sorted; no point continuing
  }
  return false;
}

export function useBeatData(beat: BeatData, lyrics?: Lyrics) {
  const frame = useCurrentFrame();
  const energy = beat.energyPerFrame[frame] ?? 0;

  const lastBeatFrame = lastAtOrBefore(beat.beatFrames, frame);
  const lastDownbeatFrame = lastAtOrBefore(beat.downbeatFrames, frame);

  const sectionAt =
    beat.sections.find((s) => frame >= s.startFrame && frame < s.endFrame) ??
    beat.sections[beat.sections.length - 1] ??
    null;

  const activeLyric =
    lyrics?.lines.find(
      (l) => frame >= l.startFrame && frame < l.endFrame
    ) ?? null;

  return {
    frame,
    energy,
    isBeat: near(beat.beatFrames, frame, 1),
    isDownbeat: near(beat.downbeatFrames, frame, 1),
    lastBeatFrame,
    lastDownbeatFrame,
    sectionAt,
    activeLyric,
  };
}
