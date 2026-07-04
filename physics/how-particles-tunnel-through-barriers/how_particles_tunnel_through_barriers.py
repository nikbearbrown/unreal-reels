"""
Bear's Notes - How Particles Tunnel Through Barriers

Rough Manim master with doodle placeholders for hand-drawn overlay.
"""
import json
from pathlib import Path

import manimpango
import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent
FONT_PATH = HERE.parent / "shared" / "fonts" / "ShadowsIntoLight-Regular.ttf"
if FONT_PATH.exists():
    manimpango.register_font(str(FONT_PATH))

SHEET = json.loads((HERE / "beat_sheet.json").read_text())
TIMINGS = json.loads((HERE / "mp3" / "timings.json").read_text())
META = SHEET["metadata"]

INK = "#1a1a1a"
ACCENT = META.get("accent_color", "#5A5653")
FORBIDDEN = META.get("forbidden_color", "#C0392B")
GHOST = "#C9BFBC"
SOFT = "#E9E4E1"
FONT = META.get("text_font", "Shadows Into Light")
TITLE = META.get("title", "How Particles Tunnel Through Barriers")


def dur(bid, fallback=3.0):
    return float(TIMINGS.get(bid, fallback))


def txt(s, size=34, color=INK):
    return Text(s, font=FONT, font_size=size, color=color)


def label_box(s, width=3.0, height=1.0, color=INK):
    box = RoundedRectangle(width=width, height=height, corner_radius=0.14, stroke_width=4, color=color, fill_color=WHITE, fill_opacity=1)
    label = txt(s, size=28, color=color).move_to(box)
    return VGroup(box, label)


_NARR = {b["beat_id"]: b.get("narration_text", "") for b in SHEET.get("beats", [])}


def _card(s, _sz=40):
    ws = s.split()
    lines = [" ".join(ws[i:i + 6]) for i in range(0, len(ws), 6)] or [""]
    g = VGroup(*[txt(l, size=_sz) for l in lines]).arrange(DOWN, buff=0.28)
    if g.width > 11.5:
        g.scale_to_fit_width(11.5)
    return g


class BearsDoodlesVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        self.intro()
        self.doodle("A00", "classical ball denied by hill")
        self.classical_scene()
        self.wave_particle_scene()
        self.tunnel_wave_scene()
        self.barrier_compare_scene()
        self.inside_region_scene()
        self.doodle("A12", "not a secret tunnel")
        self.continuity_scene()
        self.atom_scene()
        self.outro()

    def remove_all(self):
        for mob in list(self.mobjects):
            self.remove(mob)

    def hold(self, bid, used):
        self.wait(max(0.05, dur(bid) - used))

    def doodle_box(self, label):
        box = DashedVMobject(RoundedRectangle(width=5.5, height=2.85, corner_radius=0.18, color=GHOST, stroke_width=4), num_dashes=40)
        tag = txt(f"[doodle {label}]", size=30, color=GHOST).next_to(box, DOWN, buff=0.25)
        return VGroup(box, tag)

    def _intro_hero(self):
        bar = Rectangle(width=0.7, height=1.8, color=INK, fill_color=ACCENT, fill_opacity=0.18, stroke_width=4)
        left = ParametricFunction(lambda x: [x, 0.55 * np.sin(4 * x), 0], t_range=[-2.2, -0.35, 0.03], color=ACCENT, stroke_width=4)
        right = ParametricFunction(lambda x: [x, 0.28 * np.sin(4 * x), 0], t_range=[0.35, 2.0, 0.03], color=ACCENT, stroke_width=4)
        return VGroup(bar, left, right)

    def intro(self):
        t = dur("INTRO")
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.3)
        brand = txt("Bear's Notes", size=44, color=INK).move_to([0, 3.0, 0])
        hero = self._intro_hero().move_to([0, 0.4, 0])
        title = txt(TITLE, size=30, color=ACCENT)
        if title.width > 11.0:
            title.scale_to_fit_width(11.0)
        title.move_to([0, -2.5, 0])
        r1, r2, r3 = min(0.9, t * 0.22), min(1.6, t * 0.4), min(1.3, t * 0.28)
        self.play(FadeIn(brand), run_time=r1)
        self.play(Create(hero), run_time=r2)
        self.play(Write(title), run_time=r3)
        self.hold("INTRO", r1 + r2 + r3)

    def doodle(self, bid, label):
        self.remove_all()
        card = _card(_NARR.get(bid, label))
        self.play(Write(card), run_time=1.0)
        self.hold(bid, 1.0)
    def valley_curve(self):
        return ParametricFunction(
            lambda t: np.array([t, 0.18 * (t + 2.5) ** 2 - 1.55, 0]) if t < -0.35
            else np.array([t, 2.35 * np.exp(-2.3 * t * t) - 1.15 + 0.06 * (t - 2.2) ** 2, 0]),
            t_range=[-5.2, 5.2, 0.02],
            color=INK,
            stroke_width=5,
        )

    def barrier_rect(self, center_x=0.0, width=1.05, height=3.0, y=-0.45):
        return Rectangle(width=width, height=height, color=FORBIDDEN, stroke_width=5).set_fill(FORBIDDEN, opacity=0.08).move_to([center_x, y, 0])

    def exp_tail(self, x0=-0.55, x1=0.55, y0=0.1, amp=0.75, color=ACCENT):
        return ParametricFunction(
            lambda t: np.array([t, y0 + amp * np.exp(-3.3 * (t - x0)), 0]),
            t_range=[x0, x1, 0.02],
            color=color,
            stroke_width=6,
        )

    def wave(self, x0=-4.6, x1=-0.55, amp=0.55, y0=0.1, cycles=3.0, color=ACCENT):
        return ParametricFunction(
            lambda t: np.array([t, y0 + amp * np.sin(cycles * TAU * (t - x0) / (x1 - x0)), 0]),
            t_range=[x0, x1, 0.02],
            color=color,
            stroke_width=6,
        )

    def classical_scene(self):
        self.remove_all()
        curve = self.valley_curve()
        ball = Circle(radius=0.18, color=INK, stroke_width=4).set_fill(SOFT, opacity=1).move_to([-3.55, -0.6, 0])
        energy = DashedLine([-5.15, 0.62, 0], [1.0, 0.62, 0], color=ACCENT, stroke_width=4, dash_length=0.18)
        elab = txt("starting energy", size=34, color=ACCENT).move_to([-2.0, 1.15, 0])
        self.play(Create(curve), FadeIn(ball), Create(energy), FadeIn(elab), run_time=1.35)
        self.hold("A01", 1.35)

        far = Rectangle(width=2.2, height=1.4, color=FORBIDDEN, stroke_width=4).set_fill(FORBIDDEN, opacity=0.08).move_to([3.5, -0.75, 0])
        flab = txt("forbidden", size=36, color=FORBIDDEN).move_to([3.5, 0.25, 0])
        barrier = Line([0.25, -1.55, 0], [0.25, 1.55, 0], color=FORBIDDEN, stroke_width=7)
        self.play(FadeIn(far), FadeIn(flab), Create(barrier), run_time=1.15)
        self.hold("A02", 1.15)

    def wave_particle_scene(self):
        self.remove_all()
        packet = ParametricFunction(
            lambda t: np.array([t, 0.8 * np.exp(-(t / 1.25) ** 2) * np.sin(6.5 * t), 0]),
            t_range=[-4.3, 4.3, 0.02],
            color=ACCENT,
            stroke_width=6,
        )
        dot = Dot([0, 0, 0], radius=0.16, color=FORBIDDEN)
        slash = Cross(dot, stroke_color=FORBIDDEN, stroke_width=5).scale(1.3)
        label = txt("wave, not certainty dot", size=40, color=ACCENT).move_to([0, 2.35, 0])
        self.play(Create(packet), FadeIn(dot), Create(slash), FadeIn(label), run_time=1.55)
        self.hold("A03", 1.55)

    def tunnel_wave_scene(self):
        self.remove_all()
        baseline = Line([-5.2, -1.55, 0], [5.2, -1.55, 0], color=INK, stroke_width=4)
        barrier = self.barrier_rect(width=1.1, height=3.2, y=0.0)
        left_valley = txt("first valley", size=34, color=INK).move_to([-3.0, -2.25, 0])
        left_wave = self.wave(x0=-4.75, x1=-0.58, amp=0.58, y0=-0.25, cycles=2.7)
        self.play(Create(baseline), Create(barrier), FadeIn(left_valley), Create(left_wave), run_time=1.5)
        self.hold("A04", 1.5)

        tail = self.exp_tail(x0=-0.55, x1=0.55, y0=-0.25, amp=0.45)
        tail_lab = txt("leaking tail", size=32, color=FORBIDDEN).move_to([0, 1.95, 0])
        self.play(Create(tail), FadeIn(tail_lab), run_time=1.15)
        self.hold("A05", 1.15)

        right_wave = self.wave(x0=0.58, x1=4.45, amp=0.18, y0=-0.25, cycles=2.2)
        far_lab = txt("far side", size=34, color=INK).move_to([3.2, -2.25, 0])
        self.play(Create(right_wave), FadeIn(far_lab), run_time=1.05)
        self.hold("A06", 1.05)

        dot = Dot([2.75, -0.25, 0], radius=0.14, color=FORBIDDEN)
        ring = Circle(radius=0.34, color=FORBIDDEN, stroke_width=4).move_to(dot)
        self.play(FadeIn(dot), Create(ring), run_time=1.0)
        self.hold("A07", 1.0)

        small = txt("small, not zero", size=38, color=FORBIDDEN).move_to([0, 2.65, 0])
        arrow = Arrow([1.35, 1.9, 0], [2.45, 0.15, 0], color=FORBIDDEN, stroke_width=4, buff=0.08)
        self.play(FadeIn(small), GrowArrow(arrow), run_time=1.05)
        self.hold("A08", 1.05)

    def comparison_panel(self, x, title, width, height, transmitted):
        base = Line([x - 2.25, -1.15, 0], [x + 2.25, -1.15, 0], color=INK, stroke_width=4)
        barrier = Rectangle(width=width, height=height, color=FORBIDDEN, stroke_width=4).set_fill(FORBIDDEN, opacity=0.08).move_to([x, 0.0, 0])
        left = self.wave(x0=x - 2.15, x1=x - width / 2, amp=0.32, y0=-0.35, cycles=1.8)
        tail = ParametricFunction(
            lambda t: np.array([t, -0.35 + 0.28 * np.exp(-3.6 * (t - (x - width / 2))), 0]),
            t_range=[x - width / 2, x + width / 2, 0.02],
            color=ACCENT,
            stroke_width=5,
        )
        right = self.wave(x0=x + width / 2, x1=x + 2.1, amp=transmitted, y0=-0.35, cycles=1.2)
        lab = txt(title, size=30, color=FORBIDDEN).move_to([x, 1.9, 0])
        return VGroup(base, barrier, left, tail, right, lab)

    def barrier_compare_scene(self):
        self.remove_all()
        wide = self.comparison_panel(-2.8, "wider barrier", 1.55, 2.5, 0.07)
        faded = txt("tail fades", size=34, color=ACCENT).move_to([-2.8, -2.35, 0])
        self.play(Create(wide), FadeIn(faded), run_time=1.65)
        self.hold("A09", 1.65)

        low = self.comparison_panel(2.8, "lower barrier", 0.95, 1.65, 0.22)
        survives = txt("more survives", size=34, color=ACCENT).move_to([2.8, -2.35, 0])
        self.play(Create(low), FadeIn(survives), run_time=1.55)
        self.hold("A10", 1.55)

    def inside_region_scene(self):
        self.remove_all()
        barrier = self.barrier_rect(width=2.5, height=3.4, y=0.0)
        tail = self.exp_tail(x0=-1.25, x1=1.25, y0=-0.25, amp=1.0)
        dot = Dot([0.15, 0.06, 0], radius=0.15, color=FORBIDDEN)
        label = txt("inside forbidden region", size=38, color=FORBIDDEN).move_to([0, 2.45, 0])
        self.play(Create(barrier), Create(tail), FadeIn(dot), FadeIn(label), run_time=1.55)
        self.hold("A11", 1.55)

    def continuity_scene(self):
        self.remove_all()
        boundary = Line([0, -1.8, 0], [0, 1.8, 0], color=FORBIDDEN, stroke_width=5)
        left = self.wave(x0=-4.6, x1=0.0, amp=0.62, y0=0.0, cycles=2.5)
        right = ParametricFunction(
            lambda t: np.array([t, 0.55 * np.exp(-1.4 * t), 0]),
            t_range=[0.0, 3.8, 0.02],
            color=ACCENT,
            stroke_width=6,
        )
        stop = Line([0, 0.9, 0], [0, -0.9, 0], color=GHOST, stroke_width=4)
        cross = Cross(stop, stroke_color=FORBIDDEN, stroke_width=5)
        label = txt("waves do not stop instantly", size=40, color=ACCENT).move_to([0, 2.45, 0])
        self.play(Create(boundary), Create(left), Create(right), FadeIn(stop), Create(cross), FadeIn(label), run_time=1.55)
        self.hold("A13", 1.55)

    def atom_scene(self):
        self.remove_all()
        nucleus = Circle(radius=0.72, color=FORBIDDEN, stroke_width=5).set_fill(FORBIDDEN, opacity=0.12)
        cloud = ParametricFunction(
            lambda t: np.array([1.7 * np.cos(t), 0.9 * np.sin(t), 0]),
            t_range=[0, TAU, 0.02],
            color=ACCENT,
            stroke_width=5,
        )
        inside = Dot([0.25, 0.05, 0], radius=0.11, color=ACCENT)
        lab = txt("electron time inside nucleus", size=38, color=ACCENT).move_to([0, 2.35, 0])
        self.play(Create(nucleus), Create(cloud), FadeIn(inside), FadeIn(lab), run_time=1.55)
        self.hold("A14", 1.55)

        impossible = label_box("impossible\npath", width=2.7, height=1.15, color=FORBIDDEN).move_to([-2.35, -2.0, 0])
        tiny = label_box("tiny\nprobability", width=2.95, height=1.15, color=ACCENT).move_to([2.35, -2.0, 0])
        arrow = Arrow([-0.85, -2.0, 0], [0.85, -2.0, 0], color=INK, stroke_width=4, buff=0.1)
        self.play(FadeIn(impossible), GrowArrow(arrow), FadeIn(tiny), run_time=1.3)
        self.hold("A15", 1.3)

    def outro(self):
        t = dur("OUTRO")
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)
        thanks = txt("Thanks for watching", size=44, color=INK).move_to([0, 1.7, 0])
        title = txt(TITLE, size=30, color=ACCENT)
        if title.width > 11.0:
            title.scale_to_fit_width(11.0)
        title.move_to([0, 0.2, 0])
        url = txt("youtube.com/@NikBearBrown", size=36, color=INK).move_to([0, -1.7, 0])
        self.play(Write(thanks), run_time=1.2)
        self.play(FadeIn(title), run_time=1.0)
        self.play(Write(url), run_time=1.2)
        self.wait(max(0.6, t - 3.8))
