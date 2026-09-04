/**
 * Render the ACOSE annotation guide to DOCX from build/book.json.
 *
 * The JSON is produced by build/export_json.py, which reuses the PDF builder's
 * markdown parser, so both outputs carry identical content.
 *
 * Cover uses validated recipe R1 (Pure Paragraph Left) from the docx skill's
 * design system; helpers calcTitleLayout / splitTitleLines / calcCoverSpacing are
 * copied verbatim from that reference and must not be reinvented.
 */
const {
  AlignmentType, BorderStyle, Document, Footer, Header, HeadingLevel, LevelFormat,
  NumberFormat, PageBreak, PageNumber, Packer, Paragraph, SectionType, ShadingType,
  Table, TableCell, TableLayoutType, TableOfContents, TableRow,
  TabStopPosition, TabStopType, TextRun, WidthType,
} = require("docx");
const fs = require("fs");
const path = require("path");

const ROOT = path.dirname(__dirname);
const BOOK = JSON.parse(fs.readFileSync(path.join(__dirname, "book.json"), "utf8"));
const OUT = path.join(ROOT, "dist", "Panduan_Anotasi_ACOSE_Bahasa_Indonesia.docx");

// ── palette ───────────────────────────────────────────────────────────────
// Same slate/teal the PDF uses (pdf.py palette.cascade, minimal/monochrome/seed 42)
// poured into the shape design-system.md expects, so both formats look like one book.
// Grey ramp for subtitle/meta/footer follows the skill's own light-palette values.
const P = {
  bg: "FFFFFF",
  titleColor: "475B66",
  subtitleColor: "606060",
  metaColor: "707070",
  footerColor: "A0A0A0",
  accent: "2B6886",
  slate: "475B66",
  text: "151617",
  muted: "80878A",
  border: "B2C3CC",
  stripe: "EAEBEC",
  panel: "E9ECED",
  codeBg: "EEEFF0",
};
const HEAD_FONT = "Segoe UI";
const BODY_FONT = "Georgia";
const MONO_FONT = "Consolas";

const PG = { size: { width: 11906, height: 16838 } };
const BODY_MARGIN = { top: 1418, bottom: 1418, left: 1247, right: 1247 };

// ── cover helpers (verbatim from references/design-system.md) ──────────────
function splitTitleLines(title, charsPerLine) {
  if (title.length <= charsPerLine) return [title];
  const breakAfter = new Set([
    ..."，。、；：！？", ..."的与和及之在于为", ..."-_—–·/", ..." \t",
  ]);
  const lines = [];
  let remaining = title;
  while (remaining.length > charsPerLine) {
    let breakAt = -1;
    for (let i = charsPerLine; i >= Math.floor(charsPerLine * 0.6); i--) {
      if (i < remaining.length && breakAfter.has(remaining[i - 1])) { breakAt = i; break; }
    }
    if (breakAt === -1) {
      const limit = Math.min(remaining.length, Math.ceil(charsPerLine * 1.3));
      for (let i = charsPerLine + 1; i < limit; i++) {
        if (breakAfter.has(remaining[i - 1])) { breakAt = i; break; }
      }
    }
    if (breakAt === -1) {
      breakAt = charsPerLine;
      const prevChar = remaining[breakAt - 1];
      const nextChar = remaining[breakAt];
      if (prevChar && nextChar && !breakAfter.has(prevChar) && !breakAfter.has(nextChar) &&
          /[\u4e00-\u9fff]/.test(prevChar) && /[\u4e00-\u9fff]/.test(nextChar)) {
        breakAt = breakAt - 1;
      }
    }
    lines.push(remaining.slice(0, breakAt).trim());
    remaining = remaining.slice(breakAt).trim();
  }
  if (remaining) lines.push(remaining);
  if (lines.length > 1 && lines[lines.length - 1].length <= 2) {
    const last = lines.pop();
    lines[lines.length - 1] += last;
  }
  return lines;
}

