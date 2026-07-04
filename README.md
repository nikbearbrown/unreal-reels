# Unreal Reels

**Turn a script, story, song, or textbook chapter into a finished short video — agent-driven, audio-first.**

Unreal Reels is a video engine (and a set of agent skills) for making short films, music
videos, mini-biographies, explainer videos, and narrated lecture videos. Two laws govern
everything in this repo:

1. **Audio is the master clock.** Narration or music is generated and *measured* first;
   every downstream duration — clip length, slide hold, caption timing — is derived from
   real audio, never estimated from word count.
2. **Phase-gated.** You approve at the cheapest decision point (the plan, the script, the
   storyboard keeper, the Studio preview), and only the failing unit is ever regenerated.
   Rendering is always human-approved — nothing auto-renders.

The spine is **`beat_sheet.json`**: one beat = one narrated/sung unit = one visual. Every
pipeline emits it, reads it, or writes back to it, which is why the parts compose.

It runs through an AI agent (Claude Code, Cursor, or the Claude desktop app) that drives
a small set of scripts against a few image/video/audio services.

## Two production families

```
REELS — storyboard-first                     LECTURES — deck-first
story/lyrics → beats → audio →               chapter.md → asset pool → slide deck →
references → stills → video → overlay        narrated lecture video (Remotion)
```

### Reels: the three aspects

One engine, three genre lenses (each in [`aspects/`](aspects/)):

| Aspect | Makes | Focus |
|---|---|---|
| **Songbird** | music videos, lyric videos | performance + beat-synced motion graphics |
| **Bios** | mini-biographies | narrated life-stories over B-roll, one figure |
| **Explainer** | learning / explainer videos | concepts, doodles, figures, step-by-step |

Plus two production skills in [`skills/`](skills/):

- **`lyric-match`** — re-cut an existing music video so every beat's clip matches its
  lyric line (frame extraction → forced-aligned lyrics → image-to-video per beat).
- **`songbird-dance`** — a character dancing ON the beat (Seedance 2.0: image + audio
  slice → motion locked to that audio; long ~10–15s downbeat-aligned beats).

### Lectures: chapter in, narrated video out

Three skills, run in order (see [`skills/PIPELINE.md`](skills/PIPELINE.md)):

```
chapter.md
   ▼  STAGE 1 · lecture-assets   build a POOL of candidate visuals (over-generate; force nothing)
   ▼  STAGE 2 · slide-deck       select from the pool → a brutalist .dc.html deck (human gate on the plan)
   ▼  STAGE 3 · deck-lecture     deck → narrated video: voice-clone audio per slide, karaoke
   ▼                             captions, progressive figures / doodles / bullets (no static
lecture.mp4                      screen >~5s), preview in Remotion Studio, then YOU render
```

The narration **discusses** each slide, it doesn't read it — every beat expands the
slide's `data-speaker-notes` into spoken teaching voice, with an overlap guard that flags
scripts that recite. The visual language lives in [`brutalist/`](brutalist/) (one red
`#C8102E`, warm ink, grays, no blue).

## The reels pipeline (everything starts with a storyboard)

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

See [`docs/pipeline.md`](docs/pipeline.md).

## You need accounts on three services

Unreal Reels **orchestrates** these — it does not include or proxy them. You bring your
own keys (set as environment variables; nothing is stored in this repo):

