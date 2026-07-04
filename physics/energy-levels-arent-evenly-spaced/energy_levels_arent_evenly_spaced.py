"""
energy_levels_arent_evenly_spaced.py
====================================
Bear's Notes — "Why Quantum Energy Levels Aren't Evenly Spaced"
Quantum Mechanics Vol. 1, Ch. 5 (Candidate 12).

Dual-orientation, layout-engine driven (bn_layout). The SAME scene renders 16:9
OR 9:16; portrait positions are RECOMPUTED from the content band so content fills
the frame instead of floating.
  • Landscape (16:9): box LEFT, energy ladder RIGHT (side by side).
  • Portrait  (9:16): box fills the TOP band, ladder fills the BOTTOM band (stacked),
    running captions in the seam, channel/outro kept out of the bottom UI zone.
Same audio for both (assemble muxes mp3/). SILENT scene.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim -qh energy_levels_arent_evenly_spaced.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/assemble.py . --mode manim
    manim -qh -r 1080,1920 energy_levels_arent_evenly_spaced.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/manim_layout_audit.py energy_levels_arent_evenly_spaced.py --png
    python ../../bears-doodles/scripts/assemble.py . --mode manim --portrait
"""
import json
from pathlib import Path

import numpy as np
from manim import *

import bn_layout as BL
from bn_layout import is_portrait, band, rows, fit, fit_width, fit_text, rw, rh, rcx, rcy, safe_w, safe_h

HERE = Path(__file__).resolve().parent

INK     = "#1a1a1a"
ACCENT  = "#5A5653"
RED     = "#C0392B"
GHOST   = "#C9BFBC"
FONT    = "Shadows Into Light"
TITLE   = "Why Quantum Energy Levels Aren't Evenly Spaced"
CHANNEL = "youtube.com/@NikBearBrown"

# ── landscape layout constants (unchanged, approved 16:9) ────────────────────
LANDSCAPE = dict(
    lx0=-5.4, lx1=-1.8, yc=0.0, amp=0.85, wlo=-1.8, whi=1.8,
    ax=1.2, rx=4.8, e0=-2.0, k=0.275, val_dx=0.5, val_fs=26,
    axis_y0=-2.3, axis_y1=2.7, energy_fs=24,
    nlbl_y=2.3, nlbl_fs=26,
    cap_x=0.0, cap_y=3.0, cap_w=11.0, cap_fs=26,
    punch_x=0.0, punch_y=-3.05, punch_fs=30,
    gx=0.7, gap_lab_dx=-0.45, gap_fs=22,
)

L: dict = {}


def _portrait_L():
    """Derive the portrait layout from the content band so panels FILL it."""
    b = band()
    box_r, lad_r = rows(b, [0.92, 1.08], gap=0.5)   # box on top, ladder below
    seam_cy = (box_r[1] + lad_r[3]) / 2.0
    # box panel fills the top band, full width
    lx_half = rw(box_r) * 0.5 * 0.88
    wlo, whi = box_r[1] + 0.10, box_r[3] - 0.12
    yc = (wlo + whi) / 2.0
    amp = (whi - wlo) / 2.0 * 0.52
    # ladder fills the bottom band; axis near left, rungs ~72% across
    ax = lad_r[0] + 0.40
    rx = ax + rw(lad_r) * 0.70
    axis_y0, axis_y1 = lad_r[1] + 0.08, lad_r[3] - 0.05
    h1, h4 = axis_y0 + 0.16, axis_y1 - 0.12          # n=1 low, n=4 high → fill height
    k = (h4 - h1) / 15.0
    e0 = h1 - k
    return dict(
        lx0=-lx_half, lx1=lx_half, yc=yc, amp=amp, wlo=wlo, whi=whi,
        ax=ax, rx=rx, e0=e0, k=k, val_dx=0.34, val_fs=18,
        axis_y0=axis_y0, axis_y1=axis_y1, energy_fs=18,
        nlbl_y=whi - 0.10, nlbl_fs=22,
        cap_x=0.0, cap_y=seam_cy, cap_w=rw(b) * 0.96, cap_fs=21,
        punch_x=0.0, punch_y=seam_cy, punch_fs=22,
        gx=ax + 0.42, gap_lab_dx=0.22, gap_fs=16,
    )


