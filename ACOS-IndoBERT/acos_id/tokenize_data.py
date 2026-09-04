"""Generator `tokenized_data/` — deliverable D3 dari PRD IndoBERT.

Dua keluaran per split, meniru berkas yang sudah ada di repo untuk rest16:

1. `<domain>_<split>_quad_bert.tsv` — teks sudah ter-WordPiece, span di-remap ke
   indeks token WordPiece. Dipakai Step 1 (co-extraction).
2. `<domain>_<split>_pair.tsv` — `teks####<a_span> <o_span>\\t<KAT#SENTI> ...`,
   satu baris per pasangan (aspek, opini) unik. Dipakai Step 2.

Konvensi offset yang sudah diverifikasi terhadap berkas repo: `st` inklusif,
`ed` eksklusif, keduanya indeks **whitespace-token pada teks yang SUDAH
ter-WordPiece** (`yum !` span `0,1` → `yu ##m !` span `0,2`). Bukan indeks
karakter, bukan indeks subword hasil tokenizer runtime.

Tokenizer diterima sebagai parameter, bukan dikunci ke IndoBERT: satu-satunya
yang dituntut adalah `tokenize(word) -> list[str]`. Ini yang membuat gate 2
(regenerasi data Inggris dengan vocab `bert-base-uncased` lalu dibandingkan
dengan berkas repo) bisa dijalankan dengan fungsi yang sama, dan membuat
pembanding XLM-R nanti tidak menuntut generator baru.
"""
from __future__ import annotations

import collections
import json
import os
import sys

from .taxonomy import DOMAIN

UNK = "[UNK]"

SPLITS = ("train", "dev", "test")


def retokenize_line(tokenizer, text: str, quads: list):
    """Ubah satu baris ACOS mentah menjadi versi ter-WordPiece.

    Mengembalikan `(new_text, new_quads, info)`; `info` mencatat jumlah `[UNK]`
    yang disisipkan dan jumlah span yang bergeser.
    """
    words = text.strip().split()
    pieces = []
    start_of = []          # start_of[i] = indeks subword pertama untuk words[i]
    end_of = []            # end_of[i]   = indeks setelah subword terakhir
    n_unk = 0

    for word in words:
        sub = tokenizer.tokenize(word)
        if not sub:
            # Tokenizer bisa mengembalikan daftar kosong untuk karakter kontrol.
            # Sisipkan [UNK] supaya indeks tidak bergeser — tanpa ini seluruh
            # span setelahnya salah, dan kesalahannya tidak terlihat di mana pun.
            sub = [UNK]
            n_unk += 1
        start_of.append(len(pieces))
        pieces.extend(sub)
        end_of.append(len(pieces))

    def remap(span: str):
        st_s, ed_s = span.split(",")
        st, ed = int(st_s), int(ed_s)
        if st < 0 or ed < 0:
            return span, False
        if st >= len(words) or ed > len(words):
            return None, False
        if ed <= st:
            # Span lebar-nol (`3,3`) ada di data upstream — satu kali di
            # rest16_quad_train.tsv baris 451. Berkas repo memetakannya menjadi
            # satu subword (`3,4`), bukan membuangnya, dan pembentuk fitur
            # upstream memang memberi label B-A tanpa I-A untuk kasus ini
            # (`run_classifier_dataset_utils.py:308`). Diikuti apa adanya supaya
            # regenerasi data Inggris tetap identik dengan berkas repo.
            new = f"{start_of[st]},{start_of[st] + 1}"
            return new, new != span
        new = f"{start_of[st]},{end_of[ed - 1]}"
        return new, new != span

    new_quads = []
    n_shift = 0
    n_bad = 0
    for quad in quads:
        parts = quad.split(" ")
        if len(parts) != 4:
            n_bad += 1
            continue
        asp, cat, senti, opi = parts
        new_asp, sh_a = remap(asp)
        new_opi, sh_o = remap(opi)
        if new_asp is None or new_opi is None:
            n_bad += 1
            continue
        n_shift += int(sh_a) + int(sh_o)
        new_quads.append(f"{new_asp} {cat} {senti} {new_opi}")

    info = {"n_unk": n_unk, "n_shift": n_shift, "n_span_invalid": n_bad,
            "n_pieces": len(pieces)}
    return " ".join(pieces), new_quads, info


