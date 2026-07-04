"""
atom_and_laser_quantize_worked.py
=================================
Bear's Notes — deep / long-form expand of "Why an Atom and a Laser Cavity
Quantize for the Same Reason". 16:9 ONLY. Intuition (a wave fits between two walls)
-> idea-to-math (one rule n*lambda/2 = L, branching to f_n = nc/2L for a cavity and
E_n = n^2 h^2 / 8 m L^2 for a box) -> worked example (0.30 m cavity -> 500 MHz mode
spacing, ~9.5e5 half-waves at 633 nm; 1 nm box -> E1~0.38 eV, E2~1.5 eV)
-> predicts (bigger L -> tighter rungs) -> recap. SILENT. MathTex math.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim -qh atom_and_laser_quantize_worked.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/manim_layout_audit.py atom_and_laser_quantize_worked.py
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
TITLE  = "Why an Atom and a Laser Quantize for the Same Reason"
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


def vwave(fn, xc, yb, yt, color=ACCENT, sw=6):
    """A wave running vertically (yb->yt) with horizontal displacement fn(s)."""
    return ParametricFunction(lambda s: [xc + fn(s), yb + s * (yt - yb), 0],
                              t_range=[0, 1, 0.004], color=color, stroke_width=sw)


def hwalls(xc, hw, yb, yt, sw=7):
    return VGroup(Line([xc - hw, yt, 0], [xc + hw, yt, 0], color=INK, stroke_width=sw),
                  Line([xc - hw, yb, 0], [xc + hw, yb, 0], color=INK, stroke_width=sw))


def ladder(cx, ys, hw=0.7, color=ACCENT, sw=6):
    return VGroup(*[Line([cx - hw, y, 0], [cx + hw, y, 0], color=color, stroke_width=sw) for y in ys])


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

    def _hero(self):
        w = hwalls(0, 1.0, -1.0, 1.0, sw=6)
        wave = vwave(lambda s: 0.6 * np.sin(np.pi * s), 0, -1.0, 1.0, ACCENT, 4)
        return VGroup(w, wave)

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
        msg = {"H01": "A laser shines in exact colours; an atom holds exact energies.",
               "H02": "Both come from one rule — a wave has to fit between two walls."}[bid]
        c = card(msg, 36).to_edge(UP, buff=1.0)
        if bid == "H01":
            fr = VGroup(*[Line([x, -1.7, 0], [x, -0.3, 0], color=ACCENT, stroke_width=8)
                          for x in (-1.0, -0.5, 0.0, 0.5, 1.0)])
        else:
            w = hwalls(0, 1.2, -1.8, -0.2, sw=6)
            fr = VGroup(w, vwave(lambda s: 0.5 * np.sin(np.pi * s), 0, -1.8, -0.2, ACCENT, 5))
        self.play(Write(c), run_time=min(1.3, t * 0.4))
        self.play(Create(fr), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 2.7))
        self.play(FadeOut(c, fr), run_time=0.4)

    # ── A — intuition: a wave fits between two walls ──────────────────────────
    def _intuition(self):
        t1 = dur("A01")
        w = hwalls(0, 1.6, -2.2, 2.2)
        mid = DashedLine([0, -2.2, 0], [0, 2.2, 0], color=GHOST, stroke_width=2)
        mis = vwave(lambda s: 1.15 * np.sin(2.6 * np.pi * s + 0.5), 0, -2.2, 2.2, INK, 5)
        dotB = Dot([1.15 * np.sin(0.5), -2.2, 0], color=RED, radius=0.1)
        dotT = Dot([1.15 * np.sin(2.6 * np.pi + 0.5), 2.2, 0], color=RED, radius=0.1)
        cap1 = txt("most wavelengths cancel", 26, RED).move_to([-4.2, 2.9, 0])
        self.play(Create(w), Create(mid), run_time=t1 * 0.4)
        self.play(Create(mis), FadeIn(dotB, dotT), FadeIn(cap1), run_time=t1 * 0.6)

        t2 = dur("A02")
        flat = Line([0, -2.2, 0], [0, 2.2, 0], color=GHOST, stroke_width=4)
        fit = vwave(lambda s: 1.15 * np.sin(np.pi * s), 0, -2.2, 2.2, ACCENT, 6)
        dotB2 = Dot([0, -2.2, 0], color=ACCENT, radius=0.1)
        dotT2 = Dot([0, 2.2, 0], color=ACCENT, radius=0.1)
        cap2 = txt("only standing waves survive", 26, ACCENT).move_to([4.0, 2.9, 0])
        self.play(Transform(mis, flat), FadeOut(dotB, dotT), run_time=t2 * 0.3)
        self.play(Create(fit), FadeIn(dotB2, dotT2), FadeIn(cap2), run_time=t2 * 0.5)
        self.wait(max(0.2, t2 * 0.2))
        self.play(FadeOut(w, mid, mis, fit, dotB2, dotT2, cap1, cap2), run_time=0.5)

    # ── M — idea -> math: one rule, two branches ──────────────────────────────
    def _derivation(self):
        t1 = dur("M01")
        intro = txt("a whole number of half-waves fits the length L", 26, INK).move_to([0, 3.0, 0])
        self.play(FadeIn(intro), run_time=t1 * 0.8)
        self.wait(max(0.1, t1 * 0.2))

        rule = mtex(r"\frac{n\lambda}{2} = L", 50).move_to([0, 1.6, 0])
        boxr = SurroundingRectangle(rule, color=ACCENT, buff=0.2)
        self.play(Write(rule), Create(boxr), run_time=dur("M02") * 0.85)
        self.wait(max(0.1, dur("M02") * 0.15))
        self._rule = VGroup(rule, boxr)

        las_lbl = txt("LASER → colours", 26, INK).move_to([-3.6, -0.4, 0])
        f_eq = mtex(r"f_n = \frac{nc}{2L}", 40).move_to([-3.6, -1.7, 0])
        self.play(FadeIn(las_lbl), Write(f_eq), run_time=dur("M03") * 0.85)
        self.wait(max(0.1, dur("M03") * 0.15))

        atom_lbl = txt("ATOM → energies", 26, INK).move_to([3.6, -0.4, 0])
        e_eq = mtex(r"E_n = \frac{n^2 h^2}{8 m L^2}", 40).move_to([3.6, -1.7, 0])
        self.play(FadeIn(atom_lbl), Write(e_eq), run_time=dur("M04") * 0.85)
        self.wait(max(0.1, dur("M04") * 0.15))
        self.play(FadeOut(intro, las_lbl, f_eq, atom_lbl, e_eq), run_time=0.5)

    # ── W — worked example: two columns ───────────────────────────────────────
    def _worked(self):
        self.play(self._rule.animate.scale(0.62).move_to([0, 3.1, 0]), run_time=dur("W01"))
        divider = DashedLine([0, -2.2, 0], [0, 2.2, 0], color=GHOST, stroke_width=2)
        self.play(Create(divider), run_time=0.2)

        # laser column (left)
        l_title = txt("laser cavity", 28, INK).move_to([-3.5, 1.9, 0])
        l_L = mtex(r"L = 0.30\ \text{m}", 32).move_to([-3.5, 0.9, 0])
        l_df = mtex(r"\Delta f = \frac{c}{2L} \approx 500\ \text{MHz}", 32, RED).move_to([-3.5, -0.3, 0])
        l_n = mtex(r"n = \frac{2L}{\lambda} \approx 9.5\times 10^{5}", 32).move_to([-3.5, -1.6, 0])
        self.play(FadeIn(l_title, l_L), run_time=dur("W01") * 0.2 + 0.1)
        self.play(Write(l_df), run_time=dur("W02") * 0.85); self.wait(max(0.1, dur("W02") * 0.15))
        self.play(Write(l_n), run_time=dur("W03") * 0.85); self.wait(max(0.1, dur("W03") * 0.15))

        # atom column (right)
        a_title = txt("electron box", 28, INK).move_to([3.5, 1.9, 0])
        a_L = mtex(r"L = 1\ \text{nm}", 32).move_to([3.5, 0.9, 0])
        a_E = mtex(r"E_1 \approx 0.38\ \text{eV}", 32).move_to([3.5, -0.3, 0])
        a_E2 = mtex(r"E_2 \approx 1.5\ \text{eV}", 32, RED).move_to([3.5, -1.6, 0])
        self.play(FadeIn(a_title, a_L), Write(a_E), run_time=dur("W04") * 0.5)
        self.play(Write(a_E2), run_time=dur("W04") * 0.4)
        self.wait(max(0.1, dur("W04") * 0.1))
        self.play(FadeOut(divider, l_title, l_L, l_df, l_n,
                          a_title, a_L, a_E, a_E2, self._rule), run_time=0.5)

    # ── P — predicts: bigger L -> tighter rungs ───────────────────────────────
    def _predict(self):
        t1 = dur("P01")
        small = VGroup(ladder(-3.4, [-1.6, -0.5, 1.0, 2.0], color=ACCENT, sw=6),
                       txt("small L → wide gaps", 24, INK).move_to([-3.4, -2.5, 0]))
        big = VGroup(ladder(3.4, [-1.6, -1.1, -0.5, 0.2, 1.0, 1.9], color=ACCENT, sw=6),
                     txt("big L → tight gaps", 24, INK).move_to([3.4, -2.5, 0]))
        self.play(Create(small), run_time=t1 * 0.5)
        self.play(Create(big), run_time=t1 * 0.5)

        t2 = dur("P02")
        line = card("Same rule, two scales — colour and energy.", 30).move_to([0, 3.0, 0])
        self.play(Write(line), run_time=t2 * 0.8)
        self.wait(max(0.2, t2 * 0.2))
        self.play(FadeOut(small, big, line), run_time=0.5)

    # ── R — recap ─────────────────────────────────────────────────────────────
    def _recap(self):
        res = mtex(r"\frac{n\lambda}{2} = L", 56, RED).move_to([0, 1.2, 0])
        box = SurroundingRectangle(res, color=RED, buff=0.22)
        self.play(Write(res), Create(box), run_time=dur("R01") * 0.8); self.wait(max(0.1, dur("R01") * 0.2))
        line = card("Only the waves that fit are allowed to exist.", 32).move_to([0, -1.2, 0])
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
