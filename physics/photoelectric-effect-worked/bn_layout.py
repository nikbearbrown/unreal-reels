"""
bn_layout.py — orientation-aware layout ENGINE for Bear's Notes scenes.

The SAME scene file renders 16:9 (landscape) or 9:16 (portrait). Manim keeps
frame_height = 8.0 in both and only changes frame_width (14.22 → 4.5), so the job
is to (a) work inside a per-orientation CONTENT BAND that excludes platform-UI
zones, and (b) RECOMPUTE every element's position/size from that band instead of
reusing landscape coordinates. See reference/reframing-16x9-to-9x16.md.

Core model — a "rect" is a tuple (x0, y0, x1, y1) in Manim world units:
    band()                 the usable content band for this orientation
    rows(rect, weights)    split a rect into stacked sub-rects (top→bottom)
    cols(rect, weights)    split a rect into side-by-side sub-rects (left→right)
    fit(mobj, rect, frac)  scale a mobject to fill `frac` of the rect (both axes) and center it
    fit_width(mobj, rect)  scale to a width fraction of the rect and center it
    fit_text(...)          word-wrap a string into a stacked VGroup bounded to a width

Portrait band reserves the bottom ~25% and top ~12% (platform caption bar / nav)
and a right margin (action rail), per the safe-zone research. Landscape band is the
house safe area (±6.3 / ±3.4).

Render portrait by overriding the resolution:
    manim -qh <scene>.py BearsDoodlesVideo                  # 16:9
    manim -qh -r 1080,1920 <scene>.py BearsDoodlesVideo     # 9:16
Copy this file next to the scene (Manim puts the scene dir on sys.path).
"""
from manim import config, VGroup, Text, DOWN


def sync_frame_to_pixels():
    """Make the world frame match the render's pixel aspect ratio.

    Manim CE (incl. v0.20.1) sets pixel_width/height from `-r W,H` but does NOT
    always recompute config.frame_width, leaving it at the 16:9 default (14.22).
    The camera then maps a 14.22-wide world into a 1080px-wide portrait frame —
    a ~3x horizontal squish. We keep frame_height (8.0) and derive frame_width
    from the pixel aspect so the mapping is uniform. Safe for any aspect (it's a
    no-op for true 16:9). Runs at import, before the Scene/Camera is constructed.
    """
    pw = getattr(config, "pixel_width", None)
    ph = getattr(config, "pixel_height", None)
    if pw and ph:
        config.frame_width = config.frame_height * (pw / ph)


sync_frame_to_pixels()


# ── orientation + frame ──────────────────────────────────────────────────────
def is_portrait() -> bool:
    # Detect from the actual rendered PIXEL dimensions — this is what `-r W,H`
    # sets directly and is reliable across Manim versions, unlike frame_width
    # which does not always recompute when only the resolution changes.
    pw = getattr(config, "pixel_width", None)
    ph = getattr(config, "pixel_height", None)
    if pw and ph:
        return ph > pw
    return config.frame_width < config.frame_height


print(
    f"[bn_layout] mode={'PORTRAIT' if is_portrait() else 'LANDSCAPE'} "
    f"pixels={config.pixel_width}x{config.pixel_height} "
    f"frame={config.frame_width:.2f}x{config.frame_height:.2f}",
    flush=True,
)


def half_w() -> float:
    return config.frame_width / 2.0


def half_h() -> float:
    return config.frame_height / 2.0


# Landscape house safe area (half-extents).
SAFE_W, SAFE_H = 6.3, 3.4


def safe_w() -> float:
    return SAFE_W if not is_portrait() else (half_w() - 0.30)


def safe_h() -> float:
    return SAFE_H


# ── the content band (UI-aware in portrait) ──────────────────────────────────
# Portrait reserves UI zones as fractions of the 8.0-tall frame:
PORTRAIT_TOP_RESERVE = 0.10     # ~nav/handle (frac of half_h*2)
PORTRAIT_BOT_RESERVE = 0.24     # ~caption bar / CTA
PORTRAIT_SIDE_MARGIN = 0.30     # world units kept clear each side (right action rail)


def band():
    """Usable content band (x0, y0, x1, y1)."""
    if is_portrait():
        hw, hh = half_w(), half_h()
        x0 = -hw + PORTRAIT_SIDE_MARGIN
        x1 = hw - PORTRAIT_SIDE_MARGIN
        y1 = hh - (2 * hh) * PORTRAIT_TOP_RESERVE     # top edge of band
        y0 = -hh + (2 * hh) * PORTRAIT_BOT_RESERVE    # bottom edge of band
        return (x0, y0, x1, y1)
    return (-SAFE_W, -SAFE_H, SAFE_W, SAFE_H)


# ── rect helpers ─────────────────────────────────────────────────────────────
def rw(r):  return r[2] - r[0]
def rh(r):  return r[3] - r[1]
def rcx(r): return (r[0] + r[2]) / 2.0
def rcy(r): return (r[1] + r[3]) / 2.0
def center(r): return [rcx(r), rcy(r), 0]


