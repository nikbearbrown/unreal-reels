# Unreal Reels / Songbird — System Review

*Reviewed 2026-07-01 by Claude Fable 5. The system was built across sessions with Claude Opus. This is a full inventory of every skill and function, followed by an honest critique.*

---

## 1. What this system is

Unreal Reels is one **audio-first, phase-gated video engine** with genre lenses on top. Every pipeline in the repo follows the same law: **audio is the master clock** — narration or music is generated and *measured* first, and every downstream duration (clip length, slide hold, caption timing) is derived from real audio, never estimated. Every pipeline is **phase-gated**: the human approves at the cheapest decision point (the plan, the script, the storyboard keeper, the Studio preview) and only the failing unit is ever regenerated.

The single spine is **`beat_sheet.json`** — one beat = one narrated/sung unit = one visual. Every skill emits it, reads it, or writes back to it. This one schema is why the parts compose: `generate_audio.py` (built for Bear's Doodles) drives lecture videos, muzak's forced-alignment approach drives lecture captions, and the Remotion overlay theme is ported across three pipelines.

There are now **two production families**, not one:

```
REELS (storyboard-first)                    LECTURES (deck-first)
story/lyrics → beats → audio →              chapter.md → asset pool → .dc.html deck →
references → stills → video → overlay       narrated Remotion lecture video
  aspects: songbird · bios · explainer        skills: lecture-assets → slide-deck → deck-lecture
  skills:  lyric-match · songbird-dance
```

External services: **ElevenLabs** (voice clone TTS), **Higgsfield** (SoulID references, FLUX.2 storyboards, Seedance/Hailuo video), **fal.ai** (optional LoRA/alt models), plus local **ffmpeg**, **Remotion**, **librosa**, **faster-whisper**.

---

## 2. The engine — `scripts/` (26 files)

The storyboard engine every aspect drives. Grouped by phase:

**Beats & audio**

| Script | Function |
|---|---|
| `segment_story.py` | Story/script → `beat_sheet.json` (Phase 0/2 segmenter) |
| `build_dance_beatsheet.py` | Dance-mode beat sheet — long (~10–15s) downbeat-aligned segments |
| `generate_audio.py` | ElevenLabs TTS per beat; measures real durations (the master clock) |
| `slice_beat_audio.sh` | Cut master audio into one clip per beat (feeds Seedance audio-sync) |

**References & storyboard**

| Script | Function |
|---|---|
| `generate_references.sh` | Stage 0 — SoulID character reference plates (you pick keepers) |
| `generate_storyboard.sh` / `generate_storyboard_flux.sh` | Per-beat stills, FLUX.2 multi-reference against the library |
| `generate_storyboard_songbird.sh` | Storyboard variant for Songbird beat sheets |
| `generate_dance_storyboard.sh` | FLUX 16:9 stills for a dance reel |
| `generate_startend_storyboard.sh` | Start/end frames for a MIXED dance reel |
| `generate_composite_storyboard.sh` | FLUX multi-input storyboard for a STORY reel |
| `generate_stills_916.sh` | 9:16 verticals from existing 16:9 stills |
| `generate_duet_169.sh` / `composite_duet_169.py` | 16:9 two-character duet stills (outpaint / deterministic no-model composite) |
| `midjourney_prompts.sh` / `rename_midjourney.sh` | Paste-ready Midjourney prompts per beat; rename bulk downloads back to beat IDs |
| `export_discord.sh` | Downsized JPG of each keeper still → `<reel>/discord/` (the committed definition) |

**Video & assembly**

| Script | Function |
|---|---|
| `generate_video.sh` | Per-beat image+audio → video for a DANCE beat sheet (renamed from `generate_video_seedance.sh`) |
| `generate_video_songbird.sh` | Per-beat image→video for a Songbird beat sheet |
| `make_shotlist.py` | Paste-ready shot list for hand-generating a mixed reel on the web UI |
| `promote_to_seedance.py` | PASS 2 of the mixed dance pipeline — promote approved beats |
| `fetch_and_match.py` | Pull recent Higgsfield generations, match each to its beat by PROMPT |
| `build_videos.sh` | Download + assemble a reel whose clips were generated on the web |
| `reconcile.py` | After culling weak downloads: tidy up + list the redos |
| `recreate.sh` | Rebuild an existing reel's video from its committed definition + assets |

---

## 3. The six skills — `skills/`

### 3.1 `lecture-assets` (lecture stage 1) — chapter → visual pool

Over-generates candidate visuals from a chapter; forces nothing ("breadth now, selection later" — unused assets are inventory, not waste). Output: `lectures/<chapter>/assets/` with `book/`, `svg/` (via cajal), `charts/`, `doodles/`, and `assets.json` (everything tagged `candidate`).

| Script | Function |
|---|---|
| `import_book_figures.py` | Pull the book's already-rendered chapter figures into the pool (pre-vetted) |
| `new_chart.py` | Scaffold a chart in BOTH shapes from one source: `charts/<name>.drawer.js` (live-D3 source of truth) + a synced standalone `.html` |
| `add_asset.py` | Register/upsert any asset in the chapter's `assets.json` pool |

The **drawer contract** is the key design move: one D3 drawing function serves both the standalone preview and the deck (folded into the deck's `data-dc-script` registry — live D3, no iframes).

### 3.2 `slide-deck` (lecture stage 2) — chapter + pool → brutalist `.dc.html` deck

Four phases, one human gate. Nine slide archetypes (`title · section · statement · concept · equation · example · chart · figure · close`) in `templates/archetypes.py`.

| Script | Function |
|---|---|
| `build_plan.py` | Phase 0 — slice chapter into `deck_plan.json`, seed speaker-notes from prose. **THE gate: the notes become the narration** |
| `bind_assets.py` | Phase 1 — match chart/figure slides to pool assets; gap report (advisory) |
| `emit_deck.py` | Phase 2 — plan → `.dc.html` through the archetypes; copies runtime + `_ds`; folds chart drawers; copies figures |
| `verify_deck.py` | Phase 3 — audit: palette (no blue), speaker-notes on every slide, KaTeX validity, chart resolution. Fails loudly |

Regression-tested by re-deriving the Chapter 7 fairness deck and round-tripping it through deck-lecture's extractor.

### 3.3 `deck-lecture` (lecture stage 3) — deck → narrated video

The largest skill: 13 scripts + a full Remotion template. One slide = one beat = one voice-clone MP3 over the live slide, karaoke-captioned. Second law: **discuss, don't read** — narration expands `data-speaker-notes`; a Jaccard-overlap guard flags scripts that recite the slide.

| Script | Function |
|---|---|
| `extract_slides.py` | Phase 0 — deck → `beat_sheet.json` (label, speaker_notes, on_slide_text per slide) |
| `script_guard.py` | Phase 1 — discuss-don't-read guard (token overlap vs. on-slide text) |
| `tts_audit.py` | Phase 1.5 — flag TTS pronunciation risks (rare names, acronyms, symbols) BEFORE spending audio budget |
| `apply_pronunciations.py` | Bake respellings into `tts_normalized_text` only — captions keep correct spelling, only ElevenLabs sees the respelling |
| `align_captions.py` | Phase 3 — forced alignment (faster-whisper supplies timing only; words are known) → karaoke `captions.json` |
| `build_bullets.py` / `preview_bullets.py` | Phase 3.5 — starter bullet specs for text slides (sliding window, max 6 on screen) + SVG snapshot |
| `build_doodle.py` / `preview_doodle.py` | Starter doodle specs (one narration line = one new element) + SVG snapshot |
| `build_sections.py` | Extract title/divider/close slides as native cards (no iframe reload hitch) |
| `preview_tangent.py` | Snapshot an equation tangent (fixed 5-zone template) to SVG |
| `prerender_deck.py` | Screenshot each slide to a still PNG (fallback when live CSS capture is flaky) |
| `scaffold_remotion.py` | Phase 4 — assemble the Remotion project. **Stops at `npm run studio` — never auto-renders** |

Remotion components (`templates/remotion/src/`): `Lecture.tsx` (sequencer; audio-first frame math), `DeckBackground.tsx` (live iframe or prerendered still), `Bullets.tsx`, `Doodle.tsx`, `ProgressiveFigure.tsx` (NEW — reveals an authored SVG's `<g class="pf pf-N">` groups in sync with narration lines; highest visual priority), `EquationTangent.tsx`, `SectionCard.tsx`, `Captions.tsx`, `fonts.ts`, `theme.ts`, `tokens.ts`.

Visual-tier routing per slide: **progressive figure > doodle > bullets > live**, with live D3 charts staying live and short dividers allowed to hold. Rule: no static screen > ~5s while narration runs.

### 3.4 `lyric-match` — re-cut an existing music video to its lyrics

One beat = one lyric line = one source still = one Hailuo image-to-video clip cut to the beat. librosa beat grid is the master clock; faster-whisper forced alignment gives word-level lyric timing.

| Script | Function |
|---|---|
| `extract_frames.sh` | Pull frames from the source video at low fps |
| `pick_stills.py` | Score frames for sharpness; choose one source still per beat |
| `init_beat_sheet.py` | Skeleton `beat_sheet.json` for lyric-match |
| `generate_video_songbird.sh` | Per-beat image→video (copy of the engine script) |

### 3.5 `songbird-dance` — beat-synced dance reels (Seedance 2.0)

Character dances ON the beat: image + audio slice → Higgsfield Seedance 2.0 motion locked to that audio. Key difference from lyric-match: dance beats are long (~10–15s downbeat-aligned, Seedance's cap), and the prompt is mostly CHARACTER + CHOREOGRAPHY + CAMERA. Its 9 scripts (`build_dance_beatsheet.py`, `make_shotlist.py`, `promote_to_seedance.py`, `fetch_and_match.py`, `reconcile.py`, `build_videos.sh`, three storyboard/video shell scripts) are **copies of the engine scripts** — see finding F2.

### 3.6 `skills/shared/`

| Skill | Function |
|---|---|
| `media-router` (`recommend.py`) | First-pass router: which medium (live chart, doodle, bullets, still, video) each beat should get |
| `pacing` (`pace_check.py`) | Audio-first pacing check for a beat sheet — consolidation floors, flags too-short/too-long beats |

---

## 4. The three aspects — `aspects/`

### 4.1 `explainer/bears-doodles` — MinutePhysics-style sketch explainers

The oldest and deepest toolset (16 scripts): `new_video.py` (scaffold), `generate_audio.py` (**the** TTS script the whole repo reuses), `manim_template.py` + `manim_layout_audit.py` + `bn_layout.py` (orientation-aware Manim scene engine), `svg_doodles.py`, `build_intro.py`, `composite_doodles.py` / `composite_clips.py`, `assemble.py` (ffmpeg final cut), `make_short.py` (16:9 → branded 9:16 Short), `enhance_suggest.py`, `retrofit_standalone.py`, `package_video.py` (publish artifacts), `youtube_publish.py` (rolling-schedule uploads), `bn_pipeline.py` (book-ordered batch render + YouTube post-kit).

### 4.2 `explainer/scout` — mine a textbook for video candidates

`scan_book.py` prepares a book for scouting; produces reviewable candidate cards, never videos.

### 4.3 `songbird/muzak` + `muzak-overlay` — music videos

`muzak`: `new_video.py` (scaffold), `analyze_audio.py` (librosa beat/energy grid), `align_lyrics.py` / `align_lyrics_audio.py` (timed lyrics; forced alignment — the technique deck-lecture's captions reuse), `infer_design.py` (design brief from audio features), `media_prompts.py` (chunked t2i/i2v prompts). `muzak-overlay`: `overlay_new.py` — finished video + lyrics → Remotion karaoke overlay (theme ported into deck-lecture).

### 4.4 `bios/mini-bio` — narrated mini-biographies

No scripts of its own — SKILL.md + reference + templates; drives the engine `scripts/` directly. `reels/bio-bose/` is the canonical worked example, rebuildable via `recreate.sh`.

---

## 5. Design system, data contracts, supporting dirs

**`brutalist/`** — `DESIGN.md` (deck + lecture-video visual system: one red `#C8102E`, warm ink `#2a1a0e`, grays, **no blue**; Lato/NU in-deck, Inter overlays, JetBrains Mono strictly for real data) and `EQUATIONS.md` (equation-pedagogy template — the ~40s equation-tangent format).

**Data contracts** (the real API of the system): `beat_sheet.json` (spine: `beat_id`, `label`, `speaker_notes`/`narration_text`, `tts_normalized_text`, `actual_duration_s`, `audio_file`, `visual_mode`, `slide_index`) · `deck_plan.json` · `assets.json` · `figures.json` / `bullets.json` / `doodles.json` / `sections.json` / `tangents.json` · `captions.json` (karaoke schema) · `pronunciations.json` · the `drawer.js` chart contract · `.dc.html` slide format (`<section data-label data-speaker-notes>` + `deck-stage.js`/`support.js`).

**Others:** `presets/` (`cinematic-netflix.json`, `phone-grounded.json` — one knob per look) · `characters/` (little-red-cap) · `fonts/` (6 families, local files) · `reels/` (13 projects; committed definition + git-ignored heavy output) · `lectures/` (Ch.7 fairness — rendered, on YouTube; `07-fairness-regen` — the slide-deck regression) · `examples/` (one starter per aspect) · `docs/` (getting-started, setup, services, open-source-vs-paid, pipeline, references) · `.githooks/` (>50MB commit guard) · `higgsfield.txt` (service notes).

---

## 6. Review — strengths

**S1 — The two laws are real architecture, not slogans.** Audio-as-master-clock and phase-gating are enforced *in code paths*, not just documented: `generate_audio.py` writes measured `actual_duration_s` back to the sheet; `scaffold_remotion.py` derives frame counts from it; every skill stops at a named gate. This is the difference between a pipeline and a pile of scripts.

**S2 — `beat_sheet.json` as the universal spine** is the best decision in the system. It's why a TTS script written for doodle videos drives lecture narration unmodified, and why lyric alignment written for music videos became lecture captions.

**S3 — Human gates sit at the cheapest points.** Plan review before emit; script approval before audio spend; TTS audit before render budget; Studio before render. Cost discipline is designed in, and "never auto-render" is baked into the scaffold itself.

**S4 — Honest engineering culture.** SKILL.mds carry "Build status (honest)" sections that distinguish tested from untested. The live-iframe capture caveat ships with its own fallback (`prerender_deck.py`). Rare in agent-built systems; worth protecting.

**S5 — Separation of TTS-facing text from display text** (`tts_normalized_text` vs `narration_text`) is a subtle, correct design — pronunciation hacks never corrupt captions.

**S6 — Inventory-not-waste asset philosophy** (lecture-assets over-generates, tags everything `candidate`) matches how creative selection actually works.

## 7. Review — findings

**F1 — README is a release behind reality.** It describes only the reels family. Missing entirely: the lecture pipeline (`lecture-assets` → `slide-deck` → `deck-lecture`), `lyric-match`, `songbird-dance`, `brutalist/`, `lectures/`, `recreate.sh`, and it references the old `generate_video_seedance.sh` name. Fixed in this session's README update.

**F2 — Script duplication with confirmed drift (the most serious code issue).** `skills/songbird-dance/scripts/` and `skills/lyric-match/scripts/` contain *copies* of engine scripts, and they have already drifted: `promote_to_seedance.py`, `make_shotlist.py`, and `build_videos.sh` differ from their `scripts/` counterparts, and the skill copy still carries the retired `generate_video_seedance.sh` name. Two sources of truth guarantee a future bug. Fix: make skill copies thin wrappers (or symlinks/docs pointing at `scripts/`), or delete them and have SKILL.md reference the engine paths.

**F3 — Personal voice ID committed despite the scrub.** Commit `4643c16` says "scrub personal IDs," but ElevenLabs voice `TyW6NH39JcFb5M3xdIIk` is hardcoded in root `SKILL.md`, `skills/deck-lecture/SKILL.md`, `skills/deck-lecture/scripts/extract_slides.py`, and `skills/slide-deck/scripts/build_plan.py`. A voice ID isn't an API key — it's unusable without your ElevenLabs account — but it's inconsistent with the repo's own stated policy. Move the default to `.env` / `metadata.voice_id` and reference it symbolically.

**F4 — The repo violates its own naming law.** Kebab-case-no-spaces is a stated non-negotiable, yet `lectures/fairness-metrics-and-impossible-choices/Chapter 7 - Fairness Metrics.dc.html` and `lectures/07-fairness-regen/Chapter 07 - Fairness Metrics.dc.html` remain, and the root SKILL.md worked example quotes the spaced path. Known mistake per SESSION-RESUME, but it's still teaching every new agent session the wrong pattern via the worked example.

**F5 — Known path bug left standing.** `prerender_deck.py` and `scaffold_remotion.py` resolve `--deck` relative to CWD, not the folder argument — documented as having "bit me twice." A three-line `os.path.abspath` normalization ends it; documenting a footgun is not fixing it.

**F6 — Verification debt.** Declared untested: ProgressiveFigure under real render, faster-whisper on a fresh install, live CSS-capture per deck, Seedance beat-match verification. Ch.1 Studio review (in progress) covers the first. The pattern to watch: new tiers keep being added faster than old ones get render-verified.

**F7 — Housekeeping.** `generate_startend_storyboard.sh.bak` committed in `scripts/`; `__pycache__` dirs present in `skills/*/scripts/`; large uncommitted surface (the entire lecture pipeline — `skills/{lecture-assets,slide-deck}`, `PIPELINE.md`, `SESSION-RESUME.md`, `ProgressiveFigure.tsx` — exists only as untracked files). A crash or careless clean loses the newest, least-reproducible work. Commit it.

**F8 — Skill granularity is uneven.** `skills/` mixes three-stage pipelines (lecture), single-purpose tools (lyric-match), and near-duplicates of `aspects/` content (songbird-dance vs `aspects/songbird`). A newcomer can't tell what's an aspect vs a skill vs an engine. The AGENTS.md contract mostly papers over this, but the taxonomy deserves one clarifying paragraph in the README (added) and eventually a consolidation.

## 8. Recommended order of attack

1. Commit the untracked lecture pipeline (F7) — highest data-loss risk, zero effort.
2. De-duplicate skill script copies (F2) — the only finding that will silently corrupt future output.
3. Fix the `--deck` path resolution (F5) — trivial, already bit twice.
4. Rename the two spaced lecture filenames + update the SKILL.md worked example (F4).
5. Parameterize the voice ID (F3).
6. Delete `.bak` / pycache; add `__pycache__` to .gitignore if absent (F7).
7. Keep burning down verification debt at each Studio gate (F6).

None of these are architectural. The architecture — one spine, two laws, gates at the cheap points — is sound and is already proving itself by how much each new pipeline reuses the last one.
