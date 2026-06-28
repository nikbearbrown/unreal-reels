---
name: muzak-overlay
description: >
  Add synced karaoke lyrics + an audiogram waveform on top of an EXISTING finished
  music video (e.g. an AI-generated video) — the same lyric/visualizer layer the
  other Songbird videos have, composited over footage that is already done, without
  regenerating or re-rendering the original. Use when the user has a finished .mp4
  plus its lyrics and wants to "add the lyrics like the others", "overlay synced
  captions on this video", "put a karaoke/audiogram layer on an existing clip", or
  types `overlay`. Input: a video file + a lyrics .txt. Output: a runnable Remotion
  project (one kebab-case folder) that overlays the lyric + waveform layer; the
  skill stops at the project + render commands and never claims to produce the MP4
  itself (rendering needs headless Chromium).
metadata:
  tags: remotion, lyric-video, karaoke, audiogram, overlay, music-video, captions, songbird
---

# muzak-overlay — Lyrics + audiogram over an existing video

Part of **Songbird**. This is the **overlay** sibling of the `muzak` skill.

- `muzak` **builds** a video from a WAV: generated backgrounds, per-block media, the
  whole motion-graphics composition.
- `muzak-overlay` **decorates** a video that is already finished: it adds only the
  karaoke lyric layer + audiogram waveform on top, keeping the original footage as
  the background. Use it when the picture is done (often an AI-generated music video)
  and the only thing missing is the synced-lyrics layer the other songs have.

## The one rule everything else serves

**The audio is ground truth, and the audio comes from the video itself.** The script
extracts the audio out of the source `.mp4`, analyzes *that*, and plays *that* same
track in the composition. Picture and waveform can never drift, because they are the
same recording. Never bring in a separate WAV — extract from the video.

## Pipeline (one command does steps 1–5)

`scripts/overlay_new.py` orchestrates everything; it reuses muzak's analysis and
alignment scripts (single source of truth) and stamps the `templates/` project.

1. **Extract audio** — `ffmpeg` pulls `audio.wav` from the source video.
2. **Match dimensions** — `ffprobe` reads width/height/fps; the composition is sized
   to the source exactly (no rescale, no letterbox).
3. **Analyze** — `analyze_audio.py` (librosa) → `beat_data.json` (duration, fps,
   per-frame energy, sections). Sets the composition length so it ends with the track.
4. **Lyric timing** → `lyrics.json`:
   - default = `align_lyrics.py` beat-grid **seed** (no extra deps, even spacing —
     good enough to preview layout, but it does not know *when* each word is sung).
   - `--whisper` = `align_lyrics_audio.py` **forced alignment** (faster-whisper):
     true per-word karaoke timing locked to the vocal. **Use this for the final.**
5. **Stamp** the Remotion project (`templates/` → `<slug>/`) and drop the JSON +
   assets where Remotion expects them.

Then **finish locally** (Node + Chromium): `npm install` → `npm run studio` to
preview/nudge → `npm run render`. The skill never renders the MP4 itself.

### Run it

```bash
python scripts/overlay_new.py \
  --mp4 "Strange Brothers (feat. Mayfield King).mp4" \
  --lyrics song-03.txt --slug strange-brothers --dir .
# accurate karaoke (after a first seed pass), forced-aligned to the vocal:
python scripts/overlay_new.py --mp4 source.mp4 --lyrics song-03.txt \
  --slug strange-brothers --dir . --whisper --model small --force
```

`analyze` needs `librosa`; `--whisper` needs `faster-whisper` (downloads a small
model on first run). On Bear's Mac use the conda `muzak` env for librosa.

## What the composition does (templates/src)

Layer order, bottom → top:

1. **`VideoBackground.tsx`** — the source `.mp4` full-frame (`OffthreadVideo`,
   `object-fit: cover`, **muted**) + a soft **scrim**: a vertical gradient that
   darkens a horizontal band centered on `theme.waveformMid` so white text/waveform
   stay legible over bright or busy footage. The video is muted because…
2. **`AudioVisualizer.tsx` → `Waveform`** — the dense audiogram oscilloscope across
   the whole video, driven by `useAudioData(audio.wav)`.
3. **`LyricLayer.tsx`** — karaoke captions centered on the waveform line: the current
   word is brightest, sung words recede, upcoming words sit dim. Uses real per-word
   frames when forced-aligned (`words[]` in `lyrics.json`), else an even stagger.
4. **`<Audio src={audio.wav}>`** — the only sound source (the same track extracted
   from the video), so playback and the waveform stay locked.

`useBeatData.ts` is the single place timing is read. `theme.ts` is the only place the
look lives — palette, type, `waveformMid`/`waveformAmp`, `scrimHeight`/`scrimOpacity`,
`lyricStyle`. Edit the theme to restyle without touching timing.

## Knobs worth knowing

- **Lyric/waveform vertical position** — `theme.waveformMid` (0..1 fraction of
  height). 0.5 = centered over the footage; ~0.78 = lower band. Lyrics follow it.
- **Legibility** — `theme.scrimOpacity` (peak darkness) and `theme.scrimHeight`
  (band thickness). Raise both over bright footage; drop to 0 opacity to remove.
- **Waveform** — `theme.accent` (stroke color), `waveformAmp` (height), `waveformStroke`.
- **Chorus emphasis** — lines tagged chorus/hook render larger in `theme.accent2`.

## Conventions (shared with Songbird)

- One kebab-case folder per video; the source video is copied in as `source.mp4`.
- YouTube titles include **"(Claude Songbird Test)"**; descriptions lead with
  **"this is ONE STEP, not the finished video."**; keep a `youtube.md` per song.
- The skill stops at a runnable project + render commands — rendering is local.
