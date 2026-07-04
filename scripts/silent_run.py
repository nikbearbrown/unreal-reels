#!/usr/bin/env python3
"""
silent_run.py — batch-mode, gate-deferred orchestrator for the lecture pipeline.

Turns ONE chapter.md into a watchable ROUGH lecture folder with no interactive
prompts. Every former human gate becomes either (a) an auto-policy that decides
and LOGS its justification, or (b) an "agent slot": a work-packet the LLM fills
(interactively for the pilot; via the Claude Batch API for the 150-book fleet).

The two pipeline laws are preserved:
  * audio is the master clock  — timing is derived from measured audio, never here.
  * regenerate only the failing unit — stages are idempotent and content-hashed.

This script does the DETERMINISTIC work and records state; it never fakes the two
LLM slots (plan authoring, narration). If a slot is unfilled it stops cleanly at
that slot and tells you exactly what to author. That is the pilot workflow. For
the fleet, --agent batch wires the slots to an external solver (not built here).

Stages (each idempotent; --from / --only to resume):
  setup    make the lecture folder, copy runtime (support.js, deck-stage.js, _ds)
  assets   import the book's figures into the pool + assets.json
  plan     build_plan.py starter  ->  AGENT SLOT 1 (author deck_plan.json)
  deck     emit_deck.py + verify_deck.py
  extract  extract_slides.py -> beat_sheet.json  ->  AGENT SLOT 2 (narration_text)
  script   script_guard (discuss-don't-read) + tts_audit + apply_pronunciations
  audio    generate_audio.py (ElevenLabs; skipped+logged if no key)
  captions align_captions.py (faster-whisper; skipped+logged if unavailable)
  visuals  media-router recommend + build_bullets + build_doodle starters
  scaffold scaffold_remotion.py  (+ prerender_deck.py stills, best-effort)
  qc       verify + pace_check + probes  ->  qc_report.json (0-100 score)

Outputs into the lecture folder:
  decision_log.json   every auto-decision + its reason (your async review surface)
  qc_report.json      one score + itemized checks
  packets/*.md        the two agent slots, when unfilled

Pure stdlib. Calls the existing skill scripts by absolute path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
ASPECTS = REPO / "aspects"

STAGES = ["setup", "assets", "plan", "deck", "extract", "script",
          "audio", "captions", "visuals", "scaffold", "qc"]


# ─────────────────────────── small utilities ────────────────────────────────
def sh(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Run a subprocess, capture combined output, never raise."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=3600)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}"


def sha(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:12] if path.exists() else "-"


# ─────────────────── AI+1 verified-artifact sidecars ────────────────────────
# Identical shape + routing to ai1-cli/scripts/verify.py, so a lecture is a
# first-class AI+1 artifact: agents may stub+check, only a human `sign`s. If the
# book ships its own verify.py we defer to it for `sign`; the format is the same.
def _sidecar(artifact: Path) -> Path:
    return artifact.parent / (artifact.name + ".verified.json")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sidecar_state(artifact: Path) -> tuple[int, str]:
    """0 = verified+fresh, 1 = unverified/no-sidecar, 2 = stale (content changed)."""
    p = _sidecar(artifact)
    if not p.exists():
        return 1, "NO SIDECAR"
    meta = json.loads(p.read_text())
    if not meta.get("verified"):
        return 1, "UNVERIFIED"
    if meta.get("sha256") and artifact.exists() and _sha256(artifact) != meta["sha256"]:
        return 2, "STALE (edited since sign-off)"
    return 0, "verified"


def stub_sidecar(artifact: Path, phase: str) -> None:
    """Agent action: write a verified:false sidecar if none exists. Never signs."""
    p = _sidecar(artifact)
    if p.exists():
        return
    p.write_text(json.dumps({
        "artifact": artifact.name, "phase": phase,
        "verified": False, "verified_by": "", "verified_at": "",
        "note": "", "sha256": "",
    }, indent=2) + "\n")


# The two human gates of a lecture spine, mapped to AI+1 phases.
LECTURE_GATES = [("deck_plan.json", "lecture-plan"),
                 ("beat_sheet.json", "lecture-narration")]


def write_status(folder: Path, mode: str, log: "Log") -> None:
    """Lecture-local STATUS.md — the same gate-table pattern AI+1 uses at book root."""
    lines = [f"# Lecture status — {folder.name}", "",
             f"*Mode: `{mode}`. Generated by silent_run.py. "
             f"The two gates below are human sign-offs (agents may stub, never sign).*", "",
             "| Gate | Artifact | Phase | State |", "|---|---|---|---|"]
    for name, phase in LECTURE_GATES:
        art = folder / name
        _, label = sidecar_state(art)
        exists = "present" if art.exists() else "MISSING"
        lines.append(f"| {phase} | {name} | {phase} | {exists} · {label} |")
    lines += ["", "## Sign a gate (human only)",
              "```",
              f"python scripts/verify.py sign {folder}/deck_plan.json --by <you> "
              f"--phase lecture-plan",
              f"python scripts/verify.py sign {folder}/beat_sheet.json --by <you> "
              f"--phase lecture-narration",
              "```",
              "", f"Reasoning trail: `decision_log.json` · QC: `qc_report.json`"]
    (folder / "STATUS.md").write_text("\n".join(lines) + "\n")


class Log:
    """The decision log — now the REASONING attachment to the AI+1 sidecars/STATUS,
    not the gate itself. Sidecars + STATUS.md are authority; this records the why."""
    def __init__(self, folder: Path):
        self.path = folder / "decision_log.json"
        self.data = {"chapter": folder.name, "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
                     "stages": {}, "decisions": [], "blocked_on": None}
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text()))
            except Exception:  # noqa: BLE001
                pass

    def decide(self, gate: str, choice: str, reason: str, **extra):
        self.data["decisions"].append({"gate": gate, "choice": choice,
                                       "reason": reason, **extra})
        self.flush()

    def stage(self, name: str, status: str, note: str = ""):
        self.data["stages"][name] = {"status": status, "note": note,
                                     "at": time.strftime("%H:%M:%S")}
        self.flush()

    def block(self, packet: str):
        self.data["blocked_on"] = packet
        self.flush()

    def flush(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))


# ─────────────────────────── stage implementations ──────────────────────────
def stage_setup(ch: Path, folder: Path, runtime: Path | None, log: Log):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "packets").mkdir(exist_ok=True)
    copied = []
    if runtime:
        for name in ("support.js", "deck-stage.js"):
            src = runtime / name
            if src.exists():
                shutil.copy2(src, folder / name); copied.append(name)
        if (runtime / "_ds").is_dir():
            shutil.copytree(runtime / "_ds", folder / "_ds", dirs_exist_ok=True)
            copied.append("_ds/")
    log.decide("runtime_source",
               str(runtime) if runtime else "NONE",
               f"copied {copied}" if copied else "no runtime given — deck will need _ds/support.js before scaffold")
    log.stage("setup", "ok", f"folder={folder}")


def stage_assets(ch: Path, folder: Path, images: Path | None, log: Log):
    script = SKILLS / "lecture-assets/scripts/import_book_figures.py"
    if not script.exists():
        log.stage("assets", "skip", "import_book_figures.py missing"); return
    cmd = [sys.executable, str(script), str(folder), "--chapter", ch.stem]
    if images:
        cmd += ["--images", str(images)]
    rc, out = sh(cmd)
    ass = folder / "assets" / "assets.json"
    n = 0
    if ass.exists():
        try:
            n = len(json.loads(ass.read_text()).get("assets", []))
        except Exception:  # noqa: BLE001
            pass
    log.decide("asset_pool", f"{n} candidates", "imported book figures as candidate pool")
    log.stage("assets", "ok" if rc == 0 else "warn", out.strip().splitlines()[-1] if out.strip() else "")


def emit_slot(folder: Path, mode: str, name: str, body: str,
              api_messages: list[dict] | None = None) -> Path:
    """Deliver an agent slot in a mode-appropriate container. The CONTENT is the
    same across modes; only who runs the LLM changes (AI+1's three-modes rule)."""
    pk = folder / "packets"
    pk.mkdir(exist_ok=True)
    if mode == "handoff":
        p = pk / f"{name}.prompt.md"
        p.write_text(body + "\n\n---\nHANDOFF: paste this into any LLM; save its reply "
                     f"as `{name}.reply.json`, then re-run silent_run with --from the "
                     "same stage.\n")
    elif mode == "api":
        p = pk / f"{name}.request.json"
        p.write_text(json.dumps({"messages": api_messages or
                     [{"role": "user", "content": body}]}, indent=2))
    else:  # agent
        p = pk / f"{name}.md"
        p.write_text(body)
    return p


def stage_plan(ch: Path, folder: Path, log: Log, mode: str) -> bool:
    """Build the starter, then require a SIGNED deck_plan.json (AI+1 GATE, phase
    lecture-plan). Routing = verify.py: verified→use; unverified→stop; none→make."""
    plan = folder / "deck_plan.json"
    starter = folder / "deck_plan.starter.json"
    ass = folder / "assets" / "assets.json"
    cmd = [sys.executable, str(SKILLS / "slide-deck/scripts/build_plan.py"), str(ch)]
    if ass.exists():
        cmd.append(str(ass))
    cmd += ["-o", str(starter)]
    rc, out = sh(cmd)
    if rc != 0:
        log.stage("plan", "error", out.strip()[-400:]); return False

    code, label = sidecar_state(plan)
    if code == 0:  # verified + fresh -> use it, don't regenerate
        log.decide("plan_gate", "verified", "deck_plan.json signed off — using it")
        log.stage("plan", "ok", "verified"); return True
    if plan.exists():  # authored but not signed (or stale) -> AI+1 hard stop
        stub_sidecar(plan, "lecture-plan")
        log.decide("plan_gate", "awaiting-signoff",
                   f"deck_plan.json present but {label} — human must sign (verify.py sign)")
        log.block(f"sign {plan}")
        log.stage("plan", "blocked", label); return False

    # no plan yet -> emit the authoring slot in this mode, stub the sidecar, stop
    todos = starter.read_text().count("TODO")
    p = emit_slot(folder, mode, "01-author-plan", _plan_packet(ch, starter, todos))
    stub_sidecar(starter, "lecture-plan")
    log.decide("plan_gate", "SLOT", f"author deck_plan.json ({todos} TODOs) via {p.name} [{mode}]")
    log.block(str(p))
    log.stage("plan", "blocked", f"author {p.name}"); return False


def stage_deck(ch: Path, folder: Path, log: Log) -> bool:
    plan = folder / "deck_plan.json"
    deck = folder / f"{ch.stem}.dc.html"
    emit = SKILLS / "slide-deck/scripts/emit_deck.py"
    rc, out = sh([sys.executable, str(emit), str(plan), "-o", str(deck),
                  "--assets", str(folder / "assets")])
    if rc != 0 or not deck.exists():
        log.stage("deck", "error", out.strip()[-400:]); return False
    ver = SKILLS / "slide-deck/scripts/verify_deck.py"
    vrc, vout = sh([sys.executable, str(ver), str(deck)])
    log.decide("deck_verify", "pass" if vrc == 0 else "warn",
               vout.strip().splitlines()[-1] if vout.strip() else "")
    log.stage("deck", "ok" if vrc == 0 else "warn", f"{deck.name}")
    return True


def stage_extract(ch: Path, folder: Path, log: Log, mode: str) -> bool:
    """Deck -> beat_sheet.json, then require SIGNED narration (AI+1 GATE, phase
    lecture-narration — the discuss-don't-read gate). The agent may author the
    narration but may NOT sign: a human signs beat_sheet.json before audio spend."""
    deck = folder / f"{ch.stem}.dc.html"
    sheet = folder / "beat_sheet.json"
    rc, out = sh([sys.executable, str(SKILLS / "deck-lecture/scripts/extract_slides.py"),
                  str(deck), "-o", str(folder)])
    if rc != 0 or not sheet.exists():
        log.stage("extract", "error", out.strip()[-400:]); return False

    code, label = sidecar_state(sheet)
    if code == 0:
        log.decide("script_gate", "verified", "narration signed off — using it")
        log.stage("extract", "ok", "verified"); return True

    beats = json.loads(sheet.read_text()).get("beats", [])
    unfilled = [b["beat_id"] for b in beats if not (b.get("narration_text") or "").strip()]
    if unfilled:  # narration not written yet -> emit the slot, stop
        p = emit_slot(folder, mode, "02-author-narration",
                      _narration_packet(folder, beats, unfilled))
        stub_sidecar(sheet, "lecture-narration")
        log.decide("script_gate", "SLOT",
                   f"{len(unfilled)}/{len(beats)} beats need narration via {p.name} [{mode}]")
        log.block(str(p))
        log.stage("extract", "blocked", f"author {p.name}"); return False

    # narration authored but not signed -> AI+1 hard stop for human sign-off
    stub_sidecar(sheet, "lecture-narration")
    log.decide("script_gate", "awaiting-signoff",
               f"all {len(beats)} beats narrated but {label} — human must sign before audio")
    log.block(f"sign {sheet}")
    log.stage("extract", "blocked", label); return False


def stage_script(ch: Path, folder: Path, log: Log):
    guard = SKILLS / "deck-lecture/scripts/script_guard.py"
    rc, out = sh([sys.executable, str(guard), str(folder)])
    flagged = [ln for ln in out.splitlines() if "overlap" in ln.lower() or "flag" in ln.lower()]
    log.decide("discuss_dont_read", f"{len(flagged)} flagged",
               "; ".join(flagged[:6]) or "no beats over the recite threshold")
    audit = SKILLS / "deck-lecture/scripts/tts_audit.py"
    pron = folder / "pronunciations.json"
    sh([sys.executable, str(audit), str(folder), "--seed-dict", str(pron)])
    apply = SKILLS / "deck-lecture/scripts/apply_pronunciations.py"
    arc, aout = sh([sys.executable, str(apply), str(folder)])
    log.decide("pronunciations", "applied" if arc == 0 else "skip",
               aout.strip().splitlines()[-1] if aout.strip() else "")
    log.stage("script", "ok")


def stage_audio(ch: Path, folder: Path, log: Log) -> bool:
    if not os.environ.get("ELEVENLABS_API_KEY"):
        log.decide("audio", "SKIPPED", "no ELEVENLABS_API_KEY — set it and re-run --only audio")
        log.stage("audio", "skip", "no API key"); return False
    gen = ASPECTS / "explainer/bears-doodles/scripts/generate_audio.py"
    rc, out = sh([sys.executable, str(gen), str(folder)])
    ok = (folder / "mp3").is_dir()
    log.decide("audio", "generated" if ok else "error",
               out.strip().splitlines()[-1] if out.strip() else "")
    log.stage("audio", "ok" if ok else "error"); return ok


def stage_captions(ch: Path, folder: Path, log: Log):
    if not (folder / "mp3").is_dir():
        log.decide("captions", "SKIPPED", "no audio yet"); log.stage("captions", "skip"); return
    align = SKILLS / "deck-lecture/scripts/align_captions.py"
    rc, out = sh([sys.executable, str(align), str(folder)])
    ok = (folder / "captions.json").exists()
    log.decide("captions", "aligned" if ok else "skip",
               "faster-whisper forced alignment" if ok else out.strip().splitlines()[-1] if out.strip() else "unavailable")
    log.stage("captions", "ok" if ok else "skip")


def stage_visuals(ch: Path, folder: Path, log: Log):
    rec = SKILLS / "shared/media-router/scripts/recommend.py"
    rc, out = sh([sys.executable, str(rec), str(folder), "--write", "--tag"])
    log.decide("media_router", "wrote render tiers",
               out.strip().splitlines()[-1] if out.strip() else "per-beat medium chosen")
    for tool in ("build_bullets.py", "build_doodle.py"):
        sh([sys.executable, str(SKILLS / "deck-lecture/scripts" / tool), str(folder)])
    log.decide("draft_visuals", "starters",
               "bullets+doodle STARTERS used as draft visuals (hand-upgrade at refinement)")
    log.stage("visuals", "ok")


def stage_scaffold(ch: Path, folder: Path, log: Log):
    deck = folder / f"{ch.stem}.dc.html"
    pre = SKILLS / "deck-lecture/scripts/prerender_deck.py"
    prc, pout = sh([sys.executable, str(pre), str(folder), "--deck", deck.name])
    log.decide("prerender", "ok" if prc == 0 else "skip",
               "deck stills for iframe-free bg" if prc == 0 else "playwright unavailable — live iframe fallback")
    scaf = SKILLS / "deck-lecture/scripts/scaffold_remotion.py"
    src, sout = sh([sys.executable, str(scaf), str(folder), "--deck", deck.name])
    ok = (folder / "remotion").is_dir()
    log.decide("scaffold", "ok" if ok else "error",
               sout.strip().splitlines()[-1] if sout.strip() else "")
    log.stage("scaffold", "ok" if ok else "error")


def stage_qc(ch: Path, folder: Path, log: Log):
    checks, score = [], 0

    def add(name, ok, weight, detail=""):
        nonlocal score
        checks.append({"check": name, "pass": bool(ok), "weight": weight, "detail": detail})
        if ok:
            score += weight

    deck = folder / f"{ch.stem}.dc.html"
    add("deck emitted", deck.exists(), 10)
    ver = SKILLS / "slide-deck/scripts/verify_deck.py"
    vrc, _ = sh([sys.executable, str(ver), str(deck)]) if deck.exists() else (1, "")
    add("deck verify pass", vrc == 0, 15)

    sheet = folder / "beat_sheet.json"
    beats = json.loads(sheet.read_text()).get("beats", []) if sheet.exists() else []
    add("beat sheet present", bool(beats), 10, f"{len(beats)} beats")
    narrated = [b for b in beats if (b.get("narration_text") or "").strip()]
    add("all beats narrated", beats and len(narrated) == len(beats), 15,
        f"{len(narrated)}/{len(beats)}")

    pace = SKILLS / "shared/pacing/scripts/pace_check.py"
    prc, pout = sh([sys.executable, str(pace), str(folder)]) if beats else (1, "")
    add("pacing check", prc == 0, 10, (pout.strip().splitlines()[-1] if pout.strip() else "")[:120])

    audio_ok = (folder / "mp3").is_dir()
    add("audio present", audio_ok, 15, "master clock locked" if audio_ok else "no audio")
    add("captions aligned", (folder / "captions.json").exists(), 10)
    add("remotion scaffolded", (folder / "remotion").is_dir(), 10)

    # duration sanity: total narrated runtime, if measured
    durs = [b.get("actual_duration_s") for b in beats if b.get("actual_duration_s")]
    total = round(sum(d for d in durs if d), 1) if durs else 0
    report = {"chapter": folder.name, "score": score, "max": 100,
              "runtime_s": total, "beats": len(beats),
              "checks": checks,
              "blocked_on": log.data.get("blocked_on"),
              "verdict": ("watchable-draft" if score >= 70 else
                          "needs-work" if score >= 40 else "incomplete")}
    (folder / "qc_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    log.decide("qc", f"{score}/100 · {report['verdict']}", f"runtime {total}s over {len(beats)} beats")
    log.stage("qc", "ok", f"{score}/100")
    return report


# ─────────────────────────── agent-slot packets ─────────────────────────────
def _plan_packet(ch: Path, starter: Path, todos: int) -> str:
    return f"""# AGENT SLOT 1 — author the deck plan

**Chapter:** `{ch}`
**Starter:** `{starter.name}` ({todos} TODOs)
**Write:** `deck_plan.json` in this folder with every `TODO:` replaced. No TODO may remain.

The starter has the correct slide SKELETON (title, section dividers, concept/equation/
figure slides, close). Your job is the judgement a regex can't do:
- headlines that make a claim, not restate the heading
- speaker_notes that will become the narration seed (2-4 sentences, teach don't recite)
- bind figure/chart slides to a pool asset id from `assets/assets.json` where one fits
- drop slides that shouldn't be in a lecture; merge thin ones

Read the chapter and the starter, then emit the finished `deck_plan.json`.
When done, re-run: `silent_run.py <book> --chapter {ch.stem} --from deck`
"""


def _narration_packet(folder: Path, beats: list[dict], unfilled: list[str]) -> str:
    lines = [f"# AGENT SLOT 2 — write narration for {folder.name}",
             "",
             f"{len(unfilled)} of {len(beats)} beats need `narration_text`. Rule: **discuss the",
             "slide, don't read it** — expand each beat's `speaker_notes` into spoken teaching",
             "voice. Write back into `beat_sheet.json` (field `narration_text` per beat).",
             ""]
    for b in beats:
        if b["beat_id"] in unfilled:
            note = (b.get("speaker_notes") or "").strip()
            on = (b.get("on_slide_text") or "").strip()[:160]
            lines += [f"## {b['beat_id']} — {b.get('label','')}",
                      f"- on-slide: {on}",
                      f"- notes seed: {note}", ""]
    lines.append("When done, re-run: `silent_run.py <book> --chapter … --from script`")
    return "\n".join(lines)


# ─────────────────────────── driver ─────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Silent-mode rough-draft lecture builder (one chapter).")
    ap.add_argument("book", help="book dir (has chapters/ and images/)")
    ap.add_argument("--chapter", required=True, help="chapter stem, e.g. 02-... (or number)")
    ap.add_argument("--out", default=None, help="lecture folder (default: <book>/lectures/<stem>)")
    ap.add_argument("--runtime", default=None, help="dir with support.js/deck-stage.js/_ds to copy")
    ap.add_argument("--from", dest="start", choices=STAGES, default="setup")
    ap.add_argument("--only", nargs="*", choices=STAGES, help="run only these stages")
    ap.add_argument("--mode", choices=["agent", "api", "handoff"], default="agent",
                    help="how the two LLM gates (plan, narration) are filled — AI+1 modes. "
                         "Deterministic bookkeeping is identical across all three.")
    args = ap.parse_args()

    book = Path(args.book).expanduser().resolve()
    chdir = book / "chapters"
    matches = sorted(p for p in chdir.glob("*.md")
                     if p.stem == args.chapter or p.stem.startswith(args.chapter)
                     or re.match(rf"0*{re.escape(args.chapter)}\b", p.stem))
    if not matches:
        sys.exit(f"[err] no chapter matching '{args.chapter}' in {chdir}")
    ch = matches[0]
    folder = Path(args.out).expanduser().resolve() if args.out else book / "lectures" / ch.stem
    images = book / "images" if (book / "images").is_dir() else None
    runtime = Path(args.runtime).expanduser().resolve() if args.runtime else None

    folder.mkdir(parents=True, exist_ok=True)
    log = Log(folder)
    log.data["mode"] = args.mode
    print(f"[silent] {ch.name}  ->  {folder}  (mode={args.mode})")

    run = set(args.only) if args.only else set(STAGES[STAGES.index(args.start):])
    # gated stages return False to halt the run cleanly at an agent slot
    order = [
        ("setup",    lambda: (stage_setup(ch, folder, runtime, log), True)[1]),
        ("assets",   lambda: (stage_assets(ch, folder, images, log), True)[1]),
        ("plan",     lambda: stage_plan(ch, folder, log, args.mode)),
        ("deck",     lambda: stage_deck(ch, folder, log)),
        ("extract",  lambda: stage_extract(ch, folder, log, args.mode)),
        ("script",   lambda: (stage_script(ch, folder, log), True)[1]),
        ("audio",    lambda: (stage_audio(ch, folder, log), True)[1]),
        ("captions", lambda: (stage_captions(ch, folder, log), True)[1]),
        ("visuals",  lambda: (stage_visuals(ch, folder, log), True)[1]),
        ("scaffold", lambda: (stage_scaffold(ch, folder, log), True)[1]),
        ("qc",       lambda: (stage_qc(ch, folder, log), True)[1]),
    ]
    for name, fn in order:
        if name not in run:
            continue
        print(f"[silent] stage: {name}")
        cont = fn()
        if cont is False:
            write_status(folder, args.mode, log)
            print(f"[silent] halted at gate after '{name}'. Next: {log.data.get('blocked_on')}")
            print(f"[silent] STATUS: {folder/'STATUS.md'} · trail: {log.path}")
            return
    write_status(folder, args.mode, log)
    # always emit QC if we finished the chain
    if "qc" in run:
        rep = json.loads((folder / "qc_report.json").read_text())
        print(f"[silent] QC {rep['score']}/100 · {rep['verdict']} · {rep['runtime_s']}s")
    print(f"[silent] STATUS: {folder/'STATUS.md'} · trail: {log.path}")


if __name__ == "__main__":
    main()
