#!/usr/bin/env python3
"""
what_wave_particle_duality_means_bb.py — Brown Blue scene (3b1b template).

Pure Manim, silent (assemble.py muxes VO). One draw_<BEAT_ID> per beat; timing
from mp3/timings.json. Arc: the ball-with-ripples cartoon is destroyed by its
own dimensions → two questions get two answers → both classical stories fail →
ONE object (the possibility wave) → the cartoon repaired → sizes → close.

Palette: blue = the wave (the object), brown = the classical foil (ball, heaps),
highlight transient, ink dots for detections. All fill-only shapes silence
their stroke; labels are clamped into regions; the OUTRO title is fitted into
a reserved top band (all lessons from concepts #2–#3 baked in).

Render:
    manim -qh what_wave_particle_duality_means_bb.py BearsDoodlesVideo               # 16:9
    manim -qh -r 1080,1920 what_wave_particle_duality_means_bb.py BearsDoodlesVideo  # 9:16
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
        port = is_portrait()
        b = band()
        self.R_full = b
        self.port = port
        if port:
            main, side = rows(b, [0.62, 0.38], gap=0.35)
            self.R_main = inset(main, 0.12, 0.15)
            self.R_side = inset(side, 0.10, 0.12)
        else:
            main, side = cols(b, [0.64, 0.36], gap=0.5)
            self.R_main = inset(main, 0.20, 0.25)
            self.R_side = inset(side, 0.15, 0.30)
        self.R_side_eq, self.R_side_card = rows(self.R_side, [0.45, 0.55], gap=0.25)

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
                g = fit_text(" ".join(beat.get("narration_text", "").split()),
                             FONT, 40, INK, rw(self.R_full) * 0.96)
                card = fit(g, self.R_full, 0.96)
                d, h = self._pace(dur(bid))
                self.play(Write(card), run_time=d)
                self.wait(h - 0.3)
                self.play(FadeOut(card), run_time=0.3)

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

    @staticmethod
    def _bar(width, height, color, opacity=0.7):
        return Rectangle(width=width, height=height, color=color, fill_color=color,
                         fill_opacity=opacity, stroke_width=0).set_stroke(opacity=0)

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

    def _corner_main(self, s, color, line=0):
        lbl = txt(s, 22, color)
        r = self.R_main
        if lbl.width > rw(r) * 0.46:
            lbl.scale_to_fit_width(rw(r) * 0.46)
        lbl.move_to([r[0] + lbl.width / 2 + 0.05,
                     r[3] - lbl.height / 2 - 0.08 - line * 0.36, 0])
        return lbl

    def _cartoon(self, scale=1.0):
        """The ball-with-ripples cartoon; returns (ball, ripples, group)."""
        ball = Dot(color=BROWN, radius=0.16 * scale).set_stroke(opacity=0)
        ripples = VGroup(*[Circle(radius=r * scale, color=SECONDARY,
                                  stroke_width=2.5, stroke_opacity=0.8)
                           for r in (0.45, 0.75, 1.05)])
        for c in ripples:
            c.move_to(ball.get_center())
        return ball, ripples, VGroup(ball, ripples)

    def _packet_wave(self, width=1.8, amp=0.32, color=BLUE):
        """A gaussian-envelope wiggle — the honest object."""
        k = 5.5 * math.pi / width
        return ParametricFunction(
            lambda s: np.array([(s - 0.5) * width,
                                amp * math.exp(-((s - 0.5) / 0.22) ** 2)
                                * math.sin(k * (s - 0.5) * width), 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)

    # ── compact lab (act 2) ───────────────────────────────────────────────────
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
            lambda s: np.array([self.sx - 0.20 - amp * self.inten(self.ys0 + s * self.span),
                                self.ys0 + s * self.span, 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)

    def _heaps_curve(self, color=BROWN, dashed=True):
        amp = rw(self.R_main) * 0.14
        sig = self.span * 0.10

        def ih(y):
            return (math.exp(-((y - self.s1) / sig) ** 2)
                    + math.exp(-((y - self.s2) / sig) ** 2))
        fn = ParametricFunction(
            lambda s: np.array([self.sx - 0.20 - amp * ih(self.ys0 + s * self.span),
                                self.ys0 + s * self.span, 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)
        return DashedVMobject(fn, num_dashes=40) if dashed else fn

    # ══════════════════ ACT 1 · THE CARTOON (H) ══════════════════════════════
    def draw_H01(self, t):
        self.ball, self.ripples, grp = self._cartoon()
        fit(grp, self.R_main, 0.62)
        self.cartoon = grp
        d, h = self._pace(t)
        self.play(GrowFromCenter(self.ball), run_time=d * 0.5)
        self.play(LaggedStart(*[Create(c) for c in self.ripples], lag_ratio=0.25),
                  run_time=d)
        self.wait(max(0.2, h - 0.5))

    def draw_H02(self, t):
        l1 = txt("the core", 24, BROWN)
        l2 = txt("the coat", 24, SECONDARY)
        stack = VGroup(l1, l2).arrange(DOWN, buff=0.3, aligned_edge=RIGHT)
        stack.move_to([self.R_main[0] + stack.width / 2 + 0.15, rcy(self.R_main), 0])
        self._clamp_into(stack, self.R_main)
        p1 = Line(l1.get_right() + RIGHT * 0.08, self.ball.get_left() + LEFT * 0.05,
                  color=HAIRLINE, stroke_width=2)
        p2 = Line(l2.get_right() + RIGHT * 0.08,
                  self.ripples[1].get_left() + LEFT * 0.02,
                  color=HAIRLINE, stroke_width=2)
        d, h = self._pace(t)
        self.play(Write(l1), Create(p1), run_time=d * 0.6)
        self.play(Write(l2), Create(p2), run_time=d * 0.6)
        self.wait(max(0.2, h - 0.6))
        self.hook_labels = VGroup(l1, l2, p1, p2)

    def draw_H03(self, t):
        brace = Brace(self.ripples, UP, color=BLUE)
        span_lbl = txt("0.167 nm", 24, BLUE).next_to(brace, UP, buff=0.1)
        self._clamp_into(span_lbl, self.R_main)
        tick = Line(DOWN * 0.07, UP * 0.07, color=INK, stroke_width=3)
        tick.next_to(self.ball, DOWN, buff=0.18)
        tick_lbl = txt("÷ 60,000", 22, INK).next_to(tick, DOWN, buff=0.1)
        self._clamp_into(tick_lbl, self.R_main)
        d, h = self._pace(t)
        self.play(GrowFromCenter(brace), Write(span_lbl), run_time=d * 0.7)
        self.play(Create(tick), Write(tick_lbl), run_time=d * 0.6)
        self.wait(max(0.2, h - 0.7))
        self.hook_measure = VGroup(brace, span_lbl, tick, tick_lbl)

    def draw_H04(self, t):
        q = txt("?", 56, HIGHLIGHT)
        q.next_to(self.cartoon, RIGHT, buff=0.4)
        self._clamp_into(q, self.R_main)
        d, h = self._pace(t)
        self.play(self.cartoon.animate.set_opacity(0.4),
                  self.hook_labels.animate.set_opacity(0.3),
                  self.hook_measure.animate.set_opacity(0.4), run_time=d * 0.6)
        self.play(FadeIn(q, scale=0.6), run_time=0.4)
        self.play(Indicate(q, color=HIGHLIGHT, scale_factor=1.15), run_time=0.6)
        self.wait(max(0.2, h - 1.0))

    # ══════════════ ACT 2 · TWO QUESTIONS, ONE OBJECT ════════════════════════
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
        d, h = self._pace(t)
        self.play(Create(gun), Create(barrier), Create(screen), run_time=d + 0.3)
        self.wait(max(0.2, h - 0.3))

    def draw_M02(self, t):
        streaks = VGroup(*[
            Line([self.gx + 0.3, self.cy, 0],
                 [self.sx - 0.25, self.cy + dy, 0],
                 color=BLUE, stroke_width=1.5, stroke_opacity=0.35)
            for dy in np.linspace(-self.span * 0.3, self.span * 0.3, 5)])
        self.stripes = self._fringe_curve(BLUE)
        self.lblQ1 = self._corner_main("how do you travel?  → stripes", BLUE, 0)
        d, h = self._pace(t)
        self.play(LaggedStart(*[Create(s) for s in streaks], lag_ratio=0.1),
                  run_time=d * 0.6)
        self.play(FadeOut(streaks), Create(self.stripes), run_time=d * 0.8)
        self.play(Write(self.lblQ1), run_time=0.5)
        self.wait(max(0.2, h - 1.0))

    def draw_M03(self, t):
        e = Dot([self.gx + 0.15, self.cy, 0], color=BLUE, radius=0.07).set_stroke(opacity=0)
        self.lblQ2 = self._corner_main("where are you?  → one whole dot", INK, 1)
        d, h = self._pace(t)
        self.add(e)
        self.play(e.animate.move_to([self.bx, self.s1, 0]), run_time=d * 0.4, rate_func=linear)
        self.play(e.animate.move_to([self.sx - 0.12, self.cy, 0]), run_time=d * 0.4, rate_func=linear)
        dot = Dot([self.sx - 0.12, self.cy, 0], color=INK, radius=0.05).set_stroke(opacity=0)
        self.remove(e)
        self.add(dot)
        self.the_dot = dot
        self.play(Flash(dot, color=BLUE, line_length=0.12, num_lines=8,
                        flash_radius=0.2), run_time=0.5)
        self.play(Write(self.lblQ2), run_time=0.5)
        self.wait(max(0.2, h - 1.0))

    def draw_S01(self, t):
        self.heaps = self._heaps_curve(BROWN, dashed=True)
        strike = Line([self.sx - 0.9, self.ys0 + 0.1, 0],
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
        half = Sector(outer_radius=0.14, angle=PI, color=INK,
                      fill_opacity=0.9).set_stroke(opacity=0)
        half.move_to([self.sx - 0.55, self.cy - self.span * 0.28, 0])
        strike = Line(half.get_corner(DL) + DL * 0.1, half.get_corner(UR) + UR * 0.1,
                      color=SECONDARY, stroke_width=3)
        d, h = self._pace(t)
        self.play(FadeIn(half, scale=0.6), run_time=d * 0.6)
        self.play(Create(strike), run_time=0.5)
        self.play(VGroup(half, strike).animate.set_opacity(0.2), run_time=0.4)
        self.s2_grp = VGroup(half, strike)
        self.wait(max(0.2, h - 0.9))

    def draw_S03(self, t):
        d, h = self._pace(t)
        self.play(FadeOut(self.s1_grp), FadeOut(self.s2_grp), run_time=d * 0.7)
        self.wait(max(0.3, h))

    def draw_A01(self, t):
        pk = self._packet_wave(width=min(1.9, rw(self.R_main) * 0.30))
        pk.move_to([self.gx + rw(self.R_main) * 0.16, self.cy, 0])
        self.packet = pk
        d, h = self._pace(t)
        self.play(Create(pk), run_time=d)
        self.play(pk.animate.shift(RIGHT * (self.bx - pk.get_center()[0] - 0.3)),
                  run_time=max(0.8, h - 0.3), rate_func=linear)

    def draw_A02(self, t):
        line = fit_text("a map of possibility", FONT, 28, INK,
                        rw(self.R_side_eq) * 0.94)
        eqrow_top, eqrow_bot = rows(self.R_side_eq, [0.5, 0.5], gap=0.15)
        fit(line, eqrow_top, 0.85)
        eq = MathTex(r"|\psi|^2", color=INK)
        fit(eq, eqrow_bot, 0.5)
        self.side_line, self.eq = line, eq
        d, h = self._pace(t)
        self.play(Write(line), run_time=d * 0.7)
        self.play(Write(eq), run_time=d * 0.6)
        self.wait(max(0.2, h - 0.6))

    def draw_A03(self, t):
        d, h = self._pace(t)
        self.play(self.packet.animate.shift(
            RIGHT * (self.sx - 0.45 - self.packet.get_center()[0])),
            run_time=max(0.9, d), rate_func=linear)
        nd = Dot([self.sx - 0.12, self.cy + self.span * 0.18, 0],
                 color=INK, radius=0.05).set_stroke(opacity=0)
        self.add(nd)
        self.play(Flash(nd, color=BLUE, line_length=0.12, num_lines=8,
                        flash_radius=0.2),
                  FadeOut(self.packet), run_time=0.7)
        self.wait(max(0.3, h - 0.7))

    def draw_A04(self, t):
        l1 = fit_text("wave-shaped possibilities", FONT, 27, BLUE,
                      rw(self.R_side_card) * 0.94)
        l2 = fit_text("particle-shaped results", FONT, 27, INK,
                      rw(self.R_side_card) * 0.94)
        card = VGroup(l1, l2).arrange(DOWN, buff=0.22)
        fit(card, self.R_side_card, 0.88)
        self.defn = card
        d, h = self._pace(t)
        self.play(Write(l1), run_time=d * 0.6)
        self.play(Write(l2), run_time=d * 0.6)
        self.wait(max(0.2, h - 0.6))

    def draw_Y01(self, t):
        ball, ripples, grp = self._cartoon(scale=0.55)
        grp.move_to([self.gx + rw(self.R_main) * 0.14,
                     self.R_main[3] - grp.height / 2 - 0.15, 0])
        self._clamp_into(grp, self.R_main)
        # keep clear of the Q labels top-left: nudge below them
        if grp.get_top()[1] > self.R_main[3] - 0.85:
            grp.shift(DOWN * 0.9)
        small_pk = self._packet_wave(width=1.1, amp=0.2)
        small_pk.move_to(grp.get_center())
        d, h = self._pace(t)
        self.play(FadeIn(grp, scale=0.7), run_time=d * 0.5)
        self.play(FadeOut(ball), run_time=0.4)
        self.play(ReplacementTransform(ripples, small_pk), run_time=d * 0.7)
        self.repaired = small_pk
        self.wait(max(0.2, h - 1.1))

    def draw_Y02(self, t):
        d, h = self._pace(t)
        self.play(self.repaired.animate.move_to(
            [self.sx - 0.55, self.cy - self.span * 0.18, 0]),
            run_time=max(1.0, d), rate_func=linear)
        nd = Dot([self.sx - 0.12, self.cy - self.span * 0.18, 0],
                 color=INK, radius=0.05).set_stroke(opacity=0)
        self.add(nd)
        self.play(Flash(nd, color=BLUE, line_length=0.12, num_lines=8,
                        flash_radius=0.2),
                  FadeOut(self.repaired), run_time=0.6)
        self.wait(max(0.3, h - 0.6))

    def draw_N01(self, t):
        d, h = self._pace(t)
        old = VGroup(*[m for m in (getattr(self, "side_line", None),
                                   getattr(self, "eq", None),
                                   getattr(self, "defn", None)) if m is not None])
        if len(old):
            self.play(FadeOut(old), run_time=0.3)
        row1, row2 = rows(self.R_side, [0.55, 0.45], gap=0.25)
        lam = MathTex(r"\lambda = 0.167\ \mathrm{nm}", color=BLUE)
        sub = txt("atom-spacing scale", 24, SECONDARY)
        card = VGroup(lam, sub).arrange(DOWN, buff=0.2)
        fit(card, row1, 0.82)
        self.n_row2 = row2
        self.play(Write(lam), run_time=d * 0.7)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.5)
        self.wait(max(0.2, h - 0.7))

    def draw_N02(self, t):
        line = fit_text("chips & lasers are built on the wave", FONT, 25,
                        SECONDARY, rw(self.n_row2) * 0.94)
        fit(line, self.n_row2, 0.85)
        d, h = self._pace(t)
        self.play(Write(line), run_time=d)
        self.wait(max(0.2, h))

    # ══════════════════════════ ACT 3 · CLOSE ════════════════════════════════
    def draw_B01(self, t):
        eqrow, tagrow = rows(self.R_full, [0.6, 0.4], gap=0.3)
        l1 = fit_text("wave-shaped possibilities", FONT, 34, BLUE, 2 * safe_w() * 0.8)
        l2 = fit_text("particle-shaped results", FONT, 34, INK, 2 * safe_w() * 0.8)
        eq = MathTex(r"|\psi|^2", color=SECONDARY)
        close = VGroup(l1, l2, eq).arrange(DOWN, buff=0.32)
        fit(close, eqrow, 0.72)
        tags = VGroup(txt("next · the wave function", 22, SECONDARY),
                      txt("next · Schrödinger's equation", 22, SECONDARY)).arrange(DOWN, buff=0.2)
        maxw = 2 * safe_w() * 0.9
        if tags.width > maxw:
            tags.scale_to_fit_width(maxw)
        fit(tags, tagrow, 0.6)
        self.close, self.tags = close, tags
        d, h = self._pace(t)
        self.play(Write(l1), run_time=d * 0.45)
        self.play(Write(l2), run_time=d * 0.45)
        self.play(Write(eq), run_time=d * 0.35)
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in tags],
                              lag_ratio=0.3), run_time=min(1.0, h * 0.5))
        self.wait(max(0.2, h - 1.0))

    def draw_B02(self, t):
        ex = fit_text("Try it: find the ball-with-ripples picture in any "
                      "textbook, and say precisely what it gets wrong.",
                      FONT, 24, HIGHLIGHT, 2 * safe_w() * 0.86)
        ex.move_to([0, self.R_full[1] + rh(self.R_full) * 0.16, 0])
        d, h = self._pace(t)
        self.play(FadeOut(self.tags), run_time=0.4)
        self.play(self.close.animate.scale(0.72).move_to(
            [0, self.R_full[3] - rh(self.R_full) * 0.34, 0]), run_time=0.5)
        self.play(Write(ex), run_time=d)
        self.wait(max(0.2, h - 0.9))

    def draw_OUTRO(self, t):
        r = self.R_full
        band_rect = (r[0] + 0.2, r[3] - rh(r) * 0.16, r[2] - 0.2, r[3] - 0.05)
        park = fit_text(TITLE, FONT, 26, INK, (band_rect[2] - band_rect[0]) * 0.94)
        fit(park, band_rect, 0.92)
        park.set_opacity(0.7)
        self.play(FadeIn(park), run_time=0.5)
        self.wait(max(0.3, t - 0.5))
