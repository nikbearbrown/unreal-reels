"""
double_slit_fringes_worked.py
=============================
Bear's Notes — deep / long-form expand of "Why One Electron at a Time Still Builds
Stripes". 16:9 ONLY. Intuition (waves through both slits) -> idea-to-math
(de Broglie lambda=h/p; d sin(theta)=m lambda; fringe spacing dy = lambda L / d)
-> worked example (100 V electron: lambda~0.12 nm, d=100nm, L=0.5m -> dy~0.6 mm)
-> predicts (faster -> tighter; Tonomura 1989) -> recap. SILENT. MathTex math.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim -qh double_slit_fringes_worked.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/manim_layout_audit.py double_slit_fringes_worked.py
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
TITLE  = "The Double Slit: How Far Apart Are the Stripes?"
CHANNEL = "youtube.com/@NikBearBrown"

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}


def dur(b):
    return float(_T.get(b, 4.0))


def txt(s, size=34, color=INK):
    return Text(s, font=FONT, font_size=size, color=color)


def mtex(s, size=44, color=INK):
    return MathTex(s, color=color).scale(size / 44.0)


def card(s, size=34, width=11.0):
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


def fringes(cx, cy, spacing, n=5, h=1.4, color=ACCENT, sw=7):
    """A row of n bright fringes (vertical bars) centered at (cx,cy)."""
    g = VGroup()
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * spacing
        g.add(Line([x, cy - h / 2, 0], [x, cy + h / 2, 0], color=color, stroke_width=sw))
    return g


class BearsDoodlesVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        self.rng = np.random.default_rng(11)
        self._intro()
        self._hook("H01")
        self._hook("H02")
        self._intuition()
        self._derivation()
        self._worked()
        self._predict()
        self._recap()
        self._outro()

    def _slits(self, x=-4.6, gap=0.45):
        return VGroup(Line([x, -1.6, 0], [x, -gap, 0], color=INK, stroke_width=6),
                      Line([x, gap, 0], [x, 1.6, 0], color=INK, stroke_width=6))

    def _hero(self):
        sl = self._slits(x=-1.0).scale(0.7)
        fr = fringes(1.2, 0.0, 0.32, 4, 1.0, ACCENT, 5)
        return VGroup(sl, fr)

    def _intro(self):
        t = dur("INTRO")
        brand = txt("Bear's Notes", 44).move_to([0, 3.0, 0])
        hero = self._hero().move_to([0, 0.4, 0])
        title = txt(TITLE, 30, ACCENT)
        title.scale_to_fit_width(min(11.0, title.width)).move_to([0, -2.6, 0])
        self.play(FadeIn(brand), run_time=min(0.9, t * 0.25))
        self.play(Create(hero), run_time=min(1.6, t * 0.4))
        self.play(Write(title), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 3.7))
        self.play(FadeOut(brand, hero, title), run_time=0.4)

    def _hook(self, bid):
        t = dur(bid)
        msg = {"H01": "One electron at a time still piles up into stripes.",
               "H02": "And the spacing of those stripes is something we can predict."}[bid]
        c = card(msg, 36).to_edge(UP, buff=1.0)
        fr = fringes(0, -1.0, 0.5, 5, 1.6, ACCENT, 8)
        if bid == "H02":
            br = DoubleArrow([-0.25, -2.0, 0], [0.25, -2.0, 0], buff=0, color=INK, stroke_width=3, tip_length=0.12)
            dy = mtex(r"\Delta y", 30).next_to(br, DOWN, buff=0.1)
            fr = VGroup(fr, br, dy)
        self.play(Write(c), run_time=min(1.3, t * 0.4))
        self.play(Create(fr), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 2.7))
        self.play(FadeOut(c, fr), run_time=0.4)

    # ── A — intuition ───────────────────────────────────────────────────────
    def _intuition(self):
        t1 = dur("A01")
        sl = self._slits(x=-4.6)
        scr = Line([4.6, -2.4, 0], [4.6, 2.4, 0], color=INK, stroke_width=5)
        waves = VGroup()
        for sy in (-0.45, 0.45):
            for r in (0.8, 1.6, 2.4, 3.2):
                waves.add(Arc(radius=r, start_angle=-1.1, angle=2.2,
                              arc_center=[-4.6, sy, 0], color=ACCENT, stroke_width=2.2))
        self.play(Create(sl), Create(scr), run_time=t1 * 0.4)
        self.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=0.03), run_time=t1 * 0.6)

        t2 = dur("A02")
        p1 = Line([-4.6, 0.45, 0], [4.6, 0.8, 0], color=RED, stroke_width=3)
        p2 = Line([-4.6, -0.45, 0], [4.6, 0.8, 0], color=RED, stroke_width=3)
        dot = Dot([4.6, 0.8, 0], color=RED, radius=0.1)
        lbl = txt("paths differ by one wavelength", 24, RED).move_to([0, 2.7, 0])
        self.play(Create(p1), Create(p2), FadeIn(dot), FadeIn(lbl), run_time=t2 * 0.8)
        self.wait(max(0.2, t2 * 0.2))
        self.play(FadeOut(sl, scr, waves, p1, p2, dot, lbl), run_time=0.5)

    # ── M — idea -> math ────────────────────────────────────────────────────
    def _derivation(self):
        t1 = dur("M01")
        sl = self._slits(x=-5.2).scale(0.9)
        self.play(Create(sl), run_time=t1)
        f1 = mtex(r"\lambda = \frac{h}{p}", 44).move_to([1.8, 2.0, 0])
        f2 = mtex(r"d\,\sin\theta = m\lambda", 44).move_to([1.8, 0.5, 0])
        res = mtex(r"\Delta y = \frac{\lambda L}{d}", 50).move_to([1.8, -1.4, 0])
        self.play(Write(f1), run_time=dur("M02") * 0.8); self.wait(max(0.1, dur("M02") * 0.2))
        self.play(Write(f2), run_time=dur("M03") * 0.8); self.wait(max(0.1, dur("M03") * 0.2))
        boxr = SurroundingRectangle(res, color=ACCENT, buff=0.18)
        self.play(Write(res), Create(boxr), run_time=dur("M04") * 0.8); self.wait(max(0.1, dur("M04") * 0.2))
        self._res = VGroup(res, boxr)
        self.play(FadeOut(sl, f1, f2), run_time=0.5)

    # ── W — worked example ──────────────────────────────────────────────────
    def _worked(self):
        self.play(self._res.animate.scale(0.8).move_to([0, 3.0, 0]), run_time=dur("W01"))
        given = txt("electron through 100 V", 28, INK).move_to([-3.4, 1.8, 0])
        self.play(FadeIn(given), run_time=0.1)
        lines = [mtex(r"\lambda = \frac{h}{p} \approx 0.12\ \text{nm}", 36),
                 mtex(r"d = 100\,\text{nm},\ \ L = 0.5\,\text{m}", 34),
                 mtex(r"\Delta y = \frac{\lambda L}{d} \approx 0.6\ \text{mm}", 40, RED)]
        VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to([-3.0, -0.3, 0])
        fr = fringes(3.6, 0.2, 0.5, 5, 1.6, ACCENT, 8)
        br = DoubleArrow([3.35, -1.0, 0], [3.85, -1.0, 0], buff=0, color=RED, stroke_width=3, tip_length=0.12)
        self.play(Write(lines[0]), run_time=dur("W02"))
        self.play(Write(lines[1]), Create(fr), run_time=dur("W03"))
        self.play(Write(lines[2]), GrowArrow(br), run_time=dur("W04") * 0.85)
        self.wait(max(0.1, dur("W04") * 0.15))
        self.play(FadeOut(given, *lines, fr, br, self._res), run_time=0.5)

    # ── P — predicts ──────────────────────────────────────────────────────────
    def _predict(self):
        t1 = dur("P01")
        wide = VGroup(fringes(-3.2, 1.4, 0.7, 4, 1.1, ACCENT, 7),
                      txt("slow → wide", 24, INK).move_to([-3.2, -0.2, 0]))
        tight = VGroup(fringes(3.2, 1.4, 0.32, 7, 1.1, ACCENT, 5),
                       txt("fast → tight", 24, INK).move_to([3.2, -0.2, 0]))
        self.play(Create(wide), run_time=t1 * 0.5)
        self.play(Create(tight), run_time=t1 * 0.5)

        t2 = dur("P02")
        dots = VGroup(*[Dot([self.rng.uniform(-2.5, 2.5), -2.2 + self.rng.uniform(-0.1, 0.1), 0],
                            radius=0.04, color=INK) for _ in range(60)])
        tono = txt("Tonomura, 1989", 24, ACCENT).move_to([0, -3.0, 0])
        self.play(FadeIn(dots, lag_ratio=0.02), FadeIn(tono), run_time=t2 * 0.8)
        self.wait(max(0.2, t2 * 0.2))
        self.play(FadeOut(wide, tight, dots, tono), run_time=0.5)

    # ── R — recap ─────────────────────────────────────────────────────────────
    def _recap(self):
        res = mtex(r"\Delta y = \frac{\lambda L}{d}", 54, RED).move_to([0, 1.2, 0])
        box = SurroundingRectangle(res, color=RED, buff=0.2)
        self.play(Write(res), Create(box), run_time=dur("R01") * 0.8); self.wait(max(0.1, dur("R01") * 0.2))
        line = card("Random alone, lawful together — the wave sets the odds.", 32).move_to([0, -1.2, 0])
        self.play(Write(line), run_time=dur("R02") * 0.8); self.wait(max(0.1, dur("R02") * 0.2))
        self.play(FadeOut(res, box, line), run_time=0.4)

    def _outro(self):
        t = dur("OUTRO")
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)
        thanks = txt("Thanks for watching", 44).move_to([0, 1.7, 0])
        title = txt(TITLE, 30, ACCENT)
        title.scale_to_fit_width(min(11.0, title.width)).move_to([0, 0.1, 0])
        url = txt(CHANNEL, 36).move_to([0, -1.7, 0])
        self.play(Write(thanks), run_time=1.2)
        self.play(FadeIn(title), run_time=1.0)
        self.play(Write(url), run_time=1.2)
        self.wait(max(0.6, t - 4.0))
