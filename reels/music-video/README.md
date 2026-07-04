# music-video — a build-it-yourself tutorial reel

A complete, ready-to-run Unreal Reels **music video**, so you can learn the pipeline without
sourcing anything. The song, lyrics, beat grid, 28-beat `beat_sheet.json`, character art, 16:9
storyboard slides, and 28 pre-generated clips are **already here**. You do two things:

1. **Assemble what's here** into a finished video — no API keys, no accounts. Proves the pipeline end-to-end.
2. **Make your own version** — regenerate each beat in **Midjourney** from the supplied prompts + reference art, drop your clips in, and reassemble.

Song: *"Who's Gonna Bell That Cat"* (Parvati) · 28 beats · ~162 s · 16:9 · ink-and-gouache moonlit storybook.

---

## What's in this folder

| Path | What it is |
|---|---|
| `song.wav` | the mastered track — the **master clock**; every beat is timed to it |
| `lyrics.txt` | the lyric sheet |
| `beat_sheet.json` | the single source of truth — 28 beats, timings, prompts, asset paths |
| `beat_data.json` / `lyrics.json` | librosa beat grid + word-level lyric timing |
| `plates/` | character + background art (JPG) — the **reference images** you feed Midjourney |
| `slides/` | the 16:9 storyboard stills (JPG) — `B01_A_start` … each beat's **target frame** |
| `video-16x9/raw/` | 28 pre-generated clips `B01.mp4 … B28.mp4` — the inputs for Phase 1 |
| `midjourney_prompts.txt` | one **image** prompt per beat, each line starting with its beat id |
| `midjourney_motion.txt` | one **Animate** (motion) prompt per beat |

> Images are JPG (not PNG) on purpose — same look, ~10× smaller. The heavy files (`song.wav`,
> `video-16x9/`) are git-ignored; the reel's *definition* is what's meant to be shared.

---

## Phase 1 — assemble what's here (no keys needed)

This cuts each clip to its exact beat length, stitches all 28 in order, and muxes `song.wav`.
Run it from the repo root:

```bash
cd "/Users/nik/Documents/Cowork/unreal-reels" && ASSEMBLE_ONLY=1 FINAL=1 TAG=16x9 ASPECT=16:9 W=1920 H=1080 bash scripts/generate_video.sh reels/music-video
```

Output: `reels/music-video/music-video.16x9.mp4` (1920×1080, ~162 s, with sound).
Needs only `ffmpeg` + `jq` — no Higgsfield/ElevenLabs/fal keys.

---

## Phase 2 — make your own version in Midjourney

You'll replace the supplied clips with your own, one beat at a time, then rerun the same
assemble command. The trick that makes this painless: **every prompt starts with its beat id**,
so Midjourney names the download `B01_…​.mp4` and you can rename it straight back to `B01.mp4`.

### Step 1 — generate each beat's still

Open the prompt list:

```bash
open "/Users/nik/Documents/Cowork/unreal-reels/reels/music-video/midjourney_prompts.txt"
```

For each beat, paste its line into Midjourney and drag in that beat's **reference plates** (the
`plates/…jpg` files listed in the table below) so the characters stay consistent. Example — B01:

```text
B01 Three little mice creep out along the base of the moonlit fence at night, hand-drawn ink-and-gouache storybook illustration, unified moonlit lighting, matching linework and texture, characters at consistent scale, no text, no watermark --ar 16:9
```

Use `slides/B01_A_start.jpg` as your visual target for what that beat should look like.

### Step 2 — animate the still

Pick your favorite still, hit **Animate**, and paste the matching motion line. Open them with:

```bash
open "/Users/nik/Documents/Cowork/unreal-reels/reels/music-video/midjourney_motion.txt"
```

Example — B01:

```text
B01 Storybook fable: slow push-in as the mice scurry together. Smooth hand-drawn animation, gentle motion, no text.
```

### Step 3 — download every clip

Download each finished clip. Because the prompt began with `B01`, it saves as something like
`B01_Three_little_mice_....mp4`. Keep them all in one folder (e.g. `~/Downloads`).

### Step 4 — rename by the beat id and drop them in

This renames every `B01_*.mp4 → B01.mp4` and moves it into the reel, replacing the supplied clip:

```bash
cd ~/Downloads && for f in B[0-9][0-9]_*.mp4; do mv -f "$f" "/Users/nik/Documents/Cowork/unreal-reels/reels/music-video/video-16x9/raw/${f:0:3}.mp4"; done
```

You don't have to do all 28 at once — any beat you haven't replaced just keeps the original clip.

### Step 5 — reassemble

Run the exact same command as Phase 1:

```bash
cd "/Users/nik/Documents/Cowork/unreal-reels" && ASSEMBLE_ONLY=1 FINAL=1 TAG=16x9 ASPECT=16:9 W=1920 H=1080 bash scripts/generate_video.sh reels/music-video
```

Your new clips are now in `music-video.16x9.mp4`. Each is auto-fit to its beat length, so timing
stays locked to the song no matter how long Midjourney's clip is.

---

## Beat map — prompts, reference art, and target slides

Full image prompts are in `midjourney_prompts.txt`; motion prompts in `midjourney_motion.txt`.

