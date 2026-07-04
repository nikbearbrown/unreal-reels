// ProgressiveFigure.tsx — reveal an AUTHORED figure's parts in sync with the
// narration, so a rich diagram is USED (not replaced by bullets) and never sits
// fully static. The SVG is authored with reveal groups: any element wrapped in
// <g class="pf pf-N"> starts hidden and fades in at its turn. Anything without a
// pf class (the header bar, title) is visible from the first frame.
//
// Group k appears on the k-th evenly-spaced narration line, so an N-part figure
// spreads its reveals across the whole spoken slide. No rasterization, no DOM
// mutation: a single computed <style> sets each group's opacity for the frame.
// The style is SCOPED to this slide (a unique class) so stacked figure slides in
// one composition can't clobber each other's `.pf-*` rules.
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { EASE, ENTER } from "./tokens";
import type { CaptionLine } from "./Captions";

export type FigureSpec = { svg: string; groups: number; title?: string };

const groupAppear = (k: number, G: number, lines: CaptionLine[]) => {
  if (lines.length > 0 && G > 1) {
    const li = Math.round((k * (lines.length - 1)) / (G - 1));
    const ln = lines[Math.min(li, lines.length - 1)];
    return ln ? ln.startFrame : 0;
  }
  return 0;
};

export const ProgressiveFigure: React.FC<{
  spec: FigureSpec;
  lines: CaptionLine[];
  scope: string; // unique per slide (beat_id) so .pf-* rules don't leak across slides
}> = ({ spec, lines, scope }) => {
  const frame = useCurrentFrame();
  const G = Math.max(1, spec.groups);
  const cls = `pffig-${scope}`;
  const rules = Array.from({ length: G }, (_, k) => {
    const app = groupAppear(k, G, lines);
    const o = interpolate(frame - app, [0, ENTER], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: EASE,
    });
    return `.${cls} .pf-${k}{opacity:${o.toFixed(3)};}`;
  }).join("");
  const css = `.${cls} .pf{opacity:0;} ${rules} .${cls} svg{max-width:100%;max-height:100%;width:auto;height:auto;display:block;}`;

  return (
    <AbsoluteFill style={{ background: "#fff", justifyContent: "center", alignItems: "center", padding: "48px 90px" }}>
      <style>{css}</style>
      <div
        className={cls}
        style={{ width: "100%", height: "100%", display: "flex", justifyContent: "center", alignItems: "center" }}
        dangerouslySetInnerHTML={{ __html: spec.svg }}
      />
    </AbsoluteFill>
  );
};
