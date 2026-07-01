---
name: lyric-match
description: >
  Re-cut an EXISTING music video whose visuals are great but drift from the words —
  into a beat-synced reel where every beat's clip is generated image-to-video from the
  matching source frame and made to fit its lyric line. One beat = one lyric line = one
  source still = one Minimax Hailuo clip, generated at 10s and cut to the beat. Use when
  the user types `lyric-match`, `lyric match`, `rematch`, `match the lyrics`, or asks to
  sync an existing video to its lyrics, re-time a video to the vocal, turn extracted video
  frames into a lyric-matched reel, or "make the visuals land on the words." Audio-first
  and phase-gated: librosa beat grid is the master clock; faster-whisper forced alignment
  gives word-level lyric timing (beat-grid seed is the fallback); frames are scored for
  sharpness and one is chosen per beat; each beat's prompt is written by LOOKING at both
  the chosen frame and its lyric; then Hailuo image->video, cut to beat, captions, mux.
---

# Lyric Match — re-sync an existing video to its own words

You are handed a finished music video that already has beautiful imagery — a performance
cut, an AI montage, archival footage — but the pictures don't land on the lyrics. Your
job is to **keep the good visuals and make them obey the words**: rebuild the piece as a
beat-synced reel where each lyric line gets the source frame that best fits it, animated
into a short clip that resolves on the beat.

This is a sibling of `unreal-reels`. The difference in one line: unreal-reels **generates**
every still from scratch; lyric-match **starts from an existing video's frames** and only
regrades/animates them. Same plumbing, same `beat_sheet.json`, same Hailuo cut-to-beat.

## The one rule (unchanged)

**The audio is the master clock.** Beat timing comes from the real waveform (librosa),
never a word-count guess. Lyric timing comes from forced alignment to the vocal when you
can run it. Every clip length is derived from that timing; beats tile the whole song with
no gaps.

## Inputs you need in the reel folder

- the **source video** (`*.mp4`) — the visuals you're re-matching
- the **mastered audio** (`*.wav`/`*.mp3`) — the master clock
- the **lyrics** (`song-*.txt`, one line per sung line, blank line between stanzas,
  optional `TITLE:` line)

If you only have the video, extract the audio from it first (`ffmpeg -i in.mp4 -vn audio.wav`).

## Phase-gated pipeline (regenerate only the failing unit at each gate)

**Phase 1 — Audio analysis (master clock).** Run `analyze_audio.py` on the WAV →
`beat_data.json` (bpm, key, sections, `durationInFrames`, beat grid). Never hand-edit it.
→ `aspects/songbird/muzak/scripts/analyze_audio.py`

**Phase 2 — Lyric timing.** Word-level timing for every line.
- **Preferred:** `align_lyrics_audio.py` — faster-whisper transcribes the vocal with word
  timestamps, then the KNOWN lyrics are sequence-aligned onto those timestamps. Run this
  **locally** where the Whisper model can download; bump `--model small/medium` for sung
  vocals, leave `--vad` OFF so sung intros aren't clipped.
- **Fallback:** `align_lyrics.py` — a beat-grid SEED that spreads lines evenly across the
  real beat grid. Use only when Whisper can't run (e.g. the model host is blocked in a
  sandbox). Mark `timing_source` as a seed and nudge anchors at the overlay gate.
→ both in `aspects/songbird/muzak/scripts/`
**GATE 0 — lock the audio + lyric timing before touching frames.**

**Phase 3 — Frames → one still per beat.**
1. `scripts/extract_frames.sh <video> <out_dir> [FPS]` — pull frames at ~1 fps (a frame's
   index then ≈ its second in the song) into the reel folder.
2. `scripts/pick_stills.py <reel_folder>` — for each beat, take the frames whose timestamp
   falls in that beat's window and keep the **sharpest** (variance of the Laplacian); write
   `source_still` / `source_frame_number` / `source_frame_sharpness` back into the beat sheet
   and copy the keeper to `stills/<beat_id>_v1.png`.

   Frames stay in temporal order, so beat *k*'s still comes from beat *k*'s moment. If the
   source holds one shot across several beats you'll get near-twin stills — that's honest;
   widen the search or pull the second-sharpest frame only if you want visual variety.
