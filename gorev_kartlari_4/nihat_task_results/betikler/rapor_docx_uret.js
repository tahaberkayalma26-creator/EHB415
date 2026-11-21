// Nihat_Gorev_Karti_4_Rapor.md -> .docx (docx-js).
// Gereksinim: Node.js ve docx paketi (npm install docx). Kullanim: node rapor_docx_uret.js <girdi.md> <cikti.docx>
// Resim yollari .md dosyasinin klasorune gore cozulur. Ornek (nihat_task_results klasorunde):
//   node betikler/rapor_docx_uret.js Nihat_Gorev_Karti_4_Rapor.md Nihat_Gorev_Karti_4_Rapor.docx
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, AlignmentType, HeadingLevel, LevelFormat, Footer, Header, PageNumber, VerticalAlign,
} = require("docx");

const [, , SRC, OUT] = process.argv;
const BASE = path.dirname(path.resolve(SRC));
const lines = fs.readFileSync(SRC, "utf8").replace(/\r/g, "").split("\n");

// ---------------------------------------------------------------- sayfa
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1247;           // A4, 2,2 cm
const CONTENT_W = PAGE_W - 2 * MARGIN;                          // 9412 DXA
const CONTENT_PX = Math.floor(CONTENT_W / 15);                  // 1 px = 15 DXA (96 dpi)
const MAX_IMG_H_PX = 820;
const FONT = "Arial", MONO = "Courier New";

// ---------------------------------------------------------------- satir ici bicim
function inline(text, base = {}) {
  // **kalin**, `kod`, [metin](url)
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1");
  const runs = [];
  let bold = false, i = 0, buf = "";
  const flush = () => { if (buf) { runs.push(new TextRun({ text: buf, bold: bold || base.bold, italics: base.italics, size: base.size, font: base.font || FONT, color: base.color })); buf = ""; } };
  while (i < text.length) {
    if (text.startsWith("**", i)) { flush(); bold = !bold; i += 2; continue; }
    if (text[i] === "`") {
      const j = text.indexOf("`", i + 1);
      if (j > i) {
        flush();
        runs.push(new TextRun({ text: text.slice(i + 1, j), font: MONO, size: base.size ? base.size - 1 : 20, bold: bold || base.bold, italics: base.italics, color: "1F2937" }));
        i = j + 1; continue;
      }
    }
    buf += text[i]; i++;
  }
  flush();
  return runs;
}

