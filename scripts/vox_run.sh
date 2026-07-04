#!/usr/bin/env bash
# vox_run.sh — ONE command: QC-gate, render every pending Manim scene, slot the
# outputs, recompile the reel. Bash 3.2-safe. Free/local (Manim + ffmpeg).
#
#   bash scripts/vox_run.sh reels/<slug> [--height 1080]
#
# Skips any beat whose slot is already filled (manim/<B>.mp4 or media/<B>.mp4).
#
# QC GATES (tmp/qc-tooling — advisory tools, wired here as hard gates):
#   Gate A (pre-flight, render-free): static_scene_check.py per pending scene.
#           errors (exit 2) ABORT before any render; warnings print + continue.
#   Gate B (post-render, pixel-true): manim_layout_audit.py --png per scene.
#           errors (exit 2) REFUSE to slot that mp4 and abort — see the
#           annotated PNGs + layout_audit.md next to vox_graphics.py.
#   Skip both with VOX_QC=0 (e.g. `VOX_QC=0 bash scripts/vox_run.sh …`).
set -e
REEL="$1"; shift || true
HEIGHT=1080
if [ "$1" = "--height" ]; then HEIGHT="$2"; fi
VOX_QC="${VOX_QC:-1}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GFX="$ROOT/aspects/explainer/vox-explainer/manim"
GFXFILE="vox_graphics.py"
if [ -f "$ROOT/$REEL/vox_scenes.py" ]; then   # converted reels carry their own fragments
  GFX="$ROOT/$REEL"; GFXFILE="vox_scenes.py"
fi
QC="$ROOT/tmp/qc-tooling"
mkdir -p "$ROOT/$REEL/manim"

SCENES=$(python3 -c "
import re
src = open('$GFX/$GFXFILE').read()
print(' '.join(m.group(1) for m in re.finditer(r'class ([A-Z][A-Za-z0-9]*_\w+)\(Scene\)', src)))
")

# ---- figure out which scenes are actually pending (slot not filled)
PENDING=""
for S in $SCENES; do
  BID="${S%%_*}"
  if [ -f "$ROOT/$REEL/manim/$BID.mp4" ] || [ -f "$ROOT/$REEL/media/$BID.mp4" ]; then
    echo "[vox_run] skip $S — $BID already filled"
  else
    PENDING="$PENDING $S"
  fi
done
if [ -z "$PENDING" ]; then
  echo "[vox_run] nothing to render — recompiling only"
fi

# ---- GATE A: render-free pre-flight on every pending scene
# The scenes file is checked from an ISOLATED copy: the checker's
# repeated-animation heuristic assumes one Scene spanning a whole beat sheet
# (bears-doodles format); per-beat vox fragments hold one visual by design,
# so the sheet must not sit next to the file under check. Crash and
# out-of-frame checks still apply in full.
if [ "$VOX_QC" = "1" ] && [ -n "$PENDING" ] && [ -f "$QC/static_scene_check.py" ]; then
  echo "[vox_run] GATE A — static pre-flight"
  TMPQC=$(mktemp -d)
  cp "$GFX/$GFXFILE" "$TMPQC/"
  for S in $PENDING; do
    rc=0
    PYTHONPATH="$ROOT/aspects/explainer/vox-explainer/manim" \
      python3 "$QC/static_scene_check.py" "$TMPQC/$GFXFILE" --class "$S" --quiet || rc=$?
    if [ "$rc" -ge 2 ]; then
      echo "[vox_run] GATE A FAILED: $S has static errors — fix vox_graphics.py, nothing rendered"
      exit 2
    elif [ "$rc" -eq 1 ]; then
      echo "[vox_run] gate A warning on $S (continuing)"
    fi
  done
fi

# ---- render + GATE B per scene
cd "$GFX"
for S in $PENDING; do
  BID="${S%%_*}"
  echo "[vox_run] rendering $S"
  manim -qh --fps 24 -r 1920,1080 "$GFXFILE" "$S"
  OUT=$(find media/videos -name "$S.mp4" | head -1)
  if [ -z "$OUT" ]; then echo "[vox_run] ERROR: no output for $S"; exit 1; fi
  if [ "$VOX_QC" = "1" ] && [ -f "$QC/manim_layout_audit.py" ]; then
    rc=0
    python3 "$QC/manim_layout_audit.py" "$GFXFILE" --class "$S" --png || rc=$?
    if [ "$rc" -ge 2 ]; then
      echo "[vox_run] GATE B FAILED: $S has layout errors — mp4 NOT slotted."
      echo "[vox_run] see $GFX/layout_audit.md and the annotated PNGs beside it."
      exit 2
    elif [ "$rc" -eq 1 ]; then
      echo "[vox_run] gate B warning on $S — slotting anyway, review $GFX/layout_audit.md"
    fi
  fi
  mv "$OUT" "$ROOT/$REEL/manim/$BID.mp4"
done

cd "$ROOT"

# ---- the outro law: brand the closing card (idempotent; needs audio + bears)
if [ -d "$ROOT/bearbrown" ]; then
  python3 scripts/vox_outro.py "$REEL" --bears "$ROOT/bearbrown" \
    || echo "[vox_run] outro skipped (no narration mp3 yet? run generate_audio.py)"
fi

python3 scripts/vox_compile.py "$REEL" --review --height "$HEIGHT"
echo "[vox_run] done → $REEL  (QC gates: $([ "$VOX_QC" = "1" ] && echo on || echo OFF))"
echo "[vox_run] this was the FULL machine pass: motion graphics + outro done;"
echo "[vox_run] any remaining slates are YOUR slots — see $REEL/SHOTLIST.md"
