# Unreal Reels

**Turn a script, story, song, or topic into a finished short video — agent-driven, storyboard-first.**

Unreal Reels is a pipeline (and a set of agent skills) for making short films, music
videos, mini-biographies, and explainer videos. Everything starts the same way: a
**script + audio**, broken into **beats**, each beat rendered as a **storyboard still**
locked to a reusable **character/reference library**, then animated and assembled. The
audio is the master clock — beat timing comes from the narration or music, never a guess.

It runs through an AI agent (Claude Code, Cursor, or the Claude desktop app) that drives
a small set of scripts against three image/video/audio services.

## The three aspects

One engine, three genre lenses:

| Aspect | Makes | Focus |
|---|---|---|
| **Songbird** | music videos, lyric videos | performance + beat-synced motion graphics |
| **Bios** | mini-biographies | narrated life-stories over B-roll, one figure |
| **Explainer** | learning / explainer videos | concepts, doodles, figures, step-by-step |

They differ in how they author the **beat list and look**; they share the same engine
below it. Each lives in [`aspects/`](aspects/).

## The pipeline (everything starts with a storyboard)

```
script/story/lyrics ─▶ segment into BEATS ─▶ generate AUDIO (measure real durations)
        │                                              │
        ▼                                              ▼  (audio = master clock)
  reference LIBRARY  ──────────────▶  STORYBOARD stills (3/beat, FLUX multi-ref, pick best)
  (SoulID plates + props)                             │
                                                      ▼
                                          per-beat VIDEO (trim to audio)
                                                      ▼
                                      title + captions OVERLAY (Remotion) ─▶ final
```

Phase-gated and audio-first. You curate at each gate (pick the reference, pick the
storyboard frame, approve the clip) so quality is controlled, not hoped for. See
[`docs/pipeline.md`](docs/pipeline.md).

## You need accounts on three services

Unreal Reels **orchestrates** these — it does not include or proxy them. You bring your
own keys (set as environment variables; nothing is stored in this repo):

- **[Higgsfield](https://higgsfield.ai)** — SoulID character references, FLUX.2 multi-reference
  storyboard, image-to-video. ([Cloud API](https://cloud.higgsfield.ai) / CLI)
- **[ElevenLabs](https://elevenlabs.io)** — narration text-to-speech (your voice or a character's).
- **[fal.ai](https://fal.ai)** — optional: FLUX LoRA style training, alternate video models.

Setup + links: [`docs/services.md`](docs/services.md).

Also needed locally: **Python 3**, **Node 18+** (for Remotion assembly), **ffmpeg**, `jq`, `curl`.

## Quick start

```bash
git clone https://github.com/nikbearbrown/unreal-reels.git
cd unreal-reels
git config core.hooksPath .githooks   # enable the >50MB commit guard
# 1. install tools + set up keys — see docs/setup.md
# 2. point your agent at AGENTS.md and say what you want to make
```

Then, in an agent session: *"Make a 60-second explainer of photosynthesis"* or
*"Turn these lyrics into a music video."* The agent reads [`AGENTS.md`](AGENTS.md),
segments the beats, and walks you through the gates.

**New here?** [`docs/getting-started.md`](docs/getting-started.md) walks you through making one
of each — a music video, a mini-bio, and an explainer. Not sure what's free vs. paid?
[`docs/open-source-vs-paid.md`](docs/open-source-vs-paid.md) breaks it down (a lot is free).

Or run the engine directly — each stage is a script in [`scripts/`](scripts/):

```bash
python scripts/segment_story.py story.txt --slug my-film --title "My Film" -o beat_sheet.json
python scripts/generate_audio.py reels/my-film          # ElevenLabs narration + durations
bash   scripts/generate_references.sh reels/my-film      # SoulID reference plates -> you pick
bash   scripts/generate_storyboard_flux.sh reels/my-film # FLUX storyboard from your library
# then: per-beat video (trim to audio) + Remotion overlay
```

## Layout

```
scripts/     THE STORYBOARD ENGINE — segment, audio, references, FLUX storyboard, (video, overlay)
SKILL.md     the engine as an agent skill (the core; the aspects below feed it)
presets/     look presets (cinematic-netflix, phone-grounded, …) — one knob for the whole look
docs/        getting-started · setup · services · open-source-vs-paid · pipeline · references
aspects/     songbird · bios · explainer — each bundles its genre skill(s):
               songbird/  → muzak, muzak-overlay     (music videos)
               bios/      → mini-bio                  (mini-biographies)
               explainer/ → bears-doodles, scout      (learning videos)
skills/      shared/ — cross-cutting skills every aspect uses:
               media-router (which medium per beat) · pacing (how long should it be)
examples/    one tiny starter input per aspect
reels/       YOUR projects — the reproducible DEFINITION is committed (beat_sheet.json,
               source text, discord/ storyboard JPGs, midjourney_prompts.txt); the heavy
               regenerable output (full-res stills, audio, video) stays local (git-ignored)
```

## License

[MIT](LICENSE) © 2026 Nik Bear Brown.
