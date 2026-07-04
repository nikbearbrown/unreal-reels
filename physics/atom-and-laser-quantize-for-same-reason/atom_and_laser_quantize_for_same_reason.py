"""
atom_and_laser_quantize_for_same_reason.py
==========================================
Bear's Notes — "Why an Atom and a Laser Cavity Quantize for the Same Reason"
Quantum Mechanics Vol. 1, Ch. 4 (Candidate 11).

9 MANIM beats (A01-A08), SILENT 16:9, three stages:
  3) a mismatched wave between two walls cancels to nothing on its round trip,
  4) a fitted wave (zero at both walls) reinforces into a standing wave,
  5) only a discrete ladder of modes fits — the atom's energies and the laser's
     colors are the same fact.
Mostly Transform/Create (stroke-on, fast render). INTRO + two hook beats are
placeholder markers. assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh atom_and_laser_quantize_for_same_reason.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

import bn_layout as BL
from bn_layout import is_portrait, band, rows, cols, fit, fit_text, rw, rh, rcy, safe_w

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # fitted / surviving waves
RED     = "#C0392B"     # mismatched ends + "cancels"
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why an Atom and a Laser Cavity Quantize for the Same Reason"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

L = 3.2                 # wall half-separation
BASE = 0.5              # baseline for the single-wave stages
AMP = 1.15
WTOP, WBOT = 2.6, -2.4  # wall extent

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 3.0, "A02": 4.5, "A03": 5.0, "A04": 4.0, "A05": 5.0, "A06": 5.0,
       "A07": 5.5, "A08": 4.5, "INTRO": 5.5, "H01": 5.0, "H02": 4.0, "OUTRO": 9.0}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def mismatched(x):
    return AMP * np.sin(2.6 * np.pi * (x + L) / (2 * L) + 0.5)


def mode(n):
    return lambda x: AMP * np.sin(n * np.pi * (x + L) / (2 * L))


def graph(fn, color=ACCENT, sw=5, base=BASE):
    return ParametricFunction(lambda x: [x, base + fn(x), 0],
                              t_range=[-L, L, 0.02], color=color, stroke_width=sw)


def walls(base=BASE):
    left = Line([-L, WBOT, 0], [-L, WTOP, 0], color=INK, stroke_width=7)
    right = Line([L, WBOT, 0], [L, WTOP, 0], color=INK, stroke_width=7)
    bl = DashedLine([-L, base, 0], [L, base, 0], color=GHOST, stroke_width=2)
    return VGroup(left, right, bl)


_bsp = HERE / "beat_sheet.json"
_BS = json.loads(_bsp.read_text()) if _bsp.exists() else {}
_NARR = {b["beat_id"]: b.get("narration_text", "") for b in _BS.get("beats", [])}
_DEEP_TEX = _BS.get("metadata", {}).get("deep_teaser_tex")


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
        if is_portrait():
            self._p_all()
            return

        self._intro_card()
        self._hook("H01", "[ doodle: laser + atom ]")
        self._hook("H02", "[ doodle: laser = atom ]")

        # STAGE 1 — mismatched cancels (A01-A03)
        self._stage_cancel()
        self.play(FadeOut(*self.mobjects), run_time=0.4)
        self.wait(0.1)

        # STAGE 2 — fitted reinforces (A04-A05)
        self._stage_fit()
        self.play(FadeOut(*self.mobjects), run_time=0.4)
        self.wait(0.1)

        # STAGE 3 — the ladder = atom energies = laser colors (A06-A08)
        self._stage_ladder()

        self._outro_card()

    # ── PORTRAIT (9:16) — walls HORIZONTAL (top+bottom), wave runs UP the tall
    #    axis with horizontal displacement; fits a narrow tall frame cleanly ────
    PWB, PWT = -1.7, 2.0     # bottom / top wall heights
    PWHW = 1.55             # wall half-width (x)
    PAMP = 1.15             # standing-wave amplitude (horizontal)
    PXC = 0.0

    def _p_walls(self, hw=None, xc=0.0):
        hw = self.PWHW if hw is None else hw
        top = Line([xc - hw, self.PWT, 0], [xc + hw, self.PWT, 0], color=INK, stroke_width=7)
        bot = Line([xc - hw, self.PWB, 0], [xc + hw, self.PWB, 0], color=INK, stroke_width=7)
        mid = DashedLine([xc, self.PWB, 0], [xc, self.PWT, 0], color=GHOST, stroke_width=2)
        return VGroup(top, bot, mid)

    def _p_vwave(self, fn, color=ACCENT, sw=6, xc=0.0):
        return ParametricFunction(
            lambda s: [xc + fn(s), self.PWB + s * (self.PWT - self.PWB), 0],
            t_range=[0, 1, 0.004], color=color, stroke_width=sw)

    def _p_cap(self, s, color=INK, y=2.8, size=30):
        return fit_text(s, FONT, size, color, 2 * safe_w() * 0.92).move_to([0, y, 0])

    def _p_intro(self):
        t = dur("INTRO")
        brow, hrow, trow = rows(band(), [0.18, 0.5, 0.32], gap=0.25)
        brand = fit(Text("Bear's Notes", font=FONT, font_size=44, color=INK), brow, 0.82)
        hero = fit(self._p_intro_hero(), hrow, 0.82)
        title = fit(fit_text(TITLE, FONT, 30, ACCENT, rw(trow) * 0.96), trow, 0.98)
        self.play(FadeIn(brand), run_time=min(0.9, t * 0.25))
        self.play(Create(hero), run_time=min(1.6, t * 0.4))
        self.play(Write(title), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 3.7))
        self.play(FadeOut(brand, hero, title), run_time=0.4)

    def _p_intro_hero(self):
        walls = VGroup(Line([-1.1, 1.1, 0], [1.1, 1.1, 0], color=INK, stroke_width=6),
                       Line([-1.1, -1.1, 0], [1.1, -1.1, 0], color=INK, stroke_width=6))
        wave = ParametricFunction(lambda s: [0.7 * np.sin(np.pi * s), -1.1 + s * 2.2, 0],
                                  t_range=[0, 1, 0.01], color=ACCENT, stroke_width=4)
        return VGroup(walls, wave)

    def _p_hook_sketch(self, bid):
        walls = VGroup(Line([-0.9, 0.9, 0], [0.9, 0.9, 0], color=INK, stroke_width=6),
                       Line([-0.9, -0.9, 0], [0.9, -0.9, 0], color=INK, stroke_width=6))
        if bid == "H01":
            beam = Line([-0.6, -1.5, 0], [0.6, -1.5, 0], color=ACCENT, stroke_width=6)
            atom = Circle(radius=0.32, color=ACCENT, stroke_width=4).move_to([0, 0, 0])
            return VGroup(walls, atom, beam)
        wave = ParametricFunction(lambda s: [0.55 * np.sin(np.pi * s), -0.9 + s * 1.8, 0],
                                  t_range=[0, 1, 0.01], color=ACCENT, stroke_width=4)
        return VGroup(walls, wave)

    def _p_card(self, bid, label=""):
        t = dur(bid)
        crow, srow = rows(band(), [0.36, 0.64], gap=0.3)
        c = fit(fit_text(_NARR.get(bid, label), FONT, 34, INK, rw(crow) * 0.96), crow, 0.96)
        sk = fit(self._p_hook_sketch(bid), srow, 0.8)
        self.play(Write(c), run_time=min(1.4, t * 0.4))
        self.play(Create(sk), run_time=min(1.2, t * 0.3))
        self.wait(max(0.3, t - 2.6))
        self.play(FadeOut(c, sk), run_time=0.4)

    def _p_all(self):
        self._p_intro()
        self._p_card("H01", "[ laser + atom ]")
        self._p_card("H02", "[ the same fact ]")

        self._p_stage_cancel()
        self.play(FadeOut(*self.mobjects), run_time=0.4)
        self.wait(0.1)
        self._p_stage_fit()
        self.play(FadeOut(*self.mobjects), run_time=0.4)
        self.wait(0.1)
        self._p_stage_ladder()

        BL.outro(self, TITLE, CHANNEL, dur("OUTRO"), teaser_tex=_DEEP_TEX,
                 font=FONT, ink=INK, accent=ACCENT)

    def _p_stage_cancel(self):
        # A01 — walls
        t = dur("A01")
        w = self._p_walls()
        cap = self._p_cap("trapped between two walls", color=INK)
        self.play(Create(w), FadeIn(cap), run_time=t * 0.85)
        self.wait(max(0.1, t * 0.15))

        # A02 — mismatched wave, non-zero at the walls
        t = dur("A02")
        mfn = lambda s: self.PAMP * np.sin(2.6 * np.pi * s + 0.5)
        wave = self._p_vwave(mfn, color=INK)
        dotB = Dot([self.PXC + mfn(0), self.PWB, 0], color=RED, radius=0.1)
        dotT = Dot([self.PXC + mfn(1), self.PWT, 0], color=RED, radius=0.1)
        cap2 = self._p_cap("doesn't vanish at the walls", color=RED)
        self.play(Transform(cap, cap2), Create(wave), run_time=t * 0.6)
        self.play(FadeIn(dotB), FadeIn(dotT), run_time=t * 0.4)

        # A03 — reflected copy out of phase → cancels to a flat line
        t = dur("A03")
        refl = self._p_vwave(lambda s: -mfn(s), color=GHOST)
        self.play(Create(refl), run_time=t * 0.4)
        flat1 = Line([self.PXC, self.PWB, 0], [self.PXC, self.PWT, 0], color=GHOST, stroke_width=4)
        flat2 = Line([self.PXC, self.PWB, 0], [self.PXC, self.PWT, 0], color=GHOST, stroke_width=4)
        cap3 = self._p_cap("cancels to nothing", color=RED)
        self.play(Transform(wave, flat1), Transform(refl, flat2),
                  FadeOut(dotB), FadeOut(dotT), Transform(cap, cap3), run_time=t * 0.5)
        self.wait(max(0.2, t * 0.1))

    def _p_stage_fit(self):
        # A04 — fitted half-wave, zero at both walls
        t = dur("A04")
        w = self._p_walls()
        wave = self._p_vwave(lambda s: self.PAMP * np.sin(np.pi * s), color=ACCENT, sw=6)
        dotB = Dot([self.PXC, self.PWB, 0], color=ACCENT, radius=0.1)
        dotT = Dot([self.PXC, self.PWT, 0], color=ACCENT, radius=0.1)
        cap = self._p_cap("zero at both walls — it fits", color=ACCENT)
        self.play(Create(w), FadeIn(cap), run_time=t * 0.3)
        self.play(Create(wave), FadeIn(dotB), FadeIn(dotT), run_time=t * 0.7)

        # A05 — pulse to show reinforcement
        t = dur("A05")
        cap5 = self._p_cap("reinforces into a standing wave", color=ACCENT)
        self.play(Transform(cap, cap5), run_time=t * 0.2)
        self.play(wave.animate.stretch(1.3, 0, about_point=[self.PXC, 0, 0]), run_time=t * 0.3)
        self.play(wave.animate.stretch(1 / 1.3, 0, about_point=[self.PXC, 0, 0]), run_time=t * 0.3)
        self.play(Indicate(wave, color=ACCENT, scale_factor=1.04), run_time=t * 0.2)

    def _p_stage_ladder(self):
        xs = [-1.05, 0.0, 1.05]
        amp = 0.34
        hw = 0.7
        # A06 — three modes side by side, n=1,2,3
        t = dur("A06")
        top = Line([-1.6, self.PWT, 0], [1.6, self.PWT, 0], color=INK, stroke_width=7)
        bot = Line([-1.6, self.PWB, 0], [1.6, self.PWB, 0], color=INK, stroke_width=7)
        modes = VGroup()
        nlabels = VGroup()
        for i, xc in enumerate(xs):
            n = i + 1
            wv = ParametricFunction(
                lambda s, n=n, xc=xc: [xc + amp * np.sin(n * np.pi * s), self.PWB + s * (self.PWT - self.PWB), 0],
                t_range=[0, 1, 0.004], color=ACCENT, stroke_width=5)
            modes.add(wv)
            nlabels.add(Text(f"n={n}", font=FONT, font_size=24, color=INK).move_to([xc, self.PWB - 0.32, 0]))
        cap = self._p_cap("only a discrete set fits", color=INK)
        self.play(Create(top), Create(bot), FadeIn(cap), run_time=t * 0.25)
        self.play(LaggedStart(*[Create(m) for m in modes], lag_ratio=0.18),
                  FadeIn(nlabels), run_time=t * 0.75)

        # A07 — atom energies = laser colors
        t = dur("A07")
        cap7 = self._p_cap("atom's energies = laser's colors", color=ACCENT)
        self.play(Transform(cap, cap7), Indicate(modes, color=ACCENT), run_time=t * 0.7)
        self.wait(max(0.2, t * 0.3))

        # A08 — punchline
        t = dur("A08")
        red = self._p_cap("only what fits survives", color=RED, y=-1.92, size=30)
        self.play(Write(red), run_time=t * 0.7)
        self.wait(max(0.2, t * 0.3))

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        walls = VGroup(Line([-1.4, -1.0, 0], [-1.4, 1.0, 0], color=INK, stroke_width=6),
                       Line([1.4, -1.0, 0], [1.4, 1.0, 0], color=INK, stroke_width=6))
        wave = ParametricFunction(lambda x: [x, 0.8 * np.sin(np.pi * (x + 1.4) / 2.8), 0],
                                  t_range=[-1.4, 1.4, 0.03], color=ACCENT, stroke_width=4)
        return VGroup(walls, wave)

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
            beam = Line([-2.2, -1.0, 0], [-0.3, -1.0, 0], color=ACCENT, stroke_width=6)
            atom = Circle(radius=0.45, color=ACCENT, stroke_width=4).move_to([1.3, -1.0, 0])
            return VGroup(beam, atom, Text("exact colors, exact energies", font=FONT, font_size=26, color=INK).move_to([0, -2.6, 0]))
        if bid == "H02":
            eq = VGroup(Line([-0.6, -0.8, 0], [0.6, -0.8, 0], color=INK, stroke_width=7),
                        Line([-0.6, -1.2, 0], [0.6, -1.2, 0], color=INK, stroke_width=7))
            return VGroup(eq, Text("the same fact", font=FONT, font_size=28, color=INK).move_to([0, -2.4, 0]))
        return None

    def _stage_cancel(self):
        # A01 — walls
        t1 = dur("A01")
        w = walls()
        self.play(Create(w), run_time=t1 * 0.85)
        self.wait(max(0.1, t1 * 0.15))

        # A02 — mismatched wave, non-zero ends
        t2 = dur("A02")
        wave = graph(mismatched, color=INK)
        dotL = Dot([-L, BASE + mismatched(-L), 0], color=RED, radius=0.1)
        dotR = Dot([L, BASE + mismatched(L), 0], color=RED, radius=0.1)
        cap2 = Text("doesn't vanish at the walls", font=FONT, font_size=26, color=RED).move_to([0, 3.0, 0])
        self.play(Create(wave), run_time=t2 * 0.6)
        self.play(FadeIn(dotL), FadeIn(dotR), FadeIn(cap2), run_time=t2 * 0.4)

        # A03 — reflected copy out of phase → cancels to flat
        t3 = dur("A03")
        refl = graph(lambda x: -mismatched(x), color=GHOST)
        self.play(Create(refl), run_time=t3 * 0.4)
        flat1 = Line([-L, BASE, 0], [L, BASE, 0], color=GHOST, stroke_width=4)
        flat2 = Line([-L, BASE, 0], [L, BASE, 0], color=GHOST, stroke_width=4)
        cap3 = Text("cancels to nothing", font=FONT, font_size=28, color=RED).move_to([0, 3.0, 0])
        self.play(Transform(wave, flat1), Transform(refl, flat2),
                  FadeOut(dotL), FadeOut(dotR), Transform(cap2, cap3), run_time=t3 * 0.5)
        self.wait(max(0.2, t3 * 0.1))

    # ── STAGE 2 — fitted wave reinforces ──────────────────────────────────────
    def _stage_fit(self):
        # A04 — fitted half-wave, zero at both ends
        t4 = dur("A04")
        w = walls()
        wave = graph(mode(1), color=ACCENT, sw=6)
        dotL = Dot([-L, BASE, 0], color=ACCENT, radius=0.1)
        dotR = Dot([L, BASE, 0], color=ACCENT, radius=0.1)
        cap4 = Text("zero at both walls — it fits", font=FONT, font_size=26, color=ACCENT).move_to([0, 3.0, 0])
        self.play(Create(w), run_time=t4 * 0.3)
        self.play(Create(wave), FadeIn(dotL), FadeIn(dotR), FadeIn(cap4), run_time=t4 * 0.7)

        # A05 — pulse to show reinforcement, then settle
        t5 = dur("A05")
        cap5 = Text("reinforces into a standing wave", font=FONT, font_size=26, color=ACCENT).move_to([0, 3.0, 0])
        self.play(Transform(cap4, cap5), run_time=t5 * 0.2)
        self.play(wave.animate.stretch(1.28, 1, about_point=[0, BASE, 0]), run_time=t5 * 0.3)
        self.play(wave.animate.stretch(1 / 1.28, 1, about_point=[0, BASE, 0]), run_time=t5 * 0.3)
        self.play(Indicate(wave, color=ACCENT, scale_factor=1.03), run_time=t5 * 0.2)

    # ── STAGE 3 — the mode ladder ─────────────────────────────────────────────
    def _stage_ladder(self):
        ybs = [-1.4, 0.2, 1.8]
        amp_s = 0.5

        # A06 — three fitting modes stacked
        t6 = dur("A06")
        left = Line([-L, WBOT, 0], [-L, WTOP, 0], color=INK, stroke_width=7)
        right = Line([L, WBOT, 0], [L, WTOP, 0], color=INK, stroke_width=7)
        rungs = VGroup()
        nlabels = VGroup()
        for i, yb in enumerate(ybs):
            n = i + 1
            lvl = DashedLine([-L, yb, 0], [L, yb, 0], color=GHOST, stroke_width=2)
            wv = ParametricFunction(lambda x, n=n, yb=yb: [x, yb + amp_s * np.sin(n * np.pi * (x + L) / (2 * L)), 0],
                                    t_range=[-L, L, 0.02], color=ACCENT, stroke_width=5)
            rungs.add(lvl, wv)
            nlabels.add(Text(f"n={n}", font=FONT, font_size=24, color=INK).move_to([-L - 0.55, yb, 0]))
        cap6 = Text("only a discrete set fits", font=FONT, font_size=26, color=INK).move_to([0, 3.0, 0])
        self.play(Create(left), Create(right), run_time=t6 * 0.25)
        self.play(LaggedStart(*[Create(m) for m in rungs], lag_ratio=0.12),
                  FadeIn(nlabels), FadeIn(cap6), run_time=t6 * 0.75)

        # A07 — atom / laser tags
        t7 = dur("A07")
        atom = Text("ATOM\nenergies", font=FONT, font_size=26, color=INK).move_to([-5.1, 0.2, 0])
        laser = Text("LASER\ncolors", font=FONT, font_size=26, color=INK).move_to([5.1, 0.2, 0])
        a_arr = Arrow([-4.3, 0.2, 0], [-L - 0.15, 0.2, 0], buff=0, color=GHOST, stroke_width=3)
        l_arr = Arrow([4.3, 0.2, 0], [L + 0.15, 0.2, 0], buff=0, color=GHOST, stroke_width=3)
        cap7 = Text("same ladder, both times", font=FONT, font_size=26, color=ACCENT).move_to([0, 3.0, 0])
        self.play(FadeIn(atom), FadeIn(laser), GrowArrow(a_arr), GrowArrow(l_arr),
                  Transform(cap6, cap7), run_time=t7 * 0.8)
        self.wait(max(0.2, t7 * 0.2))

        # A08 — punchline
        t8 = dur("A08")
        red = Text("only what fits survives", font=FONT, font_size=30, color=RED).move_to([0, -3.05, 0])
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
