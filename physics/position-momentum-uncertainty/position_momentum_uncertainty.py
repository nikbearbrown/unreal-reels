"""
position_momentum_uncertainty.py
================================
Bear's Notes — "Why You Can't Pin Down Position and Momentum at Once"
Quantum Mechanics Vol. 1, Ch. 9 (Candidate 07).

9 MANIM beats (A01–A08), SILENT 16:9. Two linked panels — position (top) and
momentum/wavelength (bottom) — whose Gaussian widths trade off as a width tracker
squeezes the position spike. INTRO + two hook beats are placeholder markers.
assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh position_momentum_uncertainty.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim

Width tracker (`sx`) is local — no clash with Manim's Scene.time. v1.
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"
RED     = "#C0392B"
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why You Can't Pin Down Position and Momentum at Once"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

# panels
H = 1.7              # curve height (constant; WIDTH carries the teaching)
TOP = 0.7           # position baseline
BOT = -3.0          # momentum baseline
C = 1.1             # momentum width = C / position width
XR = 6.2

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.0, "A02": 5.0, "A03": 4.0, "A04": 4.0, "A05": 4.5, "A06": 4.5,
       "A07": 5.5, "A08": 5.0, "INTRO": 4.5, "H01": 4.5, "H02": 5.5, "OUTRO": 6.5}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def gauss_graph(base, sigma):
    return FunctionGraph(lambda x: base + H * np.exp(-(x / sigma) ** 2),
                         x_range=[-XR, XR, 0.03], color=ACCENT, stroke_width=5)


_bsp = HERE / "beat_sheet.json"
_NARR = {b["beat_id"]: b.get("narration_text", "") for b in (
    __import__("json").loads(_bsp.read_text()).get("beats", []) if _bsp.exists() else [])}


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
        self.sx = ValueTracker(2.2)        # position width (local — not self.time)
        self._intro_card()
        self._hook("H01", "[ doodle: pin the particle ]")
        self._hook("H02", "[ doodle: not the microscope ]")
        self._panels()
        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        top = ParametricFunction(lambda x: [x, 0.7 + 0.7 * np.exp(-(x / 0.4) ** 2), 0], t_range=[-2.0, 2.0, 0.02], color=ACCENT, stroke_width=4)
        bot = ParametricFunction(lambda x: [x, -0.9 + 0.55 * np.exp(-(x / 1.4) ** 2), 0], t_range=[-2.4, 2.4, 0.02], color=ACCENT, stroke_width=4)
        return VGroup(top, bot)

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
            dot = Dot([0, -1.0, 0], color=ACCENT, radius=0.13)
            cal = VGroup(Line([-0.5, -0.5, 0], [-0.5, -1.5, 0], color=INK, stroke_width=4),
                         Line([0.5, -0.5, 0], [0.5, -1.5, 0], color=INK, stroke_width=4))
            return VGroup(dot, cal, Text("pin it down?", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        if bid == "H02":
            lens = Circle(radius=0.6, color=ACCENT, stroke_width=4).move_to([0, -1.0, 0])
            slash = Line([-0.55, -1.55, 0], [0.55, -0.45, 0], color=ACCENT, stroke_width=5)
            return VGroup(lens, slash, Text("not the microscope", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        return None

    def _panels(self):
        sx = self.sx

        # A01 — axes + labels
        t1 = dur("A01")
        top_ax = Line([-XR, TOP, 0], [XR, TOP, 0], color=INK, stroke_width=3)
        bot_ax = Line([-XR, BOT, 0], [XR, BOT, 0], color=INK, stroke_width=3)
        # panel labels: just above the LEFT end of each axis, inside the frame
        top_lbl = Text("position", font=FONT, font_size=26, color=INK)
        top_lbl.move_to([-6.0 + top_lbl.width / 2, TOP + 0.5, 0])
        bot_lbl = Text("momentum", font=FONT, font_size=26, color=INK)
        bot_lbl.move_to([-6.0 + bot_lbl.width / 2, BOT + 0.5, 0])
        self.play(Create(top_ax), Create(bot_ax), FadeIn(top_lbl), FadeIn(bot_lbl), run_time=t1 * 0.8)
        self.wait(max(0.1, t1 * 0.2))

        # A02 — wide position, sharp momentum
        t2 = dur("A02")
        top = gauss_graph(TOP, sx.get_value())
        bot = gauss_graph(BOT, C / sx.get_value())
        self.play(Create(top), Create(bot), run_time=t2 * 0.6)
        top.add_updater(lambda m: m.become(gauss_graph(TOP, sx.get_value())))
        bot.add_updater(lambda m: m.become(gauss_graph(BOT, C / sx.get_value())))
        sharp = Text("sharp momentum", font=FONT, font_size=24, color=ACCENT).move_to([0, BOT + 2.0, 0])
        self.play(FadeIn(sharp), run_time=t2 * 0.4)

        # A03 — wide position uncertain
        t3 = dur("A03")
        wide = Text("where? uncertain", font=FONT, font_size=24, color=ACCENT).move_to([0, TOP + 2.0, 0])
        self.play(FadeIn(wide), run_time=t3 * 0.5)
        self.wait(max(0.2, t3 * 0.5))

        # A04 — squeeze the position to a spike
        t4 = dur("A04")
        self.play(FadeOut(sharp, wide), sx.animate.set_value(0.55), run_time=t4, rate_func=smooth)

        # A05 — needs many wavelengths
        t5 = dur("A05")
        many = Text("many wavelengths", font=FONT, font_size=24, color=ACCENT).move_to([0, BOT + 2.0, 0])
        spike = Text("pinned position", font=FONT, font_size=24, color=ACCENT).move_to([0, TOP + 2.0, 0])
        self.play(FadeIn(many), FadeIn(spike), run_time=t5 * 0.7)
        self.wait(max(0.2, t5 * 0.3))

        # A06 — the inverse trade
        t6 = dur("A06")
        narrow_br = DoubleArrow([-0.5, TOP - 0.2, 0], [0.5, TOP - 0.2, 0], color=INK, buff=0, stroke_width=3, tip_length=0.12)
        wide_br = DoubleArrow([-2.4, BOT - 0.2, 0], [2.4, BOT - 0.2, 0], color=INK, buff=0, stroke_width=3, tip_length=0.12)
        self.play(GrowArrow(narrow_br), GrowArrow(wide_br), run_time=t6 * 0.7)
        self.wait(max(0.2, t6 * 0.3))

        # A07 — see-saw + product bound
        t7 = dur("A07")
        self.play(sx.animate.set_value(2.2), run_time=t7 * 0.35, rate_func=smooth)
        self.play(sx.animate.set_value(0.9), run_time=t7 * 0.35, rate_func=smooth)
        bound = Text("width x width never goes below a limit", font=FONT, font_size=26, color=INK).move_to([0, -1.05, 0])
        self.play(FadeIn(bound), run_time=t7 * 0.3)

        # A08 — not the microscope
        t8 = dur("A08")
        self.play(FadeOut(many, spike, narrow_br, wide_br), run_time=t8 * 0.2)
        intrinsic = Text("baked into the wave — before you look", font=FONT, font_size=28, color=RED).move_to([0, -1.05, 0])
        self.play(FadeOut(bound), Write(intrinsic), run_time=t8 * 0.6)
        self.wait(max(0.2, t8 * 0.2))
        for m in (top, bot):
            m.clear_updaters()

    # ── OUTRO ─────────────────────────────────────────────────────────────────
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
