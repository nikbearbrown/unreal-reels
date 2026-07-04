"""
the_ultraviolet_catastrophe.py
===============================
Bear's Notes — "The Ultraviolet Catastrophe"
Quantum Mechanics Vol. 1, Ch. 1 (Candidate 02).

Renders the 11 MANIM beats (A02-A12) as one continuous, SILENT scene, each beat
timed to its real ElevenLabs audio duration from mp3/timings.json. The two DOODLE
beats (INTRO, A01) live ahead of this block and are stitched in at assembly; the
voiceover is laid over the whole thing by assemble.py.

Run order (audio first → timings.json → render → assemble):
    ai
    python ../../bears-doodles/scripts/generate_audio.py .      # writes mp3/ + timings.json
    manim -pqh the_ultraviolet_catastrophe.py BearsDoodlesVideo  # 1080p → media/
    python ../../bears-doodles/scripts/assemble.py . --mode clips --captions

If timings.json is absent (e.g. a quick preview before audio), fallback durations
are used so it still renders.

v1 — visual proportions may need light tuning on first render.
"""
import json
from pathlib import Path

import numpy as np
from manim import *

import bn_layout as BL
from bn_layout import is_portrait, band, rows, fit, fit_text, rw, safe_w, safe_h

HERE = Path(__file__).resolve().parent

# ── palette (from beat_sheet metadata) ───────────────────────────────────────
INK        = "#1a1a1a"
ACCENT     = "#5A5653"   # Warm Slate — the true/Planck curve
FORBIDDEN  = "#C0392B"   # red — the Rayleigh–Jeans runaway (the catastrophe)
GHOST      = "#D8C9C6"   # faded red ghost of the runaway
EMPTY      = "#B8B8B8"   # greyed-out (unaffordable) modes
FONT       = "Shadows Into Light"

# ── real audio durations (ground truth) ──────────────────────────────────────
_TIMINGS = {}
_tp = HERE / "mp3" / "timings.json"
if _tp.exists():
    _TIMINGS = json.loads(_tp.read_text())

# fallback estimates (seconds) used only if timings.json is missing
_FALLBACK = {
    "A02": 5.5, "A03": 5.0, "A04": 6.0, "A05": 5.5, "A06": 6.5,
    "A07": 5.5, "A08": 6.0, "A09": 6.0, "A10": 5.5, "A11": 6.0, "A12": 6.5,
}


def dur(bid: str) -> float:
    return float(_TIMINGS.get(bid, _FALLBACK.get(bid, 5.0)))


# ── safe area ─────────────────────────────────────────────────────────────────
# The 16:9 frame is ~14.22 wide × 8 tall. Keep ALL drawing inside this inset so
# nothing touches the edges (~8% margin = title/action-safe). Plot + labels live
# within ±SAFE_HALF_W, ±SAFE_HALF_H.
SAFE_HALF_W, SAFE_HALF_H = 6.3, 3.4

# ── plot coordinate mapping (inside the safe area) ────────────────────────────
X0, Y0 = -5.2, -2.3          # plot origin in scene space
XS, YS = 1.45, 1.15          # scene units per (frequency, brightness)
F_MAX  = 6.0
TITLE  = "The Ultraviolet Catastrophe"
CHANNEL = "youtube.com/@NikBearBrown"

# Small placeholder marker (scene coords: cx, cy, w, h). It only marks the spot —
# the doodle clip is composited over the region in the SEPARATE ffmpeg pass, which
# defines the real overlay size. Keep it small; the video covers it anyway.
MARK = (0.0, 0.0, 1.4, 1.9)


def P(f, b):
    """frequency f, brightness b → scene point."""
    return np.array([X0 + f * XS, Y0 + b * YS, 0.0])


