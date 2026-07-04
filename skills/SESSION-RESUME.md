# Session resume — lecture-video pipeline (as of this session)

Paste the block at the bottom into a new conversation to continue.

---

## Where the whole thing stands

**Pipeline:** `chapter.md → [lecture-assets] → [slide-deck] → [deck-lecture] → narrated .mp4`
All three skills are built and live in `unreal-reels/skills/`. This session built the
missing middle (slide-deck), added a drawer contract to lecture-assets, and ran the
**entire pipeline end-to-end on Chapter 1** of the computational-skepticism book —
including a new **progressive-figure** tier in deck-lecture.

## What got built / done this session

1. **slide-deck skill (stage 2) — DONE & regression-tested.**
   `unreal-reels/skills/slide-deck/` — `build_plan.py` (Phase 0 gate) → `bind_assets.py`
   (Phase 1 report) → `emit_deck.py` (Phase 2: plan → `.dc.html`, copies runtime + `_ds`,
   folds chart drawers, copies figures) → `verify_deck.py` (Phase 3 audit). Nine slide
   archetypes in `templates/archetypes.py`. Decisions locked: drawer.js contract +
   SVG-raster fallback; single Phase-0 gate; re-derived Ch.7 as regression target
   (round-trips through deck-lecture's `extract_slides.py`).

2. **lecture-assets drawer contract — DONE.** `scripts/new_chart.py` scaffolds
   `charts/<name>.drawer.js` (the live-D3 source of truth) + a synced standalone `.html`.
   emit_deck folds drawers into the deck's `data-dc-script` registry (live D3, no iframes).

3. **deck-lecture progressive-figure tier — NEW, built this session.** A visual tier that
   reveals an authored SVG's parts in sync with narration. SVG parts wrapped in
   `<g class="pf pf-N">`; `ProgressiveFigure.tsx` fades each group in on its narration
   line (scoped CSS, no rasterization). Scaffold embeds the SVG text + counts groups from
   `<folder>/figures.json`. Also fixed this session: the **bullets** tier now uses a
   sliding window (max 6 on screen) so long slides get a reveal every ~5–6s without a wall
   of text; **font** fix (Inter fallback chain + mono-numbers regex only fires on real data
   like `99%`/`0.8`, not ordinals/years); **no-auto-render** rule baked into scaffold +
   SKILL (stop at `npm run studio`, human renders).

4. **Chapter 1 full run:**
   - **Assets pool** (`csai/lectures/01-the-skeptics-toolkit/assets/`): imported 9 book
     figures (flagged 7 as stub bars), authored 2 live D3 charts (turkey-confidence-timeline,
     cost-asymmetry) + 4 SVG figures (four-moves-checklist, artifact-vs-world,
     five-supervisory-capacities, fluency-trap-mechanism) + 8 doodle candidates + cajal report.
   - **Deck**: `deck/01-the-skeptics-toolkit.dc.html` (14 slides, verified, uses 6 pool assets).
   - **Video** (`deck/`): narration written (14 beats, discuss-don't-read passed), audio
     generated on the Mac (ElevenLabs, ~10.5 min, durations locked), captions aligned,
     bullets for 6 text slides, progressive figures for 4 figure slides, 2 live charts,
     2 short dividers. Remotion project scaffolded and ready.

## Immediate next action (Ch.1 video)

The project is scaffolded in place. Preview, then YOU render (never auto-render):

```
cd /Users/nik/Documents/Cowork/computational-skepticism-for-ai/lectures/01-the-skeptics-toolkit/deck/remotion && npm run studio
```

Scrub S05 / S07 / S10 / S12 (the progressive figures) — that tier is new and was NOT
render-tested, so Studio is the source of truth. If good, `npm run render` →
`remotion/out/skeptics-toolkit.mp4`. If a group won't fade / a figure overflows / a TS
error on launch, report it.

## Open threads / known rough edges

- **Progressive-figure tier is unverified by an actual render** — needs a Studio eyeball.
- `prerender_deck.py` and `scaffold_remotion.py` resolve `--deck` relative to the CWD, not
  the folder arg — pass an ABSOLUTE `--deck` path (bit me twice this session).
- The 2 section dividers (S03, S09) still render as live deck iframes (short, fine); could
  be `sections.json` native cards later.
- Ch.1 book figures 08 & 09 (jpg-only) left as unvetted candidates — human eyeball.
- Doodle candidates authored but unused (inventory).
- **Chapter 7 open thread (older):** still needs generate_audio for the 8 equation-tangent
  beats (`--only S05T S07T S09T S14T S16T S24T S29T S32T`), re-scaffold, final render, then
  timestamped YouTube chapters. Ch.7 fairness lecture already on YouTube: https://youtu.be/5RZKbSXa-E8

## Non-negotiable conventions (reinforced this session)

- **Filenames kebab-case, NO spaces** (e.g. `01-the-skeptics-toolkit.dc.html`) — quoting-free,
  tab-completes. (The old `Chapter 7 - Fairness Metrics.dc.html` spaced name was a mistake.)
- **No static screen > ~5s** while narration runs — progressive disclosure (bullets window
  or progressive figure); charts animate; only short dividers hold.
- **Use the authored assets** — don't discard figures; animate them (progressive-figure tier).
- **Never auto-render** — stop at `npm run studio`; the human approves and renders.
- Palette: one red `#C8102E`, warm ink `#2a1a0e`, grays; **no blue**. Overlays = Inter
  (local file, with fallback); numbers = JetBrains Mono, and ONLY on real data.
- Human gates: Phase-0 deck plan, Phase-1 narration script (GATE 0 before audio), Studio
  before render. Hand off shell commands copy-paste-ready with ABSOLUTE paths.

## Where things are

- Skills: `/Users/nik/Documents/Cowork/unreal-reels/skills/{slide-deck,lecture-assets,deck-lecture}`
- Design system: `/Users/nik/Documents/Cowork/unreal-reels/brutalist/{DESIGN.md,EQUATIONS.md}`
- Pipeline overview: `/Users/nik/Documents/Cowork/unreal-reels/skills/PIPELINE.md`
- Book: `/Users/nik/Documents/Cowork/computational-skepticism-for-ai` (chapters/, images/, lectures/<slug>/)
- Ch.1 work: `.../computational-skepticism-for-ai/lectures/01-the-skeptics-toolkit/` (assets/, deck/)
- Ch.7 reference deck: `/Users/nik/Documents/Cowork/unreal-reels/lectures/fairness-metrics-and-impossible-choices`

---

## Paste-into-new-conversation block

```
Continuing the chapter → lecture-video pipeline. Read these FIRST (source of truth):
- /Users/nik/Documents/Cowork/unreal-reels/skills/SESSION-RESUME.md   (full state — read this first)
- /Users/nik/Documents/Cowork/unreal-reels/skills/PIPELINE.md
- /Users/nik/Documents/Cowork/unreal-reels/skills/{slide-deck,lecture-assets,deck-lecture}/SKILL.md
- /Users/nik/Documents/Cowork/unreal-reels/brutalist/DESIGN.md and EQUATIONS.md

STATE: all 3 pipeline skills built. Ran the FULL pipeline on Chapter 1 of
computational-skepticism-for-ai. The Ch.1 lecture video is scaffolded in
lectures/01-the-skeptics-toolkit/deck/remotion and ready to PREVIEW in Remotion Studio
(NOT yet rendered — human render gate). A new progressive-figure tier was added to
deck-lecture and needs a Studio eyeball (S05/S07/S10/S12) — it was not render-tested.

Immediate next step: I'll run `npm run studio` on that project and report how the
progressive figures + bullets + charts look; help me fix anything off, then I render.

Conventions: kebab-case filenames (no spaces); no static screen >~5s (progressive
disclosure); use authored assets (animate, don't discard); NEVER auto-render (stop at
studio); one red #C8102E + ink + grays, no blue; hand off commands with ABSOLUTE paths.
```
