"""Laser cavity: stimulated emission and photon coherence — Bear's Doodles"""
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
        """Four parallel photon arrows for the title card."""
        return VGroup(*[
            Arrow([-2.0, y, 0], [2.0, y, 0], color=OKABE["yellow"],
                  buff=0, stroke_width=4, tip_length=0.22)
            for y in (0.45, 0.15, -0.15, -0.45)
        ])

    # ── A00: five excited atoms ──────────────────────────────────────────────
    def beat_A00(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        xs = np.linspace(cx - 3.0, cx + 3.0, 5)
        self.atoms = VGroup(*[
            Circle(radius=0.25, color=OKABE["blue"], stroke_width=3)
            .set_fill(OKABE["blue"], opacity=0.3)
            .move_to([x, atom_y, 0])
            for x in xs
        ])
        self.pump_arrows = VGroup(*[
            Arrow([x, atom_y - 0.5, 0], [x, atom_y - 0.28, 0],
                  color=OKABE["orange"], buff=0, stroke_width=3, tip_length=0.16)
            for x in xs
        ])
        pump_lab = tag("excited atoms", (cx, atom_y + 0.55), fs=22, color=OKABE["blue"])
        self.play(Create(self.atoms), run_time=t * 0.4)
        self.play(Create(self.pump_arrows), FadeIn(pump_lab), run_time=t * 0.4)
        self.pump_lab = pump_lab

    # ── A01: spontaneous emission from first atom ────────────────────────────
    def beat_A01(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        x0 = cx - 3.0
        self.spontaneous = Arrow(
            [x0, atom_y, 0], [x0 + 1.5, atom_y, 0],
            color=OKABE["yellow"], buff=0.05, stroke_width=4, tip_length=0.22
        )
        spont_lab = tag("spontaneous emission", (cx - 1.8, atom_y - 0.45), fs=20, color=OKABE["yellow"])
        self.play(GrowArrow(self.spontaneous), run_time=t * 0.45)
        self.play(FadeIn(spont_lab), run_time=t * 0.3)
        self.spont_lab = spont_lab

    # ── A02: incoming photon approaching second atom ─────────────────────────
    def beat_A02(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        x1 = cx - 1.5  # second atom position
        self.incoming_photon = Arrow(
            [cx - 4.5, atom_y, 0], [x1 - 0.28, atom_y, 0],
            color=OKABE["yellow"], buff=0, stroke_width=4, tip_length=0.22
        )
        inc_lab = tag("photon arrives", (cx - 3.2, atom_y + 0.42), fs=20, color=OKABE["yellow"])
        self.play(GrowArrow(self.incoming_photon), run_time=t * 0.45)
        self.play(FadeIn(inc_lab), run_time=t * 0.3)
        self.inc_lab = inc_lab

    # ── A03: stimulated pair exits second atom ───────────────────────────────
    def beat_A03(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        x1 = cx - 1.5
        self.stim_pair = VGroup(
            Arrow([x1 + 0.28, atom_y + 0.12, 0], [x1 + 1.8, atom_y + 0.12, 0],
                  color=OKABE["yellow"], buff=0, stroke_width=4, tip_length=0.20),
            Arrow([x1 + 0.28, atom_y - 0.12, 0], [x1 + 1.8, atom_y - 0.12, 0],
                  color=OKABE["yellow"], buff=0, stroke_width=4, tip_length=0.20),
        )
        copy_lab = tag("copied direction", (cx + 0.4, atom_y + 0.55), fs=20, color=OKABE["yellow"])
        self.play(FadeOut(self.incoming_photon), FadeOut(self.inc_lab), run_time=0.3)
        self.play(Create(self.stim_pair), run_time=t * 0.4)
        self.play(FadeIn(copy_lab), run_time=t * 0.25)
        self.copy_lab = copy_lab

    # ── A04: same wavelength, phase, polarization ────────────────────────────
    def beat_A04(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        self.property_label = tag("same λ, φ, pol", (cx + 3.2, atom_y + 0.45), fs=18, color=OKABE["yellow"])
        self.play(FadeIn(self.property_label), run_time=t * 0.5)

    # ── A05: "stimulated emission" label + brace ─────────────────────────────
    def beat_A05(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        self.stim_label = tag("stimulated emission", (cx + 0.4, atom_y - 0.55), fs=22, color=ACCENT)
        brace_bar = Line([cx - 0.3, atom_y - 0.25, 0], [cx + 1.1, atom_y - 0.25, 0],
                         color=ACCENT, stroke_width=3)
        self.play(Create(brace_bar), FadeIn(self.stim_label), run_time=t * 0.55)
        self.brace_bar = brace_bar

    # ── A06: cavity mirrors ──────────────────────────────────────────────────
    def beat_A06(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        mirror_y0, mirror_y1 = atom_y - 0.7, atom_y + 0.7
        self.mirrors = VGroup(
            Line([cx - 4.5, mirror_y0, 0], [cx - 4.5, mirror_y1, 0], color=INK, stroke_width=6),
            Line([cx + 4.5, mirror_y0, 0], [cx + 4.5, mirror_y1, 0], color=INK, stroke_width=6),
        )
        # Bounce arc arrows indicating reflection
        self.bounce_arcs = VGroup(
            Arc(radius=0.4, start_angle=-PI / 2, angle=PI,
                color=ACCENT, stroke_width=3).move_to([cx - 4.5, atom_y, 0]),
            Arc(radius=0.4, start_angle=PI / 2, angle=PI,
                color=ACCENT, stroke_width=3).move_to([cx + 4.5, atom_y, 0]),
        )
        mirror_lab = tag("mirrors", (cx, atom_y + 0.95), fs=20, color=INK)
        self.play(Create(self.mirrors), run_time=t * 0.35)
        self.play(Create(self.bounce_arcs), FadeIn(mirror_lab), run_time=t * 0.4)
        self.mirror_lab = mirror_lab

    # ── A07: more photons in cavity ──────────────────────────────────────────
    def beat_A07(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        self.more_photons = VGroup(*[
            Arrow([cx - 3.5, atom_y + 0.28 * (i - 1), 0],
                  [cx + 3.5, atom_y + 0.28 * (i - 1), 0],
                  color=OKABE["yellow"], buff=0, stroke_width=3, tip_length=0.18)
            for i in range(3)
        ])
        more_lab = tag("more emissions", (cx, atom_y - 0.65), fs=20, color=OKABE["yellow"])
        self.play(FadeOut(self.pump_arrows), run_time=0.3)
        self.play(Create(self.more_photons), run_time=t * 0.4)
        self.play(FadeIn(more_lab), run_time=t * 0.25)
        self.more_lab = more_lab

    # ── A08: photon crowd — 8 parallel arrows ───────────────────────────────
    def beat_A08(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        self.photon_crowd = VGroup(*[
            Arrow([cx - 3.8, atom_y + 0.18 * (i - 3.5), 0],
                  [cx + 3.8, atom_y + 0.18 * (i - 3.5), 0],
                  color=OKABE["yellow"], buff=0, stroke_width=2, tip_length=0.14)
            for i in range(8)
        ])
        crowd_lab = tag("photon crowd", (cx, atom_y - 0.9), fs=20, color=OKABE["yellow"])
        self.play(FadeOut(self.more_photons), FadeOut(self.stim_pair), run_time=0.3)
        self.play(Create(self.photon_crowd), run_time=t * 0.4)
        self.play(FadeIn(crowd_lab), run_time=t * 0.25)
        self.crowd_lab = crowd_lab

    # ── A09: photons are indistinguishable — not like coins ──────────────────
    def beat_A09(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        bk_y = cy - 0.8
        dot1 = Dot([cx - 0.5, bk_y, 0], radius=0.15, color=OKABE["yellow"]).set_fill(OKABE["yellow"], opacity=0.8)
        dot2 = Dot([cx + 0.5, bk_y, 0], radius=0.15, color=OKABE["yellow"]).set_fill(OKABE["yellow"], opacity=0.8)
        coin_lab1 = tag("coin 1", (cx - 0.5, bk_y - 0.38), fs=16, color=INK)
        coin_lab2 = tag("coin 2", (cx + 0.5, bk_y - 0.38), fs=16, color=INK)
        coin_grp = VGroup(coin_lab1, coin_lab2)
        x_over = cross_out(coin_grp, color=FORBID, sw=4)
        indist_lab = tag("indistinguishable", (cx, bk_y - 0.75), fs=20, color=FORBID)
        self.play(FadeIn(dot1), FadeIn(dot2), FadeIn(coin_lab1), FadeIn(coin_lab2), run_time=t * 0.35)
        self.play(Create(x_over), run_time=t * 0.3)
        self.play(FadeIn(indist_lab), run_time=t * 0.2)
        self.indist_demo = VGroup(dot1, dot2, coin_grp, x_over, indist_lab)

    # ── A10: same quantum state = one shared wave ────────────────────────────
    def beat_A10(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        wave_y = cy - 1.2
        self.wave_same = ParametricFunction(
            lambda s: [s, wave_y + 0.28 * np.sin(3.0 * s), 0],
            t_range=[cx - 4.0, cx + 4.0, 0.03],
            color=OKABE["blue"], stroke_width=4
        )
        same_lab = tag("same state = 1 wave", (cx, wave_y - 0.42), fs=20, color=OKABE["blue"])
        self.play(Create(self.wave_same), run_time=t * 0.5)
        self.play(FadeIn(same_lab), run_time=t * 0.25)
        self.same_lab = same_lab

    # ── A11: second wave at different frequency ──────────────────────────────
    def beat_A11(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        wave_y2 = cy - 1.85
        self.wave_diff = ParametricFunction(
            lambda s: [s, wave_y2 + 0.20 * np.sin(5.5 * s), 0],
            t_range=[cx - 4.0, cx + 4.0, 0.03],
            color=OKABE["orange"], stroke_width=4
        )
        diff_lab = tag("different state", (cx, wave_y2 - 0.38), fs=20, color=OKABE["orange"])
        self.play(Create(self.wave_diff), run_time=t * 0.5)
        self.play(FadeIn(diff_lab), run_time=t * 0.25)
        self.diff_lab = diff_lab

    # ── A12: Bose–Einstein — occupied state wins ─────────────────────────────
    def beat_A12(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.play(Indicate(self.wave_same, color=OKABE["blue"], scale_factor=1.08), run_time=t * 0.5)
        self.bose_label = tag("Bose stats: occupied state wins",
                              (cx, cy - 2.2), fs=20, color=ACCENT)
        self.play(FadeIn(self.bose_label), run_time=t * 0.35)

    # ── A13: excited atom easier to trigger ─────────────────────────────────
    def beat_A13(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        tx, ty = cx + 2.8, cy - 0.55
        trig_atom = Circle(radius=0.22, color=OKABE["blue"], stroke_width=3)\
            .set_fill(OKABE["blue"], opacity=0.35).move_to([tx, ty, 0])
        trig_in = Arrow([tx - 1.0, ty, 0], [tx - 0.24, ty, 0],
                        color=OKABE["yellow"], buff=0, stroke_width=3, tip_length=0.16)
        trig_out1 = Arrow([tx + 0.24, ty + 0.12, 0], [tx + 1.1, ty + 0.12, 0],
                          color=OKABE["yellow"], buff=0, stroke_width=3, tip_length=0.15)
        trig_out2 = Arrow([tx + 0.24, ty - 0.12, 0], [tx + 1.1, ty - 0.12, 0],
                          color=OKABE["yellow"], buff=0, stroke_width=3, tip_length=0.15)
        trig_lab = tag("easier to trigger", (tx, ty - 0.52), fs=18, color=OKABE["green"])
        self.play(FadeIn(trig_atom), GrowArrow(trig_in), run_time=t * 0.35)
        self.play(GrowArrow(trig_out1), GrowArrow(trig_out2), run_time=t * 0.3)
        self.play(FadeIn(trig_lab), run_time=t * 0.2)
        self.trigger_demo = VGroup(trig_atom, trig_in, trig_out1, trig_out2, trig_lab)

    # ── A14: cavity selects one mode ─────────────────────────────────────────
    def beat_A14(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.play(Indicate(self.mirrors, color=ACCENT, scale_factor=1.05), run_time=t * 0.3)
        self.play(Indicate(self.photon_crowd, color=OKABE["yellow"], scale_factor=1.05), run_time=t * 0.3)
        self.mode_label = tag("cavity selects one mode", (cx, cy - 2.5), fs=20, color=ACCENT)
        self.play(FadeIn(self.mode_label), run_time=t * 0.25)

    # ── A15: output coupler ──────────────────────────────────────────────────
    def beat_A15(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        # Gap in the right mirror (white rectangle to cover part of the line)
        gap_cover = Rectangle(width=0.18, height=0.35, color=WHITE, stroke_width=0)\
            .set_fill(WHITE, opacity=1.0).move_to([cx + 4.5, atom_y, 0])
        self.output_beam = Arrow(
            [cx + 4.5, atom_y, 0], [cx + 6.0, atom_y, 0],
            color=OKABE["yellow"], buff=0, stroke_width=5, tip_length=0.24
        )
        out_lab = tag("output coupler", (cx + 5.1, atom_y + 0.45), fs=20, color=OKABE["yellow"])
        self.play(FadeIn(gap_cover), run_time=0.3)
        self.play(GrowArrow(self.output_beam), run_time=t * 0.4)
        self.play(FadeIn(out_lab), run_time=t * 0.25)
        self.gap_cover = gap_cover
        self.out_lab = out_lab

    # ── A16: coherent laser light ────────────────────────────────────────────
    def beat_A16(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        atom_y = cy + 0.6
        self.coherent_check = check((cx + 5.5, atom_y - 0.5), color=OKABE["green"], s=0.32)
        coherent_lab = tag("coherent laser beam", (cx + 4.2, atom_y - 1.0), fs=20, color=OKABE["green"])
        self.play(Indicate(self.output_beam, color=OKABE["yellow"], scale_factor=1.1), run_time=t * 0.35)
        self.play(Create(self.coherent_check), run_time=t * 0.3)
        self.play(FadeIn(coherent_lab), run_time=t * 0.25)
        self.coherent_lab = coherent_lab
