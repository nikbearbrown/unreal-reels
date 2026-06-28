# Services & setup

Unreal Reels **orchestrates** hosted AI services — it does not include, proxy, or store any
of them. You bring your own accounts and keys. Nothing here is in the repo; everything is read
from environment variables on your machine.

## Required

### Higgsfield — images & video
The core image/video engine: **SoulID** (trained character references), **FLUX.2**
(multi-reference storyboard — multiple locked subjects + a text prompt), and image-to-video.

- Sign up: <https://higgsfield.ai>
- API / CLI: <https://cloud.higgsfield.ai>
- Auth the CLI once: `higgsfield auth login`
- Check models: `higgsfield model list` · params for one: `higgsfield model get flux_2`

Used by `generate_references.sh` (SoulID plates) and `generate_storyboard_flux.sh` (FLUX.2).

### ElevenLabs — narration (text-to-speech)
Generates the spoken track that drives all timing. Use your own cloned voice or a per-character
voice (dialogue mode).

- Sign up: <https://elevenlabs.io>
- Create / clone a voice, copy its **voice id** into `beat_sheet.json` → `metadata.voice_id`.
- Set the key: `export ELEVENLABS_API_KEY="..."`
- `pip install requests mutagen`

Used by `generate_audio.py`.

## Optional

### fal.ai — style LoRA training & alternate models
Only if you want to train a custom **style LoRA** (e.g. a doodle/sketch look) or use alternate
video models.

- Sign up: <https://fal.ai>
- `pip install fal-client` · `export FAL_KEY="..."`

## Local tools

- **Python 3** — segmentation, audio.
- **Node 18+** — Remotion assembly (captions/title overlay).
- **ffmpeg** — audio extraction, clip trimming.
- **jq**, **curl** — the shell runners.

```bash
# macOS
brew install ffmpeg jq node
pip install requests mutagen
```

## Keys: where they go (and don't)

| Service | Env var | Notes |
|---|---|---|
| Higgsfield | (CLI login / cloud key) | `higgsfield auth login`; key never in repo |
| ElevenLabs | `ELEVENLABS_API_KEY` | or pass `--api-key` |
| fal.ai | `FAL_KEY` | optional |

Put them in your shell profile (`~/.zshrc`) or a local `.env` (which is git-ignored). **Never**
commit a key, and the agent will never print one.

## Costs (rough, you control them)

Images and video cost credits; narration is cheap. The pipeline is **phase-gated** precisely so
you spend deliberately: you approve the reference, then the storyboard, then the video — nothing
batches past a gate without you.
