---
name: greybox
description: >
  Zero-cost previz for explainer videos — game-dev greyboxing applied to the
  beat sheet. Takes any shared-schema `beat_sheet.json` (bears-doodles,
  brownblue, unreal-reels) and renders a deterministic, low-fidelity animated
  previz in a visual-journal / scrapbook collage style: torn-paper cutouts,
  masking tape, ink stamps, handwritten captions. One beat = one cutout on the
  page. NO generative models, NO paid APIs, NO ElevenLabs required — pure
  Python (Pillow) + ffmpeg. Use when the user types `greybox`, `previz`,
  `blockout`, or asks to block out shots/pacing before final renders, review
  beat-to-visual mapping cheaply, or "greybox this beat sheet." Output is a
  review artifact, never a published surface.
---

# Greybox — scrapbook previz before you spend a cent

You are the previz supervisor. **Greybox** is the cheap stand-in pass that
game developers run before final art: block the shots, feel the pacing, move
things freely while moving is still free. Here the "grey boxes" are a visual
journal — paper cutouts, stamps, tape, handwriting — one cutout per beat,
pages that turn at scene boundaries.

A greybox pass answers three questions **before** any Manim render,
ElevenLabs call, or generative video job:

1. **Pacing** — does the beat rhythm feel right at real (or estimated) durations?
2. **Composition** — does each scene's accumulation stay readable, or does the
   page overcrowd?
3. **Beat-to-visual mapping** — does `new_visual_element` actually carry each
   sentence, or are some beats visually empty?

**What makes this skill different from its siblings:**

| | bears-doodles / brownblue | greybox |
|---|---|---|
| Cost | ElevenLabs audio, hours of Manim render | **$0, minutes** |
| Purpose | ship a published surface | **review artifact, never published** |
| Fidelity | final | deliberately low — cutouts and stamps |
| Determinism | n/a | **bit-stable**: same sheet in, same previz out (RNG seeded by `slug|beat_id`) |
| Estimates | banned — real MP3 durations only | **allowed** — word-count timing is exactly the cheap stand-in previz exists for (estimated beats are stamped `EST`) |

## The non-negotiables

1. **Zero generative calls.** No Seedance, no nano-banana, no Higgsfield, no
   ElevenLabs, no image models — nothing billed, ever. If audio already exists
   in `mp3/` it is *reused* for the mux; it is never generated here. The
   **audio ladder** is all free and local: complete real mp3s → scratch
   robo-narration via the OS TTS (`say` on macOS, `espeak-ng`/`flite` on
   Linux; measured durations replace word-count estimates, beats stamped
   `SCR`) → a click track (tick per beat, double tick per page turn) →
   silent (`--no-audio`).
2. **Deterministic.** Every jitter, rotation, and slot placement is seeded from
   the slug and beat id. Re-running on an unchanged sheet reproduces the same
   file. Diffs in the previz mean diffs in the sheet.
3. **Beat sheet is the only input.** The shared schema
   (`../bears-doodles/templates/beat_sheet.schema.json`) is the contract; the
   skill invents no fields. Timing: `actual_duration_s` when present, else
   `words / --wps` (default 2.4), clamped 1.8–14 s and stamped `EST`.
4. **Never a published surface.** Greybox output lives in `<folder>/greybox/`,
   is excluded from packaging/publish scripts, and its media falls under the
   existing large-media gitignore (`*.mp4`, `frames/`). The board HTML and
   report MD are small and tracked.
5. **Respect the brand's screen bans.** Colors come from the sheet's
   `metadata` (accent / brown / highlight); `forbidden_color` is honored even
   here — nobody should acclimate to a look the final can't use.

## Tooling (and why not Remotion)

Pure **Python (Pillow) + ffmpeg** — the same two dependencies every pipeline
script here already assumes (`assemble.py`, `burn_captions.py`). Remotion
exists elsewhere in this repo (Muzak music videos, lecture decks) but is not
part of the explainer aspect and needs a node install per project; previz must
be lighter than the thing it previsualizes. If greybox ever needs interactive
scrubbing beyond the board HTML, a Remotion front-end can be added without
changing the beat-sheet contract.

## Where output lives

```
<video-folder>/                  e.g. quantum-mechanics-vol1/youtube/<slug>-bb/
  beat_sheet.json                input (unchanged, read-only)
  greybox/
    <slug>-greybox.mp4           the animated previz (gitignored via *.mp4)
    greybox-board.html           contact sheet: one card per beat (tracked)
    greybox-report.md            pacing table + warnings (tracked)
    greybox-scraps.md / .txt     asset prompts + id map + provenance (tracked)
    scraps/                      drop generated/archive images here (gitignored)
    scraps/sources.json          provenance sidecar: sid -> source/url (tracked)
    slots/<beat_id>/clip.mp4     drop a video clip for a beat (gitignored)
    scratch/                     cached scratch-TTS wavs (gitignored media)
    frames/board-<beat>.jpg      board keyframes (gitignored via frames/)
```

The canonical script is `scripts/greybox.py` (this folder). Per the
verified-then-copy rule, each book's `youtube/scripts/` carries a copy only
after a change is proven upstream.

## Visual grammar (fixed — do not restyle per video)

