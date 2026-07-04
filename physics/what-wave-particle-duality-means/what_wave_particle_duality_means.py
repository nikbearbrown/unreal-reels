"""
Bear's Notes - What Wave-Particle Duality Means

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
TITLE = META.get("title", "What Wave-Particle Duality Means")


def dur(bid, fallback=3.0):
    return float(TIMINGS.get(bid, fallback))


def txt(s, size=34, color=INK):
    return Text(s, font=FONT, font_size=size, color=color)


def label_box(s, width=2.8, height=1.0, color=INK):
    box = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.14,
        stroke_width=4,
        color=color,
        fill_color=WHITE,
        fill_opacity=1,
    )
    label = txt(s, size=30, color=color).move_to(box)
    return VGroup(box, label)


def wave_arc(center, radius, color=ACCENT, start=0, angle=TAU):
    return Arc(radius=radius, start_angle=start, angle=angle, arc_center=center, color=color, stroke_width=4)


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
        self.rng = np.random.default_rng(7)

        self.intro()
        self.scene_everyday_particles()
        self.scene_everyday_waves()
        self.scene_electron_wave()
        self.scene_detection_pattern()
        self.scene_summary()
        self.doodle("A13", "whisper lands in one ear")
        self.doodle("A14", "one leaf gets the ripple")
        self.final_line()
        self.outro()

    def remove_all(self):
        for mob in list(self.mobjects):
            self.remove(mob)

    def hold(self, bid, used):
        self.wait(max(0.05, dur(bid) - used))

    def doodle_box(self, label):
        box = DashedVMobject(
            RoundedRectangle(width=5.2, height=2.8, corner_radius=0.18, color=GHOST, stroke_width=4),
            num_dashes=38,
        )
        tag = txt(f"[doodle {label}]", size=30, color=GHOST).next_to(box, DOWN, buff=0.25)
        return VGroup(box, tag)

    def _intro_hero(self):
        wv = ParametricFunction(lambda x: [x, 0.5 * np.sin(3 * x), 0], t_range=[-2.4, -0.2, 0.03], color=ACCENT, stroke_width=4)
        dot = Dot([1.4, 0, 0], color=ACCENT, radius=0.18)
        return VGroup(wv, dot)

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

    def scene_everyday_particles(self):
        self.remove_all()
        track = Line([-4.2, -1.25, 0], [3.5, -1.25, 0], color=INK, stroke_width=4)
        start = Dot([-3.6, -1.25, 0], radius=0.08, color=INK)
        stop = Dot([2.8, -1.25, 0], radius=0.11, color=FORBIDDEN)
        path = VMobject(color=ACCENT, stroke_width=5)
        path.set_points_smoothly([[-3.6, -0.9, 0], [-1.2, -0.3, 0], [0.9, -0.55, 0], [2.8, -1.1, 0]])
        lab = txt("one clean story", size=36, color=ACCENT).move_to([0, 1.65, 0])
        self.play(Create(track), FadeIn(start), FadeIn(stop), Create(path), FadeIn(lab), run_time=1.45)
        self.hold("A00", 1.45)

        marble = Circle(radius=0.28, color=INK, stroke_width=4).set_fill(SOFT, opacity=0.6).move_to([-3.6, -0.98, 0])
        endpoint = Circle(radius=0.22, color=FORBIDDEN, stroke_width=4).move_to([2.8, -0.98, 0])
        one_track = txt("one track", size=30, color=INK).move_to([-2.0, -2.2, 0])
        one_stop = txt("one stop", size=30, color=FORBIDDEN).move_to([2.8, -2.2, 0])
        self.play(FadeIn(marble), FadeIn(endpoint), FadeIn(one_track), FadeIn(one_stop), run_time=1.1)
        self.play(marble.animate.move_to(endpoint.get_center()), run_time=0.9)
        self.hold("A01", 2.0)

    def scene_everyday_waves(self):
        self.remove_all()
        center = Dot([0, -0.45, 0], radius=0.11, color=INK)
        rings = VGroup(*[Circle(radius=r, color=ACCENT, stroke_width=4).move_to(center) for r in (0.45, 0.9, 1.35, 1.8)])
        lab = txt("opposite story", size=36, color=ACCENT).move_to([0, 2.2, 0])
        self.play(GrowFromCenter(center), LaggedStartMap(Create, rings, lag_ratio=0.18), FadeIn(lab), run_time=1.65)
        self.hold("A02", 1.8)

        touches = VGroup(*[
            Dot([1.8 * np.cos(a), -0.45 + 1.8 * np.sin(a), 0], radius=0.07, color=FORBIDDEN)
            for a in np.linspace(0, TAU, 10, endpoint=False)
        ])
        many = txt("many places together", size=34, color=FORBIDDEN).move_to([0, -2.65, 0])
        self.play(FadeIn(touches, lag_ratio=0.05), FadeIn(many), run_time=1.3)
        self.hold("A03", 1.8)

    def scene_electron_wave(self):
        self.remove_all()
        track = label_box("one track", color=INK).move_to([-2.9, 0.25, 0])
        spread = label_box("spread out", width=3.0, color=ACCENT).move_to([2.9, 0.25, 0])
        electron = Dot([0, 0.25, 0], radius=0.16, color=FORBIDDEN)
        title = txt("one quantum event", size=38, color=FORBIDDEN).move_to([0, 2.25, 0])
        self.play(FadeIn(track), FadeIn(spread), GrowFromCenter(electron), FadeIn(title), run_time=1.5)
        self.hold("A04", 1.5)

        self.remove_all()
        origin = Dot([0, 0, 0], radius=0.11, color=FORBIDDEN)
        rings = VGroup(*[Circle(radius=r, color=ACCENT, stroke_width=3).set_opacity(0.75 - 0.12 * i) for i, r in enumerate((0.75, 1.35, 1.95, 2.55))])
        lab = txt("before detection", size=34, color=ACCENT).move_to([0, 2.55, 0])
        self.play(GrowFromCenter(origin), LaggedStartMap(Create, rings, lag_ratio=0.18), FadeIn(lab), run_time=1.65)
        self.hold("A05", 1.65)

        not_stuff = txt("not smeared stuff", size=34, color=FORBIDDEN).move_to([0, -2.65, 0])
        slash = Line([-1.9, -2.85, 0], [1.9, -2.45, 0], color=FORBIDDEN, stroke_width=5)
        self.play(FadeIn(not_stuff), Create(slash), rings.animate.set_opacity(0.32), run_time=1.35)
        self.hold("A06", 1.35)

        rays = VGroup()
        for a in np.linspace(0, TAU, 16, endpoint=False):
            rays.add(Line([0, 0, 0], [2.7 * np.cos(a), 2.15 * np.sin(a), 0], color=GHOST, stroke_width=2))
        amap = txt("arrival map", size=34, color=ACCENT).move_to([0, 2.55, 0])
        self.play(FadeOut(not_stuff), FadeOut(slash), Transform(lab, amap), LaggedStartMap(Create, rays, lag_ratio=0.02), run_time=1.3)
        self.hold("A07", 1.3)

    def scene_detection_pattern(self):
        self.remove_all()
        wall = Line([4.5, -2.8, 0], [4.5, 2.8, 0], color=INK, stroke_width=5)
        dot = Dot([4.5, 0.3, 0], radius=0.08, color=FORBIDDEN)
        wave = VGroup(*[Circle(radius=r, color=ACCENT, stroke_width=3).set_opacity(0.25) for r in (0.8, 1.4, 2.0)]).move_to([0, 0, 0])
        lab = txt("one electron -> one dot", size=32, color=FORBIDDEN).move_to([0, 2.35, 0])
        self.play(FadeIn(wave), Create(wall), FadeIn(dot), FadeIn(lab), run_time=1.25)
        self.hold("A08", 1.25)

        ys = self.sample_stripes(310)
        dots = VGroup(*[Dot([4.5 + self.rng.uniform(-0.08, 0.08), y, 0], radius=0.026, color=INK) for y in ys])
        many = txt("many dots reveal the map", size=30, color=ACCENT).move_to([0, 2.35, 0])
        self.play(Transform(lab, many), FadeIn(dots, lag_ratio=0.004), run_time=2.2)
        self.hold("A09", 2.2)

        curve = ParametricFunction(
            lambda t: np.array([1.0 + 2.0 * ((np.cos(2.25 * t) ** 2) * np.exp(-(t / 2.25) ** 2)), t, 0]),
            t_range=[-2.7, 2.7, 0.035],
            color=ACCENT,
            stroke_width=5,
        )
        clab = txt("pattern, not route", size=30, color=ACCENT).next_to(curve, RIGHT, buff=0.15)
        self.play(Create(curve), FadeIn(clab), run_time=1.35)
        self.hold("A10", 1.35)

        arrow = Arrow([2.5, -1.8, 0], [4.5, -1.25, 0], color=FORBIDDEN, stroke_width=4, buff=0.05)
        single = txt("single click", size=32, color=FORBIDDEN).next_to(arrow, LEFT, buff=0.2)
        one_more = Dot([4.5, -1.25, 0], radius=0.09, color=FORBIDDEN)
        self.play(GrowArrow(arrow), FadeIn(single), FadeIn(one_more), run_time=1.5)
        self.hold("A11", 1.5)

    def scene_summary(self):
        self.remove_all()
        wave = label_box("wave-shaped\npossibilities", width=3.4, height=1.25, color=ACCENT).move_to([-2.2, 0.45, 0])
        plus = txt("+", size=56, color=INK).move_to([0, 0.45, 0])
        point = label_box("particle-shaped\nresults", width=3.4, height=1.25, color=FORBIDDEN).move_to([2.35, 0.45, 0])
        title = txt("duality", size=48, color=INK).move_to([0, 2.15, 0])
        self.play(FadeIn(wave), FadeIn(plus), FadeIn(point), Write(title), run_time=2.0)
        self.hold("A12", 2.0)

    def doodle(self, bid, label):
        self.remove_all()
        card = _card(_NARR.get(bid, label))
        self.play(Write(card), run_time=1.0)
        self.hold(bid, 1.0)
    def final_line(self):
        self.remove_all()
        electron = Dot([0, 0.35, 0], radius=0.14, color=FORBIDDEN)
        rings = VGroup(*[Circle(radius=r, color=ACCENT, stroke_width=4).set_opacity(0.7 - i * 0.15) for i, r in enumerate((0.65, 1.25, 1.85))])
        dot_label = txt("one click", size=32, color=FORBIDDEN).move_to([0, -2.35, 0])
        line = txt("strange, but real", size=44, color=INK).move_to([0, 2.35, 0])
        self.play(GrowFromCenter(electron), LaggedStartMap(Create, rings, lag_ratio=0.12), FadeIn(dot_label), FadeIn(line), run_time=2.1)
        self.hold("A15", 2.1)

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

    def sample_stripes(self, n):
        out = []
        while len(out) < n:
            y = self.rng.uniform(-2.6, 2.6)
            p = (np.cos(2.25 * y) ** 2) * np.exp(-(y / 2.2) ** 2)
            if self.rng.uniform() < p:
                out.append(y)
        return out
