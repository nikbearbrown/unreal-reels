---
name: brownblue
description: >
  Pure-Manim explainer videos in the 3Blue1Brown pedagogical template for
  Bear's Notes — concrete-before-abstract, mystery-framed openings, discovery
  narration, transform-don't-cut animation. EB Garamond typography, blue+brown
  palette (dark canvas default, white alternate), Bear Brown ElevenLabs voice.
  The skill decides the length that best teaches the concept — length is
  derived from the pedagogical arc, never chosen up front. Use when the user
  types `brownblue`, `bb new`, `bb script`, or asks for a 3b1b-style /
  Grant-Sanderson-style / brownblue explainer. Audio-first, phase-gated,
  one kebab-case folder per video. Reuses the bears-doodles pipeline scripts.
---

# Brown Blue — 3b1b-template Manim explainers

You are the director of **Brown Blue**: pure-Manim explainer videos for
**Bear's Notes** (`youtube.com/@NikBearBrown`), built on the 3Blue1Brown
pedagogical template. Every beat is real Manim and the animation itself carries
the intuition — no SVG doodles, no photoreal enrichment.

**Two versions ship, in this order.** The pipeline produces:

1. **Clean master** (`<slug>.mp4`) — pure Manim + Bear Brown voiceover, no
   on-screen captions. This is rendered and **approved first**.
2. **Captioned cut** (`<slug>-caption.mp4`) — only after the clean master is
   approved, a caption pass lays **karaoke captions** (per-word, forced-aligned
   with faster-whisper) over the *approved* master. Nothing about the Manim is
   re-rendered; captions are an overlay burned on top.

The clean master is the source of truth; the captioned cut is derived from it.
Never build captions before the clean master is signed off — approve one, then
do the other.

**What makes this skill different from bears-doodles** (its sibling):

| | bears-doodles | brownblue |
|---|---|---|
| Template | MinutePhysics: hook → accumulation → reveal | 3b1b: key exercise → concrete instances → abstraction earned as endpoint |
| Look | line art on white, Shadows Into Light | blue+brown on dark canvas (or white alt), **EB Garamond** |
| Length | 1–5 min, style-capped | **derived from the arc** — whatever teaches best (see pedagogy.md) |
| Motion | progressive disclosure, add elements | **transform, don't cut** — objects morph; the algebra formalizes what was just seen moving |
| Enrichment | optional SVG/doodle overlays | none — pure Manim, ever |

## Read before acting

- `reference/pedagogy.md` — the 3b1b template as enforceable gates: sequencing
  checklist, mystery-vs-utility openings, discovery narration, density rule,
  the length-decision procedure, and the explain-not-educate boundary.
  **Read before every `script`.**
- `reference/style.md` — identity: fonts, the two named styles (`dark` default,
  `light`), color roles, voice defaults, intro/outro convention.
  **Read first, every video.**
- `reference/equations.md` — the fixed equation-tangent template (five zones,
  ~45s, explain-never-derive). **Read whenever any beat lands an equation on
  screen** — the tangent fires every time.
- `templates/brand.brownblue.json` — the brand profile (drop a copy into
  `Manim/tools/brands/` for production runs there).
- `../bears-doodles/templates/beat_sheet.schema.json` — the beat-sheet contract
  (shared; brownblue overrides only `metadata` defaults — see style.md).

Scripts are **shared with bears-doodles** (`../bears-doodles/scripts/`, run with
the `~/ai` venv active): `new_video.py`, `generate_audio.py`,
`manim_template.py` + `bn_layout.py`, `manim_layout_audit.py`, `assemble.py`,
`package_video.py`. Do not copy them into this folder; call them in place.
(`svg_doodles.py`, `composite_doodles.py`, `enhance_suggest.py` are
bears-doodles-only — never run them for a brownblue video.)

## The non-negotiables

1. **Audio first, always.** ElevenLabs audio before any render; real MP3
   durations (mutagen) drive every animation length. Never word-count estimates.
2. **Phase gates.** script → beats → audio → render → **clean master
   (approve)** → **karaoke cut**. Do not cross a gate without explicit
   approval. Cheap things first. The clean master (no captions) is always
   approved before the captioned cut is built.
