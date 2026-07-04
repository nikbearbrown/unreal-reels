#!/usr/bin/env python3
"""
emit_youtube.py — YouTube description + autoposter manifest for a brownblue video.

Reads beat_sheet.json (real per-beat durations) and writes, next to the video:
    <slug>-youtube.md     the plain long-form description that actually posts
                          (youtube_publish.py uploads this file's text verbatim)
    <slug>-youtube-notes.md   human reference: titles/descriptions both aspects
    <slug>-youtube.json   autoposter manifest — a machine-readable upload spec
                          for a YouTube Data API v3 poster (long + short entries)

METADATA-DRIVEN (silent mode): all per-video copy lives in the beat sheet's
`metadata`, authored alongside the beats — nothing video-specific is hardcoded
here. Recognized keys (all optional, sensible generic fallbacks):

    chapters            [[beat_id, label], ...]  chapter anchors in beat order
    extra_tags          topic tags appended to the series base tags
    hashtags_line       trailing hashtag line of the long description
    long_title          full long-form title (else "<title> | Bear's Notes")
    description_blurb   the "In this video: ..." paragraph
    short_title         Shorts title (else "<title> #Shorts")
    short_blurb         sentence after the hook in the Short description
    hook_beats          beat_ids whose narration opens the description
                        (else ["H01","H02","H03"])

Chapters are derived from the audio timeline: anchor beats → labeled chapters,
auto-dropping any that fall <10s after the previous one (YouTube's rule) and
forcing a 0:00 first chapter.

Usage:
    python emit_youtube.py <folder> [--privacy private|unlisted|public]
                                     [--publish-at 2026-07-10T14:00:00Z]
"""
import argparse
import json
import re
from pathlib import Path

BASE_TAGS = [
    "Bear's Notes", "quantum mechanics", "physics", "quantum physics",
    "3Blue1Brown style", "science explainer", "education", "STEM",
]

DEFAULT_HASHTAGS = "#quantum #physics #quantummechanics #science #education"