def pair_lines_from_quads(text: str, quads: list):
    """Baris `*_pair.tsv` untuk **satu** kalimat (dipakai pengujian & inferensi).

    Untuk membangun berkas split gunakan `build_split`, yang mengelompokkan
    secara global — lihat catatan di `_PairAccumulator`.
    """
    acc = _PairAccumulator()
    acc.add(text, quads)
    return acc.lines()


class _PairAccumulator:
    """Pengelompokan pasangan `(teks, span_aspek, span_opini)` **lintas baris**.

    Aturan ini dipulihkan dengan membandingkan berkas repo terhadap
    `*_quad_bert.tsv`-nya, bukan dari dokumentasi. Dua hal yang tidak terduga:

    1. Kunci pengelompokan mencakup **teks**, sehingga dua baris quad berbeda
       dengan kalimat identik menyatu menjadi satu baris pair. Itulah asal
       `FOOD#QUALITY#2 FOOD#QUALITY#2` pada baris pertama
       `rest16_test_pair.tsv`: kalimat `yu ##m !` muncul dua kali di berkas quad,
       masing-masing satu quad. Label duplikat dibiarkan; `read_pair_gold()`
       men-dedup saat membaca (`dataset_utils.py:25`).
    2. Urutan baris di dalam satu kalimat dikelompokkan **per label** (urutan
       kemunculan pertama label itu), bukan urutan quad apa adanya. Tanpa aturan
       ini 20 dari 2.279 kalimat rest16 keluar dengan urutan berbeda dari berkas
       repo — cukup untuk membuat gate 2 gagal walau isinya sama.
    """

    def __init__(self):
        self._texts = collections.OrderedDict()

    def add(self, text: str, quads: list):
        entry = self._texts.setdefault(
            text, {"labels": collections.OrderedDict(), "pairs": collections.OrderedDict()})
        for quad in quads:
            asp, cat, senti, opi = quad.split(" ")
            label = f"{cat}#{senti}"
            key = (asp, opi)
            entry["pairs"].setdefault(key, []).append(label)
            slot = entry["labels"].setdefault(label, [])
            if key not in slot:
                slot.append(key)

    def lines(self):
        out = []
        for text, entry in self._texts.items():
            emitted = set()
            for keys in entry["labels"].values():
                for key in keys:
                    if key in emitted:
                        continue
                    emitted.add(key)
                    asp, opi = key
                    labels = " ".join(entry["pairs"][key])
                    out.append(f"{text}####{asp} {opi}\t{labels}")
        return out

    def __len__(self):
        return sum(len(e["pairs"]) for e in self._texts.values())


