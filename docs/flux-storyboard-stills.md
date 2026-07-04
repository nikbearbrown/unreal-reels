# FLUX Storyboard Stills

This is the standing rule for Unreal Reels storyboard generation.

## Core Rule

`PNG/` images are source/reference inputs. They are not the final storyboard frames.

For each beat, create the storyboard stills by sending the reference image or images to
FLUX/Higgsfield together with the beat's visual prompt:

- `beat.assets` or `beat.reference` supplies the input image(s).
- `beat.image_prompt` supplies the visual scene.
- If present, `beat.image_prompt_a` creates `B##_A_start.png`.
- If present, `beat.image_prompt_b` creates `B##_B_end.png`.
- The generated outputs go in `stills/story/` for vertical `9:16` and
  `stills/story-16x9/` for wide `16:9`.

Do not create storyboard stills by locally resizing, cropping, color-grading, or
otherwise deriving them from the input PNGs. Local image processing can make contact
sheets or previews, but those previews are not the storyboard deliverables.

## Beat Sheet Pattern

Example:

```json
{
  "beat_id": "B26",
  "assets": ["PNG/myqwewrnvow.png"],
  "storyboard_start": "stills/story/B26_A_start.png",
  "storyboard_end": "stills/story/B26_B_end.png",
  "storyboard_start_16x9": "stills/story-16x9/B26_A_start.png",
  "storyboard_end_16x9": "stills/story-16x9/B26_B_end.png",
  "image_prompt": "Miniver pats empty pockets and looks irritated, the fantasy collapsing into need. Black-and-white portrait, no text."
}
```

Interpretation:

1. Upload or pass `PNG/myqwewrnvow.png` as the FLUX input image.
2. Use the `image_prompt` as the text prompt.
3. Generate a still for the requested aspect ratio.
4. Save the result at the matching `storyboard_*` path.
5. Only after the generated still is approved should video generation begin.

## Aspect Outputs

When both aspect ratios are needed, run the same beat through FLUX twice:

- `ASPECT=9:16` -> `stills/story/B##_A_start.png` and `B##_B_end.png`
- `ASPECT=16:9` -> `stills/story-16x9/B##_A_start.png` and `B##_B_end.png`

If a beat only has one `image_prompt`, use it for the still. If a start/end pair is
needed, write distinct `image_prompt_a` and `image_prompt_b` first, then generate each
frame separately from the same reference images.

## Paid-Service Gate

FLUX/Higgsfield spends credits. Always get explicit user approval before running the
actual generation command. Dry runs, prompt docs, beat-sheet edits, and contact sheets
are safe local prep.

## Checklist Before Generating

- Read `beat_sheet.json`.
- Confirm every referenced `PNG/...` asset exists.
- Confirm the prompt is a visual scene, not lyrics, narration, captions, or dialogue.
- Confirm the intended aspect ratio.
- Ask before starting paid FLUX/Higgsfield generation.
- Save outputs exactly where the beat sheet points.
- Update `chosen_still` only after the user picks or approves the keeper.
