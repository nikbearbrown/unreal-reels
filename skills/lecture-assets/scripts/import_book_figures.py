#!/usr/bin/env python3
"""
import_book_figures.py — pull the book's ALREADY-RENDERED chapter figures into the
asset pool as candidates. Many textbooks ship per-chapter figures (SVG/PNG/JPG) in
an images/ dir — those are pre-vetted, on-brand assets; the pool should include them
before generating anything new.

Copies <book>/images/<chapter>-fig-*.{svg,png,jpg} into
<lecture_folder>/assets/book/ and registers one manifest entry per figure number
(SVG preferred), titled from the chapter's "Figure N — …" prompts where present.

Usage:
    python import_book_figures.py <lecture_folder>
    python import_book_figures.py <lecture_folder> --images /path/to/images --chapter <slug>
"""
import argparse
import json
import re
import shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="…/lectures/<chapter>")
    ap.add_argument("--images", default=None, help="book images/ dir (default: ../../images)")
    ap.add_argument("--chapter", default=None, help="chapter slug (default: folder name)")
    args = ap.parse_args()

    lec = Path(args.folder).resolve()
    slug = args.chapter or lec.name
    book = lec.parent.parent
    images = Path(args.images) if args.images else book / "images"
    out = lec / "assets" / "book"
    out.mkdir(parents=True, exist_ok=True)

    # titles from the chapter's "Figure N — title" lines
    titles = {}
    ch_md = book / "chapters" / f"{slug}.md"
    if ch_md.exists():
        for m in re.finditer(r"^#+\s*Figure\s+(\d+)\s*[—:-]\s*(.+)$", ch_md.read_text(errors="replace"), re.M):
            titles[int(m.group(1))] = m.group(2).strip().rstrip(".")

    # gather figure files by number, preferring svg > png > jpg for the manifest ref
    by_num = {}
    for f in sorted(images.glob(f"{slug}-fig-*")):
        m = re.search(r"-fig-(\d+)\.(svg|png|jpg|jpeg)$", f.name)
        if not m:
            continue
        by_num.setdefault(int(m.group(1)), []).append(f)

    manifest = lec / "assets" / "assets.json"
    data = json.loads(manifest.read_text()) if manifest.exists() else {"assets": []}
    data.setdefault("assets", [])
    pref = {"svg": 0, "png": 1, "jpg": 2, "jpeg": 2}
    added = 0
    for num in sorted(by_num):
        files = sorted(by_num[num], key=lambda p: pref.get(p.suffix.lstrip("."), 9))
        for f in files:
            shutil.copy2(f, out / f.name)
        best = files[0]
        aid = f"{slug}-book-fig-{num:02d}"
        concept = titles.get(num, f"book figure {num}")
        entry = {"id": aid, "kind": "figure", "concept": concept, "source": "book",
                 "file": f"book/{best.name}", "status": "candidate",
                 "notes": "shipped with the book; formats: " + ", ".join(p.suffix.lstrip(".") for p in files)}
        data["assets"] = [a for a in data["assets"] if a.get("id") != aid]
        data["assets"].append(entry)
        added += 1

    manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"[ok] imported {added} book figures into {out} (svg preferred, all formats copied)")
    for num in sorted(by_num):
        print(f"    fig-{num:02d}: {titles.get(num, '(untitled)')}")


if __name__ == "__main__":
    main()
