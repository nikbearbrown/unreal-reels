# ONBOARDING — publishing from a second machine (Aditi)

The publisher is
`books/unreal-reels/aspects/explainer/bears-doodles/scripts/youtube_publish.py`
(clone of the PUBLIC repo `github.com/nikbearbrown/unreal-reels`). Credentials
NEVER live inside any repo — they live in a folder like this one
(`publish-workspace/`), outside every clone. The repo's .gitignore blocks the
credential filenames as a second line of defense; don't rely on it.

## What crosses machines and what never does

| file | crosses? | why |
|---|---|---|
| `client_secret.json` | YES — copy to her publish-workspace | the OAuth APP credential, not an account credential |
| `youtube_token.json` | **NEVER** | bound to the Google login that minted it; each person mints their own |
| `youtube_publish_ledger.json` | **NEVER** | machine-local schedule state; two ledgers in one playlist double-book slots |

## Setup on the new machine (once)

1. Create `~/Documents/publish-workspace/` — OUTSIDE every repo clone, and
   confirm it is not in an iCloud/Drive-synced path.
2. Copy `client_secret.json` into it (AirDrop/USB — not email, not git).
3. Prerequisite in Google Cloud console (Bear, once): if the OAuth consent
   screen is in **Testing** status, either add Aditi's Google account as a
   test user (refresh tokens then EXPIRE EVERY 7 DAYS) or — better — flip the
   app to **In production** (no verification needed for these scopes,
   private use).
4. First run of the publisher opens a browser OAuth flow. Aditi signs into
   HER Google account, and at the account chooser **selects the BRAND
   CHANNEL, not her personal channel**. This is the #1 mistake; an upload to
   the wrong channel cannot be moved. Her manager role on the brand channel
   is what authorizes her — revoking the role revokes her access without
   touching anyone else's token.
5. The flow writes `youtube_token.json` into her publish-workspace. Hers,
   never shared, revocable independently.

## First run is a throwaway

Upload ONE private test video with no scheduling, then confirm in YouTube
Studio that it landed on the brand channel under her manager identity —
BEFORE touching a real reel or the drip scheduler.

## The ledger law (both machines, forever)

One playlist = one publishing machine = one ledger. The drip scheduler
(`--schedule-scope playlist --interval-hours 2 --floor-minutes 15`) computes
slots from the LOCAL ledger only; a second machine publishing into the same
playlist will double-book premiere slots. Split by series: Aditi publishes
playlists that are hers end-to-end; the quantum playlists stay on Bear's
Mac. Never merge or copy ledgers.

## Division of labor (the default)

Media production needs NO credentials: SHOTLIST → generate/download → drop in
`reels/<slug>/pantry/` with the beat prefix (`B03 — anything.mp4`) → `pantry`
→ rebuild. Only publishing needs this file's setup. When in doubt, produce on
any machine, publish from one.
