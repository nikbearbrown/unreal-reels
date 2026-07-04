# Session state — music-video tutorial reel

_Pick-up notes for continuing in a fresh session._

## What this is
Repo: `/Users/nik/Documents/Cowork/unreal-reels` (Unreal Reels — storyboard-first, audio-first
short-video pipeline). We built a self-contained **build-it-yourself music-video tutorial** at
`reels/music-video/`, derived from the existing `reels/who-s-gonna-bell-that-cat` reel, so a
learner needs no WAV/lyrics/art of their own.

Song: *"Who's Gonna Bell That Cat"* — 28 beats, ~162 s, 16:9, ink-and-gouache storybook.

## What's done
- `reels/music-video/` scaffolded: `song.wav`, `lyrics.txt`, `beat_sheet.json` (28 beats, 16:9),
  `beat_data.json`, `lyrics.json`.
- PNG → **JPG** conversion (the requested size win): `plates/` (28 refs) + `slides/` (53 storyboard
  stills), 421 MB → 36 MB. `beat_sheet.json` asset paths rewritten to `plates/*.jpg`.
- 28 pre-generated clips copied to `video-16x9/raw/B01…B28.mp4` (for the keyless Phase-1 build).
- `midjourney_prompts.txt` + `midjourney_motion.txt` — one line per beat, **each starting with its
  beat id** so Midjourney downloads rename straight back to `B01.mp4`.
- `README.md` — numbered tutorial (Phase 1 assemble-only, Phase 2 regenerate in Midjourney).
- `WALKTHROUGH.md` + `narration.txt` — script for an optional narrated walkthrough video (not rendered).

## Engine fixes made this session (in `scripts/`)
1. **Renamed** `generate_video_seedance.sh` → **`generate_video.sh`** (all refs updated: `build_videos.sh`,
   README, shotlists). "Seedance" is just Higgsfield's image→video model; the name was misleading for
   the assemble path.
2. `ASSEMBLE_ONLY=1` no longer requires Higgsfield auth — so the assemble path is truly key-less.
3. **Concat bug fixed**: the concat list now writes **absolute** clip paths (ffmpeg's concat demuxer
   resolves paths relative to the list file, not CWD — relative paths were doubling and failing).
4. Data fix: `video-16x9/raw/B03.mp4` had been truncated during copy; re-copied, verified it decodes.

## The build command (Phase 1, no keys)
```bash
cd "/Users/nik/Documents/Cowork/unreal-reels" && ASSEMBLE_ONLY=1 FINAL=1 TAG=16x9 ASPECT=16:9 W=1920 H=1080 bash scripts/generate_video.sh reels/music-video
```
Output: `reels/music-video/music-video.16x9.mp4` (+ `.silent.mp4`).

## Where we left off / open items
- Last run reached the `=== concat + master audio ===` step. That step re-encodes the full ~162 s
  1080p timeline (~30–90 s) — **verify `music-video.16x9.mp4` was produced and plays.** If concat
  errored, confirm you're running the fixed `generate_video.sh` (absolute paths in `_concat.txt`).
- **Optional narrated walkthrough video** — not built. Needs an ElevenLabs voice id (I bake it into
  the TTS command), then assemble a montage timed to the VO. Or ask for a captioned, no-voice version
  (no keys). See `WALKTHROUGH.md`.
- **Not committed.** `reels/` heavy output is git-ignored; the reel's definition (beats, prompts,
  JPG slides, README) is committable. Decide whether to commit/push the engine fixes + this reel.
- Earlier this session: added an env-var key-check command to `AGENTS.md` and a keys section to
  `docs/getting-started.md` — also **uncommitted**.

## Handy paths
- Reel: `/Users/nik/Documents/Cowork/unreal-reels/reels/music-video`
- Engine: `/Users/nik/Documents/Cowork/unreal-reels/scripts/generate_video.sh`
- Source reel it came from: `reels/who-s-gonna-bell-that-cat`
