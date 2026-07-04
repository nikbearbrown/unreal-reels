#!/usr/bin/env python3
"""
grounding_check.py — the spine's fidelity gate (Tier A + Tier B).

Answers the top quality bar in THE-SPINE.md: does the lecture narration say
anything the source doesn't support? Produces the professor's triage list.

Two tiers, cheapest first:

  TIER A — fidelity to THIS chapter (anti-hallucination).
    For each claim-bearing narration sentence, is it grounded in the source
    chapter.md the lecture was built from? A claim IN the chapter is safe; a
    claim NOT in the chapter is a candidate hallucination -> FLAG.

  TIER B — corroboration by the shared commons (facts/<domain>/facts.json).
    Match the claim against the fact dictionary and read its earned status:
      verified / agreement  -> corroborated (safe elaboration even if not verbatim)
      unverified            -> weak; note it
      conflict              -> the commons already knows this is contested -> FLAG hard
      no match              -> commons is silent; rely on Tier A

  A claim IN the chapter but CONFLICT in the commons is the most interesting
  flag: the book itself may be wrong/dated. Surface it — don't resolve it.

WHERE THE MODEL IS ALLOWED (same rule as facts/): matching a paraphrase to a
fact is paraphrase-recall, which lexical similarity under-recalls (facts/README
defers embeddings). So: deterministic lexical prefilter here (reusing the facts
helpers); an optional LLM adjudicator runs ONLY on the near-miss band and it
FLAGS, never decides or verifies. This script implements the deterministic pass
and emits the near-miss band for optional adjudication.

Reuses facts/extract-facts.py bookkeeping (normalize, wording_similarity, ...)
so there is ONE source of truth for matching + consensus.

Output: writes `grounding.json` (per-beat verdicts + the flags list) into the
lecture folder and returns a fidelity summary for qc_report.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

# ── reuse the facts/ bookkeeping (single source of truth) ────────────────────
def load_facts_module(facts_dir: Path):
    spec = importlib.util.spec_from_file_location("factslib", facts_dir / "extract-facts.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


# ── claim extraction (deterministic, conservative) ──────────────────────────
# RECALL-FIRST: a missed claim is a missed hallucination, so we treat every
# declarative sentence as a candidate claim UNLESS it is clearly a teaching aside
# (a question, or a second-person/imperative framing move). It is safe to
# over-collect: a non-claim just matches nothing and gets Tier-A grounded against
# the chapter. It is NOT safe to under-collect (the earlier copula-only regex
# silently dropped actively-phrased fabrications). The robust version of claim
# extraction is an LLM pass (low-tier, flags only); this is the deterministic floor.
SKIP_STARTS = ("notice", "let's", "let us", "so let", "now let", "think about",
               "imagine", "consider", "remember", "note that", "here's the",
               "that's why", "this is why", "as we", "as you")


def claim_sentences(text: str) -> list[str]:
    out = []
    for s in re.split(r"(?<=[.!?])\s+", (text or "").strip()):
        s = s.strip()
        if len(s.split()) < 5 or s.endswith("?"):
            continue
        low = s.lower()
        if any(low.startswith(w) for w in SKIP_STARTS):
            continue
        out.append(s)
    return out


# ── the check ────────────────────────────────────────────────────────────────
def build_index(facts: list[dict], terms: list[dict], fx):
    """Precompute normalized canonicals for fast lexical matching."""
    idx = []
    for f in facts:
        idx.append((fx.normalize(f["canonical"]), f))
    for t in terms:  # a glossary definition is a single-source candidate too
        if t.get("definition"):
            idx.append((fx.normalize(t["definition"]), {"canonical": t["definition"],
                        "consensus": "unverified", "verified": False,
                        "evidence": [{"source": "wikipedia", "url": t.get("url")}],
                        "_from": "terms"}))
    return idx


def best_match(sentence: str, idx, fx, hi=0.62, lo=0.45):
    """Return (fact, score, band) — band in {hit, near, miss}."""
    ns = fx.normalize(sentence)
    best, best_s = None, 0.0
    for norm, fact in idx:
        s = 1.0 if norm == ns else fx.wording_similarity(ns, norm)
        if s > best_s:
            best, best_s = fact, s
    band = "hit" if best_s >= hi else "near" if best_s >= lo else "miss"
    return best, round(best_s, 3), band


def grade(sentence: str, chapter_norm: str, fact, score, band, fx) -> dict:
    in_chapter = fx.normalize(sentence)[:80] in chapter_norm or \
        fx.wording_similarity(fx.normalize(sentence), "") if False else \
        _chapter_supports(sentence, chapter_norm, fx)
    consensus = (fact or {}).get("consensus")
    verified = (fact or {}).get("verified")

    # decision table (Tier A gates hallucination; Tier B adds corroboration/contest)
    if band == "hit" and consensus == "conflict":
        verdict, flag = "contested", "commons marks this claim CONFLICT — expert must adjudicate"
    elif not in_chapter and band != "hit":
        verdict, flag = "unverifiable", "not supported by the source chapter and no commons match — possible hallucination"
    elif not in_chapter and (verified or consensus == "agreement"):
        verdict, flag = "elaboration", None  # not in chapter but corroborated -> safe add
    elif in_chapter and band == "hit" and (verified or consensus == "agreement"):
        verdict, flag = "grounded+corroborated", None
    elif in_chapter:
        verdict, flag = "grounded", None
    else:
        verdict, flag = "review", "weak/uncertain support — spot-check"
    return {"sentence": sentence, "in_chapter": in_chapter,
            "match_score": score, "match_band": band,
            "match_consensus": consensus, "match_canonical": (fact or {}).get("canonical"),
            "verdict": verdict, "flag": flag}


def _chapter_supports(sentence: str, chapter_norm: str, fx, thresh=0.5) -> bool:
    """Cheap Tier-A: does the chapter contain a sufficiently-similar window?"""
    ns = fx.normalize(sentence)
    key = " ".join(ns.split()[:8])
    if key and key in chapter_norm:
        return True
    # fall back to a token-overlap ratio against the whole chapter
    toks = set(ns.split())
    if not toks:
        return False
    hit = sum(1 for t in toks if t in chapter_norm)
    return hit / len(toks) >= thresh


def run(folder: Path, facts_dir: Path, domain: str, chapter_md: Path | None):
    fx = load_facts_module(facts_dir)
    dom = facts_dir / domain
    facts = json.loads((dom / "facts.json").read_text()) if (dom / "facts.json").exists() else []
    terms = json.loads((dom / "terms.json").read_text()) if (dom / "terms.json").exists() else []
    idx = build_index(facts, terms, fx)

    chapter_norm = fx.normalize(chapter_md.read_text()) if chapter_md and chapter_md.exists() else ""
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    beats = sheet.get("beats", [])

    results, flags, near = [], [], []
    for b in beats:
        for sent in claim_sentences(b.get("narration_text", "")):
            fact, score, band = best_match(sent, idx, fx)
            g = grade(sent, chapter_norm, fact, score, band, fx)
            g["beat_id"] = b.get("beat_id")
            results.append(g)
            if g["flag"]:
                flags.append({"beat_id": g["beat_id"], "sentence": sent,
                              "verdict": g["verdict"], "flag": g["flag"],
                              "match": g["match_canonical"]})
            if band == "near":  # hand to optional LLM adjudicator
                near.append({"beat_id": g["beat_id"], "sentence": sent,
                             "candidate": g["match_canonical"], "score": score})

    out = {"chapter": folder.name, "domain": domain,
           "claims_checked": len(results), "flags": flags,
           "near_misses_for_adjudication": near,
           "fidelity": {
               "unverifiable": sum(1 for r in results if r["verdict"] == "unverifiable"),
               "contested": sum(1 for r in results if r["verdict"] == "contested"),
               "review": sum(1 for r in results if r["verdict"] == "review"),
               "grounded": sum(1 for r in results if r["verdict"].startswith("grounded")),
           },
           "results": results}
    (folder / "grounding.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="lecture folder (has beat_sheet.json)")
    ap.add_argument("--facts-dir", required=True, help="path to the facts/ repo")
    ap.add_argument("--domain", required=True, help="facts subdomain, e.g. physics")
    ap.add_argument("--chapter", default=None, help="source chapter.md (Tier-A grounding)")
    args = ap.parse_args()
    out = run(Path(args.folder).expanduser().resolve(),
              Path(args.facts_dir).expanduser().resolve(),
              args.domain,
              Path(args.chapter).expanduser() if args.chapter else None)
    fd = out["fidelity"]
    print(f"[grounding] {out['claims_checked']} claims · "
          f"{fd['unverifiable']} unverifiable · {fd['contested']} contested · "
          f"{fd['review']} review · {len(out['near_misses_for_adjudication'])} near-misses")
    print(f"[grounding] wrote {Path(args.folder)/'grounding.json'}")


if __name__ == "__main__":
    main()
