# The pipeline

Storyboard-first, audio-first, phase-gated. One `beat_sheet.json` per reel threads every stage.

## Stages

### 1 — Segment  (`scripts/segment_story.py`) ✅
Script/story → `beat_sheet.json`. Splits the text into beats (verbatim, ≤~28 words each, never
mid-sentence) so each beat fits one video clip. Infers `characters_present` heuristically — eyeball
it. Leaves `image_prompt` empty (authored next); fills `narration_text`.
```bash
python scripts/segment_story.py story.txt --meta-from ../other/beat_sheet.json \
  --slug my-film --title "My Film" --max-words 28 -o reels/my-film/beat_sheet.json
```

### 2 — Audio  (`scripts/generate_audio.py`) ✅
ElevenLabs TTS per beat → `mp3/beat-<id>.mp3`, measures the **real** duration with mutagen, writes
`actual_duration_s` back. This is ground-truth timing for everything downstream.
```bash
python scripts/generate_audio.py reels/my-film         # --dry-run to plan
```
**Gate:** listen. Regenerate a single beat with `--only B07`.

### 3 — References  (`scripts/generate_references.sh`) ✅
For each SoulID character, 10 clean reference plates (front/¾, even light, plain background, full
costume) → `references/candidates/`. **You curate** (delete the bad, keep the great) and move
keepers into `references/characters/<ref_key>/`.
```bash
bash scripts/generate_references.sh reels/my-film       # COUNT=10
```
**Gate:** pick the great plate per character. A different wardrobe state = its own `ref_key` folder.

### 4 — Storyboard  (`scripts/generate_storyboard_flux.sh`) ✅
FLUX.2 multi-reference: for each beat, attach the reference(s) of the characters present (up to 4)
+ the look preset + the `image_prompt`, generate N variations, auto-download to `stills/`.
```bash
VARIATIONS=2 bash scripts/generate_storyboard_flux.sh reels/my-film
```
**Gate:** pick the keeper per beat (set `chosen_still`); redo rejects with a better prompt/ref.

### 5 — Video  (to finish) 🚧
Per beat: image-to-video from the chosen still + `video_prompt`. Request the smallest tier that
covers the audio (6s or 10s), then `ffmpeg -t <actual_duration_s>` trims the clip to the line.
Compose stills so the key action lands early (the tail gets trimmed). Auto-download to the reel.
**Gate:** approve each clip.

### 6 — Overlay  (to finish) 🚧
Remotion: lay the **title + narration captions** over the approved clips, timed from ElevenLabs
word timestamps (no forced alignment needed), mux the narration as the master track. The
`muzak-overlay` aspect has the Remotion caption layer to adapt.

## Why audio-first

Beat length = its complete spoken line, measured, never estimated. The video is requested one
tier longer and trimmed down to the audio — so a clip always covers its narration and you never
freeze a held frame or cut a line. Aim ~5s/beat, ceiling ~9–10s; split anything longer.

## Why references over prompts

FLUX clones identity *and* wardrobe from the reference image, and keeps multiple references as
**distinct** subjects (a person and an animal don't blend into a werewolf — which two SoulIDs in
one frame do). So the prompt's job shrinks to action + composition; the library carries who.
```

Status: stages 1–4 are built and working; 5–6 are partially built (video trim-to-audio is a thin
wrapper over the image-to-video call; overlay adapts the Songbird/muzak Remotion layer).
