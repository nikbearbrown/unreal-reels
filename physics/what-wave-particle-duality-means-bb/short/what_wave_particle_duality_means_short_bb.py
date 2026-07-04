#!/usr/bin/env python3
"""
what_wave_particle_duality_means_short_bb.py — Brown Blue SHORT cut (< 3:00).

Condensed duality: cartoon killed by dimensions → two questions → two failed
stories → the possibility wave → |ψ|² → the definition. Apparatus in R_MAIN,
equations/definition in the R_TOP strip. Audit-safe patterns throughout.

Render:
    manim -qh what_wave_particle_duality_means_short_bb.py BearsDoodlesVideo               # 16:9
    manim -qh -r 1080,1920 what_wave_particle_duality_means_short_bb.py BearsDoodlesVideo  # 9:16
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

    # ── helpers ──────────────────────────────────────────────────────────────
    def _pace(self, t, f=0.5):
        d = max(0.4, min(2.0, t * f))
        return d, max(0.2, t - d)

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

    def _clamp_into(self, mobj, r, pad=0.06):
        if mobj.get_left()[0] < r[0]:
            mobj.shift(RIGHT * (r[0] - mobj.get_left()[0] + pad))
        if mobj.get_right()[0] > r[2]:
            mobj.shift(LEFT * (mobj.get_right()[0] - r[2] + pad))
        if mobj.get_top()[1] > r[3]:
            mobj.shift(DOWN * (mobj.get_top()[1] - r[3] + pad))
        if mobj.get_bottom()[1] < r[1]:
            mobj.shift(UP * (r[1] - mobj.get_bottom()[1] + pad))
        return mobj

    def _packet_wave(self, width=1.6, amp=0.28, color=BLUE):
        k = 5.5 * math.pi / width
        return ParametricFunction(
            lambda s: np.array([(s - 0.5) * width,
                                amp * math.exp(-((s - 0.5) / 0.22) ** 2)
                                * math.sin(k * (s - 0.5) * width), 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)

    def _build_lab_geometry(self):
        r = self.R_main
        self.gx = r[0] + rw(r) * 0.10
        self.bx = r[0] + rw(r) * 0.46
        self.sx = r[2] - rw(r) * 0.05
        self.cy = rcy(r)
        span = rh(r) * 0.72
        self.ys0, self.ys1 = self.cy - span / 2, self.cy + span / 2
        self.span = span
        self.s1 = self.cy + span * 0.16
        self.s2 = self.cy - span * 0.16
        self.gap = span * 0.055
        wband = span / 5.0
        sig = 0.40 * span

        def inten(y):
            return (math.cos(math.pi * (y - self.cy) / wband) ** 2
                    * math.exp(-((y - self.cy) / sig) ** 2))
        self.inten = inten

    def _fringe_curve(self, color=BLUE):
        amp = rw(self.R_main) * 0.14
        return ParametricFunction(
            lambda s: np.array([self.sx - 0.18 - amp * self.inten(self.ys0 + s * self.span),
                                self.ys0 + s * self.span, 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)

    def _heaps_curve(self, color=BROWN, dashed=True):
        amp = rw(self.R_main) * 0.14
        sig = self.span * 0.10

        def ih(y):
            return (math.exp(-((y - self.s1) / sig) ** 2)
                    + math.exp(-((y - self.s2) / sig) ** 2))
        fn = ParametricFunction(
            lambda s: np.array([self.sx - 0.18 - amp * ih(self.ys0 + s * self.span),
                                self.ys0 + s * self.span, 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)
        return DashedVMobject(fn, num_dashes=40) if dashed else fn

    # ══════════════════════════ BEATS ════════════════════════════════════════
    def draw_H01(self, t):
        ball = Dot(color=BROWN, radius=0.16).set_stroke(opacity=0)
        ripples = VGroup(*[Circle(radius=r, color=SECONDARY, stroke_width=2.5,
                                  stroke_opacity=0.8) for r in (0.45, 0.75, 1.05)])
        grp = VGroup(ball, ripples)
        for c in ripples:
            c.move_to(ball.get_center())
        fit(grp, self.R_main, 0.6)
        self.ball, self.ripples, self.cartoon = ball, ripples, grp
        d, h = self._pace(t)
        self.play(GrowFromCenter(ball), run_time=d * 0.5)
        self.play(LaggedStart(*[Create(c) for c in ripples], lag_ratio=0.25),
                  run_time=d)
        self.wait(max(0.2, h - 0.5))

    def draw_H02(self, t):
        brace = Brace(self.ripples, UP, color=BLUE)
        span_lbl = txt("0.167 nm", 24, BLUE).next_to(brace, UP, buff=0.1)
        self._clamp_into(span_lbl, self.R_main)
        tick_lbl = txt("÷ 60,000", 22, INK).next_to(self.ball, DOWN, buff=0.25)
        self._clamp_into(tick_lbl, self.R_main)
        d, h = self._pace(t)
        self.play(GrowFromCenter(brace), Write(span_lbl), run_time=d * 0.7)
        self.play(Write(tick_lbl), run_time=d * 0.5)
        self.play(self.cartoon.animate.set_opacity(0.4), run_time=0.4)
        self.wait(max(0.2, h - 0.9))

    def draw_M01(self, t):
        self._build_lab_geometry()
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
        streaks = VGroup(*[
            Line([self.gx + 0.3, self.cy, 0], [self.sx - 0.22, self.cy + dy, 0],
                 color=BLUE, stroke_width=1.5, stroke_opacity=0.35)
            for dy in np.linspace(-self.span * 0.3, self.span * 0.3, 5)])
        self.stripes = self._fringe_curve(BLUE)
        d, h = self._pace(t)
        self.play(Create(gun), Create(barrier), Create(screen), run_time=d * 0.8)
        self.play(LaggedStart(*[Create(s) for s in streaks], lag_ratio=0.1),
                  run_time=d * 0.5)
        self.play(FadeOut(streaks), Create(self.stripes), run_time=d * 0.7)
        self.wait(max(0.2, h - 1.2))

    def draw_M02(self, t):
        e = Dot([self.gx + 0.15, self.cy, 0], color=BLUE, radius=0.07).set_stroke(opacity=0)
        d, h = self._pace(t)
        self.add(e)
        self.play(e.animate.move_to([self.bx, self.s1, 0]), run_time=d * 0.4, rate_func=linear)
        self.play(e.animate.move_to([self.sx - 0.10, self.cy, 0]), run_time=d * 0.4, rate_func=linear)
        dot = Dot([self.sx - 0.10, self.cy, 0], color=INK, radius=0.05).set_stroke(opacity=0)
        self.remove(e)
        self.add(dot)
        self.play(Flash(dot, color=BLUE, line_length=0.12, num_lines=8,
                        flash_radius=0.2), run_time=0.5)
        self.wait(max(0.3, h - 0.5))

    def draw_S01(self, t):
        self.heaps = self._heaps_curve(BROWN, dashed=True)
        strike = Line([self.sx - 0.85, self.ys0 + 0.1, 0],
                      [self.sx - 0.05, self.ys1 - 0.1, 0],
                      color=SECONDARY, stroke_width=3)
        d, h = self._pace(t)
        self.play(Create(self.heaps), run_time=d * 0.8)
        self.play(Create(strike), run_time=0.5)
        self.play(VGroup(self.heaps, strike).animate.set_stroke(opacity=0.2),
                  run_time=0.4)
        self.s1_grp = VGroup(self.heaps, strike)
        self.wait(max(0.2, h - 0.9))

    def draw_S02(self, t):
        half = Sector(outer_radius=0.13, angle=PI, color=INK,
                      fill_opacity=0.9).set_stroke(opacity=0)
        half.move_to([self.sx - 0.5, self.cy - self.span * 0.3, 0])
        strike = Line(half.get_corner(DL) + DL * 0.1, half.get_corner(UR) + UR * 0.1,
                      color=SECONDARY, stroke_width=3)
        d, h = self._pace(t)
        self.play(FadeIn(half, scale=0.6), run_time=d * 0.5)
        self.play(Create(strike), run_time=0.4)
        self.play(FadeOut(VGroup(half, strike)), FadeOut(self.s1_grp),
                  run_time=0.5)
        self.wait(max(0.2, h - 0.9))

    def draw_A01(self, t):
        pk = self._packet_wave(width=min(1.7, rw(self.R_main) * 0.30))
        pk.move_to([self.gx + rw(self.R_main) * 0.16, self.cy, 0])
        self.packet = pk
        d, h = self._pace(t)
        self.play(Create(pk), run_time=d)
        self.play(pk.animate.shift(RIGHT * (self.bx - pk.get_center()[0] - 0.25)),
                  run_time=max(0.7, h - 0.3), rate_func=linear)

    def draw_A02(self, t):
        eq = MathTex(r"|\psi|^2", color=INK)
        fit(eq, self.R_top, 0.6)
        self.eq = eq
        d, h = self._pace(t)
        self.play(Write(eq), run_time=d)
        self.wait(max(0.2, h))

    def draw_A03(self, t):
        d, h = self._pace(t)
        self.play(self.packet.animate.shift(
            RIGHT * (self.sx - 0.4 - self.packet.get_center()[0])),
            run_time=max(0.8, d * 0.8), rate_func=linear)
        nd = Dot([self.sx - 0.10, self.cy + self.span * 0.18, 0],
                 color=INK, radius=0.05).set_stroke(opacity=0)
        self.add(nd)
        self.play(Flash(nd, color=BLUE, line_length=0.12, num_lines=8,
                        flash_radius=0.2),
                  FadeOut(self.packet), run_time=0.6)
        line = fit_text("wave-shaped possibilities · particle-shaped results",
                        FONT, 26, INK, rw(self.R_top) * 0.94)
        fit(line, self.R_top, 0.9)
        self.play(ReplacementTransform(self.eq, line), run_time=0.7)
        self.defn_line = line
        self.wait(max(0.2, h - 1.3))

    def draw_P01(self, t):
        pk = self._packet_wave(width=1.1, amp=0.2)
        pk.move_to([self.gx + rw(self.R_main) * 0.16, self.cy - self.span * 0.22, 0])
        d, h = self._pace(t)
        self.play(Create(pk), run_time=d * 0.4)
        self.play(pk.animate.move_to([self.sx - 0.5, self.cy - self.span * 0.22, 0]),
                  run_time=max(0.8, d * 0.7), rate_func=linear)
        nd = Dot([self.sx - 0.10, self.cy - self.span * 0.22, 0],
                 color=INK, radius=0.05).set_stroke(opacity=0)
        self.add(nd)
        self.play(Flash(nd, color=BLUE, line_length=0.12, num_lines=8,
                        flash_radius=0.2), FadeOut(pk), run_time=0.5)
        self.play(Indicate(self.defn_line, color=HIGHLIGHT, scale_factor=1.04),
                  run_time=0.6)
        self.wait(max(0.2, h - 1.1))

    def draw_OUTRO(self, t):
        park = fit_text(TITLE, FONT, 28, INK, rw(self.R_top) * 0.94)
        fit(park, self.R_top, 0.9)
        park.set_opacity(0.7)
        self.play(FadeOut(self.defn_line), run_time=0.3)
        self.play(FadeIn(park), run_time=0.5)
        self.wait(max(0.3, t - 0.8))
