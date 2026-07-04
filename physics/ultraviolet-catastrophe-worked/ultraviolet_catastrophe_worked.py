"""
ultraviolet_catastrophe_worked.py
=================================
Bear's Notes — deep / long-form expand of "The Ultraviolet Catastrophe". 16:9 ONLY.
Intuition (brightness vs frequency) -> idea-to-math (classical kT per mode -> f^2
divergence; Planck E=hf -> Boltzmann freeze-out e^-hf/kT -> Planck's law) -> worked
example (300 K: kT~0.026 eV, UV 5 eV -> e^-193 ~ 1e-84; Wien lambda_max=b/T, 300K
-> 9.7um, 5800K -> 0.50um) -> predicts -> recap. SILENT. MathTex math.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim -qh ultraviolet_catastrophe_worked.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/manim_layout_audit.py ultraviolet_catastrophe_worked.py
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK    = "#1a1a1a"
ACCENT = "#5A5653"
RED    = "#C0392B"
GHOST  = "#C9BFBC"
FONT   = "Shadows Into Light"
TITLE  = "The Ultraviolet Catastrophe: Why Quantizing Energy Fixes It"
CHANNEL = "youtube.com/@NikBearBrown"

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}


def dur(b):
    return float(_T.get(b, 4.0))


def txt(s, size=34, color=INK):
    return Text(s, font=FONT, font_size=size, color=color)


def mtex(s, size=44, color=INK):
    return MathTex(s, color=color).scale(size / 44.0)


def card(s, size=32, width=11.0):
    ws = s.split()
    lines, cur = [], ""
    for w in ws:
        t = (cur + " " + w).strip()
        if cur and len(t) > 34:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    g = VGroup(*[txt(l, size) for l in lines]).arrange(DOWN, buff=0.26)
    if g.width > width:
        g.scale_to_fit_width(width)
    return g


def b_rj(f):
    return 0.17 * f ** 2


def b_planck(f):
    return 1.65 * f ** 3 / (np.exp(0.95 * f) - 1.0)


class BearsDoodlesVideo(Scene):
    # plot mapping (left side)
    X0, Y0, XS, YS, FMAX = -6.0, -2.3, 0.95, 1.05, 6.0

    def P(self, f, b):
        return [self.X0 + f * self.XS, self.Y0 + b * self.YS, 0]

    def construct(self):
        self.camera.background_color = WHITE
        self._intro()
        self._hook("H01")
        self._hook("H02")
        self._intuition()
        self._derivation()
        self._worked()
        self._predict()
        self._recap()
        self._outro()

    def _axes(self):
        xa = Line(self.P(0, 0), self.P(self.FMAX + 0.2, 0), color=INK, stroke_width=4).add_tip(tip_length=0.16)
        ya = Line(self.P(0, 0), self.P(0, 4.6), color=INK, stroke_width=4).add_tip(tip_length=0.16)
        xl = txt("frequency", 22).next_to(xa, RIGHT, buff=0.06).shift(DOWN * 0.12)
        yl = txt("brightness", 22).next_to(ya, UP, buff=0.1)
        return VGroup(xa, ya), VGroup(xl, yl)

    def _rj(self, f_hi=4.6):
        return ParametricFunction(lambda t: self.P(t, b_rj(t)), t_range=[0.05, f_hi, 0.02], color=RED, stroke_width=6)

    def _pl(self):
        return ParametricFunction(lambda t: self.P(t, b_planck(t)), t_range=[0.05, self.FMAX, 0.02], color=ACCENT, stroke_width=6)

    def _hero(self):
        ax = VGroup(Line([-2.2, -1.0, 0], [2.2, -1.0, 0], color=INK, stroke_width=3),
                    Line([-2.2, -1.0, 0], [-2.2, 1.3, 0], color=INK, stroke_width=3))
        pk = ParametricFunction(lambda x: [x, -1.0 + 1.7 * np.exp(-((x + 0.3) / 0.8) ** 2), 0],
                                t_range=[-2.2, 2.2, 0.02], color=ACCENT, stroke_width=4)
        run = ParametricFunction(lambda x: [x, -1.0 + 0.18 * np.exp(1.4 * (x + 2.2)), 0],
                                 t_range=[-2.2, -0.4, 0.02], color=RED, stroke_width=4)
        return VGroup(ax, pk, run)

    def _intro(self):
        t = dur("INTRO")
        brand = txt("Bear's Notes", 44).move_to([0, 3.0, 0])
        hero = self._hero().move_to([0, 0.4, 0])
        title = txt(TITLE, 28, ACCENT)
        title.scale_to_fit_width(min(11.0, title.width)).move_to([0, -2.6, 0])
        self.play(FadeIn(brand), run_time=min(0.9, t * 0.25))
        self.play(Create(hero), run_time=min(1.6, t * 0.4))
        self.play(Write(title), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 3.7))
        self.play(FadeOut(brand, hero, title), run_time=0.4)

    def _hook(self, bid):
        t = dur(bid)
        msg = {"H01": "Classical physics said a warm glow should blast you with ultraviolet.",
               "H02": "It doesn't — the fix was Planck's energy chunks."}[bid]
        c = card(msg, 36).to_edge(UP, buff=1.0)
        ax = VGroup(Line([-2.0, -1.6, 0], [2.0, -1.6, 0], color=INK, stroke_width=3),
                    Line([-2.0, -1.6, 0], [-2.0, 0.6, 0], color=INK, stroke_width=3))
        if bid == "H01":
            cv = ParametricFunction(lambda x: [x, -1.6 + 0.12 * np.exp(1.6 * (x + 2.0)), 0],
                                    t_range=[-2.0, -0.2, 0.02], color=RED, stroke_width=5)
        else:
            cv = ParametricFunction(lambda x: [x, -1.6 + 1.9 * np.exp(-((x + 0.2) / 0.7) ** 2), 0],
                                    t_range=[-2.0, 2.0, 0.02], color=ACCENT, stroke_width=5)
        sk = VGroup(ax, cv)
        self.play(Write(c), run_time=min(1.3, t * 0.4))
        self.play(Create(sk), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 2.7))
        self.play(FadeOut(c, sk), run_time=0.4)

    def _intuition(self):
        t1 = dur("A01")
        axes, labels = self._axes()
        pl = self._pl().set_stroke(opacity=0.3)
        self.play(Create(axes), FadeIn(labels), run_time=t1 * 0.6)
        self.play(Create(pl), run_time=t1 * 0.4)
        t2 = dur("A02")
        rj = self._rj()
        rl = txt("classical → ∞", 24, RED).move_to(self.P(3.4, 4.2))
        self.play(Create(rj), FadeIn(rl), run_time=t2 * 0.8)
        self.wait(max(0.2, t2 * 0.2))
        self._plot = VGroup(axes, labels, pl, rj, rl)
        self.play(FadeOut(self._plot), run_time=0.5)

    def _derivation(self):
        t1 = dur("M01")
        axes, _ = self._axes()
        axes.scale(0.7).to_corner(DL, buff=0.5)
        rj = self._rj().scale(0.7).move_to(axes.get_center() + np.array([0.4, 0.5, 0]))
        self.play(Create(axes), Create(rj), run_time=t1)
        f1 = mtex(r"\bar{E} = kT", 42).move_to([2.4, 2.4, 0])
        f2 = mtex(r"u \propto f^2\,kT \;\to\; \infty", 40, RED).move_to([2.4, 1.2, 0])
        res = mtex(r"E = hf", 50).move_to([2.4, -0.2, 0])
        f4 = mtex(r"e^{-hf/kT}", 40).move_to([2.4, -1.4, 0])
        f5 = mtex(r"u \propto \frac{f^3}{e^{hf/kT}-1}", 40, ACCENT).move_to([2.4, -2.7, 0])
        self.play(Write(f1), run_time=dur("M02") * 0.8); self.wait(max(0.1, dur("M02") * 0.2))
        self.play(Write(f2), run_time=dur("M03") * 0.8); self.wait(max(0.1, dur("M03") * 0.2))
        boxr = SurroundingRectangle(res, color=ACCENT, buff=0.16)
        self.play(Write(res), Create(boxr), run_time=dur("M04") * 0.8); self.wait(max(0.1, dur("M04") * 0.2))
        self.play(Write(f4), run_time=dur("M05") * 0.8); self.wait(max(0.1, dur("M05") * 0.2))
        self.play(Write(f5), run_time=dur("M06") * 0.8); self.wait(max(0.1, dur("M06") * 0.2))
        self._res = VGroup(res, boxr)
        self.play(FadeOut(axes, rj, f1, f2, f4, f5), run_time=0.5)

    def _worked(self):
        self.play(self._res.animate.scale(0.8).move_to([0, 3.1, 0]), run_time=dur("W01"))
        given = txt("room temperature, T = 300 K", 26).move_to([-3.2, 2.0, 0])
        self.play(FadeIn(given), run_time=0.1)
        lines = [mtex(r"kT \approx 0.026\ \text{eV}", 36),
                 mtex(r"\frac{hf}{kT} \approx \frac{5}{0.026} \approx 193", 34),
                 mtex(r"e^{-193} \sim 10^{-84}", 38, RED),
                 mtex(r"\lambda_{\max} = \frac{b}{T} \approx 9.7\,\mu\text{m at }300\,\text{K}", 32)]
        VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([-2.6, -0.4, 0])
        for i, b in enumerate(("W02", "W03", "W04", "W05")):
            self.play(Write(lines[i]), run_time=dur(b))
        # W06 — spectrum strip with two peaks
        t = dur("W06")
        strip = Line([-3.2, -3.0, 0], [3.2, -3.0, 0], color=INK, stroke_width=4)
        irdot = Dot([2.4, -3.0, 0], color=RED, radius=0.1)
        irl = txt("300 K → IR", 22, RED).next_to(irdot, UP, buff=0.1)
        sundot = Dot([-1.4, -3.0, 0], color=ACCENT, radius=0.1)
        sunl = txt("5800 K → visible", 22, ACCENT).next_to(sundot, UP, buff=0.1)
        self.play(Create(strip), FadeIn(irdot, irl, sundot, sunl), run_time=t * 0.85)
        self.wait(max(0.1, t * 0.15))
        self.play(FadeOut(given, *lines, strip, irdot, irl, sundot, sunl, self._res), run_time=0.5)

    def _predict(self):
        t = dur("P01")
        axes, labels = self._axes()
        axes.scale(0.85).move_to([0, -0.3, 0]); labels.scale(0.85)
        cool = ParametricFunction(lambda u: [(-4.5 + 6 * u), -1.6 + 1.4 * np.exp(-(((-4.5 + 6 * u) + 2.5) / 1.2) ** 2), 0],
                                  t_range=[0, 1, 0.02], color="#B23B3B", stroke_width=5)
        hot = ParametricFunction(lambda u: [(-4.5 + 6 * u), -1.6 + 2.4 * np.exp(-(((-4.5 + 6 * u) + 0.2) / 1.0) ** 2), 0],
                                 t_range=[0, 1, 0.02], color=ACCENT, stroke_width=5)
        lab = txt("hotter → peak slides toward visible", 24, INK).move_to([0, 2.6, 0])
        self.play(Create(cool), run_time=t * 0.4)
        self.play(Create(hot), FadeIn(lab), run_time=t * 0.4)
        self.wait(max(0.2, t * 0.2))
        self.play(FadeOut(cool, hot, lab), run_time=0.4)

    def _recap(self):
        res = mtex(r"E = hf", 56, ACCENT).move_to([0, 1.2, 0])
        box = SurroundingRectangle(res, color=ACCENT, buff=0.2)
        self.play(Write(res), Create(box), run_time=dur("R01") * 0.8); self.wait(max(0.1, dur("R01") * 0.2))
        line = card("No infinity — just a peak that climbs with temperature.", 32).move_to([0, -1.2, 0])
        self.play(Write(line), run_time=dur("R02") * 0.8); self.wait(max(0.1, dur("R02") * 0.2))
        self.play(FadeOut(res, box, line), run_time=0.4)

    def _outro(self):
        t = dur("OUTRO")
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)
        thanks = txt("Thanks for watching", 44).move_to([0, 1.7, 0])
        title = txt(TITLE, 28, ACCENT)
        title.scale_to_fit_width(min(11.0, title.width)).move_to([0, 0.1, 0])
        url = txt(CHANNEL, 36).move_to([0, -1.7, 0])
        self.play(Write(thanks), run_time=1.2)
        self.play(FadeIn(title), run_time=1.0)
        self.play(Write(url), run_time=1.2)
        self.wait(max(0.6, t - 4.0))
