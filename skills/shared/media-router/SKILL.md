---
name: media-router
description: >
  Recommends the best visual medium for every beat of a narrated educational
  explainer — Manim (programmatic vector animation), Remotion (compositional
  motion graphics), text-to-image (Illustrae/Midjourney/Nano Banana), or
  text-to-video (Higgsfield/Runway/Sora/Kling) — to MAXIMIZE learning outcomes,
  not polish. Use when the user types `route`, `recommend media`, `which medium`,
  `pick renderer`, `media router`, or asks what tool a beat should use, or hands
  over a beat sheet / storyboard for per-beat media selection. Reads a beat sheet,
  classifies each beat, writes a recommended `render` with a confidence and reason,
  runs the red-flag checks, and leaves a one-field human override. Evidence-grounded
  (CTML + Cognitive Load Theory); recommends the best default, never the
  easiest-to-produce.
---

# Media Router — best medium per beat

You decide, per beat, which of four media gives the best **learning outcome**, then
write that choice into the beat record as a *default the human can override*. You are
the renderer-selection layer of the pipeline: scout/expert proposes the video →
narration-first storyboard → **you route each beat** → the right renderer builds it →
ffmpeg composites + adds sound.

This skill is about *learning*, not production mechanics. (For how a Manim or doodle
beat is actually produced, see the bears-doodles `whiteboard/reference/routing.md`.)

## The one principle that governs everything

**Engagement and polish are not learning.** The independent evidence is blunt about
this: animated vs. talking-head video is a statistical *null*; learners reliably
"like it but don't learn from it"; slick math animation produces an *illusion of
understanding* (high ratings, overestimated comprehension). The single most impressive
medium for a beat — cinematic generative video, glossy motion — is the one most likely
to buy ratings without learning. **Your job is to resist "what looks good" and pick
what the evidence supports.** Recommend the best medium; let the human override only
with a stated design reason.

## How to route a beat

1. **Read the beat's `content_type`** — it should already be set at storyboard time
   (see `whiteboard/reference/storyboard.md`), which makes routing deterministic. The
   canonical machine values are: `mechanism`, `equation`, `structure`, `geometric`
   (abstract structures → Manim), `data`, `realworld`, `title`. Only if `content_type`
   is missing, infer it from the narration / `visual_key` (the script does this as a
   keyword fallback, defaulting safe when unsure).
2. **Look up the default** for that type in `reference/decision-table.md`. That table
   carries the rationale, the corrected effect sizes, the fallbacks, and the override
   conditions. Read it before routing — do not route from memory.
