#!/usr/bin/env python3
"""
svg_doodles.py — build SVG-icon animations for the doodle sections of a video
=============================================================================
The intro, the hook beats, and a short outro normally sit as placeholder doodle
markers in the Manim master. This script turns them into real SVG-icon animations
(drawn-on, timed to each beat) that play UNDERNEATH — you can later overlay a
hand-drawn doodle on top, or just cut them straight in Premiere.

It reads a video's beat_sheet.json, and for every doodle beat (render == "doodle")
plus a synthesised OUTRO, it:
  1. infers a concept keyword from the beat's prose (new_visual_element / narration
     / the video's `thing` + title) — NO edits to the beat sheet,
  2. resolves that to an icon in the library (brand/app packs excluded by default),
  3. if anything can't be resolved, it PAUSES: prints the unmatched beats and the
     exact `svgrepo_download.py <term>` command to add them, then exits without
     writing — add the SVG(s) and re-run,
  4. otherwise emits `<slug>_svg_doodles.py` (one Manim Scene per beat) + a
     `<slug>_svg_plan.json`, and prints the render command.

Durations come from each beat's actual_duration_s (falls back to a default), so no
audio/timings file is needed.

Usage:
    python svg_doodles.py <video-folder>
    python svg_doodles.py <video-folder> --icons ~/ai/assets/validated
    python svg_doodles.py <video-folder> --transparent      # render .mov w/ alpha
    python svg_doodles.py <video-folder> --include-brands    # don't skip logo packs

Default icon search order: --icons, else ~/ai/assets/validated, else
~/Documents/Codex/Manim/shared/svg.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# packs that are brand/app logos — excluded from concept matching by default
BRAND_PREFIXES = (
    "1051339-social-media", "1077028-social-network",
    "111682-social-websites", "3884251-home-screen-apps",
)

STOP = {
    "the", "a", "an", "of", "to", "and", "with", "in", "on", "at", "as", "is",
    "it", "its", "for", "into", "that", "this", "their", "your", "you", "one",
    "two", "single", "small", "big", "full", "body", "looking", "holding",
    "draws", "drawn", "stroke", "white", "background", "doodle", "style", "no",
    "hand", "visible", "then", "title", "appears", "card", "marker", "same",
    "across", "whole", "scene", "up", "down", "left", "right", "person",
    "people", "they", "them", "his", "her", "while", "before", "after", "very",
}

# light synonym expansion: concept word -> extra search tokens
SYNONYMS = {
    "momentum": ["arrow", "vector"],
    "wave": ["wave", "signal", "frequency", "sound"],
    "packet": ["wave", "signal"],
    "particle": ["atom", "dot", "molecule"],
    "energy": ["battery", "power", "bolt", "lightning"],
    "equation": ["calculator", "math", "blackboard", "formula"],
    "equations": ["calculator", "math", "blackboard", "formula"],
    "math": ["calculator", "formula"],
    "ladder": ["ladder", "stairs", "steps"],
    "spin": ["atom", "rotate", "refresh", "cycle"],
    "atom": ["atom", "atomic"],
    "microscope": ["microscope"],
    "laser": ["laser", "light", "bulb", "beam"],
    "color": ["palette", "color", "spectrum"],
    "colors": ["palette", "color", "spectrum"],
    "cloud": ["cloud"],
    "box": ["box", "cube", "container"],
    "wall": ["wall", "brick", "barrier"],
    "ball": ["ball", "sphere", "circle"],
    "hill": ["mountain", "hill"],
    "current": ["bolt", "electricity", "power"],
    "tip": ["needle", "pen", "probe"],
    "bear": ["bear"],
    "coin": ["coin", "money"],
    "jar": ["jar", "bottle", "flask"],
}

INTRO_FALLBACK = "bear"     # series mascot
OUTRO_FALLBACK = "bear"


def tokens(text: str) -> list[str]:
    raw = re.findall(r"[a-zA-Z]+", (text or "").lower())
    return [t for t in raw if t not in STOP and len(t) > 2]


def icon_tokens(path: Path) -> set[str]:
    parts = re.split(r"[-_]", path.stem.lower())
    return {p for p in parts if not p.isdigit() and len(p) > 2}


def build_index(icon_dir: Path, include_brands: bool) -> list[tuple[Path, set[str]]]:
    idx = []
    for p in sorted(icon_dir.rglob("*.svg")):
        if not include_brands and any(p.stem.startswith(b) for b in BRAND_PREFIXES):
            continue
        idx.append((p, icon_tokens(p)))
    return idx


def expand(toks: list[str]) -> list[str]:
    out = list(toks)
    for t in toks:
        out += SYNONYMS.get(t, [])
    # de-dup, keep order
    seen, res = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            res.append(t)
    return res


def resolve(beat: dict, meta: dict, index: list[tuple[Path, set[str]]],
            min_score: int) -> tuple[Path | None, list[str], int]:
    """Subject-only icon match for a hook beat. Return (icon_path|None, tokens, score).

    Uses ONLY the beat's own content (new_visual_element + narration) so the icon
    actually matches the subject — no mascot fallback, no global title/thing padding."""
    base = tokens(beat.get("new_visual_element", "")) + tokens(beat.get("narration_text", ""))
    search = list(dict.fromkeys(expand(base)))            # de-dup, keep order
    weights = {t: max(1, 6 - i) for i, t in enumerate(search)}  # earlier tokens weigh more

    best, best_score = None, 0
    for path, itoks in index:
        score = sum(weights[t] for t in weights if t in itoks)
        if score > best_score or (score == best_score and best and score > 0
                                   and len(path.stem) < len(best.stem)):
            best, best_score = path, score
    if best_score < min_score:
        return None, search[:8], best_score
    return best, search[:8], best_score


# ── scene emission ────────────────────────────────────────────────────────────
SCENE_TEMPLATE = '''"""
{slug}_svg_doodles.py  (AUTO-GENERATED by svg_doodles.py)
SVG-icon animations for the doodle sections of "{title}".
Each beat is its own Scene -> its own clip; overlay a doodle on top or cut in Premiere.

