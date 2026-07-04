// Bullets.tsx — the text-heavy fallback. When a slide has no D3 chart and no
// authored doodle, we don't stare at it: after the live hold, the slide's key
// points animate in as bullets, one per narration line. Deck typography (Lato),
// NU-red dash markers — matches the deck, not a separate "doodle" style.
//
// BASIC RULE this enforces: nothing on screen stays static for long. Points arrive
// in step with the narration (one per timed line). To allow a reveal every few
// seconds on a long slide WITHOUT the screen becoming a wall of text, we show a
// SLIDING WINDOW of the most recent points — older ones fade out as new ones
// arrive. So a 60-second slide can have a dozen reveals and never show more than
// WINDOW at once.
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { OVERLAY_FONT as fontFamily } from "./fonts";
import { COLORS, EASE, ENTER, FONTS, NUM_RE } from "./tokens";
import type { CaptionLine } from "./Captions";

const NU_RED = COLORS.red;
const INK = COLORS.ink;
const PAST = COLORS.secondary;

// how many points stay visible at once (the rest have faded off the top)
const WINDOW = 6;

export type Bullet = { text: string; atLine?: number; atFrac?: number };
export type BulletSpec = { title?: string; bullets: Bullet[] };

// set numeric tokens (60%, 0.8, 0.6/0.3) in mono so data reads as data
const withMonoNumbers = (text: string) =>
  text.split(NUM_RE).map((part, i) =>
    NUM_RE.test(part) ? (
      <span key={i} style={{ fontFamily: FONTS.mono, fontSize: "0.92em" }}>{part}</span>
    ) : (
      <span key={i}>{part}</span>
    )
  );

const appearFrame = (b: Bullet, lines: CaptionLine[], hold: number, phase: number, i: number, n: number) => {
  if (b.atLine != null && lines.length > 0) {
    const ln = lines[Math.min(b.atLine, lines.length - 1)];
    return Math.max(0, (ln ? ln.startFrame : 0) - hold);
  }
  if (b.atFrac != null) return Math.round(b.atFrac * phase);
  return Math.round(((i + 0.5) / Math.max(1, n)) * phase); // even stagger
};

export const Bullets: React.FC<{
  spec: BulletSpec;
  lines: CaptionLine[];
  holdFrames: number;
  phaseFrames: number;
}> = ({ spec, lines, holdFrames, phaseFrames }) => {
  const frame = useCurrentFrame();
  const items = spec.bullets;
  const n = items.length;
  const appears = items.map((b, i) => appearFrame(b, lines, holdFrames, phaseFrames, i, n));
  let current = -1;
  for (let i = 0; i < appears.length; i++) if (appears[i] <= frame) current = i;

  // sliding window: render the newest WINDOW revealed points; the one just below
  // the window fades out as the newest fades in, so there's no hard pop.
  const windowStart = Math.max(0, current - (WINDOW - 1));
  const exiting = windowStart - 1; // index leaving the window (may be -1)

  const size = 50;
  const gap = 32;

  return (
    <AbsoluteFill style={{ background: "#fff", fontFamily, padding: "104px 130px", justifyContent: "flex-start" }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 10, background: NU_RED }} />
      {spec.title ? (
        <>
          <div style={{ fontSize: 66, fontWeight: 400, color: INK, letterSpacing: "-0.01em", maxWidth: 1560 }}>
            {withMonoNumbers(spec.title)}
          </div>
          <div style={{ width: 96, height: 6, background: NU_RED, margin: "24px 0 48px" }} />
        </>
      ) : null}
      <div style={{ display: "flex", flexDirection: "column", gap, maxWidth: 1560 }}>
        {items.map((b, i) => {
          if (i < exiting || i > current) return null;      // outside the window
          const local = frame - appears[i];
          const oIn = interpolate(local, [0, ENTER], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });
          // fade the exiting item out in lockstep with the newest fading in
          let o = oIn;
          if (i === exiting && exiting >= 0) {
            const newest = frame - appears[current];
            const oOut = interpolate(newest, [0, ENTER], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });
            o = oOut;
          }
          if (o <= 0.001) return null;
          const isCurrent = i === current;
          return (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 28,
                opacity: o,
                transform: `translateX(${(1 - oIn) * -36}px)`,
              }}
            >
              <div style={{ width: 38, height: 6, background: isCurrent ? NU_RED : PAST, marginTop: size * 0.5, flex: "0 0 auto" }} />
              <div
                style={{
                  fontSize: size,
                  lineHeight: 1.28,
                  fontWeight: isCurrent ? 700 : 400,
                  color: isCurrent ? INK : PAST,
                }}
              >
                {withMonoNumbers(b.text)}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
