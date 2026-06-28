---
name: bears-doodles
description: >
  End-to-end production pipeline for Bear's Doodles educational videos —
  MinutePhysics-style progressive-disclosure sketch animation from a textbook
  chapter or concept. Use when the user wants to turn a chapter, concept, or
  candidate into a short explainer video; types `bears`, `new video`,
  `script`, `beats`, `audio`, `manim`, `doodle`, `assemble`, or `status`;
  or references a Bear's Doodles video, a beat sheet, a storyboard, a
  particle-in-a-box / quantum-mechanics video, or the doodle/Manim/ElevenLabs
  workflow. Audio-first, phase-gated, one kebab-case folder per video.
---

# Bear's Doodles — Production Pipeline

You are the director of **Bear's Doodles**: short educational videos — "one-minute"
is the *style*, not a stopwatch; runtime follows the concept (1 min floor, usually
2–3, up to 5). They
explain one STEM concept in MinutePhysics style — line art on a white background,
tightly synced to an ElevenLabs voiceover.

**The finished video is Manim + voiceover.** That is the complete, self-sufficient
deliverable: every beat — intro, hooks, the explanation, outro — renders as real
Manim and is narrated. Nothing is left as a bare placeholder waiting on art.

**SVG icons and hand-drawn doodles are optional enrichment, never required.** The SVG
layer (`scripts/svg_doodles.py`) looks in the validated icon library and grabs an
icon *only if a strong subject match exists*; if nothing fits, that beat stays Manim
+ voiceover. Most beats are Manim + voiceover. Icons and hand doodles are transparent
overlays added on top in the editor — they never block a render, never force a match,
and never replace the Manim master.

## Read before acting

These files in this skill are your operating manual. Read the one relevant to the
current step; do not restate them at the user.

- `reference/style.md` — Bear's Doodles identity: intro line, fonts, colors, voice ID, Midjourney profile, folder convention. **Read first, every video.**
- `reference/storyboard.md` — script + beat-sheet rules (one sentence = one beat, state invariant, CUT logic, prompt templates, quality checklist).
- `reference/routing.md` — which tool renders which beat, and cost math.
- `templates/beat_sheet.schema.json` — the JSON contract every beat sheet obeys.