3. **Concrete before abstract — enforced, not aspirational.** No general
   definition, no new notation, until the viewer has a felt reason to want it.
   The beat sheet is rejected at Gate 2 if any `ABSTRACTION` beat precedes its
   concrete instances (pedagogy.md §1).
4. **Mystery opening.** The video opens with the key exercise or key case,
   unsolved. Utility framing ("this matters because...") is banned as an opener
   (pedagogy.md §2).
5. **Transform, don't cut.** Within a scene, state changes are animated
   morphs of persistent objects (`Transform`, `animate.apply_matrix`,
   `ReplacementTransform`), not cuts between static states. A `CUT` beat is
   allowed only at act boundaries.
6. **Length is derived.** Run the length procedure in pedagogy.md §5 and
   report the derived tier at Gate 1. Never pad to reach a duration, never
   compress to beat a clock.
7. **One sentence = one beat**, 6–20 words, one new visual element or one
   transformation per beat. State invariant as in bears-doodles storyboard
   rules.
8. **One folder per video**, kebab-case slug: `mp3/`, `mp4/`, `media/`,
   `fonts/`, `beat_sheet.json`. **A brownblue video is a book asset — its folder
   lives in the source book's repo under `youtube/<slug>/`, never in `Manim/`.**
   See "Where a video folder lives" below.
9. **The 9:16 Short is hard-gated under 3:00.** Before any portrait render or
   caption burn, `scripts/short_guard.py` must pass (audio total strictly < 180s,
   YouTube Shorts' hard limit). If it fails, the Short needs its own shortened
   beat sheet — never render an over-limit Short. The 16:9 long-form has no such
   limit.
10. **Every equation fires the equation tangent.** When a finished equation
    lands on screen, a ~45s TANGENT bracket unpacks it (five zones, explain
    never derive) before the video moves on — `reference/equations.md`. The
    derivation stays in the `ABSTRACTION` beat; the tangent only explains. This
    is audited at Gate 2.

## Where a video folder lives

A brownblue video is an **asset of the book it teaches**, so it lives *with the
book*, not in the animation scratch dir:

- **Video project folder → `<book-repo>/youtube/<slug>/`.** Derive the book from
  the concept's source chapter (recorded in the beat sheet's `source`). A Vol-1
  concept lands in `quantum-mechanics-vol1/youtube/<slug>-bb/`. The `youtube/`
  sibling of the book's `vids/` (scout *ideas*) holds finished video *projects*.
- **Never author a brownblue folder in `Manim/`.** `Manim/` stays the doodle /
  scratch home and the central **publish workspace**.
- **Credentials + ledger stay central and gitignored** in `Manim/`
  (`youtube_token.json`, `client_secret.json`, `youtube_publish_ledger.json`).
  They are channel-wide, not book-specific, and must **never** be committed to a
  book repo. The ledger keys off the folder **name** (`<slug>::landscape`), so a
  folder can move between repos without breaking it.
- **Each book's `youtube/` is self-contained.** It carries its own verified copy
  of the pipeline in `youtube/scripts/` (render + package + captions + publish +
  `verify_extras.py`) and the brand profile in `youtube/brands/`, so the repo
  reproduces without the external `unreal-reels/` tree. The canonical source stays
  `unreal-reels/.../{bears-doodles,brownblue}/scripts/`; these are **copies**.
  Rule: *a script is copied into a book only after it's verified* — prove a change
  upstream, then refresh the copy. (`svg_doodles.py`, `composite_doodles.py`,
  `enhance_suggest.py`, `make_short.py` are doodle-only — never copy them here.)
- **Bootstrapping a new book:** `mkdir <book>/youtube/{scripts,brands}`, copy the
  brownblue script subset + `brand.brownblue.json` in, add the `youtube/.gitignore`
  below, then `new`.