- **[Higgsfield](https://higgsfield.ai)** — SoulID character references, FLUX.2 multi-reference
  storyboard, image-to-video (Seedance, Hailuo). ([Cloud API](https://cloud.higgsfield.ai) / CLI)
- **[ElevenLabs](https://elevenlabs.io)** — narration text-to-speech (your voice or a character's).
- **[fal.ai](https://fal.ai)** — optional: FLUX LoRA style training, alternate video models.

Setup + links: [`docs/services.md`](docs/services.md).

Also needed locally: **Python 3**, **Node 18+** (for Remotion assembly), **ffmpeg**, `jq`, `curl`.
For lecture captions / lyric timing: `faster-whisper`; for beat analysis: `librosa`.

## Quick start

```bash
git clone https://github.com/nikbearbrown/unreal-reels.git
cd unreal-reels
git config core.hooksPath .githooks   # enable the >50MB commit guard
# 1. install tools + set up keys — see docs/setup.md
# 2. point your agent at AGENTS.md and say what you want to make
```

**Just opened the folder in an agent (Cowork / Claude Code / Cursor)?** Paste this first so it
orients itself before you ask for anything:

```text
This is the Unreal Reels repo — a storyboard-first, audio-first pipeline for turning a
script, song, or textbook chapter into a short video. Get oriented before we start:

1. Read AGENTS.md and README.md to learn the operating contract and the beat_sheet.json schema.
2. Skim scripts/ (the engine), aspects/ (songbird / bios / explainer), skills/ (lyric-match,
   songbird-dance, and the lecture pipeline: lecture-assets → slide-deck → deck-lecture),
   and docs/getting-started.md.
3. Check which service keys are set in my environment (HIGGSFIELD, ELEVENLABS, FAL) without
   printing their values — just tell me which are present and which are missing.
4. List any existing projects in reels/ and lectures/ and tell me their status.

Then summarize, in a few sentences, what this repo does and the phase-gated pipeline. Finally,
ask me what I want to make — a music video (Songbird), a mini-bio (Bios), an explainer, a
dance reel, a lyric re-cut, or a narrated lecture from a chapter — and what about.
Don't run any generation yet; wait for me to choose.
```

It reads itself in, reports which paid services you're set up for, and stops to ask what you
want. Then just say it: *"Make a 60-second explainer of photosynthesis"*, *"Turn these lyrics
into a music video"*, or *"Turn chapter 3 into a lecture video."*

**New here?** [`docs/getting-started.md`](docs/getting-started.md) walks you through making
one of each. Not sure what's free vs. paid?
[`docs/open-source-vs-paid.md`](docs/open-source-vs-paid.md) breaks it down (a lot is free).

Or run the engine directly — each stage is a script in [`scripts/`](scripts/):

```bash
python scripts/segment_story.py story.txt --slug my-film --title "My Film" -o beat_sheet.json
python scripts/generate_audio.py reels/my-film          # ElevenLabs narration + durations
bash   scripts/generate_references.sh reels/my-film      # SoulID reference plates -> you pick
bash   scripts/generate_storyboard_flux.sh reels/my-film # FLUX storyboard from your library
bash   scripts/generate_video.sh reels/my-film           # per-beat video (trim to audio)
bash   scripts/recreate.sh reels/bio-bose                # rebuild a reel from its committed definition
```

## Layout

```
scripts/     THE STORYBOARD ENGINE — segment, audio, references, FLUX storyboard, video,
             duets, Midjourney round-trip, reconcile/recreate
SKILL.md     the engine as an agent skill (the core; the aspects below feed it)
presets/     look presets (cinematic-netflix, phone-grounded, …) — one knob for the whole look
brutalist/   the lecture/deck design system (DESIGN.md, EQUATIONS.md)
docs/        getting-started · setup · services · open-source-vs-paid · pipeline · references
             · SYSTEM-REVIEW (full skill + function inventory and critique)
aspects/     songbird · bios · explainer — each bundles its genre skill(s):
               songbird/  → muzak, muzak-overlay     (music videos)
               bios/      → mini-bio                  (mini-biographies)
               explainer/ → bears-doodles, scout      (learning videos)
skills/      production + pipeline skills:
               lecture-assets → slide-deck → deck-lecture   (chapter → narrated lecture video)
               lyric-match · songbird-dance                 (music-video production modes)
               shared/ — media-router (which medium per beat) · pacing (how long should it be)
               PIPELINE.md — the lecture pipeline overview
examples/    one tiny starter input per aspect
reels/       YOUR reel projects — the reproducible DEFINITION is committed (beat_sheet.json,
               source text, discord/ storyboard JPGs, midjourney_prompts.txt); the heavy
               regenerable output (full-res stills, audio, video) stays local (git-ignored)
lectures/    YOUR lecture projects — deck + beat sheet + captions committed; audio/renders local
```

## License

[MIT](LICENSE) © 2026 Nik Bear Brown.
