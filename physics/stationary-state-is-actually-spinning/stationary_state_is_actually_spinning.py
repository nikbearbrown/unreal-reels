"""
stationary_state_is_actually_spinning.py
========================================
Bear's Notes — "Why a 'Stationary' Quantum State Is Actually Spinning"
Quantum Mechanics Vol. 1, Ch. 4 (Candidate 09).

9 MANIM beats (A01-A08) as one continuous SILENT 16:9 scene. A clock hand (the
complex wave function) spins in the Argand plane at a constant rate; its Re/Im
projections oscillate 90 degrees apart, but its length is constant — so |psi|^2 on
the right sits frozen while the hand whirls. Rotation is driven by a ValueTracker
(`self.ang`, local — no clash with Manim's Scene.time). INTRO + two hook beats are
placeholder markers. assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh stationary_state_is_actually_spinning.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # the spinning hand / circle
RED     = "#C0392B"     # the closing emphasis
GHOST   = "#C9BFBC"     # projections
FONT    = "Shadows Into Light"
TITLE   = "Why a 'Stationary' Quantum State Is Actually Spinning"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

# Argand plane (left panel)
CX, CY = -3.2, 0.1     # plane origin
R = 1.7                # hand length (constant)
AX = 2.4               # axis half-extent

# probability panel (right)
PX = 3.6               # bar centre x
FLOOR = -2.4           # shared baseline
BAR_W = 1.1
BAR_H = R              # |psi|^2 visual height (constant)

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.5, "A02": 4.0, "A03": 4.0, "A04": 5.5, "A05": 4.5, "A06": 5.0,
       "A07": 5.5, "A08": 5.0, "INTRO": 5.0, "H01": 5.5, "H02": 4.5, "OUTRO": 9.0}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def spin(t):
    # angle advanced during a beat of length t: ~one turn per 3.2 s
    return 2 * np.pi * (t / 3.2)


def tip(a):
    return np.array([CX + R * np.cos(a), CY + R * np.sin(a), 0.0])


def hand_arrow(a):
    return Arrow([CX, CY, 0], tip(a), buff=0, color=ACCENT, stroke_width=6,
                 max_tip_length_to_length_ratio=0.18)


def tip_dot(a):
    return Dot(tip(a), radius=0.09, color=ACCENT)


def re_proj(a):
    tp = tip(a)
    return DashedVMobject(Line(tp, [tp[0], CY, 0], color=GHOST, stroke_width=3), num_dashes=7)


def im_proj(a):
    tp = tip(a)
    return DashedVMobject(Line(tp, [CX, tp[1], 0], color=GHOST, stroke_width=3), num_dashes=7)


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
        self.ang = ValueTracker(0.5)        # rotation angle (local — not self.time)
        self._intro_card()
        self._hook("H01", "[ doodle: still object ]")
        self._hook("H02", "[ doodle: spinning hand revealed ]")
        self._clock_scene()
        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        c = Circle(radius=0.9, color=ACCENT, stroke_width=4)
        h = Arrow([0, 0, 0], [0.9 * np.cos(0.7), 0.9 * np.sin(0.7), 0], buff=0, color=ACCENT, stroke_width=6)
        return VGroup(c, h)

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
            sq = Square(side_length=1.0, color=ACCENT, stroke_width=4).move_to([0, -1.0, 0])
            return VGroup(sq, Text("nothing moves", font=FONT, font_size=28, color=INK).move_to([0, -2.5, 0]))
        if bid == "H02":
            c = Circle(radius=0.7, color=ACCENT, stroke_width=4).move_to([0, -1.0, 0])
            h = Arrow([0, -1.0, 0], [0.7 * np.cos(0.7), -1.0 + 0.7 * np.sin(0.7), 0], buff=0, color=ACCENT, stroke_width=5)
            return VGroup(c, h, Text("spinning underneath", font=FONT, font_size=28, color=INK).move_to([0, -2.5, 0]))
        return None

    def _clock_scene(self):
        ang = self.ang

        # A01 — the complex plane
        t1 = dur("A01")
        re_ax = Line([CX - AX, CY, 0], [CX + AX, CY, 0], color=INK, stroke_width=3)
        im_ax = Line([CX, CY - AX, 0], [CX, CY + AX, 0], color=INK, stroke_width=3)
        re_lbl = Text("Re", font=FONT, font_size=24, color=INK).next_to(re_ax, RIGHT, buff=0.12)
        im_lbl = Text("Im", font=FONT, font_size=24, color=INK).next_to(im_ax, UP, buff=0.12)
        self.play(Create(re_ax), Create(im_ax), run_time=t1 * 0.6)
        self.play(FadeIn(re_lbl), FadeIn(im_lbl), run_time=t1 * 0.4)

        # A02 — the clock hand + traced circle (static)
        t2 = dur("A02")
        circle = DashedVMobject(Circle(radius=R, color=GHOST, stroke_width=3).move_to([CX, CY, 0]), num_dashes=44)
        hand = hand_arrow(ang.get_value())
        dot = tip_dot(ang.get_value())
        self.play(Create(circle), run_time=t2 * 0.4)
        self.play(GrowArrow(hand), FadeIn(dot), run_time=t2 * 0.6)
        hand.add_updater(lambda m: m.become(hand_arrow(ang.get_value())))
        dot.add_updater(lambda m: m.become(tip_dot(ang.get_value())))

        # A03 — start spinning
        t3 = dur("A03")
        self.play(ang.animate.increment_value(spin(t3)), run_time=t3, rate_func=linear)

        # A04 — Re/Im projections, 90 degrees apart
        t4 = dur("A04")
        rp = re_proj(ang.get_value())
        ip = im_proj(ang.get_value())
        rp.add_updater(lambda m: m.become(re_proj(ang.get_value())))
        ip.add_updater(lambda m: m.become(im_proj(ang.get_value())))
        cap4 = Text("real & imaginary, 90 degrees apart", font=FONT, font_size=26, color=INK).move_to([CX, 3.0, 0])
        self.play(FadeIn(rp), FadeIn(ip), FadeIn(cap4),
                  ang.animate.increment_value(spin(t4)), run_time=t4, rate_func=linear)

        # A05 — length never changes
        t5 = dur("A05")
        cap5 = Text("length never changes", font=FONT, font_size=26, color=ACCENT).move_to([CX, 3.0, 0])
        self.play(Transform(cap4, cap5), Indicate(circle, color=ACCENT, scale_factor=1.06),
                  ang.animate.increment_value(spin(t5)), run_time=t5, rate_func=linear)

        # A06 — square it: the steady probability bar
        t6 = dur("A06")
        floor = Line([1.4, FLOOR, 0], [5.8, FLOOR, 0], color=INK, stroke_width=3)
        bar = Rectangle(width=BAR_W, height=BAR_H, color=INK, stroke_width=4,
                        fill_color=ACCENT, fill_opacity=0.22)
        bar.move_to([PX, FLOOR + BAR_H / 2, 0])
        blab = Text("|psi|squared", font=FONT, font_size=26, color=INK).next_to(bar, UP, buff=0.2)
        self.play(Create(floor), run_time=t6 * 0.2)
        self.play(GrowFromEdge(bar, DOWN), FadeIn(blab),
                  ang.animate.increment_value(spin(t6 * 0.8)), run_time=t6 * 0.8, rate_func=linear)

        # A07 — spinning vs frozen
        t7 = dur("A07")
        cap7 = Text("spinning", font=FONT, font_size=26, color=ACCENT).move_to([CX, 3.0, 0])
        frozen = Text("frozen", font=FONT, font_size=26, color=INK).move_to([PX, 3.0, 0])
        self.play(Transform(cap4, cap7), FadeIn(frozen),
                  ang.animate.increment_value(spin(t7)), run_time=t7, rate_func=linear)

        # A08 — the punchline; stop motion for a clean hold
        t8 = dur("A08")
        self.play(ang.animate.increment_value(spin(t8 * 0.5)), run_time=t8 * 0.5, rate_func=linear)
        for m in (hand, dot, rp, ip):
            m.clear_updaters()
        red = Text("stationary outside, spinning underneath", font=FONT, font_size=30, color=RED).move_to([0, -3.05, 0])
        self.play(Write(red), run_time=t8 * 0.5)

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
