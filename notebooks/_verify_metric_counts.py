"""Verifikasi lokal untuk penyimpanan & pelaporan TP/FP/FN pada notebook STAGED.

Mengeksekusi sel 1b hasil generate (tanpa torch), memasang modul `eval_metrics`
tiruan yang meniru struktur upstream, lalu memeriksa lima hal:

1. `patch_eval_metrics_counts` membuat measureQuad & measureQuad_imp mengembalikan
   tp/fp/fn dengan nilai yang benar.
2. measureQuad_imp mengagregasi seluruh slot difficulty, bukan hanya slot terakhir,
   dan tidak melempar KeyError untuk teks di luar `text_type`.
3. `history_display_frame` menghasilkan kolom TP/FP/FN + persen dengan urutan tetap.
4. `metrics_display_frame` memisahkan hitungan mentah dari laju.
5. `SubtaskMetricCapture` menangkap tp/fp/fn dari format log `{:.2%}` pair_eval.

Jalankan: python notebooks/_verify_metric_counts.py
"""
import io
import json
import logging
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NB = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb")

failures = []


def check(name, cond, detail=""):
    print(("  ✅ " if cond else "  ❌ ") + name + (f" — {detail}" if detail else ""))
    if not cond:
        failures.append(name)


def cell_source(needle):
    nb = json.load(io.open(NB, encoding="utf-8"))
    for c in nb["cells"]:
        if c["cell_type"] == "code" and needle in "".join(c["source"]):
            return "".join(c["source"])
    raise LookupError(needle)


def fake_eval_metrics():
    """Modul tiruan dengan tanda tangan & cacat yang sama seperti upstream."""
    m = types.ModuleType("eval_metrics")

    def measureQuad(pred, gold):
        return {"precision": -1.0, "recall": -1.0, "micro-F1": -1.0}

    def measureQuad_imp(pred, gold, text_type):
        # Upstream: text_type[text] → KeyError untuk teks di luar gold.
        for text in pred:
            text_type[text]
        return {"precision": -1.0, "recall": -1.0, "micro-F1": -1.0}

    m.measureQuad = measureQuad
    m.measureQuad_imp = measureQuad_imp
    return m


print("1. Memuat sel 1b dari notebook hasil generate")
sys.path.insert(0, ROOT)
sys.modules["eval_metrics"] = fake_eval_metrics()
ns = {"__name__": "__main__"}
exec(compile(
    "import json\nfrom datetime import datetime\nimport pandas as pd\n"
    + cell_source("class step_stage:"), "<cell-1b>", "exec"), ns)
for n in ("patch_eval_metrics_counts", "history_display_frame",
          "metrics_display_frame", "best_epoch_row"):
    check(f"{n} terdefinisi", n in ns)

print("\n2. patch_eval_metrics_counts: measureQuad mengembalikan tp/fp/fn")
em = ns["patch_eval_metrics_counts"]()
# 2 benar, 1 salah prediksi, 1 gold terlewat sama sekali
pred = {"t1": ["a", "b", "x"], "t2": ["c"]}
gold = {"t1": ["a", "b"], "t2": ["c"], "t3": ["d", "e"]}
res = em.measureQuad(pred, gold)
check("kunci lengkap", set(res) == {"precision", "recall", "micro-F1", "tp", "fp", "fn"},
      str(sorted(res)))
check("tp = 3", res["tp"] == 3.0, f"tp={res['tp']}")
check("fp = 1", res["fp"] == 1.0, f"fp={res['fp']}")
check("fn = 2", res["fn"] == 2.0, f"fn={res['fn']}")
_p, _r = 3 / 4, 3 / 5
check("precision konsisten dengan tp/(tp+fp)", abs(res["precision"] - _p) < 1e-12,
      f"{res['precision']:.4f}")
check("recall konsisten dengan tp/(tp+fn)", abs(res["recall"] - _r) < 1e-12,
      f"{res['recall']:.4f}")
check("F1 konsisten", abs(res["micro-F1"] - 2 * _p * _r / (_p + _r)) < 1e-12,
      f"{res['micro-F1']:.4f}")

print("\n3. measureQuad_imp: agregat semua slot difficulty & aman tanpa text_type")
text_type = {"t1": [0, 4], "t2": [1, 4], "t3": [3, 4]}
res_imp = em.measureQuad_imp({**pred, "t_luar": ["z"]}, gold, text_type)
check("tidak melempar KeyError untuk teks di luar text_type", True)
check("kunci lengkap", set(res_imp) == {"precision", "recall", "micro-F1", "tp", "fp", "fn"})
# t1 → slot 0 & 4, t2 → slot 1 & 4, t_luar → slot 4 (default)
check("tp agregat = 6 (2 dari t1 ×2 slot + 1 dari t2 ×2 slot)", res_imp["tp"] == 6.0,
      f"tp={res_imp['tp']}")
