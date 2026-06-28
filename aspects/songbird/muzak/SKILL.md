---
name: muzak
description: >
  Turn a song (a WAV plus its lyrics) into a beat-synced music video built
  mostly from Remotion motion graphics — spectrum/waveform audio visualizers,
  beat-reactive springs, energy-driven color, and kinetic lyrics, all driven
  off an offline beat analysis of the actual audio. Use when the user wants a
  music video, a lyric video, an audio-reactive visualizer, or to "set this
  track to motion graphics"; or types `muzak`, `new`, `analyze`, `lyrics`,
  `plan`, `build`, `render`, or `status`. Audio-first, phase-gated, one
  kebab-case folder per song. The skill only asks for custom media when a
  specific beat genuinely needs it — everything else is generated in code.
metadata:
  tags: remotion, music-video, lyric-video, audio-visualizer, beat-sync, librosa, motion-graphics, wav, kinetic-typography
---

# Muzak — Music Video Pipeline

Part of **Songbird** — Claude + CLI tools for music-video production. Videos publish
as early-stage tests; see the `publish` phase for the YouTube title/description convention.

You are the director of a **music video built in Remotion**. The input is a song:
a **WAV file** and its **lyrics**. The output is a runnable Remotion project whose
motion graphics are locked to the music — bars that dance to the spectrum, cuts
that land on the beat, color that breathes with the energy envelope, and lyrics
that hit in time. The look should be *mostly Remotion-generated*; you ask the user
for custom media (a photo, a clip, a logo, an SVG) **only** for the few beats where
hand-made media genuinely beats anything code can draw.

This is the motion sibling of `cajal-video-tutorial` and `bears-doodles`: same
discipline — **audio-first, phase-gated, one folder per artifact, the skill stops
at a runnable project + render commands and never claims to have produced the MP4
itself** (rendering needs headless Chromium and minutes of compute).

## The one rule everything else serves

**The audio is ground truth.** Every animation length, cut, flash, and lyric hit is
derived from an offline analysis of the *actual WAV* — never from guessing the tempo
or eyeballing the lyrics. `analyze` runs first and writes `beat_data.json`; nothing
downstream invents timing. If the beat data and the music ever disagree, the music
wins and the data gets regenerated.

## Read before acting

These bundled files are your operating manual. Read the one relevant to the current
phase; don't restate them at the user.

- `references/remotion-audio.md` — the Remotion audio APIs and their gotchas
  (`visualizeAudio`, `useWindowedAudioData`, `delayRender`/`continueRender`, the
  power-of-two and log-scaling traps). **Read before writing any visualizer code.**
- `references/motion-patterns.md` — the reusable recipes: beat-reactive springs,
  scene cuts on beat, energy→color, waveform paths, music-under-voice ducking, and
  **which visualizer to choose for which kind of section.**
- `references/lyrics-to-scene.md` — how to **author the per-block scene descriptions**
  for generated background media: the interpretation stack (literal→emotion→metaphor→
  shot grammar), the never-echo-the-lyric rule, and how to flatten to one prompt line.
  **Read before writing `scenes.json`.**
- `references/audiogram.md` — the **look options**: visualizer types (incl. the
  audiogram), audiogram tuning knobs, lyric/karaoke styles, beat reactions. **Read
  before changing the visual style.**
- `references/design-inference.md` — how muzak **derives the look from the song**:
  the feature→design mapping rules and the hard constraints. **Read before `design`.**
- `references/beat-data-schema.md` — the exact JSON contract `analyze` produces and
  `build` consumes.
- `references/default-look.md` — the neutral fallback look and the design precedence
  chain. Read when no design source exists.

