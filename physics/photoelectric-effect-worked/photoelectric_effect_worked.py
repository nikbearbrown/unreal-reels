"""
photoelectric_effect_worked.py
==============================
Bear's Notes — deep / long-form expand of "Why a Dim Blue Lamp Beats a Blinding
Red One". 16:9 ONLY. Intuition recap -> idea-to-math (E=hf, work function, K_max
= hf - phi) -> worked example (sodium: blue ejects, red never) -> what it predicts
-> recap. Text = Shadows Into Light; math = MathTex (LaTeX/MacTeX). SILENT.

Verified numbers (hc = 1240 eV*nm): phi_Na = 2.28 eV; blue 450nm -> 2.76 eV ->
K = 0.48 eV (ejects); red 700nm -> 1.77 eV < phi -> no ejection; threshold 544 nm.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim -qh photoelectric_effect_worked.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/manim_layout_audit.py photoelectric_effect_worked.py
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
BLUE   = "#2A6FB0"
GHOST  = "#C9BFBC"
FONT   = "Shadows Into Light"
TITLE  = "The Photoelectric Effect: Why Colour Beats Brightness"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}


def dur(b):
    return float(_T.get(b, 4.0))


def txt(s, size=34, color=INK):
    return Text(s, font=FONT, font_size=size, color=color)


def mtex(s, size=44, color=INK):
    return MathTex(s, color=color).scale(size / 44.0)


def card(s, size=38, width=11.0):
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


def packet(x, y, color, r=0.15):
    return Dot([x, y, 0], radius=r, color=color)


class BearsDoodlesVideo(Scene):
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

    # ── INTRO ──────────────────────────────────────────────────────────────
    def _hero(self):
        plate = Line([-1.4, -0.9, 0], [1.0, -0.9, 0], color=INK, stroke_width=6)
        ray = Arrow([-1.2, 1.0, 0], [-0.4, -0.7, 0], color=BLUE, buff=0, stroke_width=5)
        e = Dot([0.1, -0.3, 0], color=BLUE, radius=0.14)
        ea = Arrow([0.1, -0.4, 0], [1.4, 0.9, 0], color=BLUE, buff=0, stroke_width=4)
        return VGroup(plate, ray, e, ea)

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

    # ── HOOKS ──────────────────────────────────────────────────────────────
    def _hook(self, bid):
        t = dur(bid)
        c = card(self._narr(bid), 36).to_edge(UP, buff=1.0)
        plate = Line([-1.6, -1.4, 0], [1.6, -1.4, 0], color=INK, stroke_width=6)
        if bid == "H01":
            redray = Arrow([-1.6, 0.0, 0], [-0.9, -1.2, 0], color=RED, buff=0, stroke_width=5)
            x = VGroup(Line([-1.2, -1.0, 0], [-0.6, -1.6, 0], color=RED, stroke_width=5),
                       Line([-1.2, -1.6, 0], [-0.6, -1.0, 0], color=RED, stroke_width=5))
            blueray = Arrow([0.8, 0.0, 0], [1.2, -1.2, 0], color=BLUE, buff=0, stroke_width=5)
            e = Dot([1.4, -1.2, 0], color=BLUE, radius=0.12)
            ea = Arrow([1.4, -1.2, 0], [2.0, 0.2, 0], color=BLUE, buff=0, stroke_width=4)
            sk = VGroup(plate, redray, x, blueray, e, ea)
        else:
            sk = VGroup(packet(-1.0, -0.6, RED, 0.13), txt("red · weak", 24, RED).move_to([-1.0, -1.4, 0]),
                        packet(1.0, -0.3, BLUE, 0.22), txt("blue · strong", 24, BLUE).move_to([1.0, -1.4, 0]))
        self.play(Write(c), run_time=min(1.3, t * 0.4))
        self.play(Create(sk), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 2.7))
        self.play(FadeOut(c, sk), run_time=0.4)

    def _narr(self, bid):
        return {"H01": "A blinding red lamp frees no electrons; a faint blue one frees them instantly.",
                "H02": "Light's energy arrives in fixed, colour-sized packets."}.get(bid, "")

    # ── A — intuition ───────────────────────────────────────────────────────
    def _plate(self, y=-1.6, x0=-3.0, x1=3.0):
        bar = Line([x0, y, 0], [x1, y, 0], color=INK, stroke_width=7)
        es = VGroup(*[Dot([x0 + 0.6 + i * 0.7, y + 0.12, 0], radius=0.09, color=INK) for i in range(7)])
        return bar, es

    def _intuition(self):
        t1 = dur("A01")
        bar, es = self._plate()
        packs = VGroup(*[packet(-2.4 + i * 0.8, 2.6, INK, 0.12) for i in range(7)])
        self.play(Create(bar), FadeIn(es), run_time=t1 * 0.5)
        self.play(packs.animate.shift(DOWN * 3.0), run_time=t1 * 0.5)
        self.play(FadeOut(packs), run_time=0.2)

        t2 = dur("A02")
        thr = DashedLine([-3.2, 0.2, 0], [3.2, 0.2, 0], color=ACCENT, stroke_width=3)
        tl = txt("escape energy", 24, ACCENT).next_to(thr, RIGHT, buff=0.1)
        redbar = Line([-1.5, -1.6, 0], [-1.5, -0.5, 0], color=RED, stroke_width=10)
        rl = txt("red · weak", 24, RED).next_to(redbar, UP, buff=0.12)
        bluebar = Line([1.5, -1.6, 0], [1.5, 1.2, 0], color=BLUE, stroke_width=10)
        bl = txt("blue · strong", 24, BLUE).next_to(bluebar, UP, buff=0.12)
        self.play(GrowFromEdge(redbar, DOWN), FadeIn(rl), run_time=t2 * 0.5)
        self.play(GrowFromEdge(bluebar, DOWN), FadeIn(bl), run_time=t2 * 0.5)

        t3 = dur("A03")
        self.play(Create(thr), FadeIn(tl), run_time=t3 * 0.5)
        self.play(Indicate(bluebar, color=BLUE), Indicate(thr, color=ACCENT), run_time=t3 * 0.3)
        self.wait(max(0.2, t3 * 0.2))
        self.play(FadeOut(bar, es, thr, tl, redbar, rl, bluebar, bl), run_time=0.5)

    # ── M — idea -> math ──────────────────────────────────────────────────────
    def _derivation(self):
        t1 = dur("M01")
        bar = Line([-6.0, -1.4, 0], [-3.6, -1.4, 0], color=INK, stroke_width=6)
        ray = Arrow([-5.4, 0.6, 0], [-4.8, -1.2, 0], color=BLUE, buff=0, stroke_width=4)
        self.play(Create(bar), Create(ray), run_time=t1)

        f1 = mtex(r"E = hf = \frac{hc}{\lambda}", 44).move_to([2.2, 2.0, 0])
        f2 = txt("work function", 26, ACCENT)
        f2b = mtex(r"\phi", 44, ACCENT)
        f2g = VGroup(f2, f2b).arrange(RIGHT, buff=0.2).move_to([2.2, 0.5, 0])
        res = mtex(r"K_{\max} = hf - \phi", 50, INK).move_to([2.2, -1.1, 0])
        f4 = mtex(r"f_0 = \frac{\phi}{h}", 40).move_to([2.2, -2.6, 0])
        self.play(Write(f1), run_time=dur("M02") * 0.8); self.wait(max(0.1, dur("M02") * 0.2))
        self.play(Write(f2g), run_time=dur("M03") * 0.8); self.wait(max(0.1, dur("M03") * 0.2))
        boxr = SurroundingRectangle(res, color=ACCENT, buff=0.18)
        self.play(Write(res), Create(boxr), run_time=dur("M04") * 0.8); self.wait(max(0.1, dur("M04") * 0.2))
        self.play(Write(f4), run_time=dur("M05") * 0.8); self.wait(max(0.1, dur("M05") * 0.2))
        self._res = VGroup(res, boxr)
        self.play(FadeOut(bar, ray, f1, f2g, f4), run_time=0.5)

    # ── W — worked example ────────────────────────────────────────────────────
    def _worked(self):
        self.play(self._res.animate.scale(0.8).move_to([0, 3.0, 0]), run_time=dur("W01"))
        given = mtex(r"\phi_{\text{Na}} \approx 2.28\ \text{eV}", 38).move_to([-3.4, 1.7, 0])
        self.play(Write(given), run_time=0.1)

        blue = [mtex(r"E_{\text{blue}} = \frac{hc}{450} \approx 2.76\ \text{eV}", 34, BLUE),
                mtex(r"K = 2.76 - 2.28 \approx 0.48\ \text{eV}", 34, BLUE)]
        VGroup(*blue).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to([-3.0, 0.4, 0])
        red = [mtex(r"E_{\text{red}} = \frac{hc}{700} \approx 1.77\ \text{eV}", 34, RED),
               mtex(r"1.77 < 2.28", 34, RED)]
        VGroup(*red).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to([-3.0, -1.8, 0])

        # verdict markers on the right
        ok = VGroup(Dot([3.3, 0.4, 0], color=BLUE, radius=0.14),
                    Arrow([3.3, 0.3, 0], [4.2, 1.4, 0], color=BLUE, buff=0, stroke_width=4),
                    txt("ejects", 26, BLUE).move_to([3.7, -0.2, 0]))
        no = VGroup(Line([3.0, -1.5, 0], [3.6, -2.1, 0], color=RED, stroke_width=6),
                    Line([3.0, -2.1, 0], [3.6, -1.5, 0], color=RED, stroke_width=6),
                    txt("no ejection", 26, RED).move_to([4.4, -1.8, 0]))
        self.play(Write(blue[0]), run_time=dur("W02"))
        self.play(Write(blue[1]), FadeIn(ok), run_time=dur("W03"))
        self.play(Write(red[0]), run_time=dur("W04"))
        self.play(Write(red[1]), FadeIn(no), run_time=dur("W05"))

        t6 = dur("W06")
        lam = mtex(r"\lambda_0 = \frac{hc}{\phi} \approx 544\ \text{nm}", 36).move_to([0, -3.0, 0])
        self.play(Write(lam), run_time=t6 * 0.8); self.wait(max(0.1, t6 * 0.2))
        self.play(FadeOut(given, *blue, *red, ok, no, lam, self._res), run_time=0.5)

    # ── P — predicts ──────────────────────────────────────────────────────────
    def _predict(self):
        t1 = dur("P01")
        bar, es = self._plate(y=-2.2, x0=-2.5, x1=2.5)
        crowd = VGroup(*[packet(-3.0 + (i % 6) * 1.0, 2.4 - (i // 6) * 0.6, RED, 0.1) for i in range(12)])
        self.play(Create(bar), FadeIn(es), run_time=t1 * 0.4)
        self.play(crowd.animate.shift(DOWN * 3.8).set_opacity(0.0),
                  LaggedStart(*[Wiggle(e) for e in es], lag_ratio=0.05), run_time=t1 * 0.6)
        nolbl = txt("0 freed", 28, RED).move_to([0, 1.4, 0])
        self.play(FadeIn(nolbl), run_time=0.2)

        t2 = dur("P02")
        blue = packet(0, 2.6, BLUE, 0.2)
        self.play(blue.animate.move_to([0, -2.05, 0]), run_time=t2 * 0.4)
        freed = es[3]
        self.play(blue.animate.set_opacity(0.0),
                  freed.animate.move_to([0.6, 1.6, 0]).set_color(BLUE),
                  Flash(freed.get_center(), color=BLUE), run_time=t2 * 0.5)
        self.wait(max(0.1, t2 * 0.1))

        t3 = dur("P03")
        ph = packet(-2.4, 1.8, BLUE, 0.18)
        pl = txt("one photon", 26, BLUE).next_to(ph, UP, buff=0.12)
        self.play(GrowFromCenter(ph), FadeIn(pl), Indicate(freed, color=BLUE), run_time=t3 * 0.7)
        self.wait(max(0.2, t3 * 0.3))
        self.play(FadeOut(bar, es, nolbl, freed, ph, pl), run_time=0.5)

    # ── R — recap ─────────────────────────────────────────────────────────────
    def _recap(self):
        res = mtex(r"K_{\max} = hf - \phi", 54, RED).move_to([0, 1.2, 0])
        box = SurroundingRectangle(res, color=RED, buff=0.2)
        self.play(Write(res), Create(box), run_time=dur("R01") * 0.8); self.wait(max(0.1, dur("R01") * 0.2))
        line = card("Colour sets the energy per hit; brightness only sets how many hits.", 32).move_to([0, -1.2, 0])
        self.play(Write(line), run_time=dur("R02") * 0.8); self.wait(max(0.1, dur("R02") * 0.2))
        self.play(FadeOut(res, box, line), run_time=0.4)

    # ── OUTRO ─────────────────────────────────────────────────────────────────
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
