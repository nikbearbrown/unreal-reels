#!/usr/bin/env python3
"""
record_correction.py — the writeback path: an expert's lecture edit becomes
signed evidence in the shared commons (facts/<domain>/facts.json).

When a professor refines the spine ("that definition is wrong, it's X"), the
correction is not just a local text edit — it is trusted-tier, human-authored
evidence. This closes the loop: the 150 experts making 150 books their own are,
as a byproduct, building a signed, cross-referenced fact commons.

Two cases (both reuse facts/extract-facts.py bookkeeping):

  CORRECTION of an existing fact:
    - append a REFUTES evidence record to the old fact  -> recompute -> conflict
    - make_fact() the corrected canonical (tier=textbook, the expert) -> candidate
  NOVEL claim the commons lacked:
    - make_fact() straight from the book + expert as the source

Then, because a HUMAN authored it, we can sign it: verified=true with a
SHA-256 over the exact canonical (the facts/ sign-off mechanism). Edit the fact
later and the hash no longer matches -> signature auto-invalidates. The model is
NEVER allowed down this path; corrections are human acts by construction.

Provenance recorded on every writeback: expert id, book, chapter, and the
lecture beat_id that triggered it — so any fact traces back to the edit that
produced it.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path


def load_facts_module(facts_dir: Path):
    spec = importlib.util.spec_from_file_location("factslib", facts_dir / "extract-facts.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)  # type: ignore
    return mod


def sign(canonical: str, expert: str) -> dict:
    h = hashlib.sha256(canonical.strip().encode("utf-8")).hexdigest()
    return {"verified": True, "verified_by": expert,
            "verified_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "signature_sha256": h}


def record(facts_dir: Path, domain: str, *, corrected: str, expert: str,
           book: str, chapter: str, beat_id: str,
           refutes: str | None, verbatim: str, sign_off: bool):
    fx = load_facts_module(facts_dir)
    sources = fx.load_sources()
    path = facts_dir / domain / "facts.json"
    facts = json.loads(path.read_text()) if path.exists() else []

    # the expert is a trusted, non-openstax source -> strongest corroboration
    citation = {"source": "textbook", "publisher": None, "book": book,
                "module": chapter, "url": None, "verbatim": verbatim,
                "retrieved": time.strftime("%Y-%m-%d"), "verdict": "SUPPORTS",
                "contributed_by": expert, "via_beat": beat_id}

    # 1) if this corrects an existing fact, refute the old one
    if refutes:
        for f in facts:
            if fx.normalize(f["canonical"]) == fx.normalize(refutes):
                f["evidence"].append({**citation, "verbatim": f"Corrected by {expert}: "
                                      f"was '{refutes[:80]}'", "verdict": "REFUTES"})
                fx.recompute_consensus(f, sources)  # -> conflict, needs_review
                break

    # 2) add the corrected/novel claim as a candidate, then optionally sign it
    new = fx.make_fact({"canonical": corrected, "domain": [domain], "stable": True,
                        "category": "CORRECTION"}, citation, "trusted", sources)
    fx.merge_fact(facts, new, sources)          # dedups/append-vote per facts/ rules
    target = next(f for f in facts if fx.normalize(f["canonical"]) == fx.normalize(corrected))
    if sign_off:
        target.update(sign(target["canonical"], expert))
        target["status"] = "human-verified"

    path.write_text(json.dumps(facts, indent=2, ensure_ascii=False))
    return target


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts-dir", required=True)
    ap.add_argument("--domain", required=True)
    ap.add_argument("--corrected", required=True, help="the correct claim (becomes canonical)")
    ap.add_argument("--refutes", default=None, help="the wrong claim it replaces (optional)")
    ap.add_argument("--expert", required=True, help="signer id, e.g. 'Prof. X <email>'")
    ap.add_argument("--book", required=True)
    ap.add_argument("--chapter", required=True)
    ap.add_argument("--beat", required=True, help="lecture beat_id that triggered the edit")
    ap.add_argument("--verbatim", default="", help="supporting passage")
    ap.add_argument("--sign", action="store_true", help="human sign-off (verified=true, hash-pinned)")
    a = ap.parse_args()
    t = record(Path(a.facts_dir).expanduser().resolve(), a.domain,
               corrected=a.corrected, expert=a.expert, book=a.book, chapter=a.chapter,
               beat_id=a.beat, refutes=a.refutes, verbatim=a.verbatim, sign_off=a.sign)
    print(f"[writeback] fact '{t['canonical'][:60]}...' consensus={t['consensus']} "
          f"verified={t.get('verified')}")


if __name__ == "__main__":
    main()
