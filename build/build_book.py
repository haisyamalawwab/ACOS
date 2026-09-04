"""Build the ACOSE annotation guide (reports/022*.md) into one corporate-styled PDF book.

Pipeline: markdown blocks -> ReportLab flowables -> body PDF (with auto TOC),
then cover_render.py template 02 is merged in as page 1.
"""
from __future__ import annotations

import html
import os
import re
from dataclasses import dataclass, field

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Flowable,
    Frame,
    HRFlowable,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")
OUT_DIR = os.path.join(ROOT, "dist")

BOOK_TITLE = "Kata, Data, Rasa"
BOOK_SUBTITLE = "Panduan Anotasi ACOSE untuk Ulasan Berbahasa Indonesia"
BOOK_SERIES = "Panduan Teknologi Tepat Guna · Seri 022"

# --- palette: pdf.py palette.cascade --mode minimal --harmony monochrome --seed 42 ---
PAGE_BG = colors.HexColor("#f0f0f1")
SECTION_BG = colors.HexColor("#eeeff0")
CARD_BG = colors.HexColor("#e9eced")
TABLE_STRIPE = colors.HexColor("#eaebec")
HEADER_FILL = colors.HexColor("#475b66")
COVER_BLOCK = colors.HexColor("#536e7b")
BORDER = colors.HexColor("#b2c3cc")
ICON = colors.HexColor("#416f85")
ACCENT = colors.HexColor("#2b6886")
ACCENT_2 = colors.HexColor("#4a5cb7")
TEXT_PRIMARY = colors.HexColor("#151617")
TEXT_MUTED = colors.HexColor("#80878a")

FONT_FILES = {
    "Display": "C:/Windows/Fonts/segoeui.ttf",
    "Display-Bold": "C:/Windows/Fonts/segoeuib.ttf",
    "Display-Light": "C:/Windows/Fonts/segoeuil.ttf",
    "Body": "C:/Windows/Fonts/georgia.ttf",
    "Body-Bold": "C:/Windows/Fonts/georgiab.ttf",
    "Body-Italic": "C:/Windows/Fonts/georgiai.ttf",
    "Body-BoldItalic": "C:/Windows/Fonts/georgiaz.ttf",
    "Mono": "C:/Windows/Fonts/consola.ttf",
}
FALLBACK_FONT = "Display"  # Georgia lacks U+2192; Segoe UI covers it


def register_fonts() -> None:
    for name, path in FONT_FILES.items():
        pdfmetrics.registerFont(TTFont(name, path))
    registerFontFamily(
        "Body", normal="Body", bold="Body-Bold",
        italic="Body-Italic", boldItalic="Body-BoldItalic",
    )
    registerFontFamily("Display", normal="Display", bold="Display-Bold", italic="Display")
    registerFontFamily("Mono", normal="Mono", bold="Mono", italic="Mono")


# --- chapter map: stem -> (kicker, running head, book-style title) --------
CHAPTERS = [
    ("022aa_halaman_judul_dan_kata_pengantar", "PEMBUKA", "Kata Pengantar",
     "Kata Pengantar"),
    ("022a_apa_itu_acose", "BAB 1", "Apa Itu ACOSE",
     "Apa Itu ACOSE? Dari Pertanyaan Besar, Kita Pecah Jadi Lima"),
    ("022b_aspek_dan_opini", "BAB 2", "Aspek & Opini",
     "Aspek & Opini: Menemukan Benda dan Kata Rasanya"),
    ("022c_kategori", "BAB 3", "Kategori",
     "Kategori: Memberi Nama Resmi pada Benda"),
    ("022d_sentimen", "BAB 4", "Sentimen",
     "Sentimen: Suka, Biasa Aja, atau Tidak Suka"),
    ("022e_emosi", "BAB 5", "Emosi",
     "Emosi: Perasaan Sesungguhnya, dan Kenapa Ini Bagian Tersulit"),
    ("022f_format_data", "BAB 6", "Format Data",
     "Format Data: Bagaimana Mencatat Semuanya"),
    ("022g_kasus_sulit_dan_faq", "BAB 7", "Kasus Sulit & FAQ",
     "Kasus Sulit dan Tanya-Jawab: Saat Bahasa Mulai Nakal"),
    ("022h_di_balik_layar_dan_manfaat", "BAB 8", "Di Balik Layar",
     "Di Balik Layar: Kenapa Semua Ini Berharga, dan Jujur Soal Batasannya"),
]

