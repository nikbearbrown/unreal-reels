# Codex brief — build Bear's Notes explainer videos to house standard

You are building short MinutePhysics-style explainer videos from open-access STEM
textbooks, on an existing pipeline called **bears-doodles** (brand name on screen:
**Bear's Notes**). Another agent already built ~24 of these to a fixed standard;
your job is to produce videos **indistinguishable from those** in structure, style,
and file layout. Match the contract below exactly. When in doubt, copy an existing
finished video rather than inventing.

---

## 0. Orient yourself first (do this before writing anything)

The canonical pipeline lives in the Cowork repo:

- `~/Documents/Cowork/bears-doodles/SKILL.md` — the orchestrator (commands + gates + non-negotiables)
- `~/Documents/Cowork/bears-doodles/reference/style.md` — house style (colors, font, voice, safe area)
- `~/Documents/Cowork/bears-doodles/reference/storyboard.md` — beat/quality checklist
- `~/Documents/Cowork/bears-doodles/scripts/` — the scripts you will run:
  `generate_audio.py`, `manim_template.py`, `assemble.py`, `manim_layout_audit.py`,
  `package_video.py`, `svg_doodles.py` (optional), `new_video.py`
- `~/Documents/Cowork/bears-doodles/templates/beat_sheet.schema.json` — beat sheet schema

Gold reference video (study it before building — scene + beat sheet + script):
`~/Documents/Cowork/Manim/energy-levels-arent-evenly-spaced/`
(`energy_levels_arent_evenly_spaced.py`, `beat_sheet.json`, `script.md`)

Your repo already has one finished video to pattern-match against:
`~/Documents/Cowork/Codex/Manim/why-particle-in-box-cannot-sit-still/`

**If your sandbox cannot read `~/Documents/Cowork/`**, stop and ask the user to
either (a) widen access to that folder, or (b) copy `bears-doodles/` (SKILL.md +
reference/ + scripts/ + templates/) into your repo. Do not reimplement the scripts
from scratch — they encode details (audio muxing, freeze-frame tail, layout audit)
that must stay identical.

New videos you build go in **`~/Documents/Cowork/Codex/Manim/<slug>/`**, one
kebab-case folder per video. The validated SVG library and fonts are shared at
`~/Documents/Cowork/Codex/Manim/shared/` (font TTF:
`shared/fonts/ShadowsIntoLight-Regular.ttf` — install it so Manim resolves the font).

---

## 1. The non-negotiables (do not violate these)

1. **Audio first, always.** Generate the ElevenLabs narration before any Manim
   render. Real MP3 durations (read via `mutagen`) drive every animation length.
   Never time animation from word-count guesses.
2. **Phase gates — stop for approval.** The gates are: **script → beat sheet →
   audio → render → assemble**. Build the cheap artifacts first and only spend
   render compute after the cheap ones are approved. Present and STOP at each gate.
3. **Manim + voiceover is the entire video.** Every beat — including intro, hooks,
   and outro — renders completely in Manim and is narrated. There are **no
   placeholder boxes** and nothing the master depends on outside Manim. SVG icons
   and hand-drawn doodles are *optional* overlays added later in an editor; a video
   with zero icons is still finished. Never force an icon, never gate a render on
   missing art.
4. **The scene class is always `class BearsDoodlesVideo(Scene)`** — this name is
   plumbing the scripts depend on. Keep it exactly, in every video. The file is
   `<slug_with_underscores>.py`.
5. **The scene is SILENT** — no `add_sound`. `assemble.py` muxes the narration
   deterministically (Manim's `add_sound` is flaky with caching). Render with
   `manim -qh <file>.py BearsDoodlesVideo` (no `-p`; `-p` auto-opens the silent
   render and looks like "no sound").

---

## 2. House style (match exactly)

- **Background:** white. **Aspect:** 16:9 (1920×1080) by default.
- **Font (all non-math text):** `Shadows Into Light`.
- **Colors:**
  - Ink (all primary line art): `#1a1a1a`
  - Accent (the one pedagogical element per scene — the key curve/wave): Warm Slate `#5A5653`
  - Forbidden (barriers, "not allowed" states, final emphasis): Red `#C0392B` — **never override**, red = forbidden is consistent series grammar
  - Ghost (faint guides): `#C9BFBC`
- **Safe area:** keep ALL content inside ~8% inset. Define usable half-extents
  `SAFE_W, SAFE_H = 6.3, 3.4` and position every label/plot inside them. Never
  `to_edge()` flush to the border. Give gutters between panels room too.
- **Voice (ElevenLabs):** voice id ``, model
  `eleven_multilingual_v2`, stability `0.80`, similarity_boost `0.75`, style `0.00`,
  speed `0.92`, output `mp3_44100_128`. (Overridable only via `metadata.voice_id`.)

---

## 3. The mandatory intro / hook / outro treatment

- **INTRO = an infographic title card, not bare text.** Three stacked elements on
  white: the brand `Bear's Notes` (top), a **Manim hero graphic that visually
  matches the video's title** (center — the video's own motif, e.g. a blackbody
  curve, an energy ladder, a wave packet), and the title in Shadows Into Light
  (bottom, inside the safe area). Implement it as an `_intro_hero()` method (or
  inline) that draws the topic motif. The bear mascot is NOT in the master — it is
  an optional overlay added later.
- **HOOKS draw something.** Each hook beat renders its narration AND a small topic
  sketch — never a plain text card alone.
- **OUTRO = a SEPARATE clean card.** Clear the canvas first
  (`if self.mobjects: self.play(FadeOut(*self.mobjects))`), then draw, centered and
  inside the safe area: `Thanks for watching` + the title + `youtube.com/@NikBearBrown`.
  Never draw the outro on top of the last animation frame.

---

## 4. Workflow (run per video)

Activate the project venv first (`ai`). Then:

1. **Pick a candidate.** Read `<book>/vids/video-ideas.md` and take an approved
   `Candidate NN` card. One clean tension + one clean resolution.
2. **`script`** — write a MinutePhysics arc (Hook → Accumulation → Reveal →
   Implication). One sentence = one beat, 6–20 words each. Size to the concept
   (tight idea ≈ 8–12 sentences; most 20–40; complex up to ~70). Prepend the intro
   beat and append the outro beat. Save `script.md`. **Present numbered + STOP (Gate 1).**
3. **`beats`** — write `beat_sheet.json` to the schema. Every beat defaults to
   `render: manim` (intro/hooks/outro included). `metadata.series = "Bears Notes"`,
   channel `youtube.com/@NikBearBrown`. Run the storyboard checklist. Present a beat
   table + production summary (beat count, scenes, est. duration). **Do NOT invent
   dollar costs.** **STOP (Gate 2).**
4. **`audio`** — confirm `ELEVENLABS_API_KEY` is set and `mutagen` installed; run
   `generate_audio.py <folder>`. Writes `mp3/beat-<ID>.mp3` + `mp3/timings.json`.
   Report durations. **STOP (Gate 3).**
5. **`manim`** — copy `manim_template.py` into the folder as `<slug>.py`, fill one
   draw function per beat, with the intro hero / hook sketches / standalone outro
   from §3. Render `manim -qh <slug>.py BearsDoodlesVideo`.
6. **`audit`** — run `manim_layout_audit.py <slug>.py` from inside the folder. It
   flags text-on-text overlaps and out-of-safe-area text deterministically. Fix
   every ERROR and review WARNINGS before assembling. (`--png` boxes each collision.)
7. **`assemble`** — `assemble.py <folder> --mode manim`. Muxes the narration onto
   the silent render and appends a **1-second freeze-frame tail** (`--tail 1.0`,
   default) so the last word of audio is never clipped. Output is the master MP4 in
   `mp4/` — this is the complete, watchable video.
8. **`publish`** (optional) — `package_video.py <folder>` writes the YouTube
   description + hashtags and a doodle to-do.

`svg` (optional icon overlays) only ever happens between `assemble` and a final
editor pass, and is skippable entirely. The video is done at `assemble`.

---

## 5. Acceptance checklist (every video must pass)

- [ ] Folder `~/Documents/Cowork/Codex/Manim/<slug>/` with `script.md`,
      `beat_sheet.json`, `<slug>.py`, `mp3/`, `mp4/master*.mp4`
- [ ] Scene class is exactly `BearsDoodlesVideo(Scene)`, scene is silent
- [ ] White bg, Shadows Into Light, ink/accent/red/ghost palette, all content in safe area
- [ ] Intro is an infographic hero (brand + topic Manim graphic + title), not bare text
- [ ] Hooks each draw a topic sketch; no placeholder boxes anywhere
- [ ] Outro is a separate cleared card: "Thanks for watching" + title + youtube.com/@NikBearBrown
- [ ] `layout_audit.md` shows 0 errors
- [ ] Audio matches real MP3 durations; 1s freeze tail present; nothing clipped
- [ ] `metadata.series = "Bears Notes"`, voice + style settings match §2

Build one video end to end, stopping at each gate for approval, before scaling to a batch.
