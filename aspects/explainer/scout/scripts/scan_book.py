#!/usr/bin/env python3
"""
scan_book.py — prepare a book for scouting.

Creates <book>/vids/ and writes <book>/vids/_chapters.json, a manifest of the
book's chapters (path, title, word count, image count) so the scout knows exactly
what to read. It does NOT generate ideas — that is the model's job, by reading the
chapters. This just lays out the worktable.

Usage:
    python scan_book.py path/to/quantum-mechanics-vol1
    python scan_book.py --all path/to/books-root      # every book folder under root
"""
import argparse
import json
import re
import sys
from pathlib import Path


def book_title(book: Path) -> str:
    meta = book / "metadata.yaml"
    title = subtitle = ""
    if meta.exists():
        for line in meta.read_text(errors="ignore").splitlines():
            m = re.match(r'\s*title:\s*"?(.+?)"?\s*$', line)
            if m and not title:
                title = m.group(1)
            m = re.match(r'\s*subtitle:\s*"?(.+?)"?\s*$', line)
            if m and not subtitle:
                subtitle = m.group(1)
    base = title or book.name
    return f"{base} — {subtitle}" if subtitle else base


def chapter_title(md: Path) -> str:
    for line in md.read_text(errors="ignore").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    # fall back to a tidied filename
    return md.stem.replace("-", " ").title()


def scan_one(book: Path) -> dict:
    chapters_dir = book / "chapters"
    if not chapters_dir.is_dir():
        return {}
    vids = book / "vids"
    vids.mkdir(exist_ok=True)

    entries = []
    for md in sorted(chapters_dir.glob("*.md")):
        name = md.stem
        # skip front/back matter
        if any(k in name.lower() for k in ("frontmatter", "back-matter", "backmatter")):
            continue
        text = md.read_text(errors="ignore")
        entries.append({
            "file": str(md.relative_to(book)),
            "path": str(md),
            "title": chapter_title(md),
            "words": len(text.split()),
            "images": text.count("![") ,
        })

    manifest = {
        "book": book.name,
        "book_title": book_title(book),
        "chapter_count": len(entries),
        "chapters": entries,
    }
    (vids / "_chapters.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return manifest


def report(manifest: dict):
    if not manifest:
        print("[skip] no chapters/ folder")
        return
    print(f"[ok] {manifest['book_title']}  ({manifest['chapter_count']} chapters)")
    print(f"     vids/ ready, manifest written to vids/_chapters.json")
    for c in manifest["chapters"]:
        print(f"       {c['file']:60}  {c['words']:>5}w  {c['images']:>2} img  {c['title']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare a book (or all books) for scouting.")
    ap.add_argument("path", help="A book folder, or a books root with --all")
    ap.add_argument("--all", action="store_true", help="Treat path as a root; scan every book folder under it")
    args = ap.parse_args()

    root = Path(args.path).expanduser().resolve()
    if args.all:
        books = [p for p in sorted(root.iterdir()) if (p / "chapters").is_dir()]
        if not books:
            print(f"[err] no book folders (with chapters/) under {root}", file=sys.stderr)
            return 1
        for b in books:
            report(scan_one(b))
            print()
    else:
        if not (root / "chapters").is_dir():
            print(f"[err] {root} has no chapters/ folder", file=sys.stderr)
            return 1
        report(scan_one(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