function calcTitleLayout(title, maxWidthTwips, preferredPt = 40, minPt = 24) {
  const charWidth = (pt) => pt * 20;
  const charsPerLine = (pt) => Math.floor(maxWidthTwips / charWidth(pt));
  let titlePt = preferredPt;
  let lines;
  while (titlePt >= minPt) {
    const cpl = charsPerLine(titlePt);
    if (cpl < 2) { titlePt -= 2; continue; }
    lines = splitTitleLines(title, cpl);
    if (lines.length <= 3) break;
    titlePt -= 2;
  }
  if (!lines || lines.length > 3) {
    const cpl = charsPerLine(minPt);
    lines = splitTitleLines(title, cpl);
    titlePt = minPt;
  }
  return { titlePt, titleLines: lines };
}

function calcCoverSpacing(params) {
  const {
    titleLineCount = 1, titlePt = 36, hasSubtitle = false,
    hasEnglishLabel = false, metaLineCount = 0,
    fixedHeight = 800, pageHeight = 16838, marginTop = 0, marginBottom = 0,
  } = params;
  const SAFETY = 1200;
  const usableHeight = pageHeight - marginTop - marginBottom - SAFETY;
  const titleHeight = titleLineCount * (titlePt * 23 + 200);
  const subtitleHeight = hasSubtitle ? (12 * 23 + 600) : 0;
  const englishLabelHeight = hasEnglishLabel ? (9 * 23 + 600) : 0;
  const metaHeight = metaLineCount * (10 * 23 + 100);
  const implicitParaHeight = 3 * 300;
  const contentHeight = titleHeight + subtitleHeight + englishLabelHeight +
                        metaHeight + fixedHeight + implicitParaHeight;
  const remainingSpace = usableHeight - contentHeight;
  const safeRemaining = Math.max(remainingSpace, 400);
  const FOOTER_MIN = 800;
  const rawTop = Math.floor(safeRemaining * 0.45);
  const rawBottom = Math.floor(safeRemaining * 0.45);
  const bottomSpacing = Math.max(rawBottom, FOOTER_MIN);
  const topSpacing = Math.max(rawTop - Math.max(0, FOOTER_MIN - rawBottom), 400);
  const midSpacing = Math.max(safeRemaining - topSpacing - bottomSpacing, 0);
  return { topSpacing, midSpacing, bottomSpacing };
}

// ── cover recipe R1 (structure verbatim from design-system.md) ─────────────
const NB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNoBorders = {
  top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB,
};

function buildCoverR1(config) {
  const CP = config.palette;
  const padL = 1200, padR = 800;

  // calcTitleLayout models CJK metrics (one char ~ pt*20 twips). This title is
  // Latin, where a glyph averages about half that, so the width passed in is
  // doubled; otherwise a 16-character title would be broken over three lines.
  const availableWidth = (11906 - padL - padR - 300) * 2;
  const { titlePt, titleLines } = calcTitleLayout(config.title, availableWidth, 40, 24);
  const titleSize = titlePt * 2;

  const spacing = calcCoverSpacing({
    titleLineCount: titleLines.length, titlePt,
    hasSubtitle: !!config.subtitle, hasEnglishLabel: !!config.englishLabel,
    metaLineCount: (config.metaLines || []).length,
    fixedHeight: 400,
  });

  const accentLeft = { style: BorderStyle.SINGLE, size: 8, color: CP.accent, space: 12 };
  const children = [];

  children.push(new Paragraph({ spacing: { before: spacing.topSpacing } }));

  if (config.englishLabel) {
    children.push(new Paragraph({
      indent: { left: padL, right: padR }, spacing: { after: 500 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: CP.accent, space: 8 } },
      children: [new TextRun({
        text: config.englishLabel, size: 18, color: CP.accent,
        font: { ascii: HEAD_FONT, eastAsia: HEAD_FONT }, characterSpacing: 40,
      })],
    }));
  }

  for (let i = 0; i < titleLines.length; i++) {
    children.push(new Paragraph({
      indent: { left: padL },
      spacing: {
        after: i < titleLines.length - 1 ? 100 : 300,
        line: Math.ceil(titlePt * 23), lineRule: "atLeast",
      },
      children: [new TextRun({
        text: titleLines[i], size: titleSize, bold: true,
        color: CP.titleColor, font: { ascii: HEAD_FONT, eastAsia: HEAD_FONT },
      })],
    }));
  }

  if (config.subtitle) {
    children.push(new Paragraph({
      indent: { left: padL, right: padR }, spacing: { after: 800, line: 320 },
      children: [new TextRun({
        text: config.subtitle, size: 24, color: CP.subtitleColor,
        font: { ascii: BODY_FONT, eastAsia: BODY_FONT },
      })],
    }));
  }

  for (const line of (config.metaLines || [])) {
    children.push(new Paragraph({
      indent: { left: padL + 200, right: padR }, spacing: { after: 80 },
      border: { left: accentLeft },
      children: [new TextRun({
        text: line, size: 22, color: CP.metaColor,
        font: { ascii: BODY_FONT, eastAsia: BODY_FONT },
      })],
    }));
  }

  children.push(new Paragraph({ spacing: { before: spacing.bottomSpacing } }));

  children.push(new Paragraph({
    indent: { left: padL, right: padR },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: CP.accent, space: 8 } },
    spacing: { before: 200 },
    tabStops: [{ type: TabStopType.RIGHT, position: 11906 - padL - padR }],
    children: [
      new TextRun({ text: config.footerLeft || "", size: 16, color: CP.footerColor, font: { ascii: HEAD_FONT } }),
      new TextRun({ text: "\t" }),
      new TextRun({ text: config.footerRight || "", size: 16, color: CP.footerColor, font: { ascii: HEAD_FONT } }),
    ],
  }));

  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: "exact" },
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: CP.bg }, borders: noBorders,
        children,
      })],
    })],
  })];
}

