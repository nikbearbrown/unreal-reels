# Silent Mode — batch rough-draft lectures for 150 books

*Design proposal, 2026-07-01. Context: AICR HPC access (248 B200 + 152 RTX Pro GPUs), 150 books, target = a watchable rough draft of every chapter, refined later on the Mac with Opus/Fable.*

---

## Verdict

Doable, and the architecture is already 80% right for it: audio-as-master-clock means timing is *derived*, not authored, so anything silent mode gets wrong can be swapped later and the pipeline mechanically re-times itself. But two assumptions in the ask are wrong, and the design below corrects them.

**Pushback 1 — your bottleneck is not rendering, it's your attention.** 150 books × ~12 chapters ≈ 1,800 videos ≈ 300 hours of footage. At 2× speed that's 150 hours of watching — a month of full-time work just to *review* the rough drafts. So silent mode's primary deliverable is not the videos; it's the **triage layer**: per-chapter QC scores, contact sheets, decision logs, and 60-second preview reels, ranked worst-first, so you watch full renders only where the machine says something's off or the book matters most. Rough drafts without triage is a warehouse you'll never open.

**Pushback 2 — "silent" doesn't mean removing the gates; it means moving them.** The gates exist because they sit at the cheapest fix points. In silent mode every gate becomes an *auto-decision + logged justification*: the plan gate auto-accepts and logs the plan; the script gate auto-rewrites over-threshold beats and logs the overlap score; the render gate becomes an automated QC audit on the finished mp4. Your review then happens asynchronously against the decision log — which is exactly the "changes only I and Opus/Fable can make" workflow you described. Gate-deferred, not gate-free.

---

## What batches and what doesn't

| Stage | Needs | Silent-batchable? |
|---|---|---|
| Chapter → deck plan, narration scripts, bullets, doodle specs | LLM | Yes — Claude API (see cost note) |
| SVG figures, D3 charts (lecture-assets/cajal) | LLM + templates | Yes |
| TTS narration | ElevenLabs *or* local clone | Yes — **local for drafts** (see below) |
| Forced alignment (faster-whisper) | GPU | Yes — ideal cluster work |
| Deck emit + verify | CPU | Yes |
| Remotion render | CPU + headless Chromium | Yes — the big parallelism win |
| Manim (bears-doodles) | CPU | Yes |
| Mini-bio storyboards/video (Higgsfield, Seedance, Hailuo) | Paid external APIs + curation | **No** — keep gated |

The decisive fact: **the lecture pipeline needs zero image-generation services.** Deck + SVG + D3 + TTS + Remotion, end to end. That's why lectures are the silent-mode v1. Mini-bios burn real Higgsfield money per attempt and their whole quality model is "pick the keeper" — batch them silent and you pay for stills nobody curated. Bios stay interactive (or get a placeholder-still draft mode later).

## The TTS decision (the one real architecture question)

1,800 chapters × ~10 min ≈ 18,000 minutes of narration. Through ElevenLabs that is serious money for *drafts you expect to change*. Instead:

- **Drafts:** open voice clone (F5-TTS / XTTS-class) on the RTX Pro nodes, cloned from your existing ElevenLabs reference audio. Marginal cost ≈ zero, quality = fine for "is this chapter right?"
- **Finals:** on approved chapters only, regenerate the changed beats through ElevenLabs.

This works *because* of the master-clock law: swap the audio, and captions, slide holds, and frame counts all re-derive from the new measured durations. Draft audio ≠ final audio is a re-run, not a re-edit. The refactor must make that re-run one command per chapter.

Do **not** move script drafting to an open model on the B200s to save API dollars. Weak narration is the single thing that costs the most *of your time* at refinement. Claude API for all prose; the cluster for alignment, TTS, and render. Spend GPU on what's parallel, spend model quality on what you'll read.

## Refactor plan (ordered)

**0. Pay the debts first — batch multiplies every footgun by 1,800.**
The F2 script drift, the F5 CWD-relative `--deck` bug, spaced filenames, and the uncommitted lecture pipeline all become 1,800-fold bugs in silent mode. Fix before anything else. (See SYSTEM-REVIEW.md §8.)

**1. `silent_run.py` — one orchestrator, one chapter, no prompts.**
`silent_run.py <book> --chapter NN` runs lecture-assets → slide-deck → deck-lecture with every gate on auto-policy, and emits into the chapter folder:

- `decision_log.json` — what each former gate decided and why (plan slices, asset bindings + gap report, overlap scores + rewrites, TTS respellings applied, tier routing per slide)
- `qc_report.json` — verify_deck + pace_check + caption coverage + post-render probes (black-frame scan, silence scan, duration sanity, first/last-frame checks) → **one 0–100 QC score**
- `contact-sheet.jpg` — one thumbnail per slide
- `preview.mp4` — ~60s: title + 3 lowest-confidence beats + close
- `rough.mp4` — the full draft render

Auto-policies are mostly already written: `media-router/recommend.py` *is* the silent tier-router; `build_bullets.py`/`build_doodle.py` starters become the draft visuals instead of hand-authored ones; `tts_audit.py`'s suggested respellings get auto-applied at HIGH confidence. Silent mode is largely promoting existing "starter" tools to "default."

**2. `batch_run.py` — the fleet.**
Walks `books/*/chapters/*.md`, one Slurm array task per chapter (chapters are embarrassingly parallel), content-hash caching so a re-run touches only changed units — the repo's "regenerate only the failing unit" law, applied at fleet scale. Emits `fleet_manifest.json`: every chapter × status × QC score × paths. This is your triage dashboard.

