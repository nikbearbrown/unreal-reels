"""
tunnel_through_thin_wall.py
===========================
Bear's Notes — "Why a Particle Can Pass Through a Wall It Can't Go Over" (tunneling)
Quantum Mechanics Vol. 1, Ch. 6 (Candidate 05).

9 MANIM beats (A01–A08) as one continuous, SILENT 16:9 scene, each timed to its real
ElevenLabs duration from mp3/timings.json. INTRO + two hook beats are placeholder
markers. assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh tunnel_through_thin_wall.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # the wave
RED     = "#C0392B"     # the barrier / can't cross
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why a Particle Can Pass Through a Wall It Can't Go Over"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.0, "A02": 5.0, "A03": 4.5, "A04": 4.5, "A05": 5.0, "A06": 4.0,
       "A07": 5.0, "A08": 4.5, "INTRO": 4.0, "H01": 5.0, "H02": 5.5, "OUTRO": 6.5}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def wave_osc(x0, x1, amp, k=3.4, color=ACCENT, sw=5):
    return ParametricFunction(lambda x: [x, amp * np.sin(k * (x - x0)), 0],
                              t_range=[x0, x1, 0.02], color=color, stroke_width=sw)


def decay_curve(x0, x1, amp, kappa, color=ACCENT, sw=5):
    return ParametricFunction(lambda x: [x, amp * np.exp(-kappa * (x - x0)), 0],
                              t_range=[x0, x1, 0.02], color=color, stroke_width=sw)


def barrier(cx, w):
    return Rectangle(width=w, height=4.6, color=RED, fill_color=RED,
                     fill_opacity=0.12, stroke_width=4).move_to([cx, 0, 0])


def baseline():
    return Line([-6.4, 0, 0], [6.4, 0, 0], color=INK, stroke_width=2)


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
        self._intro_card()
        self._hook("H01", "[ doodle: ball rolls back ]")
        self._hook("H02", "[ doodle: particle on far side ]")

        # SCENE 3 — oscillation → decay
        self._A01_A03()
        self.play(FadeOut(*self.mobjects), run_time=0.4)
        self.wait(0.1)

        # SCENE 4 — thin barrier transmits
        self._A04_A08()

        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_hero(self):
        bar = Rectangle(width=0.7, height=2.0, color=INK, fill_color=ACCENT, fill_opacity=0.18, stroke_width=4)
        left = ParametricFunction(lambda x: [x, 0.6 * np.sin(4 * x), 0], t_range=[-2.2, -0.35, 0.03], color=ACCENT, stroke_width=4)
        right = ParametricFunction(lambda x: [x, 0.3 * np.sin(4 * x), 0], t_range=[0.35, 2.0, 0.03], color=ACCENT, stroke_width=4)
        return VGroup(bar, left, right)

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
            hill = Arc(radius=1.2, start_angle=0.2, angle=2.7, color=INK, stroke_width=4).move_to([0, -1.2, 0])
            ball = Dot([-0.6, -0.7, 0], color=ACCENT, radius=0.13)
            return VGroup(hill, ball, Text("rolls back", font=FONT, font_size=28, color=INK).move_to([0, -2.7, 0]))
        if bid == "H02":
            bar = Rectangle(width=0.5, height=1.5, color=INK, fill_color=ACCENT, fill_opacity=0.18, stroke_width=4).move_to([0, -1.0, 0])
            dot = Dot([1.3, -1.0, 0], color=ACCENT, radius=0.14)
            return VGroup(bar, dot, Text("already across", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        return None

    def _A01_A03(self):
        # A01
        t1 = dur("A01")
        base = baseline()
        bar = barrier(cx=1.3, w=1.6)          # spans x 0.5 .. 2.1
        incident = wave_osc(-6.0, 0.5, 1.0)
        self.play(Create(base), run_time=t1 * 0.25)
        self.play(Create(bar), Create(incident), run_time=t1 * 0.6)
        self.wait(max(0.1, t1 * 0.15))

        # A02 — classically must stop; wave doesn't cut off
        t2 = dur("A02")
        stop = Line([0.5, -1.4, 0], [0.5, 1.4, 0], color=RED, stroke_width=5)
        slabel = Text("can't cross", font=FONT, font_size=26, color=RED).next_to(bar, UP, buff=0.2)
        self.play(Create(stop), FadeIn(slabel), run_time=t2 * 0.55)
        self.wait(max(0.1, t2 * 0.45))
        self.play(FadeOut(stop, slabel), run_time=0.01)

        # A03 — decay inside
        t3 = dur("A03")
        decay = decay_curve(0.5, 2.1, 1.0, 0.9)
        dlabel = Text("decays, doesn't oscillate", font=FONT, font_size=24, color=ACCENT).next_to([1.3, -1.3, 0], DOWN, buff=0.1)
        self.play(Create(decay), FadeIn(dlabel), run_time=t3 * 0.75)
        self.wait(max(0.2, t3 * 0.25))

    # ── A04–A08 — thick fails, thin transmits ─────────────────────────────────
    def _A04_A08(self):
        base = baseline()
        incident = wave_osc(-6.0, 0.0, 1.0)

        # A04 — thick barrier, decay to ~zero
        t4 = dur("A04")
        thick = barrier(cx=1.5, w=3.0)        # x 0 .. 3
        d_thick = decay_curve(0.0, 3.0, 1.0, 1.05)
        lbl4 = Text("thick: nothing gets through", font=FONT, font_size=26, color=INK).move_to([0, 2.9, 0])
        self.play(Create(base), Create(incident), run_time=t4 * 0.35)
        self.play(Create(thick), Create(d_thick), FadeIn(lbl4), run_time=t4 * 0.5)
        self.wait(max(0.1, t4 * 0.15))

        # A05 — narrow it; leftover amplitude
        t5 = dur("A05")
        thin = barrier(cx=0.5, w=1.0)         # x 0 .. 1
        d_thin = decay_curve(0.0, 1.0, 1.0, 1.05)
        lbl5 = Text("thin: leftover at the edge", font=FONT, font_size=26, color=INK).move_to([0, 2.9, 0])
        self.play(Transform(thick, thin), Transform(d_thick, d_thin),
                  Transform(lbl4, lbl5), run_time=t5 * 0.7)
        self.wait(max(0.2, t5 * 0.3))

        # A06 — transmitted wave relaunches
        t6 = dur("A06")
        amp_t = float(np.exp(-1.05 * 1.0))    # leftover ≈ 0.35
        trans = wave_osc(1.0, 5.8, amp_t)
        self.play(Create(trans), run_time=t6 * 0.8)
        self.wait(max(0.1, t6 * 0.2))

        # A07 — small but real chance
        t7 = dur("A07")
        chance = Text("small but real chance", font=FONT, font_size=26, color=ACCENT).next_to(trans, UP, buff=0.2).shift(RIGHT * 0.5)
        self.play(FadeIn(chance), Indicate(trans, color=ACCENT), run_time=t7 * 0.7)
        self.wait(max(0.2, t7 * 0.3))

        # A08 — tunneled through, not over
        t8 = dur("A08")
        self.play(FadeOut(lbl4, chance), run_time=t8 * 0.2)
        final = Text("tunneled through, not over", font=FONT, font_size=30, color=INK).move_to([0, 2.9, 0])
        self.play(Write(final), run_time=t8 * 0.6)
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