// ---------------------------------------------------------------- tablo
function splitRow(line) {
  const s = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  const cells = []; let cur = "", code = false;
  for (const ch of s) {
    if (ch === "`") code = !code;
    if (ch === "|" && !code) { cells.push(cur.trim()); cur = ""; } else cur += ch;
  }
  cells.push(cur.trim());
  return cells;
}
const plain = (t) => t.replace(/\*\*|`/g, "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
const BORDER = { style: BorderStyle.SINGLE, size: 4, color: "BFC5CD" };
const BORDERS = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER };

function makeTable(rows) {
  const head = rows[0], body = rows.slice(2);
  const n = head.length;
  const all = [head, ...body].map((r) => { while (r.length < n) r.push(""); return r.slice(0, n); });
  const size = n >= 9 ? 15 : n >= 7 ? 16 : 18;                  // 7,5 / 8 / 9 pt
  const charW = size * 5.9, pad = 190;                         // DXA / karakter (yaklasik), hucre kenar payi
  const words = (t) => plain(t).split(/[\s/]+/).reduce((m, w) => Math.max(m, w.length), 0);
  const minW = [], want = [];
  for (let c = 0; c < n; c++) {
    let mw = words(head[c]) * 1.1, ww = Math.min(plain(head[c]).length, 16);
    for (const r of body) { mw = Math.max(mw, words(r[c])); ww = Math.max(ww, Math.min(plain(r[c]).length, 46)); }
    minW.push(Math.max(mw, 2) * charW + pad); want.push(Math.max(ww, mw, 2) * charW + pad);
  }
  const sMin = minW.reduce((a, b) => a + b, 0), sWant = want.reduce((a, b) => a + b, 0);
  let widths;
  if (sWant <= CONTENT_W) widths = want.map((w) => (w * CONTENT_W) / sWant);
  else if (sMin >= CONTENT_W) widths = minW.map((w) => (w * CONTENT_W) / sMin);
  else { const f = (CONTENT_W - sMin) / (sWant - sMin); widths = minW.map((m, c) => m + f * (want[c] - m)); }
  widths = widths.map(Math.floor);
  widths[n - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  const center = [];
  for (let c = 0; c < n; c++) center.push(c > 0 && body.every((r) => plain(r[c]).length <= 18));
  const keep = all.length <= 15;
  let rowIdx = 0;
  const mkRow = (r, isHead) => { const last = ++rowIdx === all.length; return new TableRow({
    tableHeader: isHead, cantSplit: true,
    children: r.map((t, c) => new TableCell({
      width: { size: widths[c], type: WidthType.DXA }, borders: BORDERS, verticalAlign: VerticalAlign.CENTER,
      shading: isHead ? { fill: "E5E7EB", type: ShadingType.CLEAR, color: "auto" } : undefined,
      margins: { top: 40, bottom: 40, left: 80, right: 80 },
      children: [new Paragraph({ alignment: center[c] || isHead ? AlignmentType.CENTER : AlignmentType.LEFT, spacing: { before: 0, after: 0 },
                                 keepNext: keep && !last, keepLines: true, children: inline(t, { size, bold: isHead }) })],
    })),
  }); };
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: widths,
                     rows: [mkRow(all[0], true), ...all.slice(1).map((r) => mkRow(r, false))] });
}

// ---------------------------------------------------------------- resim
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}
function makeImage(rel) {
  const file = path.join(BASE, rel);
  const { w, h, data } = pngSize(file);
  let s = Math.min(1, CONTENT_PX / w, MAX_IMG_H_PX / h);
  return new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60, line: 240, lineRule: "auto" },
    children: [new ImageRun({ type: "png", data, transformation: { width: Math.round(w * s), height: Math.round(h * s) },
                              altText: { title: path.basename(rel), description: rel, name: path.basename(rel) } })] });
}

// ---------------------------------------------------------------- bloklar
const out = [];
let numInstance = 0, titleDone = false;
const LIST_RE = /^(\s*)([-*]|\d+\.)\s+(.*)$/;
let i = 0;
while (i < lines.length) {
  const line = lines[i];
  if (!line.trim()) { i++; continue; }
  if (/^---+\s*$/.test(line)) { i++; continue; }

  // kod blogu
  if (line.startsWith("```")) {
    const code = []; i++;
    while (i < lines.length && !lines[i].startsWith("```")) code.push(lines[i++]);
    i++;
    let nx = i; while (nx < lines.length && !lines[nx].trim()) nx++;
    const glue = code.length <= 3 && !(nx < lines.length && lines[nx].startsWith("#"));
    code.forEach((c, k) => out.push(new Paragraph({
      spacing: { before: k === 0 ? 80 : 0, after: k === code.length - 1 ? 120 : 0, line: 240, lineRule: "auto" },
      shading: { fill: "F3F4F6", type: ShadingType.CLEAR, color: "auto" }, indent: { left: 113, right: 113 },
      keepLines: true, keepNext: k < code.length - 1 || glue,
      children: [new TextRun({ text: c || " ", font: MONO, size: 16 })] })));
    continue;
  }

  // baslik
  const hm = line.match(/^(#{1,4})\s+(.*)$/);
  if (hm) {
    const lvl = hm[1].length, txt = hm[2];
    if (lvl === 1 && !titleDone) {
      titleDone = true;
      out.push(new Paragraph({ heading: HeadingLevel.TITLE, children: inline(txt) }));
    } else {
      const H = [null, HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4][lvl];
      out.push(new Paragraph({ heading: H, pageBreakBefore: lvl === 1, children: inline(txt) }));
    }
    i++; continue;
  }

  // tablo
  if (line.trim().startsWith("|")) {
    const rows = [];
    while (i < lines.length && lines[i].trim().startsWith("|")) rows.push(splitRow(lines[i++]));
    out.push(makeTable(rows));
    out.push(new Paragraph({ spacing: { before: 0, after: 80 }, children: [] }));
    continue;
  }

  // resim + sekil yazisi
  const im = line.match(/^!\[[^\]]*\]\(([^)]+)\)\s*$/);
  if (im) { out.push(makeImage(im[1])); i++; continue; }
  if (/^\*Şekil\s/.test(line.trim())) {
    const t = line.trim().replace(/^\*/, "").replace(/\*$/, "");
    out.push(new Paragraph({ style: "Caption", alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 },
                             children: inline(t, { italics: true, size: 18, color: "374151" }) }));
    i++; continue;
  }

  // alinti (ozet kutusu)
  if (line.startsWith(">")) {
    const paras = []; let cur = [];
    while (i < lines.length && lines[i].startsWith(">")) {
      const t = lines[i].replace(/^>\s?/, "");
      if (!t.trim()) { if (cur.length) paras.push(cur.join(" ")); cur = []; } else cur.push(t);
      i++;
    }
    if (cur.length) paras.push(cur.join(" "));
    paras.forEach((p, k) => out.push(new Paragraph({
      shading: { fill: "EEF2F7", type: ShadingType.CLEAR, color: "auto" },
      border: { left: { style: BorderStyle.SINGLE, size: 18, color: "1F4E79", space: 8 } },
      indent: { left: 170, right: 113 }, spacing: { before: k === 0 ? 120 : 0, after: k === paras.length - 1 ? 200 : 100 },
      children: inline(p) })));
    continue;
  }

  // liste
  if (LIST_RE.test(line)) {
    let numbered = null;
    while (i < lines.length) {
      const l = lines[i];
      if (!l.trim()) {                                  // bos satir: liste devam ediyor mu?
        let j = i + 1; while (j < lines.length && !lines[j].trim()) j++;
        if (j < lines.length && (LIST_RE.test(lines[j]) || /^\s{3,}\S/.test(lines[j]))) { i = j; continue; }
        break;
      }
      const m = l.match(LIST_RE);
      if (m) {
        const level = m[1].length >= 2 ? 1 : 0;
        const isNum = /\d+\./.test(m[2]);
        if (isNum && level === 0 && numbered === null) numbered = ++numInstance;
        out.push(new Paragraph({
          numbering: isNum ? { reference: "num", level, instance: numbered } : { reference: "bul", level },
          spacing: { before: 0, after: 60 }, children: inline(m[3]) }));
      } else if (/^\s{2,}\S/.test(l)) {               // madde icindeki devam paragrafi
        out.push(new Paragraph({ indent: { left: 720 }, spacing: { before: 60, after: 60 }, children: inline(l.trim()) }));
      } else break;
      i++;
    }
    continue;
  }

  // denklem satiri (2 bosluk girintili)
  if (/^ {2}\S/.test(line)) {
    out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 80 },
                             children: [new TextRun({ text: line.trim(), font: "Times New Roman", size: 23 })] }));
    i++; continue;
  }

  // paragraf
  out.push(new Paragraph({ alignment: AlignmentType.LEFT, spacing: { before: 0, after: 120 }, children: inline(line.trim()) }));
  i++;
}

