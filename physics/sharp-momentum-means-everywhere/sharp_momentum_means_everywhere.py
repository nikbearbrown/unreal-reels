"""
sharp_momentum_means_everywhere.py
==================================
Bear's Notes — "Why a Sharp-Momentum Particle Must Be Everywhere at Once"
Quantum Mechanics Vol. 1, Ch. 8 (Candidate 17).

9 MANIM beats (A01-A08), SILENT 16:9, one continuous ACCUMULATE scene. A single
exact momentum is one endless constant-amplitude wave (flat probability everywhere,
can't be normalized). Adding more nearby momenta (a growing dot-spectrum) makes the
summed wave reinforce in one spot and cancel elsewhere — a localized packet. The sum
is normalized by the number of terms, so the centre height stays fixed while the
edges collapse. Stroke-on Transform (a touch slower than pure stroke-on due to dense
sampling). INTRO + two hooks are placeholder markers. assemble.py muxes the voiceover.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim --flush_cache --disable_caching -qh sharp_momentum_means_everywhere.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
"""
import json
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"     # the wave / packet
RED     = "#C0392B"     # the 'everywhere' probability + emphasis
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why a Sharp-Momentum Particle Must Be Everywhere at Once"
CHANNEL = "youtube.com/@NikBearBrown"

SAFE_W, SAFE_H = 6.3, 3.4
MARK = (0.0, 0.0, 1.4, 1.9)

K0 = 6.0
DK = 0.45
WB = 0.5                 # wave baseline
AMP = 1.3
XR = 6.0                 # plot half-range
PY = -2.1                # probability baseline

# mini momentum spectrum (top-left)
KXL, KXR = -5.7, -2.7
KAY = 2.5


def xk(k):
    return KXL + (KXR - KXL) * (k - (K0 - 2)) / 4.0

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.5, "A02": 5.5, "A03": 4.0, "A04": 4.5, "A05": 4.5, "A06": 5.0,
       "A07": 4.5, "A08": 5.0, "INTRO": 5.5, "H01": 5.0, "H02": 4.5, "OUTRO": 9.5}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


def ks(M):
    return [K0 + (i - (M - 1) / 2) * DK for i in range(M)]


def Ssum(x, M):
    return sum(np.cos(k * x) for k in ks(M)) / M


def wave(M):
    return ParametricFunction(lambda x: [x, WB + AMP * Ssum(x, M), 0],
                              t_range=[-XR, XR, 0.008], color=ACCENT, stroke_width=4)


