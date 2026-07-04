"""
Bear's Notes - Who Observes Schrodinger's Cat

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
TITLE = META.get("title", "Who Observes Schrödinger's Cat")


def dur(bid, fallback=3.0):
    return float(TIMINGS.get(bid, fallback))


def txt(s, size=34, color=INK):
    return Text(s, font=FONT, font_size=size, color=color)


def label_box(s, width=3.0, height=1.0, color=INK, size=28):
    box = RoundedRectangle(width=width, height=height, corner_radius=0.14, stroke_width=4, color=color, fill_color=WHITE, fill_opacity=1)
    label = txt(s, size=size, color=color).move_to(box)
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
        self.doodle("A00", "cat story crossed out")
        self.observation_question()
        self.doodle("A02", "sealed box with quantum trigger")
        self.event_branches()
        self.cat_branches()
        self.entanglement_scene()
        self.observer_scene()
        self.collapse_scene()
        self.possibilities_scene()
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
        box = Rectangle(width=1.7, height=1.5, color=INK, stroke_width=5)
        q = txt("?", size=72, color=ACCENT).move_to(box.get_center())
        return VGroup(box, q)

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
    def observation_question(self):
        self.remove_all()
        q = txt("observation", size=56, color=ACCENT).move_to([0, 0.35, 0])
        mark = txt("?", size=92, color=FORBIDDEN).next_to(q, RIGHT, buff=0.35)
        line = Line([-2.55, -0.45, 0], [2.55, -0.45, 0], color=INK, stroke_width=4)
        label = txt("where does it begin?", size=36, color=INK).move_to([0, -1.2, 0])
        self.play(FadeIn(q), FadeIn(mark), Create(line), FadeIn(label), run_time=1.35)
        self.hold("A01", 1.35)

    def event_branches(self):
        self.remove_all()
        event = label_box("quantum\nevent", width=2.3, height=1.1, color=INK).move_to([-4.0, 0, 0])
        top = label_box("record A", width=2.4, height=1.0, color=ACCENT).move_to([1.6, 1.15, 0])
        bottom = label_box("record B", width=2.4, height=1.0, color=ACCENT).move_to([1.6, -1.15, 0])
        a1 = Arrow([-2.75, 0.22, 0], [0.2, 1.08, 0], color=INK, stroke_width=4, buff=0.1)
        a2 = Arrow([-2.75, -0.22, 0], [0.2, -1.08, 0], color=INK, stroke_width=4, buff=0.1)
        self.play(FadeIn(event), GrowArrow(a1), GrowArrow(a2), FadeIn(top), FadeIn(bottom), run_time=1.55)
        self.hold("A03", 1.55)

        fired = txt("trigger fired", size=32, color=FORBIDDEN).move_to(top)
        self.play(Transform(top[1], fired), run_time=0.9)
        self.hold("A04", 0.9)

        quiet = txt("trigger quiet", size=32, color=ACCENT).move_to(bottom)
        self.play(Transform(bottom[1], quiet), run_time=0.9)
        self.hold("A05", 0.9)

    def cat_marker(self, pos, color=INK):
        face = Circle(radius=0.28, color=color, stroke_width=4).move_to(pos)
        ears = VGroup(
            Polygon(np.array(pos) + [-0.18, 0.22, 0], np.array(pos) + [-0.04, 0.48, 0], np.array(pos) + [0.08, 0.22, 0], color=color, stroke_width=4),
            Polygon(np.array(pos) + [0.18, 0.22, 0], np.array(pos) + [0.04, 0.48, 0], np.array(pos) + [-0.08, 0.22, 0], color=color, stroke_width=4),
        )
        eyes = VGroup(Dot(np.array(pos)+[-0.09, 0.04, 0], radius=0.025, color=color), Dot(np.array(pos)+[0.09, 0.04, 0], radius=0.025, color=color))
        return VGroup(face, ears, eyes)

    def cat_branches(self):
        self.remove_all()
        cat = self.cat_marker([-3.9, 0, 0])
        top = label_box("branch A", width=2.8, height=1.0, color=FORBIDDEN).move_to([1.55, 1.2, 0])
        bottom = label_box("branch B", width=2.8, height=1.0, color=ACCENT).move_to([1.55, -1.2, 0])
        a1 = Arrow([-3.25, 0.22, 0], [0.05, 1.1, 0], color=INK, stroke_width=4, buff=0.1)
        a2 = Arrow([-3.25, -0.22, 0], [0.05, -1.1, 0], color=INK, stroke_width=4, buff=0.1)
        note = txt("not separate", size=38, color=FORBIDDEN).move_to([0, 2.45, 0])
        self.play(Create(cat), GrowArrow(a1), GrowArrow(a2), FadeIn(top), FadeIn(bottom), FadeIn(note), run_time=1.5)
        self.hold("A06", 1.5)

        follows = txt("experience follows event", size=36, color=ACCENT).move_to([0, -2.45, 0])
        self.play(FadeIn(follows), run_time=1.0)
        self.hold("A07", 1.0)

        top_pair = txt("fired + saw result", size=31, color=FORBIDDEN).move_to(top)
        self.play(Transform(top[1], top_pair), run_time=0.95)
        self.hold("A08", 0.95)

        bottom_pair = txt("quiet + saw nothing", size=31, color=ACCENT).move_to(bottom)
        self.play(Transform(bottom[1], bottom_pair), run_time=0.95)
        self.hold("A09", 0.95)

    def entanglement_scene(self):
        self.remove_all()
        bad = label_box("fired\n+\nunseen", width=2.6, height=1.55, color=FORBIDDEN, size=26).move_to([-2.5, 0.3, 0])
        cross = Cross(bad, stroke_color=FORBIDDEN, stroke_width=5)
        good = label_box("records\nmust match", width=3.0, height=1.25, color=ACCENT).move_to([2.1, 0.3, 0])
        self.play(FadeIn(bad), Create(cross), FadeIn(good), run_time=1.35)
        self.hold("A10", 1.35)

        link = CurvedArrow([-1.0, -1.05, 0], [0.65, -1.05, 0], angle=-TAU/4, color=ACCENT, stroke_width=4)
        lab = txt("entanglement", size=46, color=ACCENT).move_to([0, 2.2, 0])
        not_ignorance = txt("not ordinary ignorance", size=34, color=FORBIDDEN).move_to([0, -2.15, 0])
        self.play(Create(link), FadeIn(lab), FadeIn(not_ignorance), run_time=1.2)
        self.hold("A11", 1.2)

    def observer_scene(self):
        self.remove_all()
        box = Rectangle(width=2.1, height=1.35, color=INK, stroke_width=4).move_to([-2.85, 0, 0])
        observer = label_box("observer", width=2.4, height=1.0, color=INK).move_to([2.9, 0, 0])
        record = label_box("same\nrecord", width=2.2, height=1.0, color=ACCENT).move_to([0, 1.35, 0])
        arrow1 = Arrow([-1.75, 0.35, 0], [-0.75, 1.05, 0], color=ACCENT, stroke_width=4, buff=0.05)
        arrow2 = Arrow([1.75, 0.35, 0], [0.75, 1.05, 0], color=ACCENT, stroke_width=4, buff=0.05)
        self.play(Create(box), FadeIn(observer), FadeIn(record), GrowArrow(arrow1), GrowArrow(arrow2), run_time=1.45)
        self.hold("A12", 1.45)

        branch = RoundedRectangle(width=6.2, height=2.3, corner_radius=0.18, color=GHOST, stroke_width=4).move_to([0, 0.4, 0])
        blab = txt("observer is in the branch", size=34, color=FORBIDDEN).move_to([0, -1.55, 0])
        self.play(Create(branch), FadeIn(blab), run_time=1.2)
        self.hold("A13", 1.2)

    def collapse_scene(self):
        self.remove_all()
        left = label_box("history A", width=2.4, height=1.0, color=GHOST).move_to([-2.4, 0.8, 0])
        right = label_box("history B", width=2.4, height=1.0, color=GHOST).move_to([2.4, 0.8, 0])
        selected = SurroundingRectangle(left, color=FORBIDDEN, stroke_width=5, buff=0.18)
        collapse = txt("collapse?", size=52, color=FORBIDDEN).move_to([0, -0.9, 0])
        self.play(FadeIn(left), FadeIn(right), Create(selected), FadeIn(collapse), run_time=1.45)
        self.hold("A14", 1.45)

        q = txt("final observer?", size=44, color=ACCENT).move_to([0, -2.25, 0])
        marks = VGroup(*[txt("?", size=42, color=FORBIDDEN).move_to([x, 2.15, 0]) for x in [-1.0, 0, 1.0]])
        self.play(FadeIn(q), LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.15), run_time=1.1)
        self.hold("A15", 1.1)

    def possibilities_scene(self):
        self.remove_all()
        one = label_box("one outcome\nbecomes real", width=3.2, height=1.25, color=FORBIDDEN).move_to([-2.65, 0.65, 0])
        unknown = txt("unknown why", size=34, color=FORBIDDEN).move_to([-2.65, -0.65, 0])
        self.play(FadeIn(one), FadeIn(unknown), run_time=1.25)
        self.hold("A16", 1.25)

        trunk = Line([1.05, -1.6, 0], [1.05, 1.4, 0], color=INK, stroke_width=4)
        branches = VGroup()
        for y in [-0.85, -0.15, 0.55, 1.15]:
            branches.add(Line([1.05, y, 0], [3.55, y + 0.45, 0], color=ACCENT, stroke_width=4))
            branches.add(Line([1.05, y, 0], [3.55, y - 0.45, 0], color=ACCENT, stroke_width=4))
        many = txt("branches continue", size=34, color=ACCENT).move_to([2.45, -2.25, 0])
        self.play(Create(trunk), Create(branches), FadeIn(many), run_time=1.45)
        self.hold("A17", 1.45)

        summary = txt("the measurement problem", size=52, color=INK).move_to([0, 2.65, 0])
        arrow = Arrow([-0.8, 2.25, 0], [0.8, 2.25, 0], color=FORBIDDEN, stroke_width=4, buff=0.05)
        self.play(FadeIn(summary), GrowArrow(arrow), run_time=1.0)
        self.hold("A18", 1.0)

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
