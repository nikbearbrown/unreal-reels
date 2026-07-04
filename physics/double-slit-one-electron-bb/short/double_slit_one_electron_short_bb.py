#!/usr/bin/env python3
"""
double_slit_one_electron_short_bb.py — Brown Blue SHORT cut (< 3:00).

Condensed single-electron double slit: apparatus in R_MAIN, equations in a
slim R_TOP strip. Dots sampled from the real cos² fringe distribution (fixed
seed). All fill-only shapes silence their stroke (audit-safe).

Render:
    manim -qh double_slit_one_electron_short_bb.py BearsDoodlesVideo               # 16:9
    manim -qh -r 1080,1920 double_slit_one_electron_short_bb.py BearsDoodlesVideo  # 9:16
"""
import json
import math
from pathlib import Path

from manim import *  # noqa: F401,F403
import numpy as np
import bn_layout as BL  # noqa: F401
from bn_layout import (is_portrait, band, rows, cols, fit, fit_width, fit_text,
                       rw, rh, rcx, rcy, center, safe_w, safe_h, inset)

HERE = Path(__file__).resolve().parent
SHEET = json.loads((HERE / "beat_sheet.json").read_text())
TIMINGS_PATH = HERE / "mp3" / "timings.json"
TIMINGS = json.loads(TIMINGS_PATH.read_text()) if TIMINGS_PATH.exists() else {}
META = SHEET["metadata"]

CANVAS    = "#16161D"
INK       = "#ECE6D8"
BLUE      = META.get("accent_color", "#58C4DD")
BROWN     = META.get("brown_color", "#CD853F")
HIGHLIGHT = META.get("highlight_color", "#F0E442")
SECONDARY = "#8A8780"
HAIRLINE  = "#3A3A44"
FONT      = META.get("text_font", "EB Garamond")
TITLE     = META.get("title", "")


def dur(beat_id, fallback=4.0):
    return float(TIMINGS.get(beat_id, fallback))


def txt(s, size=36, color=INK, weight="NORMAL"):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight)


