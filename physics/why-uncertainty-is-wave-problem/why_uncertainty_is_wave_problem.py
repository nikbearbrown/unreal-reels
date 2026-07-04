"""Heisenberg uncertainty is a wave property, not a measurement disturbance — Bear's Doodles"""
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
        """Sine wave with a wide brace below it."""
        wave = ParametricFunction(
            lambda t: [t, 0.35 * np.sin(3.0 * t), 0],
            t_range=[-2.0, 2.0, 0.05],
            color=OKABE["blue"], stroke_width=4
        )
        brace = Brace(wave, DOWN, color=ACCENT)
        return VGroup(wave, brace)

    # ── A00: mystery vs. wave problem ────────────────────────────────────────
    def beat_A00(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.mystery_text = Text("?", font=FONT, font_size=72, color=FORBID)\
            .move_to([cx - 2.5, cy + 0.5, 0])
        preview_wave = ParametricFunction(
            lambda s: [s, cy - 0.2 + 0.28 * np.sin(3.0 * s), 0],
            t_range=[cx - 1.0, cx + 3.5, 0.04],
            color=OKABE["blue"], stroke_width=3
        )
        theme_lab = tag("uncertainty = wave problem,\nnot mystery", (cx + 1.2, cy + 0.8), fs=20, color=ACCENT)
        self.play(FadeIn(self.mystery_text), run_time=t * 0.25)
        self.play(Create(preview_wave), run_time=t * 0.3)
        self.play(FadeIn(theme_lab), run_time=t * 0.2)
        self.play(FadeOut(self.mystery_text), run_time=t * 0.15)
        self.preview_wave = preview_wave
        self.theme_lab = theme_lab

    # ── A01: clean sine wave ─────────────────────────────────────────────────
    def beat_A01(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.sine_wave = ParametricFunction(
            lambda s: [s, cy + 0.7 + 0.40 * np.sin(3.0 * s), 0],
            t_range=[cx - 4.0, cx + 4.0, 0.03],
            color=OKABE["blue"], stroke_width=4
        )
        long_lab = tag("long wave", (cx - 3.2, cy + 1.35), fs=20, color=OKABE["blue"])
        self.play(FadeOut(self.preview_wave), run_time=0.25)
        self.play(Create(self.sine_wave), run_time=t * 0.5)
        self.play(FadeIn(long_lab), run_time=t * 0.25)
        self.long_lab = long_lab

    # ── A02: double arrow marking one wavelength ─────────────────────────────
    def beat_A02(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        wave_y = cy + 0.7
        # one period of sin(3x): period = 2π/3 ≈ 2.09
        lam = 2.0 * np.pi / 3.0
        x_peak1 = cx - lam / 2
        x_peak2 = cx + lam / 2
        self.lambda_arrow = darrow(
            [x_peak1, wave_y + 0.62, 0], [x_peak2, wave_y + 0.62, 0],
            color=ACCENT, sw=3
        )
        lam_lab = tag("clear λ", (cx, wave_y + 0.92), fs=20, color=ACCENT)
        self.play(Create(self.lambda_arrow), run_time=t * 0.45)
        self.play(FadeIn(lam_lab), run_time=t * 0.3)
        self.lam_lab = lam_lab

    # ── A03: clear frequency label + f indicator dot ─────────────────────────
    def beat_A03(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.freq_label = tag("clear frequency f = 1/λ", (cx, cy + 0.0), fs=20, color=ACCENT)
        # Dot marking one cycle's peak to make "clear f" concrete
        self.freq_dot = Dot([cx, cy + 0.7 + 0.40, 0], radius=0.11, color=ACCENT)\
            .set_fill(ACCENT, opacity=0.8)
        self.play(FadeIn(self.freq_label), run_time=t * 0.3)
        self.play(FadeIn(self.freq_dot), run_time=t * 0.35)

    # ── A04: brace over full width — Δx large ───────────────────────────────
    def beat_A04(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        wave_y = cy + 0.7
        # Brace spanning the full wave width
        span_line = Line([cx - 4.0, wave_y - 0.62, 0], [cx + 4.0, wave_y - 0.62, 0],
                         color=GHOST, stroke_width=1)
        self.spread_brace = Brace(self.sine_wave, DOWN, color=ACCENT)
        brace_lab = tag("spread across space: Δx large",
                        (cx, cy + 0.7 - 0.62 - 0.42), fs=19, color=ACCENT)
        self.play(Create(self.spread_brace), run_time=t * 0.45)
        self.play(FadeIn(brace_lab), run_time=t * 0.3)
        self.brace_lab = brace_lab

    # ── A05: narrow Gaussian pulse ───────────────────────────────────────────
    def beat_A05(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.pulse = ParametricFunction(
            lambda s: [s, cy - 0.5 + 0.70 * np.exp(-6.0 * (s - cx) ** 2), 0],
            t_range=[cx - 2.0, cx + 2.0, 0.02],
            color=OKABE["orange"], stroke_width=4
        )
        pulse_lab = tag("short pulse: clear location", (cx, cy - 1.35), fs=20, color=OKABE["orange"])
        self.play(Create(self.pulse), run_time=t * 0.5)
        self.play(FadeIn(pulse_lab), run_time=t * 0.3)
        self.pulse_lab = pulse_lab

    # ── A06: many overlapping frequencies needed ─────────────────────────────
    def beat_A06(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        ks = [4, 6, 8, 10]
        ys = [cy - 1.6, cy - 1.85, cy - 2.1, cy - 2.35]
        self.many_freqs = VGroup(*[
            ParametricFunction(
                lambda s, k=kk, base_y=yy: [s, base_y + 0.12 * np.sin(k * s), 0],
                t_range=[cx - 2.2, cx + 2.2, 0.03],
                color=GHOST, stroke_width=2
            )
            for kk, yy in zip(ks, ys)
        ])
        multi_lab = tag("many λ needed for short pulse", (cx, cy - 2.45), fs=19, color=GHOST)
        self.play(Create(self.many_freqs), run_time=t * 0.5)
        self.play(FadeIn(multi_lab), run_time=t * 0.3)
        self.multi_lab = multi_lab

    # ── A07: Δx small → Δk large (with narrow-band indicator arrow) ─────────
    def beat_A07(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.ux_text = tag("Δx small  →  Δk large", (cx, cy + 1.75), fs=22, color=ACCENT)
        # Arrow pointing at the narrow pulse to illustrate "Δx small"
        self.ux_arrow = Arrow([cx - 1.8, cy - 0.1, 0], [cx - 0.4, cy - 0.3, 0],
                              color=ACCENT, buff=0, stroke_width=3, tip_length=0.18)
        self.play(FadeIn(self.ux_text), run_time=t * 0.3)
        self.play(GrowArrow(self.ux_arrow), run_time=t * 0.35)

    # ── A08: Δk small → Δx large (with wide-span brace arrow) ───────────────
    def beat_A08(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.uk_text = tag("Δk small  →  Δx large", (cx, cy + 1.25), fs=22, color=OKABE["blue"])
        # Arrow spanning the full sine wave to illustrate "Δx large"
        self.uk_arrow = darrow([cx - 3.5, cy + 0.7 - 0.65, 0], [cx + 3.5, cy + 0.7 - 0.65, 0],
                               color=OKABE["blue"], sw=3)
        self.play(FadeIn(self.uk_text), run_time=t * 0.3)
        self.play(Create(self.uk_arrow), run_time=t * 0.35)

    # ── A09: sine wave becomes quantum wave function ψ ───────────────────────
    def beat_A09(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        new_wave = ParametricFunction(
            lambda s: [s, cy + 0.7 + 0.40 * np.sin(3.0 * s), 0],
            t_range=[cx - 4.0, cx + 4.0, 0.03],
            color=OKABE["green"], stroke_width=4
        )
        psi_lab = tag("ψ = quantum wave function", (cx + 1.5, cy + 1.35), fs=20, color=OKABE["green"])
        self.play(ReplacementTransform(self.sine_wave, new_wave), run_time=t * 0.45)
        self.play(FadeIn(psi_lab), run_time=t * 0.3)
        self.sine_wave = new_wave
        self.psi_lab = psi_lab

    # ── A10: position = peak of packet ──────────────────────────────────────
    def beat_A10(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        peak_dot = Dot([cx, cy - 0.5 + 0.70, 0], radius=0.12, color=OKABE["orange"])\
            .set_fill(OKABE["orange"], opacity=0.9)
        self.play(Indicate(self.pulse, color=OKABE["orange"], scale_factor=1.06), run_time=t * 0.35)
        self.play(FadeIn(peak_dot), run_time=t * 0.2)
        self.pos_label = tag("position = where packet sits", (cx + 2.2, cy - 0.35), fs=18, color=OKABE["orange"])
        self.play(FadeIn(self.pos_label), run_time=t * 0.3)
        self.peak_dot = peak_dot

    # ── A11: momentum from frequency content ─────────────────────────────────
    def beat_A11(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        mom_wave = ParametricFunction(
            lambda s: [s, cy - 1.5 + 0.12 * np.sin(6.0 * s), 0],
            t_range=[cx - 2.0, cx + 2.0, 0.03],
            color=OKABE["blue"], stroke_width=3
        )
        self.mom_label = tag("momentum from frequency content",
                             (cx, cy - 1.85), fs=18, color=OKABE["blue"])
        self.play(Create(mom_wave), run_time=t * 0.4)
        self.play(FadeIn(self.mom_label), run_time=t * 0.3)
        self.mom_wave = mom_wave

    # ── A12: narrower Gaussian → more k components ──────────────────────────
    def beat_A12(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.narrow_pulse = ParametricFunction(
            lambda s: [s, cy - 0.5 + 0.70 * np.exp(-18.0 * (s - cx) ** 2), 0],
            t_range=[cx - 1.0, cx + 1.0, 0.01],
            color=OKABE["orange"], stroke_width=4
        )
        # extra frequency lines to show more k needed
        extra_freqs = VGroup(*[
            ParametricFunction(
                lambda s, k=kk, ii=ii: [s, cy - 1.6 - 0.22 * ii + 0.09 * np.sin(k * s), 0],
                t_range=[cx - 2.0, cx + 2.0, 0.02],
                color=FORBID, stroke_width=2
            )
            for ii, kk in enumerate([12, 16, 20, 24])
        ])
        narrow_lab = tag("narrow packet → many k", (cx, cy - 0.35), fs=19, color=OKABE["orange"])
        self.play(ReplacementTransform(self.pulse, self.narrow_pulse), run_time=t * 0.4)
        self.play(Create(extra_freqs), run_time=t * 0.3)
        self.play(FadeIn(narrow_lab), run_time=t * 0.2)
        self.extra_freqs = extra_freqs
        self.narrow_lab = narrow_lab

    # ── A13: Δk large → Δp large (with FORBID spread indicator) ────────────
    def beat_A13(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.dp_label = tag("Δk large  →  Δp large", (cx, cy + 0.75), fs=20, color=FORBID)
        # Red spread arrow spanning the extra_freqs area to show "many k"
        self.dp_arrow = darrow([cx - 1.8, cy - 1.4, 0], [cx + 1.8, cy - 1.4, 0],
                               color=FORBID, sw=4)
        self.play(FadeIn(self.dp_label), run_time=t * 0.3)
        self.play(Create(self.dp_arrow), run_time=t * 0.35)

    # ── A14: Heisenberg uncertainty principle equation ───────────────────────
    def beat_A14(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.hup = MathTex(r"\Delta x \, \Delta p \geq \hbar/2", color=ACCENT,
                           font_size=42).move_to([cx, cy + 1.6, 0])
        hup_lab = tag("Heisenberg uncertainty", (cx, cy + 2.1), fs=20, color=ACCENT)
        self.play(Write(self.hup), run_time=t * 0.5)
        self.play(FadeIn(hup_lab), run_time=t * 0.3)
        self.hup_lab = hup_lab

    # ── A15: waves always knew this (cross out "quantum invented this") ──────
    def beat_A15(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        not_invented_txt = tag("quantum invented this", (cx - 2.0, cy - 1.85), fs=18, color=GHOST)
        self.play(FadeIn(not_invented_txt), run_time=t * 0.25)
        self.not_invented_x = cross_out(not_invented_txt, color=FORBID, sw=4)
        always_lab = tag("waves always knew this", (cx - 2.0, cy - 2.3), fs=18, color=ACCENT)
        self.play(Create(self.not_invented_x), run_time=t * 0.35)
        self.play(FadeIn(always_lab), run_time=t * 0.25)
        self.not_invented_txt = not_invented_txt
        self.always_lab = always_lab

    # ── A16: check — unavoidable for matter waves ────────────────────────────
    def beat_A16(self, t):
        cx, cy = rcx(self.stage), rcy(self.stage)
        self.final_check = check((cx + 4.0, cy + 1.6), color=OKABE["green"], s=0.32)
        final_lab = tag("unavoidable for matter waves", (cx + 2.5, cy + 2.0), fs=20, color=OKABE["green"])
        self.play(Indicate(self.hup, color=ACCENT, scale_factor=1.08), run_time=t * 0.35)
        self.play(Create(self.final_check), run_time=t * 0.3)
        self.play(FadeIn(final_lab), run_time=t * 0.25)
        self.final_lab = final_lab
