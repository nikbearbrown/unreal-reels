"""
Bear's Notes - How an Electron's Wave Guides One Click

Rough Manim master. Doodle beats are marked with placeholder boxes so the
hand-drawn clips can be overlaid later in Rush/Premiere.
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
TITLE = META.get("title", "How an Electron's Wave Guides One Click")


def dur(bid, fallback=3.0):
    return float(TIMINGS.get(bid, fallback))


def txt(s, size=34, color=INK):
    return Text(s, font=FONT, font_size=size, color=color)


def label_box(s, width=3.0, height=1.0, color=INK):
    box = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.14,
        stroke_width=4,
        color=color,
        fill_color=WHITE,
        fill_opacity=1,
    )
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
        self.rng = np.random.default_rng(11)

        self.intro()
        self.doodle("A00", "cross out the tiny route card")
        self.wave_scene()
        self.landscape_scene()
        self.detection_scene()
        self.repeat_scene()
        self.doodle("A10", "cross out the hidden bead")
        self.movement_scene()
        self.final_line()
        self.outro()

    def remove_all(self):
        for mob in list(self.mobjects):
            self.remove(mob)

    def hold(self, bid, used):
        self.wait(max(0.05, dur(bid) - used))

    def doodle_box(self, label):
        box = DashedVMobject(
            RoundedRectangle(width=5.45, height=2.85, corner_radius=0.18, color=GHOST, stroke_width=4),
            num_dashes=40,
        )
        tag = txt(f"[doodle {label}]", size=30, color=GHOST).next_to(box, DOWN, buff=0.25)
        return VGroup(box, tag)

    def _intro_hero(self):
        g1 = Line([-2.2, 0.7, 0], [2.2, 0.7, 0], color=INK, stroke_width=5)
        g2 = Line([-2.2, -0.7, 0], [2.2, -0.7, 0], color=INK, stroke_width=5)
        wv = ParametricFunction(lambda x: [x, 0.45 * np.sin(3 * x), 0], t_range=[-2.2, 2.2, 0.03], color=ACCENT, stroke_width=4)
        return VGroup(g1, g2, wv)

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
    def wave_scene(self):
        self.remove_all()
        origin = Dot([-2.65, 0, 0], radius=0.12, color=FORBIDDEN)
        rings = VGroup(*[
            Circle(radius=r, color=ACCENT, stroke_width=4).move_to(origin).set_opacity(0.8 - i * 0.12)
            for i, r in enumerate((0.5, 1.0, 1.55, 2.1))
        ])
        spots = VGroup(*[
            Dot([x, y, 0], radius=0.06, color=INK).set_opacity(0.6)
            for x, y in [(-1.0, 1.1), (0.2, 0.55), (1.25, -0.4), (2.35, 0.9), (0.7, -1.2)]
        ])
        lab = txt("possible landing places", size=34, color=ACCENT).move_to([1.1, 2.35, 0])
        self.play(GrowFromCenter(origin), LaggedStartMap(Create, rings, lag_ratio=0.15), FadeIn(spots), FadeIn(lab), run_time=1.8)
        self.hold("A01", 1.8)

        not_material = txt("not electron material", size=34, color=FORBIDDEN).move_to([0, -2.55, 0])
        slash = Line([-2.1, -2.78, 0], [2.1, -2.33, 0], color=FORBIDDEN, stroke_width=5)
        self.play(FadeIn(not_material), Create(slash), rings.animate.set_opacity(0.25), run_time=1.25)
        self.hold("A02", 1.25)

    def landscape_curve(self):
        return ParametricFunction(
            lambda t: np.array([t, -1.35 + 2.05 * np.exp(-((t + 0.85) / 1.0) ** 2) + 0.75 * np.exp(-((t - 1.65) / 0.65) ** 2), 0]),
            t_range=[-3.6, 3.6, 0.035],
            color=ACCENT,
            stroke_width=5,
        )

    def landscape_scene(self):
        self.remove_all()
        floor = Line([-4.0, -1.35, 0], [4.0, -1.35, 0], color=INK, stroke_width=3)
        curve = self.landscape_curve()
        click = Dot([-0.55, 0.55, 0], radius=0.11, color=FORBIDDEN)
        title = txt("probability landscape", size=38, color=ACCENT).move_to([0, 2.45, 0])
        self.play(Create(floor), Create(curve), FadeIn(click), FadeIn(title), run_time=1.45)
        self.hold("A03", 1.45)

        high_arrow = Arrow([-0.95, 2.05, 0], [-0.75, 0.9, 0], color=FORBIDDEN, stroke_width=4, buff=0.05)
        high = txt("more likely", size=32, color=FORBIDDEN).next_to(high_arrow, UP, buff=0.15)
        self.play(GrowArrow(high_arrow), FadeIn(high), run_time=1.1)
        self.hold("A04", 1.1)

        low_arrow = Arrow([2.85, 0.65, 0], [3.25, -1.05, 0], color=GHOST, stroke_width=4, buff=0.05)
        low = txt("less likely", size=32, color=GHOST).next_to(low_arrow, UP, buff=0.15)
        self.play(GrowArrow(low_arrow), FadeIn(low), run_time=1.1)
        self.hold("A05", 1.1)

    def detection_scene(self):
        self.remove_all()
        wall = Line([3.6, -2.55, 0], [3.6, 2.55, 0], color=INK, stroke_width=5)
        wave = self.landscape_curve().scale(0.62).move_to([-1.05, -0.15, 0]).set_opacity(0.35)
        dot = Dot([3.6, 0.45, 0], radius=0.12, color=FORBIDDEN)
        lab = txt("one red dot", size=34, color=FORBIDDEN).next_to(dot, LEFT, buff=0.35)
        self.play(FadeIn(wave), Create(wall), FadeIn(dot), FadeIn(lab), run_time=1.3)
        self.hold("A06", 1.3)

        arrow = Arrow([0.9, 0.2, 0], [3.45, 0.45, 0], color=FORBIDDEN, stroke_width=4, buff=0.05)
        collapse = txt("single result", size=34, color=FORBIDDEN).move_to([0, 2.25, 0])
        self.play(wave.animate.set_opacity(0.1).scale(0.7), GrowArrow(arrow), FadeIn(collapse), run_time=1.35)
        self.hold("A07", 1.35)

    def repeat_scene(self):
        self.remove_all()
        wall = Line([4.25, -2.7, 0], [4.25, 2.7, 0], color=INK, stroke_width=5)
        first = Dot([4.25, 0.75, 0], radius=0.09, color=GHOST)
        second = Dot([4.25, -0.35, 0], radius=0.11, color=FORBIDDEN)
        again = txt("same setup, new click", size=34, color=FORBIDDEN).move_to([0, 2.35, 0])
        self.play(Create(wall), FadeIn(first), FadeIn(second), FadeIn(again), run_time=1.35)
        self.hold("A08", 1.35)

        ys = self.sample_pattern(280)
        dots = VGroup(*[Dot([4.25 + self.rng.uniform(-0.07, 0.07), y, 0], radius=0.028, color=INK) for y in ys])
        shape = self.landscape_curve().rotate(PI / 2).scale(0.55).move_to([2.05, 0, 0]).set_color(ACCENT)
        label = txt("dots trace the wave", size=32, color=ACCENT).move_to([0, 2.35, 0])
        self.play(Transform(again, label), FadeIn(dots, lag_ratio=0.004), Create(shape), run_time=2.1)
        self.hold("A09", 2.1)

    def movement_scene(self):
        self.remove_all()
        axes = VGroup(
            Line([-4.0, -1.25, 0], [4.0, -1.25, 0], color=INK, stroke_width=3),
            Line([-3.8, -1.45, 0], [-3.8, 2.2, 0], color=INK, stroke_width=3),
        )
        wave1 = self.landscape_curve().scale(0.72).move_to([-0.25, -0.1, 0])
        wave2 = self.landscape_curve().scale(0.72).move_to([0.75, -0.1, 0]).set_opacity(0.25)
        motion = Arrow([-0.4, 1.65, 0], [0.9, 1.65, 0], color=FORBIDDEN, stroke_width=4, buff=0.05)
        moving = txt("how the wave moves", size=36, color=FORBIDDEN).move_to([0, 2.45, 0])
        self.play(Create(axes), Create(wave1), FadeIn(wave2), GrowArrow(motion), FadeIn(moving), run_time=1.6)
        self.hold("A11", 1.6)

        rulebook = label_box("quantum mechanics", width=4.0, color=INK).move_to([0, -2.45, 0])
        self.play(FadeIn(rulebook), wave1.animate.shift(RIGHT * 0.55), wave2.animate.set_opacity(0.45), run_time=1.35)
        self.hold("A12", 1.35)

    def final_line(self):
        self.remove_all()
        map_box = label_box("spread-out\npossibility map", width=3.7, height=1.25, color=ACCENT).move_to([-2.35, 0.3, 0])
        arrow = Arrow([-0.35, 0.3, 0], [1.25, 0.3, 0], color=INK, stroke_width=4, buff=0.12)
        click = VGroup(Dot([2.35, 0.3, 0], radius=0.15, color=FORBIDDEN), txt("one click", size=34, color=FORBIDDEN).next_to([2.35, 0.3, 0], DOWN, buff=0.25))
        title = txt("wave guides the odds", size=44, color=INK).move_to([0, 2.25, 0])
        self.play(FadeIn(map_box), GrowArrow(arrow), FadeIn(click), FadeIn(title), run_time=1.7)
        self.hold("A13", 1.7)

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

    def sample_pattern(self, n):
        out = []
        while len(out) < n:
            y = self.rng.uniform(-2.45, 2.45)
            p = 0.2 + 0.8 * np.exp(-((y - 0.35) / 0.9) ** 2) + 0.35 * np.exp(-((y + 1.35) / 0.55) ** 2)
            p = min(1.0, p / 1.35)
            if self.rng.uniform() < p:
                out.append(y)
        return out
