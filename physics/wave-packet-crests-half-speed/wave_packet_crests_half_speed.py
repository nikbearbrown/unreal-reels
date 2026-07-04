"""
wave_packet_crests_half_speed.py
================================
Bear's Notes — "Why a Wave Packet's Wiggles Move at Half the Speed of the Packet"
Quantum Mechanics Vol. 1, Ch. 8 (Candidate 06).

9 MANIM beats (A01–A08), SILENT 16:9, continuous real-time motion driven by a
ValueTracker. The packet's envelope moves at the group velocity; its crests move at
half that (phase velocity), so a tagged crest drifts toward the rear. INTRO + two
hook beats are placeholder markers. assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh wave_packet_crests_half_speed.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim

Note: this scene re-evaluates the wave each frame (continuous motion), so it renders
slower than the stroke-on videos. v1 — speeds/sizes may want a tuning pass.
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # wave + envelope
RED     = "#C0392B"     # tagged crest dot
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why a Wave Packet's Wiggles Move at Half the Speed of the Packet"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

# packet parameters
A_AMP = 1.2            # amplitude (scene units)
SIGMA = 1.3           # envelope width
K = 5.5               # carrier wavenumber
VG = 0.40             # group (envelope) velocity
VP = 0.20             # phase (crest) velocity = VG/2
X0 = -3.2             # starting envelope centre
XR = 6.8              # plot half-range
_n = round(X0 * K / (2 * np.pi))

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.0, "A02": 5.0, "A03": 4.0, "A04": 4.5, "A05": 4.5, "A06": 4.5,
       "A07": 5.0, "A08": 5.0, "INTRO": 5.5, "H01": 4.5, "H02": 4.5, "OUTRO": 6.5}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def xc(t):
    return X0 + VG * t


def envelope(x, t):
    return A_AMP * np.exp(-((x - xc(t)) / SIGMA) ** 2)


def psi(x, t):
    return envelope(x, t) * np.cos(K * (x - VP * t))


def dot_point(t):
    x = VP * t + 2 * np.pi * _n / K
    return np.array([x, envelope(x, t), 0.0])


def wave_graph(t):
    return FunctionGraph(lambda x: psi(x, t), x_range=[-XR, XR, 0.04], color=ACCENT, stroke_width=4)


def env_graph(t, sign=1):
    return DashedVMobject(
        FunctionGraph(lambda x: sign * envelope(x, t), x_range=[-XR, XR, 0.06]).set_stroke(GHOST, 3),
        num_dashes=60)


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
        self.tt = ValueTracker(0.0)
        self._intro_card()
        self._hook("H01", "[ doodle: rippling blob ]")
        self._hook("H02", "[ doodle: ripples slide back ]")
        self._packet_scene()
        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        return ParametricFunction(lambda x: [x, 0.9 * np.exp(-(x / 1.3) ** 2) * np.cos(5 * x), 0],
                                  t_range=[-2.6, 2.6, 0.02], color=ACCENT, stroke_width=4)

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
        pk = lambda: ParametricFunction(lambda x: [x, -1.0 + 0.7 * np.exp(-(x / 1.1) ** 2) * np.cos(6 * x), 0],
                                        t_range=[-2.4, 2.4, 0.02], color=ACCENT, stroke_width=4)
        if bid == "H01":
            return VGroup(pk(), Text("a blob of waves", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        if bid == "H02":
            arr = Arrow([0.5, -1.0, 0], [-0.9, -1.0, 0], color=INK, buff=0, stroke_width=5)
            return VGroup(pk(), arr, Text("ripples slide back", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        return None

    def _packet_scene(self):
        T = self.tt

        # A01 — build the static packet, then attach motion updaters
        t1 = dur("A01")
        wave = wave_graph(0)
        eu, ed = env_graph(0, 1), env_graph(0, -1)
        self.play(Create(eu), Create(ed), run_time=t1 * 0.4)
        self.play(Create(wave), run_time=t1 * 0.5)
        wave.add_updater(lambda m: m.become(wave_graph(T.get_value())))
        eu.add_updater(lambda m: m.become(env_graph(T.get_value(), 1)))
        ed.add_updater(lambda m: m.become(env_graph(T.get_value(), -1)))
        self.wait(max(0.1, t1 * 0.1))

        # A02 — start moving
        self.play(T.animate.increment_value(dur("A02")), run_time=dur("A02"), rate_func=linear)

        # A03 — tag a crest
        dot = Dot(dot_point(T.get_value()), radius=0.1, color=RED)
        dot.add_updater(lambda m: m.move_to(dot_point(T.get_value())))
        self.play(FadeIn(dot, scale=0.5), T.animate.increment_value(dur("A03")),
                  run_time=dur("A03"), rate_func=linear)

        # A04 — speed legend (envelope long, crest half)
        env_arrow = Arrow([-6.0, 2.7, 0], [-3.4, 2.7, 0], color=ACCENT, buff=0, stroke_width=5)
        crest_arrow = Arrow([-6.0, 2.1, 0], [-4.7, 2.1, 0], color=RED, buff=0, stroke_width=5)
        env_lbl = Text("envelope", font=FONT, font_size=24, color=ACCENT).next_to(env_arrow, RIGHT, buff=0.15)
        crest_lbl = Text("crest (half)", font=FONT, font_size=24, color=RED).next_to(crest_arrow, RIGHT, buff=0.15)
        legend = VGroup(env_arrow, crest_arrow, env_lbl, crest_lbl)
        self.play(FadeIn(legend), T.animate.increment_value(dur("A04")), run_time=dur("A04"), rate_func=linear)

        # A05 — dot slides to the rear
        self.play(T.animate.increment_value(dur("A05")), run_time=dur("A05"), rate_func=linear)

        # A06 — crests born at front, die at rear
        self.play(T.animate.increment_value(dur("A06")), run_time=dur("A06"), rate_func=linear)
        dot.clear_updaters()
        self.play(FadeOut(dot), run_time=0.01)

        # A07 — name the velocities (hold motion)
        t7 = dur("A07")
        vlabel = VGroup(
            Text("crest = phase velocity", font=FONT, font_size=26, color=RED),
            Text("envelope = group velocity  (2x)", font=FONT, font_size=26, color=ACCENT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, -2.6, 0])
        self.play(FadeIn(vlabel), run_time=t7 * 0.5)
        self.wait(max(0.2, t7 * 0.5))

        # A08 — the particle is the envelope
        t8 = dur("A08")
        cx_now = xc(T.get_value())
        here = Text("the particle is here", font=FONT, font_size=26, color=INK).move_to([cx_now, 2.4, 0])
        self.play(FadeOut(legend), eu.animate.set_stroke(ACCENT, 5), ed.animate.set_stroke(ACCENT, 5),
                  FadeIn(here), run_time=t8 * 0.6)
        self.wait(max(0.2, t8 * 0.4))
        # stop updaters so the outro holds a static frame
        for m in (wave, eu, ed):
            m.clear_updaters()
        self._keep = VGroup(wave, eu, ed, vlabel, here)

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