Render (all clips):
    manim {flags} {slug}_svg_doodles.py {scene_names}
"""
from pathlib import Path
from manim import *

INK = "#1a1a1a"
ACCENT = "#5A5653"
FONT = "Shadows Into Light"
TITLE = {title!r}
ICONS = {icons!r}
DUR = {durs!r}


def _icon(beat_id, height=3.0):
    m = SVGMobject(ICONS[beat_id])
    m.set_stroke(INK, width=3).set_fill(ACCENT, opacity=1.0)
    m.scale_to_fit_height(height)
    return m


class _Base(Scene):
    beat_id = "INTRO"
    show_title = False        # intro/outro: title text. hooks: icon only.

    def construct(self):
        self.camera.background_color = WHITE
        t = DUR.get(self.beat_id, 4.0)
        has_icon = self.beat_id in ICONS
        used = 0.0
        if has_icon:
            icon = _icon(self.beat_id)
            icon.move_to([0, 0.4 if self.show_title else 0, 0])
            dt = min(2.0, t * 0.55)
            self.play(DrawBorderThenFill(icon), run_time=dt)
            used += dt
        if self.show_title:
            ttl = Text(TITLE, font=FONT, font_size=30, color=INK)
            ttl.scale_to_fit_width(min(11.0, ttl.width))
            ttl.to_edge(DOWN, buff=0.6) if has_icon else ttl.move_to(ORIGIN)
            dt = min(1.4, t * 0.3)
            self.play(Write(ttl), run_time=dt)
            used += dt
        self.wait(max(0.3, t - used))

{scene_classes}
'''

CLASS_TEMPLATE = '''class {cls}(_Base):
    beat_id = {bid!r}
    show_title = {show_title}
'''


def cls_name(bid: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", bid.title()) + "SVG"


def short_caption(beat: dict) -> str:
    nv = beat.get("new_visual_element", "")
    # first few words, title-light
    words = re.findall(r"[A-Za-z']+", nv)
    return " ".join(words[:4]).strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Generate SVG-icon doodle-section animations.")
    ap.add_argument("folder", help="video folder containing beat_sheet.json")
    ap.add_argument("--icons", default=None, help="icon library dir")
    ap.add_argument("--no-transparent", dest="transparent", action="store_false",
                    help="render opaque (white bg) instead of the default alpha .mov")
    ap.set_defaults(transparent=True)
    ap.add_argument("--include-brands", action="store_true", help="don't skip logo packs")
    ap.add_argument("--min-score", type=int, default=2,
                    help="min match strength for a hook icon (default 2; lower = looser)")
    ap.add_argument("--quality", default="-qh", help="manim quality flag (default -qh)")
    args = ap.parse_args(argv)

    folder = Path(args.folder).expanduser().resolve()
    sheet_path = folder / "beat_sheet.json"
    if not sheet_path.exists():
        print(f"[svg-doodles] no beat_sheet.json in {folder}", file=sys.stderr)
        return 1
    sheet = json.loads(sheet_path.read_text())
    meta = sheet.get("metadata", {})
    beats = sheet.get("beats", [])

    # icon library resolution
    candidates = []
    if args.icons:
        candidates.append(Path(args.icons).expanduser())
    candidates += [Path("~/Documents/Cowork/Manim/shared/svg").expanduser(),
                   Path("~/ai/assets/validated").expanduser(),
                   Path("~/Documents/Codex/Manim/shared/svg").expanduser()]
    icon_dir, index = None, []
    for c in candidates:
        if not c.is_dir():
            continue
        idx = build_index(c, args.include_brands)
        if idx:                      # skip dirs that exist but hold no usable SVGs
            icon_dir, index = c, idx
            break
        print(f"[svg-doodles] {c} exists but indexed 0 icons — trying next")
    if icon_dir is None:
        print("[svg-doodles] no icon library with usable SVGs found. Tried:\n  " +
              "\n  ".join(str(c) for c in candidates), file=sys.stderr)
        return 1
    print(f"[svg-doodles] icon library: {icon_dir}  ({len(index)} icons indexed)")

    # which beats get an SVG animation: doodle beats + the outro
    targets = [b for b in beats if b.get("render") == "doodle"
               or b.get("beat_type") == "OUTRO" or b.get("beat_id") == "OUTRO"]
    if not targets:
        print("[svg-doodles] no doodle/outro beats found.")
        return 0

    plan, icons, durs, classes, names = {}, {}, {}, [], []
    skipped = []     # hook beats with no sensible icon -> left for a hand doodle
    for b in targets:
        bid = b["beat_id"]
        is_intro = (bid == "INTRO" or b.get("beat_type") == "INTRO")
        is_outro = (bid == "OUTRO" or b.get("beat_type") == "OUTRO")
        dur_s = float(b.get("actual_duration_s", 4.0))

        if is_intro or is_outro:
            # title card only — no auto-icon (bear / branding gets overlaid by hand)
            durs[bid] = dur_s
            names.append(cls_name(bid))
            classes.append(CLASS_TEMPLATE.format(cls=cls_name(bid), bid=bid, show_title="True"))
            plan[bid] = {"icon": None, "kind": "title", "duration": dur_s}
            print(f"  title {bid:6} -> title card (no icon)")
            continue

        # hook beat: subject icon only if it genuinely matches
        path, search, score = resolve(b, meta, index, args.min_score)
        if path is None:
            skipped.append((bid, search, score))
            print(f"  --    {bid:6} no clear icon (best score {score}) -> leave for hand doodle")
            continue
        icons[bid] = str(path)
        durs[bid] = dur_s
        names.append(cls_name(bid))
        classes.append(CLASS_TEMPLATE.format(cls=cls_name(bid), bid=bid, show_title="False"))
        plan[bid] = {"icon": str(path), "kind": "icon", "score": score, "duration": dur_s}
        print(f"  icon  {bid:6} -> {path.name}  (score {score})")

    if not names:
        print("[svg-doodles] nothing to render (no title cards or matching hook icons).")
        return 0

    # emit scene file
    slug = meta.get("slug", folder.name)
    flags = "-t " + args.quality if args.transparent else args.quality
    scene_src = SCENE_TEMPLATE.format(
        slug=slug, title=meta.get("title", slug), icons=icons, durs=durs,
        flags=flags, scene_names=" ".join(names),
        scene_classes="\n".join(classes))
    out_scene = folder / f"{slug}_svg_doodles.py"
    out_scene.write_text(scene_src)
    (folder / f"{slug}_svg_plan.json").write_text(json.dumps(plan, indent=2))

    print(f"\n[svg-doodles] wrote {out_scene.name} and {slug}_svg_plan.json")
    if skipped:
        print(f"[svg-doodles] {len(skipped)} hook beat(s) left for a hand doodle "
              f"(no subject icon): {', '.join(b for b, _, _ in skipped)}")
    print("[svg-doodles] render the SVG doodle clips with:")
    print(f"    cd {folder}")
    print(f"    manim {flags} {out_scene.name} {' '.join(names)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