def make_dots(M):
    return VGroup(*[Dot([xk(k), KAY, 0], color=INK, radius=0.07) for k in ks(M)])


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
        self._hook("H01", "[ doodle: one momentum arrow ]")
        self._hook("H02", "[ doodle: smeared everywhere ]")
        self._fourier_scene()
        self._outro_card()

    # ── cards ────────────────────────────────────────────────────────────────
    def _marker(self):
        cx, cy, w, h = MARK
        return DashedVMobject(Rectangle(width=w, height=h, color=GHOST, stroke_width=3)
                              .move_to([cx, cy, 0]), num_dashes=24)

    def _intro_card(self):
        # Infographic title card: brand + the video's hero Manim graphic + title.
        t = dur("INTRO")
        brand = Text("Bear's Notes", font=FONT, font_size=44, color=INK).move_to([0, 3.0, 0])
        hero = wave(9).set_stroke(width=5).scale(0.72).move_to([0, 0.5, 0])   # the signature packet
        title = Text(TITLE, font=FONT, font_size=30, color=ACCENT)
        title.scale_to_fit_width(min(11.5, title.width)).move_to([0, -2.5, 0])
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
        # a small topic-relevant Manim drawing beside the hook text (not just text)
        if bid == "H01":            # one exact momentum -> a single clean arrow
            arr = Arrow([-2.4, -0.9, 0], [2.4, -0.9, 0], color=ACCENT, buff=0, stroke_width=7)
            lab = Text("one exact momentum", font=FONT, font_size=30, color=INK).next_to(arr, DOWN, buff=0.3)
            return VGroup(arr, lab)
        if bid == "H02":            # wave fills all space -> an endless flat wave
            w = ParametricFunction(lambda x: [x, -0.9 + 0.45 * np.sin(3.2 * x), 0],
                                   t_range=[-6.0, 6.0, 0.02], color=ACCENT, stroke_width=5)
            lab = Text("everywhere at once", font=FONT, font_size=28, color=RED).move_to([0, -2.5, 0])
            return VGroup(w, lab)
        return None
    def _say(self, txt, color=INK):
        return Text(txt, font=FONT, font_size=26, color=color).move_to([0, 3.05, 0])

    # ── A01–A08 ───────────────────────────────────────────────────────────────
    def _fourier_scene(self):
        # mini momentum spectrum frame
        kaxis = Line([KXL - 0.2, KAY, 0], [KXR + 0.2, KAY, 0], color=INK, stroke_width=2)
        klbl = Text("momenta", font=FONT, font_size=20, color=INK).next_to(kaxis, LEFT, buff=0.2)

        # A01 — single endless wave
        t1 = dur("A01")
        self.wave = wave(1)
        self.dots = make_dots(1)
        cap = self._say("one momentum: one endless wave", ACCENT)
        self.play(Create(kaxis), FadeIn(klbl), run_time=t1 * 0.25)
        self.play(Create(self.wave), FadeIn(self.dots), FadeIn(cap), run_time=t1 * 0.75)
        self._cap = cap

        # A02 — flat probability everywhere
        t2 = dur("A02")
        flat = DashedLine([-XR, PY, 0], [XR, PY, 0], color=RED, stroke_width=5)
        flbl = Text("same everywhere — can't be normalized", font=FONT, font_size=24, color=RED).move_to([0, PY - 0.55, 0])
        cap2 = self._say("nowhere in particular", RED)
        self.play(Create(flat), FadeIn(flbl), Transform(self._cap, cap2), run_time=t2 * 0.8)
        self.wait(max(0.2, t2 * 0.2))

        # A03 — clear, prepare to add momenta
        t3 = dur("A03")
        cap3 = self._say("to localize it, add nearby momenta", INK)
        self.play(FadeOut(flat, flbl), Transform(self._cap, cap3), run_time=t3 * 0.8)

        # A04 — three momenta
        t4 = dur("A04")
        nd = make_dots(3)
        cap4 = self._say("a few neighbors: it starts to bunch", INK)
        self.play(Transform(self.wave, wave(3)), FadeOut(self.dots), FadeIn(nd),
                  Transform(self._cap, cap4), run_time=t4)
        self.dots = nd

        # A05 — six momenta
        t5 = dur("A05")
        nd = make_dots(6)
        cap5 = self._say("more momenta, sharper middle", INK)
        self.play(Transform(self.wave, wave(6)), FadeOut(self.dots), FadeIn(nd),
                  Transform(self._cap, cap5), run_time=t5)
        self.dots = nd

        # A06 — many momenta -> localized packet
        t6 = dur("A06")
        nd = make_dots(11)
        cap6 = self._say("many momenta: a single blob", ACCENT)
        self.play(Transform(self.wave, wave(11)), FadeOut(self.dots), FadeIn(nd),
                  Transform(self._cap, cap6), run_time=t6)
        self.dots = nd

        # A07 — probability bump (one place)
        t7 = dur("A07")
        bump = ParametricFunction(lambda x: [x, PY + 1.25 * np.exp(-(x / 0.9) ** 2), 0],
                                  t_range=[-XR, XR, 0.02], color=ACCENT, stroke_width=4)
        blbl = Text("one place", font=FONT, font_size=24, color=ACCENT).move_to([2.0, PY + 0.9, 0])
        cap7 = self._say("the particle is finally somewhere", ACCENT)
        self.play(Create(bump), FadeIn(blbl), Transform(self._cap, cap7), run_time=t7 * 0.8)
        self.wait(max(0.2, t7 * 0.2))

        # A08 — punchline
        t8 = dur("A08")
        self.play(FadeOut(self._cap), run_time=t8 * 0.2)
        red = Text("one momentum: everywhere — a place needs many", font=FONT, font_size=26, color=RED).move_to([0, -3.05, 0])
        self.play(Write(red), run_time=t8 * 0.6)
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