# Lines that only made sense when each chapter was a standalone file.
DROP_LINE_PREFIXES = ("**Seri:**", "**Sebelumnya:**", "**Bagian:**", "**Tanggal:**",
                      "**Proyek:**", "**Tugas:**", "**Versi:**")
NAV_RE = re.compile(r"^\*Lanjut ke .*\*$")
# 022aa repeats the series line as an H2 under its H1; the cover already carries it.
DROP_HEADING_RE = re.compile(r"^Buku Panduan Teknologi Tepat Guna")
TECH_ASIDE_RE = re.compile(r"BAGI YANG MAU LEBIH DALAM")
GLYPH_STRIP = {"▪️": "", "▪": "", "🎉": ""}

# The chapters used to be separate files and cite each other by file code. In one
# bound book those codes point at nothing, so rewrite them to chapter names.
XREF_MAP = {
    "aa": "Pembuka", "a": "Bab 1", "b": "Bab 2", "c": "Bab 3", "d": "Bab 4",
    "e": "Bab 5", "f": "Bab 6", "g": "Bab 7", "h": "Bab 8",
}
XREF_RE = re.compile(r"\b022(aa|[a-h])\b")
EXERCISE_RE = re.compile(r"^\*?\*?Latihan")

# ══════════════════════════════════════════════════════════════════
# markdown -> blocks
# ══════════════════════════════════════════════════════════════════
@dataclass
class Block:
    kind: str
    text: str = ""
    items: list = field(default_factory=list)
    rows: list = field(default_factory=list)
    level: int = 0
    flag: str = ""


def clean_source(raw: str) -> str:
    for bad, good in GLYPH_STRIP.items():
        raw = raw.replace(bad, good)
    return XREF_RE.sub(lambda m: XREF_MAP[m.group(1)], raw)


def parse_markdown(text: str) -> list[Block]:
    lines = clean_source(text).split("\n")
    blocks: list[Block] = []
    buf: list[str] = []
    i = 0

    def flush_para() -> None:
        if buf:
            blocks.append(Block("para", " ".join(buf).strip()))
            buf.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para()
            i += 1
            continue
        if stripped.startswith(DROP_LINE_PREFIXES) or NAV_RE.match(stripped):
            flush_para()
            i += 1
            continue
        if set(stripped) <= {"-", "—"} and len(stripped) >= 3:
            flush_para()
            i += 1
            continue

        if stripped.startswith("```"):
            flush_para()
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            i += 1  # closing fence
            while code and not code[0].strip():
                code.pop(0)
            while code and not code[-1].strip():
                code.pop()
            if code:
                blocks.append(Block("code", "\n".join(code)))
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            flush_para()
            level = len(m.group(1))
            title = m.group(2).strip()
            if DROP_HEADING_RE.match(title):
                i += 1
                continue
            flag = "tech" if TECH_ASIDE_RE.search(title) else ""
            blocks.append(Block("heading", title, level=level, flag=flag))
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and re.match(
            r"^\|[\s:|-]+\|$", lines[i + 1].strip()
        ):
            flush_para()
            rows: list[list[str]] = []
            header = [c.strip() for c in stripped.strip("|").split("|")]
            rows.append(header)
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            width = max(len(r) for r in rows)
            rows = [r + [""] * (width - len(r)) for r in rows]
            blocks.append(Block("table", rows=rows))
            continue

        if stripped.startswith(">"):
            flush_para()
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]).rstrip())
                i += 1
            blocks.append(Block("quote", items=parse_quote_body(quote)))
            continue

        if re.match(r"^([-*])\s+\S", stripped) or re.match(r"^\d+\.\s+\S", stripped):
            flush_para()
            ordered = bool(re.match(r"^\d+\.", stripped))
            items, i = collect_list(lines, i, ordered)
            blocks.append(Block("list", items=items, flag="ol" if ordered else "ul"))
            continue

        buf.append(stripped)
        i += 1

    flush_para()
    return blocks


