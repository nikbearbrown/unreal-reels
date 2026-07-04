#!/usr/bin/env python3
"""
dim_blue_beats_blinding_red_bb.py — Brown Blue scene (3b1b template).

Pure Manim, silent (assemble.py muxes the Bear Brown VO). One draw_<BEAT_ID>
per beat; timing from mp3/timings.json (real audio durations).

PALETTE (silent-mode decision): the video is about red vs blue light and red is
banned on screen. Low-frequency light renders in warm amber #E07B39 (NOT brown
— brown-for-red was rejected); high-frequency light in palette blue #58C4DD.
Narration says "red"/"blue"; the drawn wavelength (long lazy vs short tight)
carries the physics.

ORIENTATION-AWARE via bn_layout: every element is placed into a band()-derived
rect with fit/fit_text — the same file renders 16:9 and 9:16. Act 2 uses a
MAIN region (the collision lab) + SIDE region (equations / number cards):
side-by-side cols in landscape, stacked rows in portrait.

Render:
    manim -qh dim_blue_beats_blinding_red_bb.py BearsDoodlesVideo               # 16:9
    manim -qh -r 1080,1920 dim_blue_beats_blinding_red_bb.py BearsDoodlesVideo  # 9:16
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
WARM      = META.get("warm_color", "#E07B39")
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
        # Act-2 regions: MAIN = collision lab, SIDE = equations / cards.
        if port:
            main, side = rows(b, [0.58, 0.42], gap=0.35)
            self.R_main = inset(main, 0.12, 0.15)
            self.R_side = inset(side, 0.10, 0.12)
        else:
            main, side = cols(b, [0.60, 0.40], gap=0.5)
            self.R_main = inset(main, 0.20, 0.25)
            self.R_side = inset(side, 0.15, 0.30)
        # equations stack above the card row inside SIDE
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
        r = rect if rect is not None else self.R_full
        lbl = txt(s, 30, color)
        x = r[2] - lbl.width / 2 - 0.2
        y = r[3] - lbl.height / 2 - 0.15
        return lbl.move_to([x, y, 0])

    # ══════════════════ ACT 1 · THE HOOK LAB (plate + lamps) ═════════════════
    def _wave(self, x0, x1, y, lam, color, amp=0.16):
        """A traveling-light squiggle from x0 to x1 at height y, wavelength lam."""
        return ParametricFunction(
            lambda s: np.array([x0 + s * (x1 - x0),
                                y + amp * math.sin(2 * math.pi * (x1 - x0) * s / lam), 0]),
            t_range=[0, 1, 0.01], color=color, stroke_width=3)

    def _hook_geometry(self):
        """Lamp zone (left/top) and plate zone (right/bottom) inside R_full."""
        r = inset(self.R_full, 0.2, 0.25)
        if self.port:
            lampz, platez = rows(r, [0.45, 0.55], gap=0.4)
        else:
            lampz, platez = cols(r, [0.48, 0.52], gap=0.6)
        return r, lampz, platez

    def _make_plate(self, platez):
        plate = RoundedRectangle(corner_radius=0.08, width=1.1, height=2.6,
                                 color=INK, stroke_width=4,
                                 fill_color=HAIRLINE, fill_opacity=0.35)
        fit(plate, platez, 0.9 if self.port else 0.8)
        if not self.port:
            # tall slab hugging the right of its zone
            plate.stretch_to_fit_width(min(plate.width, rw(platez) * 0.28))
            plate.move_to([platez[2] - plate.width / 2, rcy(platez), 0])
        n = 5
        ys = np.linspace(plate.get_bottom()[1] + 0.25, plate.get_top()[1] - 0.25, n)
        xface = plate.get_left()[0] + 0.12
        electrons = VGroup(*[Dot([xface, y, 0], color=BLUE, radius=0.07) for y in ys])
        return plate, electrons

    def _make_lamp(self, lampz, color, radius_frac=0.16):
        lamp = Circle(radius=1.0, color=color, fill_color=color,
                      fill_opacity=0.28, stroke_width=4)
        lamp.scale_to_fit_width(min(rw(lampz), rh(lampz)) * radius_frac * 2)
        lamp.move_to([rcx(lampz) - rw(lampz) * 0.25, rcy(lampz), 0] if not self.port
                     else [rcx(lampz), rcy(lampz) + rh(lampz) * 0.15, 0])
        return lamp

    def _waves_between(self, lamp, plate, lam, color, k=3):
        x0 = lamp.get_right()[0] + 0.15
        x1 = plate.get_left()[0] - 0.15
        if self.port:
            # light travels downward in portrait: rotate the idea — keep horizontal
            # waves but from lamp bottom to plate top via a mid column
            x0 = min(x0, x1 - 1.0)
        yc = lamp.get_center()[1]
        offs = np.linspace(-0.5, 0.5, k)
        return VGroup(*[self._wave(x0, x1, yc + o, lam, color) for o in offs])

    def draw_H01(self, t):
        r, lampz, platez = self._hook_geometry()
        self.plate, self.electrons = self._make_plate(platez)
        self.lamp = self._make_lamp(lampz, WARM)
        self.waves = self._waves_between(self.lamp, self.plate, lam=1.6, color=WARM)
        self.lamp_lbl = txt("red", 26, SECONDARY).next_to(self.lamp, DOWN, buff=0.15)
        if self.lamp_lbl.get_bottom()[1] < self.R_full[1]:
            self.lamp_lbl.next_to(self.lamp, UP, buff=0.15)
        d, h = self._pace(t)
        self.play(Create(self.plate), FadeIn(self.electrons), run_time=d * 0.5)
        self.play(GrowFromCenter(self.lamp), FadeIn(self.lamp_lbl), run_time=d * 0.5)
        self.play(Create(self.waves), run_time=min(1.2, h * 0.6))
        self.wait(max(0.2, h - 1.2))

    def draw_H02(self, t):
        blue_lamp = self._make_lamp(self._hook_geometry()[1], BLUE, radius_frac=0.11)
        blue_lamp.move_to(self.lamp.get_center())
        new_waves = self._waves_between(blue_lamp, self.plate, lam=0.55, color=BLUE)
        new_lbl = txt("blue", 26, SECONDARY).move_to(self.lamp_lbl.get_center())
        d, h = self._pace(t)
        self.play(ReplacementTransform(self.lamp, blue_lamp),
                  ReplacementTransform(self.waves, new_waves),
                  ReplacementTransform(self.lamp_lbl, new_lbl), run_time=d)
        self.lamp, self.waves, self.lamp_lbl = blue_lamp, new_waves, new_lbl
        # two electrons fly off instantly
        flyers = VGroup(self.electrons[1], self.electrons[3])
        arcs = [e.copy().shift(RIGHT * 1.1 + UP * (0.5 if i == 0 else -0.4))
                for i, e in enumerate(flyers)]
        self.play(*[e.animate.move_to(a.get_center()).set_opacity(0.25)
                    for e, a in zip(flyers, arcs)], run_time=min(1.0, h * 0.6))
        self.wait(max(0.2, h - 1.0))

    def draw_H03(self, t):
        warm_lamp = self._make_lamp(self._hook_geometry()[1], WARM, radius_frac=0.22)
        warm_lamp.move_to(self.lamp.get_center())
        new_waves = self._waves_between(warm_lamp, self.plate, lam=1.6, color=WARM, k=7)
        # place the label relative to the NEW, larger lamp (the old position sat
        # on the bigger circle's stroke — TEXT_ON_CURVE audit error)
        new_lbl = txt("red", 26, SECONDARY).next_to(warm_lamp, DOWN, buff=0.25)
        if new_lbl.get_bottom()[1] < self.R_full[1]:
            new_lbl.next_to(warm_lamp, UP, buff=0.25)
        # restore the two flown electrons (fresh red run: plate is full again)
        d, h = self._pace(t)
        self.play(ReplacementTransform(self.lamp, warm_lamp),
                  ReplacementTransform(self.waves, new_waves),
                  ReplacementTransform(self.lamp_lbl, new_lbl),
                  self.electrons[1].animate.set_opacity(1).move_to(
                      self.electrons[0].get_center() + UP * 0.55),
                  self.electrons[3].animate.set_opacity(1).move_to(
                      self.electrons[4].get_center() + DOWN * 0.55),
                  run_time=d)
        self.lamp, self.waves, self.lamp_lbl = warm_lamp, new_waves, new_lbl
        self.x100 = self._corner_label("×100", INK)
        self.play(FadeIn(self.x100, scale=0.7), run_time=0.4)
        self.wait(max(0.2, h - 0.4))

    def draw_H04(self, t):
        q = txt("?", 64, HIGHLIGHT).next_to(self.plate, RIGHT, buff=0.3)
        if q.get_right()[0] > self.R_full[2]:
            q.next_to(self.plate, UP, buff=0.2)
        self.qmark = q
        d, h = self._pace(t)
        self.play(FadeIn(q, scale=0.6), self.x100.animate.set_opacity(0.4), run_time=d * 0.7)
        self.play(Indicate(q, color=HIGHLIGHT, scale_factor=1.15), run_time=0.6)
        self.wait(max(0.2, h - 0.6))

    def draw_W01(self, t):
        # waves soften into broad ripples washing the whole plate
        c = self.lamp.get_center()
        radii = np.linspace(0.6, 3.4, 5)
        ripples = VGroup(*[
            Arc(radius=rr, start_angle=-PI / 3, angle=2 * PI / 3, color=WARM,
                stroke_width=2, stroke_opacity=0.7, arc_center=c) for rr in radii])
        bars = VGroup(*[
            Line(e.get_center() + RIGHT * 0.16 + DOWN * 0.12,
                 e.get_center() + RIGHT * 0.16 + UP * 0.02,
                 color=SECONDARY, stroke_width=5) for e in self.electrons])
        for bb in bars:
            bb.save_state()
            bb.stretch(0.15, 1, about_point=bb.get_bottom())
        self.bars = bars
        d, h = self._pace(t)
        self.play(ReplacementTransform(self.waves, ripples),
                  FadeOut(self.qmark), FadeOut(self.x100), run_time=d)
        self.waves = ripples
        self.play(FadeIn(bars), run_time=0.3)
        self.play(*[bb.animate.restore() for bb in bars],
                  run_time=max(0.8, h - 0.5), rate_func=linear)
        self.wait(0.2)

    def draw_W02(self, t):
        r = self._hook_geometry()[0]
        strike = Line([r[0], r[1] + rh(r) * 0.2, 0], [r[2], r[3] - rh(r) * 0.2, 0],
                      color=SECONDARY, stroke_width=3)
        never = self._corner_label("never", SECONDARY)
        d, h = self._pace(t)
        self.play(Create(strike), run_time=d * 0.7)
        self.play(FadeIn(never), run_time=0.4)
        self.wait(max(0.2, h - 0.8))
        self.play(FadeOut(never), run_time=0.3)

    # ══════════ ACT 2 · PACKETS, THE WELL, THE COLLISIONS (MAIN+SIDE) ═════════
    def _packet(self, color, size=0.13):
        # stroke opacity 0: fill-only shapes must not register as "curves" in
        # the layout audit (zero-WIDTH strokes still have opacity 1 by default)
        return Dot(color=color, radius=size).set_fill(color, 0.9).set_stroke(opacity=0)

    @staticmethod
    def _bar(width, height, color, opacity=0.7):
        """Fill-only bar with its phantom stroke silenced (audit-safe)."""
        return Rectangle(width=width, height=height, color=color, fill_color=color,
                         fill_opacity=opacity, stroke_width=0).set_stroke(opacity=0)

    def draw_K01(self, t):
        r = self.R_main
        y = rcy(r)
        smooth = ParametricFunction(
            lambda s: np.array([r[0] + s * rw(r), y + 0.35 * math.sin(6 * math.pi * s), 0]),
            t_range=[0, 1, 0.01], color=INK, stroke_width=3)
        n = 9
        xs = np.linspace(r[0] + 0.2, r[2] - 0.2, n)
        stream = VGroup(*[self._packet(INK) for _ in range(n)])
        for p, x in zip(stream, xs):
            p.move_to([x, y, 0])
        d, h = self._pace(t)
        self.play(Create(smooth), run_time=d * 0.6)
        self.play(ReplacementTransform(smooth, stream), run_time=d * 0.6)
        self.play(stream.animate.shift(RIGHT * 0.4), run_time=max(0.6, h - 0.4),
                  rate_func=linear)
        self.stream = stream

    def draw_K02(self, t):
        r = self.R_main
        colw = rw(r) / 2
        wx, bx = r[0] + colw * 0.5, r[0] + colw * 1.5
        base_y = r[1] + rh(r) * 0.22
        warm_p = self._packet(WARM, 0.15).move_to([wx, r[3] - 0.5, 0])
        blue_p = self._packet(BLUE, 0.19).move_to([bx, r[3] - 0.5, 0])
        wbar = self._bar(0.4, rh(r) * 0.22, WARM)
        bbar = self._bar(0.4, rh(r) * 0.50, BLUE)
        wbar.move_to([wx, base_y + wbar.height / 2, 0])
        bbar.move_to([bx, base_y + bbar.height / 2, 0])
        wlbl = txt("red · weak", 22, SECONDARY)
        blbl = txt("blue · strong", 22, SECONDARY)
        for lbl, bar, x in ((wlbl, wbar, wx), (blbl, bbar, bx)):
            if lbl.width > colw * 0.9:
                lbl.scale_to_fit_width(colw * 0.9)
            lbl.next_to(bar, DOWN, buff=0.22)   # tied to its bar, clear of everything
            if lbl.get_bottom()[1] < r[1]:
                lbl.shift(UP * (r[1] - lbl.get_bottom()[1] + 0.05))
        d, h = self._pace(t)
        self.play(FadeOut(self.stream), run_time=0.3)
        self.play(FadeIn(warm_p), FadeIn(blue_p), run_time=0.4)
        self.play(GrowFromEdge(wbar, DOWN), GrowFromEdge(bbar, DOWN),
                  Write(wlbl), Write(blbl), run_time=d)
        self.wait(max(0.2, h - 0.7))
        self.k_group = VGroup(warm_p, blue_p, wbar, bbar, wlbl, blbl)
        self.wbar, self.warm_p = wbar, warm_p

    def draw_K03(self, t):
        # densify the warm stream; the warm bar is unchanged
        wx = self.warm_p.get_center()[0]
        top = self.R_main[3] - 0.3
        minis = VGroup(*[self._packet(WARM, 0.09).move_to(
            [wx + dx, top - i * 0.28, 0])
            for i, dx in enumerate(np.tile([-0.3, 0.0, 0.3], 3)[:8])])
        d, h = self._pace(t)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in minis],
                              lag_ratio=0.06), run_time=d)
        self.play(Indicate(self.wbar, color=HIGHLIGHT, scale_factor=1.06), run_time=0.7)
        self.wait(max(0.2, h - 0.7))
        self.minis = minis

    def _make_well(self):
        """U-shaped well in R_main with a rim hairline = the escape cost."""
        r = self.R_main
        w = rw(r) * 0.46
        hgt = rh(r) * 0.55
        cx = rcx(r)
        y0 = r[1] + rh(r) * 0.12
        left = Line([cx - w / 2, y0 + hgt, 0], [cx - w / 2, y0, 0], color=INK, stroke_width=4)
        bottom = Line([cx - w / 2, y0, 0], [cx + w / 2, y0, 0], color=INK, stroke_width=4)
        right = Line([cx + w / 2, y0, 0], [cx + w / 2, y0 + hgt, 0], color=INK, stroke_width=4)
        well = VGroup(left, bottom, right)
        rim = DashedLine([cx - w / 2 - 0.25, y0 + hgt, 0], [cx + w / 2 + 0.25, y0 + hgt, 0],
                         color=HAIRLINE, stroke_width=3)
        lbl = txt("escape cost", 22, SECONDARY)
        if lbl.width > rw(r) * 0.4:
            lbl.scale_to_fit_width(rw(r) * 0.4)
        lbl.next_to(rim, UP, buff=0.1).shift(LEFT * (w * 0.25))
        if lbl.get_left()[0] < r[0]:
            lbl.shift(RIGHT * (r[0] - lbl.get_left()[0] + 0.05))
        return well, rim, lbl, (cx, y0, hgt, w)

    def draw_C01(self, t):
        d, h = self._pace(t)
        # park the comparison small in the side card row (it becomes reference)
        parked = self.k_group.copy()
        cap_w, cap_h = rw(self.R_side_card) * 0.8, rh(self.R_side_card) * 0.8
        parked.scale_to_fit_width(cap_w)
        if parked.height > cap_h:
            parked.scale_to_fit_height(cap_h)
        parked.move_to(center(self.R_side_card)).set_opacity(0.45)
        self.parked = parked
        # fade, don't morph: a cross-screen ReplacementTransform drags the labels
        # through the middle of the frame and trips the audit mid-flight
        self.play(FadeOut(self.minis), FadeOut(self.k_group),
                  FadeIn(parked), run_time=d * 0.6)
        self.well, self.rim, self.rim_lbl, self.wellgeo = self._make_well()
        cx, y0, hgt, w = self.wellgeo
        self.e_dot = Dot([cx, y0 + 0.16, 0], color=BLUE, radius=0.09)
        self.play(Create(self.well), run_time=d * 0.6)
        self.play(FadeIn(self.e_dot, scale=0.5),
                  Create(self.rim), Write(self.rim_lbl), run_time=min(1.0, h * 0.5))
        self.wait(max(0.2, h - 1.0))

    def draw_C02(self, t):
        cx, y0, hgt, w = self.wellgeo
        pk = self._packet(BLUE, 0.12).move_to([cx - w, y0 + hgt + 0.4, 0])
        d, h = self._pace(t)
        self.play(pk.animate.move_to(self.e_dot.get_center()), run_time=d * 0.8)
        self.play(FadeOut(pk, scale=0.3),
                  Flash(self.e_dot, color=BLUE, line_length=0.15,
                        num_lines=8, flash_radius=0.25), run_time=0.5)
        # the natural wrong picture: one packet split as sips among many — struck out
        ghost = VGroup(*[Dot(color=SECONDARY, radius=0.05) for _ in range(4)])
        ghost.arrange(RIGHT, buff=0.18).move_to([cx, y0 + hgt + 0.45, 0])
        gs = Line(ghost.get_corner(DL) + DL * 0.08, ghost.get_corner(UR) + UR * 0.08,
                  color=SECONDARY, stroke_width=3)
        wrong = VGroup(ghost, gs)
        self.play(FadeIn(wrong), run_time=0.4)
        self.wait(max(0.2, h - 1.3))
        self.play(FadeOut(wrong), run_time=0.4)

    def _hop(self, frac, color, tt, escape=False):
        """One packet in; the electron rises to frac of rim height (or escapes)."""
        cx, y0, hgt, w = self.wellgeo
        pk = self._packet(color, 0.12 if color == WARM else 0.15)
        pk.move_to([cx - w, y0 + hgt + 0.4, 0])
        rise = y0 + 0.16 + (hgt - 0.16) * frac
        anims_in = [pk.animate.move_to(self.e_dot.get_center())]
        self.play(*anims_in, run_time=tt * 0.35)
        self.remove(pk)
        if escape:
            out = [cx + w * 0.9, y0 + hgt + 0.7, 0]
            self.play(self.e_dot.animate.move_to([cx, y0 + hgt + 0.12, 0]),
                      run_time=tt * 0.3, rate_func=rush_from)
            self.play(self.e_dot.animate.move_to(out), run_time=tt * 0.35)
        else:
            self.play(self.e_dot.animate.move_to([cx, rise, 0]),
                      run_time=tt * 0.3, rate_func=rush_into)
            shimmer = VGroup(*[Line(ORIGIN, UP * 0.12, color=WARM, stroke_width=2,
                                    stroke_opacity=0.6).move_to(
                [cx + dx, rise + 0.25, 0]) for dx in (-0.15, 0.0, 0.15)])
            self.play(self.e_dot.animate.move_to([cx, y0 + 0.16, 0]),
                      FadeIn(shimmer, shift=UP * 0.2), run_time=tt * 0.25)
            self.play(FadeOut(shimmer), run_time=tt * 0.1)

    def draw_X01(self, t):
        self._hop(0.6, WARM, t * 0.85)
        self.wait(max(0.15, t * 0.15))

    def draw_X02(self, t):
        cx, y0, hgt, w = self.wellgeo
        # bottom-LEFT of the lab: clear of the rain (top-left), the escape arc
        # and the speed arrow (both top-right)
        self.counter = txt("freed: 0", 24, SECONDARY)
        self.counter.move_to([self.R_main[0] + self.counter.width / 2 + 0.12,
                              self.R_main[1] + self.counter.height / 2 + 0.10, 0])
        rain = VGroup(*[self._packet(WARM, 0.08).move_to(
            [cx - w + 0.3 * i, y0 + hgt + 0.5 + 0.15 * (i % 3), 0]) for i in range(6)])
        d, h = self._pace(t)
        self.play(FadeIn(self.counter), FadeIn(rain, lag_ratio=0.1), run_time=d * 0.5)
        self.play(rain.animate.move_to([cx, y0 + hgt * 0.5, 0]).set_opacity(0),
                  self.e_dot.animate.move_to([cx, y0 + 0.16 + (hgt - 0.16) * 0.6, 0]),
                  run_time=d * 0.5, rate_func=rush_into)
        self.play(self.e_dot.animate.move_to([cx, y0 + 0.16, 0]), run_time=0.4)
        self.remove(rain)
        self.play(Indicate(self.counter, color=SECONDARY, scale_factor=1.05), run_time=0.5)
        self.wait(max(0.2, h - 0.9))

    def draw_X03(self, t):
        self._hop(1.0, BLUE, t * 0.7, escape=True)
        new_c = txt("freed: 1", 24, INK).move_to(self.counter.get_center())
        self.play(Transform(self.counter, new_c), run_time=0.4)
        self.wait(max(0.15, t * 0.3 - 0.4))

    def draw_X04(self, t):
        cx, y0, hgt, w = self.wellgeo
        # energy bar beside the well, split at the rim height
        bx = cx + w * 0.85
        paid = self._bar(0.3, hgt - 0.16, BLUE, 0.35)
        paid.move_to([bx, y0 + 0.16 + paid.height / 2, 0])
        left_over = self._bar(0.3, 0.5, HIGHLIGHT, 0.85)
        left_over.move_to([bx, y0 + hgt + left_over.height / 2, 0])
        arrow = Arrow(self.e_dot.get_center(),
                      self.e_dot.get_center() + RIGHT * 0.9, color=HIGHLIGHT,
                      buff=0.12, stroke_width=5, max_tip_length_to_length_ratio=0.25)
        d, h = self._pace(t)
        self.play(GrowFromEdge(paid, DOWN), run_time=d * 0.5)
        self.play(GrowFromEdge(left_over, DOWN), run_time=d * 0.5)
        self.play(paid.animate.set_opacity(0.15),
                  ReplacementTransform(left_over, arrow), run_time=min(1.0, h * 0.6))
        self.wait(max(0.2, h - 1.0))
        self.speed_arrow, self.paid_bar = arrow, paid

    # ---- abstractions in the SIDE region -------------------------------------
    def draw_A01(self, t):
        self.play(FadeOut(self.parked), run_time=0.3)
        eqrow, namerow = rows(self.R_side_eq, [0.62, 0.38], gap=0.15)
        eq1 = MathTex(r"E = h\nu", color=INK)
        fit(eq1, eqrow, 0.6)
        name = txt("photon", 26, INK)
        fit(name, namerow, 0.5)
        d, h = self._pace(t)
        self.play(Write(eq1), run_time=d)
        self.play(FadeIn(name, shift=UP * 0.1), run_time=0.5)
        self.wait(max(0.2, h - 0.8))
        self.eq1, self.photon_name = eq1, name

    def draw_A02(self, t):
        eq2 = MathTex(r"K = h\nu - \Phi", color=INK)
        cap = rw(self.R_side_card) * 0.8
        if eq2.width > cap:
            eq2.scale_to_fit_width(cap)
        eq2.move_to([rcx(self.R_side_card),
                     self.R_side_card[3] - eq2.height / 2 - 0.1, 0])
        d, h = self._pace(t)
        self.play(FadeOut(self.photon_name), run_time=0.3)
        self.play(Write(eq2), run_time=d)
        # transient: tie Φ to the rim hairline
        u1 = Line(eq2.get_corner(DR) + LEFT * 0.25 + DOWN * 0.08,
                  eq2.get_corner(DR) + DOWN * 0.08, color=HIGHLIGHT, stroke_width=3)
        u2 = self.rim.copy().set_color(HIGHLIGHT)
        self.play(Create(u1), Create(u2), run_time=0.5)
        self.wait(max(0.2, h - 1.0))
        self.play(FadeOut(u1), FadeOut(u2), run_time=0.4)
        self.eq2 = eq2

    def draw_A03(self, t):
        r = self.R_side_card
        axis_y = r[1] + rh(r) * 0.3
        x0, x1 = r[0] + 0.2, r[2] - 0.2
        axis = Line([x0, axis_y, 0], [x1, axis_y, 0], color=SECONDARY, stroke_width=2)
        xm = x0 + (x1 - x0) * 0.55
        tickm = Line([xm, axis_y - 0.08, 0], [xm, axis_y + 0.08, 0], color=INK, stroke_width=3)
        nu0 = MathTex(r"\nu_0", color=INK).scale(0.7).next_to(tickm, DOWN, buff=0.1)
        warm_seg = Line([x0, axis_y, 0], [xm, axis_y, 0], color=WARM,
                        stroke_width=6, stroke_opacity=0.8)
        blue_seg = Line([xm, axis_y, 0], [x1, axis_y, 0], color=BLUE,
                        stroke_width=6, stroke_opacity=0.8)
        d, h = self._pace(t)
        self.play(Create(axis), Create(warm_seg), Create(blue_seg), run_time=d * 0.7)
        self.play(Create(tickm), Write(nu0), run_time=d * 0.4)
        self.play(warm_seg.animate.set_stroke(opacity=0.25), run_time=0.5)
        self.wait(max(0.2, h - 0.5))
        self.thresh = VGroup(axis, tickm, nu0, warm_seg, blue_seg)

    # ---- payoff: the lamps return --------------------------------------------
    def draw_P01(self, t):
        r = self.R_main
        top = r[3] - 0.35
        warm_lamp = Circle(radius=0.28, color=WARM, fill_color=WARM,
                           fill_opacity=0.3, stroke_width=3).move_to(
            [rcx(r) - rw(r) * 0.25, top, 0])
        blue_lamp = Circle(radius=0.16, color=BLUE, fill_color=BLUE,
                           fill_opacity=0.3, stroke_width=3).move_to(
            [rcx(r) + rw(r) * 0.25, top, 0])
        q = txt("?", 40, HIGHLIGHT).move_to([rcx(r), top, 0])
        d, h = self._pace(t)
        # the rim label served its purpose (Φ is named); in portrait the lamps
        # would sit right on top of it
        self.play(FadeOut(self.rim_lbl),
                  FadeIn(warm_lamp), FadeIn(blue_lamp), run_time=d * 0.7)
        self.play(FadeIn(q, scale=0.6), run_time=0.3)
        self.play(FadeOut(q, scale=0.4), run_time=0.5)
        self.wait(max(0.2, h - 0.8))
        self.warm_lamp, self.blue_lamp = warm_lamp, blue_lamp

    def draw_P02(self, t):
        cx, y0, hgt, w = self.wellgeo
        torrent = VGroup(*[self._packet(WARM, 0.07).move_to(
            self.warm_lamp.get_center() + DOWN * (0.35 + 0.22 * i) +
            RIGHT * (0.12 * ((i % 3) - 1))) for i in range(7)])
        trickle = VGroup(*[self._packet(BLUE, 0.12).move_to(
            self.blue_lamp.get_center() + DOWN * (0.5 + 0.9 * i)) for i in range(2)])
        d, h = self._pace(t)
        self.play(FadeIn(torrent, lag_ratio=0.05), FadeIn(trickle), run_time=d * 0.5)
        # torrent dies below the rim; trickle frees a second electron
        e2 = Dot(self.e_dot.get_center(), color=BLUE, radius=0.09) \
            if self.e_dot.get_center()[1] > y0 + hgt else self.e_dot
        free = Dot([cx, y0 + 0.16, 0], color=BLUE, radius=0.09)
        self.add(free)
        self.play(torrent.animate.shift(DOWN * 0.9).set_opacity(0.0),
                  trickle.animate.shift(DOWN * 1.2).set_opacity(0.0),
                  free.animate.move_to([cx - w * 0.7, y0 + hgt + 0.6, 0]),
                  run_time=max(1.0, d))
        self.wait(max(0.3, h - 0.5))

    # ---- the number, on the sodium card ---------------------------------------
    def draw_N01(self, t):
        d, h = self._pace(t)
        # the equations and threshold axis had their moment — clear the WHOLE
        # side column so the sodium card gets real room (the cramped card row
        # caused text-on-text collisions in portrait)
        old = VGroup(*[m for m in (getattr(self, "thresh", None),
                                   getattr(self, "eq1", None),
                                   getattr(self, "eq2", None)) if m is not None])
        if len(old):
            self.play(FadeOut(old), run_time=0.3)
        r = self.R_side
        headrow, barrow = rows(r, [0.20, 0.80], gap=0.20)
        head = txt("sodium · 300 nm", 24, INK)
        fit(head, headrow, 0.85)
        bar_h = rh(barrow) * 0.72
        base = barrow[1] + 0.10
        bar_x = rcx(r) - rw(r) * 0.22
        full = self._bar(0.5, bar_h, BLUE, 0.6)
        full.move_to([bar_x, base + bar_h / 2, 0])
        cost_y = base + bar_h * (2.28 / 4.13)
        cost = DashedLine([full.get_left()[0] - 0.25, cost_y, 0],
                          [min(full.get_right()[0] + 1.1, r[2] - 0.1), cost_y, 0],
                          color=HAIRLINE, stroke_width=3)
        # values live in the empty right half of the column, vertically separated:
        # the photon energy up at the bar top, the cost just under its own line
        v1 = txt("4.13 eV", 20, BLUE)
        v1.move_to([bar_x + 0.25 + 0.2 + v1.width / 2, base + bar_h - v1.height / 2, 0])
        v2 = txt("2.28 eV", 20, SECONDARY)
        v2.move_to([v1.get_center()[0], cost_y - 0.18 - v2.height / 2, 0])
        for mo in (v1, v2):
            if mo.get_right()[0] > r[2]:
                mo.shift(LEFT * (mo.get_right()[0] - r[2] + 0.05))
        self.play(FadeIn(head), run_time=0.4)
        self.play(GrowFromEdge(full, DOWN), Create(cost), run_time=d)
        self.play(FadeIn(v1), FadeIn(v2), run_time=0.4)
        surplus = self._bar(0.5, bar_h - bar_h * (2.28 / 4.13), HIGHLIGHT, 0.5)
        surplus.move_to([full.get_center()[0], cost_y + surplus.height / 2, 0])
        self.play(FadeIn(surplus), run_time=0.4)
        self.play(FadeOut(surplus), run_time=0.4)
        self.wait(max(0.2, h - 1.2))
        self.sod_full, self.sod_head, self.sod_v1, self.sod_base, self.sod_barh = \
            full, head, v1, base, bar_h
        self.sod_cost_y = cost_y
        self.R_sodium = r

    def draw_N02(self, t):
        new_head = txt("sodium · 546 nm", 24, INK).move_to(self.sod_head.get_center())
        if new_head.width > self.sod_head.width * 1.2:
            new_head.scale_to_fit_width(self.sod_head.width * 1.2)
        new_h = self.sod_barh * (2.27 / 4.13)
        new_bar = self._bar(0.5, new_h, WARM, 0.6)
        new_bar.move_to([self.sod_full.get_center()[0], self.sod_base + new_h / 2, 0])
        # value rides just ABOVE the cost line (bar top ends a hair below it);
        # the 2.28 label sits below the line — clear vertical separation
        new_v1 = txt("2.27 eV", 20, WARM)
        new_v1.move_to([self.sod_v1.get_center()[0],
                        self.sod_cost_y + 0.18 + new_v1.height / 2, 0])
        watts = txt("10,000 W", 22, SECONDARY)
        watts.next_to(new_bar, LEFT, buff=0.2)
        if watts.get_left()[0] < self.R_sodium[0]:
            watts.next_to(new_bar, UP, buff=0.15).shift(LEFT * 0.3)
        d, h = self._pace(t)
        self.play(Transform(self.sod_head, new_head),
                  Transform(self.sod_full, new_bar),
                  Transform(self.sod_v1, new_v1), run_time=d)
        self.play(FadeIn(watts, scale=0.8), run_time=0.4)
        self.wait(max(0.2, h - 0.4))

    # ══════════════════════════ ACT 3 · CLOSE ════════════════════════════════
    def draw_B01(self, t):
        eqrow, tagrow = rows(self.R_full, [0.6, 0.4], gap=0.3)
        eq1 = MathTex(r"E = h\nu", color=INK)
        eq2 = MathTex(r"K = h\nu - \Phi", color=INK)
        eqs = VGroup(eq1, eq2).arrange(DOWN, buff=0.4)
        fit(eqs, eqrow, 0.55)
        tags = VGroup(txt("next · measuring h", 22, SECONDARY),
                      txt("next · the double slit", 22, SECONDARY)).arrange(DOWN, buff=0.2)
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
        ex = fit_text("Try it: find the longest wavelength that can free an "
                      "electron from your metal.", FONT, 24, HIGHLIGHT,
                      2 * safe_w() * 0.86)
        ex.move_to([0, self.R_full[1] + rh(self.R_full) * 0.12, 0])
        d, h = self._pace(t)
        self.play(FadeOut(self.tags), run_time=0.4)
        self.play(self.close.animate.scale(0.72).move_to(
            [0, self.R_full[3] - rh(self.R_full) * 0.18, 0]), run_time=0.5)
        self.play(Write(ex), run_time=d)
        self.wait(max(0.2, h - 0.9))

    def draw_OUTRO(self, t):
        park = fit_text(TITLE, FONT, 26, INK, 2 * safe_w() * 0.8)
        park.set_opacity(0.7)
        park.move_to([0, self.R_full[3] - park.height / 2 - 0.1, 0])
        self.play(FadeIn(park), run_time=0.5)
        self.wait(max(0.3, t - 0.5))
