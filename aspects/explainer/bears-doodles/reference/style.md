# Bear's Doodles — Series Identity & Setup

Locked defaults. A video may override a value in its `beat_sheet.json` `metadata`,
but these are the series standard.

## Opening (every video)

The first beat is the intro. ElevenLabs narrates:

```
Bear's Doodles

<title>
```

The blank line is a real paragraph break — in ElevenLabs that renders as a short
pause. `generate_audio.py` inserts it automatically as beat `INTRO`. Visually,
Manim renders the title card (brand + title in Shadows Into Light) with a small
**bear marker** for the intro doodle.

## Closing (every video)

The last beat is the `OUTRO`. ElevenLabs narrates a thanks + channel call-out:

```
Thanks for watching <title> — find more Bear's Doodles at <channel>
```

`<channel>` defaults to `youtube.com/@NikBearBrown` (`metadata.channel_url`).
The outro **keeps the finished plot on screen** and parks the **title in the upper
margin band** — text only, no marker (`render: none`). Nothing else goes on screen:
**no channel URL** (it collides with bottom-of-frame labels and is already in the
narration + the YouTube description) and no "Thanks for watching" (spoken only).
Because the plot is confined to the safe area, the title's margin band is reliably
empty, so the outro clears **any** ending frame. The intro is the one place the Bear
mascot is built in.

## Deliverable & assembly

The deliverable is the **Manim master + voiceover** — a complete, watchable video on
its own. Every beat renders in Manim (intro/hook/outro as clean title/keyword/text
cards, the explanation as graphs/simulations) and `assemble.py` muxes the narration.
There are **no placeholder windows that must be filled** for the video to be finished.

**Optional enrichment, layered on top:** SVG icons (`svg_doodles.py`, pulled from the
validated `Manim/shared/svg` library only when a beat has a strong subject match) and
hand-drawn doodles are transparent overlays added in a video editor (Premiere/Rush)
over the intro/hook/outro windows. Manim cannot ingest mp4, so these always sit on
top, added by hand; `composite_doodles.py` can auto-rough-cut them for preview. A
video with zero overlays is still a finished video — never force an icon or a doodle.

## Fonts

- **Non-math text** (labels, titles, captions): **Shadows Into Light**. The TTF ships in the project at `Manim/shared/fonts/ShadowsIntoLight-Regular.ttf`. Install it on the machine (double-click the TTF) so Manim's `Text(..., font="Shadows Into Light")` resolves.
- **Math**: Manim `MathTex` (LaTeX). Requires MacTeX (`brew install --cask mactex-no-gui`).

## Colors

Defaults live in `Manim/shared/colors.json`:

```json
{ "accent_color": "#5A5653", "forbidden_color": "#C0392B", "text_font": "Shadows Into Light" }
```

- **Ink** (all primary line art): near-black `#1a1a1a`.
- **Accent** (the one pedagogical element per scene — wavefunction, key curve): **Warm Slate `#5A5653`** by default. ~7:1 on white (AA), ~5.8:1 against red. Topic-appropriate accent overrides go in the beat sheet `metadata.accent_color`.
- **Forbidden** (states/barriers/violations — the "this is not allowed" language): **Red `#C0392B`**, universal across the series. Do not override; red = forbidden is consistent visual grammar.
- Max 3 colors in any doodle. Never rely on red–green contrast alone; pair color with shape or position.

## The Bear mascot — intro/outro only

The Bear is the *series mascot*, not the everyman. It appears in the **intro and
outro** (branding) and nowhere else — unless a bear is genuinely relevant to the
concept. Inside a video, doodle characters depict whatever the concept calls for,
usually a generic **person** ("your body", "an observer"). Don't reach for the bear
in body beats; reach for the character the idea actually needs.

## The doodle "thing"

Each video has a small object that represents the concept (Earth, a philosopher,
a sun, a particle). Rendered as a small black square with white text label, or a
Bear's Doodles sketch, drawn in stroke by stroke. Color it only where it makes
sense (yellow sun), max 3 colors.

### Bear's Doodles Midjourney template (character / abstract things)

```
[SUBJECT], flat vector illustration. Thick black lines, solid colors, bold lines,
simple details. White background. Napkin sketch style, simple doodle, black and white.
--ar [ASPECT] --profile 2hu1pm2 j3xc8st i7dpdo9 8qzx41e 196d1wf
```

The profile ID (`2hu1pm2 j3xc8st i7dpdo9 8qzx41e 196d1wf`, five tokens) locks the
house style across the whole character library. The descriptor stack carries the
look; the profile locks cross-session consistency. Cowork writes the `[SUBJECT]`
(detailed — pose, "standing, full body, legs visible", species accuracy) and the
fixed suffix; the human picks the best of the 4-up.

## Voice

