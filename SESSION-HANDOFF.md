# Unreal Reels — session handoff

_Working repo: `/Users/nik/Documents/Cowork/unreal-reels`_

## What this session did

1. **Oriented** in the Unreal Reels repo (AGENTS.md, README, getting-started, scripts/aspects).
2. **Ported the Bose mini-bio into the repo as the canonical Bios example** at
   `reels/bio-bose/` — copied from the finished `Manim/bio-bose/` (a ~30s Satyendra Nath
   Bose mini-bio). Includes `beat_sheet.json`, `bio-bose-youtube.md`, the Manim scene
   (`bio_bose.py`, `bn_layout.py`, `fonts/`), narration (`mp3/`), footage (`clips/`), and
   both finished cuts (`mp4/bio-bose.mp4` 16:9 + `mp4/bio-bose-short.mp4` 9:16). Added a
   `reels/bio-bose/README.md` marking it as the copy-me template.
3. **Built `scripts/recreate.sh`** — a one-command "recreate an existing reel" dispatcher.
   Reads `beat_sheet.json` and either rebuilds a Manim mini-bio into an MP4 (Bios) or opens
   a Remotion project in studio (Songbird/lecture). Bios path needs **no API keys** because
   the reel's audio + clips are committed.
4. **Updated `docs/getting-started.md`** — new lead section "Step 1 — recreate an existing
   video (one command)"; relabeled the old "Step 0 / 0.5" headings so numbering flows.
5. **Fixed the 9:16 equation card** (`_card_equation`): in portrait the label
   "BOSE-EINSTEIN DISTRIBUTION" now scales to the band width (much bigger) and is stacked
   cleanly ABOVE the whole equation, and the equation is fit to the band so it no longer
   runs to the edge. **16:9 layout unchanged.** Applied to BOTH copies:
   `reels/bio-bose/bio_bose.py` AND `Manim/bio-bose/bio_bose.py` (the one being rendered).

## Service keys (as of this session)

None set in the checked environment — `ELEVENLABS_API_KEY`, `FAL_KEY` missing; Higgsfield
CLI not authenticated; no `.env`. Not needed to *recreate* Bose (assets committed); needed
to author a *new* figure (ElevenLabs = narration, Higgsfield = Soul-ID + clips).

## Immediate next step (unverified)

Re-render the 9:16 Short and confirm the equation-card fix looks right:

```bash
cd "/Users/nik/Documents/Cowork/unreal-reels" && bash scripts/recreate.sh reels/bio-bose --short
```

If the label reads as *too* big next to the equation, dial it from `0.92` → ~`0.75–0.80`
of band width in `_card_equation` (both copies).

## Open threads / not yet done

- **Verify** the re-rendered Short (couldn't run Manim in-session — no local Manim here).
- **Propagate the equation fix to the template** `aspects/bios/mini-bio/templates/` so future
  bios inherit it (only the two bio-bose copies were patched).
- **User's own bio** — not started. Goal: an AI figure. Suggested **Ada Lovelace** (clean
  structural twin to Bose, but pre-AI/computing origin); truer-AI alternatives: **Turing,
  Frank Rosenblatt (perceptron), John McCarthy, Claude Shannon**. Flow: author
  `reels/<slug>/beat_sheet.json` (who→why→impact, clip/card rhythm, open+close on Soul-ID),
  then set keys → audio → references → storyboard → video → overlay.
- **Offered but not done:** add the one-command block to `README.md`; wire a `remotion/`
  recreate example (e.g. the `music-video` reel) to exercise the Remotion branch.
- **Git:** all edits are the LOCAL working copy — commit + push to update github.com.

## Key paths

- Example reel: `reels/bio-bose/` · finished cuts in `reels/bio-bose/mp4/`
- One-command recreate: `scripts/recreate.sh <reel> [--short]`
- Equation card code: `_card_equation` in `reels/bio-bose/bio_bose.py` and `Manim/bio-bose/bio_bose.py`
- Bios authoring contract: `aspects/bios/mini-bio/SKILL.md` · operating contract: `AGENTS.md`