check("fp agregat = 3 (1 dari t1 ×2 slot + 1 dari t_luar)", res_imp["fp"] == 3.0,
      f"fp={res_imp['fp']}")
check("fn agregat = 4 (t3 belum diprediksi ×2 slot)", res_imp["fn"] == 4.0,
      f"fn={res_imp['fn']}")
check("rincian 5 slot disimpan di modul", len(em.LAST_DIFFICULTY_BREAKDOWN) == 5,
      f"{len(em.LAST_DIFFICULTY_BREAKDOWN)} slot")
check("agregat ≠ slot terakhir saja (bug upstream)",
      res_imp["tp"] != em.LAST_DIFFICULTY_BREAKDOWN[4]["tp"],
      f"agregat {res_imp['tp']} vs slot4 {em.LAST_DIFFICULTY_BREAKDOWN[4]['tp']}")
check("patch idempoten", ns["patch_eval_metrics_counts"]().measureQuad is em.measureQuad)

print("\n4. history_display_frame: kolom TP/FP/FN + persen")
hist = [{"epoch": 1, "loss": 0.9, "tp": 10.0, "fp": 5.0, "fn": 7.0,
         "precision": 10 / 15, "recall": 10 / 17, "micro-F1": 0.625,
         "peak_vram_mb": 1024.0},
        {"epoch": 2, "loss": 0.4, "tp": 14.0, "fp": 3.0, "fn": 3.0,
         "precision": 14 / 17, "recall": 14 / 17, "micro-F1": 0.8235,
         "peak_vram_mb": 1100.0}]
df = ns["history_display_frame"](hist)
check("urutan kolom awal benar",
      list(df.columns)[:8] == ["epoch", "loss", "TP", "FP", "FN",
                              "Precision_%", "Recall_%", "Micro_F1_%"],
      str(list(df.columns)))
check("TP tidak dipersenkan", df["TP"].tolist() == [10.0, 14.0], str(df["TP"].tolist()))
check("Micro_F1 dipersenkan", df["Micro_F1_%"].tolist() == [62.5, 82.35],
      str(df["Micro_F1_%"].tolist()))
df_lagi = ns["history_display_frame"](df.rename(
    columns={"TP": "tp", "FP": "fp", "FN": "fn", "Precision_%": "precision",
             "Recall_%": "recall", "Micro_F1_%": "micro-F1"}).to_dict("records"))
check("riwayat yang sudah persen tidak dipersenkan dua kali",
      df_lagi["Micro_F1_%"].tolist() == [62.5, 82.35], str(df_lagi["Micro_F1_%"].tolist()))
check("riwayat lama tanpa tp/fp/fn tetap jalan",
      list(ns["history_display_frame"](
          [{"epoch": 1, "loss": 1.0, "precision": 0.5, "recall": 0.5,
            "micro-F1": 0.5}]).columns) == ["epoch", "loss", "Precision_%",
                                            "Recall_%", "Micro_F1_%"])
check("riwayat kosong → DataFrame kosong", ns["history_display_frame"]([]).empty)

print("\n5. best_epoch_row")
row, f1, ep = ns["best_epoch_row"](hist)
check("epoch terbaik = 2", ep == 2, f"ep={ep}")
check("f1 terbaik = 0.8235", abs(f1 - 0.8235) < 1e-9, f"f1={f1}")
check("baris terbaik memuat tp", row.get("tp") == 14.0, str(row.get("tp")))
row_p, f1_p, ep_p = ns["best_epoch_row"]([{"epoch": 3, "micro-F1": 82.35}])
check("riwayat berskala persen dinormalisasi ke fraksi", abs(f1_p - 0.8235) < 1e-9,
      f"f1={f1_p}")
check("riwayat kosong tidak melempar", ns["best_epoch_row"]([]) == ({}, 0.0, 0))

print("\n6. metrics_display_frame: hitungan vs laju")
dfo = ns["metrics_display_frame"](res)
check("6 baris metrik", len(dfo) == 6, f"{len(dfo)} baris")
_ht = dfo[dfo["Jenis"] == "hitungan"]
_lj = dfo[dfo["Jenis"] == "laju"]
check("3 baris hitungan (TP/FP/FN)", set(_ht["Metrik"]) == {"TP", "FP", "FN"},
      str(sorted(_ht["Metrik"])))
check("3 baris laju", set(_lj["Metrik"]) == {"precision", "recall", "micro-F1"},
      str(sorted(_lj["Metrik"])))
