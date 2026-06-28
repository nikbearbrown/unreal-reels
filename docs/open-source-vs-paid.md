# Free (open source) vs. paid services

The **engine is open source and runs locally for free.** The cost is only the **generative
models** (voice, images, video), and even those you can self-host if you have a capable GPU. So
you have a choice at each generative stage: a **hosted paid API** (no GPU, easy, per-credit) or
**self-hosted open models** (free, but needs a strong GPU and more setup).

## Stage by stage

| Stage | Free / open-source | Paid hosted (easy button) |
|---|---|---|
| Segment text → beats | ✅ Python (this repo) | — |
| Beat / onset analysis (music) | ✅ librosa | — |
| Forced alignment (caption timing) | ✅ faster-whisper | — |
| Narration TTS | ⚠️ Piper / Coqui / macOS `say` (free; lower quality, weak voice-cloning) | **ElevenLabs** (voice cloning, best quality) |
| Character reference plates | ⚠️ local SD/FLUX + IP-Adapter (GPU) | **Higgsfield SoulID** |
| Storyboard (multi-reference stills) | ⚠️ local FLUX + IP-Adapter/ControlNet (GPU) | **Higgsfield FLUX.2** |
| Image → video | ⚠️ local video models (heavy GPU), or Ken-Burns on stills (free, no real motion) | **Higgsfield / Kling / Veo** |
| Style LoRA training | ✅ kohya / diffusers (GPU) | **fal.ai** |
| Overlay / captions / assembly | ✅ Remotion + ffmpeg | — |

✅ = free and local · ⚠️ = free but needs a capable GPU + setup, *or* pay a hosted service.

## The honest summary

- **The glue — segmentation, timing, beat analysis, caption alignment, overlay, assembly — is
  100% free and local.** You can clone this repo and run all of that today with no account.
- **The generative models are the cost.** With **no GPU**, the hosted services are effectively
  required for images/video/voice-cloning. With **a strong GPU**, you can run nearly everything
  free via ComfyUI (FLUX/SD + IP-Adapter), a local TTS, and local video — trading money for
  setup time and slower iteration.

## By aspect — how free can each get?

- **Songbird (music videos) — most free-friendly.** The spine is all open-source: beat/onset
  analysis (librosa), karaoke captions (faster-whisper), and the audiogram + motion graphics
  (Remotion). You supply your own music. Generated stills/clips are optional garnish (paid or
  local). You can ship a real lyric/audiogram video with **zero paid services**.
- **Explainer — largely free.** Narration via local TTS, figures drawn as **SVG/diagrams**
  (code, not generated), labels/equations as Remotion overlays. Pay only if you want photoreal
  generated visuals instead of clean diagrams.
- **Bios — partly paid.** Needs narration (TTS — local or ElevenLabs) and figure visuals
  (local or Higgsfield). The narrator-over-B-roll structure means a few good images go a long
  way, so paid spend is modest.

**Bottom line:** you can learn and build the *entire* pipeline for free, and produce real music
videos and explainers with only open-source tools. The photoreal, character-locked films (the
SoulID + FLUX.2 work) are where the hosted models earn their keep — they replace owning a GPU.
