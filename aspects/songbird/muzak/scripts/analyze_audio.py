#!/usr/bin/env python3
"""
analyze_audio.py — offline beat/energy analysis of a song's WAV.

This is the *ground truth* timing for a muzak music video. Everything the
Remotion project does — cuts, flashes, lyric hits, color breathing — is derived
from the JSON this script writes, never from a guessed tempo. Run it once per
song (or re-run if the audio changes); never hand-edit the output.

Output schema is documented in references/beat-data-schema.md. Summary:

    {
      "version": 1,
      "fps": 30,
      "bpm": 122.0,
      "durationInSeconds": 184.3,
      "durationInFrames": 5529,
      "beatTimestamps":     [s, ...],   # every beat, seconds
      "downbeatTimestamps": [s, ...],   # bar starts (best-effort), seconds
      "beatFrames":         [f, ...],   # beats rounded to video frames
      "downbeatFrames":     [f, ...],
      "energyPerFrame":     [0..1, ...],# one onset-strength value per video frame
      "sections": [ {"start": s, "end": s, "startFrame": f, "endFrame": f,
                     "label": "section_1"} , ... ]
    }

Usage:
    python analyze_audio.py audio.wav --fps 30 -o beat_data.json

librosa does the heavy lifting. If it isn't installed the script prints an
install hint and exits non-zero rather than crashing cryptically.
"""

import argparse
import json
import sys


def _require_deps():
    try:
        import numpy  # noqa: F401
        import librosa  # noqa: F401
    except ImportError as e:
        sys.stderr.write(
            "muzak: missing dependency (%s).\n"
            "Install the analysis deps, then re-run:\n"
            "    pip install librosa soundfile numpy\n"
            "(in this sandbox: pip install librosa soundfile numpy --break-system-packages)\n"
            % e.name
        )
        sys.exit(2)


_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# Krumhansl-Schmuckler key profiles.
_MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def _timbre_features(y, sr, rms_amp=None, hop_length=512, chroma=None):
    """Brightness, dynamic range, and key/mode — the design-inference signals.

    brightness: mean spectral centroid normalized to 0..1 (0=dark/warm,
        1=bright/cool). The primary signal for color temperature.
    dynamic_range_db: 95th-10th percentile of RMS in dB. Low (<6) = compressed,
        so beat-hit exaggeration must be capped; high (>12) = punchy, allow drama.
    key / mode: Krumhansl-Schmuckler correlation on the harmonic chroma. mode is
        a weak warm/cool palette *bias*, gated by mode_confidence (the margin
        between the winning and runner-up correlations).
    """
    import numpy as np
    import librosa

    sc = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    mean_centroid = float(np.mean(sc))
    brightness = float(np.clip((mean_centroid - 500.0) / 7500.0, 0.0, 1.0))

    rms = rms_amp if rms_amp is not None else librosa.feature.rms(y=y, hop_length=hop_length)[0]
    # Measure dynamic range on *active* audio only. Digital silence (quiet intros,
    # gaps) drives RMS toward the dB floor and would inflate the range, making a
    # tame track look punchy. Keep frames above 5% of peak RMS before the spread.
    peak = float(np.max(rms)) if len(rms) else 0.0
    active = rms[rms > 0.05 * peak] if peak > 0 else rms
    if len(active) < 10:
        active = rms
    rms_db = librosa.amplitude_to_db(active)
    dynamic_range_db = float(np.percentile(rms_db, 95) - np.percentile(rms_db, 10))

    # key/mode from chroma (reuse the precomputed CQT chroma; fall back to a
    # cheap STFT chroma if none was passed). We skip HPSS here — on a full mix it
    # roughly doubles analysis time for a marginal key-detection gain, and key is
    # only a weak palette bias anyway.
    try:
        if chroma is None:
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
        cm = np.mean(chroma, axis=1)
        best = (-np.inf, None, None)
        runner = -np.inf
        for tonic in range(12):
            rotated = np.roll(cm, -tonic)
            for mode_name, profile in (("major", _MAJOR_PROFILE), ("minor", _MINOR_PROFILE)):
                corr = float(np.corrcoef(rotated, profile)[0, 1])
                if corr > best[0]:
                    runner = best[0]
                    best = (corr, _NOTE_NAMES[tonic], mode_name)
                elif corr > runner:
                    runner = corr
        key, mode = best[1], best[2]
        # confidence = how decisively the winner beats the runner-up (0..~0.3)
        mode_confidence = round(float(best[0] - runner), 3) if np.isfinite(runner) else 0.0
    except Exception:
        key, mode, mode_confidence = None, None, 0.0

    return {
        "brightness": round(brightness, 3),
        "mean_spectral_centroid_hz": round(mean_centroid, 1),
        "dynamic_range_db": round(dynamic_range_db, 2),
        "key": key,
        "mode": mode,
        "mode_confidence": mode_confidence,
    }


