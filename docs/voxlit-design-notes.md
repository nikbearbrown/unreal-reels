# voxlit — the spoken-word / literature extension of Vox

Design notes, pre-build. The proposal: your performance of a PD literary work
is the master clock; the visual plane teaches the work's history and meaning
while the listener hears the work itself. Karaoke derivative for those who
want the words.

## Why this works

The laundering function was built for exactly this. A film about a 1915 poem
wants manuscripts, Poetry magazine scans, Rembrandt etchings, Hamlet
playbills, fog footage — sources that never match. One newsprint treatment
makes them one film. And the genre has a real lineage worth naming:
illuminated marginalia, the Norton Critical Edition, Pop-Up Video, Genius
annotations. voxlit is marginalia that moves. Naming the lineage keeps the
design honest — we know what those forms do well (cite, gloss, delight) and
where they die (chattering over the text).

Technically, spoken word is the *best possible case* for the pipeline: a
known text read by one voice means faster-whisper forced alignment is
near-perfect. Word-timed annotation stops being aspirational (the current
vox-prufrock sheet warns its timing is first-pass) and becomes trustworthy.
Karaoke falls out of the same `words.json` for free.

## The central tension — solve it, don't decorate it

**Two texts, one language channel.** Vox explainers put text on screen while
a voice talks because narration and plane are one argument by one author.
Here the ears are full of Eliot. Anything the plane *says* competes with the
poem for the same verbal-processing lane (Mayer's redundancy/split-attention
problem, straight from the CLT playbook). This is the design constraint that
makes voxlit its own mode, and it yields laws:

1. **The margin teaches in the breaths.** Chips land on line-ends, stanza
   turns, refrains — never mid-line. The alignment gives us every breath.
2. **Chip budget: ≤5 words, or non-verbal.** A portrait with dates teaches
   without costing a sentence. Prefer iconic teaching over prose teaching.
3. **The margin goes quiet when the poem goes loud.** The charged lines
   ("And in short, I was afraid") get bare cards or clean plates. No chip
   ever shares the frame with the poem's peaks.
4. **Teaching density cap**, like the 40% motion-language rule: teach-role
   beats ≤ ~1/3 of the film. Viewers came for the poem.

## The new axis: `beat.role`

`illustrate | teach | breathe` — orthogonal to shot type and source, locked
at the plan gate. Lint: no two consecutive teach beats; every stanza gets at
least one breathe. Teach-beat kinds for literature:

- **ALLUSION** — the chip cites what the line is quoting: Marvell's coy
  mistress at "squeezed the universe into a ball," John 11 at Lazarus,
  Matthew 14 at the platter, Hesiod at "works and days," *Twelfth Night* at
  "dying fall," the Hamlet playbill at the turn. Prufrock is allusion-dense —
  that's why it's the right fixture.
- **PROVENANCE** — the June 1915 *Poetry* scan on screen while those lines
  are read; "Eliot was 22; Pound forced it into print."
- **GLOSS** — "etherized": a modern surgical word where a Romantic poem
  expects a sunset. One chip teaches the whole modernist break.
- **STRUCTURE** — a refrain counter when "the women come and go" returns.
- **ADAPTATION MARKER** — the chip that says where the country verses leave
  Eliot. Honesty requirement and a teaching moment about adaptation itself.

**Meaning is taught by juxtaposition, not caption.** The edit argues; the
chips cite. Interpretation lives in which plate you cut to — putting "this
symbolizes paralysis" in text on screen is how the mode dies. Scholarship
gate below keeps chips to citable fact.

## Clock mode 3: recitation

The skill has voiceover (per-beat TTS) and music (librosa bar grid). voxlit
adds **recitation**: forced alignment of the known text; beats are verse
sentences cut at breath points. GATE 0 becomes *alignment lock* — inspect
`words.json` against the recording, then everything keys to it.

## The karaoke law (corrected: CC overlay, not a second cut)

ONE master. The words ride as a **synced closed-caption track** cut at the
source's own verse lines (`<slug>.srt` from `align/lines.json`) — the
official CC track, for those who turn it on. No derivative cut to maintain.
Optional word-timed karaoke highlight = a Remotion overlay variant
(`vox_karaoke.py`) rendered only on request; same assembly, burn-in flag.
Chips stay out of the lower third so CC and marginalia can coexist —
CC is viewer-opted, so the two-texts collision is the viewer's choice.

Wrinkle worth deciding: the master's ink cards already quote the poem ("Do I
dare / disturb the universe?"). I'd keep them — quoting the line *being
heard* is signaling, not redundancy; it's external teaching text that
competes. The rule: on-screen words may only be words currently in the ear.

## Sibling skill, not a mode flag

The voxbio precedent: same chassis, own SKILL.md. The workflow genuinely
differs — no script authoring, no TTS spend, and `factcheck` becomes a
**scholarship gate**: every chip claim sourced like a footnote (allusion,
date, biographical fact), because a wrong marginal note in a literature film
is worse than a wrong number in an explainer — it teaches confidently and
falsely. Keep vox-explainer lean; let `voxlit` own the recitation clock, the
role axis, the margin laws, the karaoke law.

## One challenge to the premise

Is teaching-*while*-hearing better than teaching-*then*-hearing? The
alternative shape: a 60–90s cold-open prologue (pure vox, sets the frame —
1915, Pound, what an interior monologue is), then the poem runs mostly clean
with only allusion chips. That's how a lot of great criticism actually works:
arm the reader, then get out of the way. The simultaneous-margin version is
more novel and more Vox; the prologue version is pedagogically safer. A
hybrid is legal in the current design — front-load two or three PROVENANCE
beats during the musical intro, keep the margin sparse after. The Prufrock
fixture can test both: the review cut makes re-roling beats cheap.

## What changes for reels/vox-prufrock

The current sheet is ~90% illustrate-role. Extension pass: re-role ~15–20
beats to teach (the allusions above), run forced alignment to replace the
uniform-line clock, re-snap beat boundaries to breaths instead of bars, keep
the four-crimson accent rule intact. Then cut the karaoke derivative from
the same sheet.
