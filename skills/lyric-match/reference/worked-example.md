# Worked example — "Lift Every Voice and Sing" (Mayfield King)

The reel that this skill was extracted from. End-to-end, in the reel folder
`reels/lift-every-voice-and-sing/` (paths relative to the unreal-reels repo root;
`$M = aspects/songbird/muzak/scripts`).

```bash
cd reels/lift-every-voice-and-sing

# Phase 1 — master clock
python3 $M/analyze_audio.py "LifteveryvoiceandsingMayfieldGDMusinique-mastered.wav" \
    --fps 30 -o beat_data.json
#   -> 169.7s, 92.3 bpm, G# minor, 8 sections, beat grid

# Phase 2 — lyric timing
#   PREFERRED (run locally, Whisper model can download):
python3 $M/align_lyrics_audio.py song-06.txt \
    --audio "Lifteveryvoice...-mastered.wav" --beat-data beat_data.json \
    -o lyrics.json --model small
#   FALLBACK (sandbox blocked Hugging Face -> used this here):
python3 $M/align_lyrics.py song-06.txt --beat-data beat_data.json -o lyrics.json
#   -> 32 lines, ~1.5 w/s, timing_source = beat-grid seed

# init the beat sheet (one beat per line, contiguous tiling)
python3 ../../skills/lyric-match/scripts/init_beat_sheet.py . \
    --audio "Lifteveryvoice...-mastered.wav" --lyrics song-06.txt \
    --title "Lift Every Voice and Sing" --artist "Mayfield King" \
    --source-video "Lift Every Voice and Sing _ Mayfield King.mp4"

# Phase 3 — frames -> one sharp still per beat
#   (frames were already extracted at 1 fps; otherwise:)
# ../../skills/lyric-match/scripts/extract_frames.sh "...King.mp4" . 1
python3 ../../skills/lyric-match/scripts/pick_stills.py . --fps 1
#   -> 147 frames, 32 unique keepers copied to stills/B01_v1.png ... B32_v1.png

# Phase 4 — match each still to its lyric (VISION step, not a script):
#   open each stills/BNN_v1.png, read beats[N].lyric_text, and write
#   beats[N].image_prompt + video_prompt + corrected subject.

# Phase 5 — video, cut to beat (run where higgsfield is authenticated)
EXTRA_ARGS="--duration 10" ../../skills/lyric-match/scripts/generate_video_songbird.sh .
#   -> video/raw/BNN.mp4 (10s Hailuo)  +  video/BNN.mp4 (center-cut to beat)

# Phase 6 — assemble: concat in beat order + mux the original WAV
FINAL=1 EXTRA_ARGS="--duration 10" \
    ../../skills/lyric-match/scripts/generate_video_songbird.sh .
```

## What the source frames turned out to be

The selection reproduced the video's own structure: the colour **singer** (studio,
vintage mic, blue shirt) bookends and punctuates the song (6 beats), while a gallery
of high-contrast **black-and-white / sepia portraits** carries the dark-past / stony-road
/ weary-years lines (26 beats) — Frederick Douglass- and Sojourner Truth-style elders,
a civil-rights rally singer, the Johnson-brothers-era top-hat piano duo, a photographer,
a boxer, period music rooms. Because the source holds some shots across several beats,
a few keepers are near-twins (B20/B21, B23/B24, B26/B27, B28/B29) — expected when
re-matching an existing cut.

## Lessons baked into the skill

- **Run faster-whisper locally.** The seed fallback works and rides the real beat grid,
  but it spaces lines evenly; word-level timing makes the captions and cuts land on the
  actual vocal. Re-run + nudge before the final render.
- **A frame's index = its second** only if you extract at 1 fps (or pass the real `--fps`).
- **Look at the picture AND the words.** The subject tags from a first guess were wrong on
  8 of 32 beats; only opening each still fixed them.
- **Hailuo at 10s, center-cut to the beat.** Request 10s, let ffmpeg shave both ends so the
  strongest motion sits mid-clip on the beat.
