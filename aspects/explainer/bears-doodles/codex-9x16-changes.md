# Codex brief — Bear's Notes now ships 9:16 as well as 16:9

Context for the Codex agent working on the Bear's Notes / Manim video pipeline. This explains the dual-orientation (9:16 portrait) system that was just added, the engine that powers it, the **gotchas that will silently break a render if you don't know them**, and how to convert a scene. Read this before touching any scene for portrait.

---

## What changed, in one paragraph

Every video now ships **both** a 16:9 landscape master (YouTube) **and** a 9:16 portrait master (Shorts/TikTok/Reels), produced from the **same scene file and the same audio** — only the layout reflows. Portrait is **not** a scaled or cropped copy of landscape: it's a genuine re-layout (side-by-side panels become stacked top/bottom, content is sized to the width and distributed down the height). A shared engine, `bn_layout.py`, does the orientation detection and provides the layout primitives. `energy_levels_arent_evenly_spaced.py` is the **reference implementation** — copy its structure.

Canonical files (in the Cowork repo; sync these into your environment):
- `bears-doodles/scripts/bn_layout.py` — the layout engine (copy it **next to each scene**; Manim puts the scene dir on `sys.path`)
- `bears-doodles/scripts/assemble.py` — now has `--portrait`
- `bears-doodles/scripts/make_short.py` — branded-reframe fallback (no re-render)
- `bears-doodles/scripts/manim_layout_audit.py` — aspect-aware overlap/out-of-frame auditor
- `bears-doodles/reference/reframing-16x9-to-9x16.md` — the full reflow ruleset (research-backed)
- `bears-doodles/reference/style.md` → "Aspect ratio" section
- Reference scene: `Manim/energy-levels-arent-evenly-spaced/energy_levels_arent_evenly_spaced.py`

---

## ⚠️ Three gotchas that will waste your time if you skip them

1. **Manim v0.20.1 does NOT recompute the world `frame_width` when you change resolution with `-r`.** It sets the pixels to 1080×1920 but leaves `frame_width` at the 16:9 default (14.22), so the camera maps a 14-unit-wide world into a 1080px portrait frame → ~3× horizontal squish. **`bn_layout.sync_frame_to_pixels()` fixes this on import** (it derives `frame_width = frame_height * pixel_width/pixel_height`). Therefore **every scene must `import bn_layout` at module top** — that import is what corrects the frame. It's a no-op for true 16:9.

2. **Render portrait with `-r 1080,1920 --fps 60`, NOT `-qh -r 1080,1920`.** `-qh` forces 1920×1080 and overrides `-r`, so you silently render landscape. (Landscape still uses `-qh`.) Confirm in the log line the scene prints: `[bn_layout] mode=PORTRAIT (stacked) pixels=1080x1920 frame=4.50x8.00`. If it says `frame=14.22` or `mode=LANDSCAPE`, the render is wrong.

3. **Manim caches partial frames.** After changing geometry, render with `--disable_caching --flush_cache` or you'll get stale frames from the previous (possibly broken) pass and think your fix didn't work.

`is_portrait()` is detected from **pixel dimensions** (`pixel_height > pixel_width`), not `frame_width`, because pixels are what `-r` reliably sets.

---

## The engine: `bn_layout.py`

A "rect" is `(x0, y0, x1, y1)` in Manim world units.

- `is_portrait()` — pixel-based orientation test.
- `sync_frame_to_pixels()` — runs at import; fixes the v0.20.1 frame bug (see gotcha 1).
- `band()` — the usable **content band**. Landscape = house safe area (±6.3 / ±3.4). **Portrait reserves UI zones**: bottom ~24% (caption bar/CTA), top ~10% (nav/handle), ~0.30u side margins (right action rail). Returns the rect everything must live inside.
- `rows(rect, weights, gap)` / `cols(rect, weights, gap)` — split a rect into stacked / side-by-side sub-rects by weight.
- `fit(mobj, rect, frac=0.92)` — scale a mobject to **fill** the rect (tighter axis) and center it. This is the "fill, don't float" primitive.
- `fit_width(mobj, rect, frac)` — scale to a width fraction; center.
- `fit_text(s, font, size, color, max_width)` — **greedy** word-wrap that packs each line to the real measured width (not a words-per-line guess), so text runs the full column with fewer, larger lines.
- helpers: `half_w/half_h`, `safe_w/safe_h`, `rw/rh/rcx/rcy/center`, `inset`, `frac_point`.

---

## The layout rules (why portrait is a re-layout, not a scale)

