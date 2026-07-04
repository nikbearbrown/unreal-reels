"""Schrödinger's cat is a reductio ad absurdum, not a physics claim — Bear's Doodles"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))

import numpy as np
from manim import *
from bn_bio import (BioScene, INK, ACCENT, FORBID, GHOST, OKABE, FONT,
                    particle, arrow, darrow, tag, labeled, cross_out, check,
                    dna_helix, cell, brace_label)
from bn_layout import rcx, rcy, rw, rh, center, fit, is_portrait


class BearsDoodlesVideo(BioScene):

    def intro_hero(self):
        """Box with a question mark — the famous sealed-box image."""
        box = Rectangle(width=1.4, height=1.4, color=INK, stroke_width=4)
        qmark = Text("?", font=FONT, font_size=52, color=ACCENT)
        return VGroup(box, qmark)

    # ── A00: the sealed box + cat ────────────────────────────────────────────
    def beat_A00(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.box = Rectangle(width=1.5, height=1.5, color=INK, stroke_width=4)\
            .set_fill(GHOST, opacity=0.15).move_to([cx - 3.0, cy, 0])
        self.cat = Circle(radius=0.3, color=OKABE["orange"], stroke_width=3)\
            .set_fill(OKABE["orange"], opacity=0.35).move_to([cx - 3.0, cy, 0])
        exp_lab = tag("Schrödinger's thought experiment", (cx - 3.0, cy - 1.1), fs=18, color=INK)
        self.play(Create(self.box), run_time=t * 0.35)
        self.play(GrowFromCenter(self.cat), run_time=t * 0.3)
        self.play(FadeIn(exp_lab), run_time=t * 0.2)
        self.exp_lab = exp_lab

    # ── A01: radioactive trigger inside box ──────────────────────────────────
    def beat_A01(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.trigger = Dot([cx - 3.5, cy + 0.45, 0], radius=0.15, color=FORBID)\
            .set_fill(FORBID, opacity=0.8)
        trig_lab = tag("quantum trigger", (cx - 3.0, cy + 0.95), fs=18, color=FORBID)
        self.play(FadeIn(self.trigger), run_time=t * 0.4)
        self.play(FadeIn(trig_lab), run_time=t * 0.3)
        self.trig_lab = trig_lab

    # ── A02: classical OR — two separate outcome boxes ───────────────────────
    def beat_A02(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        # "Alive" box
        box_alive = Rectangle(width=0.9, height=0.7, color=OKABE["green"], stroke_width=3)\
            .set_fill(OKABE["green"], opacity=0.1).move_to([cx, cy + 0.5, 0])
        dot_alive = Circle(radius=0.18, color=OKABE["green"], stroke_width=2)\
            .set_fill(OKABE["green"], opacity=0.5).move_to([cx, cy + 0.5, 0])
        # "Dead" box
        box_dead = Rectangle(width=0.9, height=0.7, color=FORBID, stroke_width=3)\
            .set_fill(FORBID, opacity=0.1).move_to([cx, cy - 0.2, 0])
        dead_x = cross_out(box_dead, color=FORBID, sw=4)
        or_lab = tag("classical: OR", (cx, cy - 0.8), fs=20, color=INK)
        self.classical_boxes = VGroup(box_alive, dot_alive, box_dead, dead_x)
        self.play(Create(box_alive), FadeIn(dot_alive), run_time=t * 0.3)
        self.play(Create(box_dead), Create(dead_x), run_time=t * 0.3)
        self.play(FadeIn(or_lab), run_time=t * 0.2)
        self.or_lab = or_lab

    # ── A03: quantum AND — superposition box ─────────────────────────────────
    def beat_A03(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        q_box = Rectangle(width=1.1, height=1.1, color=ACCENT, stroke_width=3)\
            .set_fill(ACCENT, opacity=0.08).move_to([cx + 2.5, cy + 0.15, 0])
        q_alive = Circle(radius=0.25, color=OKABE["green"], stroke_width=2)\
            .set_fill(OKABE["green"], opacity=0.4).move_to([cx + 2.3, cy + 0.25, 0])
        q_dead = Circle(radius=0.25, color=FORBID, stroke_width=2)\
            .set_fill(FORBID, opacity=0.4).move_to([cx + 2.7, cy + 0.05, 0])
        sup_lab = tag("quantum: AND", (cx + 2.5, cy - 0.6), fs=20, color=ACCENT)
        sup_lab2 = tag("(superposition)", (cx + 2.5, cy - 0.95), fs=17, color=ACCENT)
        self.quantum_box = VGroup(q_box, q_alive, q_dead)
        self.q_alive = q_alive
        self.q_dead = q_dead
        self.play(Create(q_box), run_time=t * 0.3)
        self.play(FadeIn(q_alive), FadeIn(q_dead), run_time=t * 0.3)
        self.play(FadeIn(sup_lab), FadeIn(sup_lab2), run_time=t * 0.25)
        self.sup_lab = sup_lab
        self.sup_lab2 = sup_lab2

    # ── A04: measurement collapses to one outcome ────────────────────────────
    def beat_A04(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        collapse_lab = tag("measurement → collapse", (cx + 2.5, cy + 1.1), fs=18, color=FORBID)
        self.play(FadeOut(self.q_dead), run_time=t * 0.4)
        self.play(FadeIn(collapse_lab), run_time=t * 0.3)
        self.collapse_lab = collapse_lab

    # ── A05: Schrödinger meant absurdity ─────────────────────────────────────
    def beat_A05(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.absurd = Text("ABSURD!", font=FONT, font_size=34, color=FORBID)\
            .move_to([cx - 3.0, cy + 1.3, 0])
        absurd_arrow = Arrow([cx - 3.0, cy + 1.0, 0], [cx - 3.0, cy + 0.82, 0],
                             color=FORBID, buff=0, stroke_width=3, tip_length=0.18)
        absurd_note = tag("Schrödinger meant absurdity", (cx - 3.0, cy - 1.5), fs=18, color=FORBID)
        self.play(FadeIn(self.absurd), run_time=t * 0.35)
        self.play(GrowArrow(absurd_arrow), run_time=t * 0.25)
        self.play(FadeIn(absurd_note), run_time=t * 0.25)
        self.absurd_arrow = absurd_arrow
        self.absurd_note = absurd_note

    # ── A06: electron IS in superposition ────────────────────────────────────
    def beat_A06(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        ex, ey = cx + 4.5, cy + 1.2
        el_main = Dot([ex, ey, 0], radius=0.15, color=OKABE["blue"]).set_fill(OKABE["blue"], opacity=0.9)
        el_sh1 = Dot([ex - 0.22, ey - 0.12, 0], radius=0.10, color=OKABE["blue"]).set_fill(OKABE["blue"], opacity=0.4)
        el_sh2 = Dot([ex + 0.22, ey + 0.12, 0], radius=0.10, color=OKABE["blue"]).set_fill(OKABE["blue"], opacity=0.25)
        el_lab = tag("electron: real\nsuperposition", (ex, ey - 0.55), fs=17, color=OKABE["blue"])
        self.electron_super = VGroup(el_main, el_sh1, el_sh2)
        self.play(FadeIn(el_sh2), FadeIn(el_sh1), FadeIn(el_main), run_time=t * 0.4)
        self.play(FadeIn(el_lab), run_time=t * 0.3)
        self.el_lab = el_lab

    # ── A07: wave function = spread position ─────────────────────────────────
    def beat_A07(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        wave_cx = cx + 3.5
        self.wave_spread = ParametricFunction(
            lambda s: [s, cy - 0.5 + 0.3 * np.sin(4.0 * s), 0],
            t_range=[cx + 1.5, cx + 5.5, 0.04],
            color=OKABE["blue"], stroke_width=4
        )
        wave_lab = tag("wave = spread position", (wave_cx, cy - 1.05), fs=18, color=OKABE["blue"])
        self.play(Create(self.wave_spread), run_time=t * 0.5)
        self.play(FadeIn(wave_lab), run_time=t * 0.25)
        self.wave_lab = wave_lab

    # ── A08: localized = many wavelengths ───────────────────────────────────
    def beat_A08(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.gaussian = ParametricFunction(
            lambda s: [s, cy - 1.55 + 0.55 * np.exp(-8.0 * (s - cx) ** 2), 0],
            t_range=[cx - 1.2, cx + 1.2, 0.02],
            color=OKABE["orange"], stroke_width=4
        )
        # several small wavy lines below to suggest many frequencies
        mini_waves = VGroup(*[
            ParametricFunction(
                lambda s, k=kk: [s, cy - 1.9 + 0.08 * np.sin(k * s), 0],
                t_range=[cx - 1.0, cx + 1.0, 0.03],
                color=GHOST, stroke_width=2
            )
            for kk in (6, 9, 12)
        ])
        gauss_lab = tag("localized = many λ needed", (cx, cy - 2.3), fs=18, color=OKABE["orange"])
        self.play(Create(self.gaussian), run_time=t * 0.4)
        self.play(Create(mini_waves), run_time=t * 0.3)
        self.play(FadeIn(gauss_lab), run_time=t * 0.2)
        self.mini_waves = mini_waves
        self.gauss_lab = gauss_lab

    # ── A09: macroscopic objects: λ ≈ 0 ────────────────────────────────────
    def beat_A09(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.macro_rect = Rectangle(width=1.0, height=0.5, color=GHOST, stroke_width=3)\
            .set_fill(GHOST, opacity=0.25).move_to([cx, cy - 2.35, 0])
        macro_lab = tag("macroscopic: λ ≈ 0", (cx, cy - 2.4), fs=18, color=GHOST)
        # cross out the mini waves to indicate no wave behavior
        wave_x = cross_out(self.mini_waves, color=FORBID, sw=3)
        self.play(Create(self.macro_rect), run_time=t * 0.35)
        self.play(Create(wave_x), run_time=t * 0.3)
        self.play(FadeIn(macro_lab), run_time=t * 0.2)
        self.macro_lab = macro_lab
        self.wave_x = wave_x

    # ── A10: cat wavelength is 10⁻³⁵ m ─────────────────────────────────────
    def beat_A10(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.cat_wave_x_label = tag("cat λ ≈ 10⁻³⁵ m", (cx - 3.0, cy + 1.65), fs=19, color=ACCENT)
        tiny_wave = ParametricFunction(
            lambda s: [s, cy + 0.05 * np.sin(20 * s), 0],
            t_range=[cx - 3.8, cx - 2.2, 0.02],
            color=GHOST, stroke_width=2
        )
        self.cat_wave_x = cross_out(tiny_wave, color=FORBID, sw=3)
        self.play(FadeIn(self.cat_wave_x_label), run_time=t * 0.35)
        self.play(Create(tiny_wave), Create(self.cat_wave_x), run_time=t * 0.4)
        self.tiny_wave = tiny_wave

    # ── A11: double-slit: 1 electron → 1 dot ───────────────────────────────
    def beat_A11(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        sx = cx - 4.0
        # barrier with gap (two rectangles)
        bar_top = Rectangle(width=0.15, height=0.55, color=INK, stroke_width=3)\
            .set_fill(INK, opacity=0.6).move_to([sx, cy + 0.55, 0])
        bar_bot = Rectangle(width=0.15, height=0.55, color=INK, stroke_width=3)\
            .set_fill(INK, opacity=0.6).move_to([sx, cy - 0.55, 0])
        self.slit = VGroup(bar_top, bar_bot)
        # screen on the right
        self.screen = Line([sx + 2.5, cy - 1.0, 0], [sx + 2.5, cy + 1.0, 0],
                           color=INK, stroke_width=4)
        self.single_dot = Dot([sx + 2.5, cy + 0.3, 0], radius=0.09, color=OKABE["blue"])\
            .set_fill(OKABE["blue"], opacity=0.9)
        single_lab = tag("1 electron → 1 dot", (sx + 1.0, cy - 1.35), fs=17, color=OKABE["blue"])
        self.play(Create(self.slit), run_time=t * 0.3)
        self.play(Create(self.screen), run_time=t * 0.25)
        self.play(FadeIn(self.single_dot), run_time=t * 0.2)
        self.play(FadeIn(single_lab), run_time=t * 0.15)
        self.single_lab = single_lab

    # ── A12: many electrons → interference stripes ──────────────────────────
    def beat_A12(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        sx = cx - 4.0
        screen_x = sx + 2.5
        stripe_ys = np.linspace(cy - 0.85, cy + 0.85, 9)
        self.stripes = VGroup(*[
            Dot([screen_x, yy, 0], radius=0.07, color=OKABE["blue"])
            .set_fill(OKABE["blue"], opacity=(0.9 if i % 2 == 0 else 0.15))
            for i, yy in enumerate(stripe_ys)
        ])
        stripe_lab = tag("many electrons →\ninterference stripes", (sx + 1.0, cy - 1.55), fs=16, color=OKABE["blue"])
        self.play(FadeOut(self.single_dot), run_time=0.2)
        self.play(FadeIn(self.stripes), run_time=t * 0.45)
        self.play(FadeIn(stripe_lab), run_time=t * 0.2)
        self.stripe_lab = stripe_lab

    # ── A13: block one slit → no stripes ────────────────────────────────────
    def beat_A13(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        sx = cx - 4.0
        screen_x = sx + 2.5
        # fill in one slit gap
        self.blocked_slit = Rectangle(width=0.16, height=0.28, color=INK, stroke_width=0)\
            .set_fill(INK, opacity=0.9).move_to([sx, cy, 0])
        # single blob replaces stripes
        blob = VGroup(*[
            Dot([screen_x, cy + 0.14 * (i - 2), 0], radius=0.07, color=OKABE["blue"])
            .set_fill(OKABE["blue"], opacity=0.8 - 0.15 * abs(i - 2))
            for i in range(5)
        ])
        no_lab = tag("1 slit → no stripes", (sx + 1.0, cy + 1.3), fs=17, color=INK)
        self.play(FadeIn(self.blocked_slit), run_time=t * 0.3)
        self.play(ReplacementTransform(self.stripes, blob), run_time=t * 0.4)
        self.play(FadeIn(no_lab), run_time=t * 0.2)
        self.blob = blob
        self.no_lab = no_lab

    # ── A14: remove block — wave through both slits ──────────────────────────
    def beat_A14(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        sx = cx - 4.0
        self.play(FadeOut(self.blocked_slit), run_time=0.25)
        arc1 = Arc(radius=0.6, start_angle=-PI / 3, angle=2 * PI / 3,
                   color=OKABE["sky"], stroke_width=3).move_to([sx, cy + 0.28, 0])
        arc2 = Arc(radius=0.6, start_angle=-PI / 3, angle=2 * PI / 3,
                   color=OKABE["sky"], stroke_width=3).move_to([sx, cy - 0.28, 0])
        self.both_slits_wave = VGroup(arc1, arc2)
        wave_lab = tag("wave through both slits", (sx + 1.0, cy + 1.5), fs=17, color=OKABE["sky"])
        self.play(Create(self.both_slits_wave), run_time=t * 0.45)
        self.play(FadeIn(wave_lab), run_time=t * 0.25)
        self.both_lab = wave_lab

    # ── A15: delocalized electrons in solids ─────────────────────────────────
    def beat_A15(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        lx, ly = cx - 4.2, cy - 1.5
        # 3x3 atom lattice
        lattice_dots = VGroup(*[
            Dot([lx + 0.38 * i, ly + 0.38 * j, 0], radius=0.08, color=ACCENT)
            .set_fill(ACCENT, opacity=0.7)
            for i in range(4) for j in range(3)
        ])
        wave_overlay = ParametricFunction(
            lambda s: [lx + s * 1.4, ly + 0.15 * np.sin(8 * s), 0],
            t_range=[0, 1, 0.02],
            color=OKABE["sky"], stroke_width=3
        )
        self.lattice = VGroup(lattice_dots, wave_overlay)
        lat_lab = tag("delocalized electrons\nin solids", (lx + 0.7, ly - 0.55), fs=16, color=ACCENT)
        self.play(Create(lattice_dots), run_time=t * 0.35)
        self.play(Create(wave_overlay), run_time=t * 0.3)
        self.play(FadeIn(lat_lab), run_time=t * 0.2)
        self.lat_lab = lat_lab

    # ── A16: molecular orbital ───────────────────────────────────────────────
    def beat_A16(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        ox, oy = cx - 1.5, cy - 1.5
        dotA = Dot([ox - 0.3, oy, 0], radius=0.12, color=OKABE["blue"]).set_fill(OKABE["blue"], opacity=0.7)
        dotB = Dot([ox + 0.3, oy, 0], radius=0.12, color=OKABE["blue"]).set_fill(OKABE["blue"], opacity=0.7)
        orb = Ellipse(width=1.0, height=0.55, color=OKABE["sky"], stroke_width=3)\
            .set_fill(OKABE["sky"], opacity=0.2).move_to([ox, oy, 0])
        self.mol_orbital = VGroup(orb, dotA, dotB)
        mol_lab = tag("molecular orbital", (ox, oy - 0.55), fs=17, color=OKABE["sky"])
        self.play(Create(orb), run_time=t * 0.3)
        self.play(FadeIn(dotA), FadeIn(dotB), run_time=t * 0.3)
        self.play(FadeIn(mol_lab), run_time=t * 0.2)
        self.mol_lab = mol_lab

    # ── A17: energy bands ────────────────────────────────────────────────────
    def beat_A17(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        bx, by = cx + 2.0, cy - 0.8
        self.band_val = Rectangle(width=2.0, height=0.42, color=OKABE["blue"], stroke_width=3)\
            .set_fill(OKABE["blue"], opacity=0.35).move_to([bx, by, 0])
        self.band_cond = Rectangle(width=2.0, height=0.42, color=OKABE["orange"], stroke_width=3)\
            .set_fill(OKABE["orange"], opacity=0.35).move_to([bx, by + 0.82, 0])
        self.bands = VGroup(self.band_val, self.band_cond)
        band_lab = tag("energy bands", (bx, by + 1.4), fs=18, color=INK)
        self.play(Create(self.band_val), run_time=t * 0.3)
        self.play(Create(self.band_cond), run_time=t * 0.3)
        self.play(FadeIn(band_lab), run_time=t * 0.2)
        self.band_lab = band_lab

    # ── A18: band gap ────────────────────────────────────────────────────────
    def beat_A18(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        bx, by = cx + 2.0, cy - 0.8
        # gap arrow between the two bands
        gap_arr = darrow([bx + 1.2, by + 0.21, 0], [bx + 1.2, by + 0.61, 0],
                         color=FORBID, sw=3)
        self.band_gap = gap_arr
        gap_lab = tag("band gap →\nsemiconductor", (bx + 2.4, by + 0.4), fs=16, color=FORBID)
        self.play(Create(gap_arr), run_time=t * 0.4)
        self.play(FadeIn(gap_lab), run_time=t * 0.3)
        self.gap_lab = gap_lab

    # ── A19: chip ────────────────────────────────────────────────────────────
    def beat_A19(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        chip_x, chip_y = cx + 4.8, cy - 0.15
        chip_rects = VGroup(*[
            Rectangle(width=0.18, height=0.18, color=ACCENT, stroke_width=2)
            .set_fill(ACCENT, opacity=0.3)
            .move_to([chip_x + 0.22 * (i % 3), chip_y + 0.22 * (i // 3), 0])
            for i in range(9)
        ])
        chip_border = Rectangle(width=0.85, height=0.85, color=INK, stroke_width=3)\
            .set_fill(GHOST, opacity=0.12).move_to([chip_x + 0.22, chip_y + 0.22, 0])
        self.chip = VGroup(chip_border, chip_rects)
        chip_arr = Arrow([chip_x + 0.65, chip_y + 0.22, 0], [chip_x + 1.2, chip_y + 0.22, 0],
                         color=INK, buff=0, stroke_width=3, tip_length=0.16)
        chip_lab = tag("chip → device", (chip_x + 0.22, chip_y - 0.65), fs=17, color=INK)
        self.play(Create(chip_border), Create(chip_rects), run_time=t * 0.4)
        self.play(GrowArrow(chip_arr), run_time=t * 0.25)
        self.play(FadeIn(chip_lab), run_time=t * 0.2)
        self.chip_arr = chip_arr
        self.chip_lab = chip_lab

    # ── A20: check — cat → quantum → chip → video ────────────────────────────
    def beat_A20(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.final_check = check((cx + 5.5, cy + 1.6), color=OKABE["green"], s=0.32)
        final_lab = tag("cat → quantum → chip → video", (cx + 3.2, cy + 2.0), fs=18, color=OKABE["green"])
        self.play(Indicate(self.chip, color=ACCENT, scale_factor=1.08), run_time=t * 0.35)
        self.play(Create(self.final_check), run_time=t * 0.3)
        self.play(FadeIn(final_lab), run_time=t * 0.25)
        self.final_lab = final_lab
