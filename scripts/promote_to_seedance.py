#!/usr/bin/env python3
"""promote_to_seedance.py — PASS 2 of the mixed dance pipeline.

After you've built and watched the all-Kling cut, promote the section(s) that earn
the audio-locked motion to Seedance. This re-tags the given beats' video_model to
seedance_2_0 (optionally MERGING a run of consecutive beats into one <=15s Seedance
beat). Then re-run the storyboard (it makes a single start frame for seedance beats)
and slice_beat_audio, and regenerate just those beats with Seedance.

Usage:
  python promote_to_seedance.py <reel_folder> B07 B08 B09          # tag these as seedance
  python promote_to_seedance.py <reel_folder> B07 B08 B09 --merge  # merge them into one <=15s beat
"""
import json, os, sys

def main():
    args = sys.argv[1:]
    merge = "--merge" in args
    args = [a for a in args if a != "--merge"]
    folder = args[0]; ids = set(args[1:])
    if not ids: raise SystemExit("give beat IDs to promote, e.g. B07 B08")
    p = os.path.join(folder, "beat_sheet.json")
    d = json.load(open(p)); beats = d["beats"]; fps = d["metadata"]["fps"]

    if merge:
        sel = [b for b in beats if b["beat_id"] in ids]
        sel.sort(key=lambda b: b["start_frame"])
        if any(sel[i]["end_frame"] != sel[i+1]["start_frame"] for i in range(len(sel)-1)):
            raise SystemExit("merge requires consecutive beats")
        span = (sel[-1]["end_frame"] - sel[0]["start_frame"]) / fps
        if span > 15.5: raise SystemExit(f"merged span {span:.1f}s exceeds Seedance 15s cap")
        keep = sel[0]
        keep["end_frame"] = sel[-1]["end_frame"]; keep["end_s"] = round(keep["end_frame"]/fps, 2)
        keep["duration_s"] = round((keep["end_frame"]-keep["start_frame"])/fps, 2)
        keep["video_model"] = "seedance_2_0"
        keep["lyric_text"] = " / ".join(b["lyric_text"] for b in sel if b["lyric_text"])
        beats = [b for b in beats if b["beat_id"] == keep["beat_id"] or b["beat_id"] not in ids]
    else:
        for b in beats:
            if b["beat_id"] in ids:
                b["video_model"] = "seedance_2_0"

    # renumber contiguous, refresh audio_slice paths
    beats.sort(key=lambda b: b["start_frame"])
    for n, b in enumerate(beats):
        b["beat_id"] = f"B{n+1:02d}"; b["audio_slice"] = f"audio/{b['beat_id']}.wav"
    d["beats"] = beats
    d["metadata"]["counts"] = {"beats": len(beats),
        "kling": sum(1 for b in beats if b["video_model"]=="kling"),
        "seedance": sum(1 for b in beats if b["video_model"]!="kling")}
    json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
    print(f"promoted -> {d['metadata']['counts']}")
    print("next: re-run generate_startend_storyboard.sh (single start frame for the seedance beats),")
    print("      slice_beat_audio.sh, then generate_video.sh on the promoted beats.")

if __name__ == "__main__":
    main()