3. **Write the recommendation** into the beat: `render` (the suggested medium),
   `render_confidence` (high / moderate / low), and `render_reason` (one line, citing
   the principle — e.g. "schematic line-art, control + accuracy; ties static, dodges
   seductive detail"). Never overwrite an existing human `render_override`.
4. **Run the red-flag checks** (below) against the beat. A red flag is a *block*, not a
   suggestion — surface it.
5. If `content_type` is missing and you can't classify confidently, **apply the global
   fallback** (below) — don't guess a fancy medium.

The script `scripts/recommend.py` does steps 1–4 as a deterministic first pass; you
refine its output with judgment the keywords can't capture.

## The defaults (what the system auto-picks)

| Beat type | Default medium | Confidence |
|---|---|---|
| Process / mechanism | **Manim** (schematic, one element per spoken idea) | Moderate |
| Equation / quantitative relationship | **Manim** (LaTeX, worked-example build) | High |
| Static labeled structure / diagram | **Remotion** compositing a *vetted* illustration | Moderate |
| Data / quantities | **Remotion** (Manim for analytic curves) | High |
| Real-world / human context | **Text-to-image** (Ken-Burns in Remotion); T2V only if motion *is* the content | Low–Moderate |
| Definitional / title / typographic | **Remotion** (key term only, no narration duplication) | High |

**Why Manim is the mechanism default — state it honestly.** The animation literature
does *not* say animation beats well-designed static graphics for understanding a
process (overall d ≈ 0.23–0.37; animation only reliably wins when the *features of
change* — direction, speed, trajectory — are themselves the thing to learn). Manim is
the default because it is **schematic, pixel-precise, and fully controllable**: it
can't hallucinate a structure, it nails signaling + temporal contiguity, and it makes
"one new element per spoken idea" cheap — and it at least *ties* static while avoiding
the seductive-detail and AI-accuracy traps. It is not the default because animation
"teaches better." Its honest fallback: **a 2–3-state mechanism is evidence-equivalent
as a sequence of static frames in Remotion** — and cheaper. Route there when the
mechanism is simple or mostly about labeled anatomy.

## Global fallback

If a beat has no usable content type, default to **Remotion displaying a static
schematic diagram with focused typographic labels.** It is the lowest-risk choice
across learners and subjects: information permanence (no transient-information cost),
self-paced label↔structure saccades, minimal seductive detail. Never fall back to a
generative-video or photoreal default.

## Red flags — these BLOCK a beat, regardless of type

1. **On-screen text that duplicates the narration** (redundancy effect). Strip it to a
   ≤3-word label, or remove it. *Not the same as the accessibility caption track:* a
   toggleable player-caption VTT (learner-controlled, off by default) is fine and even
   helps non-native speakers; the violation is **verbatim text baked into the frame**
   alongside the same spoken words.
2. **Text-to-video or text-to-image for invisible / molecular / precise content.**
   Generative media confabulate structure that *looks* authoritative and seeds false
   schemas. No T2V/T2I for any mechanism, equation, or microscale structure.
3. **AI-generated stills for scientific structures, with a non-expert author.** AI
   image models distort anatomy badly (gross inaccuracies are the norm, not the
   exception), and a non-expert *cannot vet them*. Structural bio/anatomy beats need an
   expert-reviewed illustration or a built-to-spec schematic — not non-expert
   generation. Treat "vetted T2I" as requiring real vetting.
4. **Decorative photoreal as atmosphere** (seductive detail). Cinematic b-roll behind a
   concept primes the wrong schema and depletes the visual channel. Cut any realism
   that isn't itself the thing being learned.
5. **Gratuitous / racing animation.** Multiple elements moving at once, or a build that
   outruns the narration, violates the apprehension principle and dumps transient load.
   Enforce: one new element per spoken idea, synced to the voice — not to visual rhythm.

## Overrides — capture the reason

The recommendation is a default. The human may override by setting `render_override`
plus `render_override_reason`, tagged either:

- **`design`** — a positive judgment ("static reads better here; this equation is a
  label, not a derivation"). The good kind.
- **`constraint`** — a downgrade because of capacity ("no one to build the Manim beat").
  This should be near-extinct now that agents build renderers on demand; a pile of
  `constraint` overrides is a staffing signal, not a design choice — surface it.

Never let an author's tool fluency silently set the default. The default is the best
medium; deviations are reasoned and logged.

## Boundary conditions (shift the default when these hold)

- **Novice in the subfield** → favor the high-scaffolding default (Manim step-build,
  segmented, integrated labels). Real-world context beats earn their place as anchors.
- **Near-expert in the specific subfield** → expertise reversal: scaffolding and slow
  builds become redundant load. Prefer a static or quickly-revealed overview; drop the
  derivation. (Caveat: do not over-apply — segmenting does *not* cleanly reverse for
  experts.)
- **High element-interactivity content** (metabolic pathways, multi-step derivations) →
  intrinsic load is already high; split into sub-beats and reveal sequentially. Never
  animate the whole system at once.
- **Low element-interactivity** (single fact/definition) → the cheapest clear medium is
  fine; Manim's overhead buys little.

## Read before acting

- `reference/decision-table.md` — the full evidence-grounded matrix: per-type rationale,
  *independent* (not Mayer-in-house) effect sizes, fallbacks, and confidence/contested
  flags. **Read first, every routing pass.**
- `scripts/recommend.py` — deterministic first-pass router over a `beat_sheet.json`.

## Note on installing this as a triggerable skill

This is an in-repo project skill (same shape as `tools/skills/whiteboard` and
`tools/skills/scout`) — agents and the pipeline use it by reading this file and running
the script. To make it an *auto-triggering* Cowork skill (so it fires on "route this
beat sheet" without being pointed at), package `tools/skills/media-router/` into a
plugin and install it via Settings → Capabilities; the SKILL.md here is the core.
