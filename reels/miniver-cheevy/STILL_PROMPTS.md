# Miniver Cheevy - FLUX Still Generation

Use this file as the handoff note for Miniver Cheevy stills.

## Rule

The files in `PNG/` are FLUX reference inputs. They are not finished storyboard stills.

For every beat in `beat_sheet.json`, send the beat's `assets` image to FLUX together
with the beat's `image_prompt`. Save the generated result to the beat's
`storyboard_start` / `storyboard_end` paths, and to the matching `story-16x9` paths
when generating the wide version.

Do not fill `stills/story/` or `stills/story-16x9/` by locally cropping or resizing
the `PNG` inputs. Those folders are for generated FLUX outputs.

## Example

For this beat:

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

The intended operation is:

1. Use `PNG/myqwewrnvow.png` as the input image/reference.
2. Use the `image_prompt` as the FLUX prompt.
3. Generate the `9:16` still and save it under `stills/story/`.
4. Generate the `16:9` still and save it under `stills/story-16x9/`.
5. Repeat for A/B start-end frames if separate prompts exist.

## Current Note

If local placeholder files exist in `stills/`, treat them as invalid unless they were
actually generated through FLUX/Higgsfield from the beat prompt plus the input PNG.
The real storyboard stills for this reel should be regenerated through the FLUX flow.

See also: `../../docs/flux-storyboard-stills.md`.
