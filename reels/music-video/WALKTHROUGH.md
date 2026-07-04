# music-video — narrated walkthrough (script + build)

A ~75-second voice-over that teaches the reel while showing it. The narration is written; the
voice + render run on **your** machine (they need your ElevenLabs key and are heavy), so this
file hands you the exact commands. The pure VO text is in `narration.txt`.

## The script (7 scenes)

| # | On screen | Narration |
|---|---|---|
| 1 | `music-video.16x9.mp4` playing (title card) | This is a music video — twenty-eight beats, under three minutes, built entirely inside Unreal Reels. Here's how to build this exact one, then make it your own. |
| 2 | the folder / file tree | Everything's already here: the song, the lyrics, the beat sheet, the artwork, and twenty-eight ready-made clips. You don't need an account or a key to start. |
| 3 | the Phase-1 command + the final playing | Phase one is assembly. One command cuts every clip to its beat, stitches them in order, and lays the song on top. Out comes a finished sixteen-by-nine video. |
| 4 | `midjourney_prompts.txt` scrolling | Phase two — make it yours. Open the prompt list. Every line starts with its beat number, so when Midjourney saves the clip, it's already named for the beat. |
| 5 | plates + a slide side by side | Drag in the reference plates so the mice and the cat stay the same characters across every shot. Pick a frame, animate it, download the clip. |
| 6 | the rename command + reassemble | Rename each clip to its beat number, drop it in, and run the same assemble command. Your shots replace the originals — and the timing stays locked to the song. |
| 7 | final montage / logo | That's the whole idea: the audio is the clock, the references lock the look, and you curate every step. Now go bell that cat. |

## Build it — 3 handoff steps

**1. Generate the voice-over** (uses your ElevenLabs key). Tell me which ElevenLabs voice to use
and I'll bake its id into this command for you — you shouldn't have to edit it. The shape:

```bash
cd "/Users/nik/Documents/Cowork/unreal-reels/reels/music-video" && curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/<voice-id-I-will-fill-in>" -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "$(python3 -c 'import json;print(json.dumps({"text":open("narration.txt").read(),"model_id":"eleven_multilingual_v2"}))')" --output walkthrough.mp3
```

**2. Tell me it's done.** Once `walkthrough.mp3` exists, I'll assemble the montage — timing each
of the 7 scenes to the voice-over, dropping in the slides, the prompt-list screen, and the final
clip — and hand you back the render command. (Doing the montage now, before the VO exists, would
just be guessing at scene lengths.)

**3. Render + review** the walkthrough MP4 with the command I hand back.

> Prefer a captioned, no-voice version instead? Say so — that one I can build with no keys at all,
> straight from `slides/` + `song.wav`.
