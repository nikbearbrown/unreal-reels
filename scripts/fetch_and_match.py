#!/usr/bin/env python3
"""fetch_and_match.py — pull recent Higgsfield generations, match each by its PROMPT
to a beat in this reel, download it, and name it for that beat + slot.

Workflow: you generate on the web (unlimited tier), then run this once. It calls
`higgsfield generate list --json`, reads each job's params.prompt + result_url, and
matches the prompt against every beat's video_prompt / start_prompt / end_prompt in
beat_sheet.json (exact, else closest >= --min-sim). Then it downloads:
  video job  -> video/raw/<beat>.mp4                 (matched on video_prompt)
  image job  -> stills/story[-16x9]/<beat>_A_start.png / _B_end.png  (start/end prompt; folder by aspect)
Multiple jobs with the same prompt -> keeps the most recent (use --all to save _v1,_v2...).

Usage:
  python fetch_and_match.py <reel_folder> [--video|--image] [--size 50]
      [--min-sim 0.82] [--all] [--force] [--dry-run] [--from-json FILE]
Requires: higgsfield CLI authenticated (unless --from-json), curl-free (uses urllib).
"""
import argparse, json, os, re, subprocess, sys, urllib.request
from difflib import SequenceMatcher

def norm(s): return re.sub(r"\s+", " ", (s or "").strip().lower())

def get_jobs(args):
    if args.from_json:
        return json.load(open(args.from_json))
    size = min(args.size, 100)   # Higgsfield caps page size at 100
    if args.size > 100: print(f"(note: --size {args.size} capped to 100 by Higgsfield)", file=sys.stderr)
    cmd = ["higgsfield", "generate", "list", "--json", "--size", str(size)]
    if args.video: cmd.append("--video")
    if args.image: cmd.append("--image")
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)

VIDEO_MODELS = ("kling", "minimax", "hailuo", "seedance", "veo", "wan", "grok_video")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--video", action="store_true", help="video jobs only")
    ap.add_argument("--image", action="store_true", help="image jobs only")
    ap.add_argument("--size", type=int, default=100)   # Higgsfield's max page; the deepest one call reaches
    ap.add_argument("--min-sim", type=float, default=0.82)
    ap.add_argument("--fuzzy", action="store_true", help="accept non-exact prompt matches >= --min-sim (default: exact only)")
    ap.add_argument("--all", action="store_true", help="save every match as _v1,_v2 (default: latest only)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--from-json", default=None, help="read jobs from a saved JSON file instead of the CLI")
    args = ap.parse_args()

    f = args.folder
    d = json.load(open(os.path.join(f, "beat_sheet.json")))
    beats = d["beats"]
    default_ar = d.get("metadata", {}).get("aspect_ratio", "9:16")   # this reel's primary aspect
    def tag_for(ar):  # 16:9 != default -> its own dir ("16x9"); the default aspect -> no tag
        ar = str(ar or "")
        return "" if (not ar or ar == str(default_ar)) else ar.replace(":", "x")

    # candidate prompts -> (beat_id, kind)  kind in {video, start, end}
    cands = []
    for b in beats:
        if b.get("video_prompt"): cands.append((norm(b["video_prompt"]), b["beat_id"], "video"))
        if b.get("start_prompt"): cands.append((norm(b["start_prompt"]), b["beat_id"], "start"))
        if b.get("end_prompt"):   cands.append((norm(b["end_prompt"]),   b["beat_id"], "end"))

    def match(p):
        p = norm(p)
        for cp, bid, kind in cands:
            if cp == p: return bid, kind, 1.0
        best = (None, None, 0.0)
        for cp, bid, kind in cands:
            r = SequenceMatcher(None, p, cp).ratio()
            if r > best[2]: best = (bid, kind, r)
        return best if best[2] >= args.min_sim else (None, None, best[2])

    def target(job, bid, kind):
        jt = (job.get("job_set_type") or "").lower()
        is_video = kind == "video" or any(v in jt for v in VIDEO_MODELS)
        ar = (job.get("params", {}) or {}).get("aspect_ratio", "")
        tag = tag_for(ar)
        if is_video:
            sub = f"video-{tag}" if tag else "video"        # 16:9 -> video-16x9/raw/, default -> video/raw/
            return os.path.join(sub, "raw", f"{bid}.mp4")
        sub = f"stills/story-{tag}" if tag else "stills/story"
        suf = "_A_start" if kind == "start" else ("_B_end" if kind == "end" else "_A_start")
        return os.path.join(sub, f"{bid}{suf}.png")

    jobs = [j for j in get_jobs(args) if j.get("status") == "completed" and j.get("result_url")]
    jobs.sort(key=lambda j: j.get("created_at", 0), reverse=True)  # newest first

    seen = {}; planned = []; nomatch = 0; dup = 0; fuzzy = []
    for j in jobs:
        prompt = (j.get("params", {}) or {}).get("prompt", "")
        bid, kind, sim = match(prompt)
        if not bid:
            nomatch += 1; continue
        if sim < 1.0 and not args.fuzzy:    # exact-only by default; non-exact needs --fuzzy
            nomatch += 1; fuzzy.append((sim, bid, kind, prompt[:70])); continue
        tgt = target(j, bid, kind)
        if not args.all:
            if tgt in seen: dup += 1; continue   # older duplicate of a prompt already taken (newest kept)
            seen[tgt] = True
        else:
            n = seen.get(tgt, 0) + 1; seen[tgt] = n
            if n > 1:
                base, ext = os.path.splitext(tgt); tgt = f"{base}_v{n}{ext}"
        if sim < 1.0: fuzzy.append((sim, bid, kind, prompt[:70]))
        planned.append((tgt, j["result_url"], bid, kind, sim, prompt[:60]))

    print(f"{len(jobs)} jobs = {len(planned)} new + {dup} older-duplicate + {nomatch} unmatched"
          + (f"  ({len(fuzzy)} fuzzy)" if fuzzy else "  (all exact)"))
    if fuzzy:
        verb = "ACCEPTED (--fuzzy)" if args.fuzzy else "REJECTED (use --fuzzy to accept)"
        print(f"  fuzzy matches {verb}:")
        for sim, bid, kind, pv in sorted(fuzzy, reverse=True)[:12]:
            print(f"    ~{sim:.2f}  {bid}/{kind}  «{pv}»")
    ok = 0
    for tgt, url, bid, kind, sim, pv in planned:
        full = os.path.join(f, tgt)
        if os.path.exists(full) and not args.force:
            print(f"  skip (exists) {tgt}"); continue
        tag = "=" if sim == 1.0 else f"~{sim:.2f}"
        if args.dry_run:
            print(f"  {tgt:42} <{tag}> {bid}/{kind}  «{pv}»"); ok += 1; continue
        os.makedirs(os.path.dirname(full), exist_ok=True)
        try:
            urllib.request.urlretrieve(url, full); print(f"  -> {tgt}  <{tag}> {bid}/{kind}"); ok += 1
        except Exception as e:
            print(f"  FAILED {tgt}: {e}", file=sys.stderr)
    print(f"{'would download' if args.dry_run else 'downloaded'} {ok} files")

if __name__ == "__main__":
    main()
