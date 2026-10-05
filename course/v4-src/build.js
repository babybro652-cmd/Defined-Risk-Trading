const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const path = require("path");
const { MdOutlineMonitor, MdWarningAmber } = require("react-icons/md");
const { applyTheme } = require("/root/.claude/skills/synced/f6c69b0d-2994-409e-b556-64c0f0a73413_558c0509-a0f0-4e18-bd03-3cd6af8c0033/pptx/scripts/apply_theme.js");
const { M4, M5 } = require("./content.js");

const K = { ink: "111111", white: "FFFFFF", gray: "6E6E6E", lgray: "A8A8A8", panel: "F2F2F2", orange: "E8912D", blue: "2A6FDB", dpanel: "1E1E1E", red: "C0392B" };
const HF = "Arial", BF = "Calibri";
const W = 13.333, H = 7.5, MX = 0.7;

const THEME = {
  name: "DRT Course",
  headFontFace: HF, bodyFontFace: BF,
  colors: { dk1: K.ink, lt1: K.white, dk2: "333333", lt2: K.panel, accent1: K.orange, accent2: K.blue, accent3: "1A9E5F", accent4: "D94141", accent5: K.gray, accent6: "8E8E8E", hlink: K.blue, folHlink: K.gray },
};

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

function T(slide, text, o) { slide.addText(text, Object.assign({ isTextBox: true, fontFace: BF, margin: 0, valign: "top" }, o)); }