// ── inline markdown -> TextRun[] ───────────────────────────────────────────
/**
 * Emit one TextRun per inline fragment, handling `code`, **bold**, *italic*.
 *
 * Code spans are stashed before the emphasis pass. Without that, a line like
 * *(Jawaban: `MAKANAN#HARGA`.)* matches the italic alternative first and the
 * backticks end up printed literally.
 */
function runs(text, opts = {}) {
  const base = {
    size: opts.size || 21,
    color: opts.color || P.text,
    font: { ascii: opts.font || BODY_FONT, eastAsia: opts.font || BODY_FONT },
  };
  const codes = [];
  const stashed = text.replace(/`([^`]+)`/g, (_, code) => {
    codes.push(code);
    return "\u0001" + (codes.length - 1) + "\u0001";
  });

  const out = [];
  const emit = (chunk, emph) => {
    if (!chunk) return;
    // Expand any stashed code spans, keeping the surrounding emphasis.
    const parts = chunk.split(/\u0001(\d+)\u0001/);
    for (let i = 0; i < parts.length; i++) {
      const piece = parts[i];
      if (!piece) continue;
      if (i % 2 === 1) {
        out.push(new TextRun(Object.assign({}, emph, {
          text: codes[Number(piece)],
          size: Math.max(base.size - 2, 16),
          color: P.text,
          font: { ascii: MONO_FONT, eastAsia: MONO_FONT },
          shading: { fill: P.codeBg },
        })));
      } else {
        out.push(new TextRun(Object.assign({}, base, emph, { text: piece })));
      }
    }
  };

  const re = /(\*\*\*[^*]+\*\*\*)|(\*\*[^*]+\*\*)|(\*[^*\n]+\*)/g;
  let last = 0;
  let m;
  while ((m = re.exec(stashed)) !== null) {
    emit(stashed.slice(last, m.index), {});
    const tok = m[0];
    if (tok.startsWith("***")) emit(tok.slice(3, -3), { bold: true, italics: true });
    else if (tok.startsWith("**")) emit(tok.slice(2, -2), { bold: true });
    else emit(tok.slice(1, -1), { italics: true });
    last = m.index + tok.length;
  }
  emit(stashed.slice(last), {});
  return out.length ? out : [new TextRun(Object.assign({}, base, { text: "" }))];
}

/** Plain text of an inline string, for headings that must not carry markup. */
function plain(text) {
  return text.replace(/\*\*\*/g, "").replace(/\*\*/g, "")
             .replace(/\*/g, "").replace(/`/g, "").trim();
}

