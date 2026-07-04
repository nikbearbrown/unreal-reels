"""
dim_blue_beats_blinding_red.py
==============================
Bear's Notes — "Why a Dim Blue Lamp Beats a Blinding Red One" (photoelectric effect)
Quantum Mechanics Vol. 1, Ch. 1 (Candidate 03).

9 MANIM beats (A01–A08) as one continuous, SILENT 16:9 scene, each timed to its real
ElevenLabs duration from mp3/timings.json. INTRO + two hook beats are placeholder
markers (doodle clips overlaid later). assemble.py muxes the voiceover.

Colour carries the teaching: red packets are low-energy, blue packets high-energy
(a colorblind-safe pair).

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -pqh dim_blue_beats_blinding_red.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim

v1 — packet sizes / timing may want a tuning pass after render.
"""
import json
from pathlib import Path

import numpy as np
from manim import *

import bn_layout as BL
from bn_layout import is_portrait, band, rows, fit, fit_text, rw, safe_w, safe_h

HERE = Path(__file__).resolve().parent

INK    = "#1a1a1a"
ACCENT = "#5A5653"
RED    = "#C0392B"
BLUE   = "#2A6FB0"
GHOST  = "#C9BFBC"
FONT   = "Shadows Into Light"
TITLE  = "Why a Dim Blue Lamp Beats a Blinding Red One"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

# apparatus
SURF_Y = 0.0                 # metal surface height
THRESH_Y = 1.3               # escape-energy threshold
BLOCK = None                 # built in A03

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.0, "A02": 5.0, "A03": 4.5, "A04": 5.0, "A05": 4.5, "A06": 5.0,
       "A07": 4.5, "A08": 4.5, "INTRO": 4.5, "H01": 5.5, "H02": 5.0, "OUTRO": 6.5}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def packet(x, y, color, r=0.14):
    return Dot([x, y, 0], radius=r, color=color)


_bsp = HERE / "beat_sheet.json"
_BS = json.loads(_bsp.read_text()) if _bsp.exists() else {}
_NARR = {b["beat_id"]: b.get("narration_text", "") for b in _BS.get("beats", [])}
_DEEP_TEX = _BS.get("metadata", {}).get("deep_teaser_tex")


def _card(s, _sz=40):
    ws = s.split()
    lines = [" ".join(ws[i:i + 6]) for i in range(0, len(ws), 6)] or [""]
    g = VGroup(*[Text(l, font=FONT, font_size=_sz, color=INK) for l in lines]).arrange(DOWN, buff=0.28)
    if g.width > 11.5:
        g.scale_to_fit_width(11.5)
    return g


class BearsDoodlesVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        self.rng = np.random.default_rng(5)
        if is_portrait():
            self._p_all()
            return
        self._intro_card()
        self._hook("H01", "[ doodle: red floodlight ]")
        self._hook("H02", "[ doodle: blue glow ]")

        # SCENE 3 — what packets are
        self._A01()
        self._A02()
        self.play(FadeOut(*self.mobjects), run_time=0.4)
        self.wait(0.1)

        # SCENE 4 — the collisions
        self._A03_A08()

        self._outro_card()

    # ── PORTRAIT (9:16) — vertical photoelectric telling ──────────────────────
    def _p_plate(self, y=-1.5):
        bar = Line([-1.7, y, 0], [1.7, y, 0], color=INK, stroke_width=7)
        es = VGroup(*[Dot([-1.3 + i * 0.65, y + 0.12, 0], radius=0.09, color=INK) for i in range(5)])
        return bar, es

    def _p_card(self, bid, label=""):
        t = dur(bid)
        crow, srow = rows(band(), [0.32, 0.68], gap=0.3)
        c = fit(fit_text(_NARR.get(bid, label), FONT, 34, INK, rw(crow) * 0.96), crow, 0.96)
        sk = self._p_hook_sketch(bid)
        if sk is not None:
            fit(sk, srow, 0.8)
        r1 = min(1.4, t * 0.4)
        self.play(Write(c), run_time=r1)
        if sk is not None:
            self.play(Create(sk), run_time=min(1.2, t * 0.3))
        self.wait(max(0.3, t - r1 - 1.6))
        self.play(FadeOut(c, sk) if sk is not None else FadeOut(c), run_time=0.4)

    def _p_hook_sketch(self, bid):
        plate = Line([-1.4, -1.3, 0], [1.4, -1.3, 0], color=INK, stroke_width=6)
        if bid == "H01":
            ray = Arrow([-0.9, 0.6, 0], [-0.4, -1.1, 0], color=RED, buff=0, stroke_width=5)
            x = VGroup(Line([-0.1, -0.9, 0], [0.5, -1.5, 0], color=RED, stroke_width=5),
                       Line([-0.1, -1.5, 0], [0.5, -0.9, 0], color=RED, stroke_width=5))
            return VGroup(plate, ray, x)
        ray = Arrow([-0.6, 0.6, 0], [-0.1, -1.1, 0], color=BLUE, buff=0, stroke_width=5)
        e = Dot([0.3, -1.1, 0], color=BLUE, radius=0.13)
        ea = Arrow([0.3, -1.1, 0], [1.0, 0.6, 0], color=BLUE, buff=0, stroke_width=4)
        return VGroup(plate, ray, e, ea)

    def _p_intro(self):
        t = dur("INTRO")
        brow, hrow, trow = rows(band(), [0.2, 0.48, 0.32], gap=0.25)
        brand = fit(Text("Bear's Notes", font=FONT, font_size=44, color=INK), brow, 0.82)
        hero = fit(self._intro_hero(), hrow, 0.78)
        title = fit(fit_text(TITLE, FONT, 30, ACCENT, rw(trow) * 0.96), trow, 0.98)
        self.play(FadeIn(brand), run_time=min(0.9, t * 0.25))
        self.play(Create(hero), run_time=min(1.6, t * 0.4))
        self.play(Write(title), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 3.7))
        self.play(FadeOut(brand, hero, title), run_time=0.4)

    def _p_all(self):
        self._p_intro()
        self._p_card("H01", "[ red floodlight ]")
        self._p_card("H02", "[ blue glow ]")

        # A01 — packets fall onto the plate
        t = dur("A01")
        bar, es = self._p_plate(y=-1.7)
        packs = VGroup(*[packet(-1.2 + i * 0.6, 2.8, INK, 0.12) for i in range(5)])
        self.play(Create(bar), FadeIn(es), run_time=t * 0.5)
        self.play(packs.animate.shift(DOWN * 3.6), run_time=t * 0.4)
        self.play(FadeOut(packs), run_time=0.2)

        # A02 — red weak vs blue strong, vs escape threshold
        t = dur("A02")
        thr = DashedLine([-1.8, 0.5, 0], [1.8, 0.5, 0], color=ACCENT, stroke_width=3)
        tl = Text("escape energy", font=FONT, font_size=22, color=ACCENT).next_to(thr, UP, buff=0.1)
        redbar = Line([-1.0, -1.7, 0], [-1.0, -0.4, 0], color=RED, stroke_width=10)
        rl = Text("red", font=FONT, font_size=22, color=RED).next_to(redbar, DOWN, buff=0.12)
        bluebar = Line([1.0, -1.7, 0], [1.0, 1.4, 0], color=BLUE, stroke_width=10)
        bl= Text("blue", font=FONT, font_size=22, color=BLUE).next_to(bluebar, DOWN, buff=0.12)
        self.play(GrowFromEdge(redbar, DOWN), FadeIn(rl),
                  GrowFromEdge(bluebar, DOWN), FadeIn(bl), run_time=t * 0.6)
        self.play(Create(thr), FadeIn(tl), run_time=t * 0.4)
        self.play(FadeOut(bar, es, thr, tl, redbar, rl, bluebar, bl), run_time=0.4)

        # A03 — plate + electrons + threshold (the apparatus we'll fire at)
        t = dur("A03")
        bar, es = self._p_plate(y=-1.9)
        thr = DashedLine([-1.8, -0.4, 0], [1.8, -0.4, 0], color=ACCENT, stroke_width=3)
        tl = Text("escape energy", font=FONT, font_size=22, color=ACCENT).next_to(thr, UP, buff=0.1)
        self.play(Create(bar), FadeIn(es), run_time=t * 0.6)
        self.play(Create(thr), FadeIn(tl), run_time=t * 0.4)

        # A04 — one red falls, bounces, electron stays
        t = dur("A04")
        red = packet(0, 2.7, RED, 0.13)
        self.play(red.animate.move_to([0, -1.75, 0]), run_time=t * 0.4)
        self.play(Wiggle(es[2]), red.animate.move_to([1.2, 0.6, 0]).set_opacity(0.0), run_time=t * 0.45)
        self.wait(max(0.1, t * 0.15))

        # A05 — barrage of red, nothing
        t = dur("A05")
        barrage = VGroup(*[packet(self.rng.uniform(-1.6, 1.6), 2.4 + self.rng.uniform(0, 0.8), RED, 0.1) for _ in range(14)])
        self.play(FadeIn(barrage, lag_ratio=0.05), run_time=t * 0.3)
        self.play(barrage.animate.shift(DOWN * 4.2).set_opacity(0.0),
                  LaggedStart(*[Wiggle(e) for e in es], lag_ratio=0.05), run_time=t * 0.5)
        self.wait(max(0.1, t * 0.2))

        # A06 — one blue frees an electron (flies up off the top)
        t = dur("A06")
        blue = packet(0, 2.7, BLUE, 0.18)
        self.play(blue.animate.move_to([0, -1.85, 0]), run_time=t * 0.4)
        freed = es[2]
        self.play(blue.animate.set_opacity(0.0),
                  freed.animate.move_to([0.5, 1.6, 0]).set_color(BLUE),
                  Flash(freed.get_center(), color=BLUE), run_time=t * 0.5)
        self.wait(max(0.1, t * 0.1))

        # A07 — tally
        t = dur("A07")
        rt = Text("red: 0 freed", font=FONT, font_size=26, color=RED).move_to([0, 2.6, 0])
        bt = Text("blue: 1 freed", font=FONT, font_size=26, color=BLUE).move_to([0, 2.1, 0])
        self.play(FadeIn(rt), run_time=t * 0.45)
        self.play(FadeIn(bt), run_time=t * 0.4)
        self.wait(max(0.1, t * 0.15))

        # A08 — the photon
        t = dur("A08")
        self.play(FadeOut(rt, bt), run_time=t * 0.2)
        pl = Text("one photon", font=FONT, font_size=26, color=BLUE).move_to([0, 2.3, 0])
        self.play(FadeIn(pl), Indicate(freed, color=BLUE), run_time=t * 0.6)
        self.wait(max(0.2, t * 0.2))

        BL.outro(self, TITLE, CHANNEL, dur("OUTRO"), teaser_tex=_DEEP_TEX,
                 font=FONT, ink=INK, accent=ACCENT)

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        plate = Line([-2.0, -0.9, 0], [0.6, -0.9, 0], color=INK, stroke_width=6)
        light = Arrow([-1.4, 1.1, 0], [-0.6, -0.7, 0], color=ACCENT, buff=0, stroke_width=5)
        elec = Dot([-0.1, -0.3, 0], color=ACCENT, radius=0.14)
        ea = Arrow([-0.1, -0.5, 0], [1.5, 0.6, 0], color=ACCENT, buff=0, stroke_width=4)
        return VGroup(plate, light, elec, ea)

    def _intro_card(self):
        t = dur("INTRO")
        brand = Text("Bear's Notes", font=FONT, font_size=44, color=INK).move_to([0, 3.0, 0])
        hero = self._intro_hero().move_to([0, 0.4, 0])
        title = Text(TITLE, font=FONT, font_size=30, color=ACCENT)
        title.scale_to_fit_width(min(11.0, title.width)).move_to([0, -2.5, 0])
        r1, r2, r3 = min(0.9, t * 0.22), min(1.6, t * 0.4), min(1.3, t * 0.28)
        self.play(FadeIn(brand), run_time=r1)
        self.play(Create(hero), run_time=r2)
        self.play(Write(title), run_time=r3)
        self.wait(max(0.2, t - r1 - r2 - r3 - 0.4))
        self.play(FadeOut(brand, hero, title), run_time=0.4)

    def _hook(self, bid, label):
        t = dur(bid)
        card = _card(_NARR.get(bid, label)).scale(0.82).to_edge(UP, buff=0.7)
        sketch = self._hook_sketch(bid)
        r1 = min(1.4, t * 0.38)
        self.play(Write(card), run_time=r1)
        used = r1
        if sketch is not None:
            r2 = min(1.4, t * 0.34)
            self.play(Create(sketch), run_time=r2)
            used += r2
        self.wait(max(0.3, t - used - 0.4))
        self.play(FadeOut(card, sketch) if sketch is not None else FadeOut(card), run_time=0.4)

    def _hook_sketch(self, bid):
        plate = lambda: Line([-1.6, -1.5, 0], [1.0, -1.5, 0], color=INK, stroke_width=6)
        ray = lambda: Arrow([-1.3, -0.4, 0], [-0.5, -1.3, 0], color=ACCENT, buff=0, stroke_width=5)
        if bid == "H01":
            x = VGroup(Line([0.5, -0.8, 0], [1.1, -0.2, 0], color=INK, stroke_width=5),
                       Line([0.5, -0.2, 0], [1.1, -0.8, 0], color=INK, stroke_width=5))
            return VGroup(plate(), ray(), x, Text("bright red: nothing", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        if bid == "H02":
            e = Dot([-0.2, -1.3, 0], color=ACCENT, radius=0.13)
            ea = Arrow([-0.2, -1.3, 0], [1.3, -0.2, 0], color=ACCENT, buff=0, stroke_width=4)
            return VGroup(plate(), ray(), e, ea, Text("faint blue: electrons fly", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        return None

    def _A01(self):
        t = dur("A01")
        beam = Rectangle(width=10, height=0.5, color=GHOST, fill_color=GHOST,
                         fill_opacity=0.4, stroke_width=0).move_to([-1, 0, 0])
        self.play(FadeIn(beam, shift=RIGHT), run_time=t * 0.35)
        packs = VGroup(*[packet(-5 + i * 1.1, 0, INK, r=0.12) for i in range(9)])
        self.play(FadeOut(beam), LaggedStartMap(GrowFromCenter, packs, lag_ratio=0.1),
                  run_time=t * 0.45)
        self.play(packs.animate.shift(RIGHT * 1.2), run_time=t * 0.2)
        self._p = packs

    # ── A02 — red weak vs blue strong ─────────────────────────────────────────
    def _A02(self):
        t = dur("A02")
        self.play(FadeOut(self._p), run_time=t * 0.15)
        base = Line([-3.5, -1.6, 0], [3.5, -1.6, 0], color=INK, stroke_width=3)
        red = packet(-1.8, -1.6 + 0.12, RED, r=0.13)
        red_bar = Line([-1.8, -1.6, 0], [-1.8, -0.6, 0], color=RED, stroke_width=8)
        red_lbl = Text("red · weak", font=FONT, font_size=26, color=RED).next_to(red_bar, UP, buff=0.15)
        blue = packet(1.8, -1.6 + 0.18, BLUE, r=0.19)
        blue_bar = Line([1.8, -1.6, 0], [1.8, 1.4, 0], color=BLUE, stroke_width=8)
        blue_lbl = Text("blue · strong", font=FONT, font_size=26, color=BLUE).next_to(blue_bar, UP, buff=0.15)
        self.play(Create(base), run_time=t * 0.2)
        self.play(GrowFromCenter(red), GrowFromEdge(red_bar, DOWN), FadeIn(red_lbl), run_time=t * 0.3)
        self.play(GrowFromCenter(blue), GrowFromEdge(blue_bar, DOWN), FadeIn(blue_lbl), run_time=t * 0.3)
        self.wait(max(0.2, t * 0.2))

    # ── A03–A08 — collisions ──────────────────────────────────────────────────
    def _metal(self):
        block = Rectangle(width=2.2, height=3.0, color=INK, fill_color="#e9e9e9",
                          fill_opacity=1.0, stroke_width=4).move_to([4.4, SURF_Y - 1.5, 0])
        electrons = VGroup(*[Dot([3.55 + i * 0.42, SURF_Y, 0], radius=0.08, color=INK)
                             for i in range(5)])
        thresh = DashedLine([3.0, THRESH_Y, 0], [5.8, THRESH_Y, 0], color=ACCENT, stroke_width=3)
        tlabel = Text("escape energy", font=FONT, font_size=24, color=ACCENT).next_to(thresh, UP, buff=0.12)
        return block, electrons, thresh, tlabel

    def _A03_A08(self):
        # A03 — metal + threshold
        t3 = dur("A03")
        block, electrons, thresh, tlabel = self._metal()
        self.play(Create(block), LaggedStartMap(GrowFromCenter, electrons, lag_ratio=0.15),
                  run_time=t3 * 0.6)
        self.play(Create(thresh), FadeIn(tlabel), run_time=t3 * 0.35)
        self.wait(max(0.1, t3 * 0.1))

        # A04 — red bounces, electron stays
        t4 = dur("A04")
        red = packet(-5, SURF_Y, RED, r=0.13)
        self.play(red.animate.move_to([3.4, SURF_Y, 0]), run_time=t4 * 0.4)
        e = electrons[2]
        self.play(Wiggle(e), red.animate.move_to([-1, 1.0, 0]).set_opacity(0.0), run_time=t4 * 0.45)
        self.wait(max(0.1, t4 * 0.15))

        # A05 — barrage of red, nothing
        t5 = dur("A05")
        barrage = VGroup(*[packet(-6 + self.rng.uniform(0, 1.5), self.rng.uniform(-1.2, 1.2), RED, r=0.1)
                           for _ in range(16)])
        self.play(FadeIn(barrage, lag_ratio=0.05), run_time=t5 * 0.3)
        self.play(barrage.animate.shift(RIGHT * 7).set_opacity(0.0),
                  LaggedStart(*[Wiggle(e) for e in electrons], lag_ratio=0.05), run_time=t5 * 0.5)
        self.wait(max(0.1, t5 * 0.2))

        # A06 — one blue frees an electron
        t6 = dur("A06")
        blue = packet(-5, SURF_Y, BLUE, r=0.18)
        self.play(blue.animate.move_to([3.4, SURF_Y, 0]), run_time=t6 * 0.4)
        freed = electrons[2]
        self.play(blue.animate.set_opacity(0.0),
                  freed.animate.move_to([1.5, THRESH_Y + 1.6, 0]).set_color(BLUE),
                  Flash(freed.get_center(), color=BLUE), run_time=t6 * 0.5)
        self.wait(max(0.1, t6 * 0.1))
        self._freed = freed
        self._scene = VGroup(block, electrons, thresh, tlabel)

        # A07 — tally
        t7 = dur("A07")
        crowd = VGroup(*[packet(-5.6 + (i % 4) * 0.35, 2.4 - (i // 4) * 0.35, RED, r=0.09) for i in range(12)])
        red_tally = Text("0 freed", font=FONT, font_size=28, color=RED).next_to(crowd, DOWN, buff=0.2)
        oneblue = packet(-2.0, 2.2, BLUE, r=0.18)
        blue_tally = Text("1 freed", font=FONT, font_size=28, color=BLUE).next_to(oneblue, DOWN, buff=0.2)
        self.play(FadeIn(crowd, lag_ratio=0.05), FadeIn(red_tally), run_time=t7 * 0.45)
        self.play(GrowFromCenter(oneblue), FadeIn(blue_tally), run_time=t7 * 0.4)
        self.wait(max(0.1, t7 * 0.15))
        self._tally = VGroup(crowd, red_tally, oneblue, blue_tally)

        # A08 — the photon
        t8 = dur("A08")
        self.play(FadeOut(self._tally), run_time=t8 * 0.2)
        photon = packet(-2.0, 2.0, BLUE, r=0.2)
        plabel = Text("one photon", font=FONT, font_size=26, color=BLUE).next_to(photon, UP, buff=0.15)
        self.play(GrowFromCenter(photon), FadeIn(plabel), Indicate(self._freed, color=BLUE),
                  run_time=t8 * 0.6)
        self.wait(max(0.2, t8 * 0.2))

    # ── OUTRO ─────────────────────────────────────────────────────────────────
    def _outro_card(self):
        t = dur("OUTRO")
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)
        thanks = Text("Thanks for watching", font=FONT, font_size=44, color=INK).move_to([0, 1.7, 0])
        title = Text(TITLE, font=FONT, font_size=30, color=ACCENT)
        title.scale_to_fit_width(min(11.0, title.width)).move_to([0, 0.2, 0])
        url = Text("youtube.com/@NikBearBrown", font=FONT, font_size=36, color=INK).move_to([0, -1.7, 0])
        self.play(Write(thanks), run_time=1.2)
        self.play(FadeIn(title), run_time=1.0)
        self.play(Write(url), run_time=1.2)
        self.wait(max(0.6, t - 3.8))
