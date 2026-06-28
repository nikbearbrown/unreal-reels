#!/usr/bin/env python3
"""
recommend.py — first-pass media router for a beat sheet.

Reads a video's beat_sheet.json, classifies each beat into a content type, and
recommends the best visual medium for LEARNING (not polish), with a confidence and a
one-line reason. Runs the red-flag checks. Advisory and non-destructive: it never
overwrites a human `render_override`; with --write it adds `render`,
`render_confidence`, and `render_reason` suggestions only where the human hasn't
decided.

This is the deterministic keyword pass. An agent/human refines the calls the keywords
can't make — read ../SKILL.md and ../reference/decision-table.md for the judgment layer.

Media: manim | remotion | t2i (text-to-image) | t2v (text-to-video)

Usage:
    python recommend.py path/to/<video-folder>            # print a routing table
    python recommend.py path/to/<video-folder> --write    # also write suggestions back
    python recommend.py path/to/beat_sheet.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── content-type keyword signatures (checked in priority order) ──────────────
EQUATION = re.compile(
    r"(=|≈|≤|≥|∫|∑|√|±|×|÷|\^|\\frac|\bequation\b|\bderiv|\bformula\b|\bsolve\b|"
    r"\bcalculat|\bratio\b|α|β|γ|δ|θ|λ|μ|σ|Δ|\bproportional\b)", re.I)
DATA = re.compile(
    r"\b(graph|chart|plot|curve|axis|axes|trend|distribution|histogram|scatter|"
    r"bar chart|frequency|percent|percentage|over time|time[- ]series|dose[- ]response|"
    r"survival curve|correlat|data\b|dataset|statistic)\b", re.I)
MECHANISM = re.compile(
    r"\b(cascade|binds?|binding|replicat|transcri|translat|divides?|division|mitosis|"
    r"meiosis|flows?|diffus|cycle|pathway|activat|inhibit|propagat|signal|folds?|"
    r"cross(es|ing)?|pumps?|splits?|attaches?|releases?|moves?|step[- ]by[- ]step|"
    r"process|mechanism|sequence|then|first.*then|how .* works|"
    # physics / quantum behaviour (terse concept beats still route to Manim):
    r"wave(function|length)?|oscillat|curvature|curv(es|ing)?|vibrat|orbit|spin|"
    r"tunnel|collaps|superposition|ground state|excited|node|energy level|momentum|"
    r"amplitude|quantum|trajector|velocity|accelerat|\bforce\b|\bfield\b|standing wave)\b",
    re.I)
STRUCTURE = re.compile(
    r"\b(structure|anatomy|anatomic|cross[- ]section|organelle|membrane|map of|layout|"
    r"diagram of|parts of|labeled|label the|components?|circuit|lattice|organi[sz]ation|"
    r"located|location of)\b", re.I)
GEOMETRIC = re.compile(
    r"\b(unit cell|crystal|lattice|graph theory|venn|set diagram|vector space|"
    r"coordinate|geometr|axis of symmetry|tessellat)\b", re.I)
REALWORLD = re.compile(
    r"\b(patient|clinic|clinical|microscop|biopsy|real[- ]world|in the lab|laboratory|"
    r"looks? like|photo|scene|scenario|everyday|in nature|field|specimen|sample under)\b",
    re.I)
TITLE = re.compile(
    r"\b(welcome|thanks for watching|in this video|today we|let'?s introduce|"
    r"definition|is defined as|the term|key term|chapter|section|outline|agenda)\b", re.I)

# molecular/invisible cue → blocks generative media for accuracy
INVISIBLE = re.compile(
    r"\b(molecul|atom|electron|protein|enzyme|receptor|gene|dna|rna|cell(ular)?|"
    r"ion|orbital|quantum|subatomic|nucleus|membrane|antibody|virus|chromosom)\b", re.I)

# ── type → recommendation ─────────────────────────────────────────────────────
REC = {
    "equation":   ("manim",    "high",     "LaTeX precision + worked-example build; color-code changing terms"),
    "mechanism":  ("manim",    "moderate", "schematic, controllable, one element per spoken idea; ties static, dodges seductive detail"),
    "structure":  ("remotion", "moderate", "vetted illustration + spatial-contiguity labels / progressive reveal"),
    "geometric":  ("manim",    "high",     "natively geometric; precise construction"),
    "data":       ("remotion", "high",     "exact axes/labels, reveal in narrated order, descriptive title"),
    "realworld":  ("t2i",      "low",      "real-world anchor; Ken-Burns in Remotion; only if perceptual features ARE the content"),
    "title":      ("remotion", "high",     "key term only (<=3 words), no narration duplication"),
    "default":    ("remotion", "moderate", "global fallback: static schematic diagram + labels (permanence, low risk)"),
}


def classify(text: str) -> str:
    t = text or ""
    if TITLE.search(t):
        return "title"
    if EQUATION.search(t):
        return "equation"
    if DATA.search(t):
        return "data"
    if GEOMETRIC.search(t):
        return "geometric"
    if MECHANISM.search(t):
        return "mechanism"
    if STRUCTURE.search(t):
        return "structure"
    if REALWORLD.search(t):
        return "realworld"
    return "default"


def red_flags(beat: dict, ctype: str, media: str, text: str) -> list[str]:
    flags = []
    # 1. on-screen text duplicating narration
    ost = (beat.get("on_screen_text") or "").strip()
    narr = (beat.get("narration_text") or "").strip()
    if ost and narr and _similar(ost, narr):
        flags.append("on-screen text duplicates narration → cut to a <=3-word label "
                     "(accessibility captions go in the VTT track, not the frame)")
    # 2 & 3. generative media on invisible/precise content
    if media in ("t2v", "t2i") and (ctype in ("mechanism", "equation") or
                                    (ctype == "structure" and INVISIBLE.search(text or ""))):
        flags.append("generative media on invisible/precise content → confabulation risk; "
                     "use manim/remotion (a non-expert cannot vet AI accuracy)")
    if media == "t2v" and INVISIBLE.search(text or ""):
        flags.append("text-to-video for molecular/microscale content → never (no real footage exists)")
    # 4. realworld photoreal must earn its place
    if ctype == "realworld":
        flags.append("seductive-detail check: keep ONLY if the photoreal features are the "
                     "thing being learned; otherwise cut (decorative realism harms learning)")
    return flags


def _similar(a: str, b: str) -> bool:
    aw = set(re.findall(r"\w+", a.lower()))
    bw = set(re.findall(r"\w+", b.lower()))
    if not aw or not bw:
        return False
    overlap = len(aw & bw) / len(aw | bw)
    return overlap >= 0.6  # most words shared → effectively duplicate


def route(beat: dict) -> dict:
    bid = beat.get("beat_id", "?")
    if bid in ("INTRO", "OUTRO"):
        ctype = "title"
    else:
        text = " ".join(str(beat.get(k, "")) for k in ("content_type", "visual_key", "narration_text"))
        ctype = beat.get("content_type") if beat.get("content_type") in REC else classify(text)
    text = " ".join(str(beat.get(k, "")) for k in ("visual_key", "narration_text"))
    media, conf, reason = REC[ctype]
    return {
        "beat_id": bid,
        "content_type": ctype,
        "render": media,
        "render_confidence": conf,
        "render_reason": reason,
        "red_flags": red_flags(beat, ctype, media, text),
        "overridden": bool(beat.get("render_override")),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="First-pass media router for a beat sheet.")
    ap.add_argument("target", help="video folder or beat_sheet.json")
    ap.add_argument("--write", action="store_true",
                    help="write render/render_confidence/render_reason back (never clobbers render_override)")
    ap.add_argument("--tag", action="store_true",
                    help="backfill an inferred content_type into beats that lack one (for human review; "
                         "never overwrites an existing content_type; skips beats it can't classify)")
    args = ap.parse_args(argv)

    p = Path(args.target)
    sheet_path = p / "beat_sheet.json" if p.is_dir() else p
    if not sheet_path.exists():
        print(f"[router] beat sheet not found: {sheet_path}", file=sys.stderr)
        return 2
    sheet = json.loads(sheet_path.read_text())
    beats = sheet.get("beats", [])

    print(f"[router] {sheet.get('metadata', {}).get('title', sheet_path.parent.name)}")
    print(f"{'beat':6} {'type':11} {'media':9} {'conf':9} reason / flags")
    print("-" * 92)
    any_flag = False
    for b in beats:
        r = route(b)
        tag = "OVERRIDE" if r["overridden"] else r["render"]
        print(f"{r['beat_id']:6} {r['content_type']:11} {tag:9} {r['render_confidence']:9} {r['render_reason']}")
        for f in r["red_flags"]:
            any_flag = True
            print(f"{'':6} {'':11} {'⚑':9} {'':9} {f}")
        if args.write and not r["overridden"]:
            b["render"] = r["render"]
            b["render_confidence"] = r["render_confidence"]
            b["render_reason"] = r["render_reason"]
        if args.tag and not b.get("content_type") and r["content_type"] != "default":
            b["content_type"] = r["content_type"]
        elif args.tag and r["content_type"] == "default" and not b.get("content_type"):
            print(f"{'':6} {'':11} {'?':9} {'':9} could not classify — set content_type by hand")

    if args.write or args.tag:
        sheet_path.write_text(json.dumps(sheet, indent=2))
        what = " + ".join(([f"render suggestions"] if args.write else []) +
                          (["inferred content_type"] if args.tag else []))
        print(f"\n[router] wrote {what} into {sheet_path} "
              f"(existing content_type / render_override left untouched)")
    print("\n[router] reminder: defaults are best-for-learning, not easiest-to-make. "
          "Override only with a stated design reason. See ../reference/decision-table.md.")
    return 1 if any_flag else 0


if __name__ == "__main__":
    raise SystemExit(main())