def collect_list(lines: list[str], i: int, ordered: bool) -> tuple[list[str], int]:
    """Gather one list, folding indented continuation lines into their item."""
    pattern = r"^\d+\.\s+(.*)$" if ordered else r"^[-*]\s+(.*)$"
    items: list[str] = []
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if not stripped:
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if re.match(pattern, nxt) or (nxt.startswith(" ") and items):
                i += 1
                continue
            break
        m = re.match(pattern, stripped)
        if m:
            items.append(m.group(1).strip())
            i += 1
            continue
        if items and (raw.startswith("  ") or raw.startswith("\t")):
            if re.match(r"^[-*]\s+\S", stripped) or re.match(r"^\d+\.\s+\S", stripped):
                items.append("– " + re.sub(r"^([-*]|\d+\.)\s+", "", stripped))
            else:
                items[-1] += " " + stripped
            i += 1
            continue
        break
    return items, i


def parse_quote_body(quote_lines: list[str]) -> list[tuple[str, str]]:
    """Split a blockquote into ('para'|'bullet', text) pairs."""
    out: list[tuple[str, str]] = []
    buf: list[str] = []
    for line in quote_lines:
        stripped = line.strip()
        if not stripped:
            if buf:
                out.append(("para", " ".join(buf)))
                buf.clear()
            continue
        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if buf:
                out.append(("para", " ".join(buf)))
                buf.clear()
            out.append(("bullet", m.group(1).strip()))
            continue
        if out and out[-1][0] == "bullet" and (line.startswith("  ") or line.startswith("\t")):
            out[-1] = ("bullet", out[-1][1] + " " + stripped)
            continue
        buf.append(stripped)
    if buf:
        out.append(("para", " ".join(buf)))
    return out


# ══════════════════════════════════════════════════════════════════
# inline markdown -> ReportLab markup
# ══════════════════════════════════════════════════════════════════
_CODE_TOKEN = "@@CODE%d@@"