class BearsDoodlesVideo(Scene):
    def construct(self):
        self.camera.background_color = CANVAS
        self.port = is_portrait()
        b = band()
        self.R_full = b
        top, main = rows(b, [0.20, 0.80], gap=0.25)
        self.R_top = inset(top, 0.10, 0.10)
        self.R_main = inset(main, 0.15, 0.20)
        self._setup_lab_geometry()

        for beat in SHEET["beats"]:
            bid, btype = beat["beat_id"], beat["beat_type"]
            if btype == "INTRO":
                self._intro(dur(bid, 2.5))
                continue
            if btype == "CUT" and self.mobjects:
                self.play(FadeOut(*self.mobjects), run_time=0.4)
                self.wait(0.1)
            m = getattr(self, f"draw_{bid}", None)
            if m is not None:
                m(dur(bid))
            elif btype == "HOLD":
                self.wait(dur(bid, 2.0))
            else:
                self._text_card(beat.get("narration_text", ""), dur(bid))

    # ── helpers ──────────────────────────────────────────────────────────────
    def _pace(self, t, f=0.5):
        d = max(0.4, min(2.0, t * f))
        return d, max(0.2, t - d)

    def _text_card(self, s, t):
        g = fit_text(" ".join(s.split()), FONT, 40, INK, rw(self.R_full) * 0.96)
        card = fit(g, self.R_full, 0.96)
        d, h = self._pace(t)
        self.play(Write(card), run_time=d)
        self.wait(h - 0.3)
        self.play(FadeOut(card), run_time=0.3)

    def _intro(self, t):
        brow, trow, rrow = rows(self.R_full, [0.30, 0.45, 0.25], gap=0.25)
        brand = fit(txt("Bear's Notes", 40, SECONDARY), brow, 0.7)
        title = fit(fit_text(TITLE, FONT, 54, INK, rw(trow) * 0.96), trow, 0.96)
        rule = Line(LEFT, RIGHT, color=BROWN, stroke_width=3)
        rule.set_width(min(title.width, rw(rrow) * 0.8)).move_to(center(rrow))
        tick = Dot(color=BLUE, radius=0.06).next_to(rule, RIGHT, buff=0.15)
        self.play(FadeIn(brand), run_time=0.5)
        self.play(Write(title), run_time=min(1.4, t * 0.5))
        self.play(Create(rule), FadeIn(tick), run_time=0.5)
        self.wait(max(0.2, t - 2.6))
        self.play(FadeOut(brand, title, rule, tick), run_time=0.4)

    def _place_counter(self, c):
        """Bottom-left of the lab, capped to end LEFT of the barrier (the full
        text otherwise runs into the barrier's lower segment in portrait)."""
        maxw = (self.bx - 0.30) - self.R_main[0] - 0.12
        if c.width > maxw:
            c.scale_to_fit_width(maxw)
        c.move_to([self.R_main[0] + c.width / 2 + 0.12,
                   self.R_main[1] + c.height / 2 + 0.08, 0])
        return c

    def _microdot(self, y):
        x = self.sx - 0.10 + float(self.rng.uniform(-0.04, 0.04))
        return Dot([x, y, 0], color=INK, radius=0.03).set_stroke(opacity=0)

    # ── lab geometry ──────────────────────────────────────────────────────────
    def _setup_lab_geometry(self):
        r = self.R_main
        self.gx = r[0] + rw(r) * 0.10
        self.bx = r[0] + rw(r) * 0.46
        self.sx = r[2] - rw(r) * 0.05
        self.cy = rcy(r)
        span = rh(r) * 0.80
        self.ys0, self.ys1 = self.cy - span / 2, self.cy + span / 2
        self.span = span
        self.s1 = self.cy + span * 0.16
        self.s2 = self.cy - span * 0.16
        self.gap = span * 0.055
        self.rng = np.random.default_rng(7)
        wband = span / 5.0
        sig = 0.40 * span

        def inten(y):
            return (math.cos(math.pi * (y - self.cy) / wband) ** 2
                    * math.exp(-((y - self.cy) / sig) ** 2))
        self.inten = inten
        ys = []
        while len(ys) < 190:
            y = float(self.rng.uniform(self.ys0, self.ys1))
            if float(self.rng.uniform(0, 1)) < inten(y):
                ys.append(y)
        self.dot_ys = ys

    def _fringe_curve(self, color=BLUE):
        amp = rw(self.R_main) * 0.15
        return ParametricFunction(
            lambda s: np.array([self.sx - 0.20 - amp * self.inten(self.ys0 + s * self.span),
                                self.ys0 + s * self.span, 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)

    def _heaps_curve(self, color=SECONDARY, dashed=False):
        amp = rw(self.R_main) * 0.15
        sig = self.span * 0.10

        def ih(y):
            return (math.exp(-((y - self.s1) / sig) ** 2)
                    + math.exp(-((y - self.s2) / sig) ** 2))
        fn = ParametricFunction(
            lambda s: np.array([self.sx - 0.20 - amp * ih(self.ys0 + s * self.span),
                                self.ys0 + s * self.span, 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)
        return DashedVMobject(fn, num_dashes=40) if dashed else fn

    def _arc_fan(self, cyy, color=BLUE, opacity=0.7):
        reach = (self.sx - 0.30) - self.bx
        radii = np.linspace(0.22, max(0.5, reach), 4)
        return VGroup(*[
            Arc(radius=rr, start_angle=-PI / 3, angle=2 * PI / 3, color=color,
                stroke_width=2, stroke_opacity=opacity,
                arc_center=[self.bx, cyy, 0]) for rr in radii])

    def _fly(self, color, slit_y, land_y, tt, radius=0.07):
        e = Dot([self.gx + 0.12, self.cy, 0], color=color, radius=radius).set_stroke(opacity=0)
        self.add(e)
        self.play(e.animate.move_to([self.bx, slit_y, 0]),
                  run_time=tt * 0.45, rate_func=linear)
        self.play(e.animate.move_to([self.sx - 0.10, land_y, 0]),
                  run_time=tt * 0.45, rate_func=linear)
        d = self._microdot(land_y)
        d.move_to(e.get_center())
        self.remove(e)
        self.add(d)
        self.dots.add(d)
        self.wait(tt * 0.1)

    # ══════════════════════════ BEATS ════════════════════════════════════════
    def draw_H01(self, t):
        gun = RoundedRectangle(corner_radius=0.05, width=0.5, height=0.36,
                               color=INK, stroke_width=4,
                               fill_color=HAIRLINE, fill_opacity=0.35)
        gun.move_to([self.gx, self.cy, 0])
        bw = 5
        barrier = VGroup(
            Line([self.bx, self.ys1, 0], [self.bx, self.s1 + self.gap, 0], color=INK, stroke_width=bw),
            Line([self.bx, self.s1 - self.gap, 0], [self.bx, self.s2 + self.gap, 0], color=INK, stroke_width=bw),
            Line([self.bx, self.s2 - self.gap, 0], [self.bx, self.ys0, 0], color=INK, stroke_width=bw))
        screen = Line([self.sx, self.ys0, 0], [self.sx, self.ys1, 0], color=INK, stroke_width=5)
        self.gun, self.barrier, self.screen = gun, barrier, screen
        self.dots = VGroup()
        d, h = self._pace(t)
        self.play(Create(gun), Create(barrier), Create(screen), run_time=d)
        rest = max(0.8, h - 0.2)
        self._fly(BLUE, self.s1, self.dot_ys[0], rest * 0.5)
        self._fly(BLUE, self.s2, self.dot_ys[1], rest * 0.5)

    def draw_H02(self, t):
        batch = VGroup(*[self._microdot(y) for y in self.dot_ys[2:10]])
        self.dots.add(*batch)
        self.heaps_dashed = self._heaps_curve(SECONDARY, dashed=True)
        self.counter = self._place_counter(txt("electrons: 10", 24, SECONDARY))
        d, h = self._pace(t)
        self.play(LaggedStart(*[FadeIn(m, scale=0.4) for m in batch], lag_ratio=0.1),
                  FadeIn(self.counter), run_time=d)
        self.play(Create(self.heaps_dashed), run_time=min(1.2, h * 0.7))
        self.wait(max(0.2, h - 1.2))

    def draw_H03(self, t):
        batch = VGroup(*[self._microdot(y) for y in self.dot_ys[10:]])
        self.dots.add(*batch)
        new_c = self._place_counter(txt("electrons: 70,000", 24, INK))
        d, h = self._pace(t)
        self.play(LaggedStart(*[FadeIn(m, scale=0.4) for m in batch],
                              lag_ratio=min(0.02, 1.5 / len(batch))),
                  Transform(self.counter, new_c),
                  self.heaps_dashed.animate.set_stroke(opacity=0.25),
                  run_time=max(1.4, d))
        self.wait(max(0.3, h - 0.4))

    def draw_K01(self, t):
        self.fanA = self._arc_fan(self.s1)
        self.fanB = self._arc_fan(self.s2)
        self.stripes = self._fringe_curve(BLUE)
        d, h = self._pace(t)
        self.play(Create(self.fanA), Create(self.fanB), run_time=d * 0.7)
        self.play(Create(self.stripes), run_time=min(1.2, h * 0.7))
        self.wait(max(0.2, h - 1.2))

    def draw_K02(self, t):
        d, h = self._pace(t)
        self.play(self.fanA.animate.set_stroke(opacity=0.15),
                  self.fanB.animate.set_stroke(opacity=0.15), run_time=0.4)
        rest = max(0.9, t - 0.9)
        ball = Dot([self.gx + 0.12, self.cy, 0], color=BROWN, radius=0.08).set_stroke(opacity=0)
        self.add(ball)
        self.play(ball.animate.move_to([self.bx, self.s2, 0]), run_time=rest * 0.35, rate_func=linear)
        self.play(ball.animate.move_to([self.sx - 0.14, self.s2, 0]), run_time=rest * 0.35, rate_func=linear)
        self.play(self.heaps_dashed.animate.set_stroke(opacity=0.8), run_time=0.3)
        self.play(FadeOut(ball),
                  self.heaps_dashed.animate.set_stroke(opacity=0.3), run_time=0.4)

    def draw_K03(self, t):
        lbl = txt("one at a time", 22, INK)
        if lbl.width > rw(self.R_main) * 0.32:
            lbl.scale_to_fit_width(rw(self.R_main) * 0.32)
        lbl.next_to(self.gun, UP, buff=0.16)
        if lbl.get_top()[1] > self.R_main[3]:
            lbl.next_to(self.gun, DOWN, buff=0.16)
        if lbl.get_left()[0] < self.R_main[0]:
            lbl.shift(RIGHT * (self.R_main[0] - lbl.get_left()[0] + 0.06))
        d, h = self._pace(t)
        self.play(Write(lbl), run_time=d * 0.7)
        self.play(Indicate(self.gun, color=BLUE, scale_factor=1.08), run_time=0.6)
        self.wait(max(0.2, h - 0.6))

    def draw_A01(self, t):
        d, h = self._pace(t)
        self.play(self.fanA.animate.set_stroke(opacity=0.7),
                  self.fanB.animate.set_stroke(opacity=0.7), run_time=d)
        self.wait(max(0.3, h - 0.5))
        self.play(self.fanA.animate.set_stroke(opacity=0.2),
                  self.fanB.animate.set_stroke(opacity=0.2), run_time=0.5)

    def draw_A02(self, t):
        eq = MathTex(r"|\psi|^2", color=INK)
        fit(eq, self.R_top, 0.6)
        self.eq = eq
        d, h = self._pace(t)
        self.play(Write(eq), run_time=d)
        self.wait(max(0.2, h))

    def draw_P01(self, t):
        ring = Circle(radius=0.09, color=SECONDARY, stroke_width=3)
        pupil = Dot(radius=0.032, color=SECONDARY).set_stroke(opacity=0)
        pupil.move_to(ring.get_center())
        eye = VGroup(ring, pupil)
        eye.move_to([self.bx - 0.28, self.s1 + 0.02, 0])
        heaps = self._heaps_curve(BROWN, dashed=False)
        d, h = self._pace(t)
        self.play(FadeIn(eye, scale=0.6), run_time=d * 0.4)
        self.play(ReplacementTransform(self.stripes, heaps),
                  self.dots.animate.set_opacity(0.30),
                  self.fanA.animate.set_stroke(opacity=0.0),
                  self.fanB.animate.set_stroke(opacity=0.0),
                  FadeOut(self.heaps_dashed),
                  run_time=max(1.0, d * 0.8))
        self.wait(max(0.3, h - 0.6))

    def draw_B01(self, t):
        line = VGroup(
            txt("2,000-atom molecules: stripes", 24, INK),
            txt("·", 24, SECONDARY),
            MathTex(r"\mathrm{you:}\ \lambda \approx 10^{-35}\ \mathrm{m}", color=SECONDARY)
        ).arrange(RIGHT, buff=0.25)
        d, h = self._pace(t)
        self.play(FadeOut(self.eq), run_time=0.3)
        fit(line, self.R_top, 0.9)
        self.play(Write(line), run_time=d + 0.3)
        self.wait(max(0.2, h - 0.6))
        self.scale_line = line

    def draw_OUTRO(self, t):
        park = fit_text(TITLE, FONT, 28, INK, rw(self.R_top) * 0.94)
        fit(park, self.R_top, 0.9)
        park.set_opacity(0.7)
        self.play(FadeOut(self.scale_line), run_time=0.3)
        self.play(FadeIn(park), run_time=0.5)
        self.wait(max(0.3, t - 0.8))