def XCL():  return (L["lx0"] + L["lx1"]) / 2.0
def WL():   return L["lx1"] - L["lx0"]
def h(n):   return L["e0"] + L["k"] * n * n


def wave_n(n):
    return ParametricFunction(
        lambda x: [x, L["yc"] + L["amp"] * np.sin(n * np.pi * (x - L["lx0"]) / WL()), 0],
        t_range=[L["lx0"], L["lx1"], 0.01], color=ACCENT, stroke_width=5)


def box_walls():
    left = Line([L["lx0"], L["wlo"], 0], [L["lx0"], L["whi"], 0], color=INK, stroke_width=7)
    right = Line([L["lx1"], L["wlo"], 0], [L["lx1"], L["whi"], 0], color=INK, stroke_width=7)
    bl = DashedLine([L["lx0"], L["yc"], 0], [L["lx1"], L["yc"], 0], color=GHOST, stroke_width=2)
    return VGroup(left, right, bl)


def rung(n):
    y = h(n)
    line = DashedLine([L["ax"], y, 0], [L["rx"], y, 0], color=ACCENT, stroke_width=4)
    dot = Dot([L["ax"], y, 0], color=ACCENT, radius=0.07)
    return VGroup(line, dot)


def val(n):
    return Text(str(n * n), font=FONT, font_size=L["val_fs"], color=INK).move_to([L["rx"] + L["val_dx"], h(n), 0])


_bsp = HERE / "beat_sheet.json"
_BS = json.loads(_bsp.read_text()) if _bsp.exists() else {}
_NARR = {b["beat_id"]: b.get("narration_text", "") for b in _BS.get("beats", [])}
_DEEP_TEX = _BS.get("metadata", {}).get("deep_teaser_tex")   # set when a deep version exists

_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {"A01": 4.0, "A02": 4.0, "A03": 5.0, "A04": 4.5, "A05": 5.0, "A06": 5.0,
       "A07": 5.5, "A08": 4.5, "INTRO": 5.0, "H01": 5.0, "H02": 4.5, "OUTRO": 9.0}


def dur(b):
    return float(_T.get(b, _FB.get(b, 5.0)))


