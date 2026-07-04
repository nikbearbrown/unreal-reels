---
name: brownblue-convert
description: >
  Audit a doodle-style explainer folder against the Brown Blue depth standard
  and, when it falls short, rewrite it into a deeper `-bb` version. Doodles are
  ~1-minute MinutePhysics sketches (hook → accumulation → reveal, doodle+manim,
  Shadows Into Light, white canvas); Brown Blue is a 3–8 minute pure-Manim 3b1b
  explainer (concrete-before-abstract, ≥2 moving instances per abstraction,
  equation tangents, EB Garamond, blue+brown). Use when the user types
  `bb-convert`, `convert`, `bb-audit`, `audit`, or asks to convert a doodle to
  Brown Blue, audit whether a video is brownblue-depth, deepen a 1-minute video,
  or produce a `-bb` version. Audits with `scripts/audit.py`; converts through
  the brownblue `script` → `beats` flow. Phase-gated. Never publishes.
---

# Brown Blue Convert — doodle → deep Brown Blue

## SILENT MODE — THE CONTRACT (read first, do not re-litigate)

This is written down because it keeps getting re-asked. Honor it exactly:

1. **The human runs at most TWO commands per concept, ever.**
   `python scripts/silent_run.py <folder>` renders EVERYTHING (audio, 16:9,
   9:16, karaoke captions, transcript, YouTube description). Then, only after he
   has watched the masters, `python scripts/silent_publish.py <folder>` uploads
   every surface private with captions + playlists. That is the whole interface.
   Never hand him a "bazillion" step-by-step commands, per-stage invocations, or
   manual copy-paste chains.
2. **The keys live in the human's environment — this is NOT a blocker.**
   `ELEVENLABS_API_KEY` is in his shell; the YouTube OAuth tokens
   (`youtube_token.json`, `client_secret.json`, ledger) are in `Manim/`. The
   agent's sandbox does not have them and never will. Do NOT report "I can't
   render because no key," do NOT ask about keys, do NOT re-investigate the
   environment each session. Rendering and publishing happen on HIS machine when
   he runs the two commands — that is by design.
3. **"Convert" is not done until the folder is RENDER-READY.** A `-bb` conversion
   MUST include: the deep `beat_sheet.json`, the authored Manim **scene `.py`**
   (one draw per bespoke beat, `bn_layout` for both aspects) + a `bn_layout.py`
   copy in the folder, and the playlist routing metadata (`playlist` for 16:9,
   `playlist_short` for the 9:16). Verify with `silent_run.py <folder> --dry-run`
   (no keys needed). Authoring the scene is part of the job — never leave it as a
   TODO or ask the human to run the `manim` step himself.
4. **Playlist routing is fixed:** `metadata.playlist: "Quantum Mechanics"` (16:9),
   `metadata.playlist_short: "Shorts"` (9:16). Set it during conversion.
5. The agent never renders or publishes. It makes the folder ready and states the
   ONE command to run. If `silent_run` errors on his machine, he pastes the error
   block back and the agent fixes that one thing — that is the only loop.

# Brown Blue Convert — doodle → deep Brown Blue

