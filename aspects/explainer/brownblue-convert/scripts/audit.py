#!/usr/bin/env python3
"""
audit.py — score an explainer folder against the Brown Blue depth standard.

Usage:
    python3 audit.py <folder>              # one video folder
    python3 audit.py <dir-of-folders>      # audits every child that has a beat_sheet.json

Reads beat_sheet.json (and script.md if present). Prints a per-check scorecard
and a verdict: PASS (already Brown Blue depth) or NEEDS-BB-CONVERSION.
Critical checks decide the verdict; the rest are warnings that shape a rewrite.
Exit code 0 if the (single) folder PASSes, 1 if it needs conversion, 2 on error.
No third-party deps.
"""
import json
import re
import sys
from pathlib import Path

LECTURE_RED = "#C8102E"
BLUE_ACCENTS = {"#58C4DD", "#0072B2"}          # dark / light Brown Blue accents
MIN_DEPTH_S = 120.0                             # single-insight tier floor (pedagogy §5)
ROLE_WORDS = ["HOOK", "INSTANCE", "TRANSFORM", "ABSTRACTION", "PAYOFF", "BOUNDARY"]
EQ_HINTS = ("mathtex", "\\frac", "equation", "\\hat", "\\psi", "=")  # loose equation sniff


def load(folder: Path):
    bs = folder / "beat_sheet.json"
    if not bs.exists():
        return None, None
    d = json.loads(bs.read_text())
    beats = d.get("beats", d if isinstance(d, list) else [])
    return d, beats


def beat_text(b: dict) -> str:
    return " ".join(str(b.get(k, "")) for k in (
        "narration_text", "new_visual_element", "video_animation_prompt",
        "start_frame_prompt", "end_frame_prompt", "role", "beat_id"))


BEAR_WPS = 2.6  # Bear-voice words/sec (style.md: calm, unhurried, speed 0.92)


def duration(beats):
    """Measured audio when present; else estimate from narration word count
    (+0.5s consolidation buffer/beat). Returns (seconds, measured?)."""
    measured = any((b.get("actual_duration_s") or 0) for b in beats)
    if measured:
        return round(sum((b.get("actual_duration_s") or 0) for b in beats), 1), True
    total = 0.0
    for b in beats:
        words = len(str(b.get("narration_text", "")).split())
        total += words / BEAR_WPS + 0.5
    return round(total, 1), False


def has_equation(d, beats) -> bool:
    blob = json.dumps(d).lower()
    return ("mathtex" in blob) or ("equation" in blob) or any(
        h in blob for h in ("\\frac", "\\hat", "\\psi"))


def roles_in(beats):
    found = set()
    for b in beats:
        t = beat_text(b).upper()
        for r in ROLE_WORDS:
            if r in t:
                found.add(r)
    return found


def instances_before_first_abstraction(beats) -> int:
    n = 0
    for b in beats:
        t = beat_text(b).upper()
        if "ABSTRACTION" in t:
            return n
        if "INSTANCE" in t:
            n += 1
    return n  # no abstraction tagged


def has_tangent(beats) -> bool:
    return any("TANGENT" in beat_text(b).upper() for b in beats)


def audit(folder: Path):
    d, beats = load(folder)
    if d is None:
        return None
    meta = d.get("metadata", {})
    # Red scan must ignore the legitimate `forbidden_color: #C8102E` declaration.
    scan = json.loads(json.dumps(d))
    scan.get("metadata", {}).pop("forbidden_color", None)
    blob = json.dumps(scan)
    renders = {b.get("render", "?") for b in beats}
    dur, measured = duration(beats)
    eq = has_equation(d, beats)
    roles = roles_in(beats)

    checks = []  # (critical, name, ok, detail)
    checks.append((True, "pure Manim (no doodle render)",
                   "doodle" not in renders, f"renders={sorted(renders)}"))
    checks.append((True, f"duration >= {int(MIN_DEPTH_S)}s",
                   dur >= MIN_DEPTH_S, f"{dur}s {'(measured)' if measured else '(est. from narration)'}"))
    inst = instances_before_first_abstraction(beats)
    checks.append((True, ">=2 INSTANCE before ABSTRACTION",
                   ("ABSTRACTION" in roles and inst >= 2),
                   f"instances-before-abstraction={inst}, roles={'yes' if 'ABSTRACTION' in roles else 'untagged'}"))
    checks.append((True, "equation tangent when equation present",
                   (not eq) or has_tangent(beats),
                   "no equation" if not eq else ("TANGENT present" if has_tangent(beats) else "equation, NO tangent")))
    checks.append((True, f"no lecture red ({LECTURE_RED})",
                   LECTURE_RED.lower() not in blob.lower(), "clean" if LECTURE_RED.lower() not in blob.lower() else "red present"))

    checks.append((False, "series = Brown Blue",
                   meta.get("series") == "Brown Blue", f"series={meta.get('series')!r}"))
    checks.append((False, "font = EB Garamond",
                   meta.get("text_font") == "EB Garamond", f"font={meta.get('text_font')!r}"))
    checks.append((False, "style dark|light",
                   meta.get("style") in ("dark", "light"), f"style={meta.get('style')!r}"))
    checks.append((False, "blue accent_color",
                   meta.get("accent_color") in BLUE_ACCENTS, f"accent={meta.get('accent_color')!r}"))
    checks.append((False, "slug ends -bb",
                   str(meta.get("slug", folder.name)).endswith("-bb"), f"slug={meta.get('slug', folder.name)!r}"))
    checks.append((False, "3b1b beat roles tagged",
                   len(roles) >= 3, f"found={sorted(roles) or 'none'}"))
    checks.append((False, "BOUNDARY beat",
                   "BOUNDARY" in roles, "yes" if "BOUNDARY" in roles else "missing"))

    crit_fail = [c for c in checks if c[0] and not c[2]]
    verdict = "PASS" if not crit_fail else "NEEDS-BB-CONVERSION"
    return {"folder": folder.name, "verdict": verdict, "dur": dur,
            "eq": eq, "checks": checks, "crit_fail": crit_fail}


def print_report(r):
    print(f"\n=== {r['folder']} — {r['verdict']} ({r['dur']}s"
          f"{', has equation' if r['eq'] else ''}) ===")
    for critical, name, ok, detail in r["checks"]:
        tag = "CRIT" if critical else "warn"
        mark = "PASS" if ok else "FAIL"
        print(f"  [{tag}] {mark}  {name:42s} {detail}")
    if r["crit_fail"]:
        print("  -> convert: " + "; ".join(c[1] for c in r["crit_fail"]))


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.exists():
        print(f"[err] no such path: {root}")
        return 2

    if (root / "beat_sheet.json").exists():
        r = audit(root)
        print_report(r)
        return 0 if r["verdict"] == "PASS" else 1

    # directory of folders
    kids = sorted(p for p in root.iterdir() if p.is_dir() and (p / "beat_sheet.json").exists())
    if not kids:
        print(f"[err] no folders with beat_sheet.json under {root}")
        return 2
    results = [audit(p) for p in kids]
    for r in results:
        print_report(r)
    npass = sum(r["verdict"] == "PASS" for r in results)
    print(f"\n===== SUMMARY: {npass}/{len(results)} already Brown Blue depth; "
          f"{len(results) - npass} NEED -bb conversion =====")
    for r in results:
        print(f"  {r['verdict']:20s} {r['folder']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