def inline(text: str, *, base_font: str = "Body") -> str:
    """Convert bold/italic/code/links to ReportLab tags, escaping everything else."""
    codes: list[str] = []

    def stash(m: re.Match) -> str:
        codes.append(m.group(1))
        return _CODE_TOKEN % (len(codes) - 1)

    text = re.sub(r"`([^`]+)`", stash, text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Bind dashes to the preceding word so they can never start a line.
    text = re.sub(r"[ \t]+([—–])[ \t]+", " \\1 ", text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<i>\1</i>", text)

    for idx, code in enumerate(codes):
        rendered = (
            '<font name="Mono" size="9" backColor="#eef1f2"> '
            + html.escape(code, quote=False)
            + " </font>"
        )
        text = text.replace(_CODE_TOKEN % idx, rendered)
    return fallback_glyphs(text, base_font)


def fallback_glyphs(markup: str, base_font: str) -> str:
    """Wrap characters the base font cannot draw in a font that can."""
    table = pdfmetrics.getFont(base_font).face.charToGlyph
    fb = pdfmetrics.getFont(FALLBACK_FONT).face.charToGlyph
    out: list[str] = []
    in_tag = False
    for ch in markup:
        if ch == "<":
            in_tag = True
        elif ch == ">":
            in_tag = False
        if in_tag or ch == ">" or ord(ch) < 128 or ord(ch) in table or ord(ch) not in fb:
            out.append(ch)
        else:
            out.append('<font name="%s">%s</font>' % (FALLBACK_FONT, ch))
    return "".join(out)


# ══════════════════════════════════════════════════════════════════
# styles
# ══════════════════════════════════════════════════════════════════
MARGIN_X = 2.2 * cm
MARGIN_TOP = 2.5 * cm
MARGIN_BOTTOM = 1.85 * cm
CONTENT_W = A4[0] - 2 * MARGIN_X

S = {
    "kicker": ParagraphStyle(
        "kicker", fontName="Display-Bold", fontSize=10, leading=13,
        textColor=ACCENT, spaceAfter=6,
    ),
    "h1": ParagraphStyle(
        "h1", fontName="Display-Bold", fontSize=23, leading=28,
        textColor=HEADER_FILL, spaceBefore=0, spaceAfter=4,
    ),
    "h2": ParagraphStyle(
        "h2", fontName="Display-Bold", fontSize=14.5, leading=19,
        textColor=HEADER_FILL, spaceBefore=15, spaceAfter=6,
    ),
    "h3": ParagraphStyle(
        "h3", fontName="Display-Bold", fontSize=11.5, leading=15,
        textColor=ACCENT, spaceBefore=11, spaceAfter=4,
    ),
    "body": ParagraphStyle(
        "body", fontName="Body", fontSize=10.5, leading=16.5,
        textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceAfter=8,
        allowWidows=0, allowOrphans=0,
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName="Body", fontSize=10.5, leading=15.5,
        textColor=TEXT_PRIMARY, alignment=TA_LEFT,
        bulletFontName="Body", bulletFontSize=10.5,
        leftIndent=16, bulletIndent=4, spaceBefore=1, spaceAfter=3.5,
    ),
    "quote_para": ParagraphStyle(
        "quote_para", fontName="Body", fontSize=10, leading=15.5,
        textColor=TEXT_PRIMARY, alignment=TA_LEFT, spaceAfter=5,
    ),
    "quote_bullet": ParagraphStyle(
        "quote_bullet", fontName="Body", fontSize=10, leading=15.5,
        textColor=TEXT_PRIMARY, alignment=TA_LEFT,
        bulletFontName="Body", bulletFontSize=10,
        leftIndent=13, bulletIndent=2, spaceBefore=1, spaceAfter=3,
    ),
    "th": ParagraphStyle(
        "th", fontName="Display-Bold", fontSize=9.5, leading=12.5,
        textColor=colors.white, alignment=TA_LEFT,
    ),
    "td": ParagraphStyle(
        "td", fontName="Body", fontSize=9.5, leading=13.5,
        textColor=TEXT_PRIMARY, alignment=TA_LEFT,
    ),
    "toc_title": ParagraphStyle(
        "toc_title", fontName="Display-Bold", fontSize=19, leading=24,
        textColor=HEADER_FILL, spaceAfter=4,
    ),
    "code": ParagraphStyle(
        "code", fontName="Mono", fontSize=9, leading=14,
        textColor=TEXT_PRIMARY, alignment=TA_LEFT, wordWrap="LTR",
    ),
}

TOC_LEVELS = [
    ParagraphStyle("toc0", fontName="Display-Bold", fontSize=11, leading=20,
                   textColor=HEADER_FILL, leftIndent=0, spaceBefore=7),
    ParagraphStyle("toc1", fontName="Display", fontSize=9.8, leading=15.5,
                   textColor=TEXT_PRIMARY, leftIndent=16),
]

# Styles active for the chapter currently being rendered. The auto-fit pass swaps in
# slightly tightened copies for chapters whose tail spills a nearly empty page.
CUR = dict(S)
SQUEEZE_KEYS = ("body", "bullet", "quote_para", "quote_bullet")


def scaled_styles(factor: float) -> dict:
    """Copy of S with body leading/spacing tightened by `factor` (0.0 = untouched)."""
    if not factor:
        return dict(S)
    out = dict(S)
    for key in SQUEEZE_KEYS:
        base = S[key]
        out[key] = ParagraphStyle(
            key + "_sq", parent=base,
            leading=base.leading * (1 - factor),
            spaceAfter=max(base.spaceAfter * (1 - 2 * factor), 2),
        )
    return out

# ══════════════════════════════════════════════════════════════════
# custom flowables
# ══════════════════════════════════════════════════════════════════
class CalloutBox(Flowable):
    """Tinted panel with an accent left border, for the 'masalahnya apa' drawers."""

    PAD_X = 11
    PAD_Y = 9
    BAR = 3.2

    def __init__(self, flowables, width, bg=CARD_BG, bar=ACCENT):
        super().__init__()
        self.flowables = flowables
        self.width = width
        self.bg = bg
        self.bar = bar
        self._heights: list[float] = []

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        inner = self.width - 2 * self.PAD_X - self.BAR
        total = 0.0
        self._heights = []
        for f in self.flowables:
            _, h = f.wrap(inner, availHeight)
            self._heights.append(h)
            total += h
        self.height = total + 2 * self.PAD_Y
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.bg)
        c.rect(0, 0, self.width, self.height, stroke=0, fill=1)
        c.setFillColor(self.bar)
        c.rect(0, 0, self.BAR, self.height, stroke=0, fill=1)
        c.restoreState()
        y = self.height - self.PAD_Y
        x = self.BAR + self.PAD_X
        inner = self.width - 2 * self.PAD_X - self.BAR
        for f, h in zip(self.flowables, self._heights):
            y -= h
            f.drawOn(c, x, y)

    def split(self, availWidth, availHeight):
        return []


def callout(pairs: list[tuple[str, str]]) -> CalloutBox:
    inner_w = CONTENT_W - 2 * CalloutBox.PAD_X - CalloutBox.BAR
    flows: list[Flowable] = []
    for kind, text in pairs:
        if kind == "bullet":
            flows.append(Paragraph(inline(text), CUR["quote_bullet"], bulletText="•"))
        else:
            flows.append(Paragraph(inline(text), CUR["quote_para"]))
    if flows:
        last = flows[-1]
        if isinstance(last, Paragraph):
            last.style = ParagraphStyle("q_last", parent=last.style, spaceAfter=0)
    _ = inner_w
    return CalloutBox(flows, CONTENT_W)


def code_block(text: str) -> Table:
    """Fenced code: mono on a light tint with an accent left rule."""
    body = html.escape(text, quote=False).replace("\n", "<br/>")
    body = body.replace(" ", " ")
    cell = Paragraph(fallback_glyphs(body, "Mono"), S["code"])
    t = Table([[cell]], colWidths=[CONTENT_W], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SECTION_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3.2, ICON),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def make_table(rows: list[list[str]]) -> Table:
    n = len(rows[0])
    weights = []
    for col in range(n):
        longest = max(len(r[col]) for r in rows)
        weights.append(max(longest, 6))
    total = sum(weights)
    widths = [CONTENT_W * w / total for w in weights]
    floor = CONTENT_W * 0.10
    if min(widths) < floor:
        widths = [max(w, floor) for w in widths]
        scale = CONTENT_W / sum(widths)
        widths = [w * scale for w in widths]

    data = [[Paragraph(inline(c, base_font="Display"), S["th"]) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(inline(c), S["td"]) for c in r])

    t = Table(data, colWidths=widths, hAlign="CENTER", repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_FILL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, BORDER),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
    ]
    for idx in range(1, len(data)):
        if idx % 2 == 0:
            style.append(("BACKGROUND", (0, idx), (-1, idx), TABLE_STRIPE))
    t.setStyle(TableStyle(style))
    return t


