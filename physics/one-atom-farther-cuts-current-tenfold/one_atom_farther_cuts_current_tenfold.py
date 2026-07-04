"""
one_atom_farther_cuts_current_tenfold.py
========================================
Bear's Notes — "Why One Extra Atom of Distance Cuts a Tunneling Current Tenfold"
Quantum Mechanics Vol. 1, Ch. 6 (Candidate 14).

9 MANIM beats (A01-A08), SILENT 16:9. A sharp tip TRACES a bumpy atomic surface at
fixed height; the tunnelling current dies exponentially with the gap, so the gauge
needle swings ~10x between an atom top and a valley. Driven by a ValueTracker on the
tip's x-position (self.tx — local, no clash with Scene.time). INTRO + two hooks are
placeholder markers. assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh one_atom_farther_cuts_current_tenfold.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # tunnel current + needle
RED     = "#C0392B"     # the tenfold emphasis
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why One Extra Atom of Distance Cuts a Tunneling Current Tenfold"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

# surface + tip geometry
SX0, SX1 = -6.2, 2.6
P = 1.5                  # atom spacing
SY = -2.3               # mean surface height
SAMP = 0.32             # bump amplitude
TIPY = -1.0             # tip apex height (scan height)
G = float(np.log(10) / (2 * SAMP))      # decay so one bump (top->valley) = 10x
DMIN = TIPY - (SY + SAMP)                # smallest gap (over a bump top)

# gauge
GC = np.array([4.7, 0.7, 0.0])
GR = 1.25

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.0, "A02": 4.0, "A03": 5.5, "A04": 4.5, "A05": 5.5, "A06": 5.0,
       "A07": 5.0, "A08": 5.0, "INTRO": 6.0, "H01": 4.5, "H02": 4.5, "OUTRO": 9.5}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def surf(x):
    return SY + SAMP * np.cos(2 * np.pi * x / P)


def gap(x):
    return TIPY - surf(x)


def cur(x):
    return float(np.exp(-G * (gap(x) - DMIN)))   # 1 over a bump top, 0.1 in a valley


def make_tip(x):
    apex = [x, TIPY, 0]
    tl = [x - 0.36, TIPY + 1.3, 0]
    tr = [x + 0.36, TIPY + 1.3, 0]
    return Polygon(apex, tr, tl, color=INK, fill_color=GHOST, fill_opacity=0.5, stroke_width=4)


def make_tunnel(x):
    I = cur(x)
    ln = Line([x, TIPY, 0], [x, surf(x), 0], color=ACCENT, stroke_width=2 + 9 * I)
    ln.set_stroke(opacity=0.35 + 0.6 * I)
    return ln


def make_needle(x):
    I = cur(x)
    ang = np.deg2rad(150 - 120 * I)
    tip = GC + (GR - 0.2) * np.array([np.cos(ang), np.sin(ang), 0])
    return Line(GC, tip, color=ACCENT, stroke_width=5)


_bsp = HERE / "beat_sheet.json"
_NARR = {b["beat_id"]: b.get("narration_text", "") for b in (
    __import__("json").loads(_bsp.read_text()).get("beats", []) if _bsp.exists() else [])}


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
        self.tx = ValueTracker(-5.6)
        self._intro_card()
        self._hook("H01", "[ doodle: tip feels one atom ]")
        self._hook("H02", "[ doodle: needle drops ]")
        self._stm_scene()
        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        surf = ParametricFunction(lambda x: [x, -0.9 + 0.18 * np.cos(2 * np.pi * x / 1.0), 0],
                                  t_range=[-1.7, 1.7, 0.02], color=INK, stroke_width=4)
        tip = Polygon([0, 0.2, 0], [-0.3, 1.0, 0], [0.3, 1.0, 0], color=INK, fill_color=ACCENT, fill_opacity=0.4, stroke_width=4)
        link = Line([0, 0.2, 0], [0, -0.72, 0], color=ACCENT, stroke_width=4)
        return VGroup(surf, tip, link)

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
        if bid == "H01":
            surf = ParametricFunction(lambda x: [x, -1.6 + 0.2 * np.cos(2 * np.pi * x / 1.0), 0],
                                      t_range=[-1.8, 1.8, 0.02], color=INK, stroke_width=4)
            tip = Polygon([0, -0.6, 0], [-0.3, 0.1, 0], [0.3, 0.1, 0], color=INK, fill_color=ACCENT, fill_opacity=0.4, stroke_width=4)
            return VGroup(surf, tip, Text("feels one atom", font=FONT, font_size=28, color=INK).move_to([0, -2.7, 0]))
        if bid == "H02":
            arc = Arc(radius=1.0, start_angle=np.deg2rad(150), angle=np.deg2rad(-120), color=INK, stroke_width=4).move_to([0, -0.9, 0])
            ndl = Line([0, -0.9, 0], [0 + 1.0 * np.cos(np.deg2rad(140)), -0.9 + 1.0 * np.sin(np.deg2rad(140)), 0], color=ACCENT, stroke_width=5)
            return VGroup(arc, ndl, Text("current drops", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        return None

    def _gauge(self):
        arc = Arc(radius=GR, start_angle=np.deg2rad(150), angle=np.deg2rad(-120),
                  arc_center=GC, color=INK, stroke_width=4)
        hub = Dot(GC, color=INK, radius=0.06)
        lo = Text("low", font=FONT, font_size=20, color=INK).move_to(
            GC + GR * np.array([np.cos(np.deg2rad(150)), np.sin(np.deg2rad(150)), 0]) + np.array([-0.1, -0.25, 0]))
        hi = Text("high", font=FONT, font_size=20, color=INK).move_to(
            GC + GR * np.array([np.cos(np.deg2rad(30)), np.sin(np.deg2rad(30)), 0]) + np.array([0.1, -0.25, 0]))
        lbl = Text("current", font=FONT, font_size=22, color=INK).move_to(GC + np.array([0, -1.5, 0]))
        return VGroup(arc, hub, lo, hi, lbl)

    # ── A01–A08 ───────────────────────────────────────────────────────────────
    def _stm_scene(self):
        tx = self.tx

        # A01 — surface + tip
        t1 = dur("A01")
        scurve = ParametricFunction(lambda x: [x, surf(x), 0], t_range=[SX0, SX1, 0.02],
                                    color=INK, stroke_width=4)
        ground = Polygon(*[[x, surf(x), 0] for x in np.linspace(SX0, SX1, 90)],
                         [SX1, -3.4, 0], [SX0, -3.4, 0],
                         color=GHOST, fill_color=GHOST, fill_opacity=0.18, stroke_width=0)
        tip = make_tip(tx.get_value())
        self.play(FadeIn(ground), Create(scurve), run_time=t1 * 0.6)
        self.play(Create(tip), run_time=t1 * 0.4)
        tip.add_updater(lambda m: m.become(make_tip(tx.get_value())))

        # A02 — tunnel link + gauge
        t2 = dur("A02")
        tunnel = make_tunnel(tx.get_value())
        gauge = self._gauge()
        needle = make_needle(tx.get_value())
        self.play(Create(tunnel), FadeIn(gauge), Create(needle), run_time=t2 * 0.9)
        tunnel.add_updater(lambda m: m.become(make_tunnel(tx.get_value())))
        needle.add_updater(lambda m: m.become(make_needle(tx.get_value())))
        self.wait(max(0.1, t2 * 0.1))

        # A03 — equal steps multiply (1, 1/10, 1/100)
        t3 = dur("A03")
        rows = VGroup(
            Text("one step farther", font=FONT, font_size=22, color=INK),
            Text("two steps farther", font=FONT, font_size=22, color=INK),
            Text("three steps farther", font=FONT, font_size=22, color=INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([-1.4, 1.7, 0])
        vals = VGroup(
            Text("x 1", font=FONT, font_size=22, color=ACCENT),
            Text("x 1/10", font=FONT, font_size=22, color=ACCENT),
            Text("x 1/100", font=FONT, font_size=22, color=ACCENT),
        )
        for v, r in zip(vals, rows):
            v.next_to(r, RIGHT, buff=0.5)
        cap3 = Text("equal steps multiply the current", font=FONT, font_size=26, color=INK).move_to([0, 3.0, 0])
        self.play(FadeIn(rows), LaggedStart(*[FadeIn(v) for v in vals], lag_ratio=0.3),
                  FadeIn(cap3), run_time=t3 * 0.85)
        self.wait(max(0.1, t3 * 0.15))
        self._cap = cap3
        self._ladder = VGroup(rows, vals)

        # A04 — start tracing
        t4 = dur("A04")
        cap4 = Text("drag the tip across the atoms", font=FONT, font_size=26, color=INK).move_to([0, 3.0, 0])
        self.play(FadeOut(self._ladder), Transform(self._cap, cap4), run_time=t4 * 0.25)
        self.play(tx.animate.set_value(1.6), run_time=t4 * 0.75, rate_func=linear)

        # A05 — needle swings wildly (sweep back across)
        t5 = dur("A05")
        cap5 = Text("the current leaps and collapses", font=FONT, font_size=26, color=ACCENT).move_to([0, 3.0, 0])
        self.play(Transform(self._cap, cap5), run_time=t5 * 0.15)
        self.play(tx.animate.set_value(-3.0), run_time=t5 * 0.85, rate_func=linear)

        # A06 — tiny height vs big swing (park over a bump top at x=-1.5)
        t6 = dur("A06")
        self.play(tx.animate.set_value(-1.5), run_time=t6 * 0.3, rate_func=smooth)
        # bracket a real atom height: bump top (x=-1.5) vs neighbouring valley (x=-0.75)
        br = DoubleArrow([-0.45, surf(-1.5), 0], [-0.45, surf(-0.75), 0], buff=0, color=INK,
                         stroke_width=3, tip_length=0.12)
        brl = Text("one atom", font=FONT, font_size=20, color=INK).next_to(br, RIGHT, buff=0.1)
        cap6 = Text("tiny height change, tenfold signal", font=FONT, font_size=26, color=RED).move_to([0, 3.0, 0])
        self.play(GrowArrow(br), FadeIn(brl), Transform(self._cap, cap6), run_time=t6 * 0.7)

        # A07 — current profile maps the atoms
        t7 = dur("A07")
        prof = ParametricFunction(lambda x: [x, 0.7 + 0.7 * cur(x), 0], t_range=[SX0, SX1, 0.02],
                                  color=ACCENT, stroke_width=3)
        cap7 = Text("the read-out maps the atoms", font=FONT, font_size=26, color=ACCENT).move_to([0, 3.0, 0])
        self.play(Create(prof), Transform(self._cap, cap7), run_time=t7 * 0.8)
        self.wait(max(0.2, t7 * 0.2))

        # A08 — punchline
        t8 = dur("A08")
        red = Text("one atom closer, ten times the current", font=FONT, font_size=28, color=RED).move_to([0, 2.5, 0])
        self.play(FadeOut(br, brl), Transform(self._cap, red), run_time=t8 * 0.7)
        self.wait(max(0.2, t8 * 0.3))

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
