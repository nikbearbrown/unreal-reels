"""
double_slit_one_electron.py
===========================
Bear's Notes — "Why One Electron at a Time Still Builds Stripes"
Quantum Mechanics Vol. 1, Ch. 2 (Candidate 01).

Renders the 9 MANIM beats (A01–A09) as one continuous, SILENT 16:9 scene, each beat
timed to its real ElevenLabs duration from mp3/timings.json. The 3 doodle beats
(INTRO, H01, H02) are placeholder markers here; the doodle clips are overlaid later
in an editor. assemble.py muxes the voiceover (audio is NOT baked here).

Run order:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -pqh double_slit_one_electron.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim

v1 — fringe density, ripple counts, dot counts may want a tuning pass after render.
"""
import json
from pathlib import Path

import numpy as np
from manim import *

import bn_layout as BL
from bn_layout import is_portrait, band, rows, fit, fit_text, rw, safe_w, safe_h

HERE = Path(__file__).resolve().parent

# ── palette / identity ────────────────────────────────────────────────────────
INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # Warm Slate — wave / intensity / highlight
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why One Electron at a Time Still Builds Stripes"
CHANNEL = "youtube.com/@NikBearBrown"

# ── safe area (16:9; frame ~14.22 x 8) ────────────────────────────────────────
SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

# ── apparatus geometry (scene coords) ─────────────────────────────────────────
X_SRC, X_BAR, X_SCR = -6.0, -1.3, 5.0
Y_TOP = 3.1
SLIT = 0.5            # slit offset from centre
GAP = 0.35           # half-height of each slit gap

# ── timings ───────────────────────────────────────────────────────────────────
_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FALLBACK = {"A01": 4.5, "A02": 4.0, "A03": 4.0, "A04": 5.5, "A05": 5.0,
             "A06": 5.5, "A07": 5.0, "A08": 5.0, "A09": 5.0,
             "INTRO": 3.5, "H01": 5.5, "H02": 5.0, "OUTRO": 6.0}


def dur(b):
    return float(_T.get(b, _FALLBACK.get(b, 5.0)))


def intensity(y):
    """Double-slit interference intensity along the screen (height y)."""
    return np.cos(2.1 * y) ** 2 * np.exp(-(y / 2.3) ** 2)


def sample_y(n, rng):
    """Rejection-sample n screen heights from the interference intensity."""
    out = []
    while len(out) < n:
        y = rng.uniform(-3.0, 3.0)
        if rng.uniform(0, 1) < intensity(y):
            out.append(y)
    return out


def dots_at(ys, color=INK, r=0.035, jitter=0.12, rng=None):
    g = VGroup()
    for y in ys:
        dx = rng.uniform(-jitter, jitter) if rng is not None else 0
        g.add(Dot([X_SCR + dx, y, 0], radius=r, color=color))
    return g


def barrier():
    segs = VGroup(
        Line([X_BAR, -Y_TOP, 0], [X_BAR, -SLIT - GAP, 0], color=INK, stroke_width=6),
        Line([X_BAR, -SLIT + GAP, 0], [X_BAR, SLIT - GAP, 0], color=INK, stroke_width=6),
        Line([X_BAR, SLIT + GAP, 0], [X_BAR, Y_TOP, 0], color=INK, stroke_width=6),
    )
    return segs


def screen():
    return Line([X_SCR, -Y_TOP, 0], [X_SCR, Y_TOP, 0], color=INK, stroke_width=5)


def intensity_curve(scale=1.1, color=ACCENT):
    return ParametricFunction(
        lambda y: [X_SCR + scale * intensity(y), y, 0],
        t_range=[-3.0, 3.0, 0.03], color=color, stroke_width=5)


_bsp = HERE / "beat_sheet.json"
_BS = json.loads(_bsp.read_text()) if _bsp.exists() else {}
_NARR = {b["beat_id"]: b.get("narration_text", "") for b in _BS.get("beats", [])}
_DEEP_TEX = _BS.get("metadata", {}).get("deep_teaser_tex")


# ── portrait (9:16) fringe model: interference across x on a bottom screen ────
def intensity_x(x):
    return np.cos(4.0 * x) ** 2 * np.exp(-(x / 1.05) ** 2)


