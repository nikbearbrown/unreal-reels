# CLAUDE.md

This project's agent contract lives in **[AGENTS.md](AGENTS.md)** — read it first and follow
it. Everything below is Claude-/Claude-Code-specific.

## Working style here

- **Audio-first, storyboard-first, phase-gated.** Generate and *measure* the narration before
  any visuals; lock the storyboard still before the video; stop at each gate for the user to
  pick. See AGENTS.md → "First principles."
- **`reels/<slug>/beat_sheet.json` is the single source of truth.** Read it, write results back
  into it. Don't invent parallel state.
- **`image_prompt` is a visual scene only** — never the narration or dialogue (that renders as
  on-image gibberish text). Identity comes from the reference library, not the prompt.

## Running things

- The engine is plain scripts in `scripts/` (Python + bash). Run them; don't reimplement.
- `scripts/*.sh` are written **Bash 3.2-safe** (macOS default shell) — no `mapfile`, guard
  empty arrays. Keep them that way.
- The image/video/audio calls go to **Higgsfield / ElevenLabs / fal.ai** over the network and
  cost credits. These run on the user's machine with their keys — you (in a sandbox) generally
  **cannot** run them. Build/validate the command, then hand it to the user to execute.
- Heavy steps (Remotion render, video generation) are local and slow — hand off the command,
  don't claim you produced the output.

## Secrets & private content

- Never read, print, or commit API keys (`FAL_KEY`, `ELEVENLABS_API_KEY`, Higgsfield auth).
- Never commit `reels/`, reference images, audio, or renders — they're git-ignored. The repo
  ships the **engine + skills + docs**, not anyone's content.

## When a service is needed

If the user lacks Higgsfield / ElevenLabs / fal.ai, say which one and point at
[`docs/services.md`](docs/services.md). Don't fabricate a local fallback for a hosted model.

## Verify before declaring done

Dry-run scripts, `bash -n` the shell, validate `beat_sheet.json` with `jq`, and confirm a
sample assembled prompt is clean (no narration, look preset applied) before telling the user to
spend credits on a batch.
