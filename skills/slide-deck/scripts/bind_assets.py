#!/usr/bin/env python3
"""
bind_assets.py — Phase 1 of the slide-deck skill.

Match the plan's chart/figure slides to pool assets and print a GAP REPORT.
Per the locked design (decision B), this is a report, not a stop: the single
human gate is Phase 0. Here we just surface what's bound, what's missing, and
what in the pool went unused — so gaps route back to lecture-assets instead of
getting faked.

For each `chart` slide  -> needs assets/charts/<chart>.drawer.js (drawer contract)
For each `figure` slide -> needs a real file at `src`, or an `asset_ref` that
                           resolves to a candidate in assets.json

Exit code 0 always (advisory). Use --strict to exit 1 when anything is missing.

Pure stdlib. No deps.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", help="deck_plan.json")
    ap.add_argument("--assets", default=None, help="assets/ dir (default: <plan_dir>/assets)")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any binding is missing")
    args = ap.parse_args()

    plan_path = Path(args.plan).expanduser()
    plan = load(plan_path)
    assets_dir = Path(args.assets).expanduser() if args.assets else plan_path.parent / "assets"
    manifest = {}
    if (assets_dir / "assets.json").exists():
        manifest = {a["id"]: a for a in load(assets_dir / "assets.json").get("assets", [])}

    bound, missing, used_ids = [], [], set()

    for s in plan["slides"]:
        arch = s.get("archetype")
        label = s.get("label", "?")
        if arch == "chart":
            name = s.get("chart", "")
            drawer = assets_dir / "charts" / f"{name}.drawer.js"
            if drawer.exists():
                bound.append(f"chart  · {label:38.38} -> charts/{name}.drawer.js")
            else:
                missing.append(f"chart  · {label:38.38} -> MISSING charts/{name}.drawer.js "
                               f"(author the drawer in lecture-assets)")
        elif arch == "figure":
            ref = s.get("asset_ref")
            src = s.get("src", "")
            ok = False
            if ref and ref in manifest:
                used_ids.add(ref)
                a = manifest[ref]
                if a.get("status") == "candidate":
                    bound.append(f"figure · {label:38.38} -> {a['file']} ({ref})")
                    ok = True
                else:
                    missing.append(f"figure · {label:38.38} -> {ref} is status={a.get('status')} "
                                   f"(placeholder — regenerate in lecture-assets)")
                    ok = True  # accounted for
            if not ok:
                if src and not src.startswith("TODO") and (plan_path.parent / src).exists():
                    bound.append(f"figure · {label:38.38} -> {src}")
                else:
                    missing.append(f"figure · {label:38.38} -> no resolved asset (src={src!r})")

    unused = [f"{i} ({a.get('kind')}) — {a.get('concept','')[:44]}"
              for i, a in manifest.items()
              if i not in used_ids and a.get("status") == "candidate"]

    print(f"# bind report for {plan_path.name}\n")
    print(f"BOUND ({len(bound)}):")
    for b in bound:
        print("  ✓ " + b)
    print(f"\nGAPS ({len(missing)}):")
    for m in missing:
        print("  ✗ " + m)
    print(f"\nUNUSED CANDIDATES ({len(unused)}) — inventory, still useful elsewhere:")
    for u in unused:
        print("  · " + u)

    if missing and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
