"""
wave_leaks_into_forbidden_wall.py
=================================
Bear's Notes — "Why a Quantum Particle Leaks Into a Wall It Can't Climb"
Quantum Mechanics Vol. 1, Ch. 6 (Candidate 13).

9 MANIM beats (A01-A08), SILENT 16:9. A classical ball turns back at the wall; the
quantum wave oscillates on the allowed side and, at the wall, MORPHS from a (naive)
continued oscillation into a smooth exponential decay that bleeds a finite distance
into the shaded forbidden zone. Boundary is C1-smooth (value + slope match). Mostly
Transform/Create (stroke-on, fast render). INTRO + two hooks are placeholder markers.
assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh wave_leaks_into_forbidden_wall.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # the wave
RED     = "#C0392B"     # forbidden zone + emphasis
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why a Quantum Particle Leaks Into a Wall It Can't Climb"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

# wave geometry — boundary at x=0, allowed x<0, forbidden x>0
WB = 0.0                 # wave baseline (y)
A = 1.0                  # amplitude
K = 3.0                  # wavenumber
PHI = 2.2                # phase so value>0 and slope<0 at the wall
V0 = float(np.sin(PHI))          # boundary value (0.808)
KAPPA = float(-K * np.cos(PHI) / np.sin(PHI))   # decay rate (2.184) -> C1 match
XL = -6.0                # left edge of wave
XR = 6.0                 # right edge of forbidden shading
REACH = 3.0 / KAPPA      # visible penetration (~1.37)

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.5, "A02": 4.0, "A03": 4.0, "A04": 4.5, "A05": 5.0, "A06": 4.5,
       "A07": 5.5, "A08": 5.0, "INTRO": 5.5, "H01": 5.0, "H02": 4.5, "OUTRO": 9.0}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def osc(x):
    return A * np.sin(K * x + PHI)


def decay(x):
    return V0 * A * np.exp(-KAPPA * x)


def graph(fn, x0, x1, color=ACCENT, sw=5):
    return ParametricFunction(lambda x: [x, WB + fn(x), 0],
                              t_range=[x0, x1, 0.01], color=color, stroke_width=sw)


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
        self._intro_card()
        self._hook("H01", "[ doodle: ball rolls back ]")
        self._hook("H02", "[ doodle: wave seeps in ]")
        self._wall_scene()
        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        wall = Line([0, -1.0, 0], [0, 1.1, 0], color=INK, stroke_width=7)
        osc = ParametricFunction(lambda x: [x, 0.6 * np.sin(3 * x), 0], t_range=[-2.3, 0, 0.03], color=ACCENT, stroke_width=4)
        dec = ParametricFunction(lambda x: [x, 0.6 * np.exp(-2.0 * x), 0], t_range=[0, 1.7, 0.03], color=ACCENT, stroke_width=4)
        return VGroup(wall, osc, dec)

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
            hill = Arc(radius=1.2, start_angle=0.2, angle=2.7, color=INK, stroke_width=4).move_to([0, -1.2, 0])
            ball = Dot([-0.6, -0.7, 0], color=ACCENT, radius=0.13)
            return VGroup(hill, ball, Text("rolls back", font=FONT, font_size=28, color=INK).move_to([0, -2.7, 0]))
        if bid == "H02":
            dec = ParametricFunction(lambda x: [x, -1.0 + 0.9 * np.exp(-1.6 * (x + 1.5)), 0],
                                     t_range=[-1.5, 1.8, 0.03], color=ACCENT, stroke_width=4)
            return VGroup(dec, Text("seeps in", font=FONT, font_size=28, color=INK).move_to([0, -2.7, 0]))
        return None

    def _wall_scene(self):
        # A01 — setup: baseline, wall, shaded forbidden zone
        t1 = dur("A01")
        base = Line([XL, WB, 0], [XR, WB, 0], color=GHOST, stroke_width=2)
        shade = Rectangle(width=XR, height=5.0, color=RED, fill_color=RED,
                          fill_opacity=0.10, stroke_width=0).move_to([XR / 2, 0.1, 0])
        wall = Line([0, -2.4, 0], [0, 2.6, 0], color=INK, stroke_width=7)
        flab = Text("forbidden — not enough energy", font=FONT, font_size=24, color=RED).move_to([2.95, 2.3, 0])
        self.play(Create(base), FadeIn(shade), Create(wall), run_time=t1 * 0.7)
        self.play(FadeIn(flab), run_time=t1 * 0.3)

        # A02 — classical ball turns back
        t2 = dur("A02")
        ball = Dot([XL + 0.6, WB + 0.16, 0], color=INK, radius=0.16)
        tb = Text("turns back", font=FONT, font_size=24, color=INK).move_to([-3.0, -1.5, 0])
        self.play(FadeIn(ball), run_time=t2 * 0.15)
        self.play(ball.animate.move_to([-0.25, WB + 0.16, 0]), run_time=t2 * 0.35)
        self.play(ball.animate.move_to([XL + 0.6, WB + 0.16, 0]), FadeIn(tb), run_time=t2 * 0.4)
        self.play(FadeOut(ball, tb), run_time=t2 * 0.1)

        # A03 — oscillating wave on the allowed side
        t3 = dur("A03")
        wave = graph(osc, XL, 0.0, color=ACCENT, sw=5)
        self.play(Create(wave), run_time=t3 * 0.85)
        self.wait(max(0.1, t3 * 0.15))

        # A04 — boundary value (non-zero, smooth)
        t4 = dur("A04")
        bdot = Dot([0, WB + V0, 0], color=ACCENT, radius=0.1)
        bcap = Text("must stay smooth here", font=FONT, font_size=24, color=INK).move_to([-3.0, 2.3, 0])
        self.play(FadeIn(bdot), FadeIn(bcap), run_time=t4 * 0.6)
        self.wait(max(0.2, t4 * 0.4))

        # A05 — morph: naive oscillation -> exponential decay
        t5 = dur("A05")
        naive = graph(osc, 0.0, REACH + 1.4, color=GHOST, sw=4)
        tail = graph(decay, 0.0, REACH + 1.0, color=ACCENT, sw=5)
        cap5 = Text("oscillation morphs into decay", font=FONT, font_size=24, color=ACCENT).move_to([3.0, -1.6, 0])
        self.play(Create(naive), run_time=t5 * 0.4)
        self.play(Transform(naive, tail), FadeIn(cap5), run_time=t5 * 0.5)
        self.wait(max(0.1, t5 * 0.1))

        # A06 — finite penetration depth
        t6 = dur("A06")
        br = DoubleArrow([0, -0.6, 0], [REACH, -0.6, 0], buff=0, color=INK,
                         stroke_width=3, tip_length=0.14)
        brl = Text("finite reach", font=FONT, font_size=22, color=INK).next_to(br, DOWN, buff=0.12)
        self.play(GrowArrow(br), FadeIn(brl), run_time=t6 * 0.7)
        self.wait(max(0.2, t6 * 0.3))

        # A07 — reflected back
        t7 = dur("A07")
        refl = Arrow([-1.2, 1.7, 0], [-3.4, 1.7, 0], buff=0, color=ACCENT, stroke_width=5)
        rlab = Text("reflected", font=FONT, font_size=24, color=ACCENT).next_to(refl, UP, buff=0.12)
        self.play(GrowArrow(refl), FadeIn(rlab), run_time=t7 * 0.7)
        self.wait(max(0.2, t7 * 0.3))

        # A08 — punchline
        t8 = dur("A08")
        red = Text("the wave leaks into the forbidden wall", font=FONT, font_size=30, color=RED).move_to([0, -3.05, 0])
        self.play(Write(red), run_time=t8 * 0.7)
        self.wait(max(0.2, t8 * 0.3))

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
