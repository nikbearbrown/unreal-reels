# Getting started — your first video

Three quick walkthroughs, one per aspect. They all produce a `reels/<slug>/beat_sheet.json` and
run the same gated pipeline; they differ only in how the beats and look are authored. Do
[setup](setup.md) first.

Two ways to drive each:
- **Agent** (easiest): open the repo, point Claude/Cursor at [`AGENTS.md`](../AGENTS.md), and say
  what you want. It segments, runs the stages, and stops at each gate for you.
- **By hand**: run the engine scripts in [`../scripts/`](../scripts/) yourself (shown below).

A ✅ marks a step you can do with **only free / open-source tools** (see
[open-source-vs-paid](open-source-vs-paid.md)).

---

## A) Music video — Songbird

Most free-friendly: a lyric/audiogram video needs **no paid services** (you bring the track).

You provide: a mastered `song.wav` + `lyrics.txt`.

1. ✅ **Analyze the track** — beat/onset grid from the real audio (librosa).
2. ✅ **Align lyrics to the vocal** — word-level timing (faster-whisper), so captions hit on the sung word.
3. ✅ **Render** — Remotion lays karaoke captions + an audiogram waveform over the track → MP4.
4. *(optional, paid or local)* generate a still/clip for a few beats and drop them behind the waveform.

Starter input: [`../examples/songbird-demo/`](../examples/songbird-demo/). The Songbird aspect
([`../aspects/songbird/`](../aspects/songbird/)) carries the analysis + Remotion templates.

---

## B) Mini-bio — Bios

You provide: a figure (name + a few facts, or let the agent research) and a voice.

1. **Write narration beats** — a who → why-they-mattered → legacy arc, each ≤~10s.
2. **Narrate** — `generate_audio.py` (ElevenLabs voice, or a free local TTS) measures real durations. ✅ if local TTS.
3. **One reference plate** for the figure — `generate_references.sh` (Higgsfield SoulID), pick the great one.
4. **Storyboard** — `generate_storyboard_flux.sh`: figure beats reuse the reference; world/legacy beats are no-character scenes.
5. **Video + overlay** → narrated film.

```bash
python scripts/segment_story.py examples/bios-demo/source.txt --slug ada-lovelace --title "Ada Lovelace" -o reels/ada-lovelace/beat_sheet.json
# author image_prompts, set metadata.voice_id + character, then:
python scripts/generate_audio.py reels/ada-lovelace
bash   scripts/generate_references.sh reels/ada-lovelace
bash   scripts/generate_storyboard_flux.sh reels/ada-lovelace
```

Starter input: [`../examples/bios-demo/`](../examples/bios-demo/).

---

## C) Explainer

You provide: a concept or topic.

1. **Outline beats** — hook → mechanism (in steps) → synthesis, one idea per beat.
2. **Narrate** — TTS measures durations. ✅ if local TTS.
3. **Figures** — ✅ drawn as clean **SVG/diagrams** (code, label-free), *or* generated photoreal visuals (paid/local).
4. **Overlay** — labels, arrows, equations added as crisp Remotion overlays **on top** (never baked into an image — models render text as gibberish).

```bash
python scripts/segment_story.py examples/explainer-demo/source.txt --slug photosynthesis --title "Photosynthesis" -o reels/photosynthesis/beat_sheet.json
python scripts/generate_audio.py reels/photosynthesis
# figures: SVG (free) or generate_storyboard_flux.sh (paid/local), then overlay
```

Starter input: [`../examples/explainer-demo/`](../examples/explainer-demo/). The Explainer aspect
([`../aspects/explainer/`](../aspects/explainer/)) carries figure intelligence + the doodle look.

---

## The rule that applies to all three

`image_prompt` is a **visual scene only** — never the narration or dialogue, or the image model
bakes in gibberish caption text. Identity comes from the reference library; the prompt carries
action + composition. The audio is the master clock; clips are trimmed to the measured narration.