// ---------------------------------------------------------------- belge
const hd = (size, before, after, color = "1F2937") => ({ run: { font: FONT, size, bold: true, color }, paragraph: { spacing: { before, after }, keepNext: true, keepLines: true } });
const doc = new Document({
  creator: "Nihat", title: "Nihat – Görev Kartı 4 Uygulama ve Sonuç Raporu", description: "EHB415 görev kartları 4, Nihat",
  styles: {
    default: {
      document: { run: { font: FONT, size: 22 }, paragraph: { spacing: { line: 276, lineRule: "auto" } } },
      title: { run: { font: FONT, size: 36, bold: true, color: "1F4E79" }, paragraph: { spacing: { before: 0, after: 200 }, keepNext: true } },
      heading1: { run: { font: FONT, size: 32, bold: true, color: "1F4E79" }, paragraph: { spacing: { before: 0, after: 200 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
      heading2: { run: { font: FONT, size: 28, bold: true, color: "1F4E79" }, paragraph: { spacing: { before: 360, after: 140 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
      heading3: { ...hd(24, 240, 100), paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, keepLines: true, outlineLevel: 2 } },
      heading4: { ...hd(22, 200, 80), paragraph: { spacing: { before: 200, after: 80 }, keepNext: true, keepLines: true, outlineLevel: 3 } },
    },
    paragraphStyles: [{ id: "Caption", name: "Caption", basedOn: "Normal", run: { font: FONT, size: 18, italics: true, color: "374151" } }],
  },
  numbering: {
    config: [
      { reference: "bul", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 860, hanging: 260 } } } }] },
      { reference: "num", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 320 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 860, hanging: 260 } } } }] },
    ],
  },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Nihat – Görev Kartı 4 (n78, 3,5 GHz, 100 MHz)", size: 16, color: "6B7280" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["Sayfa ", PageNumber.CURRENT, " / ", PageNumber.TOTAL_PAGES], size: 16, color: "6B7280" })] })] }) },
    children: out,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("yazildi:", OUT, (b.length / 1e6).toFixed(2), "MB"); });
