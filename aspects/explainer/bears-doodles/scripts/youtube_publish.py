#!/usr/bin/env python3
"""
youtube_publish.py — upload Bear's Notes videos to YouTube on a rolling schedule.

Each video is uploaded as PRIVATE with a future `publishAt`, so YouTube flips it
public automatically at the scheduled moment (a drip release — they don't all go
out at once). The next slot is computed by looking at the LATEST already-scheduled
(private + future publishAt) video on the channel and adding the interval (default
4 hours = 6/day, matching the default upload quota), so re-running just extends
the queue.

One-time setup (see reference/youtube-publishing.md): a Google Cloud project with
the YouTube Data API enabled, an OAuth "Desktop app" client (client_secret.json),
and — important — a YouTube API audit, or uploads stay locked to private and the
publishAt will not surface them publicly.

Install (in the ~/ai venv):
    pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

Usage:
    # preview the schedule WITHOUT uploading (no quota spent):
    python youtube_publish.py --root ~/Documents/Cowork/Manim --which landscape --dry-run

    # actually upload + schedule everything not already posted:
    python youtube_publish.py --root ~/Documents/Cowork/Manim --which landscape

    # a specific set of folders, every 6 hours, starting at an explicit time:
    python youtube_publish.py FOLDER1 FOLDER2 --interval-hours 6 --start 2026-07-01T09:00:00

Flags:
    --root DIR          scan DIR for video folders (each has beat_sheet.json + mp4/)
    folders...          explicit video folders (alternative to --root)
    --which {landscape,short,both}   which master(s) to upload (default landscape)
    --interval-hours H  spacing between releases (default 4 = 6/day, matches quota)
    --start ISO         first slot if nothing is scheduled yet (default: now+interval)
    --privacy {private,unlisted}  pre-audit you may prefer unlisted; default private
    --category ID       YouTube category (default 27 = Education)
    --dry-run           compute + print the schedule, upload nothing
    --client SECRET     path to client_secret.json (default ./client_secret.json)
    --token TOKEN       path to cached token.json (default ./youtube_token.json)
    --ledger FILE       upload ledger (default ./youtube_publish_ledger.json)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",     # videos.insert
    "https://www.googleapis.com/auth/youtube",            # playlists / playlistItems
    "https://www.googleapis.com/auth/youtube.force-ssl",  # captions.insert
]
EDU_CATEGORY = "27"


# ── auth ─────────────────────────────────────────────────────────────────────
def get_service(client_secret: Path, token_path: Path):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_secret.exists():
                sys.exit(f"[yt] missing OAuth client secret: {client_secret}\n"
                         f"    See reference/youtube-publishing.md to create one.")
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


# ── reading the channel's current schedule ───────────────────────────────────
def _parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def channel_scheduled_times(youtube) -> list[datetime]:
    """Future publishAt of all private (scheduled) videos on the channel."""
    ch = youtube.channels().list(part="contentDetails", mine=True).execute()
    items = ch.get("items", [])
    if not items:
        return []
    uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    vid_ids, page = [], None
    while True:
        pl = youtube.playlistItems().list(
            part="contentDetails", playlistId=uploads, maxResults=50, pageToken=page).execute()
        vid_ids += [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
        page = pl.get("nextPageToken")
        if not page:
            break
    now = datetime.now(timezone.utc)
    times = []
    for i in range(0, len(vid_ids), 50):
        chunk = vid_ids[i:i + 50]
        vs = youtube.videos().list(part="status", id=",".join(chunk)).execute()
        for v in vs.get("items", []):
            st = v.get("status", {})
            pa = st.get("publishAt")
            if st.get("privacyStatus") == "private" and pa:
                t = _parse_iso(pa)
                if t > now:
                    times.append(t)
    return sorted(times)


def next_base_slot(scheduled: list[datetime], interval: timedelta, start: datetime | None) -> datetime:
    now = datetime.now(timezone.utc)
    if scheduled:
        base = max(scheduled)
    elif start:
        return start
    else:
        base = now
    base = max(base, now)
    return base + interval


def playlist_last_time(youtube, playlist_id: str):
    """The most recent moment anything in this playlist is (or will be)
    public: max of scheduled publishAt (private, future) and published
    publishedAt. None for an empty playlist."""
    vid_ids, page = [], None
    while True:
        pl = youtube.playlistItems().list(
            part="contentDetails", playlistId=playlist_id, maxResults=50,
            pageToken=page).execute()
        vid_ids += [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
        page = pl.get("nextPageToken")
        if not page:
            break
    times = []
    for i in range(0, len(vid_ids), 50):
        vs = youtube.videos().list(part="status,snippet",
                                   id=",".join(vid_ids[i:i + 50])).execute()
        for v in vs.get("items", []):
            st = v.get("status", {})
            if st.get("privacyStatus") == "private" and st.get("publishAt"):
                times.append(_parse_iso(st["publishAt"]))
            elif v.get("snippet", {}).get("publishedAt"):
                times.append(_parse_iso(v["snippet"]["publishedAt"]))
    return max(times) if times else None


# ── metadata ─────────────────────────────────────────────────────────────────
def read_meta(folder: Path) -> dict:
    bs = json.loads((folder / "beat_sheet.json").read_text())
    m = bs.get("metadata", {})
    title = m.get("title", folder.name.replace("-", " "))
    tags = [h.lstrip("#") for h in m.get("hashtags", [])]
    slug = m.get("slug", folder.name)
    yt_md = folder / f"{slug}-youtube.md"
    if yt_md.exists():
        desc = yt_md.read_text().strip()
    else:
        # assemble from narration if the publish step hasn't run
        beats = bs.get("beats", [])
        body = " ".join(b.get("narration_text", "") for b in beats
                        if b.get("beat_type") not in ("INTRO", "OUTRO"))
        tagline = " ".join(f"#{t}" for t in tags)
        desc = f"{title}\n\n{body}\n\n{tagline}\n\nyoutube.com/@NikBearBrown"
    srt = folder / f"{slug}.srt"
    srt_short = folder / f"{slug}-short.srt"
    return dict(slug=slug, title=title, tags=tags, description=desc,
                srt=(srt if srt.exists() else None),
                srt_short=(srt_short if srt_short.exists() else None),
                short_title=m.get("short_title"),
                playlist=m.get("playlist"), playlist_short=m.get("playlist_short"))


def pick_file(folder: Path, slug: str, which: str) -> Path | None:
    landscape = folder / "mp4" / f"{slug}.mp4"
    short = folder / "mp4" / f"{slug}-short.mp4"
    if which == "short":
        return short if short.exists() else None
    return landscape if landscape.exists() else None


def folder_meta(folder: Path) -> dict:
    """Light metadata read (tier, depth_of, slug) for concept pairing."""
    m = json.loads((folder / "beat_sheet.json").read_text()).get("metadata", {})
    return {"slug": m.get("slug", folder.name), "tier": m.get("tier", "short"),
            "depth_of": m.get("depth_of")}


def concept_pairs(ordered):
    """Bear's Notes publishes TWO videos per concept: the 1-min 9:16 SHORT and the
    2-5 min 16:9 DEEP version. They live in different folders, linked by the deep
    beat sheet's `depth_of`. Returns a list of dicts describing each pair."""
    by_slug = {}
    metas = {}
    for f in ordered:
        m = folder_meta(f)
        by_slug[m["slug"]] = f
        metas[f] = m
    pairs = []
    for f in ordered:
        m = metas[f]
        if m["tier"] != "deep":
            continue
        one_min = by_slug.get(m["depth_of"])
        deep_16x9 = pick_file(f, m["slug"], "landscape")
        short_9x16 = pick_file(one_min, m["depth_of"], "short") if one_min else None
        pairs.append({
            "concept": m["depth_of"] or m["slug"],
            "deep_folder": f, "deep_slug": m["slug"], "deep_16x9": deep_16x9,
            "min_folder": one_min, "min_slug": m["depth_of"], "short_9x16": short_9x16,
        })
    return pairs