Full detail + citations in `reference/reframing-16x9-to-9x16.md`. The load-bearing rules:

- **Reflow, don't crop or shrink.** These are authored vector scenes → we re-arrange elements; we never pixel-crop.
- **Fill the constrained dimension, distribute the abundant one.** In portrait, size content to ~90% of the band **width**, then spread it down the **height** (no big dead bands). The classic bug is keeping landscape y-positions so content floats tiny in the vertical middle — don't.
- **Recompute every position from `band()`**, never reuse a landscape coordinate. (An element at landscape-center is *upper-center* in portrait.)
- **Side-by-side → stacked top/bottom**, in reading order (most important first). If two panels can't both fit, split into sequential beats.
- **Keep content out of the bottom ~24% / right rail** (platform UI). Channel handle/outro go upper-middle, never flush bottom.
- **Type scales up and wraps more** in portrait; long captions get shortened, not shrunk to illegibility.
- Run `manim_layout_audit.py` on the portrait render — it reads frame extents from config, so it audits portrait overlaps automatically.

---

## How a scene supports both orientations

One file, branch on `is_portrait()`. **Landscape is the existing, approved layout — do not change it.** Portrait derives its geometry from `band()` rows and uses `fit()`/`fit_text()` to fill. Pattern from the reference scene:

```python
import bn_layout as BL
from bn_layout import is_portrait, band, rows, fit, fit_text, rw, safe_w, safe_h

LANDSCAPE = dict(... existing constants ...)

def _portrait_L():
    b = band()
    top_r, bot_r = rows(b, [0.92, 1.08], gap=0.5)   # stack: panel A top, panel B bottom
    # derive every constant (panel extents, label positions, caption seam) FROM these rects
    return dict(lx0=..., wlo=top_r[1]+0.1, whi=top_r[3]-0.12, ax=bot_r[0]+0.4, ...)

class BearsDoodlesVideo(Scene):
    def construct(self):
        global L
        L = _portrait_L() if is_portrait() else LANDSCAPE
        # ... draw functions read L[...] so the SAME drawing code serves both ...
```

Intro / hooks / outro: in portrait, split `band()` into rows and `fit()` each block so they fill (e.g. hook = `rows(band(), [0.34, 0.66])` → narration card fills the top row, sketch fills the bottom). In landscape, keep the existing fixed positions. The scene class name **must stay `BearsDoodlesVideo`** and the scene stays **silent** (audio is muxed by assemble) — unchanged from before.

---

## Pipeline: produce both masters

```
# 16:9
manim -qh <scene>.py BearsDoodlesVideo
python ../../bears-doodles/scripts/assemble.py . --mode manim                  # -> <slug>.mp4
# 9:16  (note: -r, NOT -qh; flush cache after geometry changes)
manim -r 1080,1920 --fps 60 --disable_caching --flush_cache <scene>.py BearsDoodlesVideo
python ../../bears-doodles/scripts/manim_layout_audit.py <scene>.py --png       # audit portrait
python ../../bears-doodles/scripts/assemble.py . --mode manim --portrait        # -> <slug>-short.mp4
```

`assemble.py --portrait` picks the 9:16 render (it probes each render's real dimensions, so it can't grab the landscape one) and writes `mp4/<slug>-short.mp4`, muxing the same narration + the 1s freeze-frame tail.

**Fallback:** for scenes not yet converted to dual-orientation, `make_short.py <folder>` wraps the finished 16:9 master in a branded 9:16 white card (brand + title + channel) with **no re-render**. Universal but the content stays small — prefer the native portrait re-render above.

---

## Status / what remains

- **Done & verified:** `energy-levels-arent-evenly-spaced` is fully converted (box fills the top band, ladder fills the bottom, hooks/intro/outro fill via `fit()`, greedy text wrap). It is the **template**.
- **Remaining:** every other scene still needs its own portrait pass. This is **bespoke per scene** — you must decide which panels stack and in what order — but you build it on the same `band`/`rows`/`fit` primitives, never hand-guessed coordinates. Landscape layouts stay untouched.

## Acceptance check per scene (portrait)
- [ ] Log shows `mode=PORTRAIT … frame=4.50x8.00`.
- [ ] Content **fills** the band (no >~15% contiguous dead band); panels stacked top/bottom, not side-by-side.
- [ ] Nothing in the bottom ~24% / right-rail UI zone; outro/handle upper-middle.
- [ ] `manim_layout_audit.py` on the portrait render: 0 errors.
- [ ] Landscape render unchanged.
- [ ] `<slug>-short.mp4` assembled, same audio, 1s tail, nothing clipped.
