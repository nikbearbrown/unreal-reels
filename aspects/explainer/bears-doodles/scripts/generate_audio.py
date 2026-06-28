#!/usr/bin/env python3
"""
generate_audio.py — Bear's Doodles audio-first TTS.

For a video folder, reads beat_sheet.json and generates one ElevenLabs MP3 per
beat (including the INTRO), measures the real duration with mutagen, and writes:

  <folder>/mp3/beat-<ID>.mp3
  <folder>/mp3/timings.json     {"INTRO": 3.1, "A00": 4.0, ...}

It also writes actual_duration_s and audio_file back into beat_sheet.json so the
beat sheet stays the single source of truth. This duration is GROUND TRUTH for
all downstream render timing — never estimate from word count.

Requires:  pip install requests mutagen   (in the ~/ai venv)
Requires:  ELEVENLABS_API_KEY in the environment (or pass --api-key).

Usage:
    python generate_audio.py path/to/<slug>
    python generate_audio.py path/to/<slug> --dry-run        # no API calls; just plan
    python generate_audio.py path/to/<slug> --only A00 A03   # regenerate specific beats
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

# Math/symbol → spoken form. Applied to tts text as a safety net even if the beat
# sheet already carries tts_normalized_text.
SYMBOLS = {
    "ψ": "psi", "Ψ": "Psi", "ℏ": "h-bar", "|ψ|²": "psi squared",
    "∫": "integral of", "→": "goes to", "≥": "greater than or equal to",
    "≤": "less than or equal to", "Δx": "delta x", "Δp": "delta p",
    "ΔE": "delta E", "∞": "infinity", "E₀": "E sub zero", "E₁": "E sub one",
    "·": " times ", "²": " squared", "½": "one half", "—": ", ",
}


def normalize_for_tts(text: str) -> str:
    for sym, spoken in SYMBOLS.items():
        text = text.replace(sym, spoken)
    return text


def measure_duration(path: Path) -> float:
    from mutagen.mp3 import MP3
    return round(MP3(str(path)).info.length, 2)


def generate_silence(out_path: Path, seconds: float):
    """Write a silent MP3 of `seconds` length (ffmpeg). Used for beats marked
    `"silent": true` — e.g. logo-reel construction/montage holds that carry no
    narration but need to occupy real time so spoken beats stay in sync."""
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
         "-t", f"{seconds:.3f}", "-q:a", "9", "-acodec", "libmp3lame", str(out_path)],
        check=True, capture_output=True)


def generate_one(text, voice_id, settings, out_path, api_key):
    # Uses the stdlib (urllib) so the only third-party dep is mutagen.
    import urllib.request
    import urllib.error
    payload = {
        "text": text,
        "model_id": settings.get("model_id", "eleven_multilingual_v2"),
        "output_format": "mp3_44100_128",
        "voice_settings": {
            "stability": settings.get("stability", 0.80),
            "similarity_boost": settings.get("similarity_boost", 0.75),
            "style": settings.get("style", 0.00),
            "use_speaker_boost": False,
        },
    }
    # ElevenLabs reads `speed` inside voice_settings on current models.
    if "speed" in settings:
        payload["voice_settings"]["speed"] = settings["speed"]
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    req = urllib.request.Request(
        API_URL.format(voice_id=voice_id),
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            out_path.write_bytes(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")[:400]
        raise SystemExit(f"[err] ElevenLabs HTTP {e.code}: {detail}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Bear's Doodles audio-first TTS generator.")
    ap.add_argument("folder", help="Path to the video folder (contains beat_sheet.json)")
    ap.add_argument("--api-key", default=os.getenv("ELEVENLABS_API_KEY"))
    ap.add_argument("--dry-run", action="store_true", help="Plan only; no API calls")
    ap.add_argument("--only", nargs="*", default=None, help="Beat IDs to (re)generate")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    sheet_path = folder / "beat_sheet.json"
    if not sheet_path.exists():
        print(f"[err] no beat_sheet.json in {folder}", file=sys.stderr)
        return 1

    sheet = json.loads(sheet_path.read_text())
    voice_id = sheet["metadata"].get("voice_id", "")
    beats = sheet["beats"]
    if not beats:
        print("[err] beat sheet has no beats. Run the `beats` command first.", file=sys.stderr)
        return 1

    mp3_dir = folder / "mp3"
    mp3_dir.mkdir(exist_ok=True)

    if not args.dry_run and not args.api_key:
        print("[err] ELEVENLABS_API_KEY not set. Export it or pass --api-key, or use --dry-run.", file=sys.stderr)
        return 2

    selected = set(args.only) if args.only else None
    timings = {}
    if (mp3_dir / "timings.json").exists():
        timings = json.loads((mp3_dir / "timings.json").read_text())

    total = 0.0
    for beat in beats:
        bid = beat["beat_id"]
        if selected and bid not in selected:
            # keep prior timing if present
            if bid in timings:
                total += timings[bid]
            continue

        out_path = mp3_dir / f"beat-{bid}.mp3"

        # Reuse an already-generated clip (e.g. a line of VO replayed across many
        # beats/segments). No API call; just point at it and measure its length.
        reuse = beat.get("reuse_audio")
        if reuse:
            rp = folder / reuse
            if args.dry_run:
                print(f"[plan] {bid:5}  reuse {reuse}")
                total += float(beat.get("actual_duration_s", 0.0))
                continue
            if not rp.exists():
                print(f"[err] reuse_audio missing: {rp}", file=sys.stderr)
                return 1
            d = measure_duration(rp)
            timings[bid] = d
            beat["audio_file"] = reuse
            beat["actual_duration_s"] = d
            total += d
            print(f"[reuse] {bid:5}  → {reuse}  {d}s")
            continue

        # Silent beat: occupy time with generated silence, no API call.
        if beat.get("silent"):
            sil = float(beat.get("silence_s", 1.0))
            if args.dry_run:
                print(f"[plan] {bid:5}  ~{sil:>5}s  (silent hold)")
                total += sil
                continue
            print(f"[gen]  {bid:5}  → {out_path.name}  (silence {sil}s)")
            generate_silence(out_path, sil)
            dur = measure_duration(out_path)
            timings[bid] = dur
            beat["audio_file"] = f"mp3/beat-{bid}.mp3"
            beat["actual_duration_s"] = dur
            total += dur
            print(f"       {dur:>5}s")
            continue

        raw = beat.get("tts_normalized_text") or beat.get("narration_text", "")
        text = normalize_for_tts(raw)
        settings = beat.get("tts_voice_settings", {})
        # Per-beat voice override enables dialogue mode (two+ speakers trading beats);
        # falls back to the metadata voice_id for ordinary single-narrator bios.
        bvoice = beat.get("voice_id", voice_id)

        if args.dry_run:
            words = len(text.split())
            est = round(words / 2.3, 2)
            print(f"[plan] {bid:5}  ~{est:>5}s  {text[:60].replace(chr(10), ' / ')}")
            total += est
            continue

        print(f"[gen]  {bid:5}  → {out_path.name}")
        generate_one(text, bvoice, settings, out_path, args.api_key)
        dur = measure_duration(out_path)
        timings[bid] = dur
        beat["audio_file"] = f"mp3/beat-{bid}.mp3"
        beat["actual_duration_s"] = dur
        total += dur
        print(f"       {dur:>5}s")

    if not args.dry_run:
        (mp3_dir / "timings.json").write_text(json.dumps(timings, indent=2))
        sheet["metadata"]["total_estimated_duration_seconds"] = round(total, 2)
        sheet_path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False))
        print(f"[ok] wrote {mp3_dir/'timings.json'}")
        print(f"[ok] updated beat_sheet.json with actual durations")

    print(f"[total] {'estimated' if args.dry_run else 'actual'} duration ≈ {round(total,2)}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
