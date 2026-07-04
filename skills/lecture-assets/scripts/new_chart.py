#!/usr/bin/env python3
"""
new_chart.py — scaffold a pool chart in BOTH shapes from one source (the drawer).

The slide-deck skill (stage 2) folds live D3 into the deck via a drawer registry
(`this._drawers['NAME'] = (c)=>{…}`), NOT via an iframe. So the pool authors every
chart as a **drawer** and derives the standalone page from it. One chart, two
artifacts, always in sync:

  charts/<name>.drawer.js   the source of truth: a self-contained `(c)=>{…}` that
                            draws into the mount `c`. emit_deck.py concatenates it
                            verbatim into the deck's <script data-dc-script>.
  charts/<name>.html        a standalone page that inlines the same drawer over a
                            mount + the d3 CDN — for articles/social/rasterizing.

Drawer contract:
  - value is a function `(c) => { … }`; `c` is the container element.
  - may use `window.d3`. Inside a deck it ALSO has the shared _define() helpers
    (RED, BLACK, N7…GOLD, D, FONT, clear, svgIn) in scope; a self-contained drawer
    (declares its own) works in both the deck and the standalone page — prefer that.
  - honest encodings only (DESIGN.md): zero baseline, scaleSqrt radii, one red,
    grays as the only neutrals, no blue, mono for data numbers, ARIA where sensible.

Usage:
    python new_chart.py <lecture_folder> --name calibration-curve \
        --concept "calibration / reliability diagram" [--sync]

  (no --sync) scaffold a new drawer stub + html + register the asset.
  --sync      regenerate charts/<name>.html from an already-edited drawer.js
              (run after you edit the drawer — keeps the standalone page in step).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DRAWER_STUB = """(c) => {
  // Self-contained pool drawer. Draws into `c`. Honest encodings only.
  const d3 = window.d3;
  const RED = '#C8102E', INK = '#2a1a0e', N5 = '#545454', N1 = '#E3E3E3';
  const FONT = '"Lato", system-ui, sans-serif';
  c.innerHTML = '';
  const W = 1480, H = 600, m = { t: 40, r: 40, b: 60, l: 70 };
  const svg = d3.select(c).append('svg')
    .attr('width', W).attr('height', H).attr('viewBox', `0 0 ${W} ${H}`)
    .style('overflow', 'visible').style('display', 'block');
  // TODO: author the encoding for "%CONCEPT%".
  svg.append('text').attr('x', W / 2).attr('y', H / 2).attr('text-anchor', 'middle')
    .attr('font-family', FONT).attr('font-size', 28).attr('fill', N5)
    .text('TODO: %NAME% — author this drawer');
}"""

HTML_WRAPPER = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>%NAME%</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
<style>
  :root {{ --white:#FFFFFF; --ink:#2a1a0e; --red:#C8102E; }}
  html,body{{margin:0;background:var(--white);color:var(--ink);
    font-family:"Lato",system-ui,sans-serif;}}
  #chart{{width:1480px;max-width:100%;margin:24px auto;}}
</style></head>
<body>
<div id="chart" role="img" aria-label="%CONCEPT%"></div>
<script>
// inlined from charts/%NAME%.drawer.js — regenerate with: new_chart.py … --sync
const draw = %DRAWER%;
draw(document.getElementById('chart'));
</script>
</body></html>
"""


def write_html(charts: Path, name: str, concept: str) -> None:
    drawer_src = (charts / f"{name}.drawer.js").read_text(encoding="utf-8").strip().rstrip(";")
    html = (HTML_WRAPPER
            .replace("%NAME%", name)
            .replace("%CONCEPT%", concept.replace('"', "'"))
            .replace("%DRAWER%", drawer_src))
    (charts / f"{name}.html").write_text(html, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="lecture folder (…/lectures/<chapter>)")
    ap.add_argument("--name", required=True, help="chart slug (kebab-case)")
    ap.add_argument("--concept", default="", help="one-line concept for the manifest/ARIA")
    ap.add_argument("--sync", action="store_true", help="only regenerate the .html from the drawer")
    args = ap.parse_args()

    charts = Path(args.folder).expanduser() / "assets" / "charts"
    charts.mkdir(parents=True, exist_ok=True)
    drawer = charts / f"{args.name}.drawer.js"

    if args.sync:
        if not drawer.exists():
            sys.exit(f"[err] {drawer} not found — nothing to sync")
        write_html(charts, args.name, args.concept or args.name)
        print(f"[ok] synced charts/{args.name}.html from the drawer")
        return

    if drawer.exists():
        sys.exit(f"[err] {drawer} exists — edit it, then run with --sync (won't clobber)")
    drawer.write_text(DRAWER_STUB.replace("%CONCEPT%", args.concept or args.name)
                      .replace("%NAME%", args.name) + "\n", encoding="utf-8")
    write_html(charts, args.name, args.concept or args.name)

    # register in the manifest via the existing tool
    add = Path(__file__).with_name("add_asset.py")
    subprocess.run([sys.executable, str(add), str(args.folder),
                    "--id", f"chart-{args.name}", "--kind", "chart",
                    "--concept", args.concept or args.name, "--source", "authored",
                    "--file", f"charts/{args.name}.drawer.js",
                    "--notes", "drawer contract: (c)=>{…}; standalone html beside it"],
                   check=False)
    print(f"[ok] scaffolded charts/{args.name}.drawer.js (+ .html) — author the drawer, "
          f"then: python new_chart.py {args.folder} --name {args.name} --sync")


if __name__ == "__main__":
    main()
