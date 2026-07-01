---
name: deck-lecture
description: >
  Turn an HTML slide deck (.dc.html) into a narrated lecture video in Remotion —
  one slide = one beat = one voice-clone MP3 played over the LIVE slide, with
  karaoke captions of the exact narration. The script DISCUSSES each slide, it
  does not read it: every beat's narration is the slide's data-speaker-notes
  expanded into spoken teaching voice. Audio-first and phase-gated. Use when the
  user types `deck-lecture`, `lecture video`, `voice-over deck`, `narrate this
  deck`, or asks to turn a slide deck / .dc.html into a spoken lecture or
  explainer video with their voice. Reuses bears-doodles ElevenLabs audio, the
  music-video faster-whisper caption pipeline, and Remotion.
metadata:
  tags: deck-to-video, lecture, voice-clone, elevenlabs, faster-whisper, remotion, captions, audio-first, phase-gated
---

# Deck Lecture — HTML slide deck → narrated lecture video

Turn a finished HTML deck into a lecture video where **one slide = one beat = one
narrated MP3 (your voice clone) over the live slide**, captioned word-by-word with
the exact narration.

## The one rule

**The narration is the master clock.** Audio is generated and *measured* first
(`actual_duration_s`); every slide's on-screen time is its real spoken duration
plus a short breath. Never estimate from word count. Captions and slide timing
are derived from the audio, not the other way around.

## The other rule — discuss, don't read

The narration is **not** the words on the slide read aloud. Each beat's script is
the slide's `data-speaker-notes` **expanded** into natural spoken teaching voice —
it explains, motivates, and connects what the slide shows. The slide carries the
formal statement; the voice carries the understanding. Guardrail: if a beat's
narration overlaps the slide's visible text too heavily, rewrite it (see
*Discuss-don't-read guard* below).

## Inputs

- A `.dc.html` deck whose slides are `<section data-label="…" data-speaker-notes="…">`
  (the deck-stage format — `deck-stage.js` + `support.js` sit beside it).
- `ELEVENLABS_API_KEY` in the environment. Voice defaults to Bear's clone
  `TyW6NH39JcFb5M3xdIIk` (override via `beat_sheet.json` → `metadata.voice_id`).