MAX_KEEP = A4[1] * 0.4


def safe_keep(flows: list[Flowable]) -> list[Flowable]:
    total = 0.0
    for f in flows:
        try:
            _, h = f.wrap(CONTENT_W, A4[1])
        except Exception:
            return list(flows)
        total += h
    if total <= MAX_KEEP:
        return [KeepTogether(flows)]
    if len(flows) >= 2:
        return [KeepTogether(flows[:2])] + list(flows[2:])
    return list(flows)


# ══════════════════════════════════════════════════════════════════
# document template: running head/foot + TOC notifications
# ══════════════════════════════════════════════════════════════════
import hashlib


class BookDoc(BaseDocTemplate):
    """Draws furniture at page END so the running head knows the page's chapter."""

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)
        self.running_label = ""
        frame = Frame(
            MARGIN_X, MARGIN_BOTTOM, CONTENT_W,
            A4[1] - MARGIN_TOP - MARGIN_BOTTOM, id="body",
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )
        self.addPageTemplates([
            PageTemplate(id="book", frames=[frame], onPageEnd=draw_furniture)
        ])

    def beforeDocument(self):
        self.running_label = ""

    def afterFlowable(self, flowable):
        label = getattr(flowable, "chapter_label", None)
        if label is not None:
            self.running_label = label
        if hasattr(flowable, "bookmark_text"):
            # +1 because the cover is merged in front of this body PDF later, which is
            # also why draw_furniture prints page + 1 in the footer.
            self.notify(
                "TOCEntry",
                (flowable.bookmark_level, flowable.bookmark_text,
                 self.page + 1, flowable.bookmark_key),
            )