**GATE 1 — eyeball `stills/`; swap any weak keeper for another frame in that window.**

**Phase 4 — Match each still to its lyric (the heart of this skill).**
For every beat, **open the chosen still and read its lyric line**, then write:
- `image_prompt` — image-to-image from `source_still`, *preserving its subject, pose and
  composition*, pushing expression + light toward what the lyric means. Never put the lyric
  TEXT in the prompt; describe the picture.
- `video_prompt` — the same scene + one camera move, told to land its key moment early and
  hold so it cuts cleanly to the beat.
- `subject` — correct it to what the frame actually shows (don't trust an earlier guess).

This is a vision step, not a script: the whole point is that a human-or-model eye looked at
**both** the picture and the words and decided they belong together.

**Phase 5 — Video (Hailuo, cut to beat).** `generate_video_songbird.sh <reel_folder>` —
per beat: `minimax_hailuo --image <chosen_still> --prompt <video_prompt>`, **request 10s**
(`EXTRA_ARGS="--duration 10"`; use `--duration 6` only when the beat ≤ 6s), then ffmpeg
**center-trims** the raw clip to the exact beat duration. Don't generate video until the
still is approved — video costs more than stills.
→ `scripts/generate_video_songbird.sh`
**GATE 2 — approve a clip before assembling.**

**Phase 6 — Assemble.** `FINAL=1 generate_video_songbird.sh <reel_folder>` concatenates the
cut clips in beat order and muxes the original WAV (the master audio). Add the title +
lyric captions in the muzak Remotion overlay, timed from the Phase-2 word timestamps.

## Reuse map (build nothing that exists)

| Need | Reuse |
|---|---|
| Beat grid + key + sections + duration | `aspects/songbird/muzak/scripts/analyze_audio.py` |
| Word-level lyric timing (preferred) | `aspects/songbird/muzak/scripts/align_lyrics_audio.py` (faster-whisper) |
| Lyric timing fallback (no Whisper) | `aspects/songbird/muzak/scripts/align_lyrics.py` (beat-grid seed) |
| Frame extraction | `scripts/extract_frames.sh` (this skill) |
| Sharpest still per beat | `scripts/pick_stills.py` (this skill) |
| Image->video, cut to beat, concat+mux | `scripts/generate_video_songbird.sh` |
| Title + captions overlay | `aspects/songbird/muzak-overlay` (Remotion) |

## beat_sheet.json — the per-beat fields lyric-match owns

Same schema as `reels/mon-homme/beat_sheet.json`, plus:

```jsonc
{
  "beat_id": "B07",
  "start_frame": 940, "end_frame": 1101, "duration_s": 5.37,   // from the master clock
  "lyric_text": "Sing a song full of the faith the dark past taught",
  "subject": "archive",                                         // what the frame shows
  "source_still": ".../frame_000036.png",                       // sharpest in this window
  "source_frame_number": 36, "source_frame_sharpness": 1316.0,
  "chosen_still": "stills/B07_v1.png",                          // the keeper (Hailuo --image)
  "prompt_mode": "image-to-image",
  "image_prompt": "Image-to-image from the source frame ... preserving subject/pose: <scene>. <lyric direction>.",
  "video_prompt": "<scene>. <camera>; subtle motion; land the key moment early; duration 5.37s.",
  "clip_tier": 6                                                // 6 if beat<=6s else 10
}
```

## The faster-whisper caveat (read this)

Word-level lyric timing wants `faster-whisper`, which downloads its model from Hugging
Face on first run. **Run Phase 2 locally** where that download works. In a locked-down
sandbox the host can be blocked (HTTP 403) and the model can't load — then you fall back to
`align_lyrics.py`'s beat-grid seed, which still rides the real beat grid but spaces lines
evenly rather than to the actual vocal. Always record which one you used in
`metadata.timing_source`, and re-run the Whisper pass + nudge anchors before the final
render whenever you can.

## Gates, in one line

`audio+lyric-lock → still-pick → still↔lyric match → clip-approve → assemble` — and at every
gate you regenerate only the unit that failed, never the whole batch.
