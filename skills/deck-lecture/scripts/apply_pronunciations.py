#!/usr/bin/env python3
"""
apply_pronunciations.py — bake respellings into the TTS-facing text only.

Reads a pronunciations.json map  {"Chouldechova": "shool-deh-KOH-vah", ...}
and, for every beat, writes `tts_normalized_text` = narration_text with each
mapped term replaced by its respelling (whole-word, case-sensitive, possessive
's preserved). `narration_text` is NEVER modified, so captions and speaker notes
keep the correct spelling; only ElevenLabs sees the respelling.

generate_audio.py already prefers tts_normalized_text over narration_text, and
align_captions.py displays narration_text — so this is the whole integration.

Run AFTER you have edited pronunciations.json, BEFORE generate_audio.py.
Re-run any time the dictionary or scripts change (idempotent: rebuilds
tts_normalized_text from narration_text each time).

Usage:
    python apply_pronunciations.py path/to/lecture_folder
    python apply_pronunciations.py path/to/folder --dict pronunciations.json --dry-run
"""
import argparse
import json
import re
from pathlib import Path


def build_replacer(mapping):
    # longest terms first so multi-word entries win over their parts
    terms = sorted([t for t in mapping if t and mapping[t]], key=len, reverse=True)
    if not terms:
        return None
    pat = re.compile(r"(?<![\w])(" + "|".join(re.escape(t) for t in terms) + r")(\'s)?(?![\w])")

    def repl(m):
        return mapping[m.group(1)] + (m.group(2) or "")
    return lambda s: pat.sub(repl, s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--dict", default="pronunciations.json",
                    help="filename inside the folder (default pronunciations.json)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    folder = Path(args.folder)
    sheet_path = folder / "beat_sheet.json"
    sheet = json.loads(sheet_path.read_text())
    dict_path = folder / args.dict
    if not dict_path.exists():
        raise SystemExit(f"[err] no {dict_path} — run tts_audit.py --seed-dict first, then fill it.")
    mapping = json.loads(dict_path.read_text())

    # Respelling-form guard: ALL-CAPS runs get letter-spelled ("KOH" -> "K O H")
    # and hyphens get read as pauses (the name comes out chopped). For v2 aliases,
    # use plain word-like spelling: "Shooldekova", not "chool-deh-KOH-vuh".
    risky = []
    for term, val in mapping.items():
        if not val or val == term:
            continue
        if re.search(r"[A-Z]{2,}", val) or "-" in val:
            risky.append((term, val))
    if risky:
        print("[warn] these respellings will likely mis-speak (CAPS = letter-spelled, "
              "hyphens = pauses). Use plain word-like spelling instead:")
        for term, val in risky:
            print(f"        {term!r}: {val!r}")
        print()

    replace = build_replacer(mapping)
    if replace is None:
        raise SystemExit("[err] pronunciations.json has no filled-in respellings yet.")

    changed = 0
    for b in sheet["beats"]:
        nar = b.get("narration_text", "")
        tts = replace(nar)
        if tts != nar:
            changed += 1
            hit = [t for t in mapping if mapping[t] and re.search(r"(?<![\w])" + re.escape(t) + r"(\'s)?(?![\w])", nar)]
            print(f"  {b['beat_id']}: respelled {', '.join(sorted(set(hit)))}")
        # always set tts_normalized_text (= narration when no terms present),
        # so it stays in sync if narration_text was edited
        b["tts_normalized_text"] = tts

    if args.dry_run:
        print(f"\n[dry-run] {changed} beats would get respellings. No file written.")
        return
    sheet_path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False))
    print(f"\n[ok] wrote tts_normalized_text on {len(sheet['beats'])} beats "
          f"({changed} contain respellings). narration_text untouched.")


if __name__ == "__main__":
    main()