def analyze(path, fps, hop_length=512, analysis_sr=22050):
    import numpy as np
    import librosa

    # Load mono at a standard *analysis* sample rate (22.05 kHz by default), not
    # the file's native rate. Beat/energy/centroid/chroma analysis doesn't need
    # 44–48 kHz, and resampling keeps a full-length song (3–5 min) analyzable in
    # seconds instead of minutes. The Remotion visualizers read the real
    # full-rate stereo file separately, so fidelity where it matters is intact.
    y, sr = librosa.load(path, sr=analysis_sr, mono=True)
    duration_s = float(len(y) / sr)
    total_frames = int(round(duration_s * fps))

    # Compute the CQT chroma ONCE and reuse it for both key detection and the
    # structural segmentation — it's the most expensive feature, so doing it
    # twice is what made long tracks slow.
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)

    # --- Tempo + beats -------------------------------------------------------
    # onset envelope first so we can reuse it both for beat tracking and for the
    # per-frame energy signal that drives color/scale.
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    tempo, beat_idx = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr, hop_length=hop_length, trim=False
    )
    bpm = float(np.atleast_1d(tempo)[0])
    beat_times = librosa.frames_to_time(beat_idx, sr=sr, hop_length=hop_length)
    beat_times = [float(t) for t in beat_times]

    # --- Downbeats (best-effort, no madmom dependency) -----------------------
    # We don't ship a full meter tracker. Assume 4/4 and mark every 4th beat,
    # phase-aligned to the strongest onset among the first four beats so bar 1
    # starts on the loudest of them. This is "good enough" for cutting on bars;
    # a design doc / user can override if a track is in 3/4 or 6/8.
    downbeat_times = []
    if beat_times:
        first4 = beat_idx[:4] if len(beat_idx) >= 4 else beat_idx
        if len(first4):
            strengths = [onset_env[min(i, len(onset_env) - 1)] for i in first4]
            phase = int(np.argmax(strengths))
        else:
            phase = 0
        downbeat_times = [beat_times[i] for i in range(phase, len(beat_times), 4)]

    # --- Per-frame energy envelope -------------------------------------------
    # Resample the onset envelope to exactly one value per *video* frame, then
    # normalize to 0..1 so the Remotion side can map it to color/opacity/scale
    # without knowing anything about the absolute scale.
    onset_times = librosa.times_like(onset_env, sr=sr, hop_length=hop_length)
    frame_times = np.arange(total_frames) / fps
    if len(onset_env) > 1:
        energy = np.interp(frame_times, onset_times, onset_env)
    else:
        energy = np.zeros(total_frames)
    emax = float(energy.max()) if len(energy) and energy.max() > 0 else 1.0
    energy_norm = [float(v / emax) for v in energy]

    # --- Timbre / harmony features (drive the design inference) ---------------
    # These are not used for timing; they are the raw signals the `design`
    # phase maps to palette, motion, and visualizer form (see
    # references/design-inference.md). Computing them here means one analysis
    # pass produces everything design needs.
    features = _timbre_features(y, sr, rms_amp=None, hop_length=hop_length, chroma=chroma)

    # --- Sections (structural segmentation) ----------------------------------
    # librosa's agglomerative segmentation over a chroma/MFCC stack gives a
    # rough verse/chorus/bridge map. We don't try to *name* them (that needs the
    # lyrics + a human); we hand back boundaries so `plan` can assign a visualizer
    # per section and `lyrics` can distribute lines within a section.
    sections = []
    try:
        n_sections = max(2, min(8, int(duration_s // 20)))  # ~one per 20s, 2..8
        mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=13)
        stack = np.vstack([librosa.util.normalize(chroma, axis=1),
                           librosa.util.normalize(mfcc, axis=1)])
        bounds = librosa.segment.agglomerative(stack, n_sections)
        bound_times = librosa.frames_to_time(bounds, sr=sr, hop_length=hop_length)
        edges = [0.0] + [float(t) for t in bound_times if 0 < t < duration_s] + [duration_s]
        edges = sorted(set(round(e, 3) for e in edges))
        for i in range(len(edges) - 1):
            s, e = edges[i], edges[i + 1]
            if e - s < 1.0:  # drop slivers
                continue
            sections.append({
                "start": s, "end": e,
                "startFrame": int(round(s * fps)), "endFrame": int(round(e * fps)),
                "label": "section_%d" % (len(sections) + 1),
            })
    except Exception as ex:  # segmentation is a nice-to-have, never fatal
        sys.stderr.write("muzak: section segmentation skipped (%s)\n" % ex)
        sections = [{"start": 0.0, "end": duration_s,
                     "startFrame": 0, "endFrame": total_frames, "label": "section_1"}]

    return {
        "version": 1,
        "fps": fps,
        "bpm": round(bpm, 2),
        "durationInSeconds": round(duration_s, 3),
        "durationInFrames": total_frames,
        "beatTimestamps": [round(t, 4) for t in beat_times],
        "downbeatTimestamps": [round(t, 4) for t in downbeat_times],
        "beatFrames": [int(round(t * fps)) for t in beat_times],
        "downbeatFrames": [int(round(t * fps)) for t in downbeat_times],
        "energyPerFrame": [round(v, 4) for v in energy_norm],
        "sections": sections,
        "features": features,
    }


def main():
    ap = argparse.ArgumentParser(description="Offline beat/energy analysis for muzak.")
    ap.add_argument("wav", help="path to the song WAV (or any audio librosa can read)")
    ap.add_argument("--fps", type=int, default=30, help="video frame rate (default 30)")
    ap.add_argument("--hop", type=int, default=512, help="librosa hop length (default 512)")
    ap.add_argument("--sr", type=int, default=22050,
                    help="analysis sample rate (default 22050; lower = faster on long tracks)")
    ap.add_argument("-o", "--out", default="beat_data.json", help="output JSON path")
    args = ap.parse_args()

    _require_deps()
    data = analyze(args.wav, args.fps, args.hop, analysis_sr=args.sr)
    with open(args.out, "w") as f:
        json.dump(data, f, indent=2)

    print("muzak: wrote %s" % args.out)
    print("  bpm:        %.1f" % data["bpm"])
    print("  duration:   %.1fs  (%d frames @ %dfps)"
          % (data["durationInSeconds"], data["durationInFrames"], args.fps))
    print("  beats:      %d  (downbeats: %d)"
          % (len(data["beatTimestamps"]), len(data["downbeatTimestamps"])))
    print("  sections:   %d" % len(data["sections"]))
    for s in data["sections"]:
        print("    %-12s %6.1fs – %6.1fs" % (s["label"], s["start"], s["end"]))
    f = data["features"]
    print("  features (design signals):")
    print("    brightness:    %.3f  (centroid %.0f Hz)  -> %s"
          % (f["brightness"], f["mean_spectral_centroid_hz"],
             "dark/warm" if f["brightness"] < 0.35 else
             "bright/cool" if f["brightness"] > 0.65 else "neutral"))
    print("    dynamic range: %.1f dB  -> %s"
          % (f["dynamic_range_db"],
             "compressed (cap beat-hits)" if f["dynamic_range_db"] < 6 else
             "wide (allow drama)" if f["dynamic_range_db"] > 12 else "moderate"))
    print("    key/mode:      %s %s  (confidence %.3f)"
          % (f["key"], f["mode"], f["mode_confidence"]))


if __name__ == "__main__":
    main()