def sample_x(n, rng):
    out = []
    while len(out) < n:
        x = rng.uniform(-1.6, 1.6)
        if rng.uniform(0, 1) < intensity_x(x):
            out.append(x)
    return out


def _card(s, _sz=40):
    ws = s.split()
    lines = [" ".join(ws[i:i + 6]) for i in range(0, len(ws), 6)] or [""]
    g = VGroup(*[Text(l, font=FONT, font_size=_sz, color=INK) for l in lines]).arrange(DOWN, buff=0.28)
    if g.width > 11.5:
        g.scale_to_fit_width(11.5)
    return g


class BearsDoodlesVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        self.rng = np.random.default_rng(7)
        if is_portrait():
            self._p_all()
            return

        self._intro_card()
        self._hook("H01", "[ doodle: fire one ]")
        self._hook("H02", "[ doodle: one dot ]")

        # SCENE 3 — the experiment (A01–A05)
        bar, scr = barrier(), screen()
        self._A01(bar, scr)
        d_few = self._A02()
        d_hundred = self._A03(d_few)
        fringe = self._A04(d_few, d_hundred)
        curve = self._A05()
        self.play(FadeOut(bar, scr, fringe, curve), run_time=0.4)
        self.wait(0.1)

        # SCENE 4 — the why (A06–A09)
        self._A06_A09()

        self._outro_card()

    # ── PORTRAIT (9:16) — vertical double-slit: source top, screen bottom ─────
    SCR_Y, BAR_Y, SRC_Y = -1.9, 1.4, 3.0   # screen / barrier / source heights
    SX0, SX1 = -1.65, 1.65                  # screen span

    def _p_apparatus(self):
        bar = VGroup(
            Line([self.SX0, self.BAR_Y, 0], [-0.45, self.BAR_Y, 0], color=INK, stroke_width=6),
            Line([-0.2, self.BAR_Y, 0], [0.2, self.BAR_Y, 0], color=INK, stroke_width=6),
            Line([0.45, self.BAR_Y, 0], [self.SX1, self.BAR_Y, 0], color=INK, stroke_width=6))
        scr = Line([self.SX0, self.SCR_Y, 0], [self.SX1, self.SCR_Y, 0], color=INK, stroke_width=5)
        return bar, scr

    def _p_dots(self, xs, r=0.035, jitter=0.1):
        g = VGroup()
        for x in xs:
            dy = self.rng.uniform(0, jitter)
            g.add(Dot([x, self.SCR_Y + 0.05 + dy, 0], radius=r, color=INK))
        return g

    def _p_card(self, bid, label=""):
        t = dur(bid)
        crow, srow = rows(band(), [0.34, 0.66], gap=0.3)
        c = fit(fit_text(_NARR.get(bid, label), FONT, 34, INK, rw(crow) * 0.96), crow, 0.96)
        sk = self._p_hook_sketch(bid)
        if sk is not None:
            fit(sk, srow, 0.82)
        self.play(Write(c), run_time=min(1.4, t * 0.4))
        if sk is not None:
            self.play(Create(sk), run_time=min(1.2, t * 0.3))
        self.wait(max(0.3, t - 2.6))
        self.play(FadeOut(c, sk) if sk is not None else FadeOut(c), run_time=0.4)

    def _p_hook_sketch(self, bid):
        bar = VGroup(Line([-1.4, 0.6, 0], [-0.3, 0.6, 0], color=INK, stroke_width=6),
                     Line([0.3, 0.6, 0], [1.4, 0.6, 0], color=INK, stroke_width=6))
        scr = Line([-1.4, -1.4, 0], [1.4, -1.4, 0], color=INK, stroke_width=5)
        if bid == "H01":
            e = Dot([0, 1.6, 0], color=ACCENT, radius=0.12)
            return VGroup(bar, scr, e)
        return VGroup(bar, scr, Dot([0.2, -1.35, 0], color=INK, radius=0.06))

    def _p_intro(self):
        t = dur("INTRO")
        brow, hrow, trow = rows(band(), [0.2, 0.48, 0.32], gap=0.25)
        brand = fit(Text("Bear's Notes", font=FONT, font_size=44, color=INK), brow, 0.82)
        hero = fit(self._intro_hero(), hrow, 0.8)
        title = fit(fit_text(TITLE, FONT, 30, ACCENT, rw(trow) * 0.96), trow, 0.98)
        self.play(FadeIn(brand), run_time=min(0.9, t * 0.25))
        self.play(Create(hero), run_time=min(1.6, t * 0.4))
        self.play(Write(title), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 3.7))
        self.play(FadeOut(brand, hero, title), run_time=0.4)

    def _p_all(self):
        self._p_intro()
        self._p_card("H01", "[ fire one ]")
        self._p_card("H02", "[ one dot ]")

        bar, scr = self._p_apparatus()
        # A01 — two slits + screen
        t = dur("A01")
        sl = Text("two slits", font=FONT, font_size=24, color=INK).next_to(bar, UP, buff=0.15)
        self.play(Create(bar), FadeIn(sl), run_time=t * 0.5)
        self.play(Create(scr), run_time=t * 0.5)

        # A02 — first scattered dots
        t = dur("A02")
        d_few = self._p_dots(sample_x(12, self.rng))
        self.play(LaggedStart(*[FadeIn(d) for d in d_few], lag_ratio=0.06), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))

        # A03 — ~100, still speckle
        t = dur("A03")
        d100 = self._p_dots(sample_x(110, self.rng))
        ctr = Text("100", font=FONT, font_size=26, color=INK).move_to([1.5, 2.6, 0])
        self.play(FadeIn(d100, lag_ratio=0.02), FadeIn(ctr), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))

        # A04 — 70,000: stripes emerge
        t = dur("A04")
        big = self._p_dots(sample_x(900, self.rng), r=0.03)
        ctr2 = Text("70,000", font=FONT, font_size=26, color=INK).move_to([1.5, 2.6, 0])
        self.play(FadeIn(big, lag_ratio=0.002), Transform(ctr, ctr2), run_time=t * 0.85)
        self.wait(max(0.1, t * 0.15))

        # A05 — intensity curve above the screen
        t = dur("A05")
        curve = ParametricFunction(lambda x: [x, self.SCR_Y + 0.2 + 1.7 * intensity_x(x), 0],
                                   t_range=[self.SX0, self.SX1, 0.02], color=ACCENT, stroke_width=5)
        cl = Text("interference", font=FONT, font_size=24, color=ACCENT).next_to(curve, UP, buff=0.1)
        self.play(Create(curve), FadeIn(cl), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))
        self.play(FadeOut(d_few, d100, ctr, big, curve, cl, sl), run_time=0.4)

        # A06 — one wave through both slits, overlapping
        t = dur("A06")
        waves = VGroup()
        for sx in (-0.2, 0.2):
            for rad in (0.5, 1.0, 1.5, 2.0):
                waves.add(Arc(radius=rad, start_angle=PI + 0.4, angle=PI - 0.8,
                              arc_center=[sx, self.BAR_Y, 0], color=ACCENT, stroke_width=2.5))
        self.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=0.04), run_time=t * 0.7)
        self.wait(max(0.2, t * 0.3))
        self.play(FadeOut(waves), run_time=0.3)

        # A07–A09 — the meaning (text over the standing apparatus)
        for bid, msg in (("A07", "self-interference sets the odds"),
                         ("A08", "each dot random; the crowd traces the odds"),
                         ("A09", "a particle travels as a wave of possibility")):
            t = dur(bid)
            c = fit_text(_NARR.get(bid, msg), FONT, 30, INK, 2 * safe_w() * 0.9).move_to([0, 0.4, 0])
            self.play(Write(c), run_time=min(1.4, t * 0.45))
            self.wait(max(0.3, t - 1.8))
            self.play(FadeOut(c), run_time=0.35)

        BL.outro(self, TITLE, CHANNEL, dur("OUTRO"), teaser_tex=_DEEP_TEX,
                 font=FONT, ink=INK, accent=ACCENT)

    # ── helpers ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        barrier = VGroup(Line([0, 1.2, 0], [0, 0.45, 0], color=INK, stroke_width=6),
                         Line([0, 0.15, 0], [0, -0.15, 0], color=INK, stroke_width=6),
                         Line([0, -0.45, 0], [0, -1.2, 0], color=INK, stroke_width=6))
        fringes = VGroup(*[Line([1.7, y - 0.16, 0], [1.7, y + 0.16, 0], color=ACCENT, stroke_width=6)
                           for y in (0.9, 0.45, 0.0, -0.45, -0.9)])
        return VGroup(barrier, fringes)

    def _intro_card(self):
        t = dur("INTRO")
        brand = Text("Bear's Notes", font=FONT, font_size=44, color=INK).move_to([0, 3.0, 0])
        hero = self._intro_hero().move_to([0, 0.4, 0])
        title = Text(TITLE, font=FONT, font_size=30, color=ACCENT)
        title.scale_to_fit_width(min(11.0, title.width)).move_to([0, -2.5, 0])
        r1, r2, r3 = min(0.9, t * 0.22), min(1.6, t * 0.4), min(1.3, t * 0.28)
        self.play(FadeIn(brand), run_time=r1)
        self.play(Create(hero), run_time=r2)
        self.play(Write(title), run_time=r3)
        self.wait(max(0.2, t - r1 - r2 - r3 - 0.4))
        self.play(FadeOut(brand, hero, title), run_time=0.4)

    def _hook(self, bid, label):
        t = dur(bid)
        card = _card(_NARR.get(bid, label)).scale(0.82).to_edge(UP, buff=0.7)
        sketch = self._hook_sketch(bid)
        r1 = min(1.4, t * 0.38)
        self.play(Write(card), run_time=r1)
        used = r1
        if sketch is not None:
            r2 = min(1.4, t * 0.34)
            self.play(Create(sketch), run_time=r2)
            used += r2
        self.wait(max(0.3, t - used - 0.4))
        self.play(FadeOut(card, sketch) if sketch is not None else FadeOut(card), run_time=0.4)

    def _hook_sketch(self, bid):
        if bid == "H01":
            src = Dot([-2.0, -1.0, 0], color=ACCENT, radius=0.13)
            arr = Arrow([-1.7, -1.0, 0], [0.6, -1.0, 0], color=INK, buff=0, stroke_width=4)
            return VGroup(src, arr, Text("one at a time", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        if bid == "H02":
            screen = Line([1.5, -1.7, 0], [1.5, -0.3, 0], color=INK, stroke_width=5)
            dot = Dot([1.5, -1.0, 0], color=ACCENT, radius=0.14)
            return VGroup(screen, dot, Text("a single dot", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        return None

    def _A01(self, bar, scr):
        t = dur("A01")
        src = Dot([X_SRC, 0, 0], color=INK)
        slabel = Text("source", font=FONT, font_size=22, color=INK).next_to(src, DOWN, buff=0.2)
        self.play(Create(bar), run_time=t * 0.5)
        self.play(Create(scr), FadeIn(src), FadeIn(slabel), run_time=t * 0.4)
        self.wait(max(0.1, t * 0.1))

    # ── A02 — first scattered dots ──────────────────────────────────────────────
    def _A02(self):
        t = dur("A02")
        ys = self.rng.uniform(-2.8, 2.8, size=12)
        g = dots_at(ys, rng=self.rng)
        self.play(LaggedStartMap(FadeIn, g, lag_ratio=0.15), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))
        return g

    # ── A03 — ~100, still speckle ───────────────────────────────────────────────
    def _A03(self, prev):
        t = dur("A03")
        ys = self.rng.uniform(-2.9, 2.9, size=90)
        g = dots_at(ys, rng=self.rng)
        counter = Text("100", font=FONT, font_size=30, color=INK).to_corner(UR).shift(LEFT * 0.4 + DOWN * 0.2)
        self.play(FadeIn(g, lag_ratio=0.02), FadeIn(counter), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))
        self._counter = counter
        return g

    # ── A04 — 70,000 → fringes ──────────────────────────────────────────────────
    def _A04(self, d1, d2):
        t = dur("A04")
        ys = sample_y(520, self.rng)
        g = dots_at(ys, rng=self.rng, r=0.03)
        new_counter = Text("70,000", font=FONT, font_size=30, color=INK).move_to(self._counter)
        self.play(FadeOut(d1, d2), run_time=0.3)
        self.play(FadeIn(g, lag_ratio=0.004),
                  Transform(self._counter, new_counter), run_time=t * 0.7)
        self.wait(max(0.1, t * 0.2))
        return VGroup(g, self._counter)

    # ── A05 — intensity curve over the fringes ──────────────────────────────────
    def _A05(self):
        t = dur("A05")
        curve = intensity_curve()
        self.play(Create(curve), run_time=t * 0.7)
        self.wait(max(0.2, t * 0.3))
        return curve

    # ── A06–A09 — the why ───────────────────────────────────────────────────────
    def _A06_A09(self):
        # A06 — one wave through both slits, ripples overlap
        t6 = dur("A06")
        bar = barrier()
        # incoming plane wavefronts (left of barrier)
        fronts = VGroup(*[Line([x, -2.2, 0], [x, 2.2, 0], color=ACCENT, stroke_width=2)
                          for x in (-5.2, -4.6, -4.0, -3.4)])
        self.play(Create(bar), run_time=t6 * 0.2)
        self.play(LaggedStartMap(Create, fronts, lag_ratio=0.2), run_time=t6 * 0.25)
        # circular ripples from each slit
        ripples = VGroup()
        for cy in (SLIT, -SLIT):
            for r in (0.7, 1.4, 2.1, 2.8, 3.5, 4.2):
                ripples.add(Arc(radius=r, start_angle=-PI / 2.2, angle=PI / 1.1,
                                arc_center=[X_BAR, cy, 0], color=ACCENT, stroke_width=2))
        self.play(FadeOut(fronts), run_time=0.2)
        self.play(LaggedStartMap(Create, ripples, lag_ratio=0.03), run_time=t6 * 0.4)
        self.wait(max(0.1, t6 * 0.1))

        # A07 — probability envelope on the screen
        t7 = dur("A07")
        scr = screen()
        curve = intensity_curve()
        plabel = Text("odds", font=FONT, font_size=22, color=ACCENT).next_to(curve, RIGHT, buff=0.1)
        self.play(Create(scr), run_time=t7 * 0.3)
        self.play(Create(curve), FadeIn(plabel), run_time=t7 * 0.5)
        self.wait(max(0.1, t7 * 0.2))
        self.play(FadeOut(bar, ripples), run_time=0.4)

        # A08 — dots rain to match the envelope
        t8 = dur("A08")
        ys = sample_y(420, self.rng)
        g = dots_at(ys, rng=self.rng, r=0.03)
        self.play(FadeIn(g, lag_ratio=0.005), run_time=t8 * 0.8)
        self.wait(max(0.1, t8 * 0.2))

        # A09 — one wave glides in, collapses to one dot
        t9 = dur("A09")
        wave = VGroup(*[Line([-5.0 + i * 0.4, -1.2, 0], [-5.0 + i * 0.4, 1.2, 0],
                             color=ACCENT, stroke_width=2) for i in range(3)])
        self.play(g.animate.set_opacity(0.25), FadeOut(curve, plabel), run_time=t9 * 0.2)
        self.play(wave.animate.shift(RIGHT * 10).set_opacity(0.0), run_time=t9 * 0.4)
        one = Dot([X_SCR, sample_y(1, self.rng)[0], 0], radius=0.07, color=ACCENT)
        self.play(Flash(one.get_center(), color=ACCENT), FadeIn(one), run_time=t9 * 0.3)
        self.wait(max(0.1, t9 * 0.1))
        self._tail = VGroup(scr, g, one)

    # ── OUTRO — title top margin, channel bottom margin, plot kept ───────────────
    def _outro_card(self):
        t = dur("OUTRO")
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)
        thanks = Text("Thanks for watching", font=FONT, font_size=44, color=INK).move_to([0, 1.7, 0])
        title = Text(TITLE, font=FONT, font_size=30, color=ACCENT)
        title.scale_to_fit_width(min(11.0, title.width)).move_to([0, 0.2, 0])
        url = Text("youtube.com/@NikBearBrown", font=FONT, font_size=36, color=INK).move_to([0, -1.7, 0])
        self.play(Write(thanks), run_time=1.2)
        self.play(FadeIn(title), run_time=1.0)
        self.play(Write(url), run_time=1.2)
        self.wait(max(0.6, t - 3.8))
