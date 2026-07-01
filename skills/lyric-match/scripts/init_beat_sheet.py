#!/usr/bin/env python3
"""init_beat_sheet.py — build a skeleton beat_sheet.json for lyric-match.

One beat = one lyric line. Beats tile the song contiguously (each ends where the
next begins; first starts at frame 0, last ends at the song's last frame), so the
assembled video has no gaps. Timing is the master clock: beat boundaries come from
lyrics.json's line startFrames (which were derived from the real librosa beat grid
or forced alignment). Prompts/stills are left EMPTY — pick_stills.py fills the
source frames, and the Phase-4 vision step writes image_prompt/video_prompt.

Usage:
    python init_beat_sheet.py <reel_folder> \
        --audio song.wav --lyrics song-06.txt \
        --title "Lift Every Voice and Sing" --artist "Mayfield King" \
        [--slug lift-every-voice-and-sing] [--source-video in.mp4]
"""
import argparse, json, os, re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--lyrics", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--artist", default="")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--source-video", default=None)
    ap.add_argument("--beat-data", default="beat_data.json")
    ap.add_argument("--lyrics-timing", default="lyrics.json")
    ap.add_argument("-o", "--out", default="beat_sheet.json")
    args = ap.parse_args()

    f = args.folder
    bd = json.load(open(os.path.join(f, args.beat_data)))
    ly = json.load(open(os.path.join(f, args.lyrics_timing)))
    fps = bd["fps"]
    lines = sorted(ly["lines"], key=lambda l: l["index"])
    if not lines:
        raise SystemExit("no lyric lines in " + args.lyrics_timing)

    slug = args.slug or re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")
    starts = [l["startFrame"] for l in lines]

    beats = []
    for n, l in enumerate(lines):
        start = 0 if n == 0 else starts[n]
        end = starts[n + 1] if n + 1 < len(lines) else bd["durationInFrames"]
        dur = round((end - start) / fps, 2)
        section = next((s["label"] for s in bd.get("sections", [])
                        if s["startFrame"] <= start < s["endFrame"]),
                       (bd["sections"][-1]["label"] if bd.get("sections") else "section_1"))
        beats.append({
            "beat_id": f"B{n+1:02d}",
            "start_s": round(start / fps, 2), "end_s": round(end / fps, 2),
            "start_frame": start, "end_frame": end, "duration_s": dur,
            "section": section, "kind": "vocal",
            "subject": None,
            "line_indices": [l["index"]],
            "lyric_text": l["text"],
            "source_still": None, "source_frame_number": None, "source_frame_sharpness": None,
            "prompt_mode": "image-to-image",
            "image_prompt": None, "storyboard_prompts": [],
            "camera": "static",
            "video_prompt": None,
            "clip_tier": 6 if dur <= 6 else 10,
            "chosen_still": None, "raw_clip": None, "video_file": None,
        })

    sheet = {
      "metadata": {
        "slug": slug, "title": args.title, "artist": args.artist,
        "aspect_ratio": "16:9", "fps": fps,
        "duration_s": bd["durationInSeconds"], "duration_frames": bd["durationInFrames"],
        "bpm": bd.get("bpm"),
        "key": f'{bd["features"].get("key")} {bd["features"].get("mode")}' if bd.get("features") else None,
        "audio_file": os.path.basename(args.audio),
        "lyrics_file": os.path.basename(args.lyrics),
        "beat_data": args.beat_data, "lyrics_timing": args.lyrics_timing,
        "source_video": (os.path.basename(args.source_video) if args.source_video else None),
        "timing_source": ly.get("timing_source", "unknown"),
        "language": ly.get("language", "en"),
        "style_preset": "TODO — derive from the source video",
        "style_bible": {"visual_style": "TODO", "color_palette": "TODO", "lighting_style": "TODO"},
        "style_suffix": "TODO — a one-line grade appended to every prompt to match the source video",
        "generation": {
          "still_source": "existing video frames (lyric-match)",
          "video_model": "minimax_hailuo (image-to-video)",
          "duration_request_s": 10,
          "rule": "each beat is image-to-video from chosen_still; request 10s then center-cut "
                  "to duration_s. image_prompt/video_prompt are authored by looking at the still AND the lyric.",
        },
        "counts": {"beats": len(beats)},
      },
      "beats": beats,
    }

    out = os.path.join(f, args.out)
    json.dump(sheet, open(out, "w"), ensure_ascii=False, indent=2)

    # integrity: contiguous tiling 0..durationInFrames
    prev = 0
    for b in beats:
        assert b["start_frame"] == prev, f"gap at {b['beat_id']}"
        prev = b["end_frame"]
    assert prev == bd["durationInFrames"], "last beat does not reach song end"
    print(f"wrote {out} | beats: {len(beats)} | contiguous 0..{prev} frames OK")
    over = [(b["beat_id"], b["duration_s"]) for b in beats if b["duration_s"] > 10.0]
    if over:
        print("WARNING beats over 10s (Hailuo max):", over)

if __name__ == "__main__":
    main()
