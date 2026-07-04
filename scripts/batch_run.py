#!/usr/bin/env python3
"""
batch_run.py — fleet driver over many chapters / many books (the 150-book layer).

Walks books, runs silent_run.py per chapter, and rolls every chapter's
qc_report.json + decision_log.json into ONE triage manifest ranked worst-first —
so a human (or 150 volunteers) reviews by exception, not by watching everything.

  batch_run.py <book> [<book> ...]           run every chapter of each book
  batch_run.py <book> --chapters 02 03 07    just these
  batch_run.py --all books/*/                shell-expanded list
  batch_run.py <book> --manifest-only        just re-roll the dashboard, no runs

Locally this is a simple loop; on the AICR cluster each (book,chapter) is one
Slurm array task calling silent_run.py — chapters are embarrassingly parallel.
This script's job is the same either way: produce fleet_manifest.json.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SILENT = REPO / "scripts" / "silent_run.py"


def chapters_of(book: Path, only: list[str] | None) -> list[Path]:
    chs = sorted((book / "chapters").glob("*.md"))
    # skip obvious non-lecture front/back matter by default
    chs = [c for c in chs if not c.stem.startswith(("00-front", "00-preface", "99-", "97-"))]
    if only:
        keep = []
        for c in chs:
            if any(c.stem == o or c.stem.startswith(o) for o in only):
                keep.append(c)
        return keep
    return chs


def roll_manifest(books: list[Path], out: Path):
    rows = []
    for book in books:
        ldir = book / "lectures"
        if not ldir.is_dir():
            continue
        for folder in sorted(ldir.iterdir()):
            qc = folder / "qc_report.json"
            dl = folder / "decision_log.json"
            if not qc.exists() and not dl.exists():
                continue
            row = {"book": book.name, "chapter": folder.name,
                   "score": None, "verdict": "not-run", "runtime_s": None,
                   "blocked_on": None, "path": str(folder)}
            if qc.exists():
                q = json.loads(qc.read_text())
                row.update(score=q.get("score"), verdict=q.get("verdict"),
                           runtime_s=q.get("runtime_s"), blocked_on=q.get("blocked_on"))
            elif dl.exists():
                d = json.loads(dl.read_text())
                row["blocked_on"] = d.get("blocked_on")
                row["verdict"] = "blocked" if d.get("blocked_on") else "in-progress"
            rows.append(row)
    # worst-first: unscored/blocked first, then ascending score
    rows.sort(key=lambda r: (r["score"] is not None, r["score"] if r["score"] is not None else -1))
    manifest = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "n": len(rows),
                "watchable": sum(1 for r in rows if (r["score"] or 0) >= 70),
                "blocked": sum(1 for r in rows if r["verdict"] == "blocked"),
                "rows": rows}
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("books", nargs="+", help="one or more book dirs")
    ap.add_argument("--chapters", nargs="*", help="chapter stems/numbers to limit to")
    ap.add_argument("--runtime", default=None, help="runtime dir passed through to silent_run")
    ap.add_argument("--manifest-only", action="store_true")
    ap.add_argument("--manifest", default=None, help="output manifest path (default: ./fleet_manifest.json)")
    args = ap.parse_args()

    books = [Path(b).expanduser().resolve() for b in args.books]
    out = Path(args.manifest).expanduser() if args.manifest else Path.cwd() / "fleet_manifest.json"

    if not args.manifest_only:
        for book in books:
            for ch in chapters_of(book, args.chapters):
                cmd = [sys.executable, str(SILENT), str(book), "--chapter", ch.stem]
                if args.runtime:
                    cmd += ["--runtime", args.runtime]
                print(f"[batch] {book.name}/{ch.stem}")
                subprocess.run(cmd)

    m = roll_manifest(books, out)
    print(f"[batch] manifest: {out}")
    print(f"[batch] {m['n']} chapters · {m['watchable']} watchable · {m['blocked']} blocked on an agent slot")


if __name__ == "__main__":
    main()