def inset(r, dx, dy=None):
    """Shrink a rect by dx (x) and dy (y, defaults to dx) on every side."""
    if dy is None:
        dy = dx
    return (r[0] + dx, r[1] + dy, r[2] - dx, r[3] - dy)


def frac_point(r, fx, fy):
    """A point inside rect at fractional position (fx, fy), origin bottom-left."""
    return [r[0] + fx * rw(r), r[1] + fy * rh(r), 0]


def rows(r, weights, gap=0.3):
    """Split rect into stacked sub-rects (top→bottom) by weight, with gaps."""
    n = len(weights)
    avail = rh(r) - gap * (n - 1)
    tot = float(sum(weights))
    out, y = [], r[3]   # start at top
    for w in weights:
        h = avail * (w / tot)
        out.append((r[0], y - h, r[2], y))
        y -= h + gap
    return out


def cols(r, weights, gap=0.3):
    """Split rect into side-by-side sub-rects (left→right) by weight, with gaps."""
    n = len(weights)
    avail = rw(r) - gap * (n - 1)
    tot = float(sum(weights))
    out, x = [], r[0]
    for w in weights:
        wd = avail * (w / tot)
        out.append((x, r[1], x + wd, r[3]))
        x += wd + gap
    return out


# ── fill helpers (scale TO the rect, then center) ────────────────────────────
def fit(mobj, r, frac=0.92):
    """Scale mobj to fill `frac` of the rect on its tighter axis, then center it."""
    if mobj.width > 1e-6 and mobj.height > 1e-6:
        s = min(rw(r) * frac / mobj.width, rh(r) * frac / mobj.height)
        mobj.scale(s)
    mobj.move_to(center(r))
    return mobj


def fit_width(mobj, r, frac=0.9, align_y=None):
    """Scale mobj so its width is `frac` of the rect width; center x; y = align_y or rect center."""
    if mobj.width > 1e-6:
        mobj.scale(rw(r) * frac / mobj.width)
    cy = rcy(r) if align_y is None else align_y
    mobj.move_to([rcx(r), cy, 0])
    return mobj


def fit_text(s, font, font_size, color, max_width, buff=0.24):
    """Word-wrap a string into a stacked VGroup whose lines FILL max_width.

    Greedy pack: add words to a line until the rendered line would exceed
    max_width, then break. This uses the real glyph widths (not a magic
    words-per-line constant), so each line runs the full available width — giving
    fewer, wider lines and larger type instead of a skinny center column.
    """
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and Text(trial, font=font, font_size=font_size).width > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    if not lines:
        lines = [s]
    g = VGroup(*[Text(ln, font=font, font_size=font_size, color=color) for ln in lines])
    g.arrange(DOWN, buff=buff)
    if g.width > max_width:
        g.scale_to_fit_width(max_width)
    return g


def outro(scene, title, channel, t=8.0, teaser_tex=None,
          font="Shadows Into Light", ink="#1a1a1a", accent="#5A5653"):
    """Tier-aware, orientation-aware outro card. Clears the canvas, then:

    - if `teaser_tex` is given (a 1-min Short whose DEEP version exists): the middle
      slot becomes "the full worked example →" + the deep's hero equation (MathTex),
      pointing viewers to the long-form instead of just repeating the title.
    - otherwise (no deep version, or the deep video itself): the standard title card.

    Gating is by metadata: pass teaser_tex only when a deep version exists, so a
    Short never promises a video that isn't there.
    """
    from manim import MathTex, Write, FadeIn, FadeOut

    if scene.mobjects:
        scene.play(FadeOut(*scene.mobjects), run_time=0.4)
    tw = 2 * safe_w() * 0.95
    thanks = Text("Thanks for watching", font=font, font_size=44, color=ink)
    url = Text(channel, font=font, font_size=36, color=ink)
    if teaser_tex:
        cue = Text("the full worked example", font=font, font_size=30, color=accent)
        eq = MathTex(teaser_tex, color=accent)
        if eq.width > tw:
            eq.scale_to_fit_width(tw)
        mid = VGroup(cue, eq).arrange(DOWN, buff=0.3)
    else:
        mid = Text(title, font=font, font_size=30, color=accent)
    if mid.width > tw:
        mid.scale_to_fit_width(tw)
    if url.width > tw:
        url.scale_to_fit_width(tw)

    if is_portrait():
        r1, r2, r3 = rows(band(), [0.30, 0.40, 0.30], gap=0.25)
        fit(thanks, r1, 0.9); fit(mid, r2, 0.96); fit(url, r3, 0.9)
    else:
        thanks.move_to([0, 1.7, 0]); mid.move_to([0, 0.1, 0]); url.move_to([0, -1.7, 0])

    scene.play(Write(thanks), run_time=1.0)
    scene.play(FadeIn(mid), run_time=1.0)
    scene.play(Write(url), run_time=1.0)
    scene.wait(max(0.6, t - 3.4))