Scripts (run in the project's environment; `analyze` needs `librosa`):

- `scripts/new_video.py` — scaffold the song folder + a blank Remotion project, copy
  the WAV into `public/`, and write a `song.json` manifest.
- `scripts/analyze_audio.py` — librosa analysis of the WAV → `beat_data.json` (bpm,
  beat + downbeat timestamps, per-frame onset energy, sections, duration, **and a
  `features` block: brightness, dynamic range, key/mode — the design signals**).
- `scripts/align_lyrics.py` — raw lyrics → timed `lyrics.json` (line → start/end
  frames, **seeded** from the beat grid) **plus a `density` block (words/sec, class)**.
- `scripts/align_lyrics_audio.py` — the accurate path: **forced alignment**. Whisper
  (faster-whisper) word timestamps, sequence-aligned to the known lyrics so the correct
  words land on real sung moments; adds per-line `words[]` for true karaoke timing.
- `scripts/infer_design.py` — features → `design.json`: a constrained design brief
  (caps, easing, allowed lyric styles, visualizer form, starting palette, section
  registers) + an optional generated `theme.ts`.
- `scripts/media_prompts.py` — chunk the song into fixed blocks (B01, B02, …, default
  5s) and write a text-to-image + text-to-video prompt for each, grounded in that
  block's lyric phrase + the design metaphor/palette. These generated clips/stills are
  the **background layer** the wave + lyrics overlay on top of.

## The design seam — muzak infers the look, then you refine it

muzak doesn't wait for a human to specify a palette: it **derives** a design from the
audio and lyrics, because look decisions are responses to musical and semantic signals
(bright timbre → cool color, compressed master → no strobing flash, fast lyrics → no
character-springs). The `design` phase runs `infer_design.py` for the constrained,
computed skeleton, then you reason the semantic fields from the lyrics. Full rules and
caps live in `references/design-inference.md`.

**Precedence for the look** (highest wins) when you `build`:

1. A hand-written design doc at `design/[slug].md` (a person who knows what they want).
2. The inferred `design.json` from the `design` phase.
3. The neutral baseline in `references/default-look.md` (only if `design` was skipped).

All aesthetics flow through **one `theme` object** (`theme.ts`, generated from
`design.json`); the mechanical components read only from it. So the look is a clean
swap and the mechanics stay design-agnostic. Never hardcode palette/type/motion in a
component — and never raise a computed cap (e.g. `flashMax`) for drama; the cap is a
fidelity guarantee, not a default.

## Inputs

- **WAV** — the master audio. MP3 is accepted but converted first
  (`ffmpeg -i in.mp3 out.wav`); WAV is more reliable for FFT analysis.
- **Lyrics** — plain text, one line per line. Section tags like `[Chorus]` are
  honored if present. Timestamps optional; if absent, `align_lyrics` seeds them and
  you refine with the user.
- **Format** (optional) — defaults to **1920×1080, 30 fps**. Square 1080×1080 or
  vertical 1080×1920 on request.
- **Design doc** (optional) — see the design seam above.

## The pipeline

```
new → analyze → lyrics → design → plan ──(gate)──► build → render handoff
 │       │         │        │        │               │          │
 │       │         │        │        │               │          └─ preview / still / render commands
 │       │         │        │        │               └─ Remotion components from templates, themed from design.json
 │       │         │        │        └─ visualizer + media plan; ask for custom media ONLY where it earns its place
 │       │         │        └─ design.json: inferred brief (palette/motion/type/visualizer) + theme.ts
 │       │         └─ lyrics.json (line → frames + density), refined with the user
 │       └─ beat_data.json (timing ground truth + timbre features)
 └─ song folder + blank Remotion project + WAV in public/
```

Respond to the **first word** of the user's message. If they paste a song/lyrics with
no command, assume `new`.

### `muzak` / `help`
List the commands below and ask for the WAV + lyrics (and any format/design wishes).

### `new <title>` — scaffold
1. Derive a kebab-case `slug` from the title.
2. Run `scripts/new_video.py --slug <slug> --title "<title>" --wav <path> [--width --height --fps]`.
   It creates the project, copies the WAV to `public/<slug>/audio.wav`, and writes
   `song.json` (slug, title, format, paths). Default format 1920×1080@30.
3. Report the folder path and the next step (`analyze`). Generate no content yet.

### `analyze` — the audio is ground truth (audio-first gate)
Confirm `librosa` is importable (the script prints an install hint if not). Run
`scripts/analyze_audio.py <project>/public/<slug>/audio.wav --fps <fps> -o <project>/beat_data.json`.
It writes the contract in `references/beat-data-schema.md`: `bpm`, `beatTimestamps[]`,
`downbeatTimestamps[]`, `energyPerFrame[]`, `sections[]`, `durationInSeconds`,
`durationInFrames`, and a **`features`** block (brightness, dynamic_range_db,
key, mode, mode_confidence — the design signals). Report tempo, duration, frame
count, the section breakdown, and the feature read-out.
**This is the timing all later phases read — do not hand-edit it; regenerate if wrong.**

### `lyrics` — time the words
Two modes. **Prefer forced alignment** — it's the difference between words that match
the vocal and words that merely drift past on a grid.

- **Accurate (recommended): forced alignment.** Run
  `scripts/align_lyrics_audio.py <lyrics.txt> --audio <project>/public/<slug>/audio.wav
  --beat-data <project>/beat_data.json -o <project>/lyrics.json [--model base]`.
  Whisper (faster-whisper — plain `pip install faster-whisper`, no native-build pain)
  produces word-level timestamps; the script sequence-aligns them to the *known* lyrics,
  so a mis-heard sung word is corrected back to the real word while keeping its real
  timing, and any word Whisper dropped is interpolated. Output carries per-line `words[]`
  for true word-by-word / karaoke timing. Use a larger `--model` (small/medium) when the
  vocal is heavily stylized.
- **Fallback (no Whisper): beat-grid seed.** Run `scripts/align_lyrics.py <lyrics.txt>
  --beat-data <project>/beat_data.json -o <project>/lyrics.json`. It distributes lines
  across their section's beats — fine for a rough cut, but it does **not** know when a
  word is actually sung, so expect drift and plan to nudge anchors by ear.

Both write a `density` block (words/sec → class) that constrains the lyric animation
style in `design`. Present the timed lines and invite corrections — fixing timing here is
far cheaper than after a render. (Gate-ish: get the timing right before designing.)

### `design` — infer the look from the song
Run `scripts/infer_design.py --beat-data <project>/beat_data.json --lyrics
<project>/lyrics.json -o <project>/design.json --emit-theme <project>/src/theme.ts`.
That fills every **computed/safety** field from the rules in
`references/design-inference.md` — beat-hit caps (from dynamic range), spring easing
(from BPM), allowed lyric styles (from density), visualizer form (from brightness), a
curated starting palette (from brightness + mode bias), and section registers.

Then do the **semantic pass yourself**: read `design-inference.md`, read the lyrics,
and fill the null fields in `design.json` — `visual_concept`, `visual_metaphor` (the
one dominant idea + the lyric lines that anchor it), section `notes` (rename
`section_N` to verse/chorus/etc. from the lyric tags), `negative_space_strategy`,
`proof_of_concept_note` — and refine the palette *within* its temperature bucket. Every
choice must trace to a feature value or a specific lyric line; never default to a
synthwave/lo-fi aesthetic the features don't support, and **never raise a computed
cap**. Present the brief with its rationale. If the user has a hand-written
`design/[slug].md`, that outranks the inferred brief (treat the computed caps as still
worth honoring).

### `plan` — visualizers + the honest media ask (GATE)
Produce a short **plan** the user signs off on before any component code:

- **Section map** — for each section (now named in `design.json`'s `section_registers`),
  name the dominant visual and **which visualizer fits**. The `design` phase already set
  a global `visualizer.type` from brightness; here you confirm or vary it per section
  using the chooser in `references/motion-patterns.md`. Rough heuristic:
  dense/loud instrumental or a drop → spectrum bars; sparse/vocal passage → smooth
  waveform; low rumble → bass pulse; quiet intro/outro → minimal, maybe just the
  energy-driven background. A visualizer that doesn't carry the moment gets cut.
- **Beat-sync moves** — where cuts land on downbeats, where beat-flashes or spring
  "thuds" fire, where the lyric style shifts (e.g., hook gets bigger type).
- **The media ask — sparing by default.** Default to *fully code-generated* visuals.
  List only the specific beats where supplied media genuinely beats code: e.g. a hero
  image on the first drop, an artist logo on the final hit, a piece of footage behind a
  chorus. For each, give the **exact filename**, the **target timestamp/section**, the
  **aspect ratio**, and where it drops (`public/<slug>/media/`). If nothing truly needs
  custom media, say so and build it all in code. Never pad the list to seem thorough.

- **Generated background media (optional, overlay).** Beyond the sparing one-off asks,
  muzak can fill the whole frame with AI-generated media. First **author the scenes** in
  `scenes.json` following `references/lyrics-to-scene.md` — describe a *scene* per block
  (shot grammar: framing, camera move, light, palette), never echoing the lyric. Then run
  `scripts/media_prompts.py --beat-data … --lyrics … --design … --scenes scenes.json
  --style "<your look>" --chunk 5 -o <project>/media-prompts.md` to chunk the song into
  blocks `B01, B02, …` and emit a clean text-to-image + text-to-video prompt per block
  (each = authored scene + your `--style` suffix; every prompt starts with its block id).
  Without `--scenes` it falls back to lyric fragments, which don't describe a scene — so
  always author scenes for anything you'll actually generate.
- **Cast + character consistency (Higgsfield).** Tag each beat in `scenes.json` under
  `cast` as `man` / `woman` / `none`. `media_prompts.py` then emits `media-jobs.json`: a
  beat with a character routes to a Soul-ID model (`text2image_soul_v2`) with that
  character's `--soul-id` and an anchor description prepended; a `none` beat routes to
  `nano_banana` (no character). Pass the Soul IDs + descriptions as flags
  (`--man-soulid/--woman-soulid/--man-desc/--woman-desc`); the user names the characters
  or you fall back to the configured defaults. The Higgsfield prompt is clean — no block
  id, no Midjourney flags — with a separate `--hf-style` (descriptive style, append
  `no text` since the overlay supplies the lyrics).
- **Generate the images (step 1, image-first).** Drop `assets/templates/generate_images.sh`
  into the song folder. It reads `media-jobs.json` and produces **3 generations per beat**
  (`gen/<id>_v1..v3.jpg`) via the Higgsfield CLI — character beats with the Soul ID, the
  rest with `nano_banana`, 16:9 by default (9:16 on request). The user picks the best per
  beat, copies it to `public/<slug>/media/<id>.jpg`, and adds it to `media-manifest.json`.
  The skill writes the script and the job spec; the user runs it (it needs their
  authenticated Higgsfield CLI).
- **Animate the stills (step 2, text+image→video).** `assets/templates/generate_videos.sh`
  reads each beat's kept still + its `video_prompt` from `media-jobs.json` and animates it
  with **Minimax Hailuo** (`minimax_hailuo --model minimax-2.3 --image <still> --duration 6
  --resolution 768`). Notes from the live schema: the image flag is `--image` (not
  `--input-images`); identity + 16:9 framing come from the still, so **no `--soul-id` and no
  `--aspect_ratio`** on the video call; duration is **6 or 10 only** — a 6s clip drops into
  the 5s slot and the overlay clips the last second. Output: `public/<slug>/media/<id>.mp4`.
- **Rebuild the overlay manifest.** After picks/clips land, run
  `assets/templates/rebuild_manifest.sh` — it scans `public/<slug>/media`, prefers a clip
  over a still per beat, and writes `src/media-manifest.json`. (Kept separate so parallel
  shards never race on the manifest.) Then reload Studio / render. The user generates clips/stills, saves them as
  `public/<slug>/media/B07.mp4` (or `.jpg`), and lists delivered files in
  `media-manifest.json`. `BackgroundMedia.tsx` drops each into its slot **under** the wave
  + lyrics; un-generated blocks fall through to the energy gradient, so the project always
  renders. The overlay layers (waveform at the bottom band, lyrics upper-middle with the
  current word highlighted) stay sharp over whatever media is behind them.

Present the plan; ask the user to approve or adjust. **Stop here.** (This is the gate.)

### `build` — generate the Remotion video
Resolve the theme via the precedence chain (hand-written `design/[slug].md` →
`design.json`/`theme.ts` → `default-look.md`). If `design` produced `theme.ts`, the
components already consume it; if a human design doc wins, map its choices into
`theme.ts` (honoring the computed caps). Then generate components from `assets/templates/`:

- `useBeatData.ts` — loads `beat_data.json` + `lyrics.json`, exposes `frame`-indexed
  helpers (`isBeat`, `lastBeatFrame`, `energy`, `sectionAt`, `activeLyric`).
- `AudioVisualizer.tsx` — spectrum **and** waveform components (pick per section per the
  plan), already log-scaled and wrapped in `delayRender`/`continueRender`.
- `BeatLayer.tsx` — beat flashes and spring thuds off the beat frames.
- `LyricLayer.tsx` — renders `lyrics.json`; its animation style comes from the theme so a
  design doc can restyle it without touching timing.
- `MusicVideo.tsx` — the composition: background (energy→color) ▸ visualizer ▸ media
  slots (`<Sequence>` per planned asset; render a labeled placeholder if the file is
  absent so the project still runs) ▸ beat layer ▸ lyric layer ▸ the single `<Audio>`.
- Register in `Root.tsx` with the song's width/height/fps and
  `durationInFrames` from `beat_data.json`.

Honor the gotchas in `references/remotion-audio.md` — power-of-two sample counts, log
scaling, no CSS transitions/animations (use `interpolate`/`spring` only), and the
`startFrom`/`dataOffsetInSeconds` frame-offset corrections. Report the files created
and that the project runs even with media placeholders.

### `render` — handoff (commands only)
Don't render here. Hand the user these, run from the project dir:
```bash
npx remotion studio                                   # preview live, scrub the sync
npx remotion still MusicVideo out/frame.png --frame=N # one-frame sanity check
npx remotion render MusicVideo out/<slug>.mp4         # full render
```
For long/high-res songs, mention `@remotion/lambda` for parallel cloud rendering.

### `publish` — Songbird YouTube metadata
muzak is part of **Songbird** — the project umbrella for the music-video skills
(Claude + CLI tools for music-video production). When a video is render-ready, write
a `youtube.md` in the project with a copy-ready **title** and **description**:

- **Title MUST contain `(Claude Songbird Test)`** while these are early-stage tests,
  e.g. `<Song> — Lyric Video (Claude Songbird Test)`.
- **Description leads with a "this is ONE STEP, not the finished video" caveat** so
  viewers understand the current minimal look (some wav visualization + lyrics) is
  intentional — more visual layers, custom media, and art direction come later.
  Then note it was built with Songbird and how (librosa analysis, Whisper
  forced-aligned lyrics, design inferred from the track), and tag `#Songbird
  #ClaudeSongbird`.

Give the title and description as separate copy-paste blocks.

### `status` — where is this song
Read the project folder and report: WAV present? `beat_data.json` present
(bpm/duration/features)? `lyrics.json` timed (+ density)? `design.json` present and its
semantic fields filled? plan approved? which components built? which planned media files
are still missing? and the next action.

## Core rules

- **Audio-first, always.** `analyze` before anything time-based. Real beat data drives
  every length and cut. Never time animation from BPM guesses or word counts.
- **Phase gates.** Don't cross `plan` without approval. Cheap things first (analysis,
  lyric timing, the plan); spend render compute only once they're accepted.
- **One folder per song**, named by the kebab-case slug. Everything lives inside it.
- **Mostly code, media sparingly.** Generate visuals in Remotion by default; ask for
  custom media only for beats that truly need it, with exact specs.
- **Sync is the point.** If a visual element isn't reacting to the music in some
  legible way, question whether it belongs.
- **Infer the look, then refine it.** Don't ask the user to invent a palette — derive
  it from the song via `design`, then reason the semantic fields from the lyrics. A
  hand-written design doc outranks the inference; computed caps are never raised for drama.
- **Mechanics design-agnostic, look themed.** Pull all aesthetics from one theme object
  generated from `design.json`, so the look is a clean swap.
- **No CSS transitions/animations.** They preview fine and break in headless render.
  Use `interpolate` (opacity/position/color) and `spring` (physical motion) only.

## Output contract

When you stop, report: the **song** (slug, tempo, duration); the **phase reached** and
**files created/changed**; the **visualizer choices** per section; **which media the user
still owes** (with specs) or that it's fully code-generated; the **render command**; and
any unresolved timing or asset gaps. Be explicit that rendering is a command the user
runs — the skill produced a runnable project, not the MP4.