class BearsDoodlesVideo(Scene):
    def construct(self):
        global L
        port = is_portrait()
        import sys
        print(f"[bn_layout] mode={'PORTRAIT (stacked)' if port else 'LANDSCAPE (side-by-side)'} "
              f"pixels={config.pixel_width}x{config.pixel_height} frame={config.frame_width:.2f}x{config.frame_height:.2f}",
              file=sys.stderr)
        L = _portrait_L() if port else LANDSCAPE
        self.camera.background_color = WHITE
        self._intro_card()
        self._hook("H01", "[ even ladder? ]")
        self._hook("H02", "[ rungs fan apart ]")
        self._ladder_scene()
        self._outro_card()

    # ── intro ─────────────────────────────────────────────────────────────────
    def _intro_hero(self):
        ys = [-0.7, -0.2, 0.7]
        return VGroup(*[Line([-1.3, y, 0], [1.3, y, 0], color=ACCENT, stroke_width=5) for y in ys])

    def _intro_card(self):
        t = dur("INTRO")
        if is_portrait():
            brow, hrow, trow = rows(band(), [0.20, 0.48, 0.32], gap=0.25)
            brand = fit(Text("Bear's Notes", font=FONT, font_size=44, color=INK), brow, 0.82)
            hero = fit(self._intro_hero(), hrow, 0.8)
            title = fit(fit_text(TITLE, FONT, 30, ACCENT, rw(trow) * 0.96), trow, 0.98)
        else:
            sh, tw = safe_h(), 2 * safe_w() * 0.95
            brand = Text("Bear's Notes", font=FONT, font_size=44, color=INK).move_to([0, sh - 0.35, 0])
            hero = self._intro_hero().move_to([0, sh * 0.12, 0])
            title = fit_text(TITLE, FONT, 32, ACCENT, tw).move_to([0, -(sh - 0.7), 0])
        r1, r2, r3 = min(0.9, t * 0.22), min(1.6, t * 0.4), min(1.3, t * 0.28)
        self.play(FadeIn(brand), run_time=r1)
        self.play(Create(hero), run_time=r2)
        self.play(Write(title), run_time=r3)
        self.wait(max(0.2, t - r1 - r2 - r3 - 0.4))
        self.play(FadeOut(brand, hero, title), run_time=0.4)

    # ── hooks ───────────────────────────────────────────────────────────────────
    def _hook(self, bid, label):
        t = dur(bid)
        if is_portrait():
            card_r, sketch_r = rows(band(), [0.34, 0.66], gap=0.3)
            card = fit(fit_text(_NARR.get(bid, label), FONT, 34, INK, rw(card_r) * 0.96), card_r, 0.96)
            sketch = self._hook_sketch(bid, with_label=False)   # card carries the words
            if sketch is not None:
                fit(sketch, sketch_r, 0.80)
        else:
            tw = 2 * safe_w() * 0.92
            card = fit_text(_NARR.get(bid, label), FONT, 34, INK, tw).to_edge(UP, buff=0.8)
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

    def _hook_sketch(self, bid, with_label=True):
        if bid == "H01":
            rungs = VGroup(*[Line([-1.4, y, 0], [1.4, y, 0], color=ACCENT, stroke_width=5)
                             for y in (-1.9, -1.4, -0.9, -0.4)])
            if not with_label:
                return rungs
            return VGroup(rungs, Text("evenly spaced?", font=FONT, font_size=28, color=INK).move_to([0, -2.5, 0]))
        if bid == "H02":
            rungs = VGroup(*[Line([-1.4, y, 0], [1.4, y, 0], color=ACCENT, stroke_width=5)
                             for y in (-1.9, -1.5, -0.8, 0.4)])
            if not with_label:
                return rungs
            return VGroup(rungs, Text("fanning apart", font=FONT, font_size=28, color=INK).move_to([0, -2.6, 0]))
        return None

    # ── main scene ──────────────────────────────────────────────────────────────
    def _cap_text(self, s, color):
        c = Text(s, font=FONT, font_size=L["cap_fs"], color=color).move_to([L["cap_x"], L["cap_y"], 0])
        if c.width > L["cap_w"]:
            c.scale_to_fit_width(L["cap_w"])
        return c

    def _nlbl(self, n):
        return Text(f"n = {n}", font=FONT, font_size=L["nlbl_fs"], color=INK).move_to([XCL(), L["nlbl_y"], 0])

    def _energy_label(self, axis):
        lbl = Text("energy", font=FONT, font_size=L["energy_fs"], color=INK)
        if is_portrait():
            lbl.rotate(PI / 2).move_to([L["ax"] - 0.30, (L["axis_y0"] + L["axis_y1"]) / 2.0, 0])
        else:
            lbl.next_to(axis, UP, buff=0.12)
        return lbl

    def _ladder_scene(self):
        t1 = dur("A01")
        box = box_walls()
        axis = Arrow([L["ax"], L["axis_y0"], 0], [L["ax"], L["axis_y1"], 0], buff=0, color=INK, stroke_width=4)
        elabel = self._energy_label(axis)
        self.play(Create(box), run_time=t1 * 0.5)
        self.play(GrowArrow(axis), FadeIn(elabel), run_time=t1 * 0.5)

        t2 = dur("A02")
        wave = wave_n(1)
        nlbl = self._nlbl(1)
        r1, v1 = rung(1), val(1)
        self.play(Create(wave), FadeIn(nlbl), run_time=t2 * 0.6)
        self.play(Create(r1), FadeIn(v1), run_time=t2 * 0.4)

        t3 = dur("A03")
        r2, v2 = rung(2), val(2)
        self.play(Transform(wave, wave_n(2)), Transform(nlbl, self._nlbl(2)), run_time=t3 * 0.5)
        self.play(Create(r2), FadeIn(v2), run_time=t3 * 0.5)

        t4 = dur("A04")
        r3, v3 = rung(3), val(3)
        self.play(Transform(wave, wave_n(3)), Transform(nlbl, self._nlbl(3)),
                  Create(r3), FadeIn(v3), run_time=t4 * 0.5)
        r4, v4 = rung(4), val(4)
        self.play(Transform(wave, wave_n(4)), Transform(nlbl, self._nlbl(4)),
                  Create(r4), FadeIn(v4), run_time=t4 * 0.5)

        t5 = dur("A05")
        gx = L["gx"]
        gaps = VGroup()
        for (na, nb, g) in [(1, 2, "3"), (2, 3, "5"), (3, 4, "7")]:
            arr = DoubleArrow([gx, h(na), 0], [gx, h(nb), 0], buff=0, color=RED,
                              stroke_width=3, tip_length=0.14)
            lab = Text(g, font=FONT, font_size=L["gap_fs"], color=RED).move_to([gx + L["gap_lab_dx"], (h(na) + h(nb)) / 2, 0])
            gaps.add(arr, lab)
        cap = self._cap_text("the gaps keep widening", RED)
        self.play(LaggedStart(*[GrowArrow(m) for m in gaps if isinstance(m, DoubleArrow)], lag_ratio=0.2),
                  *[FadeIn(m) for m in gaps if not isinstance(m, DoubleArrow)],
                  FadeIn(cap), run_time=t5 * 0.8)
        self.wait(max(0.2, t5 * 0.2))
        self._cap = cap

        t6 = dur("A06")
        self.play(Transform(self._cap, self._cap_text("each step shrinks the wavelength", ACCENT)),
                  Indicate(wave, color=ACCENT, scale_factor=1.04), run_time=t6 * 0.7)
        self.wait(max(0.2, t6 * 0.3))

        t7 = dur("A07")
        self.play(Transform(self._cap, self._cap_text("energy grows with the square of the count", ACCENT)),
                  Indicate(VGroup(r1, r4), color=ACCENT, scale_factor=1.02), run_time=t7 * 0.7)
        self.wait(max(0.2, t7 * 0.3))

        # A08 punchline. Landscape: bottom band. Portrait: ladder fills the bottom,
        # so fade the running caption and place the punchline in the seam.
        t8 = dur("A08")
        if is_portrait():
            self.play(FadeOut(self._cap), run_time=min(0.5, t8 * 0.2))
        red = Text("energy grows as n squared", font=FONT, font_size=L["punch_fs"], color=RED).move_to([L["punch_x"], L["punch_y"], 0])
        if red.width > 2 * safe_w() * 0.95:
            red.scale_to_fit_width(2 * safe_w() * 0.95)
        self.play(Write(red), run_time=t8 * 0.6)
        self.wait(max(0.2, t8 * 0.2))

    # ── outro (separate cleared card) ─────────────────────────────────────────
    def _outro_card(self):
        # Tier-aware: if a deep version exists (_DEEP_TEX set in metadata), the outro
        # points to "the full worked example" + flashes its hero equation instead of
        # just repeating the title. Otherwise the standard title outro.
        BL.outro(self, TITLE, CHANNEL, dur("OUTRO"), teaser_tex=_DEEP_TEX,
                 font=FONT, ink=INK, accent=ACCENT)