You take an existing **doodle** video folder (a ~1-minute Bear's-Doodles sketch)
and either **certify** it is already Brown Blue depth or **rewrite** it into a
`-bb` version that is. You do not invent concepts — the concept already exists in
the doodle; your job is to give it the depth, arc, and register Brown Blue
requires.

This skill is a thin front-end on **brownblue** (`../brownblue/`). It adds the
*audit* (is this already deep enough?) and the *lift* (doodle → deep script);
everything downstream — beats, audio, manim, assemble — is brownblue's, unchanged.

## Read before acting

- `../brownblue/reference/pedagogy.md` — the 3b1b arc and Gate-1/Gate-2 rules the
  rewrite must satisfy. **Read before every convert.**
- `../brownblue/reference/style.md` — palette, fonts, motion, intro/outro.
- `../brownblue/reference/equations.md` — the equation-tangent rule; every
  equation the deep version lands fires a tangent.
- `scripts/audit.py` — the runnable scorecard this skill is built around.

## What "Brown Blue depth" means (the audit rubric)

`scripts/audit.py <folder>` scores a `beat_sheet.json` (and `script.md` if
present) against these. Checks marked **[critical]** decide the verdict; the rest
are warnings that shape the rewrite.

| # | Check | Doodle typically | Brown Blue |
|---|---|---|---|
| 1 | **[critical]** No `render: doodle` beat — pure Manim | mixes doodle+manim | manim only |
| 2 | **[critical]** Duration ≥ ~120s (derive tier, pedagogy §5) | ~60–100s | 2–8 min |
| 3 | **[critical]** ≥2 moving `INSTANCE` beats before each `ABSTRACTION` | hook→reveal, 0–1 instance | ≥2 |
| 4 | **[critical]** Every landed equation has a `TANGENT` bracket | none | equations.md |
| 5 | **[critical]** No lecture red anywhere (`forbidden_color` = `#C8102E`) | uses `#C0392B` etc. | none |
| 6 | Brand metadata: `series: Brown Blue`, `style` dark/light, `text_font: EB Garamond`, blue `accent_color` | Bears Notes / Shadows Into Light | set |
| 7 | Slug ends `-bb` | plain slug | `-bb` |
| 8 | Beat roles present (HOOK/INSTANCE/TRANSFORM/ABSTRACTION/PAYOFF/BOUNDARY) | INTRO/H/A ad hoc | tagged |
| 9 | Mystery-framed opener, definitions as endpoints | often utility/label-first | required |
| 10 | BOUNDARY beat: not-taught + one viewer exercise | absent | required |

**Verdict:** `PASS` (already Brown Blue depth) only if every **[critical]**
check passes. Otherwise `NEEDS-BB-CONVERSION`, with the failing checks listed —
those become the rewrite's punch list.

## Commands

Respond to the first word (`bb-convert`, `convert`, `bb-audit`, `audit`).

### `audit <folder | book/youtube>` — score without changing anything
Run `python3 scripts/audit.py <path>`. For a directory of folders, audit each
and print the scorecard table + verdict per folder. Report which are already
deep and which need conversion; change nothing. This is the "test on the repos"
entry.

### `convert <doodle-folder>` — rewrite one doodle into `-bb`
1. **Audit first.** Run the audit. If it already `PASS`es, say so and stop —
   don't rewrite a video that's already deep.
2. **Lift the concept, not the script.** Read the doodle's `script.md` +
   `beat_sheet.json` and its `metadata.source` chapter. Extract: the ONE
   insight, the concrete case/hook, the exact objects, and any equation. Discard
   the doodle's pacing and register — you keep *what it teaches*, not *how it
   sketched it*.
3. **Re-scope to a single insight** (pedagogy §1) and **run the length
   procedure** (§5): a doodle's one idea, given ≥2 moving instances, a real
   TRANSFORM, the abstraction as an endpoint, a PAYOFF that returns to the hook,
   and any equation tangents, lands in the 2–4 min *single-insight* tier — the
   depth comes from instances and the tangent, never from padding.
4. **Write the deep `script.md`** through brownblue's `script` command
   (mystery opener, discovery voice, ≥2 instances/abstraction, equation
   tangents from equations.md, BOUNDARY beat). Show the Gate-1 audit table.
   **Stop for approval (Gate 1).**
5. **Target folder = `<same-book>/youtube/<slug>-bb/`.** If the source folder is
   the plain slug, create the `-bb` sibling; never overwrite the doodle (the
   HANDOFF rule: `-bb` *supersedes* the doodle, it doesn't delete it). `new` via
   brownblue with brownblue metadata (series, EB Garamond, dark, blue accent,
   red as `forbidden_color`).
6. **Beats → audio → manim → assemble** are brownblue's, unchanged. Hand off to
   the **brownblue** skill from `beats` onward; re-run `audit.py` on the result
   and confirm it now `PASS`es before showing a render.

### `convert-all <book/youtube>` — batch, one at a time, gated
Audit the directory, list every `NEEDS-BB-CONVERSION` folder, and convert them
**one at a time**, pausing at each Gate 1 for approval. Never emit 20 finished
scripts in one shot — depth is authored per concept, and a batch that skips the
gate produces 20 shallow rewrites, the exact failure this skill exists to catch.
Report progress against the audit punch list.

## What NOT to do
- Never overwrite or delete the source doodle — the `-bb` version is a sibling.
- Never "convert" a video that already passes the audit.
- Never reach Brown Blue length by padding (pedagogy §5 prohibition) — depth is
  instances + tangent, not filler beats.
- Never carry the doodle's Shadows-Into-Light / red / doodle-render into `-bb`.
- Never skip the equation tangent on an equation the deep version lands.
- Never publish — that's the book `youtube/` pipeline, run by the human.
