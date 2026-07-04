"""vox_scenes.py — The Ultraviolet Catastrophe, Vox edition.

One Scene per GRAPHIC/CARD beat; media slots (H01, H02, A08, A12) are filled
via media/ from the SHOTLIST archive links. Durations target the current
measured beats; after regenerating audio the compile ladder re-conforms.
Render everything: bash scripts/vox_run.sh reels/vox-the-ultraviolet-catastrophe
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve()
                       .parents[2] / "aspects/explainer/vox-explainer/manim"))
from vox_graphics import *   # noqa: F401,F403 — tokens, mobjects, BOLD guard
import numpy as np

# ---------------------------------------------------------------- helpers

X0, X1, Y0, Y1 = -5.2, 5.6, -2.6, 3.0        # chart region (scene units)

def smooth_curve(fn, x0, x1, color, width=5, n=90):
    """Stub-safe curve: VMobject through sampled points (same pattern as
    HandRing, which passes the static gate)."""
    v = VMobject(color=color, stroke_width=width)
    v.set_points_smoothly([np.array([x, fn(x), 0.0])
                           for x in np.linspace(x0, x1, n)])
    return v

def chart_axes(xlabel="frequency", ylabel="brightness"):
    ax = VGroup(
        Line([X0, Y0, 0], [X1, Y0, 0], color=INK, stroke_width=2.5),
        Line([X0, Y0, 0], [X0, Y1, 0], color=INK, stroke_width=2.5),
    )
    xl = Text(xlabel, font=SERIF, color=INK, font_size=26)
    xl.next_to(ax[0], DOWN, buff=0.25).align_to(ax[0], RIGHT)
    yl = Text(ylabel, font=SERIF, color=INK, font_size=26)
    yl.rotate(PI / 2).next_to(ax[1], LEFT, buff=0.25).align_to(ax[1], UP)
    return VGroup(ax, xl, yl)

def fx(t):   # 0..1 → x coordinate
    return X0 + t * (X1 - X0)

def wave_arc(t, n_humps, amp=0.42, color=NAVY, width=3.5):
    """A little standing-wave squiggle sitting on the baseline at position t."""
    x0, x1 = fx(t) - 0.55, fx(t) + 0.55
    return smooth_curve(lambda x: Y0 + 0.55 + amp *
                        np.sin((x - x0) / (x1 - x0) * PI * n_humps),
                        x0, x1, color, width, n=60)

def rj(x):        # Rayleigh–Jeans runaway (f²), scaled to the frame
    t = (x - X0) / (X1 - X0)
    return Y0 + 5.6 * t * t

def planck(x):    # Planck curve shape f³/(e^f − 1), scaled
    t = 9.0 * (x - X0) / (X1 - X0) + 1e-6
    return Y0 + 5.2 * (t ** 3 / (np.exp(t) - 1)) / 1.42

ARC_TS   = [0.10, 0.22, 0.34, 0.46, 0.56, 0.65, 0.73, 0.80, 0.87, 0.93]
ARC_HUMPS = [1, 1, 2, 2, 3, 3, 4, 5, 6, 7]

def all_arcs(color=NAVY):
    return VGroup(*[wave_arc(t, h, color=color)
                    for t, h in zip(ARC_TS, ARC_HUMPS)])

# ---------------------------------------------------------------- scenes

class INTRO_Title(Scene):          # ~3.2s
    def construct(self):
        t = Text("The Ultraviolet Catastrophe", font=SERIF, color=INK,
                 font_size=52, weight=BOLD)
        u = Line(t.get_corner(DL) + DOWN * 0.15, t.get_corner(DR) + DOWN * 0.15,
                 color=CRIMSON, stroke_width=2)
        s = Text("the graph that broke physics", font=SERIF, color=INK,
                 font_size=28)
        s.next_to(u, DOWN, buff=0.35)
        self.play(FadeIn(t), Create(u), run_time=0.9)
        self.play(FadeIn(s, shift=UP * 0.1), run_time=0.5)
        self.wait(1.8)


class A02_Axes(Scene):             # ~4.4s — the chart is introduced
    def construct(self):
        ch = chart_axes()
        lb = SerifLabel("how brightly it glows, by frequency", BLUE, size=30)
        lb.to_edge(UP, buff=0.55)
        self.play(Write(lb[0]), Create(lb[1]), run_time=0.8)
        self.play(Create(ch[0]), run_time=1.0)
        self.play(FadeIn(ch[1]), FadeIn(ch[2]), run_time=0.6)
        self.wait(2.0)


class A03_FewPatterns(Scene):      # ~4.7s — few patterns fit at low f
    def construct(self):
        ch = chart_axes()
        self.add(ch)
        arcs = VGroup(*[wave_arc(t, h) for t, h in
                        zip(ARC_TS[:3], ARC_HUMPS[:3])])
        self.play(LaggedStart(*[Create(a) for a in arcs],
                              lag_ratio=0.35, run_time=2.2))
        self.wait(2.3)


class A04_ManyPatterns(Scene):     # ~5.0s — the count climbs as f²
    def construct(self):
        ch = chart_axes(); self.add(ch)
        arcs = all_arcs()
        self.add(*arcs[:3])
        self.play(LaggedStart(*[Create(a) for a in arcs[3:]],
                              lag_ratio=0.12, run_time=2.2))
        count = smooth_curve(rj, X0 + 0.4, fx(0.93), CRIMSON, width=3)
        count.set_stroke(opacity=0.55)      # ghost hairline of what's coming
        self.play(Create(count), run_time=1.4)
        self.wait(1.2)


class A05_EqualShares(Scene):      # ~4.3s — equipartition as isotype
    def construct(self):
        ch = chart_axes(); self.add(ch); self.add(*all_arcs())
        squares = VGroup(*[Square(0.22).set_fill(TERRA, 1).set_stroke(width=0)
                           .move_to([fx(t), Y0 + 1.55, 0]) for t in ARC_TS])
        lb = SerifLabel("one equal share of energy, each", TERRA, size=28)
        lb.to_edge(UP, buff=0.55)
        self.play(Write(lb[0]), Create(lb[1]), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(sq, shift=DOWN * 0.6) for sq in squares],
                              lag_ratio=0.08, run_time=1.8))
        self.wait(1.4)


class A06_Runaway(Scene):          # ~5.9s — the Rayleigh–Jeans catastrophe
    def construct(self):
        ch = chart_axes(); self.add(ch); self.add(*all_arcs())
        run = smooth_curve(rj, X0 + 0.4, fx(0.97), CRIMSON, width=6)
        lb = SerifLabel("prediction: infinite ultraviolet", CRIMSON, size=30)
        lb.to_edge(UP, buff=0.55).to_edge(LEFT, buff=0.9)
        self.play(Create(run), run_time=2.2)
        self.play(Write(lb[0]), Create(lb[1]), run_time=0.9)
        self.wait(2.6)


class A07_RealCurve(Scene):        # ~5.5s — reality rises, peaks, falls
    def construct(self):
        ch = chart_axes(); self.add(ch)
        ghost = smooth_curve(rj, X0 + 0.4, fx(0.97), CRIMSON, width=4)
        ghost.set_stroke(opacity=0.25); self.add(ghost)
        real = smooth_curve(planck, X0 + 0.15, X1 - 0.2, NAVY, width=6)
        lb = SerifLabel("what real objects actually do", NAVY, size=30)
        lb.to_edge(UP, buff=0.55)
        self.play(Write(lb[0]), Create(lb[1]), run_time=0.9)
        self.play(Create(real), run_time=2.4)
        self.wait(2.0)


class A09_PriceOfUV(Scene):        # ~5.2s — chunks cost more at high f
    def construct(self):
        bars = VGroup()
        for i in range(8):
            h = 0.28 + i * 0.34
            b = Rectangle(width=0.55, height=h)
            b.set_fill(NAVY, 1).set_stroke(width=0)
            b.move_to([-4.2 + i * 1.15, Y0 + h / 2 + 0.4, 0])
            bars.add(b)
        chip = LabelChip("ultraviolet is wildly expensive", CRIMSON, size=24)
        chip.next_to(bars[-1], UP, buff=0.4).shift(LEFT * 1.2)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in bars],
                              lag_ratio=0.12, run_time=2.0))
        self.play(FadeIn(chip, shift=DOWN * 0.15), run_time=0.7)
        self.wait(2.2)


class A10_TooExpensive(Scene):     # ~4.9s — high-f patterns go dark
    def construct(self):
        ch = chart_axes(); self.add(ch)
        arcs = all_arcs(); self.add(*arcs)
        grey = VGroup(*[a.copy().set_stroke(color="#B9B3A9", opacity=0.5)
                        for a in arcs[5:]])
        self.wait(1.2)
        self.play(*[Transform(a, g) for a, g in zip(arcs[5:], grey)],
                  run_time=1.6)
        self.wait(2.0)


class A11_BendBack(Scene):         # ~4.6s — the runaway bends to reality
    def construct(self):
        ch = chart_axes(); self.add(ch)
        run = smooth_curve(rj, X0 + 0.4, fx(0.97), CRIMSON, width=6)
        self.add(run)
        real = smooth_curve(planck, X0 + 0.15, X1 - 0.2, NAVY, width=6)
        self.wait(0.8)
        self.play(Transform(run, real), run_time=2.2)
        self.wait(1.5)


class A12_Fuse(Scene):             # fallback GRAPHIC if no portrait found:
    def construct(self):           # one terracotta chunk on the finished curve
        ch = chart_axes(); self.add(ch)
        real = smooth_curve(planck, X0 + 0.15, X1 - 0.2, NAVY, width=6)
        self.add(real)
        chunk = Square(0.3).set_fill(TERRA, 1).set_stroke(width=0)
        chunk.move_to([fx(0.35), planck(fx(0.35)) + 0.35, 0])
        self.play(FadeIn(chunk, scale=1.4), run_time=0.8)
        self.play(Create(HandRing(chunk, color=TERRA)), run_time=1.0)
        self.wait(2.2)


class OUTRO_End(Scene):            # ~6.8s
    def construct(self):
        t = Text("Bear's Notes", font=SERIF, color=INK, font_size=44,
                 weight=BOLD)
        u = Line(t.get_corner(DL) + DOWN * 0.12, t.get_corner(DR) + DOWN * 0.12,
                 color=CRIMSON, stroke_width=2)
        s = Text("youtube.com/@NikBearBrown", font=SERIF, color=INK,
                 font_size=26)
        s.next_to(u, DOWN, buff=0.4)
        self.play(FadeIn(t), Create(u), run_time=0.9)
        self.play(FadeIn(s), run_time=0.5)
        self.wait(4.8)