def draw_furniture(canvas, doc):
    canvas.saveState()
    page = canvas.getPageNumber()
    label = doc.running_label
    left = A4[0] - MARGIN_X
    top_y = A4[1] - MARGIN_TOP + 20

    canvas.setFont("Display", 7.5)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(MARGIN_X, top_y, BOOK_TITLE)
    if label:
        canvas.drawRightString(left, top_y, label)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN_X, top_y - 5, left, top_y - 5)

    foot_y = MARGIN_BOTTOM - 22
    canvas.line(MARGIN_X, foot_y + 12, left, foot_y + 12)
    canvas.setFont("Display", 7.5)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(MARGIN_X, foot_y, BOOK_SERIES)
    canvas.setFont("Display-Bold", 8.5)
    canvas.setFillColor(ACCENT)
    canvas.drawRightString(left, foot_y, "%d" % (page + 1))  # +1: cover merged later
    canvas.restoreState()


def toc_text(raw: str) -> str:
    """Heading text as it should read in the TOC: no markdown, no missing glyphs."""
    clean = re.sub(r"<[^>]+>", "", raw)
    clean = clean.replace("**", "").replace("*", "").replace("`", "")
    clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
    return html.escape(clean.strip(), quote=False)


def heading_flowable(text: str, level: int, *, toc_level: int | None = None) -> Paragraph:
    style = S["h1"] if level == 1 else S["h2"] if level == 2 else S["h3"]
    key = "h_" + hashlib.md5(("%d|%s" % (level, text)).encode("utf-8")).hexdigest()[:10]
    p = Paragraph('<a name="%s"/>%s' % (key, inline(text, base_font="Display")), style)
    if toc_level is not None:
        p.bookmark_level = toc_level
        p.bookmark_text = toc_text(text)
        p.bookmark_key = key
    return p