Everything for one lecture lives in **one folder** (default: the deck's folder),
with `beat_sheet.json` as the single source of truth that every phase reads and
writes back to.

## Phase-gated pipeline (regenerate only the failing unit at each gate)

**Phase 0 — Extract.** Parse the deck into `beat_sheet.json` — one beat per slide,
carrying `slide_index` (the deck's `location.hash` index), `label`,
`speaker_notes`, `on_slide_text`, and an empty `narration_text`.
→ `scripts/extract_slides.py "<deck>.dc.html" -o <folder>`

**Phase 1 — Script (expand the notes).** For each beat, write `narration_text` by
expanding `speaker_notes` into spoken teaching voice — discuss the slide, don't
read it. Use `my-writing-style` if available so it sounds like the user. Run the
discuss-don't-read guard. **GATE — the user approves the scripts before any audio
is generated** (this is the cheapest place to fix things).

**Phase 1.5 — TTS clarity check (audit before you spend render budget).** TTS
fails at predictable categories, not at random: rare proper nouns, acronyms that
could be word- or letter-read, ambiguous symbols/single-letter variables,
ambiguous numerals, and Latin abbreviations. Scan the scripts statically, fix the
flagged spans with an inline respelling, and you only listen-test the flagged
words instead of the whole lecture.
→ `scripts/tts_audit.py <folder> --seed-dict <folder>/pronunciations.json`
(ranked HIGH/MEDIUM/LOW report; writes a respelling template for HIGH terms).
Fill the respellings in `pronunciations.json` — capitalized-syllable stress, e.g.
`"Mullainathan": "muh-LYE-nuh-thun"`, never IPA (the model ignores it). The
suggested respelling is the model's/your job; the script only finds the risks.
Then bake them into the **TTS-facing field only**:
→ `scripts/apply_pronunciations.py <folder>` — writes `tts_normalized_text` =
`narration_text` with the respellings applied. **`narration_text` is never
touched**, so captions and speaker notes keep the correct spelling; only
ElevenLabs sees the respelling. Re-run `tts_audit.py` — respelled terms show as
*resolved*. (The model `generate_audio.py` uses, `eleven_multilingual_v2`, does
not support phoneme/IPA tags — inline spelling substitution, ElevenLabs' "alias"
approach, is the supported route.)

**Phase 2 — Audio (audio-first, voice clone).** Generate one ElevenLabs MP3 per
beat (from `tts_normalized_text` when present, else `narration_text`), measure
real duration, write `actual_duration_s` + `audio_file` back to the sheet.
`beat_sheet.json` is already schema-compatible — no adapter.
→ `python ../../aspects/explainer/bears-doodles/scripts/generate_audio.py <folder>`
(writes `<folder>/mp3/beat-S01.mp3`, `mp3/timings.json`). TTS rarely fails; if one
does, regenerate only that beat with `--only S07`.
**GATE 0 — lock the audio before anything visual.**

**Phase 3 — Captions (forced alignment).** Same mechanism as the music videos:
the narration text is known, so faster-whisper supplies only the *timing*; each
known word snaps onto the moment it is actually spoken. Captions **display
`narration_text`** (correct spelling), never the respelled `tts_normalized_text`.
Produces `captions.json` with slide-local per-word frames in the karaoke schema.
→ `scripts/align_captions.py <folder> [--model base]`

**Phase 3.5 — Visuals: don't stare at text for 30s.** A dense slide is right for
~3s but the narration runs 30s+. Each slide gets one of **three tiers** (chosen
after a ~`slide_hold_s` live hold), all in the **deck's typography (Lato/NU)**:

1. **live** — slide has a D3 chart (`data-chart`): keep it on-screen the whole slide.
2. **doodle** — an authored sketch exists: draw it on (line art, **one narration
   line = one new element**). Remotion-native (no Manim): spec in `doodles.json`
   (`{beat_id:{title,elements:[…]}}`), rendered by `src/Doodle.tsx`, timed by
   `atLine`/`atFrac`. Kinds: label, rect, line, arrow, circle, dots.
   → `scripts/build_doodle.py` (starters) · `scripts/preview_doodle.py` (SVG snapshot).
3. **bullets** — for every other text-heavy slide: a **headline takeaway** (a
   meta-summary of the slide, e.g. "Fairness is a choice, not a calculation") over
   short **summary** bullets that animate in one per line (NU-red markers, current
   emphasized). The headline + bullets are **hand-written** (like the narration and
   doodles) — `build_bullets.py` only makes a rough starter; a regex can cut text
   but cannot summarize, so the real summaries are authored. Title slide, "Part N"
   dividers, and the closing card are skipped (they stay live as big-type cards).
   Spec in `bullets.json`, rendered by `src/Bullets.tsx`.
   → `scripts/build_bullets.py` (starter; preserves hand edits) ·
   `scripts/preview_bullets.py` (SVG snapshot).

A slide with neither a doodle nor bullets falls back to live, so the lecture always
renders. Priority per slide: doodle > bullets > live.

**Phase 4 — Render (live deck + doodles + captions).** Scaffold the Remotion
project, then render. `live` slides are a `deck.html#<index>` iframe (authored CSS
entry animations play) for the full slide; `doodle` slides hold the iframe
`slide_hold_s` then crossfade to the drawn sketch. Narration audio + karaoke
captions ride on top throughout; slide length = audio + tail-padding.
→ `scripts/scaffold_remotion.py <folder> --deck "<deck>.dc.html"`
→ `cd <folder>/remotion && npm install && npm run render` → `out/<slug>.mp4`
(use `npm run studio` to preview before the full render).

## Reuse map (build nothing that exists)

| Need | Reuse |
|---|---|
| Voice-clone MP3 per beat + real durations | `aspects/explainer/bears-doodles/scripts/generate_audio.py` (reads `beat_sheet.json`) |
| Beat sheet schema / audio-first convention | `beat_sheet.json` (this skill emits it directly) |
| Forced-aligned karaoke timing | faster-whisper, same approach as `aspects/songbird/muzak/scripts/align_lyrics_audio.py` |
| TTS pronunciation pre-flight | `scripts/tts_audit.py` (wordfreq + regex) + `scripts/apply_pronunciations.py` |
| Progressive-disclosure doodles | `src/Doodle.tsx` (Remotion-native, bears-doodles style) + `scripts/build_doodle.py` / `preview_doodle.py` |
| Auto bullets for text slides | `src/Bullets.tsx` + `scripts/build_bullets.py` / `preview_bullets.py` |
| Caption typography / colors | `aspects/songbird/muzak-overlay` theme → ported in `templates/remotion/src/theme.ts` |
| Composition / assembly | Remotion (`templates/remotion/`) |

## Discuss-don't-read guard

After Phase 1, for each beat compute token overlap between `narration_text` and
`on_slide_text` (Jaccard over lowercased content words). If overlap is high
(≈ > 0.6) the script is probably reading the slide — rewrite it to explain rather
than recite. Bullets and equations on the slide should appear in the narration as
*ideas*, not as transcription.

## Live-HTML caveat + fallback (honest)

Rendering the **live** deck inside Remotion (one iframe per slide at
`deck.html#<index>`) is the experimental part. Remotion drives the page clock so
authored CSS entry animations (`[data-deck-active] .rise{…}`) generally capture
deterministically, and the presenter rail is suppressed via a `localStorage` flag
injected into the copied `deck.html`. If a particular deck's animations don't
capture cleanly (blank frames, half-played animation), fall back to **prerender
mode**: screenshot each slide's settled state to PNG with headless Chromium and
swap `DeckBackground` for a still `<Img>` — the rest of the pipeline (audio,
captions, timing) is unchanged. The two design forks the user rejected for the
default (static PNG / per-reveal capture) live here as the fallback.

## Assumptions to check per deck

- Slide order = DOM order of `<section data-label>`; the deck's `location.hash`
  is a 0-based index into that order. If the deck filters/skips indices, map
  `slide_index` accordingly.
- Slides with progressive reveals: the live iframe plays the entry animation
  once, then holds the settled slide for the rest of the narration. Narration
  that references motion mid-sentence won't re-trigger it.

## Build status (honest)

**Working:** Phase 0 extractor (tested on a 39-slide deck) · `beat_sheet.json`
emitted compatible with `generate_audio.py` · Phase 1 discuss-don't-read guard ·
Phase 1.5 TTS clarity audit + respelling applier (tested on the 39-slide deck:
11 names auto-flagged and resolved into `tts_normalized_text`, captions left
correct) · Phase 3 caption aligner · Phase 3.5 visual_mode routing (8 live-D3 /
31 doodle auto-detected) + Remotion-native doodle renderer + build/preview tools
(S05 "demographic parity" authored as POC) · Phase 4 scaffold + Remotion
templates (live-iframe background, two-phase doodle slides, ported karaoke
caption layer, audio-first sequencing).
**Needs a live run to confirm:** ElevenLabs render end-to-end (needs API key),
faster-whisper install, and live CSS-animation capture for a given deck (else use
the prerender fallback).

## Worked example — the fairness-metrics deck

```
DECK="lectures/fairness-metrics-and-impossible-choices/Chapter 7 - Fairness Metrics.dc.html"
FOLDER="lectures/fairness-metrics-and-impossible-choices"

# 0. extract 39 slides -> beat_sheet.json
python skills/deck-lecture/scripts/extract_slides.py "$DECK" -o "$FOLDER"

# 1. fill each beat's narration_text (expand speaker_notes; discuss, don't read) -> GATE
python skills/deck-lecture/scripts/script_guard.py "$FOLDER"

# 1.5 TTS clarity check -> fill pronunciations.json -> bake into tts_normalized_text
python skills/deck-lecture/scripts/tts_audit.py "$FOLDER" --seed-dict "$FOLDER/pronunciations.json"
#     (edit pronunciations.json: e.g. "Chouldechova": "chool-deh-KOH-vuh")
python skills/deck-lecture/scripts/apply_pronunciations.py "$FOLDER"

# 2. audio-first voice clone (reads tts_normalized_text)
python aspects/explainer/bears-doodles/scripts/generate_audio.py "$FOLDER"   # GATE 0
# 3. forced-aligned captions
python skills/deck-lecture/scripts/align_captions.py "$FOLDER"
# 3.5 doodles for the text slides (starters, then upgrade the important ones)
python skills/deck-lecture/scripts/build_doodle.py "$FOLDER"
python skills/deck-lecture/scripts/preview_doodle.py "$FOLDER" S05   # eyeball before render
# 4. assemble + render
python skills/deck-lecture/scripts/scaffold_remotion.py "$FOLDER" --deck "$DECK"
cd "$FOLDER/remotion" && npm install && npm run render
```
