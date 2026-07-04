#!/usr/bin/env python3
"""
build_plan.py — Phase 0 of the slide-deck skill (the gate that matters).

chapter.md  (+ assets/assets.json)  ->  deck_plan.json  (a reviewable STARTER)

This does the mechanical part honestly and stops: it slices the chapter into an
ordered slide plan (title, section dividers, concept slides, equation slides,
figure/chart candidates, close) and seeds each slide's speaker_notes from the
prose. It does NOT pretend to write good teaching notes or choose the perfect
slide set — that is the human's job at the Phase-0 gate. A regex can cut a chapter
into slides; it cannot summarize or motivate. Treat the output as scaffolding to
edit, not a finished deck.

What it fills automatically:
  - title slide from the `# Chapter N — Title` line + TL;DR / italic dek
  - a `section` divider + `concept` slide per top-level `##` heading
  - an `equation` slide per `$$…$$` display block (tex filled; plain/values TODO)
  - a `figure` candidate per `![alt](…fig-NN…)` image (alt -> caption)
  - speaker_notes seeded from the first sentence(s) of each section
  - asset_ref suggestions matched against assets.json concepts (best-effort)

Everything the author must still write is marked `TODO:` in the field.

Pure stdlib. No deps.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# At most this many full equation slides per section; extra display-equations
# fold into the first slide's derivation_steps (see build()). Keeps equation-dense
# chapters from ballooning into a wall of one-equation slides.
MAX_EQ_PER_SECTION = 2

DISPLAY_EQ = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
IMG = re.compile(r"!\[(.*?)\]\((.*?)\)")
FIGCAP = re.compile(r"^\*Figure\s+([\d.]+)\s*[—-]\s*(.*?)\*", re.MULTILINE)


def first_sentences(text: str, n: int = 2) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(parts[:n]).strip()


def latex_from_dollar(md: str) -> str:
    """Convert an inline chapter equation to a KaTeX-ready string (strip $$)."""
    return md.strip().replace("\n", " ")


def split_sections(md: str) -> list[tuple[str, str]]:
    """Return [(heading, body)] for each top-level `## ` section, in order."""
    out = []
    cur_h, cur_body = None, []
    for line in md.splitlines():
        m = re.match(r"^##\s+(.*)$", line)
        if m and not line.startswith("###"):
            if cur_h is not None:
                out.append((cur_h, "\n".join(cur_body)))
            cur_h, cur_body = m.group(1).strip(), []
        elif cur_h is not None:
            cur_body.append(line)
    if cur_h is not None:
        out.append((cur_h, "\n".join(cur_body)))
    return out


# sections that are usually not lecture slides (skip by default; author can restore)
SKIP_SECTIONS = {"exercises", "prompts", "ai wayback machine", "two botspeak pillars",
                 "the shape of the rest", "llm exercise"}


def match_asset(concept: str, assets: list[dict]) -> str | None:
    """Best-effort: pick a candidate asset whose concept shares words with `concept`."""
    words = set(re.findall(r"[a-z]{4,}", concept.lower()))
    best, best_score = None, 0
    for a in assets:
        if a.get("status") != "candidate":
            continue
        aw = set(re.findall(r"[a-z]{4,}", (a.get("concept", "")).lower()))
        score = len(words & aw)
        if score > best_score:
            best, best_score = a.get("id"), score
    return best if best_score >= 2 else None


def build(md: str, assets: list[dict], chapter_slug: str, chnum: str) -> dict:
    slides: list[dict] = []

    # ── title ────────────────────────────────────────────────────────────────
    title_m = re.search(r"^#\s+(.*)$", md, re.MULTILINE)
    raw_title = title_m.group(1).strip() if title_m else chapter_slug
    # "Chapter 7 — Fairness Metrics: Choosing…" -> headline = the part after em dash
    headline = re.sub(r"^Chapter\s+\d+\s*[—-]\s*", "", raw_title).strip()
    dek_m = re.search(r"^\*(.+?)\*\s*$", md, re.MULTILINE)
    subtitle = dek_m.group(1).strip() if dek_m else ""
    slides.append({
        "archetype": "title", "label": "Title",
        "eyebrow": f"AI Engineering · Chapter {chnum}",
        "headline": headline,
        "subtitle": subtitle,
        "speaker_notes": f"TODO: open the lecture. {first_sentences(subtitle or headline, 1)}",
    })

    # ── one section divider + concept per top-level heading; equations inline ──
    part_no = 0
    for heading, body in split_sections(md):
        if heading.lower().strip() in SKIP_SECTIONS or heading.lower().startswith("tl;dr"):
            continue
        part_no += 1
        part_words = ["one", "two", "three", "four", "five", "six", "seven",
                      "eight", "nine", "ten", "eleven", "twelve"]
        pw = part_words[part_no - 1] if part_no <= len(part_words) else str(part_no)
        slides.append({
            "archetype": "section", "label": heading,
            "part": f"Part {pw}", "headline": heading,
            "subtitle": "TODO: one line on what this part establishes.",
            "speaker_notes": "Section divider.",
        })

        # concept slide seeded from the section's opening prose
        intro = first_sentences(re.sub(r"[#*`|]", "", body), 3)
        ref = match_asset(heading, assets)
        concept = {
            "archetype": "concept", "label": heading[:60],
            "eyebrow": heading, "headline": "TODO: a sharp claim, not the heading.",
            "bullets": [b for b in [first_sentences(re.sub(r"[#*`|]", "", p), 1)
                                    for p in body.split("\n\n") if p.strip()][:3] if b],
            "speaker_notes": intro or f"TODO: explain {heading}.",
        }
        if ref:
            concept["asset_ref"] = ref
        slides.append(concept)

        # equation slides — CONSOLIDATE. A section with a 10-step derivation should
        # NOT become 10 slides (that made Ch.2 balloon to 72). Emit at most
        # MAX_EQ_PER_SECTION full equation slides; the rest fold into the primary
        # slide's `derivation_steps` (a tangent, not a slide each). The author can
        # still split one back out at the Phase-0 gate if a step deserves its own beat.
        eqs = [latex_from_dollar(e) for e in DISPLAY_EQ.findall(body)]
        for i, tex in enumerate(eqs[:MAX_EQ_PER_SECTION]):
            eq_slide = {
                "archetype": "equation", "label": f"{heading} — equation",
                "eyebrow": "Equation", "headline": "TODO: name the equation",
                "subhead": "TODO: one line on what it is a statement about",
                "tex": tex,
                "plain": "TODO: plain-terms sentence.",
                "values_claim": "TODO: the contestable value the equation encodes.",
                "tangent": {
                    "lhs": "TODO", "rhs": "TODO", "claim": "TODO",
                    "glossary": [], "example": {}, "values_claim": "TODO",
                    "reentry": "TODO: hand back to the main argument.",
                },
                "speaker_notes": "TODO: expand into an equation tangent (see EQUATIONS.md).",
            }
            # fold the remaining derivation steps into the FIRST equation slide
            if i == 0 and len(eqs) > MAX_EQ_PER_SECTION:
                eq_slide["derivation_steps"] = eqs[MAX_EQ_PER_SECTION:]
                eq_slide["_note"] = (f"{len(eqs)} display equations in this section were "
                                     f"consolidated to {MAX_EQ_PER_SECTION}; extra steps in "
                                     f"derivation_steps. Split back out only if a step earns a beat.")
            slides.append(eq_slide)

        # figure candidates
        for alt, path in IMG.findall(body):
            if "images/" not in path and "fig" not in path.lower():
                continue
            ref = match_asset(alt, assets)
            fig = {
                "archetype": "figure", "label": f"Figure — {heading[:40]}",
                "eyebrow": "Figure", "headline": "TODO: what the figure shows",
                "src": f"TODO: pick from pool ({ref})" if ref else "TODO: bind a pool asset",
                "caption": alt, "alt": alt,
                "speaker_notes": alt or "TODO: describe the figure.",
            }
            if ref:
                fig["asset_ref"] = ref
            slides.append(fig)

    # ── close ─────────────────────────────────────────────────────────────────
    slides.append({
        "archetype": "close", "label": "Close",
        "eyebrow": "TODO: the takeaway eyebrow",
        "headline": "TODO: the one line to leave them with.",
        "body": "TODO: synthesize the chapter in two sentences.",
        "next": "TODO: tease the next chapter.",
        "speaker_notes": "TODO: closing narration.",
    })

    return {
        "metadata": {
            "chapter": chapter_slug,
            "chapter_number": chnum,
            "title": headline,
            "course_eyebrow": f"AI Engineering · Chapter {chnum}",
            "voice_id": "TyW6NH39JcFb5M3xdIIk",
            "runtime_from": "TODO: abs path to a lecture folder that has support.js, deck-stage.js, _ds/",
            "ds_css": None,
            "note": "STARTER plan — every TODO must be authored before emit. Review at the Phase-0 gate.",
        },
        "slides": slides,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chapter", help="path to chapter.md")
    ap.add_argument("assets", nargs="?", default=None, help="path to assets/assets.json (optional)")
    ap.add_argument("-o", "--out", required=True, help="output deck_plan.json path")
    args = ap.parse_args()

    ch = Path(args.chapter).expanduser()
    md = ch.read_text(encoding="utf-8")
    slug = ch.stem
    m = re.search(r"(\d{1,2})", slug)
    chnum = m.group(1).zfill(2) if m else "00"

    assets = []
    if args.assets and Path(args.assets).expanduser().exists():
        assets = json.loads(Path(args.assets).expanduser().read_text()).get("assets", [])

    plan = build(md, assets, slug, chnum)
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    n = len(plan["slides"])
    todos = json.dumps(plan).count("TODO")
    print(f"[ok] wrote {out}")
    print(f"[ok] {n} slide stubs | {todos} TODOs to author")
    print("[gate] Phase 0 — review/rewrite the plan (esp. speaker_notes) BEFORE emit_deck.py.")


if __name__ == "__main__":
    main()
