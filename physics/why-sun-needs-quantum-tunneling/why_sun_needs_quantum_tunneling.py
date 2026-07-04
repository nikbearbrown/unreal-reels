"""The Sun burns for billions of years because quantum tunneling allows fusion — Bear's Doodles"""
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
        """Sun circle with a wavy arrow punching through a barrier."""
        sun = Circle(radius=0.7, color=OKABE["yellow"], stroke_width=3)\
            .set_fill(OKABE["yellow"], opacity=0.25)
        barrier = Polygon(
            [-0.2, -0.5, 0], [0.0, 0.5, 0], [0.2, -0.5, 0],
            color=FORBID, stroke_width=3
        ).set_fill(FORBID, opacity=0.2).move_to([1.6, 0, 0])
        arr = Arrow([0.9, 0, 0], [2.2, 0, 0], color=OKABE["green"],
                    buff=0, stroke_width=4, tip_length=0.22)
        return VGroup(sun, barrier, arr)

    # ── A00: the Sun and "not fire" ──────────────────────────────────────────
    def beat_A00(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.sun = Circle(radius=1.5, color=OKABE["yellow"], stroke_width=4)\
            .set_fill(OKABE["yellow"], opacity=0.20).move_to([cx - 2.0, cy, 0])
        sun_lab = tag("the Sun", (cx - 2.0, cy - 1.75), fs=22, color=OKABE["yellow"])
        # Star polygon — "fire" idea, crossed out
        fire_star = Star(n=8, outer_radius=0.45, inner_radius=0.22,
                         color=FORBID, stroke_width=3)\
            .set_fill(FORBID, opacity=0.2).move_to([cx - 2.0 + 2.2, cy + 0.5, 0])
        self.no_fire = cross_out(fire_star, color=FORBID, sw=5)
        not_lab = tag("not fire", (cx + 0.6, cy + 1.1), fs=20, color=FORBID)
        self.play(Create(self.sun), run_time=t * 0.35)
        self.play(FadeIn(sun_lab), run_time=t * 0.2)
        self.play(FadeIn(fire_star), Create(self.no_fire), FadeIn(not_lab), run_time=t * 0.3)
        self.sun_lab = sun_lab
        self.fire_star = fire_star
        self.not_lab = not_lab

    # ── A01: timer — would burn too fast ─────────────────────────────────────
    def beat_A01(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        timer_arc = Arc(radius=0.5, start_angle=PI / 2, angle=-TAU * 0.8,
                        color=ACCENT, stroke_width=4).move_to([cx + 1.5, cy - 0.6, 0])
        tick = Line([cx + 1.5, cy - 0.6, 0], [cx + 1.5, cy - 0.1, 0],
                    color=ACCENT, stroke_width=3)
        timer_grp = VGroup(timer_arc, tick)
        self.timer_x = cross_out(timer_grp, color=FORBID, sw=4)
        fast_lab = tag("would burn too fast", (cx + 1.5, cy - 1.35), fs=18, color=FORBID)
        self.play(Create(timer_arc), Create(tick), run_time=t * 0.35)
        self.play(Create(self.timer_x), run_time=t * 0.3)
        self.play(FadeIn(fast_lab), run_time=t * 0.2)
        self.timer_grp = timer_grp
        self.fast_lab = fast_lab

    # ── A02: 4.6 billion years age label ─────────────────────────────────────
    def beat_A02(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.age_label = tag("4.6 billion years", (cx - 2.0, cy + 2.0), fs=22, color=ACCENT)
        self.play(FadeIn(self.age_label), run_time=t * 0.55)

    # ── A03: core of the Sun ─────────────────────────────────────────────────
    def beat_A03(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.core = Circle(radius=0.4, color=OKABE["orange"], stroke_width=3)\
            .set_fill(OKABE["orange"], opacity=0.40).move_to([cx - 2.0, cy, 0])
        core_lab = tag("core", (cx - 2.0, cy + 0.62), fs=18, color=OKABE["orange"])
        self.play(Create(self.core), run_time=t * 0.4)
        self.play(FadeIn(core_lab), run_time=t * 0.3)
        self.core_lab = core_lab

    # ── A04: two hydrogen nuclei / protons ───────────────────────────────────
    def beat_A04(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        p1 = Circle(radius=0.15, color=OKABE["blue"], stroke_width=3)\
            .set_fill(OKABE["blue"], opacity=0.55).move_to([cx - 2.3, cy, 0])
        p2 = Circle(radius=0.15, color=OKABE["blue"], stroke_width=3)\
            .set_fill(OKABE["blue"], opacity=0.55).move_to([cx - 1.7, cy, 0])
        self.protons = VGroup(p1, p2)
        prot_lab = tag("H nuclei: high pressure", (cx - 2.0, cy - 0.55), fs=17, color=OKABE["blue"])
        self.play(FadeIn(p1), FadeIn(p2), run_time=t * 0.45)
        self.play(FadeIn(prot_lab), run_time=t * 0.3)
        self.prot_lab = prot_lab

    # ── A05: fusion → helium ─────────────────────────────────────────────────
    def beat_A05(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.helium = Circle(radius=0.25, color=OKABE["green"], stroke_width=3)\
            .set_fill(OKABE["green"], opacity=0.50).move_to([cx - 2.0, cy, 0])
        he_lab = tag("fusion → helium", (cx - 2.0, cy - 0.55), fs=18, color=OKABE["green"])
        self.play(ReplacementTransform(self.protons, self.helium), run_time=t * 0.45)
        self.play(FadeIn(he_lab), run_time=t * 0.3)
        self.he_lab = he_lab

    # ── A06: energy release E = mc² ──────────────────────────────────────────
    def beat_A06(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.energy_arrow = Arrow(
            [cx - 2.0, cy + 0.27, 0], [cx - 2.0, cy + 1.0, 0],
            color=OKABE["yellow"], buff=0, stroke_width=4, tip_length=0.22
        )
        emc2 = tag("E = mc²", (cx - 1.0, cy + 0.85), fs=22, color=ACCENT)
        self.play(GrowArrow(self.energy_arrow), run_time=t * 0.4)
        self.play(FadeIn(emc2), run_time=t * 0.3)
        self.emc2 = emc2

    # ── A07: repulsion — protons push apart ──────────────────────────────────
    def beat_A07(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        # Restore two protons (replace helium)
        p1 = Circle(radius=0.15, color=OKABE["blue"], stroke_width=3)\
            .set_fill(OKABE["blue"], opacity=0.55).move_to([cx + 1.8, cy, 0])
        p2 = Circle(radius=0.15, color=OKABE["blue"], stroke_width=3)\
            .set_fill(OKABE["blue"], opacity=0.55).move_to([cx + 3.2, cy, 0])
        plus1 = tag("+", (cx + 1.8, cy), fs=14, color=INK)
        plus2 = tag("+", (cx + 3.2, cy), fs=14, color=INK)
        rep1 = Arrow([cx + 1.95, cy, 0], [cx + 1.2, cy, 0],
                     color=FORBID, buff=0, stroke_width=3, tip_length=0.16)
        rep2 = Arrow([cx + 3.05, cy, 0], [cx + 3.8, cy, 0],
                     color=FORBID, buff=0, stroke_width=3, tip_length=0.16)
        self.repulsion_arrows = VGroup(rep1, rep2)
        rep_lab = tag("repulsion", (cx + 2.5, cy - 0.55), fs=20, color=FORBID)
        self.play(FadeIn(p1), FadeIn(p2), FadeIn(plus1), FadeIn(plus2), run_time=t * 0.3)
        self.play(GrowArrow(rep1), GrowArrow(rep2), run_time=t * 0.3)
        self.play(FadeIn(rep_lab), run_time=t * 0.2)
        self.proton_pair = VGroup(p1, p2, plus1, plus2)
        self.rep_lab = rep_lab

    # ── A08: Coulomb barrier ──────────────────────────────────────────────────
    def beat_A08(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        # Triangle representing the energy barrier
        self.barrier = Polygon(
            [cx + 1.8, cy, 0],
            [cx + 2.5, cy + 1.2, 0],
            [cx + 3.2, cy, 0],
            color=FORBID, stroke_width=4
        ).set_fill(FORBID, opacity=0.18)
        bar_lab = tag("Coulomb barrier", (cx + 2.5, cy + 1.52), fs=20, color=FORBID)
        self.play(Create(self.barrier), run_time=t * 0.5)
        self.play(FadeIn(bar_lab), run_time=t * 0.3)
        self.bar_lab = bar_lab

    # ── A09: classical bounce ─────────────────────────────────────────────────
    def beat_A09(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        # Arc over the barrier going back
        self.bounce = Arc(radius=0.7, start_angle=0, angle=PI,
                          color=ACCENT, stroke_width=4).move_to([cx + 2.1, cy, 0])
        bounce_lab = tag("classical: bounces back", (cx + 2.5, cy - 0.65), fs=18, color=ACCENT)
        self.play(Create(self.bounce), run_time=t * 0.5)
        self.play(FadeIn(bounce_lab), run_time=t * 0.3)
        self.bounce_lab = bounce_lab

    # ── A10: quantum tunneling arrow through barrier ──────────────────────────
    def beat_A10(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.tunnel_arrow = DashedLine(
            [cx + 1.65, cy, 0], [cx + 3.35, cy, 0],
            color=OKABE["green"], stroke_width=5, dash_length=0.12
        )
        tun_lab = tag("quantum tunneling", (cx + 2.5, cy + 0.45), fs=20, color=OKABE["green"])
        arrow_tip = Arrow([cx + 3.1, cy, 0], [cx + 3.8, cy, 0],
                          color=OKABE["green"], buff=0, stroke_width=4, tip_length=0.20)
        self.play(Create(self.tunnel_arrow), run_time=t * 0.4)
        self.play(GrowArrow(arrow_tip), run_time=t * 0.25)
        self.play(FadeIn(tun_lab), run_time=t * 0.2)
        self.tun_lab = tun_lab
        self.arrow_tip = arrow_tip

    # ── A11: wave function leaks through barrier ──────────────────────────────
    def beat_A11(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.tunnel_wave = ParametricFunction(
            lambda s: [cx + 2.5 + s, cy + 0.38 * np.exp(-2.0 * abs(s)) * np.sin(10.0 * s), 0],
            t_range=[-1.5, 1.5, 0.02],
            color=OKABE["green"], stroke_width=4
        )
        wave_lab = tag("wave leaks through", (cx + 2.5, cy - 1.0), fs=18, color=OKABE["green"])
        self.play(Create(self.tunnel_wave), run_time=t * 0.55)
        self.play(FadeIn(wave_lab), run_time=t * 0.3)
        self.tunnel_wave_lab = wave_lab

    # ── A12: tunneling probability ───────────────────────────────────────────
    def beat_A12(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.prob_label = tag("probability ≈ 10⁻³⁰ per pair",
                              (cx + 2.5, cy - 1.55), fs=18, color=ACCENT)
        self.play(FadeIn(self.prob_label), run_time=t * 0.6)

    # ── A13: 10⁵⁷ proton pairs in the Sun ────────────────────────────────────
    def beat_A13(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        core_cx, core_cy = cx - 2.0, cy
        # Scatter small proton dots around the core
        rng = np.random.default_rng(42)
        angles = rng.uniform(0, 2 * np.pi, 8)
        radii = rng.uniform(0.1, 0.32, 8)
        self.many_protons = VGroup(*[
            Dot([core_cx + r * np.cos(a), core_cy + r * np.sin(a), 0],
                radius=0.07, color=OKABE["blue"]).set_fill(OKABE["blue"], opacity=0.7)
            for r, a in zip(radii, angles)
        ])
        many_lab = tag("10⁵⁷ pairs in Sun", (cx - 2.0, cy - 2.0), fs=18, color=OKABE["blue"])
        self.play(FadeIn(self.many_protons), run_time=t * 0.45)
        self.play(FadeIn(many_lab), run_time=t * 0.3)
        self.many_lab = many_lab

    # ── A14: tiny × enormous = steady fusion ─────────────────────────────────
    def beat_A14(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.steady_label = tag("tiny × enormous = steady fusion",
                                (cx, cy + 2.15), fs=20, color=OKABE["green"])
        # Small fusion arrows near the core
        fuse_arrs = VGroup(
            Arrow([cx - 2.5, cy + 0.4, 0], [cx - 2.15, cy + 0.15, 0],
                  color=OKABE["yellow"], buff=0, stroke_width=3, tip_length=0.14),
            Arrow([cx - 1.5, cy + 0.4, 0], [cx - 1.85, cy + 0.15, 0],
                  color=OKABE["yellow"], buff=0, stroke_width=3, tip_length=0.14),
        )
        self.play(FadeIn(self.steady_label), run_time=t * 0.35)
        self.play(Create(fuse_arrs), run_time=t * 0.35)
        self.fuse_arrs = fuse_arrs

    # ── A15: check mark — quantum tunneling = sunlight ───────────────────────
    def beat_A15(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.final_check = check((cx + 4.0, cy + 1.6), color=OKABE["green"], s=0.32)
        final_lab = tag("quantum tunneling = sunlight",
                        (cx + 2.5, cy + 2.0), fs=20, color=OKABE["green"])
        self.play(Indicate(self.tunnel_arrow, color=OKABE["green"], scale_factor=1.1), run_time=t * 0.35)
        self.play(Create(self.final_check), run_time=t * 0.3)
        self.play(FadeIn(final_lab), run_time=t * 0.25)
        self.final_lab = final_lab
