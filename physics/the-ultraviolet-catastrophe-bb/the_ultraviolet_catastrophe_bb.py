#!/usr/bin/env python3
"""
the_ultraviolet_catastrophe_bb.py — Brown Blue scene (3b1b template).

Pure Manim. Dark canvas, EB Garamond, blue+brown palette, Bear Brown VO muxed
later by assemble.py (this scene is SILENT). One draw_<BEAT_ID> per beat; timing
comes from mp3/timings.json (real audio).

ORIENTATION-AWARE via bn_layout: nothing is hardcoded in landscape world units.
Every element is placed into a band()-derived rect and scaled with fit/fit_text,
so the SAME file renders 16:9 and 9:16 correctly. The two annotation-bearing
scenes use a MAIN region (the visual) + SIDE region (cards / ratio / ladder);
in landscape SIDE is a right column, in portrait it is a stacked lower band.

Render:
    manim -qh the_ultraviolet_catastrophe_bb.py BearsDoodlesVideo                 # 16:9
    manim -qh -r 1080,1920 the_ultraviolet_catastrophe_bb.py BearsDoodlesVideo    # 9:16
"""
import json
import math
from pathlib import Path

from manim import *  # noqa: F401,F403
import numpy as np
import bn_layout as BL
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
VIOLET    = "#B48AD0"
FONT      = META.get("text_font", "EB Garamond")
TITLE     = META.get("title", "")


def dur(beat_id, fallback=4.0):
    return float(TIMINGS.get(beat_id, fallback))


def txt(s, size=36, color=INK, weight="NORMAL"):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight)


def rj(x):
    return 0.08 * x * x


def planck(x):
    return 3.0 * x * x * math.exp(-0.6 * x)