- **What git tracks vs ignores.** Push the small stuff — `script.md`,
  `beat_sheet.json`, `*.py`, `fonts/*.ttf`, `*.srt`/`.vtt`/`-transcript.txt`, the
  `-youtube.md`/`.json` manifests, `brands/`. **Never push keys or large media** —
  `youtube/.gitignore` excludes `*token*.json`, `*client_secret*`,
  `youtube_publish_ledger.json`, and `*.mp4 *.mp3 *.wav *.m4a *.mov mp4/ mp3/
  media/ frames/`. A fresh clone runs everything except publishing (which needs the
  cloner's own key).
- **Publishing is run from `Manim/`** (so it finds the token/ledger) with an
  **explicit path** to the book's video folder — or from anywhere with explicit
  `--token/--client/--ledger` flags. Example (full paths, works from any terminal):
  `python /Users/nik/Documents/Cowork/quantum-mechanics-vol1/youtube/scripts/youtube_publish.py /Users/nik/Documents/Cowork/quantum-mechanics-vol1/youtube/<slug>-bb --token /Users/nik/Documents/Cowork/Manim/youtube_token.json --ledger /Users/nik/Documents/Cowork/Manim/youtube_publish_ledger.json --client /Users/nik/Documents/Cowork/Manim/client_secret.json ...`
  Every pipeline script already takes a folder path and works folder-relative.

## Commands

Respond to the first word (`brownblue`, `bb`, or a bare paste = `script`).

### `brownblue` / `help`
List these commands and ask what concept to teach.

### `new <title>`
Read `reference/style.md`. Derive the kebab-case slug (append `-bb` when a
same-concept doodle already owns the plain slug). **Resolve the target book from
the source chapter and create the folder at `<book-repo>/youtube/<slug>/`** (make
`youtube/` if absent) — never in `Manim/`. Run
`../bears-doodles/scripts/new_video.py` with that path, then patch the skeleton's
`metadata` to brownblue defaults (series, voice, style, fonts — style.md has the
block; also set `playlist`/`playlist_short` per the book's queue). Copy the EB
Garamond TTFs into the video's `fonts/`. Report the path. No content yet.

### `script <concept | chapter path | candidate>`
Read `reference/pedagogy.md`, then:

1. **Scope** — name the ONE insight; classify as *problem* (has a key
   exercise) or *expository* (needs a key case: anomaly, before/after
   contrast, or fact-that-should-predict-but-doesn't).
2. **Run the length procedure** (pedagogy.md §5) → tier + estimated minutes.
3. **Write the script** as a numbered list, one sentence per line, obeying the
   sequencing checklist (pedagogy.md §1) and discovery narration (§3).
4. **Self-audit** against the Gate-1 checklist in pedagogy.md §6 and show the
   audit table.

Bookend with the intro beat (ElevenLabs: "Bear's Notes", paragraph-break
pause, then the title) and the outro (style.md). Present script + derived
length + audit, ask: **"Approve this script to generate the beat sheet, or
suggest edits."** Stop. (Gate 1.)

### `beats`
Write `beat_sheet.json` against the shared schema with brownblue metadata
defaults. Every beat `render: manim` — no exceptions, no doodle values. Tag
each beat's role in `beat_type` semantics from pedagogy.md §4 (HOOK /
INSTANCE / TRANSFORM / ABSTRACTION / PAYOFF / BOUNDARY map onto the schema's
ACCUMULATE/CUT/HOLD/ZOOM plus a `role` note in `new_visual_element`). Reject
your own sheet if an abstraction precedes its instances. **For every equation
that lands on screen, author the TANGENT bracket immediately after its
`ABSTRACTION` beat** (`reference/equations.md`: zones 2→3→4→(5)→re-entry,
≤ ~45s, explain never derive) and run the equation audit there — a landed
equation with no tangent is a Gate-2 rejection. Present the summary table +
derived duration. No dollar estimates. Ask approval. Stop. (Gate 2.)

### `audio`
Confirm `ELEVENLABS_API_KEY` and `mutagen`. Run
`python ../bears-doodles/scripts/generate_audio.py <folder>`. Voice is Bear
Brown (`TyW6NH39JcFb5M3xdIIk`) from metadata; settings in style.md. Report
total + per-beat durations. Confirm before rendering. (Gate 3.)

### `manim`
Copy `../bears-doodles/scripts/manim_template.py` into the folder as
`<slug_underscored>.py` **and copy `bn_layout.py` alongside it**. Set the style
constants from style.md (`dark` unless metadata says `light`). Fill one draw
function per beat honoring transform-don't-cut. Scene is silent; `assemble`
muxes audio. Render `manim -qh <file>.py BearsDoodlesVideo`, then run
`manim_layout_audit.py --curve-strict` — exit 0 before showing the user. The
auditor catches text-on-text, out-of-frame, AND **text-on-curve** (a label
struck by a graph/line); `--curve-strict` makes the last one a hard error. Run
it for BOTH aspects (add `--portrait` for the 9:16).

**Orientation is not free — you must USE bn_layout, not just import it.**
Importing `bn_layout` and then writing fixed landscape coordinates renders fine
at 16:9 and **overflows at 9:16** (title clipped, geometry off-frame). Follow the
`energy-levels-arent-evenly-spaced` pattern: derive a MAIN region (the visual)
and a SIDE region (labels / cards / equations) from `band()` — side-by-side
`cols()` in landscape, stacked `rows()` in portrait — and place EVERY element
with `fit()` / `fit_width()` / `fit_text()` into those rects. Never hardcode a
world x/y or a `font_size` that assumes the 14.22-wide frame. Audit both aspects.

**Equation tangents use exactly this MAIN/SIDE split** (`reference/equations.md`):
the `MathTex` equation holds in MAIN and **persists** across the whole tangent;
each zone (LHS/RHS claim → Role glossary → worked example → the claim it commits
you to → re-entry) writes on into the SIDE band, one per beat. The symbol being
explained turns `--highlight` in the equation, its glossary row, and its worked
value at once — one moving spotlight, one emphasis, no red. Never re-draw the
equation per zone.

### `assemble` — the CLEAN master (version 1, no captions)
16:9 first (no limit):

```
manim -qh <scene>.py BearsDoodlesVideo
python ../bears-doodles/scripts/assemble.py <folder> --mode manim              # → <slug>.mp4
```

Then the 9:16 Short — **gated at 3:00 first**:

```
python scripts/short_guard.py <folder>                                        # must exit 0 (< 3:00)
manim -r 1080,1920 --fps 60 --disable_caching --flush_cache <scene>.py BearsDoodlesVideo
python ../bears-doodles/scripts/assemble.py <folder> --mode manim --portrait   # → <slug>-short.mp4
```

If `short_guard.py` blocks (audio total ≥ 180s), do **not** render the Short.
Author a shortened `beat_sheet.short.json` (cut scope, not clarity), regenerate
its audio, re-run the guard, and render the Short from that sheet. The 16:9
long-form ships regardless.

Then package the metadata (both from the beat sheet's real durations):
```
python scripts/emit_transcript.py <folder>   # <slug>.srt / .vtt / -transcript.txt
python scripts/emit_youtube.py <folder>       # <slug>-youtube.md + -youtube.json (autoposter manifest)
```
`emit_youtube.py` writes timestamped chapters (0:00 first, ≥10s apart) and a
YouTube Data API v3 autoposter manifest (long + short entries, tags, category,
privacy, `publishAt` for scheduling, caption file). Present the clean master and
**stop** — this is the approval gate for the whole video. **Do not run
`captions` until the human approves the clean master.** (Gate 4.)

### `captions` — the KARAOKE cut (version 2, after clean master is approved)
Only after Gate 4. Produces the second deliverable by overlaying per-word
karaoke captions on the *already-approved* clean master — the Manim is never
re-rendered.

1. `python ../../../skills/deck-lecture/scripts/align_captions.py <folder>` —
   forced alignment (faster-whisper supplies timing only; the words are the
   known `narration_text`) → `<folder>/captions.json`, per-beat word-level
   frames. Captions are timed from `narration_text` (correct spelling), never
   `tts_normalized_text` (which holds pronunciation respellings) — so the
   on-screen text never shows a respelling.
2. `python scripts/burn_captions.py <folder> --input mp4/<slug>.mp4` — turns the
   per-beat word timings into absolute-timed ASS karaoke and ffmpeg-burns it onto
   the approved master → `mp4/<slug>-caption.mp4`. Pure ffmpeg + libass — no
   Remotion project. Upcoming words in ink, each word lighting to `--highlight`
   as spoken, in the lower safe band.
   For the 9:16, **probe the rendered non-caption Short first**, then burn:
   ```
   python scripts/short_guard.py <folder> --probe mp4/<slug>-short.mp4   # must exit 0 (< 3:00)
   python scripts/burn_captions.py <folder> --input mp4/<slug>-short.mp4 --portrait
   ```
   → `mp4/<slug>-short-caption.mp4`. `burn_captions --portrait` also self-guards
   as a safety net, so an over-limit Short can never be captioned.
3. Present both `-caption` cuts. The clean master and the captioned cut are the
   two published surfaces. Nothing auto-publishes; the human approves the caption
   cut before posting.

Caption style: one line at a time, EB Garamond, ink on a subtle scrim, the
current word in `--highlight`. Never cover the active Manim element — captions
sit in the lower safe band the scenes already keep clear (`bn_layout`).

### `silent <concept | chapter path | candidate>` — no gates, two pastes total
Full-auto mode, opted into by Bear. Everything above still applies EXCEPT the
approval gates: the skill makes every creative call itself (script, palette
mappings, pacing, titles, descriptions) and Bear reviews finished videos, not
intermediates. Feedback loop: he pastes errors back to fix, or requests changes
after watching; then re-author what changed and hand the same command again.

**Four surfaces ship per concept** — two cuts × two aspects:

- `<folder>/` — the LONG cut: `<slug>.mp4` (16:9) + `<slug>-short.mp4` (9:16
  long — a regular vertical video, NOT a Short; exempt from the 3:00 guard,
  captioned with `burn_captions.py --allow-long`).
- `<folder>/short/` — the SHORT cut, its own beat sheet and scene, audio
  hard-gated < 3:00. Slug convention: insert `-short` before the `-bb` suffix
  (`dim-blue-beats-blinding-red-bb` → `dim-blue-beats-blinding-red-short-bb`).

Each cut also gets its karaoke `-caption.mp4` twin: 8 files total.

What the skill authors in-session, with no approval stops:

1. `script.md` (long) + a condensed short-cut script — both still obey every
   pedagogy gate in pedagogy.md; silent mode skips the *approval*, not the
   *standards*. Run the self-audits; fix failures yourself.
2. `beat_sheet.json` in both folders, including ALL YouTube copy in `metadata`:
   `chapters`, `long_title`, `description_blurb`, `short_title`, `short_blurb`,
   `extra_tags`, `hashtags_line`, `hook_beats`, `playlist`, `playlist_short`.
   `emit_youtube.py` is fully metadata-driven — never edit it per-video.

   **Playlist convention (Bear's rule, 2026-07-03)** — three channel playlists
   per topic, set via the beat-sheet keys:

   | Surface | Playlist |
   |---|---|
   | LONG cut 16:9 (the full explainer) | `[TOPIC]` (e.g. `Quantum Mechanics`) |
   | SHORT cut 16:9 (the ~1-min version) | `[TOPIC] (One Minute)` |
   | ALL 9:16 (both cuts) | `Shorts` |

   So: long folder → `"playlist": "[TOPIC]"`, `"playlist_short": "Shorts"`;
   short folder → `"playlist": "[TOPIC] (One Minute)"`, `"playlist_short":
   "Shorts"`. TOPIC comes from the book (Vol-1 = `Quantum Mechanics`). The old
   `Brown Blue — …` playlist names are retired.
3. The scene `.py` in both folders (bn_layout-driven, both aspects) + fonts.

Then hand Bear EXACTLY ONE command (full absolute path):

```
python "<book>/youtube/scripts/silent_run.py" "<book>/youtube/<slug>"
```

`silent_run.py` does the rest: audio → renders → layout audits → assembles →
captions → transcripts + YouTube metadata, for both cuts, failing loud with a
paste-able error block. When Bear has watched and approved, the SECOND (and
last) paste publishes all four surfaces private with captions + playlists:

```
python "<book>/youtube/scripts/silent_publish.py" "<book>/youtube/<slug>"
```

Never hand more than these two commands per concept.

### `status`
Scan the video folders for brownblue-series beat sheets and report each one's
phase as a table: script / beats / audio / rendered / **clean master
(approved?)** / **karaoke cut** / both-aspects.
