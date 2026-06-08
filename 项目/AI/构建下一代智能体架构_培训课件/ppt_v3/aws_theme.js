// AWS-style theme + helpers for Harness Engineering decks (16:9 WIDE)
const pptxgen = require("pptxgenjs");

const C = {
  DARK: "232F3E",   // Squid Ink
  INK: "16191F",
  ORANGE: "FF9900", // Smile
  BLUE: "146EB4",
  GRAY: "5F6B7A",
  LINE: "D5DBDB",
  LIGHT: "F2F3F3",
  WHITE: "FFFFFF",
  GREEN: "1D8102",
  RED: "D13212",
};
const FONT = "PingFang SC";
const MONO = "Menlo";
const W = 13.33, H = 7.5;
let MODULE = "01 Opening";
function setModule(label) { MODULE = label; }

function newDeck(title) {
  const p = new pptxgen();
  p.defineLayout({ name: "W", width: W, height: H });
  p.layout = "W";
  p.author = "Harness Engineering";
  p.title = title;
  return p;
}

// dark full-bleed slide (cover / divider / transition)
function darkSlide(p) {
  const s = p.addSlide();
  s.background = { color: C.DARK };
  s.addShape(p.shapes.RECTANGLE, { x: 0.6, y: 0.6, w: 0.55, h: 0.16, fill: { color: C.ORANGE } });
  return s;
}

// light content slide with title chrome + footer. Returns slide.
function contentSlide(p, n, total, title, eyebrow) {
  const s = p.addSlide();
  s.background = { color: C.WHITE };
  s.addShape(p.shapes.RECTANGLE, { x: 0.6, y: 0.55, w: 0.16, h: 0.62, fill: { color: C.ORANGE } });
  let ty = 0.5;
  if (eyebrow) {
    s.addText(eyebrow.toUpperCase(), { x: 0.92, y: 0.46, w: 11.5, h: 0.3, fontFace: FONT, fontSize: 11, bold: true, color: C.ORANGE, charSpacing: 2, margin: 0 });
    ty = 0.74;
  }
  s.addText(title, { x: 0.92, y: ty, w: 11.7, h: 0.62, fontFace: FONT, fontSize: 24, bold: true, color: C.INK, margin: 0, valign: "top" });
  // footer
  s.addShape(p.shapes.LINE, { x: 0.6, y: 7.02, w: 12.13, h: 0, line: { color: C.LINE, width: 1 } });
  s.addText("Harness Engineering  ·  " + MODULE, { x: 0.6, y: 7.06, w: 8, h: 0.3, fontFace: FONT, fontSize: 9, color: C.GRAY, margin: 0 });
  s.addText(`${n} / ${total}`, { x: 10.73, y: 7.06, w: 2, h: 0.3, fontFace: FONT, fontSize: 9, color: C.GRAY, align: "right", margin: 0 });
  return s;
}

function bullets(items, opts = {}) {
  return items.map((it, i) => {
    const o = typeof it === "object" ? it : { text: it };
    return {
      text: o.text,
      options: Object.assign(
        { bullet: { code: "2022", indent: 14 }, breakLine: true, fontFace: FONT, fontSize: opts.fontSize || 14, color: opts.color || C.INK, paraSpaceAfter: opts.gap != null ? opts.gap : 8, indentLevel: o.lvl || 0 },
        o.opt || {}
      ),
    };
  });
}

function styledTable(p, s, rows, opts) {
  s.addTable(rows, Object.assign({
    border: { type: "solid", pt: 0.5, color: C.LINE },
    fontFace: FONT, fontSize: 12, color: C.INK, valign: "middle", align: "left",
    autoPage: false,
  }, opts));
}
// header cell helper
const hc = (t) => ({ text: t, options: { fill: { color: C.DARK }, color: C.WHITE, bold: true, align: "left", fontFace: FONT } });

// dark code / ASCII box (monospace). lines: string or array of {text,opt}
function codeBox(p, s, lines, opts) {
  const o = Object.assign({ x: 0.92, y: 1.7, w: 11.5, h: 4.0, fontSize: 11 }, opts);
  s.addShape(p.shapes.RECTANGLE, { x: o.x, y: o.y, w: o.w, h: o.h, fill: { color: "1B2530" } });
  const arr = Array.isArray(lines)
    ? lines.map((l, i) => (typeof l === "object" ? { text: l.text, options: Object.assign({ breakLine: true, color: l.color || "D5DBDB" }, l.opt || {}) } : { text: l, options: { breakLine: true, color: "D5DBDB" } }))
    : [{ text: lines }];
  s.addText(arr, { x: o.x + 0.2, y: o.y + 0.12, w: o.w - 0.4, h: o.h - 0.24, fontFace: MONO, fontSize: o.fontSize, color: "D5DBDB", valign: "top", lineSpacingMultiple: 1.08 });
}

module.exports = { pptxgen, C, FONT, MONO, W, H, newDeck, darkSlide, contentSlide, bullets, styledTable, hc, setModule, codeBox };
