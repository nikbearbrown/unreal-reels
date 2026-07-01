#!/usr/bin/env python3
"""reconcile.py — after you've culled the 'meh' downloads, tidy up + list the redos.

Aspect-aware: tracks the reel's primary aspect (video/raw/) AND any alternate aspect
you've started (e.g. video-16x9/raw/). For each beat + each track in play it:
  • collapses surviving variants (<beat>.mp4 / <beat>_v2.mp4 …) — 2+ survivors = no
    preference, so it RANDOMLY keeps one as the canonical name and (unless --keep-variants)
    deletes the rest. Same for story stills.
  • if a track is missing the clip, the beat goes to REDO.md with WHICH aspect(s) are missing.

An alternate aspect is only "in play" (demanded) if its video-<tag>/raw/ folder exists —
so 16:9 isn't flagged until you've generated at least one 16:9 clip.

Usage:  python reconcile.py <reel_folder> [--keep-variants] [--dry-run]
"""
import argparse, glob, json, os, random

def survivors(folder, rel_base):
    base = os.path.join(folder, rel_base)
    stem, ext = os.path.splitext(base)
    found = [p for p in [base] if os.path.exists(p)] + sorted(glob.glob(f"{stem}_v*{ext}"))
    return found, base

def collapse(folder, rel_base, keep, dry):
    found, base = survivors(folder, rel_base)
    if not found: return None
    chosen = random.choice(found)
    if chosen != base and not dry: os.replace(chosen, base)
    if not keep and not dry:
        for p in found:
            if p not in (base, chosen) and os.path.exists(p): os.remove(p)
    return base

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--keep-variants", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(); f = args.folder
    d = json.load(open(os.path.join(f, "beat_sheet.json")))
    m = d["metadata"]; beats = d["beats"]
    story = m.get("mode") == "story-dance" or any(b.get("start_prompt") for b in beats)
    primary_ar = m.get("aspect_ratio", "9:16")

    # aspect tracks: primary (dir 'video') + any alternate video-<tag>/raw that exists
    tracks = [("", primary_ar)]                       # (tag, aspect_label)
    for dd in sorted(glob.glob(os.path.join(f, "video-*"))):
        if os.path.isdir(os.path.join(dd, "raw")):
            tag = os.path.basename(dd)[len("video-"):]
            tracks.append((tag, tag.replace("x", ":")))

    redo = []
    for b in beats:
        bid = b["beat_id"]
        if story:
            collapse(f, f"stills/story/{bid}_A_start.png", args.keep_variants, args.dry_run)
            collapse(f, f"stills/story/{bid}_B_end.png",   args.keep_variants, args.dry_run)
        missing = []
        for tag, ar in tracks:
            sub = "video" if tag == "" else f"video-{tag}"
            collapse(f, f"{sub}/raw/{bid}.mp4", args.keep_variants, args.dry_run)
            if not os.path.exists(os.path.join(f, sub, "raw", f"{bid}.mp4")): missing.append(ar)
        why = []
        if story and not os.path.exists(os.path.join(f, f"stills/story/{bid}_A_start.png")): why.append("A_start frame missing")
        if story and not os.path.exists(os.path.join(f, f"stills/story/{bid}_B_end.png")):   why.append("B_end frame missing")
        if missing: redo.append((b, missing, "; ".join(why)))

    lines = [f"# {m.get('title','reel')} — REDO ({len(redo)} of {len(beats)} beats)",
             f"audio `{m.get('audio_file')}` · tracks: {', '.join(ar for _,ar in tracks)} · "
             f"regenerate on the web, then `build_videos.sh`.\n"]
    for b, miss, why in redo:
        bid = b["beat_id"]
        tail = f" — frames: {why}" if why else ""
        lines.append(f"### {bid} · {b.get('video_model','kling')} · {b['duration_s']}s · **missing: {', '.join(miss)}**{tail}")
        if b.get("lyric_text"): lines.append(f"_lyric:_ {b['lyric_text']}")
        if story:
            lines.append(f"- **slot A (start):** `stills/story/{bid}_A_start.png`")
            lines.append(f"- **slot B (end):** `stills/story/{bid}_B_end.png`")
        lines.append("\n_prompt:_\n```\n" + (b.get("video_prompt","").rsplit(". Duration",1)[0]) + "\n```\n")

    ids = " ".join(b["beat_id"] for b,_,_ in redo) or "none — all done!"
    if args.dry_run:
        print(f"[dry-run] tracks {[ar for _,ar in tracks]} | {len(redo)} beats to redo: {ids}")
    else:
        open(os.path.join(f, "REDO.md"), "w").write("\n".join(lines))
        print(f"reconciled | tracks {[ar for _,ar in tracks]} | REDO.md -> {len(redo)} beats: {ids}")

if __name__ == "__main__":
    main()
