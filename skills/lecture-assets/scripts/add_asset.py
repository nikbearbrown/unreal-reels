#!/usr/bin/env python3
"""
add_asset.py — register (upsert) an asset in a chapter's assets/assets.json pool.

Usage:
    python add_asset.py <lecture_folder> --id ch02-base-rate-icon-array \
        --kind figure --concept "base rates dominate positive tests" \
        --source cajal --file svg/base-rate-icon-array.svg \
        --notes "icon array of 1000 people"

kind: figure (SVG) | chart (live D3/HTML) | doodle (candidate; --file optional)
Everything registers as status "candidate" (nothing is forced).
"""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="the lecture folder (…/lectures/<chapter>)")
    ap.add_argument("--id", required=True)
    ap.add_argument("--kind", required=True, choices=["figure", "chart", "doodle"])
    ap.add_argument("--concept", required=True)
    ap.add_argument("--source", default="authored")
    ap.add_argument("--file", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--status", default="candidate")
    args = ap.parse_args()

    path = Path(args.folder) / "assets" / "assets.json"
    data = json.loads(path.read_text()) if path.exists() else {"assets": []}
    data.setdefault("assets", [])
    entry = {
        "id": args.id, "kind": args.kind, "concept": args.concept,
        "source": args.source, "file": args.file, "status": args.status,
        "notes": args.notes,
    }
    # upsert by id
    data["assets"] = [a for a in data["assets"] if a.get("id") != args.id]
    data["assets"].append(entry)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    n = len(data["assets"])
    by = {}
    for a in data["assets"]:
        by[a["kind"]] = by.get(a["kind"], 0) + 1
    print(f"[ok] {args.id} registered ({args.kind}) — pool now {n}: "
          + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))


if __name__ == "__main__":
    main()
