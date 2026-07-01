---
name: songbird-dance
description: >
  Turn a danceable song into a beat-synced dance reel where a single character dances ON
  the beat — built for Higgsfield Seedance 2.0, which takes an image + an audio clip and
  generates motion locked to that audio. Use when the user wants a dance video, a character
  dancing to a song, beat-matched choreography, a rubber-hose / Cab Calloway / Fleischer
  cartoon dance, or types `dance`, `dance reel`, `seedance`, `choreography`, `dance beats`.
  THE KEY DIFFERENCE FROM lyric-match: dance beats are long — ~10-15s downbeat-aligned
  segments (Seedance's 15s cap), not ~5s per-lyric-line beats. The dance, the character's
  look, and the danceability of the music ARE the story, so the prompt is mostly CHARACTER
  + CHOREOGRAPHY + CAMERA, with style as a short tag. Audio-first: the per-beat audio slice
  drives the on-beat motion; the master track is muxed at assembly.
---

# Songbird Dance — a character dancing on the beat

A sibling mode to `lyric-match`, for songs where the dance is the point. Same Songbird
engine, two differences: **long beats** and a **different prompt shape**.

| | lyric-match (cinematic) | songbird-dance |
|---|---|---|
| beat length | ~5-6s (one lyric line) | **~10-15s** (a dance phrase, Seedance cap) |
| boundaries | lyric-line timing | **snapped to musical downbeats** |
| video model | Minimax Hailuo (`--image`) | **Seedance 2.0** (`--image` + `--audio`) |
| prompt is about | the scene + the words | **character + choreography + camera** |

## The one rule (unchanged)

**Audio is the master clock.** Segment timing comes from the real librosa beat grid; each
beat's audio slice is fed to Seedance to drive on-beat motion. Beats tile the song with no
gaps and never exceed 15s.

## The prompt formula (this is the whole point)

For a dance beat, write the prompt in five parts, in this order — **mostly choreography**:

1. **Character** — one short clause, the look (the still locks identity; keep it brief).
2. **Dance** — the move + how it hits the beat (`a Cab Calloway strut — glides side to side,
   head bobbing, snaps a finger hard on every downbeat`).
3. **Camera** — one specific angle/move, and **vary it per beat** (locked-off wide, low hero
   angle, slow push-in, slow orbit, dutch tilt, overhead, side-tracking dolly, pull-back…).
4. **Background** — state it EXPLICITLY. Vague words ("moody backdrop") make the model invent
   a stage with a spotlight and falling confetti. Describe the actual space and what's in it
   (`a spooky monochrome-grey hall, wispy ghostly smoke-creatures drifting like Patronuses; no
   spotlight, no stage, no confetti`).
5. **Style** — a SHORT shared tag, not a paragraph. Over-stuffing the style is what makes the
   model hallucinate (collages, extra characters). One line + "no text, no extra characters."

> A tall lanky grinning rubber-hose puppet. **Dance:** a Cab Calloway strut — glides side to
> side, head bobbing, snaps a finger on every downbeat. **Camera:** locked-off wide, low
> angle, full body. Rubber-hose 1930s cartoon style, on the beat. No text.

A solo-friendly 1930s vernacular vocabulary (Fleischer rotoscoped Calloway, so it prompts
well): **Calloway strut, shimmy, soft-shoe, Charleston, Truckin', spin-and-freeze, Black
Bottom, rubber-hose melt, Lindy air-kick, conga hop, finale strut.**

## Pipeline

**Phase 1 — Audio analysis.** `analyze_audio.py` → `beat_data.json` (downbeats are the cut grid).

**Phase 2 — Dance segmentation.** `scripts/build_dance_beatsheet.py <reel> --audio … --title …
--character "…"` greedily cuts the song into **10-15s segments, each ending on a downbeat**,
never over 15s; cycles the character stills; assigns a move + a distinct camera per beat;
writes `beat_sheet.json` (mode: dance) with the four-part `video_prompt`. Optional lyrics are
attached per segment for captions only.
**GATE 0 — lock the segments + prompts.**

**Phase 3 — Per-beat audio slices.** `scripts/slice_beat_audio.sh <reel>` → `audio/<beat>.wav`,
each beat's slice (≤15s) to feed Seedance's `--audio`.

**Phase 4 — Video (Seedance, beat-matched).** `scripts/generate_video_seedance.sh <reel> [BEAT]`
— per beat: `seedance_2_0 --image chosen_still --audio audio/<beat>.wav --prompt video_prompt
--duration <≤15> --generate_audio false`, then trim to the beat. Register once:
`higgsfield model get seedance_2_0`.
**GATE 1 — TEST ONE BEAT and verify the dance lands on the beat before the full run** (compare
the clip's motion-energy peaks to `beat_data.json` beat times; "energetic" is not "on-beat").

**Phase 5 — Assemble.** `FINAL=1 generate_video_seedance.sh <reel>` concatenates the silent
clips and muxes the master WAV (clips are silent by design — `generate_audio false`).

## Mixed Kling + Seedance (two-pass — the cost-smart default)

Seedance burns credits (~8× a Kling clip) and "Unlimited" is web-only. So the default is a
**mix**, decided per beat by `beat.video_model`:

- **kling** — 5s beat, a **start + end** frame pair (Kling tweens between them), generated by
  hand on higgsfield.ai under Unlimited mode (free). Most beats.
- **seedance_2_0** — a single start frame + the beat's audio slice, audio-locked motion, ≤15s.
  Reserved for the few sections that earn it.

**Pass 1 — build it all on Kling.**
1. `build_dance_beatsheet.py … --model kling` → ~5s downbeat beats, every `video_model: kling`.
2. `generate_startend_storyboard.sh <reel>` → a `_A_start.png` + `_B_end.png` per beat (FLUX, `RES=1k`
   ≈ free). Branches automatically: seedance beats get only `_A_start.png`. **Naming matters:** the
   `_A_start` / `_B_end` suffixes map to Kling's two frame slots (A = first frame, B = last frame) AND
   sort A→B in a file listing — never `_start`/`_end`, which sort end-before-start and upload backwards.
3. `make_shotlist.py <reel>` → **SHOTLIST.md**: every beat in order with its frame files, settings,
   and prompt in a copy-block — so the web grind is upload-upload-paste down the list.
4. Generate each on the web (Kling 5s 720p Unlimited), download to `video/<beat>.mp4`.
5. Assemble locally (concat + mux master); the assembler stitches whatever clips exist.

**Pass 2 — promote the sections that earn Seedance.**
6. Watch the Kling cut. `promote_to_seedance.py <reel> B07 B08 B09 [--merge]` re-tags those beats
   (or merges a run into one ≤15s Seedance beat) and renumbers.
7. Re-run `generate_startend_storyboard.sh` (single start frame for the promoted beats) +
   `slice_beat_audio.sh`, then `generate_video_seedance.sh <reel>` on just those beats, and re-assemble.

## Download + build (web-generated clips)

After generating clips on the web (both aspects if you want), one command pulls them down
named for their beat and builds every aspect:

```
build_videos.sh <reel>     # fetch_and_match (routes 16:9 -> video-16x9/raw, primary -> video/raw)
                           # then assembles each: <slug>.mp4 (primary) + <slug>.16x9.mp4
```

Pieces it chains:
- `fetch_and_match.py <reel> --video` — `higgsfield generate list --json` → match each job's
  prompt to a beat's `video_prompt` → download to `video[-aspect]/raw/<beat>.mp4`. Newest per
  prompt by default; `--all` keeps `_v2…`. (No "liked" flag exists in the CLI — cull locally.)
- `reconcile.py <reel>` — after you delete the meh ones, randomly keeps one survivor per beat as
  the canonical name and writes **REDO.md**, a shot-list of only the still-missing beats.
- `generate_video_seedance.sh … ASSEMBLE_ONLY=1 FINAL=1` (per aspect via `TAG`) — stitches the
  dropped clips + master audio; refuses to build if a beat clip is missing (no silent short).

## Reuse map

| Need | Reuse |
|---|---|
| Beat grid + downbeats + duration | `aspects/songbird/muzak/scripts/analyze_audio.py` |
| Dance segmentation + 4-part prompts | `scripts/build_dance_beatsheet.py` (this skill) |
| Per-beat audio slices | `scripts/slice_beat_audio.sh` |
| Seedance image+audio video, cut to beat, mux | `scripts/generate_video_seedance.sh` |

## Honest cautions

- **Beat-match is the thing to verify, not assume.** Test one segment; measure peaks vs the
  grid. It's the model's advertised strength and the most common place it bluffs.
- **15s solo dance is high-variance** for character consistency — the still locks the look but
  long motion can drift. Cycle a few reference stills and keep the style tag short.
- **Seedance audio cap is 15s**, which is exactly why beats are downbeat-segmented to ≤15s.