def tech_aside_heading(text: str) -> list[Flowable]:
    """The optional AI/NLP sidebar heading gets a tinted full-width band."""
    clean = text.replace("BAGI YANG MAU LEBIH DALAM", "BAGI YANG MAU LEBIH DALAM").strip()
    clean = re.sub(r"^[:\s—-]+", "", clean)
    label = Paragraph(
        inline("UNTUK YANG INGIN LEBIH TEKNIS", base_font="Display"),
        ParagraphStyle("aside_kicker", fontName="Display-Bold", fontSize=8,
                       leading=11, textColor=colors.white),
    )
    title = Paragraph(
        inline(clean.split(":", 1)[-1].strip() if ":" in clean else clean, base_font="Display"),
        ParagraphStyle("aside_title", fontName="Display-Bold", fontSize=12.5,
                       leading=16, textColor=colors.white),
    )
    band = Table([[label], [title]], colWidths=[CONTENT_W], hAlign="CENTER")
    band.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HEADER_FILL),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (0, 0), 8),
        ("BOTTOMPADDING", (0, 0), (0, 0), 1),
        ("TOPPADDING", (0, 1), (0, 1), 0),
        ("BOTTOMPADDING", (0, 1), (0, 1), 9),
    ]))
    return [Spacer(1, 16), band, Spacer(1, 11)]


# ══════════════════════════════════════════════════════════════════
# story assembly
# ══════════════════════════════════════════════════════════════════
def render_blocks(blocks: list[Block], kicker: str, running: str,
                  chapter_title: str) -> list[Flowable]:
    story: list[Flowable] = []
    first_heading_done = False
    pending_band: list[Flowable] = []
    exercise: list[Flowable] = []
    in_exercise = False

    def emit(flows: list[Flowable]) -> None:
        """Route output into the exercise group when one is open."""
        nonlocal pending_band
        if pending_band:
            flows = pending_band + flows
            pending_band = []
        (exercise if in_exercise else story).extend(flows)

    for b in blocks:
        if b.kind == "heading":
            if b.level == 1 and not first_heading_done:
                first_heading_done = True
                k = Paragraph(inline(kicker, base_font="Display"), S["kicker"])
                k.chapter_label = running
                h = heading_flowable(chapter_title, 1, toc_level=0)
                rule = HRFlowable(width="100%", thickness=2.2, color=ACCENT,
                                  spaceBefore=7, spaceAfter=15)
                story.extend([k, h, rule])
                continue
            if in_exercise:
                story.extend(safe_keep(exercise))
                exercise = []
                in_exercise = False
            if b.flag == "tech":
                # Band must not sit alone at the foot of a page.
                story.append(CondPageBreak(5.5 * cm))
                pending_band = tech_aside_heading(b.text)
                continue
            if b.level == 2:
                story.append(CondPageBreak(3.2 * cm))
                emit([heading_flowable(b.text, 2, toc_level=1)])
                continue
            emit([heading_flowable(b.text, min(b.level, 3))])
            continue

        if b.kind == "para":
            if not in_exercise and EXERCISE_RE.match(b.text) and not pending_band:
                in_exercise = True
            emit([Paragraph(inline(b.text), CUR["body"])])
            continue

        if b.kind == "list":
            flows: list[Flowable] = []
            for n, item in enumerate(b.items, 1):
                bullet = "%d." % n if b.flag == "ol" else "•"
                flows.append(Paragraph(inline(item), CUR["bullet"], bulletText=bullet))
            flows.append(Spacer(1, 5))
            emit(flows)
            continue

        if b.kind == "quote":
            emit([Spacer(1, 3), callout(b.items), Spacer(1, 13)])
            continue

        if b.kind == "code":
            emit([Spacer(1, 4), code_block(b.text), Spacer(1, 13)])
            continue

        if b.kind == "table":
            emit([Spacer(1, 6), make_table(b.rows), Spacer(1, 15)])
            continue

    if pending_band:
        story.extend(pending_band)
    if exercise:
        story.extend(safe_keep(exercise))
    return story


def build_toc_page() -> list[Flowable]:
    toc = TableOfContents()
    toc.levelStyles = TOC_LEVELS
    toc.dotsMinLevel = 0
    return [
        Paragraph(inline("Daftar Isi", base_font="Display"), S["toc_title"]),
        HRFlowable(width="100%", thickness=2.2, color=ACCENT, spaceBefore=5, spaceAfter=14),
        toc,
        PageBreak(),
    ]


