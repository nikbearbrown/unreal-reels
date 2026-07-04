"""
solve_oscillator_without_solving_it.py
======================================
Bear's Notes — "Why You Can Solve a Quantum Oscillator Without Ever Solving It"
Quantum Mechanics Vol. 1, Ch. 7 (Candidate 15).

9 MANIM beats (A01-A08), SILENT 16:9, one continuous ACCUMULATE scene. A dot on an
evenly spaced energy ladder is stepped UP by a raise operator and DOWN by a lower
operator; energy can't be negative, so there's a floor the lowering kills, and from
that floor raising builds the entire evenly spaced spectrum. (Deliberate contrast to
Candidate 12's n^2 fanning ladder — this one is perfectly even.) Stroke-on
Create/Transform (fast render). INTRO + two hooks are placeholder markers.
assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh solve_oscillator_without_solving_it.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # dot + raise + ladder
RED     = "#C0392B"     # the floor it can't pass + emphasis
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why You Can Solve a Quantum Oscillator Without Ever Solving It"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

AX = -4.2                # energy axis x
FLOOR_Y = -2.2
DY = 0.78                # equal rung spacing
RX0, RX1 = -3.7, 2.3     # rung extent
DOTX = -0.7

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.5, "A02": 4.0, "A03": 4.0, "A04": 4.5, "A05": 5.5, "A06": 5.0,
       "A07": 4.5, "A08": 5.0, "INTRO": 5.5, "H01": 5.0, "H02": 4.5, "OUTRO": 9.5}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def ry(k):
    return FLOOR_Y + k * DY


def make_rung(k, color=INK):
    return Line([RX0, ry(k), 0], [RX1, ry(k), 0], color=color, stroke_width=5)


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
        self.rungs = {}
        self._intro_card()
        self._hook("H01", "[ doodle: scary equations ]")
        self._hook("H02", "[ doodle: up + down arrows ]")
        self._ladder_scene()
        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_card(self):
        t = dur("INTRO")
        brand = Text("Bear's Notes", font=FONT, font_size=44, color=INK).move_to([0, 3.0, 0])
        rungs = VGroup(*[Line([-1.2, y, 0], [1.2, y, 0], color=ACCENT, stroke_width=5)
                         for y in (-0.5, 0.2, 0.9)])
        dot = Dot([0, 0.2, 0], color=ACCENT, radius=0.13)
        hero = VGroup(rungs, dot).move_to([0, 0.4, 0])
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
        if bid == "H01":            # a "brutal differential equation" -> stacked squiggles
            lines = VGroup(*[ParametricFunction(lambda x, o=o: [x, o + 0.12 * np.sin(6 * x), 0],
                             t_range=[-2.2, 2.2, 0.05], color=ACCENT, stroke_width=4)
                             for o in (-0.7, -1.2, -1.7)])
            q = Text("a hard equation?", font=FONT, font_size=30, color=INK).move_to([0, -2.6, 0])
            return VGroup(lines, q)
        if bid == "H02":            # step up, step down -> two operator arrows
            up = Arrow([-0.9, -1.7, 0], [-0.9, -0.3, 0], color=ACCENT, buff=0, stroke_width=7)
            dn = Arrow([0.9, -0.3, 0], [0.9, -1.7, 0], color=INK, buff=0, stroke_width=7)
            lab = Text("up and down", font=FONT, font_size=28, color=INK).move_to([0, -2.4, 0])
            return VGroup(up, dn, lab)
        return None
    def _say(self, txt, color=INK):
        return Text(txt, font=FONT, font_size=26, color=color).move_to([0, 3.1, 0])

    # ── A01–A08 ───────────────────────────────────────────────────────────────
    def _ladder_scene(self):
        # A01 — axis + one rung + dot
        t1 = dur("A01")
        axis = Arrow([AX, -2.8, 0], [AX, 2.9, 0], buff=0, color=INK, stroke_width=4)
        elbl = Text("energy", font=FONT, font_size=24, color=INK).next_to(axis, UP, buff=0.1)
        self.rungs[3] = make_rung(3)
        self.dot = Dot([DOTX, ry(3), 0], color=ACCENT, radius=0.13)
        self.play(GrowArrow(axis), FadeIn(elbl), run_time=t1 * 0.5)
        self.play(Create(self.rungs[3]), FadeIn(self.dot), run_time=t1 * 0.5)

        # operator legend
        raise_arr = Arrow([3.1, 1.4, 0], [3.1, 2.2, 0], buff=0, color=ACCENT, stroke_width=5)
        raise_lbl = Text("raise", font=FONT, font_size=22, color=ACCENT).next_to(raise_arr, RIGHT, buff=0.15)
        lower_arr = Arrow([3.1, 0.4, 0], [3.1, -0.4, 0], buff=0, color=INK, stroke_width=5)
        lower_lbl = Text("lower", font=FONT, font_size=22, color=INK).next_to(lower_arr, RIGHT, buff=0.15)

        # A02 — raise one rung
        t2 = dur("A02")
        cap = self._say("raise: up one rung", ACCENT)
        self.play(FadeIn(raise_arr), FadeIn(raise_lbl), FadeIn(cap), run_time=t2 * 0.3)
        self._hop(3, 4, up=True, t=t2 * 0.7)
        self._cap = cap

        # A03 — lower one rung
        t3 = dur("A03")
        cap3 = self._say("lower: down one rung", INK)
        self.play(FadeIn(lower_arr), FadeIn(lower_lbl), Transform(self._cap, cap3), run_time=t3 * 0.3)
        self._hop(4, 3, up=False, t=t3 * 0.7)

        # A04 — keep lowering to the floor
        t4 = dur("A04")
        cap4 = self._say("keep lowering to the bottom", INK)
        self.play(Transform(self._cap, cap4), run_time=t4 * 0.2)
        self._hop(3, 2, up=False, t=t4 * 0.27)
        self._hop(2, 1, up=False, t=t4 * 0.27)
        self._hop(1, 0, up=False, t=t4 * 0.26)

        # A05 — the floor cannot be passed
        t5 = dur("A05")
        floor_red = make_rung(0, color=RED)
        self.play(Transform(self.rungs[0], floor_red), run_time=t5 * 0.25)
        downa = Arrow([DOTX + 0.55, ry(0), 0], [DOTX + 0.55, ry(0) - 0.7, 0], buff=0.05,
                      color=RED, stroke_width=4)
        xmark = VGroup(
            Line([-0.25, -0.25, 0], [0.25, 0.25, 0], color=RED, stroke_width=6),
            Line([-0.25, 0.25, 0], [0.25, -0.25, 0], color=RED, stroke_width=6),
        ).move_to([DOTX, ry(0) - 0.7, 0])
        nothing = Text("nothing — energy can't be negative", font=FONT, font_size=24, color=RED).move_to([0, 3.1, 0])
        self.play(GrowArrow(downa), run_time=t5 * 0.25)
        self.play(Create(xmark), Transform(self._cap, nothing), run_time=t5 * 0.3)
        self.play(FadeOut(downa, xmark), run_time=t5 * 0.2)

        # A06 — raise from the floor builds every level
        t6 = dur("A06")
        cap6 = self._say("raise builds every level", ACCENT)
        self.play(Transform(self._cap, cap6), run_time=t6 * 0.15)
        per = (t6 * 0.85) / 6
        for k in range(0, 6):
            self._hop(k, k + 1, up=True, t=per)

        # A07 — even spacing
        t7 = dur("A07")
        braces = VGroup()
        for k in range(0, 6):
            br = DoubleArrow([-3.95, ry(k), 0], [-3.95, ry(k + 1), 0], buff=0, color=INK,
                            stroke_width=2.5, tip_length=0.1)
            braces.add(br)
        cap7 = self._say("a perfectly even ladder", ACCENT)
        self.play(LaggedStart(*[GrowArrow(b) for b in braces], lag_ratio=0.1),
                  Transform(self._cap, cap7), run_time=t7 * 0.8)
        self.wait(max(0.2, t7 * 0.2))

        # A08 — punchline
        t8 = dur("A08")
        self.play(FadeOut(self._cap), run_time=t8 * 0.2)
        red = Text("the whole spectrum, no equation solved", font=FONT, font_size=28, color=RED).move_to([0, -3.05, 0])
        self.play(Write(red), run_time=t8 * 0.6)
        self.wait(max(0.2, t8 * 0.2))

    def _hop(self, kf, kt, up, t):
        col = ACCENT if up else INK
        if kt not in self.rungs:
            self.rungs[kt] = make_rung(kt)
            self.play(Create(self.rungs[kt]), run_time=t * 0.3)
            t = t * 0.7
        a = Arrow([DOTX + 0.55, ry(kf), 0], [DOTX + 0.55, ry(kt), 0], buff=0.05, color=col,
                  stroke_width=4, max_tip_length_to_length_ratio=0.35)
        self.play(GrowArrow(a), run_time=t * 0.45)
        self.play(self.dot.animate.move_to([DOTX, ry(kt), 0]), run_time=t * 0.4)
        self.play(FadeOut(a), run_time=t * 0.15)

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
