"""
measuring_spin_sideways_erases_spin_up.py
=========================================
Bear's Notes — "Why Measuring Spin Sideways Erases What You Just Learned About Spin Up"
Quantum Mechanics Vol. 1, Ch. 10 (Candidate 08).

9 MANIM beats (A01-A08) as a SILENT 16:9 scene in three measurement stages
(Z -> X -> Z Stern-Gerlach). Each stage: a beam enters a box, the box SPLITS it,
one branch is blocked (red X), the survivor is relabelled. The third Z box shows the
up/down answer is a coin flip again -- the middle (X) measurement overwrote it.
INTRO + two hook beats are placeholder markers. assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh measuring_spin_sideways_erases_spin_up.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # surviving / kept beams
RED     = "#C0392B"     # blocked beam + "overwritten" emphasis
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why Measuring Spin Sideways Erases What You Just Learned About Spin Up"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

# beam-stage geometry (one box, beam in from the left, two beams out to the right)
BX = -2.2                       # box centre x
BW, BH = 1.5, 1.9               # box size
B_L = BX - BW / 2               # box left edge  (-2.95)
B_R = BX + BW / 2               # box right edge (-1.45)
IN_X0 = -6.0
OUT_X = 5.3
YOUT = 1.65
BEAM_SW = 9

P_BR = np.array([B_R, 0.0, 0.0])
P_UP = np.array([OUT_X, YOUT, 0.0])
P_DN = np.array([OUT_X, -YOUT, 0.0])

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.0, "A02": 4.5, "A03": 5.0, "A04": 4.5, "A05": 4.0, "A06": 4.5,
       "A07": 5.0, "A08": 5.5, "INTRO": 5.5, "H01": 4.5, "H02": 5.0, "OUTRO": 9.5}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def box(label):
    r = Rectangle(width=BW, height=BH, color=INK, stroke_width=6).move_to([BX, 0, 0])
    t = Text(label, font=FONT, font_size=46, color=INK).move_to([BX, 0, 0])
    return VGroup(r, t)


def in_beam():
    return Line([IN_X0, 0, 0], [B_L, 0, 0], color=ACCENT, stroke_width=BEAM_SW)


def out_beam(sign, color=ACCENT, sw=BEAM_SW):
    return Line(P_BR, [OUT_X, sign * YOUT, 0], color=color, stroke_width=sw)


def block_x(pt, size=0.34):
    a = Line(pt + np.array([-size, -size, 0]), pt + np.array([size, size, 0]), color=RED, stroke_width=8)
    b = Line(pt + np.array([-size, size, 0]), pt + np.array([size, -size, 0]), color=RED, stroke_width=8)
    return VGroup(a, b)


def along(p_end, frac):
    return P_BR + frac * (np.array(p_end) - P_BR)


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
        self._hook("H01", "[ doodle: jar of spin-up atoms ]")
        self._hook("H02", "[ doodle: baffled, coin flips ]")

        # STAGE 1 (Z) — A01-A02
        self._stage_z1()
        self.play(FadeOut(*self.mobjects), run_time=0.4)
        self.wait(0.1)

        # STAGE 2 (X, sideways) — A03-A05
        self._stage_x()
        self.play(FadeOut(*self.mobjects), run_time=0.4)
        self.wait(0.1)

        # STAGE 3 (Z again) — A06-A08  (kept on screen for the outro)
        self._stage_z2()

        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        box = Rectangle(width=1.0, height=1.3, color=INK, stroke_width=5)
        up = Arrow([0.5, 0.25, 0], [1.7, 0.8, 0], color=ACCENT, buff=0, stroke_width=5)
        dn = Arrow([0.5, -0.25, 0], [1.7, -0.8, 0], color=ACCENT, buff=0, stroke_width=5)
        return VGroup(box, up, dn)

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
            ups = VGroup(*[Arrow([x, -1.6, 0], [x, -0.5, 0], color=ACCENT, buff=0, stroke_width=5)
                           for x in (-0.9, -0.3, 0.3, 0.9)])
            return VGroup(ups, Text("all spin-up", font=FONT, font_size=28, color=INK).move_to([0, -2.5, 0]))
        if bid == "H02":
            coin = Circle(radius=0.5, color=ACCENT, stroke_width=4).move_to([0, -1.0, 0])
            return VGroup(coin, Text("back to a coin flip", font=FONT, font_size=28, color=INK).move_to([0, -2.5, 0]))
        return None

    def _stage_z1(self):
        # A01 — beam into the Z box
        t1 = dur("A01")
        inb = in_beam()
        bx = box("Z")
        cap = Text("measures up / down", font=FONT, font_size=26, color=INK).move_to([BX, -2.7, 0])
        self.play(Create(inb), run_time=t1 * 0.4)
        self.play(FadeIn(bx), FadeIn(cap), run_time=t1 * 0.6)

        # A02 — split, block down, keep up
        t2 = dur("A02")
        up = out_beam(+1)
        dn = out_beam(-1)
        self.play(Create(up), Create(dn), run_time=t2 * 0.4)
        blk = block_x(along(P_DN, 0.62))
        keep = Text("spin-up only", font=FONT, font_size=28, color=ACCENT).move_to([3.0, YOUT + 0.55, 0])
        self.play(dn.animate.set_color(GHOST), FadeIn(blk), FadeIn(keep), run_time=t2 * 0.45)
        self.wait(max(0.15, t2 * 0.15))

    # ── STAGE 2 — X box (sideways), split L/R, block left ─────────────────────
    def _stage_x(self):
        # A03 — spin-up beam into the X box
        t3 = dur("A03")
        inb = in_beam()
        inlab = Text("spin-up", font=FONT, font_size=26, color=ACCENT).move_to([-4.3, 0.6, 0])
        bx = box("X")
        cap = Text("measures left / right", font=FONT, font_size=26, color=INK).move_to([BX, -2.7, 0])
        self.play(Create(inb), FadeIn(inlab), run_time=t3 * 0.45)
        self.play(FadeIn(bx), FadeIn(cap), run_time=t3 * 0.55)

        # A04 — equal 50/50 split
        t4 = dur("A04")
        up = out_beam(+1)
        dn = out_beam(-1)
        ulab = Text("left  50%", font=FONT, font_size=26, color=ACCENT).move_to([3.0, YOUT + 0.55, 0])
        dlab = Text("right 50%", font=FONT, font_size=26, color=ACCENT).move_to([3.0, -YOUT - 0.55, 0])
        self.play(Create(up), Create(dn), FadeIn(ulab), FadeIn(dlab), run_time=t4 * 0.8)
        self.wait(max(0.15, t4 * 0.2))

        # A05 — block left (top beam), keep right (bottom beam)
        t5 = dur("A05")
        blk = block_x(along(P_UP, 0.62))
        keep = Text("spin-right only", font=FONT, font_size=28, color=ACCENT).move_to([3.0, -YOUT - 0.55, 0])
        self.play(up.animate.set_color(GHOST), ulab.animate.set_color(GHOST),
                  FadeIn(blk), FadeOut(dlab), FadeIn(keep), run_time=t5 * 0.75)
        self.wait(max(0.2, t5 * 0.25))

    # ── STAGE 3 — Z box again, coin flip is back ──────────────────────────────
    def _stage_z2(self):
        # A06 — spin-right beam into the third Z box
        t6 = dur("A06")
        inb = in_beam()
        inlab = Text("spin-right", font=FONT, font_size=26, color=ACCENT).move_to([-4.3, 0.6, 0])
        bx = box("Z")
        cap = Text("measures up / down", font=FONT, font_size=26, color=INK).move_to([BX, -2.7, 0])
        self.play(Create(inb), FadeIn(inlab), run_time=t6 * 0.45)
        self.play(FadeIn(bx), FadeIn(cap), run_time=t6 * 0.55)
        self._cap = cap

        # A07 — splits 50/50 all over again
        t7 = dur("A07")
        up = out_beam(+1)
        dn = out_beam(-1)
        ulab = Text("up  50%", font=FONT, font_size=26, color=ACCENT).move_to([3.0, YOUT + 0.55, 0])
        dlab = Text("down 50%", font=FONT, font_size=26, color=ACCENT).move_to([3.0, -YOUT - 0.55, 0])
        self.play(Create(up), Create(dn), FadeIn(ulab), FadeIn(dlab), run_time=t7 * 0.8)
        self.wait(max(0.2, t7 * 0.2))

        # A08 — the middle measurement overwrote it
        t8 = dur("A08")
        red = Text("the middle measurement overwrote it", font=FONT, font_size=30, color=RED).move_to([1.3, -2.7, 0])
        self.play(FadeOut(cap), Write(red), run_time=t8 * 0.7)
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
