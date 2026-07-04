#!/usr/bin/env python3
"""
emit_deck.py — Phase 2 of the slide-deck skill.

deck_plan.json  ->  <Chapter NN - Title>.dc.html   (+ copies the runtime beside it)

- Renders every plan slide through templates/archetypes.py (the exact brutalist
  dialect deck-stage.js renders and deck-lecture/extract_slides.py parses).
- Folds each chart slide's drawer (charts/<name>.drawer.js, the lecture-assets
  drawer contract) into ONE `<script type="text/x-dc" data-dc-script>` registry —
  live D3 in the deck with zero nested iframes.
- Copies figure assets into the deck folder and rewrites their src.
- Copies support.js, deck-stage.js, and the _ds/ design-system folder from a
  known-good source deck folder (metadata.runtime_from) so the deck is portable.

The Component boilerplate (KaTeX auto-render + slide-change chart dispatch) is
always emitted, even with zero charts, because it is what renders [data-tex].

Pure stdlib. No deps.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

# import the archetype templates from ../templates
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "templates"))
import archetypes  # noqa: E402


# The deck runtime class. Mirrors the known-good fairness deck: it waits for d3 +
# katex, auto-renders every [data-tex], and on each slidechange redraws the active
# slide's [data-chart] via the registry we fill in _define(). {DRAWERS} is the only
# hole — one `this._drawers['name'] = <drawer.js body>;` per chart.
CHART_SCRIPT_TMPL = """<script type="text/x-dc" data-dc-script>
class Component extends DCLogic {
  componentDidMount() {
    this._ready = false;
    this._timer = null;
    this._drawers = {};
    this._onSlide = (e) => this._activate(e && e.detail && e.detail.slide);
    document.addEventListener('slidechange', this._onSlide);
    this._wait();
  }
  componentWillUnmount() {
    document.removeEventListener('slidechange', this._onSlide);
    if (this._timer) clearInterval(this._timer);
  }
  _wait() {
    const have = window.d3 && window.katex && document.querySelector('[data-tex],[data-chart]');
    if (!have) { setTimeout(() => this._wait(), 70); return; }
    this._renderMath();
    this._define();
    this._ready = true;
    const active = document.querySelector('section[data-deck-active]') || document.querySelector('section');
    this._activate(active);
  }
  _renderMath() {
    document.querySelectorAll('[data-tex]').forEach((el) => {
      if (el._k) return;
      try {
        window.katex.render(el.textContent.trim(), el, {
          displayMode: el.hasAttribute('data-display'),
          throwOnError: false,
        });
        el._k = true;
      } catch (err) { /* leave raw */ }
    });
  }
  _activate(slide) {
    if (!this._ready || !slide || !slide.querySelector) return;
    this._renderMath();
    if (this._timer) { clearInterval(this._timer); this._timer = null; }
    const c = slide.querySelector('[data-chart]');
    if (!c) return;
    const fn = this._drawers[c.getAttribute('data-chart')];
    if (fn) try { fn(c); } catch (err) { console.warn('chart', err); }
  }
  _define() {
    const d3 = window.d3;
    const RED = '#C8102E', BLACK = '#111111', N7 = '#2D2926', N5 = '#545454',
      N4 = '#787878', N3 = '#909090', N2 = '#C4C4C4', N1 = '#E3E3E3', GOLD = '#A4804A';
    const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const D = RM ? 0 : 850;
    const FONT = '"Lato", system-ui, sans-serif';
    const clear = (c) => { c.innerHTML = ''; };
    const svgIn = (c, w, h) => d3.select(c).append('svg')
      .attr('width', w).attr('height', h).attr('viewBox', `0 0 ${w} ${h}`)
      .style('overflow', 'visible').style('display', 'block');
{DRAWERS}
  }
  renderVals() { return {}; }
}
</script>"""

RUNTIME_FILES = ("support.js", "deck-stage.js")


def load_plan(plan_path: Path) -> dict:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if "slides" not in plan:
        sys.exit(f"[err] {plan_path} has no 'slides' array")
    return plan


def fold_drawers(chart_names: list[str], assets_dir: Path | None) -> tuple[str, list[str]]:
    """Return (drawers_js, missing_names). Reads charts/<name>.drawer.js per the
    lecture-assets drawer contract: each file is a self-contained (c)=>{...}."""
    parts, missing = [], []
    for name in chart_names:
        src = None
        if assets_dir is not None:
            cand = assets_dir / "charts" / f"{name}.drawer.js"
            if cand.exists():
                src = cand.read_text(encoding="utf-8").strip().rstrip(";")
        if src is None:
            missing.append(name)
            # emit a visible placeholder drawer so the deck still runs
            src = ("(c)=>{c.innerHTML='<div style=\\'font-family:var(--font-mono);"
                   "color:#C8102E;padding:40px;\\'>[chart drawer missing: "
                   f"{name}]</div>';}}")
        parts.append(f"    this._drawers['{name}'] = {src};")
    return "\n".join(parts), missing


def copy_asset(src_ref: str, plan_dir: Path, out_dir: Path) -> str:
    """Copy a figure asset into out_dir/assets/ and return the new relative src."""
    src = (plan_dir / src_ref).resolve() if not Path(src_ref).is_absolute() else Path(src_ref)
    if not src.exists():
        # leave the reference as-is; verify_deck will flag the broken img
        return src_ref
    dest_dir = out_dir / "assets"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    shutil.copy2(src, dest)
    return f"assets/{src.name}"


def copy_runtime(runtime_from: Path, out_dir: Path) -> list[str]:
    """Copy support.js, deck-stage.js, and the _ds/ folder. Returns notes."""
    notes = []
    for f in RUNTIME_FILES:
        s = runtime_from / f
        if s.exists():
            shutil.copy2(s, out_dir / f)
        else:
            notes.append(f"[warn] runtime file not found: {s}")
    # _ds/ design system
    ds_src = runtime_from / "_ds"
    if ds_src.exists():
        ds_dest = out_dir / "_ds"
        if ds_dest.resolve() != ds_src.resolve():
            if ds_dest.exists():
                shutil.rmtree(ds_dest)
            shutil.copytree(ds_src, ds_dest)
    else:
        notes.append(f"[warn] _ds/ design system not found at {ds_src}")
    return notes


def build_deck(plan: dict, plan_dir: Path, out_path: Path, assets_dir: Path | None) -> dict:
    meta = plan.get("metadata", {})
    out_dir = out_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # runtime + _ds
    runtime_from = meta.get("runtime_from")
    notes = []
    if runtime_from:
        notes += copy_runtime(Path(runtime_from).expanduser(), out_dir)
    else:
        notes.append("[warn] metadata.runtime_from unset — support.js/deck-stage.js/_ds not copied")

    ds_css = meta.get("ds_css")
    if not ds_css:
        # discover the _ds css we just copied
        found = list((out_dir / "_ds").glob("*/colors_and_type.css")) if (out_dir / "_ds").exists() else []
        ds_css = f"_ds/{found[0].parent.name}/colors_and_type.css" if found else "_ds/colors_and_type.css"

    # render slides
    rendered, chart_names = [], []
    for s in plan["slides"]:
        if s.get("archetype") == "chart" and s.get("chart"):
            chart_names.append(s["chart"])
        if s.get("archetype") == "figure" and s.get("src"):
            s = dict(s)
            s["src"] = copy_asset(s["src"], plan_dir, out_dir)
        rendered.append(archetypes.render_slide(s))

    drawers_js, missing = fold_drawers(chart_names, assets_dir)
    chart_script = CHART_SCRIPT_TMPL.replace("{DRAWERS}", drawers_js)

    shell = (Path(__file__).resolve().parent.parent / "templates" / "deck_shell.html").read_text()
    html = (shell
            .replace("{DS_CSS}", ds_css)
            .replace("{SLIDES}", "\n\n".join(rendered))
            .replace("{CHART_SCRIPT}", chart_script))
    out_path.write_text(html, encoding="utf-8")

    return {
        "slides": len(rendered),
        "charts": chart_names,
        "missing_drawers": missing,
        "notes": notes,
        "out": str(out_path),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", help="path to deck_plan.json")
    ap.add_argument("-o", "--out", required=True,
                    help='output deck path, e.g. "…/Chapter 07 - Fairness.dc.html"')
    ap.add_argument("--assets", default=None,
                    help="assets/ pool dir (for charts/<name>.drawer.js). Default: <plan_dir>/assets")
    args = ap.parse_args()

    plan_path = Path(args.plan).expanduser()
    if not plan_path.exists():
        sys.exit(f"[err] plan not found: {plan_path}")
    plan_dir = plan_path.parent
    assets_dir = Path(args.assets).expanduser() if args.assets else (plan_dir / "assets")
    if not assets_dir.exists():
        assets_dir = None

    plan = load_plan(plan_path)
    out_path = Path(args.out).expanduser()
    res = build_deck(plan, plan_dir, out_path, assets_dir)

    for n in res["notes"]:
        print(n)
    print(f"[ok] wrote {res['out']}")
    print(f"[ok] {res['slides']} slides | charts: {', '.join(res['charts']) or 'none'}")
    if res["missing_drawers"]:
        print(f"[warn] no drawer.js for: {', '.join(res['missing_drawers'])} "
              f"(placed a visible placeholder; author charts/<name>.drawer.js in the pool)")
    print("[next] Phase 3: python scripts/verify_deck.py \"" + res["out"] + "\"")


if __name__ == "__main__":
    main()
