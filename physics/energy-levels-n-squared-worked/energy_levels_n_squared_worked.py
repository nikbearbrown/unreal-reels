"""
energy_levels_n_squared_worked.py
=================================
Bear's Notes — deep / long-form expand of "energy levels aren't evenly spaced".
16:9 ONLY. Intuition recap -> idea-to-math derivation -> worked example (real
numbers) -> quantum-dot prediction -> recap. Text = Shadows Into Light; math =
MathTex (LaTeX/MacTeX). SILENT (assemble.py muxes the voiceover).

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim -qh energy_levels_n_squared_worked.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/manim_layout_audit.py energy_levels_n_squared_worked.py
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
BLUE   = "#3A6EA5"
FONT   = "Shadows Into Light"
TITLE  = "Where the n² Energy Formula Comes From"
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


def card(s, size=40, width=11.0):
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


def wave_n(n, x0, x1, yc, amp):
    return ParametricFunction(
        lambda x: [x, yc + amp * np.sin(n * np.pi * (x - x0) / (x1 - x0)), 0],
        t_range=[x0, x1, 0.01], color=ACCENT, stroke_width=5)


class BearsDoodlesVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        self._intro()
        self._hook("H01", "You'd expect an energy ladder with evenly spaced rungs.")
        self._hook("H02", "But a quantum box's rungs fan apart the higher you climb.")
        self._intuition()
        self._derivation()
        self._worked()
        self._predict()
        self._recap()
        self._outro()

    # ── INTRO ────────────────────────────────────────────────────────────────
    def _hero(self):
        ys = [-1.0, -0.4, 0.5, 1.7]   # rungs that fan apart (n^2-ish)
        return VGroup(*[Line([-1.3, y, 0], [1.3, y, 0], color=ACCENT, stroke_width=5) for y in ys])

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

    # ── HOOKS ────────────────────────────────────────────────────────────────
    def _hook(self, bid, fallback):
        t = dur(bid)
        c = card(fallback, 38).to_edge(UP, buff=1.0)
        if bid == "H01":
            sk = VGroup(*[Line([-1.6, y, 0], [1.6, y, 0], color=ACCENT, stroke_width=6)
                          for y in (-1.4, -0.8, -0.2, 0.4)])
        else:
            sk = VGroup(*[Line([-1.6, y, 0], [1.6, y, 0], color=ACCENT, stroke_width=6)
                          for y in (-1.5, -1.0, -0.1, 1.3)])
        sk.move_to([0, -0.8, 0])
        self.play(Write(c), run_time=min(1.3, t * 0.4))
        self.play(Create(sk), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 2.7))
        self.play(FadeOut(c, sk), run_time=0.4)

    # ── A — intuition recap ──────────────────────────────────────────────────
    def _intuition(self):
        # box left, energy axis right
        lx0, lx1, yc, amp = -5.8, -2.8, 0.0, 0.8
        walls = VGroup(
            Line([lx0, -1.7, 0], [lx0, 1.7, 0], color=INK, stroke_width=7),
            Line([lx1, -1.7, 0], [lx1, 1.7, 0], color=INK, stroke_width=7),
            DashedLine([lx0, yc, 0], [lx1, yc, 0], color=GHOST, stroke_width=2))
        ax, rx, e0, k = 0.8, 3.6, -2.4, 0.30
        h = lambda n: e0 + k * n * n
        axis = Arrow([ax, -2.7, 0], [ax, 3.0, 0], buff=0, color=INK, stroke_width=4)
        elabel = txt("energy", 24).next_to(axis, UP, buff=0.12)

        t1 = dur("A01")
        wave = wave_n(1, lx0, lx1, yc, amp)
        nlbl = txt("n = 1", 26).move_to([(lx0 + lx1) / 2, 2.3, 0])
        self.play(Create(walls), GrowArrow(axis), FadeIn(elabel), run_time=t1 * 0.5)
        self.play(Create(wave), FadeIn(nlbl), run_time=t1 * 0.5)

        t2 = dur("A02")
        for n in (2, 3, 4):
            self.play(Transform(wave, wave_n(n, lx0, lx1, yc, amp)),
                      Transform(nlbl, txt(f"n = {n}", 26).move_to([(lx0 + lx1) / 2, 2.3, 0])),
                      run_time=t2 / 3.0)

        t3 = dur("A03")
        rungs, vals = VGroup(), VGroup()
        for n in (1, 2, 3, 4):
            y = h(n)
            rungs.add(DashedLine([ax, y, 0], [rx, y, 0], color=ACCENT, stroke_width=4),
                      Dot([ax, y, 0], color=ACCENT, radius=0.07))
            vals.add(txt(str(n * n), 26).move_to([rx + 0.45, y, 0]))
        self.play(LaggedStart(*[Create(m) for m in rungs], lag_ratio=0.1),
                  LaggedStart(*[FadeIn(m) for m in vals], lag_ratio=0.1), run_time=t3)

        t4 = dur("A04")
        gaps = VGroup()
        for (a, b, g) in [(1, 2, "3"), (2, 3, "5"), (3, 4, "7")]:
            gaps.add(DoubleArrow([ax - 0.5, h(a), 0], [ax - 0.5, h(b), 0], buff=0,
                                 color=RED, stroke_width=3, tip_length=0.14),
                     txt(g, 22, RED).move_to([ax - 0.95, (h(a) + h(b)) / 2, 0]))
        self.play(FadeIn(gaps), run_time=t4 * 0.8)
        self.wait(max(0.2, t4 * 0.2))
        self.play(FadeOut(walls, wave, nlbl, rungs, vals, axis, elabel, gaps), run_time=0.5)

    # ── M — idea -> math ─────────────────────────────────────────────────────
    def _derivation(self):
        # small box+wave on the left as a reminder
        lx0, lx1 = -6.0, -3.4
        box = VGroup(Line([lx0, -1.2, 0], [lx0, 1.2, 0], color=INK, stroke_width=6),
                     Line([lx1, -1.2, 0], [lx1, 1.2, 0], color=INK, stroke_width=6))
        wave = wave_n(2, lx0, lx1, 0.0, 0.55)
        brace = Brace(Line([lx0, -1.4, 0], [lx1, -1.4, 0]), DOWN, color=INK)
        Llab = mtex("L", 34).next_to(brace, DOWN, buff=0.1)

        t1 = dur("M01")
        self.play(Create(box), Create(wave), run_time=t1 * 0.7)
        self.wait(max(0.1, t1 * 0.3))

        t2 = dur("M02")
        nlab = txt("n half-waves", 26).move_to([(lx0 + lx1) / 2, 1.7, 0])
        self.play(FadeIn(nlab), GrowFromCenter(brace), Write(Llab), run_time=t2)

        # formula stack on the right
        f1 = mtex(r"\lambda_n = \frac{2L}{n}", 44).move_to([2.4, 2.0, 0])
        f2 = mtex(r"p = \frac{h}{\lambda}", 44).move_to([2.4, 0.6, 0])
        f3 = mtex(r"E = \frac{p^2}{2m}", 44).move_to([2.4, -0.8, 0])
        res = mtex(r"E_n = \frac{n^2 h^2}{8 m L^2}", 50, INK).move_to([2.4, -2.6, 0])

        self.play(Write(f1), run_time=dur("M03") * 0.7); self.wait(max(0.1, dur("M03") * 0.3))
        self.play(Indicate(VGroup(wave, f1), color=ACCENT, scale_factor=1.05), run_time=dur("M04"))
        self.play(Write(f2), run_time=dur("M05") * 0.7); self.wait(max(0.1, dur("M05") * 0.3))
        self.play(Write(f3), run_time=dur("M06") * 0.7); self.wait(max(0.1, dur("M06") * 0.3))
        self.play(Indicate(VGroup(f1, f2, f3), color=ACCENT), run_time=dur("M07"))
        box_res = SurroundingRectangle(res, color=ACCENT, buff=0.18)
        self.play(Write(res), Create(box_res), run_time=dur("M08") * 0.8); self.wait(max(0.1, dur("M08") * 0.2))
        self.play(Indicate(res, color=RED, scale_factor=1.06), run_time=dur("M09"))

        self._res_group = VGroup(res, box_res)
        self.play(FadeOut(box, wave, brace, Llab, nlab, f1, f2, f3), run_time=0.5)

    # ── W — worked example ───────────────────────────────────────────────────
    def _worked(self):
        res = self._res_group
        self.play(res.animate.scale(0.85).move_to([0, 3.0, 0]), run_time=dur("W01"))

        givens = mtex(r"L = 1\,\text{nm},\ \ m = m_e", 36).move_to([-3.6, 1.7, 0])
        self.play(Write(givens), run_time=dur("W02"))

        lines = [
            mtex(r"E_1 \approx 0.38\,\text{eV}", 40),
            mtex(r"E_2 = 4E_1 \approx 1.5\,\text{eV}", 40),
            mtex(r"\Delta E \approx 1.1\,\text{eV}", 40, RED),
            mtex(r"\lambda = \frac{hc}{\Delta E} \approx 1100\,\text{nm}", 40),
        ]
        VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to([-3.4, -1.2, 0])

        # mini ladder on the right
        ax, e0, k = 3.6, -1.6, 0.55
        h = lambda n: e0 + k * n * n
        axis = Arrow([ax, -2.2, 0], [ax, 2.2, 0], buff=0, color=INK, stroke_width=4)
        r1 = VGroup(DashedLine([ax, h(1), 0], [ax + 2.0, h(1), 0], color=ACCENT, stroke_width=4),
                    mtex(r"E_1", 30).move_to([ax + 2.4, h(1), 0]))
        r2 = VGroup(DashedLine([ax, h(2), 0], [ax + 2.0, h(2), 0], color=ACCENT, stroke_width=4),
                    mtex(r"E_2", 30).move_to([ax + 2.4, h(2), 0]))
        self.play(GrowArrow(axis), run_time=0.4)

        self.play(Write(lines[0]), Create(r1), run_time=dur("W03"))
        self.play(Write(lines[1]), Create(r2), run_time=dur("W04"))
        gap = DoubleArrow([ax - 0.4, h(1), 0], [ax - 0.4, h(2), 0], buff=0, color=RED,
                          stroke_width=3, tip_length=0.14)
        self.play(Write(lines[2]), GrowArrow(gap), run_time=dur("W05"))
        photon = ArcBetweenPoints([ax - 0.4, (h(1) + h(2)) / 2, 0], [ax + 1.6, 1.9, 0],
                                  color=RED, stroke_width=4)
        self.play(Create(photon), run_time=dur("W06"))
        self.play(Write(lines[3]), run_time=dur("W07"))
        irlab = txt("near-infrared", 24, ACCENT).move_to([ax + 0.6, -2.7, 0])
        self.play(FadeIn(irlab), run_time=dur("W08") * 0.8); self.wait(max(0.1, dur("W08") * 0.2))
        self.play(FadeOut(givens, *lines, axis, r1, r2, gap, photon, irlab, res), run_time=0.5)

    # ── P — prediction (quantum dots) ────────────────────────────────────────
    def _predict(self):
        t1 = dur("P01")
        small = VGroup(Line([-4.6, -0.8, 0], [-4.6, 0.8, 0], color=INK, stroke_width=6),
                       Line([-3.4, -0.8, 0], [-3.4, 0.8, 0], color=INK, stroke_width=6))
        lab = txt("quantum dot", 26).next_to(small, UP, buff=0.3)
        self.play(Create(small), FadeIn(lab), run_time=t1)

        rel = mtex(r"E \propto \frac{1}{L^2}", 48).move_to([0, 2.0, 0])
        self.play(Write(rel), run_time=dur("P02"))

        big = VGroup(Line([2.6, -1.3, 0], [2.6, 1.3, 0], color=INK, stroke_width=6),
                     Line([4.8, -1.3, 0], [4.8, 1.3, 0], color=INK, stroke_width=6))
        sdot = Dot([-4.0, 0.0, 0], color=BLUE, radius=0.16)
        bdot = Dot([3.7, 0.0, 0], color=RED, radius=0.16)
        sgl = txt("small → blue", 24, BLUE).next_to(small, DOWN, buff=0.4)
        bgl = txt("large → red", 24, RED).next_to(big, DOWN, buff=0.4)
        self.play(Create(big), FadeIn(sdot, bdot, sgl, bgl), run_time=dur("P03"))

        res = mtex(r"E_n = \frac{n^2 h^2}{8 m L^2}", 40).move_to([0, -2.7, 0])
        self.play(Write(res), run_time=dur("P04") * 0.8); self.wait(max(0.1, dur("P04") * 0.2))
        self.play(FadeOut(small, lab, rel, big, sdot, bdot, sgl, bgl, res), run_time=0.5)

    # ── R — recap ────────────────────────────────────────────────────────────
    def _recap(self):
        c1 = card("The rungs fan out as n² because energy lives in the square of the momentum.", 34)
        c1.move_to([0, 1.6, 0])
        ep = mtex(r"E \sim p^2", 48, RED).move_to([0, -0.2, 0])
        self.play(Write(c1), run_time=dur("R01") * 0.7); self.wait(max(0.1, dur("R01") * 0.3))
        self.play(FadeIn(ep), run_time=dur("R02"))
        res = mtex(r"E_n = \frac{n^2 h^2}{8 m L^2}", 46).move_to([0, -2.3, 0])
        self.play(Write(res), run_time=dur("R03") * 0.8); self.wait(max(0.1, dur("R03") * 0.2))
        self.play(FadeOut(c1, ep, res), run_time=0.4)

    # ── OUTRO ────────────────────────────────────────────────────────────────
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