def build_split(tokenizer, in_path: str, quad_out: str, pair_out: str):
    """Proses satu split; kembalikan laporan."""
    rep = collections.Counter()
    len_hist = collections.Counter()
    pairs = _PairAccumulator()

    os.makedirs(os.path.dirname(quad_out), exist_ok=True)
    with open(in_path, encoding="utf-8") as fin, \
            open(quad_out, "w", encoding="utf-8", newline="\n") as fq:
        for raw in fin:
            raw = raw.rstrip("\n")
            if not raw.strip():
                rep["baris_kosong_dilewati"] += 1
                continue
            parts = raw.split("\t")
            text, quads = parts[0], parts[1:]
            if not quads:
                rep["baris_tanpa_quad_dilewati"] += 1
                continue

            new_text, new_quads, info = retokenize_line(tokenizer, text, quads)
            if not new_quads:
                rep["baris_dibuang_semua_span_invalid"] += 1
                continue

            rep["baris"] += 1
            rep["quad"] += len(new_quads)
            rep["unk_disisipkan"] += info["n_unk"]
            rep["span_bergeser"] += info["n_shift"]
            rep["span_invalid"] += info["n_span_invalid"]
            n_pieces = info["n_pieces"]
            len_hist[min(n_pieces // 16 * 16, 256)] += 1
            if n_pieces > 126:
                rep["baris_lebih_126_subword"] += 1

            fq.write(new_text + "\t" + "\t".join(new_quads) + "\n")
            pairs.add(new_text, new_quads)

    with open(pair_out, "w", encoding="utf-8", newline="\n") as fp:
        for line in pairs.lines():
            fp.write(line + "\n")
    rep["pair"] = len(pairs)

    out = dict(rep)
    out["histogram_panjang_subword"] = {str(k): v for k, v in sorted(len_hist.items())}
    out["berkas"] = {"quad_bert": quad_out, "pair": pair_out}
    return out


def build(tokenizer, data_dir: str, out_dir: str, *, domain: str = DOMAIN,
          splits=SPLITS, report_path: str = None) -> dict:
    """Bangun `tokenized_data/` untuk seluruh split.

    `data_dir` memuat `<domain>_quad_<split>.tsv`; `out_dir` adalah folder
    `tokenized_data/` tujuan.
    """
    report = {"domain": domain, "sumber": data_dir, "keluaran": out_dir,
              "vocab_entries": len(getattr(tokenizer, "vocab", {}) or {}),
              "split": {}}
    for split in splits:
        in_path = os.path.join(data_dir, f"{domain}_quad_{split}.tsv")
        if not os.path.exists(in_path):
            report["split"][split] = {"error": f"tidak ada: {in_path}"}
            continue
        report["split"][split] = build_split(
            tokenizer, in_path,
            os.path.join(out_dir, f"{domain}_{split}_quad_bert.tsv"),
            os.path.join(out_dir, f"{domain}_{split}_pair.tsv"),
        )

    if report_path is None:
        report_path = os.path.join(out_dir, f"_build_report_{domain}.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False, sort_keys=True)
    report["laporan"] = report_path
    return report


def load_legacy_tokenizer(vocab_dir: str, *, do_lower_case: bool = True):
    """`BertTokenizer` legacy dari folder berisi `vocab.txt`.

    Impor ditunda ke dalam fungsi agar modul ini tetap bisa diimpor di mesin
    tanpa dependensi `bert_utils` (mis. saat hanya `pair_lines_from_quads` yang
    diuji).
    """
    from bert_utils.tokenization import BertTokenizer

    return BertTokenizer.from_pretrained(vocab_dir, do_lower_case=do_lower_case)


def main(argv=None):
    """CLI: `python -m acos_id.tokenize_data <vocab_dir> <data_dir> <out_dir> [domain]`."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 3:
        print(__doc__)
        print("Pemakaian: python -m acos_id.tokenize_data <vocab_dir> <data_dir> "
              "<out_dir> [domain]")
        return 2
    vocab_dir, data_dir, out_dir = argv[0], argv[1], argv[2]
    domain = argv[3] if len(argv) > 3 else DOMAIN

    tokenizer = load_legacy_tokenizer(vocab_dir)
    rep = build(tokenizer, data_dir, out_dir, domain=domain)
    print(f"Vocab  : {vocab_dir} ({rep['vocab_entries']:,} entri)")
    for split, s in rep["split"].items():
        if "error" in s:
            print(f"  {split:5s} DILEWATI — {s['error']}")
            continue
        print(f"  {split:5s} {s.get('baris', 0):6d} baris, {s.get('quad', 0):6d} quad, "
              f"{s.get('pair', 0):6d} pair | [UNK]={s.get('unk_disisipkan', 0)} "
              f"span bergeser={s.get('span_bergeser', 0)} "
              f">126 subword={s.get('baris_lebih_126_subword', 0)}")
    print(f"  laporan: {rep['laporan']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
