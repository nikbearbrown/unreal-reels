---
name: voxlit
description: >
  Vox-style films of spoken-word performances of literature — the vox-explainer
  chassis (newsprint treatment, two-axis shots, slot contract, Manim fragments,
  Remotion annotation plane) applied to a RECITATION of a public-domain literary
  work. The performance is the master clock; the visual plane teaches the work's
  history and allusions WHILE the listener hears the work itself — marginalia
  that moves, never a competing lecture. New machinery: the recitation clock
  (forced alignment of a known text), the beat.role axis
  (illustrate | teach | breathe), the four margin laws, the scholarship gate,
  and karaoke-as-CC (words are a synced caption track the viewer turns on,
  never a second cut). Use when the user types `voxlit`, `vox poem`,
  `vox spoken word`, or asks for a Vox-style film of a poem, reading, or
  literary performance. Audio-first, phase-gated.
metadata:
  tags: vox, literature, poetry, spoken-word, marginalia, karaoke, captions, recitation, phase-gated
---

# voxlit — Vox marginalia for spoken-word literature

Sibling of vox-explainer (same chassis — treatment, tokens, two-axis shots,
slot contract, compile scripts, outro law all INHERIT; do not re-decide).
The genre lineage is illuminated marginalia / the Norton Critical Edition /
Pop-Up Video: teach the work while the work plays. The lineage also names the
failure mode — chattering over the text. The margin laws exist to prevent it.

## The premise and its one tension

Two texts, one language channel. A vox explainer may talk and label at once
because narration and plane are one argument by one author. Here the ears
are full of the poem; anything the plane SAYS competes with it. Everything
below follows from that.

## Clock mode: recitation

The performance (spoken word over a music bed, or a bare reading) is the
master clock. The text is KNOWN, so forced alignment is near-perfect:
`_align.py` (faster-whisper, runs on the Mac) matches the transcript to the
source lines → `align/words.json` (word times) + `align/lines.json` (line
times + the BREATH MAP: every inter-line gap ≥ ~350ms). Beats are line
groups cut at breaths. **GATE 0: alignment lock** — scrub five spot-checks
before anything keys to it. Until words.json exists, builders may use a
uniform-line first pass (snapped to the music bar grid if there is a bed)
but must label every word-timed feature UNTRUSTED.

## The role axis (third axis, locked at plan gate)

`beat.role: illustrate | teach | breathe` — orthogonal to shot type/source.

- **illustrate** — the plate stages the line. Meaning is taught by
  JUXTAPOSITION: the edit argues, silently. (The fog gets drawn as a cat;
  no chip says "the fog is a cat.")
- **teach** — the margin cites something checkable. Kinds:
  ALLUSION (what the line quotes: "MARVELL, 1681" · "JOHN 11" ·
  "MATTHEW 14" · "TWELFTH NIGHT, I.i"), PROVENANCE (the first-printing scan
  on screen while its lines are read; author's age; who published it),
  GLOSS (one dated word: "ETHER: 1846"), STRUCTURE (refrain tally),
  ADAPTATION MARKER (the chip that says where the performance's text leaves
  the source — mandatory when the performance adapts).
- **breathe** — nothing teaches, nothing labels. Bare card or clean plate.

## THE FOUR MARGIN LAWS (lint-enforced, violations block the plan gate)

1. **Chips land in the breaths.** Every chip's in-point is a line-end gap
   from the breath map — never mid-line. (First pass: line-end estimate,
   flagged UNTRUSTED until alignment.)
2. **≤5 words per chip, or non-verbal.** Portrait+dates beats prose.
   EXEMPTION: words currently in the ear — a card or chip may quote the
   line being spoken at any length (that is signaling, not competition).
3. **The margin goes silent on the peaks.** The work's most charged lines
   are declared at plan time (`metadata.peak_lines`); those beats must be
   role=breathe. No chip ever shares the frame with a peak.
4. **Teach cap: ≤ 1/3 of beats**, and no two consecutive teach beats.
   Viewers came for the poem.

## The scholarship gate (replaces factcheck)

Every teach chip is a footnote and gets a source line in `FACTCHECK.md`
(edition, verse, museum accession, biography page). A wrong marginal note in
a literature film teaches confidently and falsely — worse than a wrong
number in an explainer. Interpretation is NEVER chipped; it lives in the
edit (which plate, which cut). If a chip can't be cited, it's either cut or
it's an illustrate beat.

## Karaoke = closed captions, never a second cut

ONE master. The words ride as a synced caption track cut at the source's
own line breaks (`<slug>.srt` from `align/lines.json` — verse lines, not
transcription paraphrase), uploaded as the official CC track; viewers who
want the words turn them on. Optional word-timed karaoke highlight is a
Remotion overlay variant (`vox_karaoke.py`) rendered ONLY on request — same
assembly, burn-in flag, still not a re-edit. Teaching chips and CC coexist
because CC is viewer-opted and screen-bottom; chips stay out of the lower
third for exactly this reason.

## What Prufrock fixes as the fixture

`reels/vox-prufrock/` — 8:45 spoken-word performance of Eliot's 1915 poem
with a country-register adapted ending (the ADAPTATION MARKER's reason to
exist), allusion-dense (Marvell, Lazarus, Salome, Hesiod, Hamlet,
Twelfth Night), first printing scannable (Poetry, June 1915). Exercises
every teach kind, all four laws, the recitation clock, and karaoke-as-CC.

## Workflow (each gate is the user's)

1. `plan` — lines → beats at breaths; shot type × source × ROLE; peak lines
   declared; chips authored under the laws; margin lint runs →
   `SHOTLIST.md`. **GATE: approve the plan (lint must be clean).**
2. `scholarship` — every chip sourced in FACTCHECK.md. **GATE: citations hold.**
3. `align` — `python3 reels/<slug>/_align.py` on the Mac → words.json,
   lines.json, breath map; builder re-snaps; word-timed features flip to
   TRUSTED; CC srt regenerates from lines.json. **GATE 0: alignment lock.**
4. `run` — inherited vox_run/vox_compile machine pass; slates in unfilled
   slots; master audio muxed. **GATE: watch the cut.**
5. `stills` / `video` / `assemble` — inherited unchanged (FLUX plates,
   archive downloads + sidecars, Higgsfield i2v where motion earns it,
   Remotion annotation plane keyed to words.json). CC srt ships alongside;
   karaoke burn-in only on request.