def make_axes():
    x_axis = Line(P(0, 0), P(F_MAX + 0.2, 0), color=INK, stroke_width=4).add_tip(tip_length=0.18)
    y_axis = Line(P(0, 0), P(0, 4.0), color=INK, stroke_width=4).add_tip(tip_length=0.18)
    xl = Text("frequency", font=FONT, font_size=26, color=INK).next_to(x_axis, RIGHT, buff=0.1).shift(DOWN*0.15)
    yl = Text("brightness", font=FONT, font_size=26, color=INK).next_to(y_axis, UP, buff=0.12)
    return VGroup(x_axis, y_axis), VGroup(xl, yl)


def b_rj(f):
    """Rayleigh–Jeans: climbs as f² and shoots off the top."""
    return 0.17 * f ** 2


def b_planck(f):
    """Planck: rises, peaks, falls."""
    return 1.65 * f ** 3 / (np.exp(0.95 * f) - 1.0)


def rj_curve(f_hi=5.1, color=FORBIDDEN, sw=6):
    return ParametricFunction(lambda t: P(t, b_rj(t)), t_range=[0.05, f_hi, 0.02],
                              color=color, stroke_width=sw)


def planck_curve(color=ACCENT, sw=6):
    return ParametricFunction(lambda t: P(t, b_planck(t)), t_range=[0.05, F_MAX, 0.02],
                              color=color, stroke_width=sw)


