---
name: unreal-reels
description: >
  Turn a short story (or lyric, or scene list) into a narrated AI film — one beat =
  one scene = one narrated line over one generated video clip, assembled with a title
  and captions. Audio-first and phase-gated: narration is generated and measured FIRST
  and becomes the master clock; then storyboard stills (pick the keeper), then video,
  then the title/caption overlay. Two style presets share one pipeline: phone-grounded
  found-footage reels, and polished cinematic pieces. Reuses the existing mini-bio /
  bears-doodles audio, muzak storyboard + Remotion, and Higgsfield Soul/video tooling.
metadata:
  tags: story-to-film, ai-video, elevenlabs, higgsfield, minimax-hailuo, remotion, phase-gated, songbird
---

# Unreal Reels — story → narrated AI film

Part of **Songbird**. The engine that turns a narrative into a beat-synced film where
**one beat = one scene = one narrated line over one generated clip.**

## The one rule

**The narration is the master clock.** Audio is generated and *measured* first; every
beat's length is its real spoken duration (never a word-count estimate). Everything
downstream — clip length, cuts, caption timing — is derived from that audio.

## Phase-gated pipeline (regenerate only the failing unit at each gate)

**Phase 1 — Narration (audio-first).** Generate the ElevenLabs TTS for every beat (Bear's
voice `TyW6NH39JcFb5M3xdIIk` by default; per-beat `voice_id` for dialogue). Measure each
clip's real duration → that is the beat's length. TTS almost never fails; if one does,
regenerate only that beat. **Also capture ElevenLabs word-level timestamps** here — they
give Phase 5 perfect caption timing for free (no whisper alignment needed).
→ reuses `bears-doodles/scripts/generate_audio.py` (already writes `actual_duration_s`).

**Phase 2 — Beats / scenes.** The narration + measured durations *are* the beats. Each beat
carries: `narration_text`, `scene_description`, `characters_present` (Soul ID or reference
image), `dominant_action`, `camera` (one move), `style` preset, `actual_duration_s`. The whole
reel lives in one file per reel — **`<reel>/beat_sheet.json`** — which every phase reads and
writes back to (this is the exact filename `generate_audio.py` requires). See the worked
examples in `reels/watchmakers-butterfly/` and `reels/little-red-cap/`.
**GATE 0 — lock the audio before anything visual is generated.**

**Phase 3 — Storyboard stills.** Generate **3 candidate images per scene**; keep the one you
want per scene; regenerate only scenes where none land. Stills are cheap relative to video —
iterate freely here.
→ **`scripts/generate_storyboard.sh <reel_folder> [BEAT…]`** (built): prepends the `style_bible`,
locks identity with Higgsfield Soul (`text2image_soul_v2`) per `metadata.characters`, falls back
to `nano_banana` for object/world beats, retries on rate limits. **Multi-character beats (a Soul
+ a reference, e.g. Red Cap + Wolf) are flagged and skipped — they need the multi-ref runner
(NOT yet built).** **GATE 1 — pick the keeper still per scene, set `chosen_still`.**

**Phase 4 — Video.** From the **chosen still** + a text→(image-to-video) motion prompt (the
still locks composition; the prompt only adds the camera move + action), generate the clip
per scene. Request the smallest Hailuo tier that covers the audio — `--duration 6` if the
beat's audio ≤ 6s, else `--duration 10` — then `ffmpeg -t A` trims the clip to the audio.
Prompt the motion to land its key moment early (the tail gets trimmed). Don't generate video
until the still is approved — video costs more than stills.
→ reuses `generate_videos.sh` (`minimax_hailuo --image`, `--duration`) + a trim-to-audio step.
**GATE 2 — approve the clip ("if that is good") before overlay.**

**Phase 5 — Overlay.** Lay the **title card + narration captions** over the approved video in
Remotion, timed from the Phase-1 word timestamps. Mux the narration as the master audio track
(plus optional music bed).
→ reuses the `muzak-overlay` Remotion caption layer.

## Reuse map (build nothing that exists)

| Need | Reuse |
|---|---|
| Narration + real durations + voice | `bears-doodles/scripts/generate_audio.py` (reads `beat_sheet.json`) |
| Beat schema / story segmentation | extend mini-bio beat metadata (`beat_sheet.json`) |
| Solo-character storyboard stills | `scripts/generate_storyboard.sh` (built) + Higgsfield Soul / nano_banana |
| Video clips | `generate_videos.sh` (`minimax_hailuo`, 6s/10s tiers) |
| Title + captions + assembly | `muzak-overlay` Remotion |

## Build status (honest — this skill is mid-build)

**Working:** Phase 1 audio (`generate_audio.py`) · Phase 2 `beat_sheet.json` schema (two worked
examples) · Phase 3 storyboard stills for **solo-character** beats (`generate_storyboard.sh`,
Bash 3.2-safe, rate-limit backoff).

**Not yet built:**
1. **Multi-ref still runner** — place a Soul + a reference image (or 2+ characters) in one frame
   via FLUX.2 multi-ref / fal compositing. *Needed for most of Little Red Cap (Red Cap + Wolf).*
2. **Phase-4 trim-to-audio video runner** — `generate_videos.sh` clip → request tier ≥ audio →
   `ffmpeg -t A` → mux. (The one genuinely new mechanic vs the music-video chain.)
3. **Phase-5 overlay** — title + narration captions (from ElevenLabs word timestamps) in Remotion.
4. **Beat segmenter** (story → `beat_sheet.json`) and a **storyboard picker** (promote `chosen_still`).

Safe to save as a work-in-progress snapshot; not yet a finished, end-to-end skill.

## Two style presets, one pipeline (the style bible is swappable)

- **phone-grounded** — found-footage reels: one impossible thing per shot, phone-camera realism,
  flat/boring light, lower-third or no captions. (PhoneCamera.md / the Unreal Reels grounding.)
- **cinematic** — polished pieces (the Watchmaker): claymation/chiaroscuro, deliberate push-ins,
  shallow DoF.

Same plumbing; swap the `style_bible` block and the camera vocabulary. Never two pipelines.

## Gates, in one line

`audio-lock → storyboard-pick → video-approve → overlay` — and at every gate you regenerate only
the unit that failed, never the whole batch.
