"""Check every TOC entry's printed number against the footer number of the page
that actually carries the heading. That is the contract a reader sees."""
import re

import pymupdf

PDF = "dist/Panduan_Anotasi_ACOSE_Bahasa_Indonesia.pdf"
doc = pymupdf.open(PDF)
pages = [doc[i].get_text() for i in range(len(doc))]
first_chapter = next(i for i, t in enumerate(pages) if re.search(r"(?m)^PEMBUKA$", t))
print("TOC on PDF pages 2..%d, %d pages total" % (first_chapter, len(pages)))


def lines_by_row(page, y_tol=2.0):
    """Group words into visual rows so a title and its page number stay together."""
    rows: dict[float, list] = {}
    for x0, y0, x1, y1, word, *_ in page.get_text("words"):
        key = next((k for k in rows if abs(k - y0) <= y_tol), y0)
        rows.setdefault(key, []).append((x0, word))
    out = []
    for key in sorted(rows):
        words = [w for _, w in sorted(rows[key])]
        out.append(" ".join(words))
    return out


entries = []
for pno in range(1, first_chapter):
    for row in lines_by_row(doc[pno]):
        m = re.match(r"^(.*?)[\s.]*\.\s*(\d+)$", row)
        if not m:
            continue
        title = m.group(1).strip(" .")
        if title and title != "Daftar Isi":
            entries.append((title, int(m.group(2))))
print("entries parsed:", len(entries))

# Footer number printed on each PDF page (drawn bottom-right).
footer = {}
for i in range(len(pages)):
    rows = lines_by_row(doc[i])
    for row in reversed(rows):
        m = re.search(r"Seri 022\s+(\d+)$", row)
        if m:
            footer[i + 1] = int(m.group(1))
            break

bad = []
used: dict[str, int] = {}   # some headings repeat across chapters; consume them in order
for title, printed in entries:
    needle = re.sub(r"\s+", " ", title)[:30]
    # Search body pages only: the TOC itself repeats every heading title.
    found = [i + 1 for i in range(first_chapter, len(pages))
             if needle in re.sub(r"\s+", " ", pages[i])]
    if not found:
        bad.append((title, printed, "heading text not found in the body"))
        continue
    seen = used.get(needle, 0)
    target = found[seen] if seen < len(found) else found[-1]
    used[needle] = seen + 1
    want = footer.get(target)
    if want != printed:
        bad.append((title, printed, "heading is on PDF p%d, footer says %s"
                    % (target, want)))

print("mismatched entries:", len(bad))
for title, printed, why in bad[:10]:
    print("   %-50s TOC=%-3s %s" % (title[:50], printed, why))

print()
print("sample (title -> TOC number):")
for title, printed in entries[:4] + entries[-3:]:
    print("   %-60s %s" % (title[:60], printed))
doc.close()