check("hitungan ditampilkan tanpa persen",
      _ht[_ht["Metrik"] == "TP"]["Tampil"].iloc[0] == "3", 
      _ht[_ht["Metrik"] == "TP"]["Tampil"].iloc[0])
check("laju ditampilkan sebagai persen",
      _lj[_lj["Metrik"] == "precision"]["Tampil"].iloc[0] == "75.00%",
      _lj[_lj["Metrik"] == "precision"]["Tampil"].iloc[0])
check("metrik lama tanpa tp/fp/fn tetap jalan",
      len(ns["metrics_display_frame"]({"precision": 0.5, "recall": 0.5,
                                       "micro-F1": 0.5})) == 3)

print("\n7. SubtaskMetricCapture menangkap tp/fp/fn dari log pair_eval")
from colab_utils import SubtaskMetricCapture  # noqa: E402

lg = logging.getLogger("verifikasi_pair_eval")
with SubtaskMetricCapture(lg) as cap:
    # Bentuk log persis seperti pair_eval: logger.info("  {} = {:.2%}", ...)
    lg.info("***** %s results *****", "category sentiment")
    for k, v in (("fn", 4.0), ("fp", 3.0), ("micro-F1", 0.6316),
                 ("precision", 0.6667), ("recall", 0.6), ("tp", 6.0)):
        lg.info("  {} = {:.2%}".format(k, v))
    lg.info("***** Test results *****")
    lg.info("  precision = 0.99")
d = cap.to_dict()
check("hanya sub-task yang tercatat, blok Test diabaikan",
      list(d) == ["category sentiment"], str(list(d)))
check("tp terbaca 6", abs(d["category sentiment"]["tp"] - 6.0) < 1e-9,
      str(d["category sentiment"].get("tp")))
check("fp terbaca 3", abs(d["category sentiment"]["fp"] - 3.0) < 1e-9)
check("fn terbaca 4", abs(d["category sentiment"]["fn"] - 4.0) < 1e-9)
dfs = cap.to_frame()
check("to_frame punya kolom TP/FP/FN",
      [c for c in ("TP", "FP", "FN") if c in dfs.columns] == ["TP", "FP", "FN"],
      str(list(dfs.columns)))
check("N_Elements dihitung dari nama sub-task", dfs["N_Elements"].iloc[0] == 2)
with SubtaskMetricCapture(lg) as cap2:
    lg.info("***** %s results *****", "aspect")
    lg.info("  precision = 50.00%")
check("sub-task tanpa tp/fp/fn tetap menghasilkan baris (NaN)",
      len(cap2.to_frame()) == 1 and cap2.to_frame()["TP"].isna().all())

print("\n8. Agregasi 9b atas kolom TP/FP/FN")
import pandas as pd  # noqa: E402

df_sub = pd.DataFrame([
    {"Subtask": "category", "N_Elements": 1, "TP": 10.0, "FP": 2.0, "FN": 3.0,
     "Precision": 0.8, "Recall": 0.7, "Micro_F1": 0.75},
    {"Subtask": "aspect", "N_Elements": 1, "TP": 6.0, "FP": 4.0, "FN": 5.0,
     "Precision": 0.6, "Recall": 0.5, "Micro_F1": 0.55},
])
spec = {"Jumlah_Subtask": ("Subtask", "count"),
        "Micro_F1_Rata2": ("Micro_F1", "mean"),
        "Micro_F1_Min": ("Micro_F1", "min"),
        "Micro_F1_Maks": ("Micro_F1", "max")}
for c, lab in (("TP", "TP_Total"), ("FP", "FP_Total"), ("FN", "FN_Total")):
    if c in df_sub.columns and df_sub[c].notna().any():
        spec[lab] = (c, "sum")
agg = df_sub.groupby("N_Elements").agg(**spec).reset_index()
check("TP_Total = 16", agg["TP_Total"].iloc[0] == 16.0, str(agg["TP_Total"].iloc[0]))
check("FN_Total = 8", agg["FN_Total"].iloc[0] == 8.0, str(agg["FN_Total"].iloc[0]))
agg_tanpa = df_sub.drop(columns=["TP", "FP", "FN"]).groupby("N_Elements").agg(
    **{k: v for k, v in spec.items() if not k.endswith("_Total")}).reset_index()
check("agregasi tanpa kolom hitungan tetap jalan", "TP_Total" not in agg_tanpa.columns)

print("\n" + "=" * 60)
if failures:
    print(f"❌ {len(failures)} pemeriksaan gagal:")
    for f in failures:
        print("   -", f)
    sys.exit(1)
print("✅ Semua pemeriksaan lulus.")
