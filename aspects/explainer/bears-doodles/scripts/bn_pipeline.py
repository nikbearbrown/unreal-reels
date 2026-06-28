#!/usr/bin/env python3
"""
bn_pipeline.py — book-ordered render + final-passes + YouTube post-kit, one concept
at a time.

Two modes:
  plan (default)   scan the Manim root, order every concept by book position
                   (volume + chapter from each beat sheet's `source`), score
                   publish-readiness, and write PUBLISH-QUEUE.md (the YouTube order).
  run <concept>    take ONE concept (a 1-min folder slug) end to end:
                     1-min 9:16 Short:  generate_audio -> manim -r 1080,1920 ->
                                        manim_layout_audit -> assemble --portrait
                     deep   16:9     :  (its depth_of partner) generate_audio ->
                                        manim -qh -> manim_layout_audit -> assemble
                     then writes <concept>/PUBLISH-KIT.md (title, description,
                     chapters, hashtags, Related-Video + schedule instructions).
                   Add --render to actually execute (default prints the commands).

The VISUAL final pass (manim_layout_audit) is wired in automatically. The SCIENTIFIC
final pass (verify every formula/number/claim) is a human/subagent gate — the post
kit carries a FACTCHECK checklist and the kit is marked pending until signed off.

Usage:
  python bn_pipeline.py                 # plan: write PUBLISH-QUEUE.md
  python bn_pipeline.py run energy-levels-arent-evenly-spaced --render
  python bn_pipeline.py run energy-levels-arent-evenly-spaced     # dry (print cmds)
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def meta(folder: Path) -> dict:
    return json.loads((folder / "beat_sheet.json").read_text()).get("metadata", {})


def book_pos(src: str):
    v = re.search(r"vol(\d)", src or ""); c = re.search(r"chapters/(\d+)", src or "")
    return (int(v.group(1)) if v else 9, int(c.group(1)) if c else 99)


def mp4(folder: Path, slug: str, which: str) -> Path:
    return folder / "mp4" / (f"{slug}-short.mp4" if which == "short" else f"{slug}.mp4")


def scan(root: Path):
    """Return concepts ordered by book position. A 'concept' is a 1-min folder; its
    deep partner (tier=deep, depth_of==slug) is attached if present."""
    folders = [p for p in sorted(root.iterdir())
               if p.is_dir() and (p / "beat_sheet.json").exists()]
    by_slug = {meta(f).get("slug", f.name): f for f in folders}
    deep_by_parent = {}
    ones = []
    for f in folders:
        m = meta(f)
        if m.get("tier") == "deep":
            deep_by_parent[m.get("depth_of")] = f
        else:
            ones.append(f)
    concepts = []
    for f in ones:
        m = meta(f); slug = m.get("slug", f.name)
        deep = deep_by_parent.get(slug)
        concepts.append({"slug": slug, "title": m.get("title", slug), "folder": f,
                         "pos": book_pos(m.get("source", "")), "deep": deep,
                         "deep_slug": meta(deep).get("slug") if deep else None})
    concepts.sort(key=lambda c: c["pos"])
    return concepts


def readiness(c):
    short = mp4(c["folder"], c["slug"], "short").exists()
    portrait = any(("import bn_layout" in p.read_text() or "from bn_layout" in p.read_text())
                   for p in c["folder"].glob("*.py")
                   if p.name not in ("bn_layout.py",) and not p.name.endswith("_svg_doodles.py"))
    deep16 = bool(c["deep"]) and mp4(c["deep"], c["deep_slug"], "landscape").exists()
    ready = short and deep16
    need = []
    if not c["deep"]:
        need.append("author deep (expand)")
    elif not deep16:
        need.append("render deep 16:9")
    if not portrait:
        need.append("portrait-convert 1-min")
    if portrait and not short:
        need.append("render 1-min 9:16")
    return ready, need


def plan(root: Path):
    concepts = scan(root)
    lines = ["# Bear's Notes — publish queue (book order = YouTube order)", "",
             "Order = volume + chapter from each concept's `source`. Each concept publishes",
             "TWO videos: the 1-min **9:16 Short** and the deep **2–5 min 16:9**. A concept is",
             "**READY** only when both masters exist. Run `bn_pipeline.py run <slug> --render`",
             "down this list, top to bottom.", ""]
    n_ready = 0
    lines.append("| # | book | concept | deep? | READY | needs |")
    lines.append("|---|------|---------|-------|-------|-------|")
    for i, c in enumerate(concepts, 1):
        ready, need = readiness(c)
        n_ready += ready
        pos = f"v{c['pos'][0]}.{c['pos'][1]:02d}" if c["pos"][0] < 9 else "—"
        lines.append(f"| {i} | {pos} | {c['slug']} | {'yes' if c['deep'] else 'no'} | "
                     f"{'✅' if ready else '—'} | {', '.join(need) if need else ''} |")
    lines += ["", f"**{n_ready} of {len(concepts)} ready.** Concepts with book `—` lack a "
              "`source` in metadata (several look like duplicates of sourced concepts) — "
              "assign a chapter or dedup before they enter the order."]
    out = root / "PUBLISH-QUEUE.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"[plan] {len(concepts)} concepts, {n_ready} ready → {out}")
    return out


# ── run one concept ──────────────────────────────────────────────────────────
def sh(cmd, do, cwd=None, check=True):
    print(f"   $ (cd {cwd}) " + " ".join(cmd) if cwd else "   $ " + " ".join(cmd))
    if do:
        r = subprocess.run(cmd, check=False, cwd=str(cwd) if cwd else None)
        if check and r.returncode != 0:
            raise subprocess.CalledProcessError(r.returncode, cmd)
        return r.returncode


def chapters(deep_folder: Path):
    """Grouped chapters from the deep beat sheet + timings (>=3, each >=10s, start 0:00)."""
    bs = json.loads((deep_folder / "beat_sheet.json").read_text())
    T = {}
    tp = deep_folder / "mp3" / "timings.json"
    if tp.exists():
        T = json.loads(tp.read_text())
    SEC = {0: "Intro", 1: "The puzzle", 2: "The puzzle", 3: "Intuition",
           4: "From idea to the formula", 5: "Worked example", 6: "What it predicts",
           7: "Recap", 8: "Outro"}
    t = 0.0; groups = []
    for b in bs["beats"]:
        d = float(T.get(b["beat_id"], b.get("actual_duration_s", 4.0)))
        si = b.get("scene_index", 0)
        if groups and groups[-1]["si"] == si:
            groups[-1]["dur"] += d
        else:
            groups.append({"si": si, "start": t, "dur": d, "label": SEC.get(si, f"Part {si}")})
        t += d
    # merge groups < 10s into previous
    merged = []
    for g in groups:
        if merged and g["dur"] < 10 and g["label"] == merged[-1]["label"]:
            merged[-1]["dur"] += g["dur"]
        elif merged and g["dur"] < 10:
            merged[-1]["dur"] += g["dur"]
        else:
            merged.append(g)
    def stamp(s): return f"{int(s//60)}:{int(s % 60):02d}"
    out, seen = [], set()
    for g in merged:
        lab = g["label"]
        if lab in seen:
            continue
        seen.add(lab)
        out.append(f"{stamp(g['start'])} {lab}")
    if out and not out[0].startswith("0:00"):
        out[0] = "0:00 " + out[0].split(" ", 1)[1]
    return out


def desc_block(m, body, extra=""):
    tags = " ".join(m.get("hashtags", [])[:5])
    parts = [body.strip()]
    if extra.strip():
        parts.append(extra.strip())
    parts.append(m.get("channel_url", "youtube.com/@NikBearBrown"))
    parts.append(tags)
    return "\n\n".join(p for p in parts if p)


def post_kit(c, root: Path):
    f1, deep = c["folder"], c["deep"]
    m1 = meta(f1)
    short_title = m1.get("title", c["slug"])
    L = ["# PUBLISH KIT — " + c["slug"], "",
         f"Book position: v{c['pos'][0]}.{c['pos'][1]:02d}" if c["pos"][0] < 9 else "Book position: (unsourced)",
         "", "> FACTCHECK (scientific pass) — sign off before publishing:",
         "> - [ ] every formula correct  - [ ] every number correct  - [ ] every spoken claim correct",
         "> - [ ] visual layout audit clean (both renders)", ""]
    # Video 1 — Short
    hook1 = next((b.get("narration_text", "") for b in json.loads((f1/'beat_sheet.json').read_text())["beats"]
                  if b["beat_id"] == "H01"), short_title)
    L += ["## VIDEO 1 — Short (9:16)", f"- file: `mp4/{c['slug']}-short.mp4`",
          f"- title: {short_title}", "- description:", "```",
          desc_block(m1, hook1, f"Full worked example: {meta(deep).get('title') if deep else '(deep version)'} — on the channel."),
          "```",
          f"- Related Video (MANUAL, Studio): → the deep 16:9 ({c['deep_slug'] or 'deep'})", ""]
    # Video 2 — Deep
    if deep:
        m2 = meta(deep)
        b2 = json.loads((deep/'beat_sheet.json').read_text())["beats"]
        hook2 = next((b.get("narration_text", "") for b in b2 if b["beat_id"] == "H01"), m2.get("title"))
        ch = chapters(deep)
        L += ["## VIDEO 2 — Deep (16:9)", f"- file: `{c['deep_slug']}/mp4/{c['deep_slug']}.mp4`",
              f"- title: {m2.get('title')}", "- description:", "```",
              desc_block(m2, hook2),
              "", "CHAPTERS"] + ch + ["```",
              "- end screen + card → subject playlist", ""]
    else:
        L += ["## VIDEO 2 — Deep (16:9)", "- NOT BUILT — run `expand` first.", ""]
    out = f1 / "PUBLISH-KIT.md"
    out.write_text("\n".join(L) + "\n")
    print(f"[kit] {out}")


def run(root: Path, slug: str, render: bool):
    concepts = {c["slug"]: c for c in scan(root)}
    if slug not in concepts:
        sys.exit(f"[run] no concept '{slug}'")
    c = concepts[slug]
    ready, need = readiness(c)
    f1, deep = c["folder"], c["deep"]
    scene1 = next(p for p in f1.glob("*.py")
                  if p.name not in ("bn_layout.py",) and not p.name.endswith("_svg_doodles.py"))
    GA, AUD, ASM = str(SCRIPTS / "generate_audio.py"), str(SCRIPTS / "manim_layout_audit.py"), str(SCRIPTS / "assemble.py")
    print(f"[run] {slug}  (book v{c['pos'][0]}.{c['pos'][1]:02d})  needs={need or 'nothing'}")
    print("  1-min 9:16 Short:")
    sh(["python", GA, "."], render, cwd=f1)
    sh(["manim", "-r", "1080,1920", "--fps", "60", "--disable_caching", "--flush_cache",
        scene1.name, "BearsDoodlesVideo"], render, cwd=f1)
    rc = sh(["python", AUD, scene1.name, "--portrait"], render, cwd=f1, check=False)
    if rc == 2:
        print("   [!] 9:16 layout audit found ERRORS — review layout_audit.md", file=sys.stderr)
    sh(["python", ASM, ".", "--mode", "manim", "--portrait"], render, cwd=f1)
    if deep:
        scene2 = next(p for p in deep.glob("*.py")
                      if p.name not in ("bn_layout.py",) and not p.name.endswith("_svg_doodles.py"))
        print("  deep 16:9:")
        sh(["python", GA, "."], render, cwd=deep)
        sh(["manim", "-qh", scene2.name, "BearsDoodlesVideo"], render, cwd=deep)
        rc = sh(["python", AUD, scene2.name], render, cwd=deep, check=False)
        if rc == 2:
            print("   [!] deep layout audit found ERRORS — review layout_audit.md", file=sys.stderr)
        sh(["python", ASM, ".", "--mode", "manim"], render, cwd=deep)
    else:
        print("  deep 16:9: (not built — run `expand` first)")
    post_kit(c, root)
    print("[run] done. Review PUBLISH-KIT.md, sign off the FACTCHECK, then youtube_publish.py.")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="plan", choices=["plan", "run"])
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--root", default=str(Path.home() / "Documents/Cowork/Manim"))
    ap.add_argument("--render", action="store_true", help="actually run manim/ffmpeg (else print)")
    a = ap.parse_args(argv)
    root = Path(a.root).expanduser().resolve()
    if a.mode == "plan":
        plan(root)
    else:
        if not a.slug:
            sys.exit("run needs a concept slug")
        run(root, a.slug, a.render)


if __name__ == "__main__":
    raise SystemExit(main())