// ── block renderers ───────────────────────────────────────────────────────
function bodyPara(text) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 312, after: 140 },
    children: runs(text),
  });
}

function heading(text, level, opts = {}) {
  const size = level === 1 ? 34 : level === 2 ? 26 : 22;
  const color = level === 3 ? P.accent : P.slate;
  return new Paragraph({
    heading: level === 1 ? HeadingLevel.HEADING_1
      : level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3,
    keepNext: true, keepLines: true,
    spacing: {
      before: opts.before !== undefined ? opts.before : (level === 1 ? 0 : level === 2 ? 320 : 240),
      after: level === 1 ? 120 : 120,
      line: Math.ceil((size / 2) * 23), lineRule: "atLeast",
    },
    children: [new TextRun({
      text: plain(text), bold: true, size, color,
      font: { ascii: HEAD_FONT, eastAsia: HEAD_FONT },
    })],
  });
}

function listPara(text, ordered, index) {
  return new Paragraph({
    numbering: { reference: ordered ? "book-ol" : "book-ul", level: 0 },
    alignment: AlignmentType.LEFT,
    spacing: { line: 312, after: 70 },
    children: runs(text),
  });
}

/** The recurring "Sebentar, masalahnya apa?" drawer: tinted cell, teal left bar. */
function callout(items) {
  const inner = [];
  items.forEach((it, i) => {
    const isLast = i === items.length - 1;
    if (it.kind === "bullet") {
      inner.push(new Paragraph({
        numbering: { reference: "book-ul", level: 0 },
        spacing: { line: 312, after: isLast ? 0 : 60 },
        children: runs(it.text, { size: 20 }),
      }));
    } else {
      inner.push(new Paragraph({
        alignment: AlignmentType.LEFT,
        spacing: { line: 312, after: isLast ? 0 : 100 },
        children: runs(it.text, { size: 20 }),
      }));
    }
  });
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      cantSplit: true,
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: P.panel },
        borders: {
          top: NB, bottom: NB, right: NB,
          left: { style: BorderStyle.SINGLE, size: 18, color: P.accent },
        },
        margins: { top: 160, bottom: 160, left: 220, right: 200 },
        children: inner,
      })],
    })],
  });
}

/** Fenced code: monospace on a light tint with a teal left rule. */
function codeBlock(text) {
  const lines = text.split("\n");
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      cantSplit: true,
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: P.codeBg },
        borders: {
          top: NB, bottom: NB, right: NB,
          left: { style: BorderStyle.SINGLE, size: 18, color: P.accent },
        },
        margins: { top: 140, bottom: 140, left: 220, right: 200 },
        children: lines.map((ln, i) => new Paragraph({
          spacing: { line: 260, after: i === lines.length - 1 ? 0 : 20 },
          children: [new TextRun({
            text: ln || " ", size: 18, color: P.text,
            font: { ascii: MONO_FONT, eastAsia: MONO_FONT },
          })],
        })),
      })],
    })],
  });
}

/** Slate header row, white bold text, alternating light stripes. */
function dataTable(rows) {
  const cols = rows[0].length;
  const trs = rows.map((cells, r) => new TableRow({
    tableHeader: r === 0,
    cantSplit: true,
    children: cells.map((cell) => new TableCell({
      shading: {
        type: ShadingType.CLEAR,
        fill: r === 0 ? P.slate : (r % 2 === 0 ? P.stripe : "FFFFFF"),
      },
      borders: {
        top: { style: BorderStyle.SINGLE, size: 4, color: P.border },
        bottom: { style: BorderStyle.SINGLE, size: 4, color: P.border },
        left: { style: BorderStyle.SINGLE, size: 4, color: P.border },
        right: { style: BorderStyle.SINGLE, size: 4, color: P.border },
      },
      margins: { top: 90, bottom: 90, left: 130, right: 130 },
      children: [new Paragraph({
        spacing: { line: 312, after: 0 },
        children: r === 0
          ? [new TextRun({
              text: plain(cell), bold: true, size: 19, color: "FFFFFF",
              font: { ascii: HEAD_FONT, eastAsia: HEAD_FONT },
            })]
          : runs(cell, { size: 19 }),
      })],
    })),
  }));
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.AUTOFIT,
    columnWidths: new Array(cols).fill(Math.floor(9412 / cols)),
    borders: allNoBorders,
    rows: trs,
  });
}

