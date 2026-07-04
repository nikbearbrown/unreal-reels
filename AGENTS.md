# AGENTS.md — operating guide for Unreal Reels

You are driving **Unreal Reels**: a storyboard-first, audio-first pipeline that turns a
script/story/lyrics/topic into a finished short video. This file is the contract. Read it
fully before acting. (Claude Code users: `CLAUDE.md` points here.)

## First principles

1. **The audio is the master clock.** Generate narration/music first, measure its *real*
   duration per beat, and time everything off that. Never estimate from word count.
2. **Storyboard before video.** Lock the still for each beat before animating — video costs
   more and the still is the video's first frame.
3. **Phase-gated, human-curated.** Stop at each gate and let the user pick (the reference,
   the storyboard frame, the clip). Don't batch past a gate unasked.
4. **References, not descriptions, lock identity.** Characters are locked by reference
   *images* (a curated library), not by re-describing them in prompts.
   When a beat has `assets` such as `PNG/foo.png`, those files are **reference inputs to
   FLUX/Higgsfield**, not finished storyboard stills. Do not manufacture
   `stills/story/...` locally by resizing/cropping those PNGs. The `stills/` outputs are
   created by FLUX from the reference image(s) plus the beat's `image_prompt` or
   `image_prompt_a`/`image_prompt_b`; see `docs/flux-storyboard-stills.md`.
5. **One look knob.** The photographic aesthetic is a single swappable preset
   (`presets/`), applied to every beat — don't hand-tune look per shot.
6. **ALWAYS ask before using ANY paid service.** Higgsfield (SoulID, FLUX.2, image-to-video,
   Seedance), ElevenLabs TTS, and fal.ai all cost the user credits — some a lot (Seedance/
   image-to-video is expensive). Never kick off a paid/credit-spending step without the user's
   explicit go-ahead for *that* step. Free/local work (segmenting, authoring prompts, ffmpeg
   assembly, `--dry-run`/`DRY_RUN=1` previews, Manim renders on the user's machine) needs no
   permission; anything that bills an account does. When in doubt, it's paid — ask.

## The single source of truth: `beat_sheet.json`

One file per project (a "reel"), in `reels/<slug>/beat_sheet.json`. Every stage reads it and
writes results back into it. Shape:

```jsonc
{
  "metadata": {
    "slug": "...", "title": "...",
    "voice_id": "<ElevenLabs voice>",
    "aspect_ratio": "16:9",
    "style_preset": "cinematic-netflix",      // -> presets/
    "ref_prefix": "my-film",
    "characters": [
      { "name": "Hero", "ref_key": "hero", "driver": "soul",
        "soul_id": "<higgsfield soul uuid>", "look": "…wardrobe…" },
      { "name": "Beast", "ref_key": "beast", "driver": "reference" }   // image-only, no soul
    ],
    "style_bible": { "visual_style": "...", "color_palette": "...", "lighting_style": "..." }
  },
  "beats": [
    { "beat_id": "B01",
      "narration_text": "…the spoken line…",
      "image_prompt": "…the VISUAL scene, no dialogue, no words…",
      "video_prompt": "…the motion/camera move…",
      "characters_present": ["Hero"],          // which refs appear (<=4)
      "camera": "push_in",
      "actual_duration_s": null,                // filled by audio stage
      "chosen_still": null, "video_file": null  // filled by later stages
    }
  ]
}
```

**Hard rule:** `image_prompt` is a *visual scene* — never the narration, never dialogue, or
the image model renders gibberish caption/speech-bubble text. Identity comes from the
reference library; the prompt carries action + composition only.

## The stages (each is a script in `scripts/`)

| # | Stage | Script | Gate |
|---|---|---|---|
| 1 | Segment | `segment_story.py` story → `beat_sheet.json` (verbatim, ≤~28 words/beat) | review beats |
| 2 | Audio | `generate_audio.py <reel>` ElevenLabs TTS → measures `actual_duration_s` | hear narration |
| 3 | References | `generate_references.sh <reel>` 10 clean SoulID plates per character | **pick the great one** |
| 4 | Storyboard | `generate_storyboard_flux.sh <reel>` FLUX.2 multi-ref, 3/beat from the library | **pick keeper / redo** |
| 5 | Video | image→video per beat, request tier ≥ audio, `ffmpeg -t A` trim to audio | approve clip |
| 6 | Overlay | Remotion: title + captions (from ElevenLabs word timestamps) → final | — |

Stages 5–6 are partially built — see `docs/pipeline.md` for status.

## The reference library

Per reel: `reels/<slug>/references/characters/<ref_key>/` holds 1+ plates per character.
- One plate → locked to it. Several → the runner feeds up to 2 into each FLUX call (stronger
  lock), capped at 4 refs/scene.
- Build plates with stage 3 (SoulID, clean front/¾, even light, plain background, full costume).
- A different **wardrobe state** is its own `ref_key`/folder, selected per beat via
  `characters_present` — that's how you get the right *look* per shot.

## Duration & clip tiers

Beats aim ~5s, hard ceiling ~9–10s (the image-to-video clip tier). Never cut a narration line
mid-sentence to fit; if a line needs >10s, split the beat. Request the smallest video tier that
covers the audio (6s or 10s), then trim the clip down to the measured audio.

## Picking an aspect

Match the request to an aspect in `aspects/`, which sets how you author the beat list + look:
- **Songbird** — music/lyric videos (beat-synced, performance).
- **Bios** — narrated mini-biographies (one figure, B-roll under voice).
- **Explainer** — learning videos (concepts, doodles, figures, steps).
All produce the same `beat_sheet.json` and hand off to the shared engine.

## Services (the user brings keys)

This pipeline calls **Higgsfield** (SoulID, FLUX.2, image-to-video), **ElevenLabs** (TTS),
optionally **fal.ai** (LoRA/style). If a key is missing, tell the user exactly which service
and link `docs/services.md` — never invent a workaround, never commit a key.

**Checking which keys are set (names only, never values).** To see every environment
variable *name* without exposing any secret value, run:

```
env | sed 's/=.*/=/' | sort
```

This prints each variable as `NAME=` (value redacted). Use it to confirm whether e.g.
`ELEVENLABS_API_KEY` / `FAL_KEY` are present. Higgsfield uses no env var — it authenticates
its CLI (`higgsfield auth login`), so it won't show here. Never run a plain `env`, `printenv`,
or `echo $KEY` that would print a secret's value.

## Handing off commands

Whenever you give the user a command to run, make it **copy-paste-ready with
absolute full paths**, in its own code block — never a bare `npm run …` or a
relative path the user has to resolve. Always `cd` into the exact directory first,
e.g.:

```
cd "/Users/<user>/Documents/Cowork/unreal-reels/lectures/<slug>/remotion" && npm run studio
```

One command per block; if there are multiple steps, number them and give each its
own block. (Heavy/credit steps still run on the user's machine — hand off the
command, don't claim you produced the output.)

**Never make the user hand-edit a file.** If a value is missing (a `voice_id`, a
`soul_id`, a slug, a path, a prompt tweak), *ask the user for the value* and then make
the edit yourself — write it into `beat_sheet.json`, the preset, or wherever it belongs.
Do not tell the user to "open the file and set X" or "edit `metadata.voice_id`." Ask for
the info, apply it, confirm what you changed. The user pastes values; the agent edits files.

## What never to do

- Never put narration/dialogue text into an image prompt.
- Never commit `reels/`, reference images, audio, renders, or keys (see `.gitignore`).
- Never claim to have produced the final MP4 if the render/video stage runs locally — hand off
  the command.
- Never skip a gate without the user's say-so.
