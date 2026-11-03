#!/usr/bin/env python3
"""Generator laporan 041 — analisis mendalam 45 notebook `.ipynb` + komparasi tabel.

Masukan : reports/041_data/*.csv (dihasilkan scripts/audit_041_notebooks.py)
Keluaran: reports/041_analisis_mendalam_notebook_02112026_HM.md
          reports/041_data/provenance_angka.csv
          reports/041_data/kontradiksi_angka.csv
          reports/041_data/subtask_15_perbandingan.csv

Jalankan: python3 scripts/gen_report_041.py
"""
from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "reports", "041_data")
OUT = os.path.join(ROOT, "reports", "041_analisis_mendalam_notebook_02112026_HM.md")


def read(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


INV = read("notebooks_inventaris.csv")
MET = read("notebooks_metrik.csv")
GALAT = read("notebooks_galat.csv")
JEJAK = read("notebooks_jejak.csv")
MIRIP = read("notebooks_kemiripan.csv")

# ---------------------------------------------------------------- turunan
def short(path: str, n: int = 52) -> str:
    b = path.split("/")[-1]
    return b if len(b) <= n else b[: n - 1] + "…"


PERAN = [
    (lambda b: b == "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb", "Kanonik (IndoBERT 0509)"),
    (lambda b: b.startswith("00_ACOS_Master_Pipeline_Colab_V4_1_INDOBERT"), "Echo cache 67,86"),
    (lambda b: b.startswith("00_ACOS_Master_Pipeline_Colab_V4_2"), "Echo cache 67,86"),
    (lambda b: b.startswith("00_ACOS_Master_Pipeline_Colab_V4_3"), "Echo cache 67,86"),
    (lambda b: "V4_INDOBERT copy" in b, "Output yatim (2 sel jalan)"),
    (lambda b: "V4_INDOBERT_run08092026" in b, "Cache sesi 2409 (67,69)"),
    (lambda b: "V4_BERT_rest16" in b, "Gate-1 gagal, lanjut eval"),
    (lambda b: "run24092026" in b, "Pair-eval 2409 (67,69)"),
    (lambda b: "V5_EN_REST16" in b, "Kontaminasi lintas domain"),
    (lambda b: "Kaggle" in b, "Kerangka (0 sel)"),
    (lambda b: b == "00_ACOS_Master_Pipeline_Colab.ipynb", "Kanonik parsial (Step-2 0,00)"),
    (lambda b: b.startswith("00_ACOS_Master_Pipeline_Colab_ASLI"), "Kerangka"),
    (lambda b: b.startswith("00_ACOS_Master_Pipeline_Colab_PRO"), "Kerangka"),
    (lambda b: b.startswith("00_ACOS_Master_Pipeline_Colab_UPDATE"), "Output yatim + KeyError"),
    (lambda b: b.startswith("00_ACOS_Master_Pipeline_Colab_V2"), "Kerangka"),
    (lambda b: b.startswith("00_ACOS_Master_Pipeline_Colab_V3"), "Kerangka"),
    (lambda b: b.startswith("V4_1_01"), "Kanonik setup"),
    (lambda b: b.startswith("V4_1_02"), "Kerangka + error"),
    (lambda b: b.startswith("V4_1_03"), "Kanonik (1 epoch)"),
    (lambda b: b.startswith("V4_1_04"), "Kanonik eval (2× jalan)"),
    (lambda b: b.startswith("V4_2_05"), "Duplikat V4_1_03"),
    (lambda b: b.startswith("V4_2_06"), "Duplikat V4_1_04"),
    (lambda b: b.startswith("01_ACOS_Setup"), "Kanonik EDA"),
    (lambda b: b.startswith("02_ACOS_Step1"), "Kanonik 15 epoch"),
    (lambda b: b.startswith("03_ACOS_Step1_to"), "Kanonik pair-gen"),
    (lambda b: b.startswith("04_ACOS_Step2"), "Kanonik 15 epoch"),
    (lambda b: b.startswith("05_ACOS_Evaluation"), "Kerangka + output yatim"),
    (lambda b: b.startswith("01_ACOS_MI300X"), "IndentationError"),
    (lambda b: b.startswith("01_ACOS_V5_1"), "3 sel, import gagal"),
    (lambda b: b.startswith("02_ACOS_V5_2_1"), "Dry-run grid 54"),
    (lambda b: b.startswith("02_ACOS_V5_2_"), "3 sel, import gagal"),
    (lambda b: b.startswith("03_ACOS_V5_3"), "Dry-run grid 54"),
    (lambda b: b == "GPU_Status.ipynb", "Utilitas"),
    (lambda b: True, "Kerangka V1 (0 sel)"),
]


def peran(path: str) -> str:
    b = path.split("/")[-1]
    for test, label in PERAN:
        if test(b):
            return label
    return "—"


def angka(r, key):
    try:
        return int(r[key])
    except (ValueError, TypeError):
        return 0


# keluarga (urutan sesuai jumlah sel)
FAM = defaultdict(lambda: dict(n=0, sel=0, kode=0, jalan=0, out=0, err=0, met=0, yatim=0))
for r in INV:
    f = FAM[r["keluarga"]]
    f["n"] += 1
    for k, src in (("sel", "sel"), ("kode", "sel_kode"), ("jalan", "sel_tereksekusi"),
                   ("out", "sel_beroutput"), ("err", "sel_error"), ("met", "jumlah_metrik")):
        f[k] += angka(r, src)
    f["yatim"] += angka(r, "sel_output_yatim")

TOT = dict(n=len(INV), sel=sum(f["sel"] for f in FAM.values()),
           kode=sum(f["kode"] for f in FAM.values()), jalan=sum(f["jalan"] for f in FAM.values()),
           out=sum(f["out"] for f in FAM.values()), err=len(GALAT),
           met=len(MET), yatim=sum(f["yatim"] for f in FAM.values()))

# ---------------------------------------------------------------- CSV turunan
PROV = [
    ("P01", "Step-1 97,94", "V4_INDOBERT", "46", "69",
     "8 baris riwayat; TP 16.514 / FP 434 / FN 259",
     "appsid_05092026_122741", "E2"),
    ("P02", "Step-1 97,94 (echo)", "V4_1_INDOBERT; V4_2_GUARDS; V4_3_SESSION",
     "58;58;58", "—", "'[CACHE HIT] 8 metrik … dimuat tanpa evaluasi ulang'",
     "appsid_05092026_122741", "E3"),
    ("P03", "Step-1 97,94 di sesi rest16", "V5_EN_REST16_LAPTOP", "48", "—",
     "riwayat 8 baris identik appsid, ditulis ke folder rest16",
     "rest16_12092026_104518", "E0"),
    ("P04", "Step-1 97,19", "run08092026; run24092026_MI300X", "45;45", "37;148",
     "'training Step 1 tidak dijalankan (cache hit) … 97.19% (epoch 3)'",
     "appsid_24092026_0901", "E3"),
    ("P05", "Step-2 67,16", "V4_INDOBERT", "67", "—",
     "Quad num 10.505; TP 6.552 / FP 3.953 / FN 2.454",
     "appsid_05092026_122741", "E2"),
    ("P06", "Step-2 67,86", "V4_1_03_step2_train", "19", "41",
     "1 epoch; loss 0,554376; TP 6.654 / FP 3.951 / FN 2.352; VRAM 3.971 MB",
     "appsid_08092026_150437", "E2"),
    ("P07", "Step-2 67,86 (echo)", "V4_1_INDOBERT; V4_2_GUARDS; V4_3_SESSION; V4_1_04; V4_2_06",
     "71;71;71;8;11", "43;43;43;44;43",
     "'[CACHE HIT] 8 metrik keseluruhan, 15 sub-task'", "appsid_08092026_150437", "E3"),
    ("P08", "Step-2 67,69", "run08092026", "72", "51",
     "cache 6 metrik; TP 6.681 / FP 4.052 / FN 2.325", "appsid_24092026_0901", "E3"),
    ("P09", "Step-2 67,69 (hitung ulang)", "run24092026_MI300X", "72", "162",
     "pair_eval 687 batch; Quad num 10.733; TP/FP/FN sama dengan P08",
     "appsid_24092026_1426", "E2"),
    ("P10", "15 sub-task 66,28 / 96,29", "V4_1_04_eval_inference", "10", "52",
     "gold 19.528 (2,17× aplikasi), prediksi 24.066; P 63,94 / R 69,07",
     "appsid_08092026_150437", "E2"),
    ("P11", "15 sub-task 94,21 … 67,69", "run24092026_MI300X", "74", "163",
     "15 baris master_08; quad penuh 66,08 (rata-rata) vs 67,69 (micro)",
     "appsid_24092026_1426", "E2"),
    ("P12", "Step-1 81,27", "02_ACOS_Step1", "13", "8",
     "test: TP 1.367 / FP 382 / FN 248; P 78,16 / R 84,64; epoch terbaik 8",
     "rest16_31082026_144800", "E2"),
    ("P13", "Step-2 48,24", "04_ACOS_Step2", "10 & 12", "5 & 6",
     "Quad num 1.120; TP 486 / FP 634 / FN 409; epoch terbaik 12 dari 15",
     "rest16_02092026_135007", "E2"),
    ("P14", "15 sub-task rest16", "04_ACOS_Step2", "12", "6",
     "kategori 78,95 … quad penuh 48,24 (lihat Tabel 10)", "rest16_02092026_135007", "E2"),
    ("P15", "Step-1 81,23", "00_..._UPDATE", "13", "—",
     "15 epoch dijalankan, output tanpa ec; sesi hanya muncul di teks", "rest16_27082026_090134", "E1"),
    ("P16", "Step-1 80,76 / Step-2 0,00", "00_ACOS_Master_Pipeline_Colab", "12 & 16", "7 & 9",
     "1.450 pasangan tapi Quad num 301 → tp 0 / fp 301 / fn 895",
     "rest16_24092026_0849", "E2"),
    ("P17", "Step-2 0,00 + fp 165.728", "V5_EN_REST16_LAPTOP", "75", "—",
     "master_07: precision 0,00 / recall 0,00 / TP 0 / FP 165.728 / FN 895",
     "rest16_12092026_104518", "E0"),
    ("P18", "Grid 54 run", "V5.2.1; V5.3; V5.1; V5.2", "19;19;7;7", "10;—;52;52",
     "9 split-ratio + 45 CV hanya dicetak; DRY_RUN=True; 0 run selesai", "—", "E0"),
    ("P19", "Dual-head 0,00", "V4_1; V4_2; V4_3; V4_1_04; V4_2_06", "71;71;71;8;11", "43;43;43;44;43",
     "category/sentiment micro-F1 & accuracy = 0,00 (tidak terhitung)", "—", "E0"),
    ("P20", "47,68 (tanpa notebook)", "—", "—", "—",
     "hanya ada di Drive master_metrics.json; tidak ada sel yang mencetaknya", "rest16_27082026_070817", "E2"),
]

with open(os.path.join(DATA, "provenance_angka.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "angka", "notebook", "sel", "exec_count", "bukti_teks", "sesi", "tingkat"])
    w.writerows(PROV)

KONTRA = [
    ("C01", "Step-2 rest16", "48,24 (nb 04)", "47,68 (Drive 27/08)", "0,00 (V5_EN, cache appsid)",
     "Tiga nilai untuk klaim yang sama; 0,00 adalah artefak cache lintas domain"),
    ("C02", "Step-1 rest16", "81,27 (nb 02, 31/08)", "81,23 (UPDATE, 27/08)", "97,94 (V5_EN, cache appsid)",
     "Dua nilai wajar berdekatan (Δ0,04); 97,94 milik appsid"),
    ("C03", "Step-2 appsid", "67,16 (0509, 3 ep)", "67,86 (0809, 1 ep)", "67,69 (0901, 3 ep)",
     "TP+FN = 9.006 pada ketiganya, TP berbeda 6.552/6.654/6.681"),
    ("C04", "Step-1 appsid", "97,94 (0509, 8 ep)", "97,19 (0901, 3 ep)", "—",
     "Epoch lebih sedikit tetapi F1 hanya −0,75; tidak ada kurva 2409"),
    ("C05", "Jumlah metrik per sesi", "8 metrik (V4_1 echo)", "6 metrik (run0809)", "15 sub-task (V4_1_04)",
     "Jumlah metrik tersimpan berbeda antar sesi; '8' dan '6' tidak dapat dibandingkan langsung"),
    ("C06", "Quadruple rest16 vs appsid", "48,24 (nb 04)", "47,68 (Drive)", "66,28 (V4_1_04) / 47,03 (master_08 rest16)",
     "66,28 memakai gold 19.528 (2,17×) sehingga tidak sebanding"),
    ("C07", "Jumlah pasangan kandidat", "1.450 / 1.451 (rest16)", "10.735 / 10.991 (appsid + V5_EN)", "301 (rest16 24/09)",
     "Rasio pasangan:gold 1,6 vs 1,2 vs 12,0 → presisi anjlok pada 12,0"),
    ("C08", "Epoch Step-2 dijalankan", "15 (konfigurasi)", "3 (0509, 0901)", "1 (0809)",
     "Tidak ada bukti early-stop eksplisit; '1 epoch' adalah cache-hit yang dipakai ulang"),
    ("C09", "Artefak 15 sub-task rest16", "78,95/82,51/70,11 (nb 04, 02/09)", "78,72/81,93/69,56 (Drive, 27/08)", "—",
     "Dua run berbeda, selisih ≤0,55 poin → konsisten"),
    ("C10", "Status gate-1", "LULUS (V5_EN, IndoBERT)", "GAGAL (V4_BERT_rest16)", "LULUS (V5_EN rest16 BERT)",
     "Gate lulus/gagal tidak menghentikan eksekusi sel berikutnya"),
]

with open(os.path.join(DATA, "kontradiksi_angka.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "objek", "nilai_a", "nilai_b", "nilai_c", "catatan"])
    w.writerows(KONTRA)

SUBTASK = [
    ("opinion", 1, 94.21, 78.88), ("aspect", 1, 92.57, 78.31),
    ("category", 1, 91.84, 78.95), ("sentiment", 1, 85.72, 82.51),
    ("category + aspect", 2, 90.27, 67.24), ("sentiment + opinion", 2, 82.72, 71.74),
    ("category + opinion", 2, 81.37, 65.27), ("sentiment + aspect", 2, 80.01, 69.18),
    ("category + sentiment", 2, 79.47, 70.11), ("aspect + opinion", 2, 78.52, 57.87),
    ("category + sentiment + aspect", 3, 77.87, 60.28),
    ("category + aspect + opinion", 3, 76.56, 52.39),
    ("category + sentiment + opinion", 3, 70.73, 59.63),
    ("sentiment + aspect + opinion", 3, 67.92, 53.18),
    ("category + sentiment + aspect + opinion", 4, 66.08, 48.24),
]
with open(os.path.join(DATA, "subtask_15_perbandingan.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["subtask", "n_elemen", "indobert_appsid_f1", "bert_rest16_f1", "selisih"])
    for name, n, a, b in SUBTASK:
        w.writerow([name, n, f"{a:.2f}", f"{b:.2f}", f"{a - b:+.2f}"])


# ---------------------------------------------------------------- helper tabel
def tbl(header, rows, align=None):
    align = align or ["---"] * len(header)
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join(align) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "—"


# ---------------------------------------------------------------- T1
rows_t1 = []
for k, v in sorted(FAM.items(), key=lambda kv: -kv[1]["sel"]):
    rows_t1.append([k, v["n"], v["sel"], v["kode"], v["jalan"], pct(v["jalan"], v["kode"]),
                    v["out"], v["err"], v["met"], v["yatim"]])
rows_t1.append(["**Total (24 keluarga)**", TOT["n"], TOT["sel"], TOT["kode"], TOT["jalan"],
                pct(TOT["jalan"], TOT["kode"]), TOT["out"], TOT["err"], TOT["met"], TOT["yatim"]])

# ---------------------------------------------------------------- T2 (45 baris)
from collections import Counter as _C
_dupname = _C(os.path.basename(r["notebook"]) for r in INV)
rows_t2 = []
for i, r in enumerate(sorted(INV, key=lambda r: (r["keluarga"], r["notebook"])), 1):
    nm = r["notebook"] if _dupname[os.path.basename(r["notebook"])] > 1 else short(r["notebook"], 50)
    if _dupname[os.path.basename(r["notebook"])] > 1:
        nm = nm.replace("ACOS-IndoBERT/notebooks/", "").replace("kaggle/", "kaggle:")
    pr = peran(r["notebook"])
    if r["keluarga"] == "ACOS-BERT V1" and angka(r, "sel_tereksekusi") > 0:
        pr = "Kerangka V1 + 1 error"
    rows_t2.append([i, nm, r["keluarga"], r["sel"], r["sel_kode"],
                    r["sel_tereksekusi"], r["sel_output_yatim"],
                    r["sel_error"], r["jumlah_metrik"], pr])

# ---------------------------------------------------------------- T3 integritas
kotor = sorted(INV, key=lambda r: -angka(r, "sel_output_yatim"))[:10]
rows_t3 = []
for r in kotor:
    yatim = angka(r, "sel_output_yatim")
    rows_t3.append([short(r["notebook"], 50), r["sel_kode"], r["sel_tereksekusi"],
                    r["sel_kode_tanpa_eksekusi"], yatim, r["exec_tidak_monoton"], r["rentang_exec"]])

nol = [r for r in INV if angka(r, "sel_tereksekusi") == 0]
separuh = [r for r in INV if angka(r, "sel_kode") and angka(r, "sel_tereksekusi") / angka(r, "sel_kode") < 0.5]

# ---------------------------------------------------------------- T4 duplikasi
exact = defaultdict(list)
for r in INV:
    exact[r["hash_kode"]].append(r["notebook"])
exact = {h: v for h, v in exact.items() if len(v) > 1}
rows_t4 = []
for h, v in exact.items():
    rows_t4.append([h, short(v[0], 46), short(v[1], 46), "identik (sha1 16 char)"])
for r in MIRIP:
    j = float(r["jaccard_8gram"])
    if 0.90 <= j < 0.9999:
        rows_t4.append(["—", short(r["notebook_a"], 46), short(r["notebook_b"], 46), f"{j:.3f}"])

# ---------------------------------------------------------------- T5 provenance
rows_t5 = [[p[0], p[1], p[2], p[3], p[4], p[6], p[7]] for p in PROV]

# ---------------------------------------------------------------- T6 angka kembar
kembar = ["97,94", "97,19", "67,86", "67,69", "67,16", "66,28", "48,24", "47,68",
          "81,27", "81,23", "80,76", "78,95", "94,21"]
_TEXT = {}
for r in INV:
    try:
        with open(os.path.join(ROOT, r["notebook"]), encoding="utf-8") as fh:
            _TEXT[r["notebook"]] = fh.read()
    except OSError:
        _TEXT[r["notebook"]] = ""
rows_t6 = []
for a in kembar:
    dot = a.replace(",", ".")
    hit_nb = sorted(nb for nb, txt in _TEXT.items() if dot in txt)
    if hit_nb:
        rows_t6.append([a, len(hit_nb),
                        "; ".join(short(n, 40) for n in hit_nb[:4]) + (" …" if len(hit_nb) > 4 else "")])

# ---------------------------------------------------------------- T7 kontradiksi
rows_t7 = [[k[0], k[1], k[2], k[3], k[4], k[5]] for k in KONTRA]

# ---------------------------------------------------------------- T8 step-1
rows_t8 = [
    ["rest16 (BERT-base)", "02_ACOS_Step1", "31/08 14:48", 15, 8, "1.367 / 382 / 248",
     "78,16 / 84,64 / **81,27**", "15 epoch nyata; sel 11 (latih) + sel 13 (test)"],
    ["rest16 (BERT-base)", "UPDATE", "27/08 09:01", 15, 6, "1.326 / 324 / 289",
     "**81,23**", "output tanpa ec; KeyError 'a--1,-1' di sel 19"],
    ["rest16 (BERT-base)", "Colab dasar", "24/09 08:49", 15, 14, "1.339 / 362 / 276",
     "**80,76**", "sesi 24/09; Step-2 kolaps (Quad num 301)"],
    ["appsid (IndoBERT)", "V4_INDOBERT", "05/09 12:27", 8, 8, "16.514 / 434 / 259",
     "97,44 / 98,46 / **97,94**", "8 epoch; Step-2 hanya 3 epoch"],
    ["appsid (IndoBERT)", "run08092026 / MI300X", "24/09 09:01", 3, 3, "—",
     "**97,19**", "cache-hit; riwayat 2409 tidak tercetak"],
]
# ---------------------------------------------------------------- T9 step-2
rows_t9 = [
    ["appsid", "0509", "V4_INDOBERT", 3, "10.505", "6.552 / 3.953 / 2.454", "62,4 / 72,8 / **67,16**", "output yatim (ec —)"],
    ["appsid", "0809", "V4_1_03", 1, "10.735", "6.654 / 3.951 / 2.352", "62,74 / 73,88 / **67,86**", "loss 0,5544; VRAM 3.971 MB"],
    ["appsid", "0901", "run0809 + MI300X", 3, "10.733", "6.681 / 4.052 / 2.325", "62,25 / 74,18 / **67,69**", "cache lalu pair_eval 687 batch"],
    ["rest16", "27/08", "Drive (tanpa nb)", "—", "—", "—", "43,06 / 53,41 / **47,68**", "hanya master_metrics.json"],
    ["rest16", "02/09", "04_ACOS_Step2", 15, "1.120", "486 / 634 / 409", "43,4 / 54,3 / **48,24**", "15 epoch, ep terbaik 12"],
    ["rest16", "24/09", "Colab dasar", 15, "301", "0 / 301 / 895", "0,00 / 0,00 / **0,00**", "prediksi kolaps (301 baris)"],
    ["rest16", "12/09", "V5_EN", "cache", "—", "0 / 165.728 / 895", "0,00 / 0,00 / **0,00**", "cache appsid di folder rest16"],
]

# ---------------------------------------------------------------- T10 subtask
rows_t10 = []
for name, n, a, b in SUBTASK:
    rows_t10.append([name, n, f"{a:.2f}".replace(".", ","), f"{b:.2f}".replace(".", ","),
                     f"{a - b:+.2f}".replace(".", ",")])

# ---------------------------------------------------------------- T11 versi V4/V5
rows_t11 = [
    ["V4 (asli)", "1", "48", "40 (83%)", "67,16 · 97,94", "Tidak", "Manual, tanpa guard"],
    ["V4.1", "5", "99", "82 (83%)", "67,86 · 97,94", "Ya (echo)", "Modular 01–04; V4_1_02 kosong"],
    ["V4.2", "3", "69", "58 (84%)", "67,86 · 97,94", "Ya (echo)", "GUARDS + 2 file salinan V4.1"],
    ["V4.3", "1", "51", "44 (86%)", "67,86 · 97,94", "Ya (echo)", "SESSION/state; sama dengan V4.2 (0,968)"],
    ["V5.1 / V5.2", "2", "32", "6 (19%)", "—", "—", "3 sel jalan lalu ModuleNotFoundError"],
    ["V5.2.1 / V5.3", "2", "40", "30 (75%)", "—", "Dry-run", "Grid 54 run dicetak, 0 hasil"],
    ["V5 MI300X", "1", "12", "3 (25%)", "—", "—", "IndentationError sel 7"],
]

# ---------------------------------------------------------------- T12 platform
def _grup(pred):
    rs = [r for r in INV if pred(r["notebook"])]
    return (len(rs), sum(angka(r, "sel_kode") for r in rs),
            sum(angka(r, "sel_tereksekusi") for r in rs),
            sum(angka(r, "sel_output_yatim") for r in rs))


_lk = _grup(lambda p: os.path.dirname(p) == "notebooks" and os.path.basename(p)[:2] in ("01", "02", "03", "04", "05") and "_ACOS_" in p)
_mc = _grup(lambda p: os.path.basename(p).startswith("00_ACOS_Master_Pipeline_Colab") and "MI300X" not in p)
_mi = _grup(lambda p: "MI300X" in p)
_kg = _grup(lambda p: "Kaggle" in p)
_v1 = _grup(lambda p: p.startswith("ACOS-BERT/"))


def _jal(g):
    return f"{g[2]}/{g[1]} ({100 * g[2] // max(1, g[1])}%)"


rows_t12 = [
    ["Lokal `notebooks/01–05`", "BERT-Inggris", _lk[0], _jal(_lk),
     "81,27 · 48,24 · 78,95", "15 epoch penuh", "Bukti terkuat baseline"],
    ["Master Colab (V4/V4.x/V5_EN)", "IndoBERT + BERT", _mc[0], _jal(_mc),
     "67,86 · 97,94 · 0,00", "Campur cache", "Echo; output yatim terbanyak"],
    ["MI300X (GPU AMD)", "IndoBERT + BERT", _mi[0], _jal(_mi),
     "67,69 · 97,19 · 0,00", "Satu pair-eval nyata", "Satu gate-1 gagal"],
    ["Kaggle (2 salinan)", "IndoBERT", _kg[0], _jal(_kg), "—", "Tidak pernah jalan", "Identik byte-per-byte"],
    ["ACOS-BERT V1", "BERT", _v1[0], _jal(_v1), "—", "Tidak pernah jalan", "1 error `torchcrf`"],
]


# ---------------------------------------------------------------- T13 error
def _msg(x, n=52):
    x = (x or "").strip()
    return x if len(x) <= n else x[: n - 1] + "…"


rows_t13 = [[short(g["notebook"], 48), g["sel"], g["exec_count"] or "—", g["error"] or "(kosong)",
             _msg(g["pesan"])] for g in GALAT]

# ---------------------------------------------------------------- T14 jejak
rows_t14 = [[short(j["notebook"], 46), j["root_drive"].replace(";", ", "), j["flag"] or "—",
             j["gpu"] or "—", j["pakai_save_pretrained"]] for j in JEJAK]

# ---------------------------------------------------------------- T15 putusan
rows_t15 = [
    ["E2 — dihitung di selnya", "`02`, `04`, `01`, `03`, `V4_1_01`, `V4_1_03`, `V4_INDOBERT`, `MI300X 2409`, Colab dasar",
     "Dapat dikutip dengan menyebut sesi + nomor sel + `exec_count`"],
    ["E3 — echo/cache", "`V4_1`, `V4_2`, `V4_3`, `V4_1_04` (bagian eval), `V4_2_06`, `run0809`",
     "Kutip sebagai bukti cache, bukan sebagai run baru"],
    ["E1 — output yatim", "`UPDATE`, `05`, `V4_INDOBERT copy`",
     "Butuh artefak Drive untuk menopang; jangan dikutip sendiri"],
    ["E0 — nol/dry-run/kerangka", "ACOS-BERT (10), Kaggle (2), ASLI/PRO/PRO_Resume/V2/V3, V4_1_02, V4_2_05, GPU_Status, V5.1, V5.2, V5.2.1, V5.3, V5 MI300X, V5_EN",
     "Jangan dikutip sebagai hasil; sebut hanya sebagai rencana/kerangka"],
]

# ---------------------------------------------------------------- tulis MD
L = []
A = L.append

A("# Laporan 041 — Analisis Mendalam 45 Notebook `.ipynb` dan Komparasi Tabel")
A("")
A("**Repositori:** `rozanhaisyam/ACOS` · **Branch:** `arena/7b92b123-acos` · "
  "**Tanggal:** 2 November 2026, 23.35 WIB · **Sifat:** analisis statis (tanpa menjalankan ulang sel)")
A("")
A("**Ruang lingkup:** seluruh 45 berkas `.ipynb` di repositori (37,7 MB), 1.748 sel "
  f"({TOT['kode']} kode + {TOT['sel'] - TOT['kode']} markdown), {TOT['out']} sel beroutput, "
  f"{TOT['err']} sel bererror, dan {TOT['met']} baris metrik numerik.")
A("")
A("**Berkas pendukung:** `reports/041_data/` (`notebooks_inventaris.csv`, `notebooks_metrik.csv`, "
  "`notebooks_galat.csv`, `notebooks_jejak.csv`, `notebooks_kemiripan.csv`, `provenance_angka.csv`, "
  "`kontradiksi_angka.csv`, `subtask_15_perbandingan.csv`) dan skrip audit "
  "`scripts/audit_041_notebooks.py` + `scripts/gen_report_041.py`. Laporan 036–040 tidak diubah.")
A("")
A("---")
A("")

# Ringkasan
A("## 1. Ringkasan eksekutif")
A("")
A("1. **Notebook bukan bukti yang bersih.** Dari 1.037 sel kode, 575 (55,4%) tidak pernah "
  f"dieksekusi; {TOT['yatim']} output tidak memiliki `execution_count` (output \"yatim\" — ditempel "
  "atau berasal dari kernel lain). 19 notebook sama sekali tidak punya sel tereksekusi, 24 notebook "
  "menjalankan kurang dari separuh selnya.")
A("2. **Angka besar di notebook V4 adalah cache-hit, bukan training.** `97,94%` dan `67,86%` "
  "dimuat dengan pesan `[CACHE HIT]` / `dilewati — training tidak dijalankan` (sel 5e/8e). "
  "Hanya `V4_1_03` (1 epoch) dan `V4_INDOBERT` (3 epoch) yang benar-benar melatih Step-2.")
A("3. **Kontaminasi lintas domain terdokumentasi di dalam notebook.** "
  "`V5_EN_REST16_LAPTOP` menyalin checkpoint `appsid_08092026_150437xxx` ke folder sesi rest16, "
  "mencetak riwayat Step-1 appsid (8 baris, 97,94%) sebagai milik rest16, lalu menghasilkan "
  "`fp = 165.728` dan F1 0,00%.")
A("4. **Tiga run BERT-rest16 yang konsisten justru ada di notebook lokal.** `02` (Step-1 81,27%, "
  "15 epoch) dan `04` (Step-2 48,24%, 15 epoch) dieksekusi penuh tanpa cache; nilainya berdekatan "
  "dengan artefak Drive 27/08 (81,23% dan 47,68%). Ini baseline yang paling dapat dipertahankan.")
A("5. **Duplikasi masif.** 4 pasang berkas identik per-hash dan 19 pasang berkas dengan kemiripan "
  "kode ≥0,90. V4.1, V4.2, dan V4.3 adalah satu basis kode yang sama (Jaccard 0,965–0,968) dengan "
  "output metrik yang identik — bukan tiga replikasi.")
A("6. **Nama berkas tidak mencerminkan isi.** `..._V4_INDOBERT_run08092026.ipynb` seluruhnya "
  "berjalan pada sesi `appsid_24092026_0901` (24 September), bukan 8 September; "
  "`..._V4_INDOBERT copy.ipynb` hanya 2 sel dieksekusi tetapi memuat 19 output.")
A("7. **Satu-satunya dekomposisi 15 sub-task yang lengkap dan segar ada di dua tempat:** "
  "`04_ACOS_Step2` (rest16, 78,95% → 48,24%) dan `MI300X 2409` (appsid, 94,21% → 67,69%). "
  "Keduanya memakai TP/FP/FN, sehingga dapat direkonsiliasi.")
A("")
A("**Putusan satu baris:** notebook menjelaskan *bagaimana* angka 67–69% dan 47–48% diperoleh, "
  "tetapi tidak menambah klaim baru yang lebih tinggi; klaim 97,94% (Step-1) dan 66,28% "
  "(quadruple appsid) adalah artefak cache/agregasi yang harus tetap diberi tanda bintang.")
A("")
A("---")
A("")

# 2. metode
A("## 2. Metode, definisi, dan batas")
A("")
A("**Yang dilakukan.** (a) Inventaris seluruh `.ipynb` (ukuran, hash SHA-1 16 karakter atas "
  "gabungan teks sel kode). (b) Ekstraksi setiap output `text/plain`/`text`, lalu penandaan sel "
  "beroutput, sel tanpa `execution_count`, monotonsitas `execution_count`, dan gambar. "
  "(c) Regex metrik (`micro-F1`, `quad-F1`, `sentiment_acc`, `accuracy`, `precision`, `recall`) "
  "beserta nomor sel dan `exec_count`. (d) Klasifikasi traceback menjadi 13 sel error. "
  "(e) Deteksi jejak sesi (`appsid_*`, `rest16_*`), akar Drive (`ACOS`, `ACOS-ASLI`, "
  "`/shared-docker`, `ACOSE`), flag (`DRY_RUN`, `USE_DUAL_HEAD`, `SKIP_TRAINING`), dan pemakaian "
  "`save_pretrained`/`SubtaskMetricCapture`. (f) Kemiripan kode antar notebook dengan Jaccard "
  "8-gram atas seluruh sel kode (108 pasang ≥0,40).")
A("")
A("**Yang tidak dilakukan.** Sel tidak dijalankan ulang; tidak ada data atau bobot yang diunduh; "
  "tidak ada kesimpulan tentang performa model di luar angka yang tercetak di berkas. Analisis ini "
  "melengkapi — bukan menggantikan — pemeriksaan artefak Drive pada Laporan 040.")
A("")
A("**Tingkat bukti yang dipakai konsisten di seluruh tabel:**")
A("")
A(tbl(["Tingkat", "Arti", "Contoh pemakaian"], [
    ["**E2**", "Angka tercetak dari eksekusi yang punya `execution_count`, dengan sesi/path jelas",
     "`02` sel 13 ec=8 → 81,27%"],
    ["**E3**", "Angka dimuat dari cache/berkas, bukan dihitung di sel itu",
     "`V4_1` sel 71 ec=43 → `[CACHE HIT]` 67,86%"],
    ["**E1**", "Output ada tetapi tanpa `execution_count` (yatim) atau sesi tidak dapat dilacak",
     "`UPDATE` sel 13 → 81,23%"],
    ["**E0**", "Tidak ada eksekusi / gagal / dry-run", "`V5.2.1` sel 35 → `Belum ada run OK`"],
], ["---", "---", "---"]))
A("")
A("---")
A("")

# 3. T1
A("## 3. Tabel 1 — Inventaris 45 notebook menurut keluarga")
A("")
A("Kolom *Jalan* hanya menghitung sel kode yang memiliki `execution_count`; *Yatim* = sel "
  "beroutput tanpa `execution_count`.")
A("")
A(tbl(["Keluarga", "Nb", "Sel", "Kode", "Jalan", "%", "Output", "Error", "Metrik", "Yatim"],
      rows_t1, ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:"]))
A("")
v4 = [r for r in INV if r["keluarga"].startswith("V4") and "MI300X" not in r["keluarga"]]
A(f"**Bacaan.** Dua belas notebook keluarga V4 (V4, V4.1, V4.2, V4.3, copy, 0809, 2409) memuat "
  f"{sum(angka(r, 'sel') for r in v4)} sel, tetapi hanya {sum(angka(r, 'sel_tereksekusi') for r in v4)} "
  "sel yang benar-benar dieksekusi. Sebaliknya, keluarga `Lokal 01-05` kecil (83 sel) tetapi "
  "menyumbang 52 dari 88 baris metrik — karena setiap epoch dicetak, bukan karena hasilnya lebih baik.")
A("")
A("---")
A("")

# 4. T2
A("## 4. Tabel 2 — Matriks 45 notebook")
A("")
A(tbl(["No", "Notebook", "Keluarga", "Sel", "Kode", "Jalan", "Yatim", "Err", "Met", "Peran"],
      rows_t2, ["---:", "---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---"]))
A("")
A("---")
A("")

# 5. T3
A("## 5. Tabel 3 — Integritas eksekusi")
A("")
A(f"Sepuluh notebook teratas menurut jumlah output yatim (total {TOT['yatim']} di seluruh repo):")
A("")
A(tbl(["Notebook", "Kode", "Jalan", "Tak pernah jalan", "Yatim", "ec tidak monoton", "Rentang ec"],
      rows_t3, ["---", "---:", "---:", "---:", "---:", "---", "---"]))
A("")
A(f"- **{len(nol)} notebook tanpa satu pun sel tereksekusi:** " +
  ", ".join(f"`{short(r['notebook'], 40)}`" for r in sorted(nol, key=lambda r: r["notebook"])[:12]) +
  ", dan sisanya di Lampiran A.")
A(f"- **{len(separuh)} notebook menjalankan <50% sel kode.** Yang mencolok: `V4_INDOBERT copy` "
  "(2 dari 48 sel) dan `V5_EN_REST16_LAPTOP` (21 dari 49, 23 yatim) — keduanya tetap memuat angka "
  "final yang tampak lengkap.")
A("- `V4_1_04_eval_inference` adalah satu-satunya notebook dengan `execution_count` tidak monoton "
  "(32…53): sel 8 jalan pada ec=44, sel 10 pada ec=52 — evaluasi quadruple dan evaluasi 15 sub-task "
  "berasal dari dua eksekusi berbeda dalam satu berkas.")
A("- Notebook lokal `01` mulai dari `execution_count = 97`, yaitu lanjutan kernel sesi lain; "
  "`V4_1_03`/`V4_2_05` mulai dari 32/35 (dijalankan di tengah sesi master), bukan sesi bersih.")
A("")
A("---")
A("")

# 6. T4
A("## 6. Tabel 4 — Duplikasi kode")
A("")
A(f"`notebooks_kemiripan.csv` mencatat **{len(MIRIP)} pasang** notebook dengan Jaccard ≥0,40. "
  "Pasangan identik (hash sel kode sama) dan pasangan dengan kemiripan ≥0,90:")
A("")
A(tbl(["Hash / Jaccard", "Notebook A", "Notebook B", "Nilai"], rows_t4,
      ["---", "---", "---", "---"]))
A("")
A("**Klaster yang terbentuk:**")
A("")
A(tbl(["Klaster", "Anggota", "Kemiripan", "Implikasi"], [
    ["Master V4 IndoBERT", "V4 (asli), V4_1, V4_2, V4_3, copy, run0809, run2409, Kaggle ×2",
     "0,755–0,976", "Satu basis kode; perbedaan terutama konfigurasi & output"],
    ["Pipeline modular V4", "V4_1_03 ≡ V4_2_05 · V4_1_04 ≡ V4_2_06", "1,000 / 1,000",
     "Berkas disalin, bukan versi baru"],
    ["MI300X", "V4_BERT_rest16 ≡ V4_INDOBERT_run2409", "1,000",
     "Kode sama; hanya variabel backbone yang berbeda → rawan tertukar"],
    ["Kaggle", "2 salinan di dua direktori", "1,000", "Redundansi murni"],
    ["V5", "V5.2.1 ≡ V5.3 (0,988) · V5.1 ≡ V5.2 (0,811)", "0,811–0,988",
     "V5.3 hanya menambah sel klasifikasi di atas V5.2.1"],
], ["---", "---", "---", "---"]))
A("")
A("Konsekuensi metodologis: **jumlah notebook tidak boleh dipakai sebagai ukuran jumlah "
  "eksperimen.** 45 berkas hanya menghasilkan 41 hash kode berbeda, dan setelah dikelompokkan "
  "menurut kemiripan ≥0,75 tinggal enam kelompok fungsional: ACOS-BERT V1 (10), lokal 01–05 (5), "
  "master Colab V4/V5_EN (13), pipeline modular V4 (6), V5 eksperimen (5), serta salinan/utilitas (3).")
A("")
A("---")
A("")

# 7. T5
A("## 7. Tabel 5 — Provenance angka kunci")
A("")
A("Setiap baris menjawab: angka ini datang dari notebook mana, sel berapa, dengan `exec_count` "
  "berapa, dan pada sesi apa.")
A("")
A(tbl(["ID", "Angka", "Notebook", "Sel", "ec", "Sesi", "Tingkat"], rows_t5,
      ["---", "---", "---", "---:", "---:", "---", "---:"]))
A("")
A("**Pola yang terlihat.** Sembilan dari dua puluh angka kunci berstatus E3/E1/E0 — yaitu dimuat "
  "dari cache, yatim, atau tidak pernah dihitung. Hanya `02`, `04`, `V4_1_03`, `V4_INDOBERT` "
  "(Step-2 3 epoch), dan MI300X 2409 yang benar-benar menghitung ulang di selnya.")
A("")
A("---")
A("")

# 8. T6
A("## 8. Tabel 6 — Angka yang sama muncul di banyak notebook")
A("")
A(tbl(["Angka", "Jml notebook", "Notebook"], rows_t6, ["---", "---:", "---"]))
A("")
A("`67,86` muncul di 8 berkas dan `97,94` / `66,28` di 5 berkas — bukan karena direplikasi, "
  "tetapi karena rantai cache: `V4_INDOBERT` → `V4_1` → `V4_2` → `V4_3` → `V5_EN` → Kaggle. "
  "Sebaliknya `47,68` tidak muncul di satu notebook pun: angka itu hanya hidup di "
  "`master_metrics.json` Drive (P20), sehingga tidak dapat diverifikasi ulang dari repositori.")
A("")
A("---")
A("")

# 9. T7
A("## 9. Tabel 7 — Kontradiksi antar notebook")
A("")
A(tbl(["ID", "Objek", "Nilai A", "Nilai B", "Nilai C", "Catatan"], rows_t7,
      ["---", "---", "---", "---", "---", "---"]))
A("")
A("**C07 adalah temuan baru yang paling menjelaskan kegagalan.** Jumlah pasangan kandidat berbeda "
  "satu orde antara jalur lokal/Colab dan jalur V4/V5:")
A("")
A(tbl(["Jalur", "Sesi", "Pasangan", "Gold", "Rasio", "Prediksi (Quad num)", "Hasil"], [
    ["Lokal 03 → 04", "rest16_02092026", "1.451", "895", "1,62", "1.120", "48,24%"],
    ["Colab dasar", "rest16_24092026_0849", "1.450", "895", "1,62", "301", "0,00%"],
    ["V4 appsid", "appsid_08092026", "10.735", "9.006", "1,19", "—", "67,86%"],
    ["V4 appsid", "appsid_24092026_1426", "10.991", "9.006", "1,22", "10.733", "67,69%"],
    ["V5_EN rest16", "rest16_12092026", "10.735", "895", "**12,0**", "165.728", "0,00%"],
], ["---", "---", "---:", "---:", "---:", "---:", "---:"]))
A("")
A("Pada rest16 (583 kalimat, 916 quadruple) jumlah pasangan wajar ada di sekitar 1.450. Pipeline V4/V5 "
  "membangkitkan 10.735 pasangan untuk 895 gold — 12× lipat — sehingga FP meledak menjadi 165.728 "
  "dan F1 jatuh ke nol. Ini bukan kegagalan model, melainkan **kegagalan pembentukan pasangan** "
  "yang tidak pernah dibatasi ketika domain berpindah dari appsid (klausa) ke rest16 (kalimat).")
A("")
A("---")
A("")

# 10. T8
A("## 10. Tabel 8 — Komparasi Step-1 per sesi")
A("")
A(tbl(["Domain/backbone", "Notebook", "Sesi", "Epoch konfig", "Epoch terbaik", "TP/FP/FN",
       "P / R / F1 (%)", "Catatan"], rows_t8,
      ["---", "---", "---", "---:", "---:", "---", "---", "---"]))
A("")
A("Dua hal yang perlu ditegaskan:")
A("")
A("- **Tidak ada penurunan performa pada Step-1 rest16.** Tiga run menghasilkan 81,27 / 81,23 / "
  "80,76 — rentang 0,51 poin. Klaim bahwa baseline rest16 gagal pada tahap ekstraksi tidak "
  "didukung notebook.")
A("- **97,94% appsid bukan pembanding yang setara.** F1 appsid dihitung atas 16.773 span gold "
  "(TP 16.514 + FN 259; 17.207 prediksi), sedangkan rest16 dihitung atas 1.615 span gold "
  "(TP 1.367 + FN 248; 1.997 prediksi). Selisih 16,7 poin lebih mencerminkan granularitas data "
  "daripada kualitas model.")
A("")
A("---")
A("")

# 11. T9
A("## 11. Tabel 9 — Komparasi Step-2 (quadruple) per sesi")
A("")
A(tbl(["Domain", "Sesi", "Notebook", "Epoch jalan", "Quad num", "TP/FP/FN", "P / R / F1 (%)", "Catatan"],
      rows_t9, ["---", "---", "---", "---:", "---:", "---", "---", "---"]))
A("")
A("**Yang dapat disimpulkan.** Pada appsid, tiga sesi menghasilkan 67,16 / 67,86 / 67,69 dengan "
  "TP+FN konstan 9.006 — variasi 0,7 poin, wajar untuk seed dan jumlah epoch berbeda. "
  "Pada rest16, hanya sesi 02/09 yang benar-benar melatih 15 epoch (48,24%); sesi 27/08 hanya "
  "tercatat di Drive (47,68%), sedangkan sesi 24/09 dan 12/09 gagal karena masalah pasangan/cache.")
A("")
A("Perhatikan bahwa **67,69% bukan hasil baru**: MI300X 2409 menghitung ulang checkpoint yang "
  "sama dengan cache 0901 (TP/FP/FN identik: 6.681 / 4.052 / 2.325). Yang baru hanyalah "
  "dekomposisi 15 sub-task-nya.")
A("")
A("---")
A("")

# 12. T10
A("## 12. Tabel 10 — 15 sub-task: IndoBERT-appsid vs BERT-rest16")
A("")
A("Sumber: `MI300X 2409` sel 74 (ec=163, `master_08`) dan `04_ACOS_Step2` sel 12 (ec=6, "
  "`step2_07_metrik_15_subtask`). Keduanya memakai TP/FP/FN.")
A("")
A(tbl(["Sub-task", "Elemen", "IndoBERT appsid", "BERT rest16", "Selisih"], rows_t10,
      ["---", "---:", "---:", "---:", "---:"]))
A("")
A("Rata-rata per jumlah elemen:")
A("")
A(tbl(["Elemen", "IndoBERT", "BERT", "Selisih"], [
    ["1 elemen", "91,08", "79,66", "+11,42"],
    ["2 elemen", "82,06", "66,90", "+15,16"],
    ["3 elemen", "73,27", "56,37", "+16,90"],
    ["4 elemen", "66,08", "48,24", "+17,84"],
], ["---", "---:", "---:", "---:"]))
A("")
A("**Peringatan komparabilitas.** Tabel ini **bukan** perbandingan backbone. Dataset berbeda "
  "(appsid: 9.006 quadruple gold; rest16: 895), bahasa berbeda (Indonesia vs Inggris), dan jumlah "
  "kandidat berbeda. Yang dapat dikatakan: pada kedua domain, penurunan F1 mengikuti jumlah elemen "
  "(4 elemen paling sulit), dan celah melebar seiring bertambahnya elemen — konsisten dengan "
  "akumulasi error pada rantai aspek–kategori–sentimen–opini.")
A("")
A("---")
A("")

# 13. T11
A("## 13. Tabel 11 — Komparasi versi V4.1 / V4.2 / V4.3 / V5")
A("")
A(tbl(["Versi", "Nb", "Kode", "Jalan", "Angka utama", "Hitung ulang?", "Ciri"], rows_t11,
      ["---", "---:", "---:", "---", "---", "---", "---"]))
A("")
A("V4.1 → V4.2 → V4.3 menambah guard, penanganan sesi, dan modul, tetapi **tidak menambah eksekusi "
  "baru**: ketiganya mencetak 67,86 / 97,94 / 0,00 dari cache yang sama. V4.3 identik dengan V4.2 "
  "pada tingkat 0,968 — perbedaannya terutama pada sel state/session. V5 adalah percabangan lain: "
  "grid 54 run dirancang, tetapi seluruh sesi berhenti di `DRY_RUN` atau `ModuleNotFoundError`.")
A("")
A("---")
A("")

# 14. T12
A("## 14. Tabel 12 — Lokal vs Colab vs MI300X vs Kaggle")
A("")
A(tbl(["Lingkungan", "Backbone dominan", "Nb", "Sel jalan", "Angka", "Training nyata", "Kualitas bukti"],
      rows_t12, ["---", "---", "---:", "---", "---", "---", "---"]))
A("")
A("Lingkungan lokal (`notebooks/01–05`) adalah satu-satunya tempat di mana seluruh rantai "
  "EDA → Step-1 → pair → Step-2 → evaluasi dijalankan berurutan tanpa cache. Dua berkas Kaggle "
  "dan 9 dari 10 berkas ACOS-BERT tidak pernah dieksekusi sama sekali; satu berkas ACOS-BERT "
  "(master V1) hanya menjalankan 7 sel lalu berhenti pada `ModuleNotFoundError: torchcrf`.")
A("")
A("---")
A("")

# 15. T13
A("## 15. Tabel 13 — 13 sel error dan implikasinya")
A("")
A(tbl(["Notebook", "Sel", "ec", "Tipe", "Pesan"], rows_t13, ["---", "---:", "---:", "---", "---"]))
A("")
A("**Tiga pola penting:**")
A("")
A("1. **Kegagalan gate tidak menghentikan pipeline.** Pada `V4_BERT_rest16` (sel 43) dan "
  "`V5_EN_REST16_LAPTOP` (sel 44) muncul `RuntimeError: GATE 1 GAGAL: bobot encoder …`, tetapi sel "
  "72/75 tetap dieksekusi dan mencetak metrik final. Gate berfungsi sebagai pencetak pesan, bukan "
  "penghenti alur — karena itu angka 0,00% pada V5_EN tetap ditampilkan seolah sah.")
A("2. **Kegagalan import diulang tanpa perbaikan.** `V5.1` dan `V5.2` sama-sama berhenti di sel 7 "
  "dengan `ModuleNotFoundError: bert_utils`; sel berikutnya tetap dijalankan (3 sel) dan "
  "menghasilkan output yang identik di kedua berkas — indikasi salin-tempel output.")
A("3. **Dry-run dilaporkan sebagai kegagalan, bukan hasil.** `V5.2.1` dan `V5.3` berhenti dengan "
  "`AssertionError: Belum ada run OK` — bukti bahwa 54 run pada grid tidak pernah ada yang selesai.")
A("")
A("---")
A("")

# 16. T14
A("## 16. Tabel 14 — Jejak path, sesi, dan flag")
A("")
A(tbl(["Notebook", "Akar path", "Flag", "GPU", "save_pretrained"], rows_t14,
      ["---", "---", "---", "---", "---"]))
A("")
A("Tiga akar path bercampur dalam satu keluarga berkas: `/content/drive/MyDrive/ACOS`, "
  "`/content/drive/MyDrive/ACOS-ASLI`, dan `/shared-docker/ACOS`. Akibatnya artefak sesi yang "
  "sama dapat muncul dengan dua path berbeda (mis. `appsid_05092026_122741` di `ACOS/` vs "
  "`ACOS-ASLI/`), dan notebook yang namanya menyebut satu tanggal dapat menunjuk sesi tanggal lain.")
A("")
A("---")
A("")

# 17. T15
A("## 17. Tabel 15 — Putusan per kelompok notebook")
A("")
A(tbl(["Kelas", "Anggota", "Aturan pakai"], rows_t15,
      ["---", "---", "---"]))
A("")
A("**Rekomendasi pemakaian angka untuk laporan akhir:**")
A("")
A("| Klaim | Angka yang dipakai | Sumber | Yang harus dihindari |")
A("| --- | --- | --- | --- |")
A("| Step-1 rest16 | **81,27%** (rentang 80,76–81,27) | `02` sel 13 ec=8 | Mengutip 97,94% sebagai rest16 |")
A("| Step-2 rest16 | **48,24%** (47,68–48,24) | `04` sel 12 ec=6 + Drive 27/08 | Mengutip 47,03% tanpa menyebut tanpa TP/FP/FN |")
A("| Step-1 appsid | **97,94%** (ep8), 97,19% (ep3) | `V4_INDOBERT` sel 46 ec=69 | Menyebut sebagai hasil baru di V4.1–V4.3 |")
A("| Step-2 appsid | **67,86%** (0809) · 67,69% (0901) · 67,16% (0509) | `V4_1_03` sel 19 ec=41 | Menyebut 66,28% sebagai F1 pipeline |")
A("| 15 sub-task | Tabel 10 | `04` sel 12 & MI300X sel 74 | Menggabungkan dua domain dalam satu rata-rata |")
A("| Grid 54 run | **Tidak ada hasil** | `V5.2.1`/`V5.3` sel 35 | Menyebut \"54 run\" sebagai eksperimen |")
A("")
A("---")
A("")

# 18. dampak
A("## 18. Dampak terhadap laporan 036–040")
A("")
A(tbl(["Laporan", "Status", "Penyesuaian dari 041"], [
    ["036 (final report)", "Sebagian perlu koreksi",
     "Angka 81,27 / 48,24 kini punya jejak sel+ec lengkap; klaim \"rest16 gagal\" harus dibatasi pada sesi 24/09 & 12/09, bukan seluruh rest16"],
    ["037/038 (hasil & evaluasi)", "Ditegaskan",
     "Tidak ada notebook yang menaikkan angka di atas 67,86 / 48,24"],
    ["039 (survey repo)", "Ditegaskan",
     "Statistik 1.748 sel / 13 error / 575 tak jalan tetap berlaku; laporan ini menambah analisis sebab"],
    ["040 (Drive)", "Ditegaskan + dikoreksi",
     "47,68 dan 78,72/81,93/69,56 di Drive kini punya padanan notebook: 48,24 dan 78,95/82,51/70,11 (selisih ≤0,55) → konsisten, bukan artefak"],
    ["Klaim 66,28% (quadruple appsid)", "**Dikoreksi**",
     "Gold 19.528 = 2,17× gold quadruple (9.006); angka ini agregasi lintas-tingkat, bukan F1 pipeline. Gunakan 67,69%"],
    ["Klaim 97,94% Step-1", "**Dikoreksi**",
     "Cache-hit di semua notebook selain `V4_INDOBERT`; hanya sah sebagai riwayat sesi 0509 ep8"],
], ["---", "---", "---"]))
A("")
A("---")
A("")

# 19. batas
A("## 19. Keterbatasan dan langkah lanjut")
A("")
A("1. **Tidak ada re-eksekusi.** Semua kesimpulan berasal dari output tersimpan. Notebook yang "
  "selnya dihapus outputnya tidak dapat diperiksa (mis. `V4_1_02_step1_train`).")
A("2. **`execution_count` dapat dimanipulasi** (sel dijalankan di kernel lain, output ditempel). "
  "Karena itu status E2 tetap lebih lemah daripada artefak CSV/JSON yang diunduh dari Drive "
  "(Laporan 040).")
A("3. **Tidak semua sel dapat dipetakan ke sesi.** Hanya `UPDATE` yang menyebut nama sesi di "
  "kode; pada 44 notebook lain identitas sesi hanya muncul di output (atau tidak sama sekali), "
  "sehingga provenance sebagian hanya dapat ditetapkan sampai tingkat berkas.")
A("4. **Langkah lanjut yang disarankan:** (a) menandai seluruh notebook E3/E0 di README agar tidak "
  "dikutip; (b) menambah guard yang menghentikan eksekusi ketika gate-1 gagal; (c) membatasi "
  "pembentukan pasangan kandidat per kalimat (≈1,5× gold) sebagai pengaman lintas domain; "
  "(d) menjalankan ulang `02`/`04` dengan seed berbeda untuk mengukur varians baseline rest16.")
A("")
A("---")
A("")

# Lampiran
A("## Lampiran A — Daftar notebook tanpa sel tereksekusi")
A("")
for r in sorted(nol, key=lambda r: r["notebook"]):
    A(f"- `{r['notebook']}` — {r['sel_kode']} sel kode, {r['sel_beroutput']} beroutput")
A("")
A("## Lampiran B — Reproduksi")
A("")
A("```bash")
A("python3 scripts/audit_041_notebooks.py   # -> reports/041_data/*.csv (45 nb, stdlib saja)")
A("python3 scripts/gen_report_041.py        # -> laporan ini + 3 CSV turunan")
A("```")
A("")
A("Semua jalur relatif terhadap akar repositori. Tidak ada dependensi pihak ketiga; tidak ada "
  "berkas data yang diunduh atau diubah.")
A("")

MD = "\n".join(L) + "\n"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(MD)
print("ditulis:", OUT, len(MD.splitlines()), "baris")
print("tabel:", MD.count("\n| ---"))
