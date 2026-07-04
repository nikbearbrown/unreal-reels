#!/usr/bin/env python3
"""
silent_run.py — Brown Blue SILENT MODE: one command, every surface.

Given a concept folder authored by the skill (beat sheets + scene .py already
written), this runs the ENTIRE machine side with no gates:

    audio → render 16:9 → layout audit → assemble
          → render 9:16 → layout audit → assemble
          → karaoke captions (both aspects)
          → transcripts + YouTube descriptions/manifest

…for BOTH cuts of the concept:

    <folder>/          the LONG cut   → <slug>.mp4 (16:9) + <slug>-short.mp4 (9:16)
    <folder>/short/    the SHORT cut  → same pair, from its own beat sheet
                       (slug convention: insert -short before the -bb suffix)

That is 4 clean masters + 4 karaoke cuts per concept. The short cut's audio is
hard-gated < 3:00 (YouTube Shorts limit); the long cut's 9:16 is exempt (it is
a regular vertical video, not a Short) and is captioned with --allow-long.

On any failure it stops immediately and prints the failing command plus the
last lines of output — paste that block back into the chat to fix it.

Publishing is NEVER done here. After you have watched the masters, run the
silent_publish.py command this script prints at the end.

Usage:
    python silent_run.py <concept-folder>              # everything
    python silent_run.py <concept-folder> --only long  # just the long cut
    python silent_run.py <concept-folder> --only short # just the short cut
    python silent_run.py <concept-folder> --dry-run    # print the plan only
    python silent_run.py <concept-folder> --skip-audio # reuse existing mp3/

Requires (Bear's Mac, `ai` env active): manim, ffmpeg, mutagen, faster-whisper,
ELEVENLABS_API_KEY in the shell env.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Everything every step prints goes to <concept>/silent_run.log; a failure also
# writes <concept>/silent_error.log (progress bars stripped) so Claude can read
# the diagnosis directly from the folder instead of the user pasting terminal
# scroll. Set in main().
LOG_PATH: Path | None = None
ERR_PATH: Path | None = None

_BAR = re.compile(r"\d+%\||it/s|^\s*$")


def _clean(text: str) -> list[str]:
    """Drop Manim progress-bar spam; keep the lines that say something."""
    out = []
    for raw in text.splitlines():
        line = raw.split("\r")[-1]
        if not _BAR.search(line):
            out.append(line)
    return out

# where shared pipeline scripts may live, in search order:
#   1. next to this file (book-repo copies are all in one dir)
#   2. the canonical split homes (upstream unreal-reels tree)
SCRIPT_HOMES = [
    HERE,
    HERE.parent.parent / "bears-doodles" / "scripts",
    HERE.parent.parent.parent.parent.parent / "skills" / "deck-lecture" / "scripts",
]


def find_script(name: str) -> Path:
    for home in SCRIPT_HOMES:
        p = home / name
        if p.exists():
            return p
    sys.exit(f"[silent] cannot find pipeline script '{name}' "
             f"(searched: {', '.join(str(h) for h in SCRIPT_HOMES)})")


def run(cmd, cwd=None, label=""):
    """Run a step; log everything; on failure write silent_error.log and exit."""
    disp = " ".join(str(c) for c in cmd)
    print(f"\n[silent] ▶ {label or disp}")
    print(f"         $ {disp}" + (f"   (cwd: {cwd})" if cwd else ""))
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True)
    raw = (r.stdout or "") + (r.stderr or "")
    if LOG_PATH is not None:
        with LOG_PATH.open("a") as lf:
            lf.write(f"\n\n===== STEP: {label or disp}\n$ {disp}\ncwd: {cwd or os.getcwd()}"
                     f"\nexit: {r.returncode}\n")
            lf.write(raw)
    clean = _clean(raw)
    for line in clean[-12:]:
        print("         " + line)
    if r.returncode != 0:
        audits = []
        base = Path(cwd) if cwd else (Path(cmd[1]).parent if len(cmd) > 1 else None)
        for cand in ("layout_audit.md", "layout_audit.json"):
            p = (base / cand) if base else None
            if p and p.exists():
                audits.append(p)
        if ERR_PATH is not None:
            with ERR_PATH.open("w") as ef:
                ef.write(f"step: {label or disp}\ncmd:  {disp}\n"
                         f"cwd:  {cwd or os.getcwd()}\nexit: {r.returncode}\n")
                if audits:
                    ef.write("audit reports: " + ", ".join(str(a) for a in audits) + "\n")
                ef.write("\n--- output (progress bars stripped) ---\n")
                ef.write("\n".join(clean) + "\n")
        print("\n" + "=" * 72)
        print(f"[silent] FAILED at step: {label or disp}")
        for line in clean[-25:]:
            print(line)
        if audits:
            print(f"[silent] audit report: {audits[0]}")
        if ERR_PATH is not None:
            print(f"[silent] full diagnosis written to: {ERR_PATH}")
        print("\n[silent] YOUR ACTION — paste this one line into Cowork:")
        print("-" * 72)
        print(f"silent_run failed — read {ERR_PATH} and the audit report, fix it, "
              "and hand me the command again")
        print("-" * 72)
        sys.exit(r.returncode or 1)


def scene_file(folder: Path) -> Path:
    """The one non-helper .py in the folder (the Manim scene)."""
    helpers = {"bn_layout.py", "silent_run.py", "silent_publish.py"}
    cands = [p for p in folder.glob("*.py") if p.name not in helpers]
    if len(cands) != 1:
        sys.exit(f"[silent] expected exactly one scene .py in {folder}, "
                 f"found: {[p.name for p in cands] or 'none'} — author the scene first.")
    return cands[0]


def sheet_meta(folder: Path) -> dict:
    p = folder / "beat_sheet.json"
    if not p.exists():
        sys.exit(f"[silent] no beat_sheet.json in {folder} — author it first.")
    return json.loads(p.read_text())["metadata"]


def preflight(units, skip_audio):
    missing = [t for t in ("manim", "ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        sys.exit(f"[silent] not on PATH: {', '.join(missing)}. "
                 "Activate the `ai` env (and brew install ffmpeg) first.")
    if not skip_audio and not os.getenv("ELEVENLABS_API_KEY"):
        sys.exit("[silent] ELEVENLABS_API_KEY is not set in this shell.")
    for label, folder, _ in units:
        sheet_meta(folder)          # exists + parses
        scene_file(folder)          # exactly one scene
        if not (folder / "fonts").is_dir():
            print(f"[silent] warn: {folder}/fonts/ missing — relying on EB Garamond "
                  "being installed system-wide (concept #1 rendered this way).")


def process_unit(label: str, folder: Path, is_short_cut: bool, args):
    slug = sheet_meta(folder)["slug"]
    scene = scene_file(folder)
    py = sys.executable

    print(f"\n{'#' * 72}\n[silent] {label} cut — {slug}\n{'#' * 72}")

    # 1 ── audio (audio-first: real MP3 durations drive everything).
    # Never re-bill ElevenLabs for clips that already exist: skip when every
    # beat's MP3 + timings.json are present; regenerate only missing beats
    # otherwise. --force-audio redoes everything (use after narration edits,
    # or just delete the changed beats' mp3s and re-run).
    if not args.skip_audio:
        sheet = json.loads((folder / "beat_sheet.json").read_text())
        needed = [b["beat_id"] for b in sheet["beats"]
                  if not (folder / (b.get("audio_file") or
                                    f"mp3/beat-{b['beat_id']}.mp3")).exists()]
        have_timings = (folder / "mp3" / "timings.json").exists()
        if args.force_audio or not have_timings or len(needed) == len(sheet["beats"]):
            run([py, find_script("generate_audio.py"), folder], label=f"{label}: audio")
        elif needed:
            run([py, find_script("generate_audio.py"), folder, "--only", *needed],
                label=f"{label}: audio ({len(needed)} missing beat(s) only)")
        else:
            print(f"[silent] {label}: audio up to date "
                  f"({len(sheet['beats'])} clips) — skipping ElevenLabs "
                  "(delete a beat's mp3 or use --force-audio to regenerate)")

    # 2 ── ALL cheap checks BEFORE any expensive render (fail before pixels):
    #      the Shorts guard, then the layout audit for BOTH aspects — the audit
    #      only instantiates the scene (text-on-text, out-of-frame, text-on-curve),
    #      so overlaps are caught before a single -qh frame is paid for.
    if is_short_cut:
        run([py, find_script("short_guard.py"), folder], label=f"{label}: short guard (<3:00)")
    audit = find_script("manim_layout_audit.py")
    run([py, audit, scene.name, "--curve-strict"], cwd=folder,
        label=f"{label}: PRE-RENDER layout audit 16:9")
    run([py, audit, scene.name, "--portrait", "--curve-strict"], cwd=folder,
        label=f"{label}: PRE-RENDER layout audit 9:16")

    # 3 ── 16:9: render → assemble
    run(["manim", "-qh", scene.name, "BearsDoodlesVideo"], cwd=folder,
        label=f"{label}: render 16:9")
    run([py, find_script("assemble.py"), folder, "--mode", "manim"],
        label=f"{label}: assemble 16:9 → {slug}.mp4")

    # 4 ── 9:16: render → assemble
    run(["manim", "-r", "1080,1920", "--fps", "60", "--disable_caching",
         "--flush_cache", scene.name, "BearsDoodlesVideo"], cwd=folder,
        label=f"{label}: render 9:16")
    run([py, find_script("assemble.py"), folder, "--mode", "manim", "--portrait"],
        label=f"{label}: assemble 9:16 → {slug}-short.mp4")

    # 5 ── karaoke captions on both clean masters
    run([py, find_script("align_captions.py"), folder],
        label=f"{label}: forced alignment (faster-whisper)")
    run([py, find_script("burn_captions.py"), folder, "--input", f"mp4/{slug}.mp4"],
        label=f"{label}: karaoke 16:9")
    burn_portrait = [py, find_script("burn_captions.py"), folder,
                     "--input", f"mp4/{slug}-short.mp4", "--portrait"]
    if not is_short_cut:
        burn_portrait.append("--allow-long")   # 9:16 LONG is not a Short
    run(burn_portrait, label=f"{label}: karaoke 9:16")

    # 6 ── metadata: transcripts + YouTube description/manifest
    run([py, find_script("emit_transcript.py"), folder], label=f"{label}: transcripts")
    run([py, find_script("emit_youtube.py"), folder], label=f"{label}: YouTube metadata")

    return [folder / "mp4" / f"{slug}{sfx}.mp4"
            for sfx in ("", "-short", "-caption", "-short-caption")]


def main():
    ap = argparse.ArgumentParser(description="Brown Blue silent mode — one command, all surfaces.")
    ap.add_argument("folder", help="concept folder (the long cut; short cut in <folder>/short/)")
    ap.add_argument("--only", choices=["long", "short"], default=None)
    ap.add_argument("--skip-audio", action="store_true", help="reuse existing mp3/")
    ap.add_argument("--force-audio", action="store_true",
                    help="regenerate ALL ElevenLabs audio even if clips exist")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    short = folder / "short"
    global LOG_PATH, ERR_PATH
    LOG_PATH = folder / "silent_run.log"
    ERR_PATH = folder / "silent_error.log"
    if not args.dry_run:
        LOG_PATH.write_text("")           # fresh log per run
        if ERR_PATH.exists():
            ERR_PATH.unlink()             # a surviving error file means THIS run failed

    units = []
    if args.only in (None, "long"):
        units.append(("LONG", folder, False))
    if args.only in (None, "short"):
        if short.is_dir():
            # convenience: the short cut may share the parent's fonts
            if not (short / "fonts").is_dir() and (folder / "fonts").is_dir():
                shutil.copytree(folder / "fonts", short / "fonts")
            units.append(("SHORT", short, True))
        elif args.only == "short":
            sys.exit(f"[silent] no short cut at {short} — author it first.")
        else:
            print(f"[silent] note: no {short}/ — running the long cut only.")

    if args.dry_run:
        print("[silent] PLAN (dry run):")
        for label, f, is_short in units:
            slug = sheet_meta(f)["slug"]
            print(f"  {label}: {f}")
            print(f"    audio → {'guard(<3:00) → ' if is_short else ''}"
                  f"16:9 render+audit+assemble → 9:16 render+audit+assemble "
                  f"→ captions ×2 → transcripts + YT metadata")
            print(f"    outputs: mp4/{slug}.mp4  mp4/{slug}-short.mp4  "
                  f"mp4/{slug}-caption.mp4  mp4/{slug}-short-caption.mp4")
        return 0

    preflight(units, args.skip_audio)

    outputs = []
    for label, f, is_short in units:
        outputs += process_unit(label, f, is_short, args)

    clean_masters = [p for p in outputs if not p.name.endswith("-caption.mp4")]
    caption_cuts = [p for p in outputs if p.name.endswith("-caption.mp4")]
    ok = all(p.exists() for p in outputs)

    print("\n" + "=" * 72)
    print("[silent] DONE — YOUR ACTIONS, in order:")
    print("\n1. WATCH the clean masters (full paths — open in QuickTime):")
    for p in clean_masters:
        mark = " " if p.exists() else " ✗ MISSING "
        print(f"   {mark}{p}")
    print("\n2. SKIM the caption cuts:")
    for p in caption_cuts:
        mark = " " if p.exists() else " ✗ MISSING "
        print(f"   {mark}{p}")
    print("\n3a. HAPPY? paste this ONE command to publish everything "
          "(private, captions, playlists):")
    print("-" * 72)
    print(f'python "{HERE / "silent_publish.py"}" "{folder}"')
    print("-" * 72)
    print("\n3b. WANT CHANGES? paste this one line into Cowork and describe them:")
    print("-" * 72)
    print(f"silent mode {folder.name}: I watched the masters — here are my notes:")
    print("-" * 72)
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