def wavelet(f_center, humps=1, amp=0.45, span=0.45):
    """A small standing-wave arc sitting just above the axis at frequency f_center."""
    base = 0.12
    def fn(u):
        # u in [0,1] across the wavelet's frequency span
        f = f_center - span + 2 * span * u
        b = base + amp * np.sin(humps * np.pi * u)
        return P(f, b)
    return ParametricFunction(fn, t_range=[0, 1, 0.02], color=INK, stroke_width=4)


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
        if is_portrait():
            self._p_all()
            return

        # ── INTRO: brand + title (Manim text) with a small doodle marker ────
        self._intro_card()

        # ── HOOK: two doodle beats that motivate the problem ────────────────
        self._hook_beat("H01", "[ doodle: glow ]")
        self._hook_beat("H02", "[ doodle: blast ]")

        # ── SCENE 2 (A02–A06): the catastrophe ──────────────────────────────
        axes, labels = make_axes()
        self._A02(axes, labels)
        arcs = self._A03(axes)
        more_arcs, guide = self._A04(arcs)
        bars = self._A05(arcs, more_arcs)
        rj = self._A06()
        self._cut(axes, labels, arcs, more_arcs, guide, bars, rj)

        # ── SCENE 3 (A07): reality is calm ──────────────────────────────────
        self._A07()

        # ── SCENE 4 (A08–A09): energy comes in chunks ───────────────────────
        self._A08_A09()

        # ── SCENE 5 (A10–A12): the fix resolves the curve ───────────────────
        self._A10_A12()

        # ── OUTRO: thanks + channel (Manim text) with a bear marker ─────────
        self._outro_card()

    # ── PORTRAIT (9:16) — brightness-vs-frequency plot; runaway climbs UP ─────
    PPX0, PPY0, PPXS, PPYS, PPFMAX = -1.45, -1.7, 0.5, 0.95, 6.0

    def _Pp(self, f, b):
        return [self.PPX0 + f * self.PPXS, self.PPY0 + b * self.PPYS, 0]

    def _p_axes(self):
        xa = Line(self._Pp(0, 0), self._Pp(self.PPFMAX + 0.1, 0), color=INK, stroke_width=4).add_tip(tip_length=0.16)
        ya = Line(self._Pp(0, 0), self._Pp(0, 4.9), color=INK, stroke_width=4).add_tip(tip_length=0.16)
        xl = Text("frequency", font=FONT, font_size=22, color=INK).next_to(xa, DOWN, buff=0.18)
        yl = Text("brightness", font=FONT, font_size=22, color=INK).next_to(ya, UP, buff=0.1)
        return VGroup(xa, ya), VGroup(xl, yl)

    def _p_rj(self, f_hi=4.6):
        return ParametricFunction(lambda t: self._Pp(t, b_rj(t)), t_range=[0.05, f_hi, 0.02],
                                  color=FORBIDDEN, stroke_width=6)

    def _p_planck(self):
        return ParametricFunction(lambda t: self._Pp(t, b_planck(t)), t_range=[0.05, self.PPFMAX, 0.02],
                                  color=ACCENT, stroke_width=6)

    def _p_card(self, bid, label=""):
        t = dur(bid)
        crow, srow = rows(band(), [0.34, 0.66], gap=0.3)
        c = fit(fit_text(_NARR.get(bid, label), FONT, 34, INK, rw(crow) * 0.96), crow, 0.96)
        sk = self._hook_sketch(bid)
        if sk is not None:
            fit(sk, srow, 0.8)
        self.play(Write(c), run_time=min(1.4, t * 0.4))
        if sk is not None:
            self.play(Create(sk), run_time=min(1.2, t * 0.3))
        self.wait(max(0.3, t - 2.6))
        self.play(FadeOut(c, sk) if sk is not None else FadeOut(c), run_time=0.4)

    def _p_intro(self):
        t = dur("INTRO")
        brow, hrow, trow = rows(band(), [0.2, 0.48, 0.32], gap=0.25)
        brand = fit(Text("Bear's Notes", font=FONT, font_size=44, color=INK), brow, 0.82)
        hero = fit(self._intro_hero(), hrow, 0.8)
        title = fit(fit_text(TITLE, FONT, 30, ACCENT, rw(trow) * 0.96), trow, 0.98)
        self.play(FadeIn(brand), run_time=min(0.9, t * 0.25))
        self.play(Create(hero), run_time=min(1.6, t * 0.4))
        self.play(Write(title), run_time=min(1.2, t * 0.3))
        self.wait(max(0.2, t - 3.7))
        self.play(FadeOut(brand, hero, title), run_time=0.4)

    def _p_all(self):
        self._p_intro()
        self._p_card("H01", "[ glow ]")
        self._p_card("H02", "[ blast ]")

        axes, labels = self._p_axes()
        self.play(Create(axes), FadeIn(labels), run_time=dur("A02") * 0.9)
        self.wait(max(0.1, dur("A02") * 0.1))

        # A03 — a few low-frequency patterns
        t = dur("A03")
        low = VGroup(*[ParametricFunction(
            lambda u, fc=fc: self._Pp(fc - 0.3 + 0.6 * u, 0.1 + 0.5 * np.sin(np.pi * u)),
            t_range=[0, 1, 0.04], color=INK, stroke_width=3) for fc in (0.8, 1.6)])
        self.play(LaggedStart(*[Create(w) for w in low], lag_ratio=0.2), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))

        # A04 — patterns crowd in faster at higher frequency
        t = dur("A04")
        more = VGroup(*[ParametricFunction(
            lambda u, fc=fc: self._Pp(fc - 0.18 + 0.36 * u, 0.1 + 0.4 * np.sin(np.pi * u)),
            t_range=[0, 1, 0.04], color=INK, stroke_width=3) for fc in (2.6, 3.2, 3.8, 4.3, 4.8)])
        self.play(LaggedStart(*[Create(w) for w in more], lag_ratio=0.1), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))

        # A05 — classical: every pattern gets the same share (equal bars)
        t = dur("A05")
        bars = VGroup(*[Line(self._Pp(f, 0), self._Pp(f, 0.8), color=EMPTY, stroke_width=5)
                        for f in (0.8, 1.6, 2.6, 3.2, 3.8, 4.3, 4.8)])
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.08), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))

        # A06 — the runaway: RJ shoots off the top
        t = dur("A06")
        rj = self._p_rj()
        rl = Text("classical → ∞", font=FONT, font_size=24, color=FORBIDDEN).move_to([0.9, 3.0, 0])
        self.play(Create(rj), FadeIn(rl), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))
        self.play(FadeOut(low, more, bars), run_time=0.3)

        # A07 — reality: rises, peaks, falls
        t = dur("A07")
        planck = self._p_planck()
        pl = Text("real glow", font=FONT, font_size=24, color=ACCENT).next_to(planck, RIGHT, buff=0.1)
        self.play(rj.animate.set_stroke(opacity=0.25), Create(planck), FadeIn(pl), run_time=t * 0.8)
        self.wait(max(0.1, t * 0.2))

        # A08–A12 — the fix. Clear the axis labels and shrink the two curves into a
        # clean bottom strip, so the narration cards get an uncluttered top band
        # (no more colliding with the y-axis / 'brightness' / 'classical' labels).
        top, bot = rows(band(), [0.52, 0.48], gap=0.3)
        motif = VGroup(rj, planck)
        self.play(FadeOut(axes, labels, rl, pl),
                  motif.animate.scale(0.5).move_to([0, (bot[1] + bot[3]) / 2, 0]),
                  run_time=0.5)
        for bid, msg in (("A08", "energy comes only in whole chunks"),
                         ("A09", "each chunk costs more at higher frequency"),
                         ("A10", "the warm object can't afford the costly ones"),
                         ("A11", "so the runaway bends down to the real curve"),
                         ("A12", "energy in chunks lit the fuse of quantum physics")):
            t = dur(bid)
            c = fit(fit_text(_NARR.get(bid, msg), FONT, 32, INK, rw(top) * 0.96), top, 0.95)
            extra = [Indicate(motif, color=ACCENT)] if bid == "A11" else []
            self.play(Write(c), *extra, run_time=min(1.5, t * 0.45))
            self.wait(max(0.3, t - 1.9))
            self.play(FadeOut(c), run_time=0.3)

        self.play(FadeOut(motif), run_time=0.4)
        BL.outro(self, TITLE, CHANNEL, dur("OUTRO"), teaser_tex=_DEEP_TEX,
                 font=FONT, ink=INK, accent=ACCENT)

    # ── helpers ──────────────────────────────────────────────────────────────
    def _cut(self, *mobjects):
        self.play(FadeOut(*[m for m in mobjects if m is not None]), run_time=0.4)
        self.wait(0.1)

    def _hold(self, t, used):
        self.wait(max(0.2, t - used))

    def _snd(self, bid):
        """No-op. This scene is now SILENT like the rest — assemble.py muxes the
        voiceover. (Previously baked audio in-scene, which doubled it through the
        standard --mode manim assemble path.)"""
        return

    def _marker(self):
        cx, cy, w, h = MARK
        box = DashedVMobject(
            Rectangle(width=w, height=h, color=GHOST, stroke_width=3).move_to([cx, cy, 0]),
            num_dashes=24)
        return box

    # ── INTRO — brand + title text, small doodle marker ───────────────────────
    def _intro_hero(self):
        ax = VGroup(Line([-2.4, -1.0, 0], [2.4, -1.0, 0], color=INK, stroke_width=3),
                    Line([-2.4, -1.0, 0], [-2.4, 1.3, 0], color=INK, stroke_width=3))
        planck = ParametricFunction(lambda x: [x, -1.0 + 1.7 * np.exp(-((x + 0.4) / 0.8) ** 2), 0],
                                    t_range=[-2.4, 2.4, 0.02], color=ACCENT, stroke_width=4)
        runaway = ParametricFunction(lambda x: [x, -1.0 + 0.18 * np.exp(1.3 * (x + 2.4)), 0],
                                     t_range=[-2.4, -0.35, 0.02], color=FORBIDDEN, stroke_width=4)
        return VGroup(ax, planck, runaway)

    def _intro_card(self):
        t = dur("INTRO")
        self._snd("INTRO")
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

    # ── HOOK — narration card + a topic sketch ────────────────────────────────
    def _hook_beat(self, bid, label):
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
            body = Circle(radius=0.5, color=ACCENT, stroke_width=4).move_to([0, -0.9, 0])
            rays = VGroup(*[Line([0.55 * np.cos(a), -0.9 + 0.55 * np.sin(a), 0],
                                 [0.95 * np.cos(a), -0.9 + 0.95 * np.sin(a), 0], color=ACCENT, stroke_width=3)
                            for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)])
            return VGroup(body, rays, Text("warm things glow", font=FONT, font_size=28, color=INK).move_to([0, -2.5, 0]))
        if bid == "H02":
            ru = ParametricFunction(lambda x: [x, -1.6 + 0.2 * np.exp(1.3 * (x + 2.0)), 0],
                                    t_range=[-2.0, 0.0, 0.02], color=FORBIDDEN, stroke_width=4)
            return VGroup(ru, Text("classical blows up", font=FONT, font_size=28, color=FORBIDDEN).move_to([0, -2.7, 0]))
        return None
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

    def _A02(self, axes, labels):
        t = dur("A02")
        self._snd("A02")
        self.play(Create(axes), run_time=t * 0.6)
        self.play(FadeIn(labels), run_time=t * 0.25)
        self._hold(t, t * 0.85)

    # ── A03 — a few low-frequency patterns ───────────────────────────────────
    def _A03(self, axes):
        t = dur("A03")
        self._snd("A03")
        arcs = VGroup(wavelet(0.7, 1), wavelet(1.4, 2), wavelet(2.1, 3))
        self.play(LaggedStartMap(Create, arcs, lag_ratio=0.5), run_time=t * 0.75)
        self._hold(t, t * 0.75)
        return arcs

    # ── A04 — pattern count climbs as f² ──────────────────────────────────────
    def _A04(self, arcs):
        t = dur("A04")
        self._snd("A04")
        more = VGroup(*[wavelet(f, humps=int(f) + 1, amp=0.38, span=0.32)
                        for f in np.arange(2.8, 5.3, 0.55)])
        guide = DashedVMobject(
            ParametricFunction(lambda u: P(u, 0.13 * u ** 2), t_range=[0.1, 5.0, 0.03],
                               color=INK, stroke_width=2).set_opacity(0.45),
            num_dashes=40)
        self.play(LaggedStartMap(Create, more, lag_ratio=0.3), run_time=t * 0.6)
        self.play(Create(guide), run_time=t * 0.3)
        self._hold(t, t * 0.9)
        return more, guide

    # ── A05 — equal energy bars on every pattern ──────────────────────────────
    def _A05(self, arcs, more):
        t = dur("A05")
        self._snd("A05")
        all_arcs = [*arcs, *more]
        bars = VGroup()
        for a in all_arcs:
            top = a.get_top()
            bar = Line(top, top + UP * 0.5, color=ACCENT, stroke_width=6)
            bars.add(bar)
        self.play(LaggedStartMap(GrowFromEdge, bars, edge=DOWN, lag_ratio=0.15),
                  run_time=t * 0.75)
        self._hold(t, t * 0.75)
        return bars

    # ── A06 — the runaway to infinity ─────────────────────────────────────────
    def _A06(self):
        t = dur("A06")
        self._snd("A06")
        rj = rj_curve(f_hi=5.05, color=FORBIDDEN, sw=6)
        arrow = Arrow(P(4.4, b_rj(4.4)), P(5.0, b_rj(5.0)) + UP * 0.4,
                      color=FORBIDDEN, buff=0, stroke_width=6)
        self.play(Create(rj), run_time=t * 0.7)
        self.play(GrowArrow(arrow), run_time=t * 0.2)
        self._hold(t, t * 0.9)
        # bundle so the cut fades them too
        self._rj_group = VGroup(rj, arrow)
        return self._rj_group

    # ── A07 — reality is calm (Planck target) ─────────────────────────────────
    def _A07(self):
        t = dur("A07")
        self._snd("A07")
        axes, labels = make_axes()
        ghost = rj_curve(f_hi=4.6, color=GHOST, sw=4)
        planck = planck_curve(color=ACCENT, sw=6)
        self.play(Create(axes), FadeIn(labels), run_time=t * 0.4)
        self.play(FadeIn(ghost), run_time=t * 0.15)
        self.play(Create(planck), run_time=t * 0.4)
        self._hold(t, t * 0.95)
        self._cut(axes, labels, ghost, planck)

    # ── A08+A09 — energy in chunks, each costlier with frequency ──────────────
    def _A08_A09(self):
        # A08 — continuous ramp struck out, vs a staircase of equal chunks
        t8 = dur("A08")
        self._snd("A08")
        # left: a smooth ramp, struck out;  right: a staircase of equal chunks
        ramp = Line([-5, -1.4, 0], [-1.5, 1.0, 0], color=INK, stroke_width=5)
        cross = Cross(ramp, color=FORBIDDEN, stroke_width=6).scale(0.6)
        stair = VGroup()
        for i in range(4):
            step = Square(side_length=0.7, color=INK, stroke_width=5).move_to([1.6, -1.4 + i * 0.72, 0])
            stair.add(step)
        self.play(Create(ramp), run_time=t8 * 0.3)
        self.play(Create(cross), run_time=t8 * 0.2)
        self.play(LaggedStartMap(Create, stair, lag_ratio=0.3), run_time=t8 * 0.4)
        self._hold(t8, t8 * 0.9)

        # A09 — chunks grow taller with frequency; price tag on the tallest
        t9 = dur("A09")
        self._snd("A09")
        chunks = VGroup()
        for i, h in enumerate([0.5, 0.9, 1.4, 2.1]):
            c = Rectangle(width=0.6, height=h, color=INK, stroke_width=5).move_to(
                [2.0 + i * 1.0, -1.4 + h / 2, 0])
            chunks.add(c)
        tag = VGroup(
            RegularPolygon(4, color=FORBIDDEN, stroke_width=5).scale(0.35).rotate(PI / 4),
            Text("$$$", font=FONT, font_size=24, color=FORBIDDEN),
        )
        tag.arrange(RIGHT, buff=0.05).next_to(chunks[-1], UP, buff=0.2)
        self.play(FadeOut(ramp, cross, stair), run_time=t9 * 0.15)
        self.play(LaggedStartMap(GrowFromEdge, chunks, edge=DOWN, lag_ratio=0.25),
                  run_time=t9 * 0.5)
        self.play(FadeIn(tag, shift=DOWN * 0.2), run_time=t9 * 0.2)
        self._hold(t9, t9 * 0.85)
        self._cut(chunks, tag)

    # ── A10+A11+A12 — modes empty, curve bends, close ─────────────────────────
    def _A10_A12(self):
        # A10 — spectrum with high-frequency modes greyed/empty
        t10 = dur("A10")
        self._snd("A10")
        axes, labels = make_axes()
        solid = VGroup(wavelet(0.7, 1), wavelet(1.4, 2), wavelet(2.1, 3))
        empty = VGroup(*[wavelet(f, humps=int(f) + 1, amp=0.38, span=0.32).set_color(EMPTY).set_opacity(0.5)
                         for f in np.arange(3.4, 5.3, 0.6)])
        self.play(Create(axes), FadeIn(labels), run_time=t10 * 0.35)
        self.play(LaggedStartMap(Create, solid, lag_ratio=0.3), run_time=t10 * 0.3)
        self.play(LaggedStartMap(Create, empty, lag_ratio=0.2), run_time=t10 * 0.25)
        self._hold(t10, t10 * 0.9)

        # A11 — the red runaway bends down into the Warm Slate Planck curve
        t11 = dur("A11")
        self._snd("A11")
        rj = rj_curve(f_hi=3.2, color=FORBIDDEN, sw=6)
        planck = planck_curve(color=ACCENT, sw=6)
        self.play(Create(rj), run_time=t11 * 0.3)
        self.play(Transform(rj, planck), run_time=t11 * 0.55)
        self._hold(t11, t11 * 0.85)

        # A12 — highlight one chunk on the curve; hold on the finished curve
        t12 = dur("A12")
        self._snd("A12")
        fpk = 2.4
        chunk = Square(side_length=0.45, color=ACCENT, stroke_width=6,
                       fill_color=ACCENT, fill_opacity=0.18).move_to(P(fpk, b_planck(fpk)))
        self.play(FadeIn(chunk, scale=0.6), Flash(P(fpk, b_planck(fpk)), color=ACCENT),
                  run_time=t12 * 0.4)
        self._hold(t12, t12 * 0.4)