- Default ElevenLabs voice ID: **``** (override in `metadata.voice_id`).
- Settings: `eleven_multilingual_v2`, stability `0.80`, similarity_boost `0.75`, style `0.00`, `output_format mp3_44100_128`, speed `0.92`.
- No background music.

## Aspect ratio — the published set per concept

**Two videos go to YouTube per concept, in two folders:** the **1-min 9:16 Short** (from the 1-min scene) and the **2–5 min 16:9 deep** worked-example (from the `expand` scene). The 1-min scene is orientation-aware and *can* also render 16:9, but **the 1-min 16:9 is not published or rendered by default** — it's on-demand only (plain `manim -qh`) if you ever want a quick short-only landscape. The deep tier is 16:9-only. So the default published renders are: **1-min → 9:16**, **deep → 16:9**. (See `reference/shorts-vs-longform-strategy.md` and `youtube-publishing.md`.)

The 1-min scene is still **orientation-aware** (one file renders either aspect) — that's what produces the 9:16 Short. It is **not two files.** It imports `bn_layout.py` (copy it into the video folder next to the scene) and asks `is_portrait()` at the top of `construct()`, then selects a `LANDSCAPE` / `PORTRAIT` constant set. Manim keeps `frame_height = 8` in both orientations and only changes `frame_width` (14.22 → 4.5), so **vertical text stacks — intro, hooks, outro — are shared**; you only reflow the *horizontal* arrangement:

- **Landscape:** panels side-by-side (e.g. box on the left, energy ladder on the right).
- **Portrait:** panels stacked top/bottom; running captions live in the seam between them; the bottom-band content (e.g. an energy axis) leaves no room for a bottom punchline, so place late captions/punchlines in the seam after fading the earlier one.

Drive geometry from the active constant set (`L["..."]`) so the drawing code is written once. Use `bn_layout.fit_text(...)` and `scale_to_fit_width(2*safe_w()*k)` for every title/caption so text auto-narrows in portrait. Render and then run `scripts/manim_layout_audit.py` on **both** renders — it reads the frame extents from config, so it audits portrait overlaps automatically (the portrait seam is the usual offender).

Render + assemble both:

```
manim -qh <scene>.py BearsDoodlesVideo                  # 16:9
python ../../bears-doodles/scripts/assemble.py . --mode manim
manim -r 1080,1920 --fps 60 --disable_caching --flush_cache <scene>.py BearsDoodlesVideo     # 9:16 (NOT -qh: it forces 1920x1080 and overrides -r)
python ../../bears-doodles/scripts/assemble.py . --mode manim --portrait   # → <slug>-short.mp4
```

**Fallback for not-yet-converted scenes:** `scripts/make_short.py <folder>` wraps the finished 16:9 master in a branded 9:16 white card (brand + title + channel) with no re-render. Universal, but dual-panel content stays small — prefer the native portrait re-render above.

## Safe area (margins)

Never let Manim content touch the frame edges — players, rounded corners, and platform UI clip the outer band. Keep all drawing inside a **safe inset of ~8%** (title-safe). In a Manim scene this means defining usable half-extents (e.g. `SAFE_HALF_W, SAFE_HALF_H`) a margin inside the frame's true half-width/height and mapping the plot + positioning all text/labels within them — not `to_edge()` flush to the border. The space *between* panels or columns is the gutter; give it room too.

## Folder convention

One folder per video, named by the kebab-case `slug` (= the YouTube slug, single
source of truth). Under `Manim/` (or wherever the project root is):

```
<slug>/
├── beat_sheet.json          ← slug lives in metadata
├── <slug_underscored>.py    ← the Manim scene (copied from manim_template.py)
├── mp3/                      ← beat-<ID>.mp3 + timings.json
├── mp4/                      ← final video + any per-beat doodle clips (beat-<ID>-<thing>.mp4)
├── frames/                   ← Manim PNG exports / doodle start-end frames
└── media/                   ← Manim render output
shared/
├── colors.json
├── fonts/ShadowsIntoLight-Regular.ttf
└── ...
```

## Machine setup (one time)

The project Python lives in a venv at `~/ai` to avoid the Anaconda/x86 numpy
conflict on Apple Silicon. Activate it with the `ai` alias before running scripts:

```bash
ai                       # alias for: source ~/ai/bin/activate
pip install manim requests mutagen
```

ElevenLabs key as an environment variable (so it never lands in a file):

```bash
export ELEVENLABS_API_KEY="sk_..."   # add to ~/.zshrc
echo $ELEVENLABS_API_KEY             # verify it prints
```

If Cowork/Codex runs in a shell that can't see `~/.zshrc`, pass the key inline:
`ELEVENLABS_API_KEY=sk_... python scripts/generate_audio.py <folder>`.
