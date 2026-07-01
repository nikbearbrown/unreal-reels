#!/usr/bin/env python3
"""
tts_audit.py — flag TTS pronunciation risks BEFORE spending render budget.

TTS engines fail at predictable categories, not at random: rare proper nouns,
acronyms that could be read as a word or spelled out, ambiguous symbols and
single-letter variables, ambiguous numerals, and Latin abbreviations. This is a
cheap static pass that flags candidate spans, ranked by risk, so a human only
listen-tests the flagged spans instead of the whole script.

It does NOT fix pronunciation — it produces a worklist. The fix is an inline
respelling placed in each beat's `tts_normalized_text` (the TTS-facing field),
which generate_audio.py reads in preference to `narration_text`. Captions/notes
keep the correct spelling. (eleven_multilingual_v2 ignores phoneme tags, so
spelling substitution / "alias" is the supported route — see SKILL.md.)

Five categories:
  1 proper_noun   rare surnames / place / brand names      (needs wordfreq)
  2 acronym       ALLCAPS; word-read vs letter-read risk
  3 symbol        & % greek letters, single-letter variables used as words
  4 numeral       decimals, ranges, ordinals (NOT plain years)
  5 latin_abbrev  et al., i.e., e.g., vs., cf., etc.

Usage:
    python tts_audit.py path/to/lecture_folder            # scans beat_sheet.json narration
    python tts_audit.py --text script.md                  # scans a plain text/markdown file
    python tts_audit.py path/to/folder --json audit.json  # also write machine-readable report
    python tts_audit.py path/to/folder --seed-dict pron.json   # write a respelling template to fill

wordfreq is optional but strongly recommended (category 1):
    pip install wordfreq
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    from wordfreq import zipf_frequency
    HAVE_WORDFREQ = True
except Exception:
    HAVE_WORDFREQ = False

# --- allowlists: things that look risky but are safe -------------------------
SAFE_ACRONYMS = {"AI", "ZIP", "US", "USA", "UK", "EU", "OK", "TV", "ID", "FAQ",
                 "PDF", "URL", "API", "CPU", "GPU", "HTTP", "PHD"}
# common single letters that ARE words / pronouns
SAFE_SINGLE = {"a", "A", "I"}
VOWELS = set("aeiouAEIOU")

LATIN_ABBREV = re.compile(r"\b(et al\.|i\.e\.|e\.g\.|vs\.?|cf\.|etc\.|et seq\.|ibid\.)", re.I)
DECIMAL = re.compile(r"\b\d+\.\d+\b")
RANGE = re.compile(r"\b\d+\s*[–—-]\s*\d+\b")
ORDINAL = re.compile(r"\b\d+(?:st|nd|rd|th)\b", re.I)
YEAR = re.compile(r"^(1[5-9]\d{2}|20\d{2})$")
ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]{1,}\b")          # 2+ caps (GE, PPV, COMPAS)
SINGLE_VAR = re.compile(r"(?<![A-Za-z'])[a-zA-Z](?![A-Za-z'])")
GREEK_UNICODE = re.compile(r"[Ͱ-Ͽ]")
GREEK_NAME = re.compile(r"\b(alpha|beta|gamma|delta|sigma|lambda|mu|theta|epsilon|rho|phi|psi)\b", re.I)
SYMBOL = re.compile(r"[&%×÷±≤≥≠→←⇒∑∏∫√]")
PROPER = re.compile(r"\b[A-Z][a-z]{2,}(?:'s)?\b")       # Titlecase words (+ possessive)


def pronounceable_as_word(s: str) -> bool:
    """Rough: has a vowel and no run of 3+ consonants -> likely read as a word."""
    if not any(c in VOWELS for c in s):
        return False
    run = 0
    for c in s:
        if c not in VOWELS:
            run += 1
            if run >= 3:
                return False
        else:
            run = 0
    return True


def is_real_word(s: str) -> bool:
    if not HAVE_WORDFREQ:
        return False
    return zipf_frequency(s.lower(), "en") >= 3.0


def scan(text, beat_id, hits):
    """Append (category, string, risk, context, note) records to hits."""
    def ctx(m):
        a, b = max(0, m.start() - 28), min(len(text), m.end() + 28)
        return ("…" + text[a:b].replace("\n", " ") + "…").strip()

    # 5 latin abbrev
    for m in LATIN_ABBREV.finditer(text):
        hits.append(("latin_abbrev", m.group(0), "MEDIUM", beat_id, ctx(m), "expand in tts text: 'and others', 'that is', 'for example', 'versus'"))
    # 4 numerals
    for m in DECIMAL.finditer(text):
        hits.append(("numeral", m.group(0), "MEDIUM", beat_id, ctx(m), "decimal — verify reading (e.g. 'zero point eight')"))
    for m in RANGE.finditer(text):
        hits.append(("numeral", m.group(0), "MEDIUM", beat_id, ctx(m), "range — may render as subtraction; respell 'X to Y'"))
    for m in ORDINAL.finditer(text):
        hits.append(("numeral", m.group(0), "LOW", beat_id, ctx(m), "ordinal — usually fine"))
    # 3 symbols / greek / single-letter vars
    for m in SYMBOL.finditer(text):
        hits.append(("symbol", m.group(0), "MEDIUM", beat_id, ctx(m), "symbol — spell the word in tts text"))
    for m in GREEK_UNICODE.finditer(text):
        hits.append(("symbol", m.group(0), "HIGH", beat_id, ctx(m), "Greek glyph — replace with its spoken name (e.g. 'alpha')"))
    for m in GREEK_NAME.finditer(text):
        hits.append(("symbol", m.group(0), "LOW", beat_id, ctx(m), "Greek name spelled out — usually fine"))
    for m in SINGLE_VAR.finditer(text):
        tok = m.group(0)
        if tok in SAFE_SINGLE:
            continue
        hits.append(("symbol", tok, "MEDIUM", beat_id, ctx(m), "single-letter variable read as a word — verify"))
    # 2 acronyms
    for m in ACRONYM.finditer(text):
        s = m.group(0)
        if s in SAFE_ACRONYMS or YEAR.match(s):
            continue
        # skip CAP fragments inside a respelling like "chool-deh-KOH-vuh"
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if before == "-" or after == "-":
            continue
        if pronounceable_as_word(s) and is_real_word(s):
            risk, note = "HIGH", f"reads as the word '{s.lower()}' — respell letters ('{'.'.join(s)}.') or as intended"
        elif pronounceable_as_word(s):
            risk, note = "MEDIUM", "pronounceable caps — may be word-read; decide letters vs word"
        else:
            risk, note = "MEDIUM", "non-pronounceable caps — likely letter-read; add periods to be safe"
        hits.append(("acronym", s, risk, beat_id, ctx(m), note))
    # 1 proper nouns (needs wordfreq)
    if HAVE_WORDFREQ:
        # skip sentence-initial Titlecase (likely just a capitalized common word)
        for m in PROPER.finditer(text):
            s = m.group(0)
            base = s[:-2] if s.endswith("'s") else s
            before = text[:m.start()].rstrip()
            sentence_initial = (before == "" or before[-1] in ".!?\n")
            z = zipf_frequency(base.lower(), "en")
            if z >= 3.0:
                continue  # common enough
            if sentence_initial and z >= 2.0:
                continue  # probably an ordinary word starting a sentence
            risk = "HIGH" if z == 0.0 else ("HIGH" if z < 2.0 else "MEDIUM")
            note = "rare/unknown proper noun — respell phonetically (CAP the stressed syllable)"
            hits.append(("proper_noun", base, risk, beat_id, ctx(m), f"zipf {z:.1f} — {note}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", help="lecture folder with beat_sheet.json")
    ap.add_argument("--text", help="scan a plain text/markdown file instead")
    ap.add_argument("--json", help="write machine-readable report here")
    ap.add_argument("--seed-dict", help="write a respelling template (pronunciations.json) for HIGH proper nouns/acronyms")
    args = ap.parse_args()

    units = []  # (beat_id, text)
    resolved = set()  # terms already given a respelling in pronunciations.json
    if args.text:
        units = [("(file)", Path(args.text).read_text(encoding="utf-8", errors="replace"))]
    elif args.folder:
        folder = Path(args.folder)
        sheet = json.loads((folder / "beat_sheet.json").read_text())
        # audit the SOURCE script (narration_text), not the respelled audio text
        units = [(b["beat_id"], b.get("narration_text") or "") for b in sheet["beats"]]
        pron = folder / "pronunciations.json"
        if pron.exists():
            resolved = {t for t, v in json.loads(pron.read_text()).items() if v and v != t}
    else:
        ap.error("give a lecture folder or --text FILE")

    hits = []
    for bid, text in units:
        scan(text, bid, hits)

    # aggregate by (category, lowercased string)
    agg = defaultdict(lambda: {"count": 0, "risk": "LOW", "beats": set(), "ctx": "", "note": ""})
    order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    for cat, s, risk, bid, ctx, note in hits:
        k = (cat, s)
        a = agg[k]
        a["count"] += 1
        a["beats"].add(bid)
        if order[risk] >= order[a["risk"]]:
            a["risk"] = risk
        if not a["ctx"]:
            a["ctx"] = ctx
        a["note"] = note

    if not HAVE_WORDFREQ:
        print("[note] wordfreq not installed — proper-noun detection (category 1) is OFF.")
        print("       pip install wordfreq   (then re-run for the rare-name pass)\n")

    buckets = {"HIGH": [], "MEDIUM": [], "LOW": []}
    n_resolved = 0
    for (cat, s), a in agg.items():
        if s in resolved:
            n_resolved += 1
            continue  # already respelled in pronunciations.json
        buckets[a["risk"]].append((cat, s, a))
    for level in ("HIGH", "MEDIUM", "LOW"):
        rows = sorted(buckets[level], key=lambda r: (-r[2]["count"], r[0], r[1]))
        if not rows:
            continue
        print(f"{'='*70}\n{level} RISK ({len(rows)})\n{'='*70}")
        for cat, s, a in rows:
            beats = ",".join(sorted(a["beats"]))
            print(f'  [{cat}] "{s}"  ×{a["count"]}  ({beats})')
            print(f"        {a['note']}")

    high_terms = sorted({s for (cat, s), a in agg.items()
                         if a["risk"] == "HIGH" and cat in ("proper_noun", "acronym")})
    if args.seed_dict and high_terms:
        tmpl = {t: "" for t in high_terms}  # human/LLM fills the respelling
        Path(args.seed_dict).write_text(json.dumps(tmpl, indent=2, ensure_ascii=False))
        print(f"\n[ok] wrote respelling template -> {args.seed_dict} "
              f"({len(high_terms)} terms to fill)")

    if args.json:
        out = [{"category": cat, "string": s, "risk": a["risk"], "count": a["count"],
                "beats": sorted(a["beats"]), "context": a["ctx"], "note": a["note"]}
               for (cat, s), a in agg.items()]
        out.sort(key=lambda r: (-order[r["risk"]], -r["count"]))
        Path(args.json).write_text(json.dumps(out, indent=2, ensure_ascii=False))
        print(f"[ok] wrote {args.json}")

    resolved_note = f" · {n_resolved} resolved (in pronunciations.json)" if n_resolved else ""
    print(f"\nsummary: {len(buckets['HIGH'])} high · {len(buckets['MEDIUM'])} medium · "
          f"{len(buckets['LOW'])} low  (unique spans){resolved_note}")


if __name__ == "__main__":
    main()
