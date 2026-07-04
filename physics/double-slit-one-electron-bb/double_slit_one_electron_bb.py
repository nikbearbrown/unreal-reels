#!/usr/bin/env python3
"""
double_slit_one_electron_bb.py — Brown Blue scene (3b1b template).

Pure Manim, silent (assemble.py muxes the Bear Brown VO). One draw_<BEAT_ID>
per beat; timing from mp3/timings.json (real audio durations).

The lab (gun → two-slit barrier → screen) persists from H01 through N02 —
dots accumulate in place, curves morph, nothing is redrawn. Dot positions are
sampled from the actual cos²-fringe distribution with a fixed seed, so 10 dots
look random and 285 dots show clean bands: the Tonomura buildup, honestly.

Palette: series roles — blue = the wave/object, brown = the classical foil
(balls, two-heap curve), highlight transient, ink microdots for detector hits.
All fill-only shapes silence their stroke (audit-safe).

ORIENTATION-AWARE via bn_layout; same file renders 16:9 and 9:16.

Render:
    manim -qh double_slit_one_electron_bb.py BearsDoodlesVideo               # 16:9
    manim -qh -r 1080,1920 double_slit_one_electron_bb.py BearsDoodlesVideo  # 9:16
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

BATCHES = (10, 45, 90, 140)          # cumulative 285 shown dots
COUNTS  = ("10", "200", "6,000", "70,000")


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

    @staticmethod
    def _bar(width, height, color, opacity=0.7):
        return Rectangle(width=width, height=height, color=color, fill_color=color,
                         fill_opacity=opacity, stroke_width=0).set_stroke(opacity=0)

    def _microdot(self, y):
        x = self.sx - 0.12 + float(self.rng.uniform(-0.045, 0.045))
        return Dot([x, y, 0], color=INK, radius=0.032).set_stroke(opacity=0)

    # ── lab geometry (persists H01 → N02) ────────────────────────────────────
    def _setup_lab_geometry(self):
        r = self.R_main
        self.gx = r[0] + rw(r) * 0.10
        self.bx = r[0] + rw(r) * 0.46
        self.sx = r[2] - rw(r) * 0.05
        self.cy = rcy(r)
        span = rh(r) * 0.82
        self.ys0, self.ys1 = self.cy - span / 2, self.cy + span / 2
        self.span = span
        self.s1 = self.cy + span * 0.16          # upper slit
        self.s2 = self.cy - span * 0.16          # lower slit
        self.gap = span * 0.055                  # slit half-gap
        self.rng = np.random.default_rng(7)
        # rejection-sample ALL dot ys from the fringe distribution
        wband = span / 5.0
        sig = 0.40 * span

        def inten(y):
            return (math.cos(math.pi * (y - self.cy) / wband) ** 2
                    * math.exp(-((y - self.cy) / sig) ** 2))
        self.inten = inten
        ys = []
        while len(ys) < sum(BATCHES):
            y = float(self.rng.uniform(self.ys0, self.ys1))
            if float(self.rng.uniform(0, 1)) < inten(y):
                ys.append(y)
        self.dot_ys = ys

    def _fringe_curve(self, color=BLUE, amp=None):
        amp = amp if amp is not None else rw(self.R_main) * 0.16
        return ParametricFunction(
            lambda s: np.array([self.sx - 0.22 - amp * self.inten(self.ys0 + s * self.span),
                                self.ys0 + s * self.span, 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)

    def _heaps_curve(self, color=SECONDARY, dashed=False, amp=None):
        amp = amp if amp is not None else rw(self.R_main) * 0.16
        sig = self.span * 0.10

        def ih(y):
            return (math.exp(-((y - self.s1) / sig) ** 2)
                    + math.exp(-((y - self.s2) / sig) ** 2))
        fn = ParametricFunction(
            lambda s: np.array([self.sx - 0.22 - amp * ih(self.ys0 + s * self.span),
                                self.ys0 + s * self.span, 0]),
            t_range=[0, 1, 0.004], color=color, stroke_width=4)
        return DashedVMobject(fn, num_dashes=48) if dashed else fn

    def _arc_fan(self, cyy, color=BLUE, opacity=0.7):
        reach = (self.sx - 0.35) - self.bx
        radii = np.linspace(0.25, max(0.6, reach), 4)
        return VGroup(*[
            Arc(radius=rr, start_angle=-PI / 3, angle=2 * PI / 3, color=color,
                stroke_width=2, stroke_opacity=opacity,
                arc_center=[self.bx, cyy, 0]) for rr in radii])

    def _fly(self, color, slit_y, land_y, tt, radius=0.07):
        """One quantum flies gun → slit → screen and leaves a microdot."""
        e = Dot([self.gx + 0.15, self.cy, 0], color=color, radius=radius)
        e.set_stroke(opacity=0)
        self.add(e)
        self.play(e.animate.move_to([self.bx, slit_y, 0]),
                  run_time=tt * 0.45, rate_func=linear)
        self.play(e.animate.move_to([self.sx - 0.12, land_y, 0]),
                  run_time=tt * 0.45, rate_func=linear)
        d = self._microdot(land_y)
        d.move_to(e.get_center())
        self.remove(e)
        self.add(d)
        self.dots.add(d)
        self.wait(tt * 0.1)

    def _place_counter(self, c):
        """Counter lives bottom-left of the lab, and must end LEFT of the
        barrier — in portrait the full text otherwise runs into the barrier's
        lower segment (Bear's QA catch on concept #3)."""
        maxw = (self.bx - 0.30) - self.R_main[0] - 0.12
        if c.width > maxw:
            c.scale_to_fit_width(maxw)
        c.move_to([self.R_main[0] + c.width / 2 + 0.12,
                   self.R_main[1] + c.height / 2 + 0.08, 0])
        return c

    def _corner_main(self, s, color, line=0):
        """Small label in the top-LEFT of the lab (clear of arcs and screen)."""
        lbl = txt(s, 24, color)
        r = self.R_main
        if lbl.width > rw(r) * 0.4:
            lbl.scale_to_fit_width(rw(r) * 0.4)
        lbl.move_to([r[0] + lbl.width / 2 + 0.05,
                     r[3] - lbl.height / 2 - 0.08 - line * 0.38, 0])
        return lbl

    # ══════════════ ACT 1 · THE LAB (persistent, H01 → N02) ══════════════════
    def draw_H01(self, t):
        r = self.R_main
        gun = RoundedRectangle(corner_radius=0.06, width=0.55, height=0.4,
                               color=INK, stroke_width=4,
                               fill_color=HAIRLINE, fill_opacity=0.35)
        gun.move_to([self.gx, self.cy, 0])
        bw = 5
        barrier = VGroup(
            Line([self.bx, self.ys1, 0], [self.bx, self.s1 + self.gap, 0],
                 color=INK, stroke_width=bw),
            Line([self.bx, self.s1 - self.gap, 0], [self.bx, self.s2 + self.gap, 0],
                 color=INK, stroke_width=bw),
            Line([self.bx, self.s2 - self.gap, 0], [self.bx, self.ys0, 0],
                 color=INK, stroke_width=bw))
        screen = Line([self.sx, self.ys0, 0], [self.sx, self.ys1, 0],
                      color=INK, stroke_width=5)
        self.gun, self.barrier, self.screen = gun, barrier, screen
        self.dots = VGroup()
        d, h = self._pace(t)
        self.play(Create(gun), Create(barrier), Create(screen), run_time=d)
        rest = max(0.8, h - 0.2)
        self._fly(BLUE, self.s1, self.dot_ys[0], rest * 0.5)
        self._fly(BLUE, self.s2, self.dot_ys[1], rest * 0.5)

    def draw_H02(self, t):
        batch = VGroup(*[self._microdot(y) for y in self.dot_ys[2:BATCHES[0]]])
        self.dots.add(*batch)
        self.counter = self._place_counter(txt("electrons: 10", 24, SECONDARY))
        d, h = self._pace(t)
        self.play(LaggedStart(*[FadeIn(m, scale=0.4) for m in batch],
                              lag_ratio=0.12), run_time=d)
        self.play(FadeIn(self.counter), run_time=0.4)
        self.wait(max(0.2, h - 0.4))

    def draw_H03(self, t):
        self.heaps_dashed = self._heaps_curve(SECONDARY, dashed=True)
        d, h = self._pace(t)
        self.play(Create(self.heaps_dashed), run_time=d + 0.4)
        self.wait(max(0.2, h - 0.4))

    def draw_H04(self, t):
        q = txt("?", 56, HIGHLIGHT)
        q.move_to([self.sx - rw(self.R_main) * 0.30, self.cy, 0])
        self.qmark = q
        d, h = self._pace(t)
        self.play(FadeIn(q, scale=0.6),
                  self.heaps_dashed.animate.set_stroke(opacity=0.3), run_time=d * 0.7)
        self.play(Indicate(q, color=HIGHLIGHT, scale_factor=1.15), run_time=0.6)
        self.wait(max(0.2, h - 0.6))

    def draw_W01(self, t):
        self.fanA = self._arc_fan(self.s1)
        self.fanB = self._arc_fan(self.s2)
        d, h = self._pace(t)
        self.play(FadeOut(self.qmark), run_time=0.3)
        self.play(Create(self.fanA), run_time=d * 0.6)
        self.play(Create(self.fanB), run_time=d * 0.6)
        self.wait(max(0.2, h - 0.9))

    def draw_W02(self, t):
        self.stripes = self._fringe_curve(BLUE)
        self.lblW = self._corner_main("waves: stripes", BLUE, line=0)
        d, h = self._pace(t)
        self.play(Create(self.stripes), run_time=d + 0.3)
        self.play(Write(self.lblW), run_time=0.5)
        self.wait(max(0.2, h - 0.8))

    def draw_L01(self, t):
        d, h = self._pace(t)
        self.play(FadeOut(self.fanA), FadeOut(self.fanB),
                  self.stripes.animate.set_stroke(opacity=0.25), run_time=0.4)
        rest = max(0.9, t - 0.5)
        ball1 = Dot([self.gx + 0.15, self.cy, 0], color=BROWN, radius=0.08).set_stroke(opacity=0)
        self.add(ball1)
        self.play(ball1.animate.move_to([self.bx, self.s1, 0]), run_time=rest * 0.22, rate_func=linear)
        self.play(ball1.animate.move_to([self.sx - 0.16, self.s1, 0]), run_time=rest * 0.22, rate_func=linear)
        ball2 = Dot([self.gx + 0.15, self.cy, 0], color=BROWN, radius=0.08).set_stroke(opacity=0)
        self.add(ball2)
        self.play(ball2.animate.move_to([self.bx, self.s2, 0]), run_time=rest * 0.22, rate_func=linear)
        self.play(ball2.animate.move_to([self.sx - 0.16, self.s2, 0]), run_time=rest * 0.22, rate_func=linear)
        self.balls = VGroup(ball1, ball2)

    def draw_L02(self, t):
        solid = self._heaps_curve(BROWN, dashed=False)
        self.lblL = self._corner_main("particles: two heaps", BROWN, line=1)
        d, h = self._pace(t)
        self.play(ReplacementTransform(self.heaps_dashed, solid),
                  FadeOut(self.balls), run_time=d)
        self.heaps = solid
        self.play(Write(self.lblL), run_time=0.5)
        self.wait(max(0.2, h - 0.5))

    def _add_batch(self, k, tt):
        lo = sum(BATCHES[:k])
        hi = sum(BATCHES[:k + 1])
        batch = VGroup(*[self._microdot(y) for y in self.dot_ys[lo:hi]])
        self.dots.add(*batch)
        new_c = self._place_counter(txt(f"electrons: {COUNTS[k]}", 24,
                                        SECONDARY if k < 3 else INK))
        self.play(LaggedStart(*[FadeIn(m, scale=0.4) for m in batch],
                              lag_ratio=min(0.06, 1.2 / len(batch))),
                  Transform(self.counter, new_c), run_time=tt)

    def draw_T01(self, t):
        d, h = self._pace(t)
        self.play(FadeOut(self.stripes), FadeOut(self.heaps),
                  FadeOut(self.lblW), FadeOut(self.lblL), run_time=0.4)
        self._add_batch(1, max(1.0, d))
        self.wait(max(0.2, h - 0.5))

    def draw_T02(self, t):
        d, h = self._pace(t)
        self._add_batch(2, max(1.2, d))
        self.wait(max(0.2, h))

    def draw_T03(self, t):
        d, h = self._pace(t)
        self._add_batch(3, max(1.4, d))
        self.wait(max(0.3, h))

    def draw_T04(self, t):
        self.stripes = self._fringe_curve(BLUE)
        d, h = self._pace(t)
        self.play(Create(self.stripes), run_time=d + 0.4)
        self.wait(max(0.2, h - 0.4))

    def draw_T05(self, t):
        # a dark band sits midway between the center band and the next one
        wband = self.span / 5.0
        ydark = self.cy + wband / 2.0
        strip = self._bar(0.42, wband * 0.5, HIGHLIGHT, 0.30)
        strip.move_to([self.sx - 0.24, ydark, 0])
        d, h = self._pace(t)
        self.play(FadeIn(strip), run_time=d * 0.6)
        self.wait(max(0.4, h - 0.5))
        self.play(FadeOut(strip), run_time=0.4)

    def draw_T06(self, t):
        lbl = txt("one at a time", 22, INK)
        if lbl.width > rw(self.R_main) * 0.32:
            lbl.scale_to_fit_width(rw(self.R_main) * 0.32)
        lbl.next_to(self.gun, UP, buff=0.18)
        if lbl.get_top()[1] > self.R_main[3]:
            lbl.next_to(self.gun, DOWN, buff=0.18)
        # clamp inside the region: centered on the gun it pokes past the left
        # safe edge in portrait (audit: outside safe area)
        if lbl.get_left()[0] < self.R_main[0]:
            lbl.shift(RIGHT * (self.R_main[0] - lbl.get_left()[0] + 0.06))
        self.lbl_one = lbl
        d, h = self._pace(t)
        self.play(Write(lbl), run_time=d * 0.7)
        self.play(Indicate(self.gun, color=BLUE, scale_factor=1.08), run_time=0.6)
        self.wait(max(0.2, h - 0.6))

    # ---- abstraction: side region ---------------------------------------------
    def draw_A01(self, t):
        self.fanA = self._arc_fan(self.s1, BLUE, 0.45)
        self.fanB = self._arc_fan(self.s2, BLUE, 0.45)
        d, h = self._pace(t)
        self.play(FadeIn(self.fanA), FadeIn(self.fanB), run_time=d)
        self.wait(max(0.3, h - 0.5))
        self.play(self.fanA.animate.set_stroke(opacity=0.15),
                  self.fanB.animate.set_stroke(opacity=0.15), run_time=0.5)

    def draw_A02(self, t):
        l1 = fit_text("dot = where it's found", FONT, 26, INK,
                      rw(self.R_side_card) * 0.94)
        l2 = fit_text("stripes = where that's likely", FONT, 26, SECONDARY,
                      rw(self.R_side_card) * 0.94)
        card = VGroup(l1, l2).arrange(DOWN, buff=0.22)
        fit(card, self.R_side_card, 0.9)
        self.side_card = card
        d, h = self._pace(t)
        self.play(Write(l1), run_time=d * 0.6)
        self.play(Write(l2), run_time=d * 0.6)
        self.wait(max(0.2, h - 0.6))

    def draw_A03(self, t):
        eq1 = MathTex(r"|\psi|^2", color=INK)
        eqrow_top, eqrow_bot = rows(self.R_side_eq, [0.5, 0.5], gap=0.15)
        fit(eq1, eqrow_top, 0.55)
        self.eq1 = eq1
        self.eqrow_bot = eqrow_bot
        d, h = self._pace(t)
        self.play(Write(eq1), run_time=d)
        self.wait(max(0.2, h))

    def draw_A04(self, t):
        eq2 = MathTex(r"\lambda = h/p", color=INK)
        fit(eq2, self.eqrow_bot, 0.55)
        self.eq2 = eq2
        d, h = self._pace(t)
        self.play(Write(eq2), run_time=d)
        self.wait(max(0.2, h))

    # ---- payoff ----------------------------------------------------------------
    def draw_Y01(self, t):
        d, h = self._pace(t)
        land = self.cy  # center of the brightest band
        e = Dot([self.gx + 0.15, self.cy, 0], color=BLUE, radius=0.07).set_stroke(opacity=0)
        self.add(e)
        self.play(e.animate.move_to([self.bx, self.s1, 0]),
                  self.fanA.animate.set_stroke(opacity=0.4),
                  self.fanB.animate.set_stroke(opacity=0.4),
                  run_time=d * 0.6, rate_func=linear)
        nd = self._microdot(land)
        self.play(e.animate.move_to(nd.get_center()),
                  self.fanA.animate.set_stroke(opacity=0.15),
                  self.fanB.animate.set_stroke(opacity=0.15),
                  run_time=d * 0.6, rate_func=linear)
        self.remove(e)
        self.add(nd)
        self.dots.add(nd)
        self.play(Flash(nd, color=BLUE, line_length=0.12, num_lines=8,
                        flash_radius=0.2), run_time=0.5)
        self.wait(max(0.2, h - 0.7))

    def draw_Y02(self, t):
        ring = Circle(radius=0.10, color=SECONDARY, stroke_width=3)
        pupil = Dot(radius=0.035, color=SECONDARY).set_stroke(opacity=0)
        pupil.move_to(ring.get_center())
        eye = VGroup(ring, pupil)
        eye.move_to([self.bx - 0.30, self.s1 + 0.02, 0])
        heaps = self._heaps_curve(BROWN, dashed=False)
        d, h = self._pace(t)
        self.play(FadeIn(eye, scale=0.6), run_time=d * 0.4)
        self.play(ReplacementTransform(self.stripes, heaps),
                  self.dots.animate.set_opacity(0.30),
                  self.fanA.animate.set_stroke(opacity=0.0),
                  self.fanB.animate.set_stroke(opacity=0.0),
                  run_time=max(1.0, d * 0.8))
        self.heaps2, self.eye = heaps, eye
        self.wait(max(0.3, h - 0.6))

    def draw_N01(self, t):
        d, h = self._pace(t)
        old = VGroup(*[m for m in (getattr(self, "eq1", None),
                                   getattr(self, "eq2", None),
                                   getattr(self, "side_card", None)) if m is not None])
        if len(old):
            self.play(FadeOut(old), run_time=0.3)
        row1, row2 = rows(self.R_side, [0.5, 0.5], gap=0.25)
        line1 = fit_text("molecules of 2,000 atoms → stripes", FONT, 26, INK,
                         rw(row1) * 0.94)
        fit(line1, row1, 0.85)
        self.n_row2 = row2
        self.play(Write(line1), run_time=d)
        self.wait(max(0.2, h - 0.3))
        self.n_line1 = line1

    def draw_N02(self, t):
        lead = txt("you, walking:", 24, SECONDARY)
        lam = MathTex(r"\lambda \approx 10^{-35}\ \mathrm{m}", color=INK)
        grp = VGroup(lead, lam).arrange(DOWN, buff=0.18)
        fit(grp, self.n_row2, 0.8)
        d, h = self._pace(t)
        self.play(FadeIn(lead, shift=UP * 0.1), run_time=d * 0.5)
        self.play(Write(lam), run_time=d * 0.7)
        self.wait(max(0.2, h - 0.4))

    # ══════════════════════════ ACT 2 · CLOSE ════════════════════════════════
    def draw_B01(self, t):
        eqrow, tagrow = rows(self.R_full, [0.6, 0.4], gap=0.3)
        eq1 = MathTex(r"|\psi|^2", color=INK)
        eq2 = MathTex(r"\lambda = h/p", color=INK)
        eqs = VGroup(eq1, eq2).arrange(DOWN, buff=0.4)
        fit(eqs, eqrow, 0.5)
        tags = VGroup(txt("next · what ψ means", 22, SECONDARY),
                      txt("next · Davisson–Germer", 22, SECONDARY)).arrange(DOWN, buff=0.2)
        maxw = 2 * safe_w() * 0.9
        if tags.width > maxw:
            tags.scale_to_fit_width(maxw)
        fit(tags, tagrow, 0.6)
        self.close, self.tags = eqs, tags
        d, h = self._pace(t)
        self.play(Write(eq1), run_time=d * 0.5)
        self.play(Write(eq2), run_time=d * 0.5)
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in tags],
                              lag_ratio=0.3), run_time=min(1.0, h * 0.5))
        self.wait(max(0.2, h - 1.0))

    def draw_B02(self, t):
        # words as Text, formula as MathTex — fit_text fused the single-letter
        # words (h, m, v) into their neighbors in portrait (Bear's QA catch)
        line1 = fit_text("Try it: compute your own wavelength", FONT, 24,
                         HIGHLIGHT, 2 * safe_w() * 0.86)
        line2 = MathTex(r"\lambda = \frac{h}{m\,v}", color=HIGHLIGHT)
        line3 = fit_text("on your next walk.", FONT, 24, HIGHLIGHT,
                         2 * safe_w() * 0.86)
        ex = VGroup(line1, line2, line3).arrange(DOWN, buff=0.22)
        maxw = 2 * safe_w() * 0.86
        if ex.width > maxw:
            ex.scale_to_fit_width(maxw)
        ex.move_to([0, self.R_full[1] + rh(self.R_full) * 0.20, 0])
        d, h = self._pace(t)
        self.play(FadeOut(self.tags), run_time=0.4)
        # park the close LOW enough that the OUTRO title band stays free
        self.play(self.close.animate.scale(0.72).move_to(
            [0, self.R_full[3] - rh(self.R_full) * 0.34, 0]), run_time=0.5)
        self.play(Write(ex), run_time=d)
        self.wait(max(0.2, h - 0.9))

    def draw_OUTRO(self, t):
        # title lives ONLY in the reserved top band — fitted, never overlapping
        # the parked equations (they sit at 0.34·rh below the top)
        r = self.R_full
        band_rect = (r[0] + 0.2, r[3] - rh(r) * 0.16, r[2] - 0.2, r[3] - 0.05)
        park = fit_text(TITLE, FONT, 26, INK, (band_rect[2] - band_rect[0]) * 0.94)
        fit(park, band_rect, 0.92)
        park.set_opacity(0.7)
        self.play(FadeIn(park), run_time=0.5)
        self.wait(max(0.3, t - 0.5))
