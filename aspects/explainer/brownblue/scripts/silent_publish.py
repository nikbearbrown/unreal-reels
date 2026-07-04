#!/usr/bin/env python3
"""
silent_publish.py — Brown Blue SILENT MODE, command #2 of 2.

Run this ONLY after watching and approving the masters silent_run.py produced.
It uploads every surface of one concept — long cut (16:9 + 9:16) from
<folder>/ and short cut (16:9 + 9:16) from <folder>/short/ — as PRIVATE
scheduled uploads, with descriptions, caption tracks, and playlists, by
driving youtube_publish.py with the channel-wide credentials that live in the
central publish workspace (gitignored, never in a book repo).

Usage:
    python silent_publish.py <concept-folder> [--dry-run]
                              [--interval-hours 4] [--start ISO8601]
                              [--privacy private|unlisted]

The publish workspace defaults to /Users/nik/Documents/Cowork/Manim
(override with env BB_PUBLISH_WORKSPACE or --workspace).
Idempotent: the ledger skips anything already uploaded, so re-running after
a partial failure is safe.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_WORKSPACE = Path(os.getenv("BB_PUBLISH_WORKSPACE",
                                   "/Users/nik/Documents/Cowork/Manim"))


def main():
    ap = argparse.ArgumentParser(description="Publish all surfaces of one Brown Blue concept.")
    ap.add_argument("folder", help="concept folder (long cut; short cut in <folder>/short/)")
    ap.add_argument("--workspace", default=str(DEFAULT_WORKSPACE),
                    help="dir holding client_secret.json / youtube_token.json / ledger")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--interval-hours", type=float, default=4.0)
    ap.add_argument("--start", default=None, help="ISO datetime for the first slot")
    ap.add_argument("--privacy", choices=["private", "unlisted"], default="private")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    short = folder / "short"
    ws = Path(args.workspace).expanduser().resolve()

    pub = HERE / "youtube_publish.py"
    if not pub.exists():
        sys.exit(f"[publish] youtube_publish.py not found next to this script ({HERE}).")

    for name in ("client_secret.json", "youtube_token.json"):
        if not (ws / name).exists():
            sys.exit(f"[publish] {name} not found in workspace {ws} — "
                     "run from a machine that has the channel credentials.")

    folders = [str(folder)] + ([str(short)] if short.is_dir() else [])
    if len(folders) == 1:
        print(f"[publish] note: no {short}/ — publishing the long cut only.")

    cmd = [sys.executable, str(pub), *folders,
           "--no-pairs", "--which", "both",
           "--interval-hours", str(args.interval_hours),
           "--privacy", args.privacy,
           "--client", str(ws / "client_secret.json"),
           "--token", str(ws / "youtube_token.json"),
           "--ledger", str(ws / "youtube_publish_ledger.json")]
    if args.start:
        cmd += ["--start", args.start]
    if args.dry_run:
        cmd += ["--dry-run"]

    print("[publish] $", " ".join(cmd))
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