def chapter_story(stem: str, kicker: str, running: str, title: str,
                  squeeze: float = 0.0) -> list[Flowable]:
    """Render one chapter, optionally with tightened body leading."""
    global CUR
    CUR = scaled_styles(squeeze)
    src = os.path.join(REPORTS, stem + ".md")
    with open(src, encoding="utf-8") as fh:
        blocks = parse_markdown(fh.read())
    out = render_blocks(blocks, kicker, running, title)
    CUR = dict(S)
    return out


def measure_pages(stem: str, kicker: str, running: str, title: str,
                  squeeze: float) -> int:
    """Page count of a chapter on its own. Builds throwaway flowables: ReportLab
    mutates flowables while laying them out, so a measured story cannot be reused."""
    import io

    probe = BookDoc(
        io.BytesIO(), pagesize=A4,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
    )
    probe.build(chapter_story(stem, kicker, running, title, squeeze))
    return probe.page


def fit_chapter(stem: str, kicker: str, running: str, title: str) -> list[Flowable]:
    """Tighten a chapter only when that removes a page whose tail was nearly empty."""
    base_pages = measure_pages(stem, kicker, running, title, 0.0)
    for squeeze in (0.045, 0.075):
        if measure_pages(stem, kicker, running, title, squeeze) < base_pages:
            print("    %-42s %d -> %d pages (tightened %.1f%%)"
                  % (stem, base_pages, base_pages - 1, squeeze * 100))
            return chapter_story(stem, kicker, running, title, squeeze)
    return chapter_story(stem, kicker, running, title, 0.0)


def build_body(path: str) -> None:
    doc = BookDoc(
        path, pagesize=A4,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
        title=BOOK_TITLE, author="Tim ACOS-ASLI",
        creator="Tim ACOS-ASLI", subject=BOOK_SUBTITLE,
    )
    story: list[Flowable] = build_toc_page()

    for n, (stem, kicker, running, title) in enumerate(CHAPTERS):
        if n:
            story.append(PageBreak())
        story.extend(fit_chapter(stem, kicker, running, title))

    doc.multiBuild(story)


def merge_cover(cover_pdf: str, body_pdf: str, out_pdf: str) -> int:
    from pypdf import PdfReader, PdfWriter, Transformation

    a4 = (595.276, 841.89)

    def norm(page):
        box = page.mediabox
        w, h = float(box.width), float(box.height)
        if abs(w - a4[0]) > 2 or abs(h - a4[1]) > 2:
            page.add_transformation(Transformation().scale(a4[0] / w, a4[1] / h))
            page.mediabox.lower_left = (0, 0)
            page.mediabox.upper_right = a4
        return page

    writer = PdfWriter()
    writer.add_page(norm(PdfReader(cover_pdf).pages[0]))
    for page in PdfReader(body_pdf).pages:
        writer.add_page(norm(page))
    writer.add_metadata({
        "/Title": "%s — %s" % (BOOK_TITLE, BOOK_SUBTITLE),
        "/Author": "Tim ACOS-ASLI",
        "/Creator": "Tim ACOS-ASLI",
        "/Subject": "Panduan anotasi manual ACOSE (quintuple ABSA) untuk bahasa Indonesia",
        "/Keywords": "ACOSE, ACOS, ABSA, anotasi, sentimen, emosi, bahasa Indonesia, TTG",
    })
    with open(out_pdf, "wb") as fh:
        writer.write(fh)
    return len(writer.pages)


def main() -> None:
    register_fonts()
    os.makedirs(OUT_DIR, exist_ok=True)
    body = os.path.join(OUT_DIR, "_body.pdf")
    build_body(body)
    print("body built:", body)


if __name__ == "__main__":
    main()