def hms(sec):
    sec = int(round(sec))
    h, sec = divmod(sec, 3600)
    m, s = divmod(sec, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    ap.add_argument("--publish-at", default=None, help="ISO8601 UTC, e.g. 2026-07-10T14:00:00Z")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    meta = sheet["metadata"]
    slug = meta["slug"]
    title = meta["title"]
    channel = meta.get("channel_url", "youtube.com/@NikBearBrown")
    series = meta.get("series", "Brown Blue")

    beats = sheet["beats"]
    # cumulative start time per beat
    start = {}
    acc = 0.0
    for b in beats:
        start[b["beat_id"]] = acc
        acc += float(b.get("actual_duration_s", 0.0))
    total = acc

    # chapters, enforcing 0:00 first + >=10s spacing
    anchor_list = meta.get("chapters") or []
    if not anchor_list:
        print(f"[warn] metadata.chapters missing — description will have no chapter list")
    chapters, last = [], -999
    for bid, label in anchor_list:
        if bid not in start:
            continue
        t = start[bid]
        if not chapters:
            t = 0.0
        if t - last >= 10 or not chapters:
            chapters.append((t, label))
            last = t
    if chapters:
        chapters[0] = (0.0, chapters[0][1])  # force first to 0:00

    # lede = the hook narration
    hook_ids = meta.get("hook_beats", ["H01", "H02", "H03"])
    hook = [b["narration_text"] for b in beats if b["beat_id"] in hook_ids]
    lede = " ".join(" ".join(h.split()) for h in hook)

    src = meta.get("source", "")
    src_line = ""
    m = re.search(r"quantum-mechanics-(vol\d+|[a-z-]+)/chapters/(\d+)-([a-z0-9-]+)", src)
    if m:
        vol = m.group(1).replace("vol", "Vol. ")
        ch = int(m.group(2))
        chname = m.group(3).replace("-", " ").title()
        src_line = f"Source: Quantum Mechanics, {vol}, Ch. {ch} — {chname}."

    tags = BASE_TAGS + list(meta.get("extra_tags", []))
    hashtags = meta.get("hashtags_line", DEFAULT_HASHTAGS)
    blurb = meta.get("description_blurb", "")

    # ---- long-form description ----
    long_desc = []
    long_desc.append(lede)
    long_desc.append("")
    long_desc.append(f"A {series} explainer, in the 3Blue1Brown tradition: "
                     "concrete before abstract, mystery before formula.")
    if chapters:
        long_desc.append("")
        long_desc.append("Chapters:")
        for t, label in chapters:
            long_desc.append(f"{hms(t)} {label}")
    if blurb:
        long_desc.append("")
        long_desc.append(blurb)
    if src_line:
        long_desc.append("")
        long_desc.append(src_line)
    long_desc.append("")
    long_desc.append(f"More Bear's Notes: {channel}")
    long_desc.append("")
    long_desc.append(hashtags)
    long_text = "\n".join(long_desc)

    long_title = meta.get("long_title") or f"{title} | Bear's Notes"

    # ---- Short description ----
    short_title = meta.get("short_title") or f"{title} #Shorts"
    short_blurb = meta.get("short_blurb", "Full explainer on the channel.")
    first_hook = " ".join(hook[0].split()) if hook else title
    short_desc = (f"{first_hook} {short_blurb}\n\n{channel}\n\n"
                  "#Shorts #quantum #physics #science")

    # ---- description file (CLEAN) ----
    # youtube_publish.py reads this WHOLE file as the video description, so it must
    # be the plain long-form description — no markdown headers, no code fences.
    (folder / f"{slug}-youtube.md").write_text(long_text + "\n", encoding="utf-8")

    # ---- human reference (both aspects, formatted) ----
    notes = [f"# YouTube reference — {title}", "", "## Long-form (16:9)", "",
             f"**Title:** {long_title}", "", "**Description:** (this is what posts — "
             f"lives in `{slug}-youtube.md`)", "", "```", long_text, "```",
             "", "## Short (9:16)", "", f"**Title:** {short_title}", "",
             "**Description:**", "", "```", short_desc, "```", "",
             "**Tags:** " + ", ".join(tags), ""]
    (folder / f"{slug}-youtube-notes.md").write_text("\n".join(notes), encoding="utf-8")

    # ---- make tags + playlists available to youtube_publish.py ----
    sheet["metadata"]["hashtags"] = tags
    # playlists come from the book's queue decisions and are AUTHORED in metadata;
    # never invent them here (an old default filed videos under wrong names).
    for key in ("playlist", "playlist_short"):
        if not meta.get(key):
            print(f"[warn] metadata.{key} missing — publisher will fall back to "
                  f"its --playlist flag (set it in beat_sheet.json)")
    (folder / "beat_sheet.json").write_text(
        json.dumps(sheet, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- autoposter manifest ----
    def entry(kind, fname, vtitle, vdesc, is_short):
        return {
            "kind": kind,
            "file": f"mp4/{fname}",
            "caption_file": f"mp4/{fname.replace('.mp4', '-caption.mp4')}",
            "title": vtitle,
            "description": vdesc,
            "tags": tags + (["Shorts"] if is_short else []),
            "categoryId": "27",              # Education
            "privacyStatus": args.privacy,
            "publishAt": args.publish_at,    # null = publish now on upload
            "madeForKids": False,
            "defaultLanguage": "en",
            "captions": [{"language": "en", "name": "English",
                          "file": f"{slug}.srt"}],
            "thumbnail": None,
            "isShort": is_short,
        }

    manifest = {
        "poster": {
            "platform": "youtube",
            "channel": channel,
            "series": series,
            "source_chapter": src,
            "playlist": meta.get("playlist") or f"{series} — Quantum Mechanics",
            "upload_order": ["long", "short"],
            "notes": "Consumed by a YouTube Data API v3 autoposter. Upload `long` "
                     "first, then `short`. publishAt null = go live immediately; set "
                     "an ISO8601 UTC time to schedule. Requires OAuth on the channel.",
        },
        "long": entry("long", f"{slug}.mp4", long_title, long_text, False),
        "short": entry("short", f"{slug}-short.mp4", short_title, short_desc, True),
        "duration_seconds": round(total, 2),
        "slug": slug,
    }
    (folder / f"{slug}-youtube.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[ok] {slug}-youtube.md  ({len(chapters)} chapters)")
    print(f"[ok] {slug}-youtube.json  (autoposter manifest, privacy={args.privacy})")


if __name__ == "__main__":
    main()