/** Dark slate band that opens the optional technical aside. */
function techBand(title) {
  const clean = plain(title).replace(/^[^:]*:\s*/, "");
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      cantSplit: true,
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: P.slate },
        borders: noBorders,
        margins: { top: 150, bottom: 150, left: 220, right: 200 },
        children: [
          new Paragraph({
            spacing: { line: 240, after: 40 },
            children: [new TextRun({
              text: "UNTUK YANG INGIN LEBIH TEKNIS", bold: true, size: 16,
              color: "FFFFFF", characterSpacing: 30,
              font: { ascii: HEAD_FONT, eastAsia: HEAD_FONT },
            })],
          }),
          new Paragraph({
            spacing: { line: 300, after: 0 },
            children: [new TextRun({
              text: clean, bold: true, size: 24, color: "FFFFFF",
              font: { ascii: HEAD_FONT, eastAsia: HEAD_FONT },
            })],
          }),
        ],
      })],
    })],
  });
}

// ── assembly ──────────────────────────────────────────────────────────────
/** Body flowables for one chapter. Paging is handled by its section break. */
function chapterChildren(ch) {
  const out = [];

  // Kicker above the chapter title; not a Heading, so it stays out of the TOC.
  out.push(new Paragraph({
    spacing: { before: 0, after: 60, line: 312 },
    keepNext: true,
    children: [new TextRun({
      text: ch.kicker, bold: true, size: 19, color: P.accent,
      characterSpacing: 20, font: { ascii: HEAD_FONT, eastAsia: HEAD_FONT },
    })],
  }));
  out.push(heading(ch.title, 1, { before: 0 }));
  // Teal rule under the chapter title, drawn as a paragraph border.
  out.push(new Paragraph({
    spacing: { before: 0, after: 260 },
    border: { top: { style: BorderStyle.SINGLE, size: 18, color: P.accent, space: 6 } },
    children: [],
  }));

  for (const b of ch.blocks) {
    if (b.kind === "heading") {
      if (b.flag === "tech") {
        out.push(new Paragraph({ spacing: { before: 260, after: 0 }, children: [] }));
        out.push(techBand(b.text));
        out.push(new Paragraph({ spacing: { before: 160, after: 0 }, children: [] }));
      } else {
        out.push(heading(b.text, Math.min(b.level, 3)));
      }
    } else if (b.kind === "para") {
      out.push(bodyPara(b.text));
    } else if (b.kind === "list") {
      b.items.forEach((it, i) => out.push(listPara(it, b.ordered, i)));
      out.push(new Paragraph({ spacing: { after: 80 }, children: [] }));
    } else if (b.kind === "quote") {
      out.push(callout(b.items));
      out.push(new Paragraph({ spacing: { after: 180 }, children: [] }));
    } else if (b.kind === "code") {
      out.push(codeBlock(b.text));
      out.push(new Paragraph({ spacing: { after: 180 }, children: [] }));
    } else if (b.kind === "table") {
      out.push(dataTable(b.rows));
      out.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
    }
  }
  return out;
}

/**
 * One section per chapter so the running head can name the chapter as static
 * text. A STYLEREF field would also work, but if the style name failed to
 * resolve Word would print an error banner on every page instead.
 */
function chapterSections() {
  return BOOK.chapters.map((ch, ci) => ({
    properties: {
      type: SectionType.NEXT_PAGE,
      page: Object.assign(
        { size: PG.size, margin: BODY_MARGIN },
        // Only the first body section restarts numbering; the rest continue it.
        ci === 0 ? { pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } : {},
      ),
    },
    headers: { default: runningHeader(ch.running) },
    footers: { default: pageFooter() },
    children: chapterChildren(ch),
  }));
}

