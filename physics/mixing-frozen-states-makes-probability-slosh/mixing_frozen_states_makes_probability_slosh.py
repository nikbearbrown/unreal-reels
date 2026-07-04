"""
mixing_frozen_states_makes_probability_slosh.py
===============================================
Bear's Notes — "Why Mixing Two Frozen Quantum States Makes Probability Slosh"
Quantum Mechanics Vol. 1, Ch. 4 (Candidate 10).

9 MANIM beats (A01-A08) as one continuous SILENT 16:9 scene. Two infinite-well
eigenstates each have a STILL probability cloud; combine them and the cloud sloshes
left-right. The slosh is driven by two clock hands (an Argand inset, upper-left)
turning at different rates: the growing angle gap (phi = p2 - p1) is the interference
phase. Driven by two ValueTrackers (self.p1, self.p2 — local, no clash with
Scene.time). INTRO + two hook beats are placeholder markers. assemble.py muxes audio.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh mixing_frozen_states_makes_probability_slosh.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # the cloud + fast clock
RED     = "#C0392B"     # closing emphasis
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why Mixing Two Frozen Quantum States Makes Probability Slosh"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

# the well
L = 3.0                 # half-width of the box
FLOOR = -1.7
WALL_H = 3.5
S = 2.0                 # probability-cloud vertical scale

# the Argand inset (the "engine")
CC = np.array([-4.7, 1.5, 0.0])
CR = 0.8

# clock rates (seconds per turn): state 2 turns faster, so the gap grows
SLOW = 6.5
FAST = 2.6

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 3.5, "A02": 4.5, "A03": 4.5, "A04": 5.5, "A05": 4.0, "A06": 6.0,
       "A07": 5.5, "A08": 4.5, "INTRO": 5.0, "H01": 5.5, "H02": 4.5, "OUTRO": 9.0}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def adv(t, rate):
    return 2 * np.pi * t / rate


def psi1(x):
    return np.cos(np.pi * x / (2 * L))      # ground: one hump, zero at +-L


def psi2(x):
    return np.sin(np.pi * x / L)            # first excited: two lobes, zero at 0, +-L


def dens(x, phi):
    return 0.5 * psi1(x) ** 2 + 0.5 * psi2(x) ** 2 + psi1(x) * psi2(x) * np.cos(phi)


def cloud(fn):
    xs = np.linspace(-L, L, 170)
    top = [[x, FLOOR + S * fn(x), 0] for x in xs]
    pts = top + [[L, FLOOR, 0], [-L, FLOOR, 0]]
    return Polygon(*pts, color=ACCENT, stroke_width=4,
                   fill_color=ACCENT, fill_opacity=0.22)


def well():
    left = Line([-L, FLOOR, 0], [-L, FLOOR + WALL_H, 0], color=INK, stroke_width=7)
    right = Line([L, FLOOR, 0], [L, FLOOR + WALL_H, 0], color=INK, stroke_width=7)
    floor = Line([-L, FLOOR, 0], [L, FLOOR, 0], color=INK, stroke_width=4)
    return VGroup(left, right, floor)


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
        self.p1 = ValueTracker(1.4)        # state-1 angle (slow)
        self.p2 = ValueTracker(2.3)        # state-2 angle (fast); small starting gap
        self._intro_card()
        self._hook("H01", "[ doodle: still cloud in a box ]")
        self._hook("H02", "[ doodle: cloud sloshes ]")
        self._slosh_scene()
        self._outro_card()

    def _phi(self):
        return self.p2.get_value() - self.p1.get_value()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        walls = VGroup(Line([-1.3, -0.6, 0], [-1.3, 0.9, 0], color=INK, stroke_width=6),
                       Line([1.3, -0.6, 0], [1.3, 0.9, 0], color=INK, stroke_width=6),
                       Line([-1.3, -0.6, 0], [1.3, -0.6, 0], color=INK, stroke_width=4))
        bump = ParametricFunction(lambda x: [x, -0.6 + 1.1 * np.cos(np.pi * x / 2.6) ** 2, 0],
                                  t_range=[-1.3, 1.3, 0.03], color=ACCENT, stroke_width=4)
        return VGroup(walls, bump)

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
        bump = lambda cx: ParametricFunction(lambda x: [x, -1.6 + 0.9 * np.exp(-((x - cx) / 0.7) ** 2), 0],
                                             t_range=[-2.4, 2.4, 0.03], color=ACCENT, stroke_width=4)
        if bid == "H01":
            return VGroup(bump(0.0), Text("one still cloud", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        if bid == "H02":
            arr = VGroup(Arrow([-0.4, -0.6, 0], [-1.6, -0.6, 0], color=INK, buff=0, stroke_width=4),
                         Arrow([0.4, -0.6, 0], [1.6, -0.6, 0], color=INK, buff=0, stroke_width=4))
            return VGroup(bump(0.9), arr, Text("it sloshes", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        return None

    def _hand(self, angle, color, sw=5):
        tip = CC + CR * np.array([np.cos(angle), np.sin(angle), 0.0])
        return Arrow(CC, tip, buff=0, color=color, stroke_width=sw,
                     max_tip_length_to_length_ratio=0.22)

    # ── A01–A08 ───────────────────────────────────────────────────────────────
    def _slosh_scene(self):
        p1, p2 = self.p1, self.p2

        # A01 — the box
        t1 = dur("A01")
        w = well()
        self.play(Create(w), run_time=t1 * 0.85)
        self.wait(max(0.1, t1 * 0.15))

        # A02 — ground-state cloud (still)
        t2 = dur("A02")
        c = cloud(lambda x: psi1(x) ** 2)
        lab = Text("state 1", font=FONT, font_size=24, color=INK).move_to([0, 2.6, 0])
        self.play(FadeIn(c), FadeIn(lab), run_time=t2 * 0.7)
        self.wait(max(0.2, t2 * 0.3))

        # A03 — first-excited cloud (still)
        t3 = dur("A03")
        c2 = cloud(lambda x: psi2(x) ** 2)
        lab2 = Text("state 2", font=FONT, font_size=24, color=INK).move_to([0, 2.6, 0])
        self.play(Transform(c, c2), Transform(lab, lab2), run_time=t3 * 0.7)
        self.wait(max(0.2, t3 * 0.3))

        # A04 — the two clocks (spin, cloud still)
        t4 = dur("A04")
        ring = DashedVMobject(Circle(radius=CR, color=GHOST, stroke_width=3).move_to(CC), num_dashes=36)
        h1 = self._hand(p1.get_value(), INK, sw=5)
        h2 = self._hand(p2.get_value(), ACCENT, sw=5)
        clbl = Text("the engine", font=FONT, font_size=22, color=GHOST).next_to(ring, DOWN, buff=0.18)
        self.play(FadeIn(ring), GrowArrow(h1), GrowArrow(h2), FadeIn(clbl), run_time=t4 * 0.4)
        h1.add_updater(lambda m: m.become(self._hand(p1.get_value(), INK, sw=5)))
        h2.add_updater(lambda m: m.become(self._hand(p2.get_value(), ACCENT, sw=5)))
        self.play(p1.animate.increment_value(adv(t4 * 0.6, SLOW)),
                  p2.animate.increment_value(adv(t4 * 0.6, SLOW)),
                  run_time=t4 * 0.6, rate_func=linear)

        # A05 — combine into one cloud (still snapshot)
        t5 = dur("A05")
        comb = cloud(lambda x: dens(x, self._phi()))
        lab3 = Text("state 1 + state 2", font=FONT, font_size=24, color=INK).move_to([0, 2.6, 0])
        self.play(Transform(c, comb), Transform(lab, lab3), run_time=t5 * 0.7)
        self.remove(comb)
        c.add_updater(lambda m: m.become(cloud(lambda x: dens(x, self._phi()))))
        self.wait(max(0.2, t5 * 0.3))

        # A06 — slosh: clocks drift apart, cloud pumps left-right
        t6 = dur("A06")
        self.play(p1.animate.increment_value(adv(t6, SLOW)),
                  p2.animate.increment_value(adv(t6, FAST)),
                  run_time=t6, rate_func=linear)

        # A07 — the gap is the driver
        t7 = dur("A07")
        gap = Text("the gap sets the beat", font=FONT, font_size=26, color=ACCENT).move_to([0.4, 3.0, 0])
        self.play(FadeIn(gap),
                  p1.animate.increment_value(adv(t7, SLOW)),
                  p2.animate.increment_value(adv(t7, FAST)),
                  run_time=t7, rate_func=linear)

        # A08 — punchline; stop motion for a clean hold
        t8 = dur("A08")
        self.play(p1.animate.increment_value(adv(t8 * 0.45, SLOW)),
                  p2.animate.increment_value(adv(t8 * 0.45, FAST)),
                  run_time=t8 * 0.45, rate_func=linear)
        c.clear_updaters()
        h1.clear_updaters()
        h2.clear_updaters()
        red = Text("two frozen states, and the mix moves", font=FONT, font_size=30, color=RED).move_to([0, -3.0, 0])
        self.play(Write(red), run_time=t8 * 0.55)

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