| Beat | Len | Lyric | Reference plates (drag into MJ) | Target slide |
|---|---|---|---|---|
| B01 | 5.77s | Late one night behind the wall | `plates/background_v2.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg, plates/mice_v3.jpg` | `slides/B01_A_start.jpg` |
| B02 | 5.9s | Little mice held a midnight call | `plates/background_v3.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg, plates/mice_v3.jpg` | `slides/B02_A_start.jpg` |
| B03 | 5.8s | Said that cat's got claws and a silent tread | `plates/background_v4.jpg, plates/orange-cat_v3.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg` | `slides/B03_A_start.jpg` |
| B04 | 5.67s | One more scare and I might drop dead | `plates/background_v5.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg` | `slides/B04_A_start.jpg` |
| B05 | 5.53s | Brown back grumbled ain't no peace | `plates/background_v2.jpg, plates/mice_v3.jpg, plates/mice_v1.jpg` | `slides/B05_A_start.jpg` |
| B06 | 5.93s | I dive for crumbs and lose my fleece | `plates/background_v1.jpg, plates/mice_v2.jpg` | `slides/B06_A_start.jpg` |
| B07 | 5.9s | She's a ghost with fangs and golden eyes | `plates/background_v6.jpg, plates/orange-cat_v2.jpg, plates/mice_v1.jpg` | `slides/B07_A_start.jpg` |
| B08 | 5.87s | We gotta act before one more dies | `plates/background_v3.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg, plates/mice_v3.jpg` | `slides/B08_A_start.jpg` |
| B09 | 5.6s | Gray ear said let's bite and run | `plates/background_v4.jpg, plates/mice_v4.jpg, plates/mice_v1.jpg` | `slides/B09_A_start.jpg` |
| B10 | 5.93s | A hundred squeaks and she'll be done | `plates/background_v5.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg, plates/mice_v3.jpg` | `slides/B10_A_start.jpg` |
| B11 | 5.9s | But white whisker said I've got a plan | `plates/background_v2.jpg, plates/mice_v5.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg` | `slides/B11_A_start.jpg` |
| B12 | 5.93s | We'll hang a bell on that devil if we can | `plates/background_v3.jpg, plates/mice_v5.jpg, plates/mice_v1.jpg` | `slides/B12_A_start.jpg` |
| B13 | 5.4s | Ding a ling they all cried loud | `plates/background_v6.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg, plates/mice_v3.jpg` | `slides/B13_A_start.jpg` |
| B14 | 5.97s | Freedom's ringin sang the crowd | `plates/background_v4.jpg, plates/mice_v2.jpg, plates/mice_v3.jpg, plates/mice_v4.jpg` | _(regenerate)_ |
| B15 | 5.73s | We'll hear her jingle we'll dance with glee | `plates/background_v5.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg, plates/mice_v3.jpg` | `slides/B15_A_start.jpg` |
| B16 | 5.8s | She'll never again sneak up on me | `plates/background_v2.jpg, plates/orange-cat_v7.jpg, plates/mice_v1.jpg` | `slides/B16_A_start.jpg` |
| B17 | 5.43s | But brown back hushed the rebel cheer | `plates/background_v3.jpg, plates/mice_v3.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg` | `slides/B17_A_start.jpg` |
| B18 | 5.7s | With a voice like truth and a touch of fear | `plates/background_v6.jpg, plates/mice_v3.jpg, plates/mice_v1.jpg` | `slides/B18_A_start.jpg` |
| B19 | 6.03s | That bell won't ring itself my friend | `plates/background_v4.jpg, plates/mice_v3.jpg` | `slides/B19_A_start.jpg` |
| B20 | 5.97s | Who's gonna tie it round her end | `plates/background_v5.jpg, plates/orange-cat_v4.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg` | `slides/B20_A_start.jpg` |
| B21 | 5.5s | White whisker coughed well not my gig | `plates/background_v2.jpg, plates/mice_v5.jpg, plates/mice_v1.jpg` | `slides/B21_A_start.jpg` |
| B22 | 5.87s | I got a limp and a twisted twig | `plates/background_v3.jpg, plates/mice_v5.jpg` | `slides/B22_A_start.jpg` |
| B23 | 5.97s | Gray ear said that ain't my track | `plates/background_v6.jpg, plates/mice_v4.jpg, plates/mice_v1.jpg` | `slides/B23_A_start.jpg` |
| B24 | 5.97s | Since I near got snapped I don't go back | `plates/background_v4.jpg, plates/mice_v4.jpg` | `slides/B24_A_start.jpg` |
| B25 | 5.53s | So one by one they slunk to bed | `plates/background_v5.jpg, plates/mice_v1.jpg, plates/mice_v2.jpg, plates/mice_v3.jpg` | `slides/B25_A_start.jpg` |
| B26 | 5.9s | No bell was hung no word was said | `plates/background_v2.jpg, plates/orange-cat_v4.jpg` | `slides/B26_A_start.jpg` |
| B27 | 5.9s | You can preach and plan and talk real flat | `plates/background_v3.jpg, plates/mice_v1.jpg, plates/black-cat_v3.jpg` | `slides/B27_A_start.jpg` |
| B28 | 5.43s | But baby someone's gotta bell that cat | `plates/background_v6.jpg, plates/orange-cat_v2.jpg, plates/black-cat_v3.jpg` | `slides/B28_A_start.jpg` |

---

## The one rule that matters

`image_prompt` / the Midjourney prompt is a **visual scene only** — never the lyric text, or the
model bakes gibberish caption text into the frame. Captions come later as a clean overlay.
Identity comes from the **reference plates**, not from re-describing the characters.