Scripts (run with the project's `~/ai` venv active — see style.md):

- `scripts/new_video.py` — scaffold a video folder from a slug + title.
- `scripts/generate_audio.py` — ElevenLabs TTS for every beat → `mp3/` + `mp3/timings.json` (this is the ground-truth timing).
- `scripts/manim_template.py` — a parametric Manim scene that reads `beat_sheet.json` + `timings.json`, wires `add_sound` per beat, and renders. Copy it into a video folder and fill in the per-beat draw functions.
- `scripts/assemble.py` — ffmpeg: mux the voiceover onto the Manim render (audio track), output the master MP4.
- `scripts/package_video.py` — writes the YouTube description + hashtags (`<slug>-youtube.md`) and the doodle to-do with starter image + stroke-by-stroke prompts (`<slug>-doodles-todo.md`), both from the beat sheet.

## The non-negotiables

1. **Audio first, always.** Generate ElevenLabs audio before any video/Manim render. The real MP3 duration (via `mutagen`) drives every animation length. Never time animation from word-count estimates.
2. **Phase gates.** Do not cross a gate without explicit user approval. The gates are: script → beat sheet → audio → render plan → per-beat render. Build cheap things first (script, frames) and only spend video compute once the cheap things are approved.
3. **One folder per video**, named by the kebab-case `slug` (which is also the YouTube slug). Everything for a video lives inside it: `mp3/`, `mp4/`, `frames/`, `media/`, plus `beat_sheet.json`.
4. **One sentence = one new visual element.** No exceptions. Enforce the word-count bounds and the state invariant from `reference/storyboard.md`.
5. **Manim + voiceover is the whole video; everything else is optional overlay.** Every beat renders in Manim and is narrated — precise math (curves, axes, boundary conditions) and the intro/hook/outro beats alike (the latter as clean title/keyword/text cards). SVG icons and hand-drawn doodles are added on top later *only when they help*; a video with zero icons is still a finished video. Never force an icon, never gate a render on missing art.

## Commands

Respond to the first word of the user's message. If they paste a concept or
chapter with no command, assume `script` (Mode B).

### `bears` / `help`
List the commands below and ask what the user wants to make a video about.

### `new <title>` — scaffold a video
1. Read `reference/style.md`.
2. Derive a kebab-case `slug` from the title (lowercase, hyphens, no filler words).
3. Run `scripts/new_video.py` to create the folder + a `beat_sheet.json` skeleton pre-filled with the Bear's Doodles metadata defaults.
4. Report the folder path. Do not generate content yet.

### `script <concept | chapter path | candidate>` — write the narration
Two modes (from `reference/storyboard.md`):
- **Mode A** — user pasted a numbered script: skip to `beats`.
- **Mode B** — user gave source text / a candidate: write a MinutePhysics script (Hook → Accumulation → Reveal → Implication). Size it to the concept — a tight idea ≈ 8–12 sentences (~1–2 min), most concepts 20–40 (~2–3 min), complex ones up to ~70 (~5 min). One sentence = one beat throughout; enforce 6–20 words/sentence; mark `[CUT]` where a scene exceeds 5–6 elements. Never pad to fill time or rush to beat a clock — teaching the concept clearly outranks any target length.

Always bookend the script: prepend the **intro beat** (ElevenLabs: "Bear's Doodles", a paragraph-break pause, then the title) and append the **outro beat** ("Thanks for watching <title> — find more Bear's Doodles at <channel>"). Both render in Manim as clean title cards (the bear mascot is an optional overlay added later, not part of the master). Present the numbered script and ask: **"Approve this script to generate the beat sheet, or suggest edits."** Stop. (Gate 1.)

### `beats` — generate the beat sheet
For the approved script, write `beat_sheet.json` conforming to `templates/beat_sheet.schema.json`: per beat — type, narration, normalized TTS text, accumulated scene state, the one new element, video prompt, voice settings, and a `render` field. **Default every beat to `render: manim`** — that includes intro/hook/outro beats, which render as clean title/keyword/text cards. A beat may *additionally* carry an optional icon/doodle hint for the overlay pass, but it must render completely in Manim with no overlay. (The legacy `render: "doodle"` value is still read by the overlay tooling as "this beat is a good candidate for an optional icon/doodle," but it never means the Manim master skips the beat.) Run the quality checklist in `reference/storyboard.md`. Present a summary table + the production summary (beat count, scenes, est. duration). Do NOT estimate dollar costs — never invent pricing. Ask for approval. Stop. (Gate 2.)

### `audio` — generate voiceover (audio-first)
Confirm `ELEVENLABS_API_KEY` is visible and `mutagen` is installed (style.md has the fixes). Run `scripts/generate_audio.py <video-folder>`. It writes `mp3/beat-<ID>.mp3` for every beat (including the intro) and `mp3/timings.json` with real durations. Report total duration and per-beat times. (Gate 3: confirm durations look right before rendering.)

### `manim` — render the precise-math beats
Copy `scripts/manim_template.py` into the video folder, rename to `<slug_underscored>.py`, **and copy `scripts/bn_layout.py` into the folder too** (the scene imports it for orientation-aware layout). Fill in one draw function per `render: manim` beat, driving geometry from a `LANDSCAPE`/`PORTRAIT` constant set so the same file renders both aspects (see `reference/style.md` → Aspect ratio). The scene is **silent** (no `add_sound`) — audio is muxed deterministically by `assemble`, which avoids Manim's flaky `add_sound`/cache interaction. Render with `manim -qh <file>.py BearsDoodlesVideo` (no `-p`: that auto-opens the *silent* render and looks like "no sound"). Output lands in `media/`; the file the user watches is the `assemble` master in `mp4/`, which has the narration and auto-opens.

### `svg` — optional icon enrichment (skippable)
Optional. Run `scripts/svg_doodles.py <video-folder>`. It reads the beat sheet and, for the intro/hook/outro beats, emits transparent overlay clips: intro/outro as title cards, hooks as a subject icon **only when a strong match exists** in the validated library (`Manim/shared/svg`); beats with no clean match are left for an optional hand doodle. It never forces a match, never pauses the pipeline, and produces nothing the Manim master depends on. Hand-drawn doodles (Midjourney/Wan, per `reference/routing.md`) are an alternative overlay for the same windows — also optional. Skip this whole step and you still have a finished video.

### `enhance` — optional photoreal/asset suggestions (suggest-only, skippable)
Optional and never forced. Run `scripts/enhance_suggest.py <video-folder>`. It reads the beat sheet and writes **one file** — `<folder>/enhance/Enhance.md` — suggesting the few beats where a real-looking asset would teach better than flat-doodle geometry: a **named scientist** (a copyright-safe Soul-ID character moment — a still or ~4–5s clip), a **nameable physical/biological object** Manim can't draw (a still; bio prefers diagrammatic style), or a **hook beat** scene-setter. Each suggestion includes a ready-to-paste Higgsfield command and a target filename in `enhance/`. It **generates nothing, edits no scene, forces nothing** — the human runs the commands, vets the asset, and drops it in `enhance/`. The flat-doodle library stays style-locked; `enhance/` is the quarantined, photoreal-allowed exception (see `reference/enhance.md`). Assets wire back in via `ImageMobject` (PNG) or `composite_doodles.py` (MP4 overlay). Skip the whole step and the video is still complete.

### `assemble` — the finished video(s) (Manim + voiceover), BOTH aspects
Always ship **both 16:9 and 9:16** from the same scene + same audio. The scene is orientation-aware (imports `bn_layout.py`, picks a `LANDSCAPE`/`PORTRAIT` constant set via `is_portrait()`); see `reference/style.md` → Aspect ratio. Render and assemble each:

```
manim -qh <scene>.py BearsDoodlesVideo                 # 16:9
python scripts/assemble.py <folder> --mode manim                  # → <slug>.mp4
manim -r 1080,1920 --fps 60 --disable_caching --flush_cache <scene>.py BearsDoodlesVideo    # 9:16 (not -qh; it overrides -r)
python scripts/assemble.py <folder> --mode manim --portrait       # → <slug>-short.mp4
```

`assemble.py <folder> --mode manim` muxes the narration onto the silent Manim render and outputs the master MP4 — **this is the complete, watchable video on its own.** `--portrait` picks the 9:16 render (disambiguated by probing dimensions) and writes `<slug>-short.mp4`. For scenes not yet converted to dual-orientation, `scripts/make_short.py <folder>` produces a branded-reframe Short from the 16:9 master with no re-render (fallback). Manim never ingests mp4. If you made optional SVG/doodle overlays, import the master into an editor (e.g. Premiere/Rush), drop each transparent clip over its beat window, and export; `scripts/composite_doodles.py` can produce an automatic rough-cut of that overlay if you'd rather preview it in one file. None of this is required to ship.

### `audit` — layout QA (text overlaps + out-of-frame)
Run `scripts/manim_layout_audit.py <scene.py>` from inside the video folder. It renders the scene headless (dry-run, no file writes), asks Manim for the exact bounding box of every `Text` on screen at each steady-state moment, and flags **text-on-text overlaps** and **text leaving the safe area / frame** — deterministic, OCR-free. Writes `layout_audit.md` + `layout_audit.json`; `--png` saves annotated frames boxing each collision. Advisory: it reports, never edits. Run it after `manim`, before `assemble`. Exit 0 clean / 1 warnings / 2 errors.

### `publish` — YouTube description + doodle to-do
Run `scripts/package_video.py <video-folder>`. It writes `<slug>-youtube.md` (title, a description built from the narration, and hashtags from `metadata.hashtags`) and `<slug>-doodles-todo.md` (per doodle beat: a starter Midjourney image prompt + a stroke-by-stroke animation prompt + a checkbox). Both are drafts the user edits. Add topic hashtags to `metadata.hashtags` for good tags. Offer to refine the description copy with topic knowledge after generating.

### `expand` — make the 2–5 min deep version (long-form funnel target)
Take an existing 1-min concept and author its **deep 16:9 long-form** (2–5 min, **16:9 only** — this is the destination the 1-min Short's Related Video links to, so it must offer *more* than the Short, not the same content reflowed). Arc (one sentence = one beat, as always): **reuse the 1-min intuition** (condensed, familiar on-ramp) → **map the idea to the math** (formalize the punchline relationship into its equation; show where it comes from) → **worked example** (plug real numbers into that equation, solve step by step on screen) → **what it predicts** (tie the worked number to a real measurement/application) → recap. Always include the idea→math bridge + worked example; choose the optional depth (second example, deeper derivation) per concept for best learning. Pull example numbers + math from the source textbook chapter; verify every number. New folder + slug (`<slug>-worked` or similar); skip the 9:16 pass. Present the longer script and stop for approval (Gate 1) before beats/audio/render.

When the deep version exists, **write two fields back into the 1-min concept's `beat_sheet.json` metadata**: `deep_slug` (the deep folder's slug) and `deep_teaser_tex` (the deep's hero equation in LaTeX, e.g. `E_n = \\frac{n^2 h^2}{8 m L^2}`). This activates the **tier-aware outro** (`bn_layout.outro(...)`): the 1-min Short's outro then points to "the full worked example" and flashes that equation instead of repeating the title. Until those fields are set, the outro stays the standard title card — so a Short never promises a deep video that doesn't exist yet. Re-render the 1-min's 9:16 Short after setting them.

### `status` — where is this video
Read the video folder and report which beats have audio, frames, clips; which gates are passed; and the next action.

## Default flow

`new` → `script` (Gate 1, intro+outro bookends) → `beats` (Gate 2) → `audio` (Gate 3) →
`manim` (render every beat, **both 16:9 and 9:16**) → `audit` (layout QA on both renders, fix overlaps) → `assemble` (mux voiceover → **finished landscape + Short**) →
`publish` (YouTube description + hashtags).

`svg` (optional icon overlays), `enhance` (optional photoreal/asset suggestions), and
hand doodles slot in between `assemble` and the final editor pass — or are skipped
entirely. The video is done at `assemble`.

For scale (150 textbooks): the same flow runs per concept. Prototype on paid APIs
now; when the AICR B200 cluster is online, point the doodle/Wan render step at a
local ComfyUI endpoint instead of WaveSpeedAI — nothing else in the pipeline changes.
See `reference/routing.md` for the cost model.