async function build(M) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.theme = { headFontFace: HF, bodyFontFace: BF };
  pres.title = `${M.module}: ${M.name}`;
  pres.author = "Defined Risk Trading";
  const monitor = await icon(MdOutlineMonitor, K.orange);
  const warn = await icon(MdWarningAmber, K.orange);

  const footer = (dark, lessonId) => {
    const objs = [];
    return objs;
  };
  pres.defineSlideMaster({ title: "DRT_DARK", background: { color: K.ink }, objects: [] , slideNumber: { x: W - 1.2, y: H - 0.5, w: 0.6, h: 0.3, fontFace: BF, fontSize: 11, color: K.gray, align: "right" } });
  pres.defineSlideMaster({ title: "DRT_LIGHT", background: { color: K.white }, objects: [] , slideNumber: { x: W - 1.2, y: H - 0.5, w: 0.6, h: 0.3, fontFace: BF, fontSize: 11, color: K.lgray, align: "right" } });

  const lessonTitle = (id) => M.lessons[id];
  const foot = (s, dark, lesson) => {
    const c = dark ? K.gray : K.lgray;
    T(s, "Defined Risk Trading", { x: MX, y: H - 0.5, w: 4, h: 0.3, fontSize: 11, color: c });
    if (lesson && M.lessons[lesson]) T(s, `${M.module}  •  LESSON ${lesson}`, { x: W - 6.0, y: H - 0.5, w: 4.6, h: 0.3, fontSize: 11, color: c, align: "right" });
  };
  const head = (s, label, title, dark, labelColor) => {
    T(s, label, { x: MX, y: 0.45, w: 6, h: 0.35, fontSize: 14, bold: true, charSpacing: 4, color: labelColor || K.orange, fontFace: HF });
    T(s, title, { x: MX, y: 0.85, w: W - 2 * MX, h: 0.9, fontSize: 36, bold: true, color: dark ? K.white : K.ink, fontFace: HF, valign: "middle", fit: "none" });
  };

  for (const d of M.slides) {
    const dark = ["title", "divider", "do", "live", "recap", "disclaimer", "agenda"].includes(d.kind);
    const s = pres.addSlide({ masterName: dark ? "DRT_DARK" : "DRT_LIGHT" });
    s.addNotes(d.say);
    const L = d.lesson;

    switch (d.kind) {
      case "title": {
        T(s, "DEFINED RISK TRADING", { x: MX, y: 0.6, w: 6, h: 0.4, fontSize: 16, bold: true, charSpacing: 4, color: K.white, fontFace: HF });
        T(s, d.module, { x: MX, y: 2.2, w: 6, h: 0.5, fontSize: 20, bold: true, charSpacing: 6, color: K.orange, fontFace: HF });
        T(s, d.title, { x: MX, y: 2.8, w: 11, h: 2.2, fontSize: 54, bold: true, color: K.white, fontFace: HF });
        T(s, d.sub, { x: MX, y: 5.2, w: 12, h: 0.6, fontSize: 24, italic: true, color: K.lgray });
        break;
      }
      case "disclaimer": {
        s.addImage({ data: warn, x: MX, y: 0.55, w: 0.7, h: 0.7 });
        T(s, d.title, { x: MX + 0.95, y: 0.55, w: 10, h: 0.7, fontSize: 36, bold: true, color: K.white, fontFace: HF, valign: "middle" });
        T(s, "RISK DISCLAIMER", { x: MX + 0.95, y: 0.25, w: 6, h: 0.3, fontSize: 13, bold: true, charSpacing: 4, color: K.orange, fontFace: HF });
        const runs = d.lines.map((l, i) => ({ text: l, options: { bullet: { indent: 24 }, breakLine: i < d.lines.length - 1, paraSpaceAfter: 18 } }));
        T(s, runs, { x: MX, y: 1.8, w: W - 2 * MX, h: 4.6, fontSize: 26, color: K.white });
        foot(s, true, null);
        break;
      }
      case "agenda": {
        head(s, M.module, d.title, true);
        const ids = Object.keys(M.lessons);
        const two = ids.length > 4;
        const per = two ? Math.ceil(ids.length / 2) : ids.length;
        const colW = two ? 5.8 : 11;
        ids.forEach((id, i) => {
          const col = two ? Math.floor(i / per) : 0, row = two ? i % per : i;
          const x = MX + col * 6.1, y = 2.0 + row * (two ? 1.35 : 1.15);
          const bh = two ? 1.1 : 0.95;
          s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: colW, h: bh, fill: { color: K.dpanel }, rectRadius: 0.08, line: { color: K.dpanel } });
          T(s, id, { x: x + 0.3, y, w: 1.0, h: bh, fontSize: 26, bold: true, color: K.orange, fontFace: HF, valign: "middle" });
          T(s, M.lessons[id], { x: x + 1.35, y, w: colW - 1.55, h: bh, fontSize: 22, color: K.white, valign: "middle" });
        });
        foot(s, true, null);
        break;
      }
      case "divider": {
        T(s, `LESSON ${L}`, { x: MX, y: 2.6, w: 8, h: 0.5, fontSize: 22, bold: true, charSpacing: 6, color: K.orange, fontFace: HF });
        T(s, lessonTitle(L), { x: MX, y: 3.2, w: 11.5, h: 1.4, fontSize: 48, bold: true, color: K.white, fontFace: HF });
        foot(s, true, L);
        break;
      }
      case "statement": {
        head(s, d.label, d.title, false);
        s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 2.0, w: W - 2 * MX, h: 3.0, fill: { color: K.panel }, line: { color: K.panel }, rectRadius: 0.08 });
        T(s, d.big, { x: MX + 0.5, y: 2.0, w: W - 2 * MX - 1.0, h: 3.0, fontSize: 36, bold: true, color: K.ink, valign: "middle" });
        if (d.sub) T(s, d.sub, { x: MX, y: 5.3, w: W - 2 * MX, h: 1.0, fontSize: 24, color: K.gray });
        foot(s, false, L);
        break;
      }
      case "cards": {
        head(s, d.label, d.title, false);
        const n = d.cards.length, gap = 0.4, cw = (W - 2 * MX - gap * (n - 1)) / n;
        const ch = d.note ? 3.6 : 4.2;
        d.cards.forEach((c, i) => {
          const x = MX + i * (cw + gap), y = 2.0;
          const col = c.color === "blue" ? K.blue : K.orange;
          s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, fill: { color: K.panel }, line: { color: K.panel }, rectRadius: 0.08 });
          T(s, c.head, { x: x + 0.4, y: y + 0.35, w: cw - 0.8, h: 0.45, fontSize: 20, bold: true, charSpacing: 2, color: col, fontFace: HF });
          if (c.big) {
            T(s, c.big, { x: x + 0.4, y: y + 1.0, w: cw - 0.8, h: 1.2, fontSize: n === 3 ? 30 : 36, bold: true, color: K.ink, fontFace: HF, valign: "middle" });
            T(s, c.body, { x: x + 0.4, y: y + 2.4, w: cw - 0.8, h: ch - 2.6, fontSize: 22, color: K.gray });
          } else {
            T(s, c.body, { x: x + 0.4, y: y + 1.0, w: cw - 0.8, h: ch - 1.3, fontSize: 26, color: K.ink });
          }
        });
        if (d.note) T(s, d.note, { x: MX, y: 5.95, w: W - 2 * MX, h: 0.6, fontSize: 24, bold: true, color: K.ink });
        foot(s, false, L);
        break;
      }
      case "compare": {
        head(s, d.label, d.title, false);
        const cw = 5.6, y = 2.2, ch = 3.6;
        [[d.left, K.blue, MX], [d.right, K.orange, W - MX - cw]].forEach(([c, col, x]) => {
          s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, fill: { color: K.panel }, line: { color: K.panel }, rectRadius: 0.08 });
          T(s, c.head, { x: x + 0.4, y: y + 0.4, w: cw - 0.8, h: 0.5, fontSize: 22, bold: true, charSpacing: 2, color: col, fontFace: HF });
          T(s, c.body, { x: x + 0.4, y: y + 1.2, w: cw - 0.8, h: 2.1, fontSize: 34, bold: true, color: K.ink, fontFace: HF });
        });
        s.addShape(pres.shapes.RIGHT_ARROW, { x: W / 2 - 0.45, y: y + ch / 2 - 0.35, w: 0.9, h: 0.7, fill: { color: K.ink }, line: { color: K.ink } });
        foot(s, false, L);
        break;
      }
      case "steps": {
        head(s, d.label, d.title, false);
        d.steps.forEach((t, i) => {
          const y = 2.05 + i * 1.45;
          s.addShape(pres.shapes.OVAL, { x: MX, y: y + 0.1, w: 0.8, h: 0.8, fill: { color: K.orange }, line: { color: K.orange } });
          T(s, String(i + 1), { x: MX, y: y + 0.1, w: 0.8, h: 0.8, fontSize: 28, bold: true, color: K.white, align: "center", valign: "middle", fontFace: HF });
          s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX + 1.1, y, w: W - 2 * MX - 1.1, h: 1.0, fill: { color: K.panel }, line: { color: K.panel }, rectRadius: 0.06 });
          T(s, t, { x: MX + 1.4, y, w: W - 2 * MX - 1.6, h: 1.0, fontSize: 24, color: K.ink, valign: "middle" });
        });
        foot(s, false, L);
        break;
      }
      case "checklist": {
        head(s, d.label, d.title, false);
        d.steps.forEach((t, i) => {
          const y = 1.95 + i * 0.68;
          s.addShape(pres.shapes.OVAL, { x: MX, y: y + 0.04, w: 0.52, h: 0.52, fill: { color: K.ink }, line: { color: K.ink } });
          T(s, String(i + 1), { x: MX, y: y + 0.04, w: 0.52, h: 0.52, fontSize: 20, bold: true, color: K.white, align: "center", valign: "middle", fontFace: HF });
          T(s, t, { x: MX + 0.8, y, w: W - 2 * MX - 0.8, h: 0.6, fontSize: 26, color: i === 4 ? K.ink : K.ink, bold: false, valign: "middle" });
        });
        foot(s, false, L);
        break;
      }
      case "flow": {
        head(s, d.label, d.title, false);
        const n = d.boxes.length, gap = 0.7, bw = (W - 2 * MX - gap * (n - 1)) / n, y = 2.1, bh = 3.2;
        d.boxes.forEach((b, i) => {
          const x = MX + i * (bw + gap);
          s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, fill: { color: K.panel }, line: { color: K.panel }, rectRadius: 0.08 });
          T(s, b.head, { x: x + 0.3, y: y + 0.35, w: bw - 0.6, h: 0.5, fontSize: 20, bold: true, charSpacing: 2, color: K.orange, fontFace: HF });
          T(s, b.body, { x: x + 0.3, y: y + 1.05, w: bw - 0.6, h: bh - 1.3, fontSize: 28, bold: true, color: K.ink, fontFace: BF });
          if (i < n - 1) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + bw + 0.12, y: y + bh / 2 - 0.23, w: gap - 0.24, h: 0.46, fill: { color: K.ink }, line: { color: K.ink } });
        });
        if (d.note) T(s, d.note, { x: MX, y: 5.75, w: W - 2 * MX, h: 0.7, fontSize: 24, color: K.gray });
        foot(s, false, L);
        break;
      }
      case "flowsteps": {
        head(s, d.label, d.title, false);
        const cols = 3, gap = 0.35, bw = (W - 2 * MX - gap * (cols - 1)) / cols, bh = 1.6;
        d.steps.forEach((t, i) => {
          const x = MX + (i % cols) * (bw + gap), y = 2.0 + Math.floor(i / cols) * (bh + 0.3);
          const last = i === d.steps.length - 1;
          s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, fill: { color: last ? K.ink : K.panel }, line: { color: last ? K.ink : K.panel }, rectRadius: 0.08 });
          T(s, String(i + 1), { x: x + 0.3, y, w: 0.6, h: bh, fontSize: 36, bold: true, color: K.orange, fontFace: HF, valign: "middle" });
          T(s, t, { x: x + 1.0, y, w: bw - 1.2, h: bh, fontSize: 24, bold: true, color: last ? K.white : K.ink, valign: "middle" });
        });
        T(s, "One process, not five separate tools.", { x: MX, y: 5.75, w: W - 2 * MX, h: 0.6, fontSize: 26, color: K.gray });
        foot(s, false, L);
        break;
      }
      case "stats":
      case "bigstat": {
        head(s, d.label, d.title, false);
        if (d.kind === "bigstat") {
          s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 2.0, w: W - 2 * MX, h: 3.0, fill: { color: K.panel }, line: { color: K.panel }, rectRadius: 0.08 });
          T(s, d.num, { x: MX, y: 2.2, w: W - 2 * MX, h: 1.8, fontSize: 96, bold: true, color: K.orange, fontFace: HF, align: "center", valign: "middle" });
          T(s, d.label2, { x: MX, y: 4.0, w: W - 2 * MX, h: 0.7, fontSize: 28, color: K.ink, align: "center" });
          T(s, d.sub, { x: MX, y: 5.35, w: W - 2 * MX, h: 0.9, fontSize: 24, color: K.gray });
        } else {
          const n = d.stats.length, gap = 0.4, cw = (W - 2 * MX - gap * (n - 1)) / n, ch = d.note ? 3.5 : 4.0;
          d.stats.forEach((st, i) => {
            const x = MX + i * (cw + gap), y = 2.0;
            s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, fill: { color: K.panel }, line: { color: K.panel }, rectRadius: 0.08 });
            const fs = st.num.length > 7 ? 36 : 54;
            T(s, st.num, { x: x + 0.25, y: y + 0.3, w: cw - 0.5, h: 1.3, fontSize: fs, bold: true, color: K.orange, fontFace: HF, align: "center", valign: "middle" });
            T(s, st.label, { x: x + 0.3, y: y + 1.75, w: cw - 0.6, h: ch - 1.9, fontSize: 22, color: K.ink, align: "center" });
          });
          if (d.note) T(s, d.note, { x: MX, y: 5.85, w: W - 2 * MX, h: 0.7, fontSize: 24, bold: true, color: K.ink });
        }
        foot(s, false, L);
        break;
      }
      case "equation": {
        head(s, d.label, d.title, false);
        const n = d.parts.length + 1, op = 0.6, bw = (W - 2 * MX - op * (n - 1)) / n, y = 2.3, bh = 1.8;
        const all = [...d.parts, d.result];
        all.forEach((p, i) => {
          const x = MX + i * (bw + op);
          const last = i === all.length - 1;
          s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, fill: { color: last ? K.ink : K.panel }, line: { color: last ? K.ink : K.panel }, rectRadius: 0.08 });
          T(s, p, { x: x + 0.15, y, w: bw - 0.3, h: bh, fontSize: 26, bold: true, color: last ? K.white : K.ink, align: "center", valign: "middle", fontFace: HF });
          if (!last) T(s, i === all.length - 2 ? "=" : "÷", { x: x + bw, y, w: op, h: bh, fontSize: 40, bold: true, color: K.orange, align: "center", valign: "middle", fontFace: HF });
        });
        T(s, d.example, { x: MX, y: 4.6, w: W - 2 * MX, h: 0.7, fontSize: 28, color: K.ink, bold: true });
        T(s, "That's the formula professional sizing is built on. Next slide: what you'll use.", { x: MX, y: 5.5, w: W - 2 * MX, h: 0.8, fontSize: 22, color: K.gray });
        foot(s, false, L);
        break;
      }
      case "options": {
        head(s, d.label, d.title, false);
        const cw = 5.75, y = 1.95, ch = 3.75;
        [[d.a, K.blue, MX], [d.b, K.orange, W - MX - cw]].forEach(([o, col, x]) => {
          s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, fill: { color: K.panel }, line: { color: K.panel }, rectRadius: 0.08 });
          T(s, o.head, { x: x + 0.4, y: y + 0.3, w: 2.6, h: 0.5, fontSize: 20, bold: true, charSpacing: 2, color: col, fontFace: HF });
          T(s, o.big, { x: x + 3.0, y: y + 0.2, w: cw - 3.4, h: 0.7, fontSize: 36, bold: true, color: K.ink, fontFace: HF, align: "right" });
          const runs = o.lines.map((l, i) => ({ text: l, options: { bullet: { indent: 20 }, breakLine: i < o.lines.length - 1, paraSpaceAfter: 10 } }));
          T(s, runs, { x: x + 0.4, y: y + 1.15, w: cw - 0.8, h: ch - 1.35, fontSize: 24, color: K.ink });
        });
        T(s, d.note, { x: MX, y: 5.95, w: W - 2 * MX, h: 0.6, fontSize: 24, bold: true, color: K.ink });
        foot(s, false, L);
        break;
      }
      case "table": {
        head(s, d.label, d.title, false);
        const colW = [4.6, 3.0, W - 2 * MX - 7.6], rh = [0.75, 1.1, 1.1];
        let y = 2.0;
        d.rows.forEach((r, ri) => {
          let x = MX;
          s.addShape(pres.shapes.RECTANGLE, { x: MX, y, w: W - 2 * MX, h: rh[ri], fill: { color: ri === 0 ? K.ink : (ri === 1 ? K.panel : "E6E6E6") }, line: { color: K.white, width: 1 } });
          r.forEach((c, ci) => {
            T(s, c, { x: x + 0.3, y, w: colW[ci] - 0.6, h: rh[ri], fontSize: ri === 0 ? 20 : 30, bold: ri === 0 || ci === 0 || ci === 2, color: ri === 0 ? K.white : (ci === 2 ? K.orange : K.ink), fontFace: HF, align: ci === 0 ? "left" : "center", valign: "middle" });
            x += colW[ci];
          });
          y += rh[ri];
        });
        T(s, d.note, { x: MX, y: 5.6, w: W - 2 * MX, h: 0.7, fontSize: 24, color: K.gray });
        foot(s, false, L);
        break;
      }
      case "ladder": {
        head(s, d.label, d.title, false);
        const x0 = MX, lw = 5.8, y0 = 2.0;
        const hs = [1.15, 1.15, 0.0, 1.15];
        const cols = [K.blue, K.blue, K.ink, "D94141"];
        // price ladder: bars from top
        const ys = [2.0, 3.25, 4.5, 5.75];
        d.rungs.forEach((r, i) => {
          const y = ys[i];
          s.addShape(pres.shapes.LINE, { x: x0 + 1.6, y: y + 0.3, w: lw - 1.6, h: 0, line: { color: cols[i], width: 3, dashType: i === 2 ? "solid" : "dash" } });
          T(s, r.r, { x: x0, y, w: 1.5, h: 0.6, fontSize: 28, bold: true, color: cols[i], fontFace: HF, valign: "middle" });
          T(s, r.pts, { x: x0 + 1.6, y: y - 0.25, w: lw - 1.6, h: 0.5, fontSize: 20, color: K.gray, align: "right" });
        });
        s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.3, y: 2.0, w: W - MX - 7.3, h: 4.2, fill: { color: K.panel }, line: { color: K.panel }, rectRadius: 0.08 });
        T(s, d.text, { x: 7.7, y: 2.3, w: W - MX - 8.1, h: 2.0, fontSize: 26, bold: true, color: K.ink });
        T(s, "1R = your stop distance, 3.5–4 points. 2R = 7–8 points.", { x: 7.7, y: 4.3, w: W - MX - 8.1, h: 1.6, fontSize: 22, color: K.gray });
        foot(s, false, L);
        break;
      }
      case "image": {
        head(s, d.label, d.title, false, K.red);
        const ar = d.ar;
        const maxW = W - 2 * MX, maxH = 4.5;
        let w = maxW, h = w / ar; if (h > maxH) { h = maxH; w = h * ar; }
        s.addImage({ path: path.join(__dirname, d.img), x: (W - w) / 2, y: 1.85, w, h, altText: d.caption });
        T(s, d.caption, { x: MX, y: 6.45, w: W - 2 * MX, h: 0.4, fontSize: 16, italic: true, color: K.red, align: "center" });
        foot(s, false, L);
        break;
      }
      case "live": {
        s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.45, y: 0.4, w: W - 0.9, h: H - 1.1, fill: { color: K.ink }, line: { color: K.orange, width: 3, dashType: "dash" }, rectRadius: 0.1 });
        s.addImage({ data: monitor, x: MX + 0.2, y: 0.75, w: 0.8, h: 0.8 });
        T(s, "SCREEN-SHARE: TRADINGVIEW", { x: MX + 1.2, y: 0.75, w: 8, h: 0.4, fontSize: 18, bold: true, charSpacing: 4, color: K.orange, fontFace: HF });
        T(s, d.title, { x: MX + 1.2, y: 1.15, w: W - 2 * MX - 1.4, h: 0.8, fontSize: 36, bold: true, color: K.white, fontFace: HF, valign: "middle" });
        T(s, "ON THE CHART", { x: MX + 0.2, y: 2.45, w: 6, h: 0.4, fontSize: 16, bold: true, charSpacing: 3, color: K.lgray, fontFace: HF });
        d.cues.forEach((c, i) => {
          const y = 3.0 + i * 1.0;
          s.addShape(pres.shapes.OVAL, { x: MX + 0.2, y: y + 0.08, w: 0.6, h: 0.6, fill: { color: K.orange }, line: { color: K.orange } });
          T(s, String(i + 1), { x: MX + 0.2, y: y + 0.08, w: 0.6, h: 0.6, fontSize: 22, bold: true, color: K.ink, align: "center", valign: "middle", fontFace: HF });
          T(s, c, { x: MX + 1.1, y, w: W - 2 * MX - 1.5, h: 0.76, fontSize: 26, color: K.white, valign: "middle" });
        });
        break;
      }
      case "do": {
        T(s, "DO", { x: MX, y: 0.45, w: 6, h: 0.35, fontSize: 14, bold: true, charSpacing: 4, color: K.orange, fontFace: HF });
        T(s, `Your Turn: Lesson ${L}`, { x: MX, y: 0.85, w: W - 2 * MX, h: 0.9, fontSize: 36, bold: true, color: K.white, fontFace: HF, valign: "middle" });
        d.steps.forEach((t, i) => {
          const y = 2.1 + i * 1.2;
          s.addShape(pres.shapes.OVAL, { x: MX, y: y + 0.1, w: 0.7, h: 0.7, fill: { color: K.white }, line: { color: K.white } });
          T(s, String(i + 1), { x: MX, y: y + 0.1, w: 0.7, h: 0.7, fontSize: 24, bold: true, color: K.ink, align: "center", valign: "middle", fontFace: HF });
          T(s, t, { x: MX + 1.1, y, w: W - 2 * MX - 1.1, h: 0.9, fontSize: 26, color: K.white, valign: "middle" });
        });
        if (d.note) T(s, d.note, { x: MX, y: 5.9, w: W - 2 * MX, h: 0.6, fontSize: 24, italic: true, bold: true, color: K.orange });
        foot(s, true, L);
        break;
      }
      case "recap": {
        T(s, M.module + "  •  RECAP", { x: MX, y: 0.45, w: 8, h: 0.35, fontSize: 14, bold: true, charSpacing: 4, color: K.orange, fontFace: HF });
        T(s, d.title, { x: MX, y: 0.85, w: W - 2 * MX, h: 0.9, fontSize: 36, bold: true, color: K.white, fontFace: HF, valign: "middle" });
        d.items.forEach((t, i) => {
          const y = 2.0 + i * 0.75;
          s.addShape(pres.shapes.OVAL, { x: MX, y: y + 0.17, w: 0.26, h: 0.26, fill: { color: K.orange }, line: { color: K.orange } });
          T(s, t, { x: MX + 0.55, y, w: W - 2 * MX - 0.55, h: 0.6, fontSize: 24, color: K.white, valign: "middle" });
        });
        T(s, d.next, { x: MX, y: 6.0, w: W - 2 * MX, h: 0.6, fontSize: 24, bold: true, color: K.orange });
        foot(s, true, null);
        break;
      }
      default: throw new Error("kind " + d.kind);
    }
  }
  const out = path.join(__dirname, M.file);
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out, M.slides.length);
}

(async () => { await build(M4); await build(M5); })().catch(e => { console.error(e); process.exit(1); });
