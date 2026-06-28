# Auto-publishing Bear's Notes to YouTube on a schedule

`scripts/youtube_publish.py` uploads each video as **private with a future `publishAt`**, so YouTube flips it public automatically — a drip release, not all at once. The next slot is the **latest already-scheduled video on your channel + the interval** (default 4 hours = 6/day, matched to the upload quota), so re-running just extends the queue.

## The one thing that can block this: the API audit

A brand-new Google Cloud API project is **unaudited**, and YouTube **locks all API uploads to private** for unaudited projects — `publishAt` will *not* make them public until the project passes a one-time audit. Plan for this:

1. Build and test everything (uploads will land as private — useful for staging).
2. Submit the [YouTube API audit / extended-quota form](https://support.google.com/youtube/contact/yt_api_form) for your project.
3. Once approved, scheduled videos go public at their `publishAt` as intended.

Until then, the script still works for **staging** (everything uploads private on schedule); only the automatic public flip waits on the audit.

## One-time setup (≈15 min)

1. **Create a project** at [console.cloud.google.com](https://console.cloud.google.com) and **enable** "YouTube Data API v3" (APIs & Services → Library).
2. **OAuth consent screen**: User type **External**; fill the app name/email; add your own Google account under **Test users** (so you can authorize before verification).
3. **Credentials → Create credentials → OAuth client ID → Desktop app.** Download the JSON and save it next to where you'll run the script as **`client_secret.json`** (or pass `--client /path/to.json`).
4. **Install the libraries** in your `ai` venv:

   ```
   pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
   ```

5. First real run opens a browser for consent and caches a token in `youtube_token.json` (re-used after that; it auto-refreshes).

## Quota — why uploads spread over days

`videos.insert` costs **1,600 units**; the default project quota is **10,000 units/day**, so **~6 uploads per day**. The default **4-hour cadence = 6 releases/day, which matches that upload budget exactly** (6 in, 6 out — a steady queue). You *can* set a faster publish spacing, but if it exceeds 6/day the release schedule will outrun what you can upload until you request more quota (free, via the same audit/quota form). The script handles this — when the daily quota runs out it stops cleanly; re-run the next day and the ledger skips what's done while the schedule keeps appending. Request a quota increase if you want to upload faster.

## Usage

Always preview first (spends no quota, doesn't even touch the channel):

```
ai
cd ~/Documents/Cowork/Manim
python ../bears-doodles/scripts/youtube_publish.py --root . --which landscape --dry-run
```

Then upload + schedule for real (4-hour cadence = 6/day, appended after anything already scheduled):

```
python ../bears-doodles/scripts/youtube_publish.py --root . --which landscape
```

Useful flags: `--which {landscape,short,both}` (Shorts upload as separate videos), `--interval-hours 3`, `--start 2026-07-01T09:00:00` (first slot if nothing is scheduled yet; naive time = your local time), `--privacy {private,unlisted}`, `--category 27` (Education).

Files used per video folder: `mp4/<slug>.mp4` (landscape) and `mp4/<slug>-short.mp4` (Short); title + tags from `beat_sheet.json` metadata; description from `<slug>-youtube.md` if present (run `publish` / `package_video.py` first for a polished description), else assembled from the narration. Uploads are recorded in `youtube_publish_ledger.json` so re-runs never double-post.

## The two-video model + Related Video rule

**Each concept publishes exactly TWO videos, in two folders:**
- the **1-min 9:16 Short** — `<1-min-folder>/mp4/<slug>-short.mp4` (best for the vertical feed)
- the **2–5 min 16:9 deep** worked-example — `<deep-folder>/mp4/<deep-slug>.mp4` (best for long-form)

The 1-min *16:9* and the deep *9:16* are **not published** — wrong fit for their surfaces. The two folders are linked by the deep beat sheet's `depth_of: <1-min-slug>`.

- **Pairs mode (default).** The script pairs each deep folder with its 1-min source and queues a concept **only when both the deep 16:9 and the 1-min 9:16 short exist** — otherwise it's listed "NOT publish-ready" and skipped. At 6 uploads/day that's **3 concepts/day** (deep + short each). `--no-pairs` falls back to the legacy single-folder mode.
- **Related Video is a manual Studio step** (not in the Data API). The rule: **each 1-min Short points at its concept's deep 16:9** (the worked example genuinely has *more* than the Short — not a same-content twin). The script prints a per-concept "Short → Deep" checklist after each run.

## Notes
- Category 27 = Education; `selfDeclaredMadeForKids` is set to false.
- `--which short` posts the 9:16 cut as its own video (YouTube auto-classifies vertical < 3 min as a Short).
- The token and ledger are per-directory — run from a consistent folder (e.g. `~/Documents/Cowork/Manim`).