- **Page** = one `scene_index`. Kraft-paper background, deterministic fiber
  speckle, tone cycles per scene so page turns read instantly. The texture is
  a 4-frame seeded loop at 3 fps — alive like stop-motion, never jittery.
- **Beat** = one torn-paper cutout, taped down, with an ink stamp bearing the
  `beat_id` and a stand-in glyph chosen by keyword from `new_visual_element`
  (wave, box/well, arrow, axes, particle dots, glow, text — else a grey
  photo placeholder). The cutout slides in and settles during the first
  ~0.5 s of the beat, then bobs gently.
- **beat_type semantics**: `ACCUMULATE` adds a cutout; `CUT` (or a
  `scene_index` change) turns the page; `HOLD` adds nothing — a highlight
  marker pulses on the last cutout; `ZOOM` scales the last cutout up;
  `INTRO` is a big handwritten title card.
- **Caption band** (bottom): handwritten `narration_text`, beat id/type/role,
  per-beat duration (`EST`-stamped when estimated), running timecode.
- **Timeline ribbon** (very bottom): the whole video as colored beat segments
  with a moving playhead — pacing at a glance.
- **Portrait boxes**: whenever the narration names a person (capitalized
  first+last pair), a polaroid stand-in appears on the page — photo window,
  handwritten name, its own scrap id — one per person per scene. The final
  video is assumed to show their picture; the previz stands one in.
- Older cutouts on a crowded page dim; **more than 6 on one page triggers a
  report warning** (the final scene will likely overcrowd too).

## Scraps — mapping generated assets to beats

Every element cutout and every portrait gets a deterministic **3-char
alphanumeric scrap id** and a paste-ready prompt in `greybox-scraps.md`
(+ bare `greybox-scraps.txt`). Prompts open with the id — Midjourney names
output files from the first prompt token, so the filename itself carries the
mapping (e.g. `B1a, A small friendly cut-paper spider... --ar 1:1` →
`user_B1a_A_small_friendly_...png`). Drop finished images into
`greybox/scraps/` keeping the id anywhere in the filename as a token; the
next run cover-crops each one into its cutout (elements) or polaroid window
(portraits) in place of the stand-in glyph. Element prompts use `--scrap-ar`
(default 4:3); portraits are always 1:1. The prompt style block keeps
everything in the cut-paper collage look.

**Provenance and the STAND-IN X.** `scraps/sources.json` records each id's
origin (`generated` | `archive` | `user`, with URL/license). Status is
DERIVED, never hand-edited: a **portrait of a real person** whose image is
generated or unsourced renders with a semi-transparent ink X and a STAND-IN
plate (brand ink — never the forbidden red) and is listed as a warning in the
report. Generated placeholders are encouraged — they show size, gaze, and
tonal weight while blocking — but the X is removed only by replacing the file
with a sourced one. The scraps sheet prints archive search terms (LOC /
Smithsonian Open Access / Wikimedia) next to every portrait so the honest
path is as convenient as the billed one. Elements (generic scenes/objects)
may stay generated; set `"must_replace": true` in the record to force the X
on any asset.

## Clip slots — swap a video into a beat

Drop `slots/<beat_id>/clip.mp4` (generated or your own) and the clip plays in
place of that beat's cutout, **conformed to the beat's measured duration** —
audio is the master clock; clips conform, never the reverse. Conform ladder:
retime within ±5% (imperceptible; clips carry no audio) → trim from the HEAD
when long (clips settle at the end; the settled state hands off) → freeze the
tail when short → **refuse beyond 15%** with a loud report note (regenerate
at the right tier — always order the smallest tier ≥ the target). Each
decision is logged in `greybox-report.md` under "Clips (conform ladder)".
Multi-beat spans (one clip covering 2–3 consecutive beats) are a planned
schema extension; spans must never cross a scene boundary.

## Commands

Respond to the first word (`greybox`, `previz`, `blockout`).

### `greybox <folder>` — the whole pass
Run (with the `~/ai` venv or any Python ≥3.9 with Pillow; ffmpeg on PATH):

```
python scripts/greybox.py <folder>              # 16:9, 854x480 @ 12 fps
python scripts/greybox.py <folder> --portrait   # 9:16, 480x854
```

If **every** timed beat already has its `mp3/` file, the real narration is
muxed under the previz automatically (previz-at-real-pace); otherwise the
previz is silent and estimated beats are stamped `EST`. Then present all
three artifacts: the mp4, the board, and the report — and say which beats the
report flagged. Useful flags: `--fps`, `--height`, `--wps`, `--sheet` (an
alternate/draft sheet, e.g. `beat_sheet.short.json`), `--fonts`.

### `report <folder>` — pacing table only
`python scripts/greybox.py <folder> --report-only` — no video encode; writes
`greybox-report.md` + board. Use for a quick sheet review mid-authoring.

### `status <book-youtube-dir>`
Scan `<dir>/*/beat_sheet.json` and report, per video: beats, est vs actual
timing coverage, and whether a `greybox/` pass exists and is newer than the
sheet (stale previz = re-run).

## Fit in the pipeline

Greybox slots **between Gate 2 (beats) and Gate 3 (audio)** — it is the reason
to reject a sheet before paying for audio, and it stays useful after audio
exists (re-run to hear real pacing under stand-in visuals). The gate rule from
the parent skills still applies: greybox output informs the human decision; it
never substitutes for the clean-master approval.