**3. Portability contract.**
Chapter folders are already self-contained; harden that: everything the Mac needs to refine (beat_sheet, decision log, deck, assets, mp3s, remotion scaffold) lives in the folder; everything regenerable is manifest-listed. `pull_chapter.sh <book> <NN>` rsyncs one chapter down; you open it with Fable/Opus, make the surgical changes (rewrite beats S05+S09, re-voice with ElevenLabs, re-scaffold, Studio, render), push the final back.

**4. Cluster packaging.**
HPC nodes are hostile to Node + headless Chromium — build one **Apptainer image** (Python + node18 + Chromium + ffmpeg + faster-whisper + F5-TTS + fonts) and run everything in it. Check AICR's egress policy early: Claude API + (final-pass) ElevenLabs calls need outbound HTTPS from compute nodes, or the LLM/TTS phases run on a login node / your Mac and only align+render run on compute. Storage: 1,800 × (mp3s + stills + mp4) is a few TB — confirm quota. Note the render fleet wants CPU + RTX Pro nodes; the B200s are irrelevant to this workload (worth saying honestly in the AICR proposal — or pairing the proposal with a genuine model-inference use case).

**5. Pilot before fleet — non-negotiable.**
One book, ~12 chapters, fully silent, end to end. Measure: QC pass rate, your minutes-per-chapter at review, and which decision types you override most. Every frequent override becomes a better auto-policy *before* you spend 1,800 chapters learning the same lesson. Expect the pilot to reveal that ~3 of the auto-policies are bad; that's the point of the pilot.

## The review loop (the part that's actually new)

```
CLUSTER (silent)                          MAC (you + Opus/Fable)
batch_run → 1,800 chapter folders         open fleet dashboard, sort by QC ascending
  each: rough.mp4 + preview.mp4 +   ──▶   watch previews, spot-check roughs
  contact sheet + decision_log + QC       write notes.md per chapter (or dictate)
                                          pull_chapter → surgical regen with Fable:
                                            fix beats → ElevenLabs finals → Studio → render
                                          push final back / publish
```

Review discipline that makes 150 books survivable: triage on **contact sheet + decision log first** (seconds), preview.mp4 second (a minute), rough.mp4 only for flagged or flagship chapters. Rank books by importance and QC score; accept that the long tail ships as rough-plus-spot-fixes.

## What I'd explicitly not do

- Don't silent-mode mini-bios in v1 (paid APIs + curation-centric quality).
- Don't hand narration drafting to a local model to save pennies that cost you hours.
- Don't render 4K/final-quality drafts — 720p rough renders halve the fleet cost and are fully watchable for review.
- Don't skip the pilot. The system has never run unattended once; 1,800 unattended runs is not the place to find out which gate mattered.

## Can AICR run open FLUX + LLM models locally? (replacing the paid APIs)

Yes — comfortably, to the point of overkill. The cluster is 248 NVIDIA B200 (192 GB HBM3e
each) + 152 "RTX Pro" (almost certainly RTX PRO 6000 Blackwell, ~96 GB GDDR7 — confirm in
AICR docs). Every paid service in the pipeline has an open-source equivalent that fits
these GPUs with room to spare:

| Pipeline need | Paid today | Open model on AICR | Footprint (bf16) | Fits? |
|---|---|---|---|---|
| Storyboard stills | FAL FLUX | FLUX.1-dev / -schnell (12B) | ~24 GB | 1 GPU, batch many |
| Draft narration | ElevenLabs | F5-TTS / XTTS-v2 / Kokoro | <2 GB | trivial |
| Plan + narration authoring | Claude | Llama-3.3-70B, Qwen2.5-72B | ~140 GB | 1 B200, or 2 RTX Pro |
| " (frontier-ish) | Claude | DeepSeek-V3 (671B MoE) | ~1.3 TB | multi-node, doable |
| Image→video (reels/bios drafts) | Higgsfield/Seedance | Wan2.1, HunyuanVideo, LTX-Video | fits 1–2 GPUs | yes |

Serve LLMs with vLLM or TGI; FLUX via diffusers; all inside the Apptainer image. The
natural split: **RTX Pro nodes = the FLUX + TTS + Remotion render fleet** (many small
parallel jobs), **B200 nodes = local LLM inference** for the authoring gates (big memory,
tensor-parallel). This makes the B200s directly relevant to *our* workload after all —
they become the free replacement for the Claude Batch API in the fleet-LLM fork.

**The economics this unlocks:** for a 150-volunteer nonprofit, the cluster can drive the
entire *draft* pass — stills, voice, authoring, even draft video — at zero marginal API
cost. That is the real prize of AICR access.

**The one caveat, and it's the same one as before:** open-weight LLM narration is
meaningfully weaker than Claude/Fable at exactly the gate where quality buys the most
refinement time (the authoring). Recommended split — **open models for everything visual
and for TTS drafts; Claude/Fable (or a top open model, A/B-tested) for the plan +
narration authoring.** Don't let "it's free on the cluster" quietly downgrade the one
input that determines how much the 150 volunteers have to fix by hand. Prove the local-LLM
authoring against a Claude baseline on the pilot chapters before committing the fleet to it.

## Effort estimate

Debts (step 0): a day. `silent_run` + auto-policies: 2–3 sessions (most pieces exist as starters). Batch/Slurm + Apptainer: 1–2 sessions, plus whatever AICR onboarding costs. Local-TTS draft voice: 1 session to stand up and A/B against the clone. Pilot book: one overnight run. Fleet: bounded by cluster queue, not by code.