# ── upload ───────────────────────────────────────────────────────────────────
def upload(youtube, path: Path, meta: dict, publish_at: datetime, privacy: str, category: str) -> str:
    from googleapiclient.http import MediaFileUpload
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["description"][:5000],
            "tags": meta["tags"][:30],
            "categoryId": category,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    if privacy == "private":
        body["status"]["publishAt"] = publish_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    media = MediaFileUpload(str(path), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
    return resp["id"]


def insert_caption(youtube, video_id: str, srt: Path, language="en", name="English"):
    """Upload an .srt as a caption track (captions.insert; needs youtube.force-ssl)."""
    from googleapiclient.http import MediaFileUpload
    body = {"snippet": {"videoId": video_id, "language": language,
                        "name": name, "isDraft": False}}
    media = MediaFileUpload(str(srt), mimetype="application/octet-stream", resumable=False)
    youtube.captions().insert(part="snippet", body=body, media_body=media).execute()


def ensure_playlist(youtube, title: str, cache: dict) -> str:
    """Find a playlist by exact title on the authorized channel, or create it.
    Cached per run so we don't re-list."""
    if title in cache:
        return cache[title]
    pid, token = None, None
    while True:
        resp = youtube.playlists().list(part="id,snippet", mine=True,
                                        maxResults=50, pageToken=token).execute()
        for it in resp.get("items", []):
            if it["snippet"]["title"] == title:
                pid = it["id"]
                break
        token = resp.get("nextPageToken")
        if pid or not token:
            break
    if pid is None:
        resp = youtube.playlists().insert(
            part="snippet,status",
            body={"snippet": {"title": title},
                  "status": {"privacyStatus": "public"}}).execute()
        pid = resp["id"]
        print(f"      + created playlist '{title}'")
    cache[title] = pid
    return pid


def add_to_playlist(youtube, playlist_id: str, video_id: str):
    youtube.playlistItems().insert(
        part="snippet",
        body={"snippet": {"playlistId": playlist_id,
                          "resourceId": {"kind": "youtube#video", "videoId": video_id}}}
    ).execute()


# ── driver ───────────────────────────────────────────────────────────────────
def discover(root: Path) -> list[Path]:
    out = []
    for p in sorted(root.iterdir()):
        if p.is_dir() and (p / "beat_sheet.json").exists() and p.name not in ("media", "shared"):
            out.append(p)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Upload Bear's Notes videos on a rolling schedule.")
    ap.add_argument("folders", nargs="*", help="explicit video folders")
    ap.add_argument("--root", default=None, help="scan this dir for video folders")
    ap.add_argument("--which", choices=["landscape", "short", "both"], default="both")
    ap.add_argument("--require-both", dest="require_both", action="store_true", default=True,
                    help="only queue concepts that have BOTH the 16:9 and 9:16 master (default on)")
    ap.add_argument("--allow-partial", dest="require_both", action="store_false",
                    help="queue a concept even if only one orientation is rendered")
    ap.add_argument("--pairs", dest="pairs", action="store_true", default=True,
                    help="concept = 1-min 9:16 SHORT + 2-5min 16:9 DEEP (linked by depth_of); "
                         "publish both, ready only when both exist (default on)")
    ap.add_argument("--no-pairs", dest="pairs", action="store_false",
                    help="legacy: treat each folder independently")
    ap.add_argument("--interval-hours", type=float, default=4.0)
    ap.add_argument("--schedule-scope", choices=["channel", "playlist"], default="channel",
                    help="playlist: each upload schedules against ITS playlist — "
                         "max(last in playlist + interval, now + floor)")
    ap.add_argument("--floor-minutes", type=float, default=15.0,
                    help="playlist scope: minimum minutes in the future for any slot")
    ap.add_argument("--start", default=None, help="ISO datetime for the first slot if none scheduled")
    ap.add_argument("--privacy", choices=["private", "unlisted"], default="private")
    ap.add_argument("--category", default=EDU_CATEGORY)
    ap.add_argument("--playlist", default=None,
                    help="playlist for landscape/long uploads (find-or-create); "
                         "per-folder override: metadata.playlist")
    ap.add_argument("--shorts-playlist", default=None,
                    help="playlist for 9:16 short uploads; per-folder override: metadata.playlist_short")
    ap.add_argument("--no-captions", dest="captions", action="store_false", default=True,
                    help="do NOT upload the <slug>.srt caption track with each video")
    ap.add_argument("--caption-lang", default="en")
    ap.add_argument("--backfill-extras", action="store_true",
                    help="for videos ALREADY in the ledger, add captions + playlist using their "
                         "stored videoId (no re-upload). Use to retrofit past uploads.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--client", default="client_secret.json")
    ap.add_argument("--token", default="youtube_token.json")
    ap.add_argument("--ledger", default="youtube_publish_ledger.json")
    args = ap.parse_args(argv)

    folders = [Path(f).expanduser().resolve() for f in args.folders]
    if args.root:
        folders += discover(Path(args.root).expanduser().resolve())
    # de-dup, keep order
    seen, ordered = set(), []
    for f in folders:
        if f not in seen and (f / "beat_sheet.json").exists():
            seen.add(f); ordered.append(f)
    if not ordered:
        sys.exit("[yt] no video folders found (give folders or --root).")

    interval = timedelta(hours=args.interval_hours)
    start = parse_start(args.start)

    ledger_path = Path(args.ledger).expanduser().resolve()
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}

    # ── backfill mode: retrofit captions + playlist onto already-uploaded videos ──
    if args.backfill_extras:
        yt = None if args.dry_run else get_service(
            Path(args.client).expanduser().resolve(), Path(args.token).expanduser().resolve())
        pl_cache = {}
        for folder in ordered:
            meta = read_meta(folder)
            for w in (["landscape", "short"] if args.which == "both" else [args.which]):
                key = f"{meta['slug']}::{w}"
                if key not in ledger:
                    continue
                vid = ledger[key]["videoId"]
                pl_name = (meta.get("playlist_short") or args.shorts_playlist or meta.get("playlist") or args.playlist) \
                    if w == "short" else (meta.get("playlist") or args.playlist)
                print(f"[backfill] {key} -> https://youtu.be/{vid}"
                      f"{'  captions' if (args.captions and meta.get('srt')) else ''}"
                      f"{('  playlist=' + pl_name) if pl_name else ''}")
                if args.dry_run:
                    continue
                if args.captions and meta.get("srt"):
                    try:
                        insert_caption(yt, vid, meta["srt"], args.caption_lang)
                        print(f"      + captions: {meta['srt'].name}")
                    except Exception as e:
                        print(f"      ! caption failed: {str(e)[:160]}", file=sys.stderr)
                if pl_name:
                    try:
                        add_to_playlist(yt, ensure_playlist(yt, pl_name, pl_cache), vid)
                        print(f"      + added to playlist '{pl_name}'")
                    except Exception as e:
                        print(f"      ! playlist failed: {str(e)[:160]}", file=sys.stderr)
        return 0

    # build the work list (skip already-uploaded per ledger)
    work, not_ready, pair_links = [], [], []
    if args.pairs:
        # A concept ships TWO videos: the 1-min 9:16 SHORT + the 2-5min 16:9 DEEP.
        for p in concept_pairs(ordered):
            if not (p["deep_16x9"] and p["short_9x16"]):
                miss = " + ".join(x for x, ok in
                                  (("deep 16:9", p["deep_16x9"]), ("1-min 9:16 short", p["short_9x16"]))
                                  if not ok)
                not_ready.append((p["concept"], miss))
                continue
            dk = f"{p['deep_slug']}::landscape"
            sk = f"{p['min_slug']}::short"
            if dk not in ledger:
                work.append((dk, p["deep_folder"], read_meta(p["deep_folder"]), "landscape", p["deep_16x9"]))
            if sk not in ledger:
                work.append((sk, p["min_folder"], read_meta(p["min_folder"]), "short", p["short_9x16"]))
            pair_links.append((sk, dk, p["concept"]))
    else:
        whichs = ["landscape", "short"] if args.which == "both" else [args.which]
        for folder in ordered:
            meta = read_meta(folder)
            slug = meta["slug"]
            have_land = pick_file(folder, slug, "landscape") is not None
            have_short = pick_file(folder, slug, "short") is not None
            if args.require_both and not (have_land and have_short):
                missing = " ".join(m for m, ok in (("16:9", have_land), ("9:16", have_short)) if not ok)
                not_ready.append((slug, missing))
                continue
            for w in whichs:
                key = f"{slug}::{w}"
                if key in ledger:
                    continue
                f = pick_file(folder, slug, w)
                if f is None:
                    print(f"[yt] skip {key}: file not found", file=sys.stderr)
                    continue
                work.append((key, folder, meta, w, f))
    if not_ready:
        print(f"[yt] {len(not_ready)} concept(s) NOT publish-ready:", file=sys.stderr)
        for slug, missing in not_ready[:20]:
            print(f"      - {slug}  (missing {missing})", file=sys.stderr)
        if len(not_ready) > 20:
            print(f"      …and {len(not_ready) - 20} more", file=sys.stderr)
    if not work:
        print("[yt] nothing to upload (all in ledger, not ready, or no files).")
        return 0

    # schedule
    youtube = None
    floor = timedelta(minutes=args.floor_minutes)
    if not args.dry_run:
        youtube = get_service(Path(args.client).expanduser().resolve(),
                              Path(args.token).expanduser().resolve())
        scheduled = [] if args.schedule_scope == "playlist" else channel_scheduled_times(youtube)
    else:
        scheduled = []
        print("[yt] DRY RUN — reading channel skipped; schedule starts from --start or now+interval.")
    slot = next_base_slot(scheduled, interval, start)
    pl_last = {}        # playlist scope: last known slot per playlist title

    print(f"[yt] {len(work)} upload(s), every {args.interval_hours}h, privacy={args.privacy}")
    if scheduled:
        print(f"[yt] latest already-scheduled on channel: {max(scheduled).isoformat()}")
    pl_cache = {}
    for key, folder, meta, w, f in work:
        size = f.stat().st_size / 1e6
        # resolve the playlist this upload belongs to
        if w == "short":
            pl_name = meta.get("playlist_short") or args.shorts_playlist \
                or meta.get("playlist") or args.playlist
        else:
            pl_name = meta.get("playlist") or args.playlist
        # playlist-scoped scheduling: next = max(now + floor, last in playlist + interval)
        if args.schedule_scope == "playlist":
            now = datetime.now(timezone.utc)
            if pl_name and pl_name not in pl_last and youtube is not None:
                pid = ensure_playlist(youtube, pl_name, pl_cache)
                last = playlist_last_time(youtube, pid)
                if last:
                    pl_last[pl_name] = last
            last = pl_last.get(pl_name)
            slot = max(now + floor, last + interval) if last else now + floor
            if pl_name:
                pl_last[pl_name] = slot
        stamp = slot.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        extras = []
        if pl_name:
            extras.append(f"playlist='{pl_name}'")
        if args.captions and meta.get("srt"):
            extras.append("captions")
        tail = ("  [" + ", ".join(extras) + "]") if extras else ""
        print(f"  {stamp}  {w:9}  {meta['slug']}  ({size:.1f} MB){tail}")
        if not args.dry_run:
            try:
                vid = upload(youtube, f, meta, slot, args.privacy, args.category)
            except Exception as e:
                msg = str(e)
                if "quota" in msg.lower():
                    print(f"\n[yt] daily quota exhausted (~6 uploads/day on the default 10k). "
                          f"Re-run tomorrow — the ledger skips what's done and the schedule "
                          f"keeps appending.\n      ({msg[:160]})", file=sys.stderr)
                    break
                print(f"[yt] upload failed for {key}: {msg[:200]}", file=sys.stderr)
                continue
            ledger[key] = {"videoId": vid, "publishAt": stamp, "file": str(f)}
            ledger_path.write_text(json.dumps(ledger, indent=2))
            print(f"      -> https://youtu.be/{vid}  (scheduled {stamp})")
            # captions (best-effort). Shorts REFUSE uploaded caption tracks
            # (captions.insert 403s on a vertical <3:00 video — YouTube uses
            # auto-captions there), so the short surface skips cleanly.
            if w == "short":
                print("      · captions: skipped (Shorts use YouTube auto-captions)")
            elif args.captions and meta.get("srt"):
                try:
                    insert_caption(youtube, vid, meta["srt"], args.caption_lang)
                    print(f"      + captions: {meta['srt'].name}")
                except Exception as e:
                    print(f"      ! caption upload failed: {str(e)[:160]}", file=sys.stderr)
            # playlist (best-effort)
            if pl_name:
                try:
                    pid = ensure_playlist(youtube, pl_name, pl_cache)
                    add_to_playlist(youtube, pid, vid)
                    print(f"      + added to playlist '{pl_name}'")
                except Exception as e:
                    print(f"      ! playlist add failed: {str(e)[:160]}", file=sys.stderr)
        slot = slot + interval

    # MANUAL funnel step: the Related Video link can't be set via the Data API.
    # Each 1-min Short points at its concept's DEEP 2-5min 16:9 (the worked example).
    if pair_links:
        print("\n[yt] MANUAL — set Related Video in Studio for each Short (1-min 9:16 -> deep 16:9):")
        for sk, dk, concept in pair_links:
            svid = ledger.get(sk, {}).get("videoId")
            dvid = ledger.get(dk, {}).get("videoId")
            s = f"https://youtu.be/{svid}" if svid else "(short videoId)"
            d = f"https://youtu.be/{dvid}" if dvid else "(deep videoId)"
            print(f"      - {concept}:  Short {s}  ->  Deep {d}")

    if args.dry_run:
        print("\n[yt] dry run only — no uploads. Re-run without --dry-run to publish.")
    else:
        print(f"\n[yt] done. Ledger: {ledger_path}")
    return 0


def parse_start(s):
    """Parse --start. Naive strings ('2026-07-01T09:00:00') are treated as LOCAL
    time so '9am' means 9am where you are; offset-aware strings are respected."""
    if not s:
        return None
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return d


if __name__ == "__main__":
    raise SystemExit(main())
