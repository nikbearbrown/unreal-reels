---
name: mini-bio
description: >
  Build a short narrated mini-biography of ANY figure — a scientist, writer, artist,
  leader, athlete, or a fictional character (Dorothy Gale, Sherlock Holmes, Emma
  Woodhouse) — as a cinematic cut. A narrator (Bear's voice clone, or a character's own
  voice) carries the story while the visuals ALTERNATE between full-frame photoreal
  Higgsfield footage (the figure via a Soul ID, the world their story lives in, or the
  legacy it left) and clean dark Manim cards (name + dates, a signature line or equation,
  a year). Use when the user types `bio`, `mini-bio`, `new bio`, `ingest`, `clips`, or
  `build bio`, or asks for a bio / documentary-style explainer of a person or character.
  LENGTH IS STORY-DRIVEN, not a fixed target: a simple figure may run ~30s, a rich life
  up to ~5 min. Audio-first; photoreal is the star, cards carry the dates and the words.
---

# mini-bio

A mini-bio video of **any figure — real or fictional.** A narrator carries the whole
thing; the visual track ALTERNATES, beat by beat:

- **`render: "clip"`** — a full-frame Higgsfield clip. `clip_source` is one of:
  - `soul-id` — the figure, via a trained Higgsfield **Soul ID** (a consistent face;
    for real people it's an invented likeness, copyright-safe; for fictional characters
    it's the character design). **Always opens and closes the video**, and recurs as the
    spine of longer bios (see *Soul-ID density* below).
  - `world` — the milieu the story lives in: the phenomenon a scientist explained, a
    Regency ballroom, a Kansas prairie under a gathering tornado, a battlefield, a city.
  - `legacy` — what endures: the technology a discovery enabled, shelves of well-worn
    novels, a cultural icon, monuments, the adaptations a character still inspires.
- **`render: "manim"`** — a clean dark card. `card.kind` is one of:
  - `title` — `name` (all caps) + `dates` (e.g. `1775 — 1817`, or for a character its
    origin, e.g. `THE WIZARD OF OZ · 1900`).
  - `quote` — a small grey `label` + a `text` signature line (their famous words, a
    defining phrase). The general-purpose "key line" card.
  - `equation` — a small grey `label` + a big white `tex` (LaTeX → MathTex). For figures
    whose key idea IS an equation (scientists, mathematicians). Use `quote` otherwise.
  - `date` — a big year + a grey `label` (a pivotal moment).

Photoreal is the star; cards carry the dates and the words. Don't lip-sync the footage —
narration runs over silent B-roll (the one exception is dialogue mode, below).

## The story every bio must tell
Whatever the length, every mini-bio answers three questions, in order:

1. **Who was this person/character?** — open on a `soul-id` clip; establish them with a
   `title` card.
2. **Why did they matter?** — what they did, the world they worked in (`world` clips), the
   line or idea that defines them (`quote` / `equation`), the turning point.
3. **What was their impact?** — the legacy they left (`legacy` clips), a pivotal `date` —
   then **close on a `soul-id` clip** (who they became / how they're remembered).

If a draft doesn't clearly answer all three, it isn't done.

## Length is an output, not a target
**Do not write to a 30-second (or any) clock.** Duration is the *sum of the beats the
story needs* — see `reference/duration.md`. A figure with one clean idea may run ~30–60s;
a layered life with several ideas, quotes, and turns may run up to ~5 minutes. Let the
narration tell the story; then the runtime is whatever the beats add up to. Never compress
a beat below its consolidation floor to hit a number, and never pad to reach one.

### Soul-ID density scales with length
The figure should keep reappearing as the video's spine. More length → more `soul-id`:

| Length | Beats (approx) | Soul-ID beats |
|--------|----------------|---------------|
| Short (~30–60s) | 5–7 | 2 — open + close |
| Medium (~1–2.5 min) | 8–14 | 3–4 — open, close, + 1–2 between sections |
| Long (~2.5–5 min) | 14–24 | open + close + one anchoring each section (who / why / impact) |

## The locked look (see reference/style.md)
White (`#F2F0EC`) on near-black (`#0E0E12`), **grey** (`#8A8780`) for secondary text,
**no accent colour**, **Montserrat** throughout. Divider rules are white. This is NOT the
doodle look — it's documentary, so photoreal and cards read as one piece.

## Timing contract (do not break)
Every beat's on-screen time — fade-out included — equals its narration length `dur(bid)`
**exactly**. The scene budgets the hold to absorb the remainder so the master timeline
matches the audio. This is what lets `composite_clips.py` drop footage on the right cuts;
adding animation time on top of a beat's budget causes drift and "shot overhang." Note
the timing contract makes length story-driven *automatically*: longer narration = longer
beat = longer film. (Beat *minimums* — the consolidation floors — are in `duration.md`.)

## Dialogue mode (optional, two or more voices)
For a character speaking with their author, or two figures in conversation (e.g. Jane
Austen × Emma Woodhouse), set a per-beat `voice_id` on each beat — `generate_audio.py`
honours it, falling back to the metadata `voice_id`. Alternate speakers beat by beat;
the visual track still alternates clip/card the same way. Dialogue bios are usually the
longer ones — budget Soul-ID beats for *each* speaker.

## Commands

### `bio <figure>` — author + scaffold
1. Read `reference/style.md`, `reference/duration.md`, and `reference/prompts.md`.
2. Gather the facts: dates/origin, the defining line or equation, a pivotal year, the
   world the story lives in, and the legacy. Verify dates/quotes/equations. (For fictional
   figures, "facts" are canon — cite the source work; never invent canon.)
3. Decide the **length** from the richness of the story (`duration.md`), not a target.
4. Write the **alternating** beat sheet (clip / card / clip / card …) covering who / why /
   impact, narrator line on every beat, one idea per beat, opening AND closing on
   `soul-id`, with Soul-ID density matching the length.
5. Scaffold: `python scripts/new_bio.py "<Name>" --length short|medium|long`
   (copies the scene + fonts, writes a starter beat sheet at that length). Replace the
   starter beats with the authored ones.
6. List the clip beats' Higgsfield prompts as a shot list (one Soul ID per figure serves
   all that figure's soul-id beats).

### `clips` / `ingest` — pull footage from TMP
After generating the Higgsfield clips and dropping them in a `TMP/` folder named in order
(`B1_…`, `B2_…`, … = first clip beat, second clip beat, …):
```
python ../mini-bio/scripts/ingest_clips.py .
```
It **copies** (never moves) each clip into `clips/<BEAT>.mp4`, **strips the audio**, and
maps sources to the clip beats in order. TMP stays intact — delete it yourself once the
video looks great.

### `build` — render the cut (16:9 AND a 9:16 Short)
**16:9 (landscape):**
```
python ../../bears-doodles/scripts/generate_audio.py .          # narration (silent/reuse aware)
manim -qh <slug>.py BearsDoodlesVideo                            # cards + placeholders
python ../../bears-doodles/scripts/composite_clips.py .          # footage full-frame into clip windows
python ../../bears-doodles/scripts/assemble.py . --mode manim --manim-mp4 mp4/_composited.mp4
```
**9:16 (Short) — same audio, no new footage generation:**
```
manim -r 1080,1920 --fps 60 --disable_caching --flush_cache <slug>.py BearsDoodlesVideo
python ../../bears-doodles/scripts/composite_clips.py . --portrait
python ../../bears-doodles/scripts/assemble.py . --mode manim --portrait --manim-mp4 mp4/_composited-short.mp4
```
A Short is best reserved for short/medium bios; a 5-minute bio is a long-form piece, not a
Short. Make the 16:9 first; the Short reuses its footage.

Before any footage exists, the audio + `manim` + `assemble.py --mode manim` already produce a
watchable **placeholder cut** so you can judge the rhythm first. To estimate runtime with no
API calls, run `generate_audio.py . --dry-run` — it sums per-beat word-count estimates.

### `youtube` — draft titles + descriptions (long + Short)
```
python scripts/package_bio.py .
```
Writes `<slug>-youtube.md`: title options, a description built from the narration (the bio
IS the story), tags, hashtags, and a separate **#Shorts** block. Tags/hashtags are derived
from the figure and the story, not hardcoded to a field. It's a draft — refine the hook
line before posting, and verify the facts.

## Dependencies
Reuses the Bear's Notes engine in `../bears-doodles/scripts/`: `generate_audio.py`
(audio-first TTS; per-beat `voice_id`, `reuse_audio`, and silent beats), `composite_clips.py`
(full-frame footage overlay at beat windows, freezes a short clip's last frame to fill),
and `assemble.py` (mux). Keep `mini-bio/` a sibling of `bears-doodles/` in the workspace.

## Default flow
`bio` (author + scaffold) → generate footage in Higgsfield → drop in `TMP/` → `ingest`
→ `build`. Watch the placeholder cut early; lock footage last.
