#!/usr/bin/env python3
"""
dim_blue_beats_blinding_red_short_bb.py — Brown Blue SHORT cut (< 3:00).

Condensed scene for the short beat sheet. Same palette decision as the long
cut: warm amber #E07B39 for low-frequency ("red") light, blue #58C4DD for
high; drawn wavelength carries the physics; no red on screen.

Orientation-aware via bn_layout; renders 16:9 and 9:16 from the same file.

Render:
    manim -qh dim_blue_beats_blinding_red_short_bb.py BearsDoodlesVideo               # 16:9
    manim -qh -r 1080,1920 dim_blue_beats_blinding_red_short_bb.py BearsDoodlesVideo  # 9:16
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
        self.port = is_portrait()
        b = band()
        self.R_full = b
        # a slim top strip for the equation; the lab below
        top, main = rows(b, [0.22, 0.78], gap=0.25)
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
            else:
                self._text_card(beat.get("narration_text", ""), dur(bid))

    # ── helpers (concept-1 patterns) ─────────────────────────────────────────
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

    def _corner_label(self, s, color, rect=None):
        r = rect if rect is not None else self.R_full
        lbl = txt(s, 30, color)
        lbl.move_to([r[2] - lbl.width / 2 - 0.2, r[3] - lbl.height / 2 - 0.15, 0])
        return lbl

    def _wave(self, x0, x1, y, lam, color, amp=0.16):
        return ParametricFunction(
            lambda s: np.array([x0 + s * (x1 - x0),
                                y + amp * math.sin(2 * math.pi * (x1 - x0) * s / lam), 0]),
            t_range=[0, 1, 0.01], color=color, stroke_width=3)

    def _packet(self, color, size=0.13):
        # stroke opacity 0: fill-only shapes must not register as "curves" in
        # the layout audit (zero-WIDTH strokes still default to opacity 1)
        return Dot(color=color, radius=size).set_fill(color, 0.9).set_stroke(opacity=0)

    @staticmethod
    def _bar(width, height, color, opacity=0.7):
        return Rectangle(width=width, height=height, color=color, fill_color=color,
                         fill_opacity=opacity, stroke_width=0).set_stroke(opacity=0)

    # ══════════════════════ HOOK (plate + lamps) ═════════════════════════════
    def _hook_zones(self):
        r = self.R_main
        if self.port:
            return rows(r, [0.45, 0.55], gap=0.4)
        return cols(r, [0.48, 0.52], gap=0.6)

    def draw_H01(self, t):
        lampz, platez = self._hook_zones()
        plate = RoundedRectangle(corner_radius=0.08, width=1.1, height=2.4,
                                 color=INK, stroke_width=4,
                                 fill_color=HAIRLINE, fill_opacity=0.35)
        fit(plate, platez, 0.85)
        n = 4
        ys = np.linspace(plate.get_bottom()[1] + 0.22, plate.get_top()[1] - 0.22, n)
        xface = plate.get_left()[0] + 0.12
        self.electrons = VGroup(*[Dot([xface, y, 0], color=BLUE, radius=0.07) for y in ys])
        lamp = Circle(radius=0.42, color=WARM, fill_color=WARM,
                      fill_opacity=0.28, stroke_width=4).move_to(center(lampz))
        lbl = txt("red", 26, SECONDARY).next_to(lamp, DOWN, buff=0.15)
        if lbl.get_bottom()[1] < self.R_main[1]:
            lbl.next_to(lamp, UP, buff=0.15)
        waves = VGroup(*[self._wave(lamp.get_right()[0] + 0.15,
                                    plate.get_left()[0] - 0.15,
                                    lamp.get_center()[1] + o, 1.6, WARM)
                         for o in (-0.45, 0.0, 0.45)])
        self.plate, self.lamp, self.lamp_lbl, self.waves = plate, lamp, lbl, waves
        d, h = self._pace(t)
        self.play(Create(plate), FadeIn(self.electrons), run_time=d * 0.5)
        self.play(GrowFromCenter(lamp), FadeIn(lbl), run_time=d * 0.5)
        self.play(Create(waves), run_time=min(1.2, h * 0.6))
        self.wait(max(0.2, h - 1.2))

    def draw_H02(self, t):
        blue_lamp = Circle(radius=0.26, color=BLUE, fill_color=BLUE,
                           fill_opacity=0.28, stroke_width=4).move_to(self.lamp.get_center())
        new_waves = VGroup(*[self._wave(blue_lamp.get_right()[0] + 0.15,
                                        self.plate.get_left()[0] - 0.15,
                                        blue_lamp.get_center()[1] + o, 0.55, BLUE)
                             for o in (-0.45, 0.0, 0.45)])
        new_lbl = txt("blue", 26, SECONDARY).move_to(self.lamp_lbl.get_center())
        d, h = self._pace(t)
        self.play(ReplacementTransform(self.lamp, blue_lamp),
                  ReplacementTransform(self.waves, new_waves),
                  ReplacementTransform(self.lamp_lbl, new_lbl), run_time=d)
        self.lamp, self.waves, self.lamp_lbl = blue_lamp, new_waves, new_lbl
        self.play(self.electrons[1].animate.shift(RIGHT * 1.0 + UP * 0.4).set_opacity(0.25),
                  self.electrons[2].animate.shift(RIGHT * 1.0 + DOWN * 0.3).set_opacity(0.25),
                  run_time=min(1.0, h * 0.6))
        self.wait(max(0.2, h - 1.0))

    def draw_H03(self, t):
        warm_lamp = Circle(radius=0.6, color=WARM, fill_color=WARM,
                           fill_opacity=0.32, stroke_width=5).move_to(self.lamp.get_center())
        new_waves = VGroup(*[self._wave(warm_lamp.get_right()[0] + 0.15,
                                        self.plate.get_left()[0] - 0.15,
                                        warm_lamp.get_center()[1] + o, 1.6, WARM)
                             for o in np.linspace(-0.7, 0.7, 7)])
        # place the label relative to the NEW, larger lamp (audit: TEXT_ON_CURVE)
        new_lbl = txt("red", 26, SECONDARY).next_to(warm_lamp, DOWN, buff=0.25)
        if new_lbl.get_bottom()[1] < self.R_main[1]:
            new_lbl.next_to(warm_lamp, UP, buff=0.25)
        d, h = self._pace(t)
        self.play(ReplacementTransform(self.lamp, warm_lamp),
                  ReplacementTransform(self.waves, new_waves),
                  ReplacementTransform(self.lamp_lbl, new_lbl),
                  self.electrons[1].animate.set_opacity(1).shift(LEFT * 1.0 + DOWN * 0.4),
                  self.electrons[2].animate.set_opacity(1).shift(LEFT * 1.0 + UP * 0.3),
                  run_time=d)
        self.lamp, self.waves, self.lamp_lbl = warm_lamp, new_waves, new_lbl
        x100 = self._corner_label("×100", INK)
        self.play(FadeIn(x100, scale=0.7), run_time=0.4)
        self.play(Indicate(x100, color=HIGHLIGHT, scale_factor=1.1), run_time=0.5)
        self.wait(max(0.2, h - 0.9))

    # ══════════════════════ PACKETS → WELL → PAYOFF ══════════════════════════
    def draw_K01(self, t):
        r = self.R_main
        y = rcy(r)
        smooth = ParametricFunction(
            lambda s: np.array([r[0] + s * rw(r), y + 0.32 * math.sin(6 * math.pi * s), 0]),
            t_range=[0, 1, 0.01], color=INK, stroke_width=3)
        n = 8
        xs = np.linspace(r[0] + 0.2, r[2] - 0.2, n)
        stream = VGroup(*[self._packet(INK).move_to([x, y, 0]) for x in xs])
        d, h = self._pace(t)
        self.play(Create(smooth), run_time=d * 0.6)
        self.play(ReplacementTransform(smooth, stream), run_time=d * 0.6)
        self.play(stream.animate.shift(RIGHT * 0.4), run_time=max(0.5, h - 0.3),
                  rate_func=linear)
        self.stream = stream

    def draw_K02(self, t):
        r = self.R_main
        colw = rw(r) / 2
        wx, bx = r[0] + colw * 0.5, r[0] + colw * 1.5
        base_y = r[1] + rh(r) * 0.20
        warm_p = self._packet(WARM, 0.15).move_to([wx, r[3] - 0.4, 0])
        blue_p = self._packet(BLUE, 0.19).move_to([bx, r[3] - 0.4, 0])
        wbar = self._bar(0.4, rh(r) * 0.20, WARM)
        bbar = self._bar(0.4, rh(r) * 0.46, BLUE)
        wbar.move_to([wx, base_y + wbar.height / 2, 0])
        bbar.move_to([bx, base_y + bbar.height / 2, 0])
        wlbl = txt("red · weak", 22, SECONDARY)
        blbl = txt("blue · strong", 22, SECONDARY)
        for lbl, bar, x in ((wlbl, wbar, wx), (blbl, bbar, bx)):
            if lbl.width > colw * 0.9:
                lbl.scale_to_fit_width(colw * 0.9)
            lbl.next_to(bar, DOWN, buff=0.22)
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
        wx = self.warm_p.get_center()[0]
        top = self.R_main[3] - 0.25
        minis = VGroup(*[self._packet(WARM, 0.09).move_to(
            [wx + dx, top - i * 0.26, 0])
            for i, dx in enumerate(np.tile([-0.3, 0.0, 0.3], 3)[:7])])
        d, h = self._pace(t)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in minis],
                              lag_ratio=0.06), run_time=d)
        self.play(Indicate(self.wbar, color=HIGHLIGHT, scale_factor=1.06), run_time=0.7)
        self.wait(max(0.2, h - 0.7))
        self.minis = minis

    def draw_C01(self, t):
        r = self.R_main
        w = rw(r) * 0.5
        hgt = rh(r) * 0.5
        cx = rcx(r)
        y0 = r[1] + rh(r) * 0.10
        well = VGroup(
            Line([cx - w / 2, y0 + hgt, 0], [cx - w / 2, y0, 0], color=INK, stroke_width=4),
            Line([cx - w / 2, y0, 0], [cx + w / 2, y0, 0], color=INK, stroke_width=4),
            Line([cx + w / 2, y0, 0], [cx + w / 2, y0 + hgt, 0], color=INK, stroke_width=4))
        rim = DashedLine([cx - w / 2 - 0.25, y0 + hgt, 0], [cx + w / 2 + 0.25, y0 + hgt, 0],
                         color=HAIRLINE, stroke_width=3)
        lbl = txt("escape cost", 22, SECONDARY)
        if lbl.width > rw(r) * 0.4:
            lbl.scale_to_fit_width(rw(r) * 0.4)
        lbl.next_to(rim, UP, buff=0.1).shift(LEFT * (w * 0.25))
        if lbl.get_left()[0] < r[0]:
            lbl.shift(RIGHT * (r[0] - lbl.get_left()[0] + 0.05))
        self.wellgeo = (cx, y0, hgt, w)
        self.well, self.rim, self.rim_lbl = well, rim, lbl
        self.e_dot = Dot([cx, y0 + 0.15, 0], color=BLUE, radius=0.09)
        d, h = self._pace(t)
        # no parked reference copy in the short — the portrait frame is too
        # crowded (it collided with the 'escape cost' label); just clear the
        # comparison and move on
        self.play(FadeOut(self.minis), FadeOut(self.k_group), run_time=d * 0.5)
        self.play(Create(well), run_time=d * 0.5)
        self.play(FadeIn(self.e_dot, scale=0.5), Create(rim), Write(lbl),
                  run_time=min(1.0, h * 0.5))
        self.wait(max(0.2, h - 1.0))

    def draw_X01(self, t):
        cx, y0, hgt, w = self.wellgeo
        # bottom-LEFT: clear of rain (top-left) and the escape path (right)
        self.counter = txt("freed: 0", 24, SECONDARY)
        self.counter.move_to([self.R_main[0] + self.counter.width / 2 + 0.12,
                              self.R_main[1] + self.counter.height / 2 + 0.10, 0])
        rain = VGroup(*[self._packet(WARM, 0.08).move_to(
            [cx - w + 0.3 * i, y0 + hgt + 0.5 + 0.15 * (i % 3), 0]) for i in range(6)])
        d, h = self._pace(t)
        self.play(FadeIn(self.counter), FadeIn(rain, lag_ratio=0.1), run_time=d * 0.5)
        self.play(rain.animate.move_to([cx, y0 + hgt * 0.5, 0]).set_opacity(0),
                  self.e_dot.animate.move_to([cx, y0 + 0.15 + (hgt - 0.15) * 0.6, 0]),
                  run_time=d * 0.5, rate_func=rush_into)
        self.play(self.e_dot.animate.move_to([cx, y0 + 0.15, 0]), run_time=0.4)
        self.remove(rain)
        self.play(Indicate(self.counter, color=SECONDARY, scale_factor=1.05), run_time=0.5)
        self.wait(max(0.2, h - 0.9))

    def draw_X02(self, t):
        cx, y0, hgt, w = self.wellgeo
        pk = self._packet(BLUE, 0.15).move_to([cx - w, y0 + hgt + 0.4, 0])
        d, h = self._pace(t)
        self.play(pk.animate.move_to(self.e_dot.get_center()), run_time=d * 0.5)
        self.remove(pk)
        self.play(self.e_dot.animate.move_to([cx, y0 + hgt + 0.12, 0]),
                  run_time=d * 0.4, rate_func=rush_from)
        self.play(self.e_dot.animate.move_to([cx + w * 0.9, y0 + hgt + 0.6, 0]),
                  run_time=d * 0.4)
        new_c = txt("freed: 1", 24, INK).move_to(self.counter.get_center())
        self.play(Transform(self.counter, new_c), run_time=0.4)
        self.wait(max(0.2, h - 0.8))

    def draw_A01(self, t):
        eqrow, namerow = rows(self.R_top, [0.62, 0.38], gap=0.12)
        eq = MathTex(r"E = h\nu", color=INK)
        fit(eq, eqrow, 0.7)
        name = txt("photon", 26, INK)
        fit(name, namerow, 0.45)
        d, h = self._pace(t)
        self.play(Write(eq), run_time=d)
        self.play(FadeIn(name, shift=UP * 0.1), run_time=0.5)
        self.wait(max(0.2, h - 0.8))
        self.eq, self.photon_name = eq, name

    def draw_P01(self, t):
        cx, y0, hgt, w = self.wellgeo
        r = self.R_main
        top = r[3] - 0.3
        warm_lamp = Circle(radius=0.26, color=WARM, fill_color=WARM,
                           fill_opacity=0.3, stroke_width=3).move_to(
            [cx - w * 0.55, top, 0])
        blue_lamp = Circle(radius=0.15, color=BLUE, fill_color=BLUE,
                           fill_opacity=0.3, stroke_width=3).move_to(
            [cx + w * 0.55, top, 0])
        torrent = VGroup(*[self._packet(WARM, 0.07).move_to(
            warm_lamp.get_center() + DOWN * (0.3 + 0.2 * i) +
            RIGHT * (0.1 * ((i % 3) - 1))) for i in range(6)])
        trickle = self._packet(BLUE, 0.12).move_to(blue_lamp.get_center() + DOWN * 0.45)
        free = Dot([cx, y0 + 0.15, 0], color=BLUE, radius=0.09)
        d, h = self._pace(t)
        self.play(FadeOut(self.rim_lbl),
                  FadeIn(warm_lamp), FadeIn(blue_lamp), run_time=d * 0.5)
        self.add(free)
        self.play(FadeIn(torrent, lag_ratio=0.05), FadeIn(trickle), run_time=d * 0.5)
        self.play(torrent.animate.shift(DOWN * 0.8).set_opacity(0.0),
                  trickle.animate.shift(DOWN * 1.0).set_opacity(0.0),
                  free.animate.move_to([cx - w * 0.7, y0 + hgt + 0.55, 0]),
                  run_time=max(1.0, h * 0.5))
        self.wait(max(0.3, h * 0.5 - 0.4))

    def draw_OUTRO(self, t):
        # clear the equation strip first — the wrapped title parks INTO the top
        # band, and in portrait it landed exactly on 'photon' / E = hν
        old = VGroup(*[m for m in (getattr(self, "eq", None),
                                   getattr(self, "photon_name", None))
                       if m is not None])
        if len(old):
            self.play(FadeOut(old), run_time=0.3)
        park = fit_text(TITLE, FONT, 28, INK, rw(self.R_top) * 0.94)
        fit(park, self.R_top, 0.9)
        park.set_opacity(0.7)
        self.play(FadeIn(park), run_time=0.5)
        self.wait(max(0.3, t - 0.8))
