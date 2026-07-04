"""
particle_in_box.py  (rebuilt to current Bear's Notes conventions)
==================================================================
Bear's Notes — "Why a Particle in a Box Cannot Sit Still"
Quantum Mechanics Vol. 1, Ch. 5 (Candidate 04).

9 MANIM beats (A01–A08) as one continuous, SILENT 16:9 scene, each timed to its real
ElevenLabs duration from mp3/timings.json. INTRO + two hook beats are placeholder
markers (doodle clips overlaid later). assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh particle_in_box.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # the wavefunction arch
FORBID  = "#C0392B"     # the forbidden flat/still attempt
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why a Particle in a Box Cannot Sit Still"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

FLOOR = -1.6
PEAK = 2.6              # arch amplitude

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.5, "A02": 5.0, "A03": 5.5, "A04": 5.0, "A05": 5.0, "A06": 4.5,
       "A07": 5.0, "A08": 5.0, "INTRO": 4.5, "H01": 5.0, "H02": 5.0, "OUTRO": 6.5}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def walls(x=3.0):
    left = Line([-x, FLOOR, 0], [-x, FLOOR + 4.0, 0], color=INK, stroke_width=7)
    right = Line([x, FLOOR, 0], [x, FLOOR + 4.0, 0], color=INK, stroke_width=7)
    floor = Line([-x, FLOOR, 0], [x, FLOOR, 0], color=INK, stroke_width=4)
    return VGroup(left, right, floor)


def arch(x=3.0, amp=PEAK, color=ACCENT, sw=6):
    return ParametricFunction(
        lambda u: [u, FLOOR + amp * np.sin(np.pi * (u + x) / (2 * x)), 0],
        t_range=[-x, x, 0.02], color=color, stroke_width=sw)


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
        self._hook("H01", "[ doodle: marble rests ]")
        self._hook("H02", "[ doodle: quantum jitters ]")

        # SCENE 3 — fitting & curvature (A01–A06)
        w = walls()
        self._A01(w)
        self._A02(w)
        a = self._A03(w)
        self._A04(a)
        self._A05(a)
        self._A06(w, a)
        self.play(FadeOut(*self.mobjects), run_time=0.4)
        self.wait(0.1)

        # SCENE 4 — the squeeze (A07–A08)
        self._A07_A08()

        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, ww, hh = MARK
        return DashedVMobject(Rectangle(width=ww, height=hh, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        walls = VGroup(Line([-1.4, -0.9, 0], [-1.4, 1.2, 0], color=INK, stroke_width=6),
                       Line([1.4, -0.9, 0], [1.4, 1.2, 0], color=INK, stroke_width=6),
                       Line([-1.4, -0.9, 0], [1.4, -0.9, 0], color=INK, stroke_width=4))
        arch = ParametricFunction(lambda x: [x, -0.9 + 1.7 * np.sin(np.pi * (x + 1.4) / 2.8), 0],
                                  t_range=[-1.4, 1.4, 0.03], color=ACCENT, stroke_width=4)
        return VGroup(walls, arch)

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
            floor = Line([-1.5, -1.6, 0], [1.5, -1.6, 0], color=INK, stroke_width=5)
            ball = Dot([0, -1.45, 0], color=ACCENT, radius=0.15)
            return VGroup(floor, ball, Text("sits still", font=FONT, font_size=28, color=INK).move_to([0, -2.7, 0]))
        if bid == "H02":
            arch = ParametricFunction(lambda x: [x, -1.7 + 1.0 * np.sin(np.pi * (x + 1.4) / 2.8), 0],
                                      t_range=[-1.4, 1.4, 0.03], color=ACCENT, stroke_width=4)
            return VGroup(arch, Text("never holds still", font=FONT, font_size=28, color=INK).move_to([0, -2.8, 0]))
        return None

    def _A01(self, w):
        t = dur("A01")
        zeros = VGroup(Dot([-3, FLOOR, 0], color=INK), Dot([3, FLOOR, 0], color=INK))
        zlabel = VGroup(Text("0", font=FONT, font_size=24, color=INK).next_to(zeros[0], DOWN, buff=0.15),
                        Text("0", font=FONT, font_size=24, color=INK).next_to(zeros[1], DOWN, buff=0.15))
        self.play(Create(w), run_time=t * 0.6)
        self.play(FadeIn(zeros), FadeIn(zlabel), run_time=t * 0.3)
        self.wait(max(0.1, t * 0.1))
        self._zeros = VGroup(zeros, zlabel)

    # ── A02 — flat still wave fails ───────────────────────────────────────────
    def _A02(self, w):
        t = dur("A02")
        flat = Line([-3, FLOOR, 0], [3, FLOOR, 0], color=FORBID, stroke_width=7)
        cross = Text("nothing there", font=FONT, font_size=26, color=FORBID).next_to(flat, UP, buff=0.2)
        self.play(Create(flat), run_time=t * 0.4)
        self.play(FadeIn(cross), run_time=t * 0.2)
        self.play(FadeOut(flat, cross), run_time=t * 0.35)
        self.wait(max(0.1, t * 0.05))

    # ── A03 — the half-sine arch ──────────────────────────────────────────────
    def _A03(self, w):
        t = dur("A03")
        a = arch()
        self.play(Create(a), run_time=t * 0.75)
        self.wait(max(0.2, t * 0.25))
        return a

    # ── A04 — curvature = energy ──────────────────────────────────────────────
    def _A04(self, a):
        t = dur("A04")
        peak = [0, FLOOR + PEAK, 0]
        curl = Arc(radius=0.5, start_angle=PI * 0.15, angle=PI * 0.7, arc_center=peak, color=ACCENT, stroke_width=5)
        lbl = Text("curvature = energy", font=FONT, font_size=26, color=ACCENT).next_to([0, FLOOR + PEAK, 0], UP, buff=0.35)
        self.play(Create(curl), FadeIn(lbl), run_time=t * 0.7)
        self.wait(max(0.2, t * 0.3))
        self.play(FadeOut(curl, lbl), run_time=0.01)

    # ── A05 — can't flatten ───────────────────────────────────────────────────
    def _A05(self, a):
        t = dur("A05")
        self.play(a.animate.stretch(0.32, 1, about_point=[0, FLOOR, 0]), run_time=t * 0.4)
        self.play(a.animate.stretch(1 / 0.32, 1, about_point=[0, FLOOR, 0]), run_time=t * 0.4)
        self.wait(max(0.2, t * 0.2))

    # ── A06 — ground state above zero ─────────────────────────────────────────
    def _A06(self, w, a):
        t = dur("A06")
        e_level = DashedLine([-3.4, FLOOR + 0.55, 0], [3.4, FLOOR + 0.55, 0], color=ACCENT, stroke_width=3)
        gap = DoubleArrow([3.2, FLOOR, 0], [3.2, FLOOR + 0.55, 0], color=INK, buff=0, stroke_width=3, tip_length=0.12)
        glabel = Text("never zero", font=FONT, font_size=24, color=ACCENT).next_to(e_level, RIGHT, buff=0.1).shift(UP * 0.1)
        self.play(Create(e_level), GrowArrow(gap), FadeIn(glabel), run_time=t * 0.7)
        self.wait(max(0.2, t * 0.3))

    # ── A07–A08 — squeeze ─────────────────────────────────────────────────────
    def _A07_A08(self):
        t7 = dur("A07")
        w = walls(3.0)
        a = arch(3.0)
        self.play(Create(w), Create(a), run_time=t7 * 0.3)
        w2, a2 = walls(1.8), arch(1.8)
        self.play(Transform(w, w2), Transform(a, a2), run_time=t7 * 0.5)
        rise = Text("energy rises", font=FONT, font_size=26, color=ACCENT).move_to([0, FLOOR + 3.2, 0])
        self.play(FadeIn(rise, shift=UP * 0.2), run_time=t7 * 0.2)

        t8 = dur("A08")
        e_level = DashedLine([-1.8, FLOOR + 0.9, 0], [1.8, FLOOR + 0.9, 0], color=ACCENT, stroke_width=3)
        glabel = Text("E1 · ground state", font=FONT, font_size=26, color=INK).next_to(e_level, UP, buff=0.15)
        self.play(FadeOut(rise), Create(e_level), FadeIn(glabel), run_time=t8 * 0.6)
        self.wait(max(0.2, t8 * 0.4))

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