function runningHeader(chapterLabel) {
  return new Header({
    children: [new Paragraph({
      spacing: { after: 60 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: P.border, space: 4 } },
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      children: [
        new TextRun({ text: BOOK.title, size: 16, color: P.muted, font: { ascii: HEAD_FONT } }),
        new TextRun({ text: "\t" }),
        new TextRun({ text: chapterLabel, size: 16, color: P.muted, font: { ascii: HEAD_FONT } }),
      ],
    })],
  });
}

function pageFooter() {
  return new Footer({
    children: [new Paragraph({
      spacing: { before: 60 },
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: P.border, space: 6 } },
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      children: [
        new TextRun({ text: BOOK.series, size: 15, color: P.muted, font: { ascii: HEAD_FONT } }),
        new TextRun({ text: "\t" }),
        new TextRun({
          children: [PageNumber.CURRENT], bold: true, size: 17,
          color: P.accent, font: { ascii: HEAD_FONT },
        }),
      ],
    })],
  });
}

const coverConfig = {
  title: BOOK.title,
  englishLabel: "PANDUAN TEKNOLOGI TEPAT GUNA \u00b7 SERI 022",
  subtitle:
    "Kata menjadi data, supaya komputer bisa membaca rasa \u2014 keluhan dan pujian " +
    "di balik setiap ulasan. Buku ini mengajarkan cara menandai lima elemen ACOSE: " +
    "aspek, kategori, opini, sentimen, dan emosi. Ditulis untuk pembaca umum tanpa " +
    "latar belakang ilmu komputer.",
  metaLines: [
    BOOK.subtitle,
    "Proyek ACOS-ASLI \u00b7 Taksonomi resto_id",
    "Edisi pertama \u00b7 September 2026",
  ],
  footerLeft: "PROYEK ACOS-ASLI",
  footerRight: "PANDUAN ANOTASI ACOSE",
  palette: P,
};

const doc = new Document({
  title: BOOK.title + " \u2014 " + BOOK.subtitle,
  creator: "Tim ACOS-ASLI",
  description: "Panduan anotasi manual ACOSE (quintuple ABSA) untuk bahasa Indonesia",
  keywords: "ACOSE, ACOS, ABSA, anotasi, sentimen, emosi, bahasa Indonesia, TTG",
  styles: {
    default: {
      document: {
        run: { font: { ascii: BODY_FONT, eastAsia: BODY_FONT }, size: 21, color: P.text },
        paragraph: { spacing: { line: 312 } },
      },
    },
  },
  numbering: {
    config: [
      {
        reference: "book-ul",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 360, hanging: 220 } } },
        }],
      },
      {
        reference: "book-ol",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 360, hanging: 220 } } },
        }],
      },
    ],
  },
  sections: [
    {
      properties: { page: { size: PG.size, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
      children: buildCoverR1(coverConfig),
    },
    {
      properties: {
        type: SectionType.NEXT_PAGE,
        page: {
          size: PG.size, margin: BODY_MARGIN,
          pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN },
        },
      },
      footers: { default: pageFooter() },
      children: [
        new Paragraph({
          spacing: { before: 240, after: 200 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: P.accent, space: 8 } },
          children: [new TextRun({
            text: "Daftar Isi", bold: true, size: 32, color: P.slate,
            font: { ascii: HEAD_FONT, eastAsia: HEAD_FONT },
          })],
        }),
        new TableOfContents("Daftar Isi", { hyperlink: true, headingStyleRange: "1-3" }),
        new Paragraph({
          spacing: { before: 240 },
          children: [new TextRun({
            text: "Catatan: daftar isi ini dibuat dengan field code. Setelah dokumen " +
                  "diedit, klik kanan pada daftar isi lalu pilih \u201cUpdate Field\u201d " +
                  "agar nomor halamannya kembali tepat.",
            italics: true, size: 17, color: "888888",
            font: { ascii: BODY_FONT, eastAsia: BODY_FONT },
          })],
        }),
        new Paragraph({ children: [new PageBreak()] }),
      ],
    },
    ...chapterSections(),
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("wrote", OUT, "(" + (buf.length / 1024).toFixed(1) + " KB)");
});
