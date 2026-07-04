# Video Visual-QC Tooling (consolidated)

Deterministic, advisory layout-QA tools for Manim video scenes. Gathered here
2026-07-04 so the complete set lives in one pushed place. None of these edit a
scene — they report and exit (0 clean / 1 warnings / 2 errors).

## Files

| File | What it checks | Needs Manim? |
|---|---|---|
| `manim_layout_audit.py` | **Primary.** Asks Manim for the exact bounding box of every on-screen `Text` at each steady-state moment and flags: text-on-text overlap, out-of-frame / out-of-safe-area text, and text struck by a curve/stroke. `--png` saves an annotated frame per flag. Emits `layout_audit.json` + `layout_audit.md`. (515-line, newest — adds TEXT/CURVE, `--portrait`, `--curve-strict`.) | Yes (pangocairo) |
| `static_scene_check.py` | **Render-free companion.** Runs `construct()` against a geometry stub to catch: crashes, the `generic_art` template, repeated-animation (distinct-shapes-per-beat ratio), and out-of-frame explicit coordinates. Not pixel-perfect. | No |
| `manim_layout_audit_v426_older.py` | Previous generation of the primary tool (no TEXT/CURVE check). Kept for provenance. | Yes |
| `FINDINGS.md` | The full search report: every candidate found, invocation commands, git state, ranking. | — |

## Usage

```bash
# Primary — run inside a scene folder (needs a working Manim install)
python manim_layout_audit.py scene.py --png
python manim_layout_audit.py scene.py --portrait      # 9:16 safe area
python manim_layout_audit.py scene.py --curve-strict  # TEXT/CURVE -> ERROR

# Render-free pre-flight (no Manim needed)
python static_scene_check.py scene.py
python static_scene_check.py <folder>
python static_scene_check.py --all --json out.json
```

## Provenance

- `manim_layout_audit.py` (newest) was already committed+pushed in this repo at
  `aspects/explainer/bears-doodles/scripts/`; an identical copy was untracked in
  the `quantum-mechanics-vol1` repo. md5 `1212c624…`.
- `static_scene_check.py` existed **only** inside an unpushed commit in the
  `Manim` (`quantum-mechanics-videos`) repo — consolidating it here backs it up.
  md5 `3afa5002…`.

Intentionally **not** included (production/helpers, not layout QC):
`extract_frames.sh` + `pick_stills.py` (lyric-match frame extraction),
`greybox.py` (previz), `make_short.py` (reframe), `verify_extras.py` (YouTube
caption/playlist check), `verify_deck.py` / `script_guard.py` / `tts_audit.py`
(deck/text checks).