class BearsDoodlesVideo(Scene):
    def construct(self):
        self.camera.background_color = CANVAS
        port = is_portrait()
        b = band()
        self.R_full = b
        self.port = port
        # PLOT region (the persistent graph) + SIDE region (cards / ladder / ratio).
        # Landscape: side-by-side columns, each inset from the safe area so axis
        # labels and equations keep a real margin and never touch the frame edge.
        # Portrait: stacked rows (graph on top, annotations below).
        if port:
            main, side = rows(b, [0.60, 0.40], gap=0.35)
            self.R_plot = inset(main, 0.12, 0.15)
            self.R_side = inset(side, 0.10, 0.12)
        else:
            main, side = cols(b, [0.62, 0.38], gap=0.5)
            self.R_plot = inset(main, 0.20, 0.25)
            self.R_side = inset(side, 0.15, 0.30)
        # equation sits ABOVE the ladder (never beside it) so it can't run off-frame
        self.R_side_eq, self.R_side_lad = rows(self.R_side, [0.24, 0.76], gap=0.2)

        # persistent plot handles
        self.ax = self.rj_curve = self.pl_curve = self.uv_band = None

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

    def _fit_txt(self, s, rect, size=36, color=INK, frac=0.96):
        g = fit_text(" ".join(s.split()), FONT, size, color, rw(rect) * 0.96)
        return fit(g, rect, frac)

    def _text_card(self, s, t):
        card = self._fit_txt(s, self.R_full, 40)
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

    def _corner_label(self, s, color, rect=None):
        """A small label parked in the top-right corner of a region (default full)."""
        r = rect if rect is not None else self.R_full
        lbl = txt(s, 30, color)
        x = r[2] - lbl.width / 2 - 0.2
        y = r[3] - lbl.height / 2 - 0.15
        return lbl.move_to([x, y, 0])

    # ══════════════════════════ SCENE 1 · HOOK ═══════════════════════════════
    def draw_H01(self, t):
        obj = Circle(radius=1.2, color=BLUE, fill_opacity=0.15, stroke_color=INK)
        fit(obj, self.R_full, 0.34)
        self.obj = obj
        d, h = self._pace(t)
        self.play(GrowFromCenter(obj), run_time=d)
        self.play(obj.animate.set_fill(BLUE, 0.35), run_time=min(1.0, h * 0.5))
        self.wait(max(0.2, h - 1.0))

    def draw_H02(self, t):
        c = self.obj.get_center()
        R = max(rw(self.R_full), rh(self.R_full))
        rays = VGroup(*[
            Line(c, c + R * np.array([math.cos(a), math.sin(a), 0]),
                 color=BLUE, stroke_width=2, stroke_opacity=0.7)
            for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)])
        word = self._corner_label("infinite", HIGHLIGHT)
        d, h = self._pace(t)
        self.play(Create(rays), run_time=d)
        self.play(FadeIn(word), run_time=0.4)
        self.wait(max(0.2, h - 0.8))
        self.play(FadeOut(word), run_time=0.4)
        self.rays = rays

    def draw_H03(self, t):
        room = Square(color=INK, stroke_width=4)
        fit(room, self.R_full, 0.62)
        arrows = VGroup(*[
            Arrow(room.point_from_proportion(p),
                  room.get_center() + 0.6 * (room.get_center() - room.point_from_proportion(p)),
                  color=VIOLET, buff=0, stroke_width=3, max_tip_length_to_length_ratio=0.15)
            for p in np.linspace(0, 1, 12, endpoint=False)])
        self.room, self.arrows = room, arrows
        d, h = self._pace(t)
        # clean 1-to-1 morph (circle → square) + fade the rays; avoid transforming
        # a nested VGroup(circle+16 lines) into one Square (mismatched families).
        self.play(ReplacementTransform(self.obj, room),
                  FadeOut(self.rays), run_time=d)
        self.play(Create(arrows), run_time=min(1.2, h * 0.6))
        self.wait(max(0.2, h - 1.2))

    def draw_H04(self, t):
        q = txt("?", 72, HIGHLIGHT).move_to(self.room.get_center())
        d, h = self._pace(t)
        self.play(FadeOut(self.arrows), run_time=d * 0.6)
        self.play(FadeIn(q, scale=0.6), run_time=0.5)
        self.play(Indicate(q, color=HIGHLIGHT, scale_factor=1.15), run_time=0.6)
        self.wait(max(0.2, h - 1.1))

    # ══════════════════════ SCENE 2 · MODE COUNTING ══════════════════════════
    def _box(self):
        box = Rectangle(width=6.0, height=3.0, color=INK, stroke_width=4)
        return fit(box, self.R_full, 0.86)

    def _mode(self, n, box, amp_frac=0.34):
        w = box.width - 0.2
        x0 = box.get_left()[0] + 0.1
        y0 = box.get_center()[1]
        amp = box.height * amp_frac
        return ParametricFunction(
            lambda s: np.array([x0 + s * w, y0 + amp * math.sin(n * math.pi * s), 0]),
            t_range=[0, 1, 0.01], color=BLUE, stroke_width=3)

    def draw_M01(self, t):
        self.box = self._box()
        self.modes = VGroup(self._mode(1, self.box))
        d, h = self._pace(t)
        self.play(Create(self.box), run_time=d)
        self.play(Create(self.modes[0]), run_time=min(1.4, h * 0.7))
        self.wait(max(0.2, h - 1.4))

    def draw_M02(self, t):
        new = VGroup(self._mode(2, self.box, 0.28), self._mode(3, self.box, 0.24))
        self.modes.add(*new)
        self.count = self._corner_label("3", SECONDARY)
        d, h = self._pace(t)
        self.play(*[Create(m) for m in new], run_time=d)
        self.play(FadeIn(self.count), run_time=0.4)
        self.wait(max(0.2, h - 0.4))

    def draw_M03(self, t):
        crowd = VGroup(*[self._mode(n, self.box, max(0.08, 0.30 - 0.018 * n))
                         for n in range(4, 14)])
        self.modes.add(*crowd)
        new_count = self._corner_label("many", HIGHLIGHT)
        d, h = self._pace(t)
        self.play(LaggedStart(*[Create(m) for m in crowd], lag_ratio=0.08), run_time=d)
        self.play(Transform(self.count, new_count), run_time=0.4)
        self.wait(max(0.2, h - 0.4))

    def draw_M04(self, t):
        tokens = VGroup(*[Dot(m.point_from_proportion(0.5), color=HIGHLIGHT, radius=0.055)
                          for m in self.modes])
        self.tokens = tokens
        d, h = self._pace(t)
        self.play(LaggedStart(*[FadeIn(tk, scale=0.5) for tk in tokens],
                              lag_ratio=0.02), run_time=d)
        self.wait(max(0.2, h))

    def draw_M05(self, t):
        d, h = self._pace(t)
        self.play(Indicate(VGroup(*self.modes[3:], *self.tokens[3:]),
                           color=HIGHLIGHT, scale_factor=1.05), run_time=d)
        self.wait(max(0.2, h))

    # ══════════════════ SCENE 3 · THE PLOT (persistent) ══════════════════════
    def _clear_label(self, x, y, s, color, size=22, maxw=2.6):
        """Place a curve label at DATA point (x,y) — chosen in empty space, not on
        a curve — and clamp its width so it stays inside the plot region."""
        lbl = txt(s, size, color).move_to(self.ax.c2p(x, y))
        if lbl.width > maxw:
            lbl.scale_to_fit_width(maxw)
        # keep inside the plot region horizontally
        if lbl.get_right()[0] > self.R_plot[2]:
            lbl.shift(LEFT * (lbl.get_right()[0] - self.R_plot[2] + 0.05))
        if lbl.get_left()[0] < self.R_plot[0]:
            lbl.shift(RIGHT * (self.R_plot[0] - lbl.get_left()[0] + 0.05))
        return lbl

    def _make_axes(self):
        r = self.R_plot
        # leave room INSIDE r for the rotated y-axis label (left) and x label (below)
        ax = Axes(x_range=[0, 10, 2], y_range=[0, 6, 2],
                  x_length=rw(r) * 0.80, y_length=rh(r) * 0.78,
                  axis_config={"color": SECONDARY, "stroke_width": 2,
                               "include_ticks": True, "include_tip": False})
        ax.move_to([rcx(r) + 0.25, rcy(r) + 0.1, 0])   # nudge right/up to free label room
        xl = txt("frequency", 22, SECONDARY)
        if xl.width > rw(r) * 0.55:
            xl.scale_to_fit_width(rw(r) * 0.55)
        xl.next_to(ax.x_axis, DOWN, buff=0.15)
        yl = txt("brightness", 22, SECONDARY).rotate(PI / 2)
        yl.next_to(ax.y_axis, LEFT, buff=0.12)
        grp = VGroup(ax, xl, yl)
        # hard clamp: if anything pokes past the region, scale the whole group in
        if grp.width > rw(r):
            grp.scale_to_fit_width(rw(r))
        if grp.height > rh(r):
            grp.scale_to_fit_height(rh(r))
        grp.move_to(center(r))
        return grp, ax

    def draw_P01(self, t):
        grp, ax = self._make_axes()
        self.ax, self.axgrp = ax, grp
        self.rj_curve = ax.plot(rj, x_range=[0, 3.0], color=BLUE, stroke_width=5)
        d, h = self._pace(t)
        self.play(Create(grp), run_time=d)
        self.play(Create(self.rj_curve), run_time=min(1.4, h * 0.7))
        self.wait(max(0.2, h - 1.4))

    def draw_P02(self, t):
        full = self.ax.plot(rj, x_range=[0, 8.55], color=BLUE, stroke_width=5)
        x_uv = self.ax.c2p(7, 0)[0]
        x_r = self.ax.c2p(10, 0)[0]
        y_b = self.ax.c2p(0, 0)[1]
        y_t = self.ax.c2p(0, 6)[1]
        self.uv_band = Rectangle(width=x_r - x_uv, height=y_t - y_b,
                                 color=VIOLET, fill_opacity=0.10, stroke_opacity=0)
        self.uv_band.move_to([(x_uv + x_r) / 2, (y_b + y_t) / 2, 0])
        # UV band label: right of where the classical curve exits the top (x>8.66
        # it is off-frame), so this corner of the band is empty.
        uv_lbl = self._clear_label(9.15, 5.25, "ultraviolet", VIOLET, size=20,
                                   maxw=(x_r - x_uv) * 1.5)
        d, h = self._pace(t)
        self.play(FadeIn(self.uv_band), FadeIn(uv_lbl), run_time=0.5)
        self.play(Transform(self.rj_curve, full), run_time=d)
        self.wait(max(0.2, h - 0.5))

    def draw_P03(self, t):
        self.pl_curve = self.ax.plot(planck, x_range=[0, 10], color=BROWN, stroke_width=5)
        d, h = self._pace(t)
        self.play(Create(self.pl_curve), run_time=d + 0.4)
        self.wait(max(0.2, h - 0.4))

        # labels placed in EMPTY space, not on the curves:
        #  classical (blue): both curves are <3.1 near x=6.2, so y=5.5 is clear
        #  reality (brown): above the brown peak (~y4.5 @ x3.3); blue is ~0.9 there
        cl = self._clear_label(6.2, 5.5, "classical", BLUE, maxw=2.4)
        re = self._clear_label(3.3, 5.15, "reality", BROWN, maxw=2.0)
        gap = self.ax.get_area(self.rj_curve, x_range=[3.2, 5.5], color=HIGHLIGHT, opacity=0.12)
        self.labels, self.gap = VGroup(cl, re), gap
        d, h = self._pace(t)
        self.play(FadeIn(cl), FadeIn(re), run_time=d)
        self.play(FadeIn(gap), run_time=0.5)
        self.wait(max(0.2, h - 0.5))

    # ---- side-region annotations (cards / ladder / ratio) --------------------
    def _card(self, s):
        lbl = txt(s, 24, INK)
        rect = SurroundingRectangle(lbl, color=HAIRLINE, buff=0.15)
        return VGroup(rect, lbl)

    def draw_D01(self, t):
        cards = VGroup(self._card("count modes"), self._card("equal share"),
                       self._card("any energy")).arrange(DOWN, buff=0.25)
        fit(cards, self.R_side, 0.9)
        self.cards = cards
        d, h = self._pace(t)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in cards],
                              lag_ratio=0.2), run_time=d)
        self.wait(max(0.2, h))

    def draw_D02(self, t):
        check = txt("✓", 26, SECONDARY).next_to(self.cards[0], LEFT, buff=0.12)
        d, h = self._pace(t)
        self.play(FadeIn(check), self.cards[0].animate.set_opacity(0.4), run_time=d)
        self.wait(max(0.2, h))
        self.check = check

    def draw_D03(self, t):
        rect, lbl = self.cards[2][0], self.cards[2][1]
        d, h = self._pace(t)
        self.play(rect.animate.set_stroke(HIGHLIGHT, width=3),
                  lbl.animate.set_color(HIGHLIGHT), run_time=d)
        self.wait(max(0.2, h))

    def draw_F01(self, t):
        n = 5
        rungs = VGroup(*[Line(LEFT * 0.7, RIGHT * 0.7, color=BLUE, stroke_width=4)
                         for _ in range(n)]).arrange(DOWN, buff=0.35)
        fit(rungs, self.R_side_lad, 0.7)
        self.ladder = rungs
        d, h = self._pace(t)
        self.play(FadeOut(self.cards[0], self.cards[1],
                          getattr(self, "check", VGroup())), run_time=0.4)
        self.play(ReplacementTransform(self.cards[2].copy(), rungs), run_time=d)
        self.play(FadeOut(self.cards[2]), run_time=0.3)
        self.wait(max(0.2, h - 0.7))

    def _ladder_relayout(self, buff):
        c = self.ladder.get_center()
        target = VGroup(*[r.copy() for r in self.ladder]).arrange(DOWN, buff=buff).move_to(c)
        cap = rh(self.R_side_lad) * 0.94
        if target.height > cap:
            target.scale_to_fit_height(cap)
        target.move_to([rcx(self.R_side_lad), rcy(self.R_side_lad), 0])
        return target

    def draw_F02(self, t):
        # equation ABOVE the ladder, in its own row — never beside it
        eq = MathTex(r"E = h\nu", color=INK)
        fit(eq, self.R_side_eq, 0.62)
        brace = Brace(VGroup(self.ladder[0], self.ladder[1]), LEFT, color=SECONDARY)
        d, h = self._pace(t)
        self.play(GrowFromCenter(brace), run_time=d * 0.5)
        self.play(Write(eq), run_time=d * 0.5)
        self.wait(max(0.2, h))
        self.eq, self.brace = eq, brace

    def _rebrace(self, target):
        nb = Brace(VGroup(target[0], target[1]), LEFT, color=SECONDARY)
        return nb

    def draw_F03(self, t):
        target = self._ladder_relayout(0.18)
        nb = self._rebrace(target)
        flash = self.ax.get_area(self.pl_curve, x_range=[0, 2.2], color=BLUE, opacity=0.10)
        d, h = self._pace(t)
        self.play(Transform(self.ladder, target), Transform(self.brace, nb), run_time=d)
        self.play(FadeIn(flash), run_time=0.4)
        self.wait(max(0.2, h - 0.4))
        self.play(FadeOut(flash), run_time=0.3)

    def draw_F04(self, t):
        target = self._ladder_relayout(0.55)
        nb = self._rebrace(target)
        d, h = self._pace(t)
        self.play(Transform(self.ladder, target), Transform(self.brace, nb), run_time=d)
        # price tag to the RIGHT of the top rung, clamped inside the side region
        tag = txt("$$$", 24, HIGHLIGHT).next_to(self.ladder[-1], RIGHT, buff=0.15)
        if tag.get_right()[0] > self.R_side[2]:
            tag.next_to(self.ladder[-1], UP, buff=0.1)
        self.price = tag
        self.play(FadeIn(tag, scale=0.6), run_time=0.4)
        self.wait(max(0.2, h - 0.4))

    def draw_Y01(self, t):
        # a short 'warmth' budget bar to the LEFT of the top rung (stays in-region)
        top = self.ladder[-1].get_left()
        budget = Line(top + DOWN * 0.9, top + DOWN * 0.1, color=BROWN, stroke_width=8)
        blabel = txt("warmth", 20, BROWN).next_to(budget, LEFT, buff=0.12)
        grp = VGroup(budget, blabel)
        if grp.get_left()[0] < self.R_side[0]:
            grp.next_to(self.ladder[-1], DOWN, buff=0.12)
        d, h = self._pace(t)
        self.play(Create(budget), FadeIn(blabel), run_time=d)
        self.play(self.ladder[-1].animate.set_stroke(SECONDARY, opacity=0.35),
                  FadeOut(self.price), run_time=0.5)
        self.wait(max(0.2, h - 0.5))
        self.budget = grp

    def draw_Y02(self, t):
        target = self.ax.plot(planck, x_range=[0, 10], color=BLUE, stroke_width=5)
        d, h = self._pace(t)
        self.play(FadeOut(self.uv_band), run_time=0.3)
        self.play(Transform(self.rj_curve, target), run_time=max(1.4, d + 0.6))
        self.wait(max(0.2, h - 0.3))

    def draw_Y03(self, t):
        d, h = self._pace(t)
        self.play(FadeOut(self.rj_curve), FadeOut(self.gap),
                  FadeOut(self.labels[0]), run_time=d)
        self.wait(max(0.2, h))

    def draw_S01(self, t):
        # ratio in the upper part of the side region; the regime axis (S02) goes below
        self.R_ratio, self.R_regime = rows(self.R_side, [0.62, 0.38], gap=0.2)
        num = txt("chunk cost", 22, BLUE)
        den = txt("warmth", 22, BROWN)
        bar = Line(LEFT, RIGHT, color=INK, stroke_width=2).set_width(max(num.width, den.width) + 0.3)
        ratio = VGroup(num, bar, den).arrange(DOWN, buff=0.14)
        fit(ratio, self.R_ratio, 0.8)
        self.ratio = ratio
        d, h = self._pace(t)
        old = VGroup(*[m for m in (getattr(self, "ladder", None), getattr(self, "eq", None),
                                   getattr(self, "brace", None), getattr(self, "budget", None))
                       if m is not None])
        if len(old):
            self.play(FadeOut(old), run_time=0.4)
        self.play(FadeIn(ratio, shift=UP * 0.1), run_time=d)
        self.wait(max(0.2, h - 0.4))

    def draw_S02(self, t):
        r = self.R_regime
        axis = Line(LEFT, RIGHT, color=SECONDARY, stroke_width=2).set_width(rw(r) * 0.66)
        axis.move_to([rcx(r), rcy(r), 0])
        cl = txt("classical", 16, INK).next_to(axis, LEFT, buff=0.1)
        qu = txt("quantum", 16, INK).next_to(axis, RIGHT, buff=0.1)
        grp = VGroup(axis, cl, qu)
        if grp.width > rw(r):
            grp.scale_to_fit_width(rw(r))
        mark = Triangle(color=HIGHLIGHT, fill_opacity=1).scale(0.10).next_to(axis.get_left(), UP, buff=0.05)
        d, h = self._pace(t)
        self.play(Create(axis), FadeIn(cl), FadeIn(qu), run_time=d)
        self.play(mark.animate.next_to(axis.get_right(), UP, buff=0.05), run_time=min(1.4, h * 0.7))
        self.wait(max(0.2, h - 1.4))

    # ══════════════════════════ SCENE 4 · CLOSE ══════════════════════════════
    def draw_B01(self, t):
        eqrow, ladrow = rows(self.R_full, [0.6, 0.4], gap=0.3)
        eq = MathTex(r"E = h\nu", color=INK)
        fit(eq, eqrow, 0.5)
        ladder = VGroup(*[Line(LEFT * 0.4, RIGHT * 0.4, color=BLUE, stroke_width=3)
                          for _ in range(4)]).arrange(DOWN, buff=0.16)
        fit(ladder, ladrow, 0.5)
        self.close = VGroup(eq, ladder)
        d, h = self._pace(t)
        self.play(Write(eq), run_time=d)
        self.play(Create(ladder), run_time=0.6)
        self.wait(max(0.2, h - 0.6))

    def draw_B02(self, t):
        tags = VGroup(txt("next · Planck's formula", 22, SECONDARY),
                      txt("next · the photon", 22, SECONDARY)).arrange(DOWN, buff=0.2)
        maxw = 2 * safe_w() * 0.9
        if tags.width > maxw:
            tags.scale_to_fit_width(maxw)
        tags.next_to(self.close, DOWN, buff=0.4)
        self.tags = tags
        d, h = self._pace(t)
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in tags], lag_ratio=0.3), run_time=d)
        self.wait(max(0.2, h))

    def draw_B03(self, t):
        ex = fit_text("Try it: estimate hν for green light vs. room-temperature warmth.",
                      FONT, 24, HIGHLIGHT, 2 * safe_w() * 0.86)
        ex.move_to([0, self.R_full[1] + rh(self.R_full) * 0.12, 0])
        d, h = self._pace(t)
        self.play(FadeOut(self.tags), run_time=0.4)
        self.play(self.close.animate.scale(0.72).move_to(
            [0, self.R_full[3] - rh(self.R_full) * 0.18, 0]), run_time=0.5)
        self.play(Write(ex), run_time=d)
        self.wait(max(0.2, h - 0.9))
