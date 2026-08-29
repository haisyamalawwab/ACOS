"""Membangun 00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb dari PRO_Resume.

Versi V2 memperluas pemecahan sel yang sudah dilakukan pada Step 1 (5a-5f) ke
seluruh tahap berat lainnya:

  - pelacak progres `step_stage` dipindah ke sel awal (1b) agar dipakai semua tahap
  - `require_step1_stage` diganti nama menjadi `require_vars` (generik)
  - Sel 7 (jembatan pasangan)  -> 7a generate/cache, 7b laporan
  - Sel 8 (Step 2, 221 baris)  -> 8a-8f seperti pola Step 1
  - Sel 9 (evaluasi final)     -> 9a evaluasi, 9b tabel & plot

Sumber tidak diubah. Skrip idempoten: menulis ulang berkas tujuan dari nol
setiap kali dijalankan, jadi hasilnya selalu sama.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb")
DST = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb")


def md(text):
    return {"cell_type": "markdown", "metadata": {},
            "source": text.rstrip("\n").splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text.rstrip("\n").splitlines(keepends=True)}


def find_cell(nb, *needles, start=0):
    for i in range(start, len(nb["cells"])):
        c = nb["cells"][i]
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        if all(n in src for n in needles):
            return i
    raise LookupError(f"Sel dengan penanda {needles} tidak ditemukan")


MD_TITLE_EXTRA = """
---

### Versi V2 — eksekusi bertahap penuh

Notebook ini adalah turunan dari `00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb`.
Perbedaannya: **setiap tahap berat dipecah menjadi sel-sel kecil yang melaporkan
progresnya sendiri**, bukan hanya Step 1.

| Tahap | Sel | Pola |
|---|---|---|
| Pelacak progres | 1b | `step_stage` + `require_vars`, dipakai seluruh notebook |
| Step 1 (BERT-CRF) | 5a-5f | init, cache, data, model, training, laporan |
| Jembatan pasangan | 7a-7b | generate/cache, laporan |
| Step 2 (Category-Sentiment) | 8a-8f | init, cache, data, model, training, laporan |
| Evaluasi final | 9a-9b | evaluasi, tabel & plot |

Setiap sel mencetak judul, langkah bernomor dengan detik berjalan, dan durasi total.
Sel training menulis progres per epoch ke `logs/step*_progress.json` sehingga tetap
terbaca dari Drive bila tab Colab tertutup. Sel yang mahal melewati dirinya sendiri
saat artefaknya sudah ada.

Jalankan sel 1b sekali setelah setiap restart kernel — semua sel tahap
bergantung padanya.

**Metrik mentah**: sel 1b mendefinisikan `patch_eval_metrics_counts()` yang dipanggil di
sel 5a dan 8a, sehingga TP/FP/FN ikut dikembalikan oleh `measureQuad`/`measureQuad_imp`.
Hitungan itu disimpan ke `csv/step*_training_history.csv`, `logs/step*_progress.json`,
`logs/step*_run_result.json`, dan `logs/master_metrics.json`, lalu ditampilkan pada tabel
`master_03`, `master_06`, `master_07`, `master_08`, dan `master_09`."""

MD_TRACKER = """### 1b. Pelacak Progres Bertahap (`step_stage`)
Definisi dipakai oleh seluruh sel tahap di bawah. **Wajib dijalankan ulang setiap kali
kernel di-restart**, sebelum melompat ke Step 1/2 atau evaluasi.

Sel ini juga mendefinisikan `patch_eval_metrics_counts()` — patch yang membuat
`measureQuad`/`measureQuad_imp` ikut mengembalikan **TP, FP, FN** di samping
precision/recall/micro-F1, sehingga hitungan mentah bisa disimpan ke CSV/JSON dan
ditampilkan di tabel hasil. Patch-nya dipanggil dari sel 5a dan 8a (setelah
`sys.path` memuat `Extract-Classify-ACOS`), bukan di sini."""

CODE_TRACKER = '''import time


class step_stage:
    """Pelacak progres satu sel: judul, langkah bernomor + waktu, durasi akhir.

    Dipakai seluruh tahap pipeline supaya setiap sel punya jejak sendiri saat
    runtime Colab terputus di tengah eksekusi.
    """

    def __init__(self, title, total_steps=None):
        self.title = title
        self.total = total_steps
        self.n = 0
        self.t0 = None

    def __enter__(self):
        self.t0 = time.time()
        print("=" * 78)
        print(f"▶️  {self.title}")
        print("=" * 78, flush=True)
        return self

    def step(self, msg):
        self.n += 1
        tag = f"{self.n}/{self.total}" if self.total else str(self.n)
        print(f"   [{tag}] {time.time() - self.t0:6.1f}s  {msg}", flush=True)

    def note(self, msg):
        print(f"        {msg}", flush=True)

    def __exit__(self, exc_type, exc, tb):
        dur = time.time() - self.t0
        if exc_type is None:
            print(f"✅ {self.title} — selesai dalam {dur:.1f}s\\n", flush=True)
        else:
            print(f"❌ {self.title} — gagal setelah {dur:.1f}s: {exc}\\n", flush=True)
        return False


def require_vars(*names):
    """Menghentikan sel dengan pesan jelas bila sel prasyarat belum dijalankan."""
    missing = [n for n in names if n not in globals()]
    if missing:
        raise RuntimeError(
            f"Variabel {missing} belum ada di memori. Jalankan sel tahap sebelumnya "
            f"(atau sel pemulihan 6b/6c) sebelum sel ini.")


def write_stage_progress(path, **fields):
    """Menulis jejak progres yang bertahan meski runtime terputus."""
    fields["updated_at"] = datetime.now().isoformat()
    with open(path, "w", encoding="utf-8") as pf:
        json.dump(fields, pf, indent=2)
    return path


# Kolom hitungan mentah dilaporkan apa adanya; hanya kolom laju yang dipersenkan.
METRIC_COUNT_COLS = ("tp", "fp", "fn")
METRIC_RATE_COLS = ("precision", "recall", "micro-F1", "f1")


def patch_eval_metrics_counts():
    """Membuat `measureQuad` & `measureQuad_imp` ikut mengembalikan tp/fp/fn.

    Versi upstream mencetak ketiga hitungan itu lalu membuangnya, sehingga
    `pred_eval`/`pair_eval` hanya meneruskan precision/recall/micro-F1 dan
    notebook tidak pernah bisa menyimpan hitungan mentahnya. Patch ini juga
    memperbaiki dua cacat upstream sekaligus: `measureQuad_imp` melakukan
    `return` di luar loop (hanya slot difficulty terakhir yang terbawa) dan
    melempar KeyError untuk teks prediksi yang tidak ada di `text_type`.
    """
    import eval_metrics as _em

    if getattr(_em, "_ACOS_COUNTS_PATCHED", False):
        return _em

    def _prf(tp, fp, fn):
        p = 0.0 if tp + fp == 0 else 1.0 * tp / (tp + fp)
        r = 0.0 if tp + fn == 0 else 1.0 * tp / (tp + fn)
        f = 0.0 if p + r == 0 else 2 * p * r / (p + r)
        return {"precision": p, "recall": r, "micro-F1": f,
                "tp": float(tp), "fp": float(fp), "fn": float(fn)}

    def measureQuad(pred, gold):
        tp = fp = fn = 0.0
        for text in pred:
            cnt = 0
            if text in gold:
                for pair in pred[text]:
                    if pair in gold[text]:
                        cnt += 1
            tp += cnt
            fp += len(pred[text]) - cnt
            if text in gold:
                fn += len(gold[text]) - cnt
        for text in gold:
            if text not in pred:
                fn += len(gold[text])
        print("tp: {}. fp: {}. fn: {}.".format(tp, fp, fn))
        return _prf(tp, fp, fn)

    def measureQuad_imp(pred, gold, text_type):
        tp = [.0] * 5
        fp = [.0] * 5
        fn = [.0] * 5
        for text in pred:
            for dt in text_type.get(text, [4]):
                cnt = 0
                if text in gold:
                    for pair in pred[text]:
                        if pair in gold[text]:
                            cnt += 1
                tp[dt] += cnt
                fp[dt] += len(pred[text]) - cnt
                if text in gold:
                    fn[dt] += len(gold[text]) - cnt
        for text in gold:
            for dt in text_type.get(text, [4]):
                if text not in pred:
                    fn[dt] += len(gold[text])

        per_dt = []
        for i in range(5):
            print("tp: {}. fp: {}. fn: {}.".format(tp[i], fp[i], fn[i]))
            slot = _prf(tp[i], fp[i], fn[i])
            print(i, ': ', slot)
            per_dt.append(slot)
        # Agregat seluruh slot difficulty. Upstream me-return di luar loop
        # sehingga hanya slot i=4 yang terbawa.
        res = _prf(sum(tp), sum(fp), sum(fn))
        # `pair_eval` mem-format tiap nilai dengan {:.2%}, jadi nilai non-skalar
        # tidak boleh masuk dict ini; rincian per slot disimpan di modul.
        _em.LAST_DIFFICULTY_BREAKDOWN = per_dt
        return res

    _em.measureQuad = measureQuad
    _em.measureQuad_imp = measureQuad_imp
    _em.LAST_DIFFICULTY_BREAKDOWN = []
    _em._ACOS_COUNTS_PATCHED = True
    return _em


def history_display_frame(history, epochs_col="epoch"):
    """Riwayat per epoch → DataFrame siap tabel: hitungan mentah + kolom persen."""
    df = pd.DataFrame(history)
    if df.empty:
        return df
    for c in METRIC_RATE_COLS:
        if c in df.columns and pd.to_numeric(df[c], errors="coerce").max() <= 1.0:
            df[c] = (pd.to_numeric(df[c], errors="coerce") * 100).round(2)
    rename = {"tp": "TP", "fp": "FP", "fn": "FN", "precision": "Precision_%",
              "recall": "Recall_%", "micro-F1": "Micro_F1_%"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    order = [epochs_col, "loss", "TP", "FP", "FN",
             "Precision_%", "Recall_%", "Micro_F1_%"]
    cols = [c for c in order if c in df.columns]
    return df[cols + [c for c in df.columns if c not in cols]]


def metrics_display_frame(res):
    """Satu dict metrik → tabel dua-jenis: hitungan mentah dan laju dalam persen."""
    rows = []
    for k, v in res.items():
        if not isinstance(v, (int, float)):
            continue
        is_count = k in METRIC_COUNT_COLS
        rows.append({"Metrik": {"tp": "TP", "fp": "FP", "fn": "FN"}.get(k, k),
                     "Jenis": "hitungan" if is_count else "laju",
                     "Nilai": float(v),
                     "Tampil": (f"{float(v):.0f}" if is_count
                                else f"{float(v) * 100:.2f}%")})
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Jenis", ascending=False).reset_index(drop=True)
    return df


def best_epoch_row(history, f1_key="micro-F1"):
    """Baris epoch terbaik dari riwayat, apa pun skala kolom F1 yang tersimpan."""
    df = pd.DataFrame(history)
    if df.empty or f1_key not in df.columns:
        return {}, 0.0, 0
    f1 = pd.to_numeric(df[f1_key], errors="coerce")
    idx = int(f1.idxmax())
    best_f1 = float(f1.max())
    if best_f1 > 1.0:  # riwayat lama menyimpan persen
        best_f1 /= 100.0
    epoch = int(df.loc[idx].get("epoch", idx + 1))
    return df.loc[idx].to_dict(), best_f1, epoch


print("🛠️  step_stage, require_vars, write_stage_progress, patch_eval_metrics_counts, "
      "history_display_frame, metrics_display_frame, best_epoch_row siap dipakai.")'''

CODE_5A_V2 = '''require_vars("step_stage", "session_dirs", "bert_cache_dir", "DOMAIN")

from modeling import BertForQuadABSA
from bert_utils.tokenization import BertTokenizer
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import processors, output_modes
from eval_metrics import pred_eval
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from tqdm.auto import tqdm

# Toggle Melatih Ulang (Set True jika ingin melatih ulang dari awal)
FORCE_RETRAIN_STEP1 = False

with step_stage("5a. Inisialisasi Step 1: tokenizer, patch metrik, label, path", 6) as st:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        try:
            _vram_txt = f"VRAM bebas {torch.cuda.mem_get_info()[0] / 1024 ** 3:.2f} GB"
        except Exception:  # mem_get_info tidak ada di torch lama
            _vram_txt = (f"VRAM total "
                         f"{torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.2f} GB")
        st.step(f"GPU siap: {torch.cuda.get_device_name(0)} | {_vram_txt}")
    else:
        st.step("Mode CPU aktif (CUDA tidak tersedia) — training akan jauh lebih lambat")

    tokenizer = BertTokenizer.from_pretrained(bert_cache_dir, do_lower_case=True)
    st.step(f"Tokenizer dimuat: {len(tokenizer.vocab):,} entri vocab dari {bert_cache_dir}")

    _em1 = patch_eval_metrics_counts()
    st.step("eval_metrics dipatch: measureQuad & measureQuad_imp kini mengembalikan "
            "tp/fp/fn (+ agregat semua slot difficulty)")

    processor_step1 = processors["quad"]()
    label_list_step1 = processor_step1.get_labels(DOMAIN)
    num_labels_step1 = len(label_list_step1[1])
    label_map_seq = {label: i for i, label in enumerate(label_list_step1[1])}
    st.step(f"Label sekuens ({num_labels_step1}): {label_list_step1[1]}")

    step1_ckpt = session_dirs["step1_checkpoint"]
    step1_bin = os.path.join(step1_ckpt, "pytorch_model.bin")
    step1_csv = os.path.join(session_dirs["csv"], "step1_training_history.csv")
    pred_file = os.path.join(session_dirs["logs"], "pred4pipeline.txt")
    step1_progress_json = os.path.join(session_dirs["logs"], "step1_progress.json")
    os.makedirs(step1_ckpt, exist_ok=True)
    st.step(f"Checkpoint  : {step1_ckpt}")
    st.step(f"Prediksi    : {pred_file} | FORCE_RETRAIN_STEP1={FORCE_RETRAIN_STEP1} | "
            f"epoch target={NUM_EPOCHS}")'''

CODE_5E_V2 = '''require_vars("step_stage", "STEP1_SKIP_TRAINING")

if STEP1_SKIP_TRAINING:
    print("⏩ 5e dilewati — training Step 1 tidak dijalankan (cache hit).")
    print(f"   Micro-F1 terbaik tersimpan: {best_step1_f1 * 100:.2f}% (epoch {best1_epoch})")
else:
    require_vars("model_step1", "optimizer_1", "train_loader_1", "eval_loader_1")
    with step_stage(f"5e. Training Step 1 BERT-CRF — {NUM_EPOCHS} epoch pada {device}",
                    NUM_EPOCHS) as st:
        best_step1_f1 = 0.0
        best1_epoch = 1
        step1_history = []

        epoch_bar = tqdm(range(1, NUM_EPOCHS + 1), desc="Step 1 epoch", unit="epoch")
        for epoch in epoch_bar:
            model_step1.train()
            t_loss = 0.0
            batch_bar = tqdm(train_loader_1, desc=f"  epoch {epoch}/{NUM_EPOCHS}",
                             unit="batch", leave=False)
            for step, batch in enumerate(batch_bar, 1):
                batch = tuple(t.to(device) for t in batch)
                _len, _ids, _mask, _lbls, _seg, _imp_a, _imp_o = batch
                out1 = model_step1(aspect_input_ids=_ids, aspect_labels=_lbls,
                                   aspect_token_type_ids=_seg, aspect_attention_mask=_mask,
                                   exist_imp_aspect=_imp_a, exist_imp_opinion=_imp_o)
                loss, _ = unpack_model_output(out1)
                loss.backward()
                optimizer_1.step()
                optimizer_1.zero_grad()
                t_loss += loss.item()
                if step % 10 == 0 or step == len(train_loader_1):
                    batch_bar.set_postfix(loss=f"{t_loss / step:.4f}")
            batch_bar.close()

            avg_loss = t_loss / len(train_loader_1)
            model_step1.eval()
            print(f"   Epoch {epoch:02d}: evaluasi test set ({len(eval_loader_1)} batch)...",
                  flush=True)
            val_res = pred_eval(epoch, args_h, logger, tokenizer, model_step1, eval_loader_1,
                                eval_gold_1, label_list_step1, device, "quad", eval_type='test')
            val_f1 = val_res.get('micro-F1', 0.0)
            # tp/fp/fn tersedia karena patch_eval_metrics_counts() di sel 5a.
            val_tp = float(val_res.get('tp', float('nan')))
            val_fp = float(val_res.get('fp', float('nan')))
            val_fn = float(val_res.get('fn', float('nan')))

            peak_vram = torch.cuda.max_memory_allocated(device) / (1024 ** 2) if torch.cuda.is_available() else 0.0
            st.step(f"Epoch {epoch:02d} | loss {avg_loss:.4f} | TP {val_tp:.0f} FP {val_fp:.0f} "
                    f"FN {val_fn:.0f} | P {val_res.get('precision', 0.0) * 100:.2f}% "
                    f"| R {val_res.get('recall', 0.0) * 100:.2f}% "
                    f"| F1 {val_f1 * 100:.2f}% | peak VRAM {peak_vram:.0f} MB")

            step1_history.append({
                "epoch": epoch, "loss": avg_loss,
                "tp": val_tp, "fp": val_fp, "fn": val_fn,
                "precision": val_res.get('precision', 0.0),
                "recall": val_res.get('recall', 0.0),
                "micro-F1": val_f1,
                "peak_vram_mb": round(peak_vram, 2)
            })

            if val_f1 > best_step1_f1:
                best_step1_f1 = val_f1
                best1_epoch = epoch
                torch.save(model_step1.state_dict(), step1_bin)
                model_step1.config.to_json_file(os.path.join(step1_ckpt, "config.json"))
                tokenizer.save_vocabulary(step1_ckpt)
                st.note(f"🔥 Checkpoint terbaik diperbarui → {step1_ckpt}")

            # Jejak progres yang bertahan meski runtime terputus di tengah training.
            pd.DataFrame(step1_history).to_csv(step1_csv, index=False, encoding="utf-8")
            write_stage_progress(step1_progress_json, stage="STEP1_TRAINING",
                                 epoch=epoch, total_epochs=NUM_EPOCHS,
                                 last_loss=avg_loss, last_tp=val_tp, last_fp=val_fp,
                                 last_fn=val_fn, last_micro_f1=val_f1,
                                 best_micro_f1=best_step1_f1,
                                 best_epoch=best1_epoch,
                                 peak_vram_mb=round(peak_vram, 2))
            update_mcp_manifest("STEP1_TRAINING", 3, {
                "step1_epoch_progress": f"{epoch}/{NUM_EPOCHS}",
                "step1_best_micro_f1": float(best_step1_f1 * 100),
                "step1_best_epoch": best1_epoch,
            })
            epoch_bar.set_postfix(best_f1=f"{best_step1_f1 * 100:.2f}%", loss=f"{avg_loss:.4f}")
        epoch_bar.close()

        print(f"🏁 Training selesai. Micro-F1 terbaik {best_step1_f1 * 100:.2f}% "
              f"pada epoch {best1_epoch}.", flush=True)

# Ringkasan satu berkas untuk kedua cabang (training maupun cache hit).
step1_run_json = os.path.join(session_dirs["logs"], "step1_run_result.json")
_best_row1, _best_f1_1, _best_ep1 = best_epoch_row(globals().get("step1_history", []))
with open(step1_run_json, "w", encoding="utf-8") as _jf:
    json.dump({
        "mode": "cache_hit" if STEP1_SKIP_TRAINING else "trained",
        "domain": DOMAIN,
        "total_epochs_target": NUM_EPOCHS,
        "epochs_recorded": len(globals().get("step1_history", [])),
        "best_epoch": _best_ep1 or best1_epoch,
        "best_micro_f1": _best_f1_1,
        "best_micro_f1_pct": round(_best_f1_1 * 100, 2),
        "best_row": _best_row1,
        "history": globals().get("step1_history", []),
        "checkpoint": step1_ckpt,
        "csv": step1_csv,
        "saved_at": datetime.now().isoformat(),
    }, _jf, indent=2)
print(f"🧾 Ringkasan run Step 1 (termasuk TP/FP/FN per epoch) → {step1_run_json}")'''

CODE_5F_V2 = '''require_vars("step_stage", "step1_history", "best_step1_f1", "best1_epoch")

with step_stage("5f. Plot, tabel laporan, manifest & state Step 1", 5) as st:
    _p1 = os.path.join(plots_dir, "03_step1_training_loss_f1_curve.png")
    if step1_history:
        plot_training_history(
            step1_history, task_name="Step 1 (BERT-CRF)",
            output_plot_path=_p1,
            output_csv_path=step1_csv
        )
        st.step(f"Plot & CSV riwayat ditulis ({len(step1_history)} epoch)")
    else:
        st.step("Riwayat kosong — plot dilewati")

    rep.section("3. Step 1: ekstraksi aspect & opinion")
    df_s1_tabel = history_display_frame(step1_history)
    if not df_s1_tabel.empty:
        _kolom_hitung = [c for c in ("TP", "FP", "FN") if c in df_s1_tabel.columns]
        export_step_table(df_s1_tabel, name="master_03_step1_riwayat", csv_dir=csv_dir,
                          md_dir=md_dir,
                          title=f"Riwayat Training Step 1 ({DOMAIN.upper()})",
                          notes=("Metrik dihitung pada test set tiap epoch. "
                                 + ("TP/FP/FN adalah hitungan mentah span aspect/opinion; "
                                    "Precision/Recall/Micro-F1 dalam persen."
                                    if _kolom_hitung else
                                    "Kolom TP/FP/FN tidak ada — sel 5a belum dijalankan "
                                    "pada run yang menghasilkan riwayat ini.")),
                          max_rows_md=NUM_EPOCHS)
        rep.table(df_s1_tabel, max_rows=NUM_EPOCHS, caption="Metrik step 1 per epoch")
        st.step(f"Tabel master_03_step1_riwayat diekspor ({len(df_s1_tabel)} baris, "
                f"kolom hitungan: {', '.join(_kolom_hitung) or 'tidak ada'})")

        _row1, _f1_1, _ep1 = best_epoch_row(step1_history)
        rep.kv({
            "epoch_terbaik": _ep1 or best1_epoch,
            "micro-F1_terbaik": f"{_f1_1 * 100:.2f}%",
            "TP_FP_FN_epoch_terbaik": (
                f"{_row1.get('tp', float('nan')):.0f} / {_row1.get('fp', float('nan')):.0f} / "
                f"{_row1.get('fn', float('nan')):.0f}" if "tp" in _row1 else "tidak tercatat"),
            "checkpoint": step1_ckpt,
        })
        st.step(f"Micro-F1 terbaik {_f1_1 * 100:.2f}% (epoch {_ep1 or best1_epoch})")
    else:
        st.step("Tabel riwayat dilewati (tidak ada metrik per epoch)")

    if os.path.exists(_p1):
        from IPython.display import Image, display
        display(Image(_p1))
        rep.image(_p1, "Kurva training step 1")

    update_mcp_manifest("STEP1_COMPLETED", 3, {
        "step1_best_micro_f1": float(best_step1_f1 * 100 if best_step1_f1 <= 1.0 else best_step1_f1),
        "step1_checkpoint": step1_ckpt
    })
    st.step("session_manifest.json → STEP1_COMPLETED")

    save_pipeline_state({"best_step1_f1": best_step1_f1, "best_step1_epoch": best1_epoch})
    st.step(f"pipeline_state.pkl diperbarui | pred4pipeline.txt: "
            f"{'ada' if os.path.exists(pred_file) else 'BELUM ADA'}")'''

MD_7A = """## 7. Jembatan Pasangan Kandidat (Step 1 → Step 2)

### 7a. Pembentukan / Pemuatan Pasangan
Membaca `pred4pipeline.txt` dan membentuk cross-product aspect × opinion. Tag dikenali
dari polanya, bukan posisi kolom tab, supaya tag seperti `a--1,-1` tidak menyelundup ke
kolom teks dan memicu KeyError saat tokenisasi Step 2."""

CODE_7A = '''ensure_objects()
require_vars("step_stage", "session_dirs", "extract_dir")

import codecs as cs
import re

with step_stage("7a. Pasangan kandidat Step 1 → Step 2", 4) as st:
    pred_file = os.path.join(session_dirs["logs"], "pred4pipeline.txt")
    target_tokenized_tsv = os.path.join(extract_dir, "tokenized_data",
                                        f"{DOMAIN}_test_pair_1st.tsv")
    candidate_csv = os.path.join(session_dirs["csv"], "candidate_pairs_summary.csv")

    _in_mem = ('df_pairs' in globals() and df_pairs is not None
               and not df_pairs.empty and os.path.exists(target_tokenized_tsv))
    _on_disk = os.path.exists(candidate_csv) and os.path.exists(target_tokenized_tsv)

    if _in_mem:
        st.step(f"[CACHE HIT] {len(df_pairs):,} pasangan sudah ada di memori runtime")
    elif _on_disk:
        df_pairs = pd.read_csv(candidate_csv)
        st.step(f"[CACHE HIT] {len(df_pairs):,} pasangan dimuat dari {candidate_csv}")
    else:
        if not os.path.exists(pred_file):
            found_pred = auto_find_file("pred4pipeline.txt")
            if found_pred:
                os.makedirs(session_dirs["logs"], exist_ok=True)
                shutil.copy(found_pred, pred_file)
                st.step(f"pred4pipeline.txt disalin dari sesi sebelumnya: {found_pred}")
            else:
                raise FileNotFoundError(
                    f"pred4pipeline.txt tidak ada di {pred_file} maupun sesi lain. "
                    f"Jalankan Step 1 (sel 5a-5f) lebih dulu.")
        else:
            st.step(f"Sumber prediksi: {pred_file}")

        with cs.open(pred_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        st.step(f"{len(lines):,} baris prediksi dibaca")

        TAG_RE = re.compile(r'^(a|o)-(-?\\d+,-?\\d+)$')
        pair_records = []
        n_skip = 0
        os.makedirs(os.path.dirname(target_tokenized_tsv), exist_ok=True)
        with cs.open(target_tokenized_tsv, 'w', encoding='utf-8') as wf:
            for line in tqdm(lines, desc="   Membentuk pasangan", unit="baris", leave=False):
                asp, opi, text_parts = [], [], []
                for tok in line.strip().split():
                    m = TAG_RE.match(tok)
                    if m:
                        (asp if m.group(1) == 'a' else opi).append(m.group(2))
                    else:
                        text_parts.append(tok)
                if not text_parts:
                    n_skip += 1
                    continue
                text = ' '.join(text_parts)
                if not asp:
                    asp.append('-1,-1')
                if not opi:
                    opi.append('-1,-1')
                for pa in asp:
                    for po in opi:
                        wf.write(f"{text}####{pa} {po}\\n")
                        pair_records.append({"Text": text, "Aspect_Span": pa,
                                             "Opinion_Span": po})

        df_pairs = pd.DataFrame(pair_records)
        df_pairs.to_csv(candidate_csv, index=False)
        st.step(f"{len(df_pairs):,} pasangan ditulis ke {target_tokenized_tsv}"
                + (f" ({n_skip} baris kosong dilewati)" if n_skip else ""))

    st.step(f"Siap untuk Step 2 | berkas pair: "
            f"{'ada' if os.path.exists(target_tokenized_tsv) else 'BELUM ADA'}")'''

MD_7B = """### 7b. Distribusi Tipe Pasangan
Sel pelaporan: tabel implicit/explicit, plot batang, dan penyimpanan state. Aman diulang."""

CODE_7B = '''require_vars("step_stage", "df_pairs")

with step_stage("7b. Laporan distribusi pasangan kandidat", 4) as st:
    rep.section("4. Jembatan: pasangan kandidat")
    if df_pairs.empty:
        rep.text("Tidak ada pasangan kandidat yang terbentuk.")
        st.step("df_pairs kosong — tabel dan plot dilewati")
    else:
        df_pairs["Is_Implicit_Aspect"] = df_pairs["Aspect_Span"] == "-1,-1"
        df_pairs["Is_Implicit_Opinion"] = df_pairs["Opinion_Span"] == "-1,-1"
        df_pairs["Pair_Type"] = (
            df_pairs["Is_Implicit_Aspect"].map({True: "Implicit", False: "Explicit"}) + "-"
            + df_pairs["Is_Implicit_Opinion"].map({True: "Implicit", False: "Explicit"})
        )
        n_pair = len(df_pairs)
        df_tipe = df_pairs["Pair_Type"].value_counts().rename_axis(
            "Tipe_Pasangan").reset_index(name="Jumlah")
        df_tipe["Persen"] = (df_tipe["Jumlah"] / n_pair * 100).round(2)
        st.step(f"{n_pair:,} pasangan dalam {len(df_tipe)} tipe: "
                + ", ".join(f"{r.Tipe_Pasangan} {r.Persen}%" for r in df_tipe.itertuples()))

        export_step_table(df_tipe, name="master_04_tipe_pasangan", csv_dir=csv_dir,
                          md_dir=md_dir,
                          title=f"Distribusi Tipe Pasangan Kandidat ({DOMAIN.upper()})",
                          notes=f"Total {n_pair} pasangan dari cross-product aspect x opinion.")
        rep.table(df_tipe, caption="Tipe pasangan")
        export_step_table(df_pairs.head(20), name="master_05_preview_pasangan",
                          csv_dir=csv_dir, md_dir=md_dir,
                          title=f"Preview 20 Pasangan Kandidat ({DOMAIN.upper()})",
                          max_rows_md=20)
        st.step("Tabel master_04 & master_05 diekspor")

        plt.figure(figsize=(9, 5))
        _w = ["#3498db", "#9b59b6", "#e67e22", "#e74c3c"][:len(df_tipe)]
        _b = plt.bar(df_tipe["Tipe_Pasangan"], df_tipe["Jumlah"], color=_w,
                     edgecolor="black", alpha=0.88)
        for b, v in zip(_b, df_tipe["Jumlah"]):
            plt.text(b.get_x() + b.get_width() / 2, v, f"{v:,}\\n({v / n_pair * 100:.1f}%)",
                     ha="center", va="bottom", fontsize=9, fontweight="bold")
        plt.title(f"[{DOMAIN.upper()}] Pasangan Kandidat Step 1 -> Step 2",
                  fontsize=12, fontweight="bold")
        plt.ylabel("Jumlah pasangan")
        plt.margins(y=0.18)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        _pp = os.path.join(plots_dir, "04_candidate_pairs_distribution.png")
        plt.savefig(_pp, dpi=300)
        plt.show()
        plt.close()
        rep.image(_pp, "Distribusi tipe pasangan kandidat")
        st.step(f"Plot disimpan: {_pp}")

    update_mcp_manifest("CANDIDATE_PAIRS_GENERATED", 4,
                        {"candidate_pairs_count": len(df_pairs)})
    save_pipeline_state({"df_pairs": df_pairs})
    st.step("Manifest → CANDIDATE_PAIRS_GENERATED, pipeline_state.pkl diperbarui")'''

MD_8 = """## 8. Step 2: Klasifikasi Category & Sentiment (Bertahap)
Melatih `CategorySentiClassification` multi-label pada pasangan kandidat $(a, o)$.
Dipecah mengikuti pola Step 1 supaya setiap bagian bisa dilacak sendiri.

| Sel | Isi | Aman diulang |
|---|---|---|
| 8a | Import, patch tokenizer, label, path checkpoint | ya |
| 8b | Deteksi cache Step 2 (sesi aktif + sesi lama) | ya |
| 8c | Data evaluasi pasangan + gold Step 2 | ya |
| 8d | Model, data training, optimizer | ya (mengalokasi ulang VRAM) |
| 8e | Loop training per epoch + checkpoint terbaik | tidak (melatih ulang) |
| 8f | Plot, tabel laporan, manifest, simpan state | ya |

Sel 8c-8e melewati dirinya sendiri saat `STEP2_SKIP_TRAINING` bernilai `True`.
Catatan: 8c tetap dijalankan meski cache hit bila `eval_loader_2` belum ada, karena
sel evaluasi final (9a) membutuhkannya.

### 8a. Inisialisasi Step 2"""

CODE_8A = '''ensure_objects()
require_vars("step_stage", "session_dirs", "bert_cache_dir")

from modeling import CategorySentiClassification
from dataset_utils import read_pair_gold
from eval_metrics import pair_eval
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from bert_utils.tokenization import BertTokenizer
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import processors, output_modes
from tqdm.auto import tqdm
import logging

# Toggle Melatih Ulang Step 2 (Set True jika ingin memaksa melatih ulang)
FORCE_RETRAIN_STEP2 = False

with step_stage("8a. Inisialisasi Step 2: patch tokenizer, patch metrik, label, path", 6) as st:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        st.step(f"GPU cache dibersihkan | {torch.cuda.get_device_name(0)}")
    else:
        st.step("Mode CPU aktif (CUDA tidak tersedia)")

    # Token di luar vocab dipetakan ke [UNK] dan dilaporkan, bukan melempar
    # KeyError yang menghentikan seluruh epoch.
    _oov_seen = set()

    def patched_convert_tokens_to_ids(self, tokens):
        if tokens is None:
            return None
        if isinstance(tokens, str):
            try:
                return self.vocab[tokens]
            except KeyError:
                if tokens not in _oov_seen:
                    _oov_seen.add(tokens)
                    print(f"⚠️ Token di luar vocab: {ascii(tokens)}")
                return self.vocab.get('[UNK]', 100)
        ids = []
        for token in tokens:
            try:
                ids.append(self.vocab[token])
            except KeyError:
                _oov_seen.add(token)
                ids.append(self.vocab.get('[UNK]', 100))
        if len(ids) > self.max_len:
            logging.getLogger(__name__).warning(
                f"Seq len ({len(ids)}) > max ({self.max_len})")
        return ids

    BertTokenizer.convert_tokens_to_ids = patched_convert_tokens_to_ids
    st.step("BertTokenizer.convert_tokens_to_ids dipatch (OOV → [UNK], dicatat sekali)")

    # Patch evaluasi: measureQuad & measureQuad_imp ikut mengembalikan tp/fp/fn,
    # sekaligus defensif terhadap teks prediksi di luar gold (KeyError text_type)
    # dan memperbaiki return-di-luar-loop pada measureQuad_imp.
    _em2 = patch_eval_metrics_counts()
    st.step("eval_metrics dipatch: tp/fp/fn ikut dikembalikan, agregat semua slot "
            "difficulty, aman terhadap OOV/mismatched text")

    processor_step2 = processors["categorysenti"]()
    label_list_step2 = processor_step2.get_labels(DOMAIN)
    num_labels_step2 = len(label_list_step2[0])
    st.step(f"Label category-sentiment: {num_labels_step2} kelas")

    step2_ckpt = session_dirs["step2_checkpoint"]
    step2_bin = os.path.join(step2_ckpt, "pytorch_model.bin")
    step2_csv = os.path.join(session_dirs["csv"], "step2_training_history.csv")
    step2_progress_json = os.path.join(session_dirs["logs"], "step2_progress.json")
    os.makedirs(step2_ckpt, exist_ok=True)
    st.step(f"Checkpoint : {step2_ckpt}")

    # args_h dan logger2 dibangun di sini, bukan di 8d, karena 8d dilewati saat
    # cache hit sementara sel 8e dan 9a tetap membutuhkannya.
    logger2 = logging.getLogger("Step2")
    if "args_h" not in globals() or globals()["args_h"] is None:
        import types as _t
        args_h = _t.SimpleNamespace(output_dir=session_dirs["logs"],
                                    max_seq_length=MAX_SEQ_LENGTH)
        st.step(f"args_h dibangun (Step 1 dilewati di sesi ini) → {args_h.output_dir}")
    else:
        st.step(f"args_h dipakai ulang dari Step 1 → {args_h.output_dir}")

    print(f"   FORCE_RETRAIN_STEP2={FORCE_RETRAIN_STEP2} | epoch target={NUM_EPOCHS} | "
          f"batch={STEP2_BATCH_SIZE} | lr={STEP2_LR}")'''

MD_8B = """### 8b. Deteksi Cache Step 2
Menentukan `STEP2_SKIP_TRAINING`, satu-satunya penentu apakah sel 8d-8e melatih model."""

CODE_8B = '''require_vars("step_stage", "step2_bin", "step2_csv", "FORCE_RETRAIN_STEP2")

with step_stage("8b. Deteksi cache Step 2 (sesi aktif lalu sesi lama)", 4) as st:
    step2_already_done = os.path.exists(step2_bin)
    st.step("Sesi aktif — model: " + (
        f"{os.path.getsize(step2_bin) / 1024 ** 2:.1f} MB" if step2_already_done
        else "belum ada"))

    if step2_already_done:
        st.step("Pencarian sesi lama dilewati (checkpoint sesi aktif sudah ada)")
    else:
        found_bin2 = auto_find_file("pytorch_model.bin", must_contain="step2_best",
                                    search_roots=[
                                        results_base if 'results_base' in globals() else "",
                                        "/content/drive/MyDrive/ACOS/Output/results",
                                        os.path.join(base_project_dir, "Output", "results"),
                                    ])
        if found_bin2 and "step2_best" in found_bin2:
            src_dir2 = os.path.dirname(found_bin2)
            st.step(f"Checkpoint sesi sebelumnya ditemukan: {src_dir2}")
            for fn in ["pytorch_model.bin", "config.json", "vocab.txt"]:
                fp = os.path.join(src_dir2, fn)
                if os.path.exists(fp):
                    shutil.copy(fp, os.path.join(step2_ckpt, fn))
                    st.note(f"↪ {fn} ({os.path.getsize(fp) / 1024 ** 2:.1f} MB) disalin")
            found_csv2 = auto_find_file("step2_training_history.csv")
            if found_csv2:
                shutil.copy(found_csv2, step2_csv)
                st.note(f"↪ step2_training_history.csv disalin dari {found_csv2}")
            step2_already_done = os.path.exists(step2_bin)
        else:
            st.step("Tidak ada checkpoint step2_best di sesi mana pun")

    STEP2_SKIP_TRAINING = (not FORCE_RETRAIN_STEP2) and step2_already_done
    st.step("Keputusan: " + ("CACHE HIT → sel 8d-8e dilewati"
                             if STEP2_SKIP_TRAINING else
                             f"TRAINING dijalankan ({NUM_EPOCHS} epoch)"))

    if STEP2_SKIP_TRAINING:
        print(f"⏩ [CACHE HIT] Model Step 2 : {step2_ckpt}")
        if os.path.exists(step2_csv):
            df_s2_saved = pd.read_csv(step2_csv)
            step2_history = df_s2_saved.to_dict('records')
            _row_c2, best_step2_f1, best2_epoch = best_epoch_row(step2_history)
            best2_epoch = best2_epoch or NUM_EPOCHS
            _ada_hitungan = all(c in df_s2_saved.columns for c in ("tp", "fp", "fn"))
            st.step(f"Riwayat tersimpan: {len(df_s2_saved)} epoch, terbaik epoch {best2_epoch}"
                    + (" (TP/FP/FN tersedia)" if _ada_hitungan
                       else " (tanpa kolom TP/FP/FN — CSV dari run lama)"))
            if len(df_s2_saved) < NUM_EPOCHS:
                st.note(f"⚠️ Riwayat hanya {len(df_s2_saved)}/{NUM_EPOCHS} epoch — "
                        f"checkpoint dari run yang terhenti. Set FORCE_RETRAIN_STEP2=True "
                        f"bila ingin melatih penuh.")
        else:
            step2_history = []
            best_step2_f1 = 0.0
            best2_epoch = NUM_EPOCHS
            st.step("Riwayat CSV tidak ada — metrik per epoch tidak bisa dilaporkan")'''

MD_8C = """### 8c. Data Evaluasi Pasangan & Gold Step 2
Berbeda dari 5c: sel ini **tetap berjalan saat cache hit** kalau `eval_loader_2` belum ada
di memori, karena evaluasi final (9a) memerlukannya. Sumber pasangan dilaporkan eksplisit —
`_test_pair_1st.tsv` berarti skor pipeline penuh, `_test_pair.tsv` berarti Step 2 terisolasi."""

CODE_8C = '''ensure_objects()
require_vars("step_stage", "processor_step2", "label_list_step2", "tokenizer")

_need_eval_loader = ("eval_loader_2" not in globals()) or ("eval_gold_2" not in globals())
if not _need_eval_loader:
    print("⏩ 8c dilewati — eval_loader_2 dan eval_gold_2 sudah ada di memori.")
else:
    with step_stage("8c. Data evaluasi pasangan + gold Step 2", 5) as st:
        tokenized_dir = os.path.join(extract_dir, "tokenized_data")
        eval_pair_file, pakai_1st = resolve_eval_pair_file(tokenized_dir, DOMAIN,
                                                          prefer_1st=True)
        st.step(f"Sumber pasangan: {os.path.basename(eval_pair_file)} → "
                + ("prediksi step 1 (skor pipeline penuh)" if pakai_1st
                   else "gold pair (step 2 TERISOLASI, bukan skor pipeline)"))

        eval_examples_2 = pair_examples_from_file(processor_step2, eval_pair_file,
                                                 set_type="test")
        st.step(f"{len(eval_examples_2):,} contoh pasangan dibaca")

        eval_features_2 = features_step2(eval_examples_2, label_list_step2, MAX_SEQ_LENGTH,
                                         tokenizer, output_modes["categorysenti"])
        st.step(f"{len(eval_features_2):,} fitur dibentuk (max_seq_length={MAX_SEQ_LENGTH})")

        pin_mem = torch.cuda.is_available()
        num_work = 0 if sys.platform.startswith('win') else 2
        ev2_data = TensorDataset(
            torch.tensor([f.tokens_len for f in eval_features_2], dtype=torch.long),
            torch.tensor([f.aspect_input_ids for f in eval_features_2], dtype=torch.long),
            torch.tensor([f.aspect_input_mask for f in eval_features_2], dtype=torch.long),
            torch.tensor([f.aspect_segment_ids for f in eval_features_2], dtype=torch.long),
            torch.tensor([f.candidate_aspect for f in eval_features_2], dtype=torch.long),
            torch.tensor([f.candidate_opinion for f in eval_features_2], dtype=torch.long),
            torch.tensor([f.label_id for f in eval_features_2], dtype=torch.float)
        )
        eval_loader_2 = DataLoader(ev2_data, sampler=SequentialSampler(ev2_data),
                                   batch_size=16, pin_memory=pin_mem, num_workers=num_work)
        st.step(f"eval_loader_2 siap: {len(eval_loader_2)} batch × 16")

        class ArgsProxy:
            def __init__(self):
                self.bert_model = bert_cache_dir
                self.do_lower_case = True

        gold_pair_tsv = os.path.join(tokenized_dir, f"{DOMAIN}_test_pair.tsv")
        with open(gold_pair_tsv, "r", encoding="utf-8") as f:
            eval_gold_2 = read_pair_gold(f.readlines(), ArgsProxy())
        st.step(f"Gold quadruple dibaca dari {os.path.basename(gold_pair_tsv)} "
                f"({len(eval_gold_2):,} entri)")'''

MD_8D = """### 8d. Model, Data Training & Optimizer Step 2"""

CODE_8D = '''require_vars("step_stage", "STEP2_SKIP_TRAINING")

if STEP2_SKIP_TRAINING:
    print("⏩ 8d dilewati — model dan optimizer tidak diperlukan saat cache hit.")
else:
    require_vars("eval_loader_2", "eval_gold_2", "num_labels_step2")
    with step_stage("8d. Model Category-Sentiment, data training, optimizer", 5) as st:
        model_step2 = CategorySentiClassification.from_pretrained(
            bert_cache_dir, num_labels=num_labels_step2).to(device)
        _n_par2 = sum(p.numel() for p in model_step2.parameters())
        _vram2 = torch.cuda.memory_allocated(device) / 1024 ** 2 if torch.cuda.is_available() else 0.0
        st.step(f"Model dimuat ke {device}: {_n_par2 / 1e6:.1f} M parameter, "
                f"VRAM terpakai {_vram2:.0f} MB")

        train_examples_2 = processor_step2.get_train_examples(extract_dir, DOMAIN)
        st.step(f"{len(train_examples_2):,} contoh training dibaca")

        train_features_2 = features_step2(train_examples_2, label_list_step2, MAX_SEQ_LENGTH,
                                          tokenizer, output_modes["categorysenti"])
        tr2_data = TensorDataset(
            torch.tensor([f.tokens_len for f in train_features_2], dtype=torch.long),
            torch.tensor([f.aspect_input_ids for f in train_features_2], dtype=torch.long),
            torch.tensor([f.aspect_input_mask for f in train_features_2], dtype=torch.long),
            torch.tensor([f.aspect_segment_ids for f in train_features_2], dtype=torch.long),
            torch.tensor([f.candidate_aspect for f in train_features_2], dtype=torch.long),
            torch.tensor([f.candidate_opinion for f in train_features_2], dtype=torch.long),
            torch.tensor([f.label_id for f in train_features_2], dtype=torch.float)
        )
        train_loader_2 = DataLoader(tr2_data, sampler=RandomSampler(tr2_data),
                                    batch_size=STEP2_BATCH_SIZE, pin_memory=pin_mem,
                                    num_workers=num_work)
        st.step(f"train_loader_2 siap: {len(train_loader_2)} batch × {STEP2_BATCH_SIZE}")

        num_train_steps_2 = len(train_loader_2) * NUM_EPOCHS
        param_opt2 = list(model_step2.named_parameters())
        no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
        opt_grouped2 = [
            {'params': [p for n, p in param_opt2 if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
            {'params': [p for n, p in param_opt2 if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]
        optimizer_2 = BertAdam(opt_grouped2, lr=STEP2_LR, warmup=0.1, t_total=num_train_steps_2)
        st.step(f"BertAdam siap: lr={STEP2_LR}, warmup=0.1, t_total={num_train_steps_2:,} step")
        st.step(f"logger2 & args_h dari sel 8a → {args_h.output_dir}")'''

MD_8E = """### 8e. Loop Training Step 2
Bar epoch dengan ETA, bar batch dengan loss berjalan, satu baris ringkasan per epoch.
Progres per epoch ditulis ke `csv/step2_training_history.csv`, `logs/step2_progress.json`,
dan `session_manifest.json`."""

CODE_8E = '''require_vars("step_stage", "STEP2_SKIP_TRAINING")

if STEP2_SKIP_TRAINING:
    print("⏩ 8e dilewati — training Step 2 tidak dijalankan (cache hit).")
    print(f"   Micro-F1 terbaik tersimpan: {best_step2_f1 * 100:.2f}% (epoch {best2_epoch})")
else:
    require_vars("model_step2", "optimizer_2", "train_loader_2", "eval_loader_2")
    with step_stage(f"8e. Training Step 2 Category-Sentiment — {NUM_EPOCHS} epoch pada {device}",
                    NUM_EPOCHS) as st:
        best_step2_f1 = 0.0
        best2_epoch = 1
        step2_history = []

        epoch_bar = tqdm(range(1, NUM_EPOCHS + 1), desc="Step 2 epoch", unit="epoch")
        for epoch in epoch_bar:
            model_step2.train()
            t_loss = 0.0
            batch_bar = tqdm(train_loader_2, desc=f"  epoch {epoch}/{NUM_EPOCHS}",
                             unit="batch", leave=False)
            for step, batch in enumerate(batch_bar, 1):
                batch = tuple(t.to(device) for t in batch)
                _len, _ids, _mask, _seg, _cand_a, _cand_o, _lbls = batch
                out2 = model_step2(tokenizer, epoch, aspect_input_ids=_ids,
                                   aspect_token_type_ids=_seg, aspect_attention_mask=_mask,
                                   candidate_aspect=_cand_a, candidate_opinion=_cand_o,
                                   label_id=_lbls)
                loss, _ = unpack_model_output(out2)
                loss.backward()
                optimizer_2.step()
                optimizer_2.zero_grad()
                t_loss += loss.item()
                if step % 10 == 0 or step == len(train_loader_2):
                    batch_bar.set_postfix(loss=f"{t_loss / step:.4f}")
            batch_bar.close()

            avg_loss = t_loss / len(train_loader_2)
            model_step2.eval()
            print(f"   Epoch {epoch:02d}: evaluasi pasangan ({len(eval_loader_2)} batch)...",
                  flush=True)
            val_res = pair_eval(epoch, args_h, logger2, tokenizer, model_step2, eval_loader_2,
                                eval_gold_2, label_list_step2, device, "categorysenti",
                                eval_type='test')
            val_f1 = val_res.get('micro-F1', 0.0)
            # tp/fp/fn tersedia karena patch_eval_metrics_counts() di sel 8a.
            val_tp = float(val_res.get('tp', float('nan')))
            val_fp = float(val_res.get('fp', float('nan')))
            val_fn = float(val_res.get('fn', float('nan')))
            peak_vram2 = torch.cuda.max_memory_allocated(device) / (1024 ** 2) if torch.cuda.is_available() else 0.0

            st.step(f"Epoch {epoch:02d} | loss {avg_loss:.4f} | TP {val_tp:.0f} FP {val_fp:.0f} "
                    f"FN {val_fn:.0f} | P {val_res.get('precision', 0.0) * 100:.2f}% "
                    f"| R {val_res.get('recall', 0.0) * 100:.2f}% "
                    f"| quadruple micro-F1 {val_f1 * 100:.2f}% | peak VRAM {peak_vram2:.0f} MB")

            step2_history.append({
                "epoch": epoch, "loss": avg_loss,
                "tp": val_tp, "fp": val_fp, "fn": val_fn,
                "precision": val_res.get('precision', 0.0),
                "recall": val_res.get('recall', 0.0),
                "micro-F1": val_f1,
                "peak_vram_mb": round(peak_vram2, 2)
            })

            if val_f1 > best_step2_f1 or epoch == 1 or not os.path.exists(step2_bin):
                if val_f1 > best_step2_f1:
                    best_step2_f1 = val_f1
                    best2_epoch = epoch
                torch.save(model_step2.state_dict(), step2_bin)
                model_step2.config.to_json_file(os.path.join(step2_ckpt, "config.json"))
                tokenizer.save_vocabulary(step2_ckpt)
                st.note(f"🔥 Checkpoint diperbarui (epoch {epoch}, F1 {val_f1 * 100:.2f}%) → {step2_ckpt}")

            pd.DataFrame(step2_history).to_csv(step2_csv, index=False, encoding="utf-8")
            write_stage_progress(step2_progress_json, stage="STEP2_TRAINING", epoch=epoch,
                                 total_epochs=NUM_EPOCHS, last_loss=avg_loss,
                                 last_tp=val_tp, last_fp=val_fp, last_fn=val_fn,
                                 last_micro_f1=val_f1, best_micro_f1=best_step2_f1,
                                 best_epoch=best2_epoch,
                                 peak_vram_mb=round(peak_vram2, 2))
            update_mcp_manifest("STEP2_TRAINING", 5, {
                "step2_epoch_progress": f"{epoch}/{NUM_EPOCHS}",
                "step2_best_micro_f1": float(best_step2_f1 * 100),
                "step2_best_epoch": best2_epoch,
            })
            epoch_bar.set_postfix(best_f1=f"{best_step2_f1 * 100:.2f}%",
                                  loss=f"{avg_loss:.4f}")
        epoch_bar.close()

        if not os.path.exists(step2_bin):
            torch.save(model_step2.state_dict(), step2_bin)
            model_step2.config.to_json_file(os.path.join(step2_ckpt, "config.json"))
            tokenizer.save_vocabulary(step2_ckpt)
            st.note(f"💾 Checkpoint final Step 2 disimpan → {step2_ckpt}")

        print(f"🏁 Training Step 2 selesai. Micro-F1 terbaik {best_step2_f1 * 100:.2f}% "
              f"pada epoch {best2_epoch}.", flush=True)

# Ringkasan satu berkas untuk kedua cabang (training maupun cache hit).
step2_run_json = os.path.join(session_dirs["logs"], "step2_run_result.json")
_best_row2, _best_f1_2, _best_ep2 = best_epoch_row(globals().get("step2_history", []))
with open(step2_run_json, "w", encoding="utf-8") as _jf:
    json.dump({
        "mode": "cache_hit" if STEP2_SKIP_TRAINING else "trained",
        "domain": DOMAIN,
        "total_epochs_target": NUM_EPOCHS,
        "epochs_recorded": len(globals().get("step2_history", [])),
        "best_epoch": _best_ep2 or best2_epoch,
        "best_micro_f1": _best_f1_2,
        "best_micro_f1_pct": round(_best_f1_2 * 100, 2),
        "best_row": _best_row2,
        "history": globals().get("step2_history", []),
        "checkpoint": step2_ckpt,
        "csv": step2_csv,
        "sumber_kandidat": "step1" if globals().get("pakai_1st", True) else "gold",
        "saved_at": datetime.now().isoformat(),
    }, _jf, indent=2)
print(f"🧾 Ringkasan run Step 2 (termasuk TP/FP/FN per epoch) → {step2_run_json}")'''

MD_8F = """### 8f. Plot, Tabel & State Step 2"""

CODE_8F = '''require_vars("step_stage", "step2_history", "best_step2_f1", "best2_epoch")

with step_stage("8f. Plot, tabel laporan, manifest & state Step 2", 5) as st:
    _p2 = os.path.join(plots_dir, "04_step2_training_loss_f1_curve.png")
    if step2_history:
        plot_training_history(
            step2_history, task_name="Step 2 (Category-Sentiment)",
            output_plot_path=_p2, output_csv_path=step2_csv
        )
        st.step(f"Plot & CSV riwayat ditulis ({len(step2_history)} epoch)")
    else:
        st.step("Riwayat kosong — plot dilewati")

    rep.section("5. Step 2: klasifikasi category & sentiment")
    df_s2_tabel = history_display_frame(step2_history)
    if not df_s2_tabel.empty:
        _kolom_hitung2 = [c for c in ("TP", "FP", "FN") if c in df_s2_tabel.columns]
        _src_txt = 'prediksi step 1' if globals().get('pakai_1st', True) else 'gold pair'
        export_step_table(df_s2_tabel, name="master_06_step2_riwayat", csv_dir=csv_dir,
                          md_dir=md_dir,
                          title=f"Riwayat Training Step 2 ({DOMAIN.upper()})",
                          notes=("Metrik pada level quadruple lengkap. Sumber kandidat: "
                                 f"{_src_txt}. "
                                 + ("TP/FP/FN adalah hitungan mentah quadruple; "
                                    "Precision/Recall/Micro-F1 dalam persen."
                                    if _kolom_hitung2 else
                                    "Kolom TP/FP/FN tidak ada — riwayat berasal dari run "
                                    "sebelum patch metrik di sel 8a.")),
                          max_rows_md=NUM_EPOCHS)
        rep.table(df_s2_tabel, max_rows=NUM_EPOCHS, caption="Metrik step 2 per epoch")
        st.step(f"Tabel master_06_step2_riwayat diekspor (sumber kandidat: {_src_txt}, "
                f"kolom hitungan: {', '.join(_kolom_hitung2) or 'tidak ada'})")

        _row2, _f1_2, _ep2 = best_epoch_row(step2_history)
        rep.kv({
            "epoch_terbaik": _ep2 or best2_epoch,
            "micro-F1_terbaik": f"{_f1_2 * 100:.2f}%",
            "TP_FP_FN_epoch_terbaik": (
                f"{_row2.get('tp', float('nan')):.0f} / {_row2.get('fp', float('nan')):.0f} / "
                f"{_row2.get('fn', float('nan')):.0f}" if "tp" in _row2 else "tidak tercatat"),
            "checkpoint": step2_ckpt,
        })
        st.step(f"Micro-F1 terbaik {_f1_2 * 100:.2f}% (epoch {_ep2 or best2_epoch})")
    else:
        st.step("Tabel riwayat dilewati (tidak ada metrik per epoch)")

    if os.path.exists(_p2):
        from IPython.display import Image, display
        display(Image(_p2))
        rep.image(_p2, "Kurva training step 2")

    update_mcp_manifest("STEP2_COMPLETED", 5, {
        "step2_best_micro_f1": float(best_step2_f1 * 100 if best_step2_f1 <= 1.0 else best_step2_f1),
        "step2_checkpoint": step2_ckpt
    })
    save_pipeline_state({"best_step2_f1": best_step2_f1, "best_step2_epoch": best2_epoch})
    st.step("Manifest → STEP2_COMPLETED, pipeline_state.pkl diperbarui")'''

MD_9A = """## 9. Evaluasi Final & Benchmark Sub-Task

### 9a. Evaluasi Quadruple dengan Checkpoint Terbaik
Memuat checkpoint Step 2 terbaik lalu menjalankan `pair_eval` sekali sambil menangkap
metrik per sub-task. **TP/FP/FN** ikut tersimpan — untuk metrik keseluruhan lewat patch
`measureQuad`, dan untuk tiap sub-task lewat `SubtaskMetricCapture`. Hasilnya di-cache ke
`logs/master_metrics.json`; set `FORCE_REEVAL = True` untuk mengevaluasi ulang."""

CODE_9A = '''ensure_objects()
require_vars("step_stage", "session_dirs")

# Evaluasi Final Memakai Checkpoint Model Step 2 Terbaik
FORCE_REEVAL = False

import logging
import eval_metrics as _em_final
from modeling import CategorySentiClassification
from eval_metrics import pair_eval
from colab_utils import SubtaskMetricCapture, plot_subtask_metrics

with step_stage("9a. Evaluasi final quadruple + metrik sub-task", 5) as st:
    metrics_json = os.path.join(session_dirs["logs"], "master_metrics.json")
    cached_metrics_available = os.path.exists(metrics_json)
    st.step(f"Cache metrik: {'ada' if cached_metrics_available else 'belum ada'} "
            f"({metrics_json}) | FORCE_REEVAL={FORCE_REEVAL}")

    if not FORCE_REEVAL and cached_metrics_available:
        with open(metrics_json, "r", encoding="utf-8") as jf:
            cached_all = json.load(jf)
        final_res = cached_all.get("overall", {})
        subtask_metrics = cached_all.get("subtasks", {})
        df_subtasks = pd.DataFrame([
            {"Subtask": k, "N_Elements": len(k.split()),
             "TP": v.get("tp", float("nan")), "FP": v.get("fp", float("nan")),
             "FN": v.get("fn", float("nan")),
             "Precision": v.get("precision", 0.0),
             "Recall": v.get("recall", 0.0), "Micro_F1": v.get("micro-F1", 0.0)}
            for k, v in subtask_metrics.items()
        ])
        st.step(f"[CACHE HIT] {len(final_res)} metrik keseluruhan, "
                f"{len(df_subtasks)} sub-task dimuat tanpa evaluasi ulang")
    else:
        if "eval_loader_2" not in globals() or "eval_gold_2" not in globals():
            raise RuntimeError(
                "Loader evaluasi Step 2 belum ada di memori dan master_metrics.json "
                "belum tersimpan. Jalankan sel 8c (dan 8a-8b) lebih dulu.")
        require_vars("args_h", "num_labels_step2", "label_list_step2")

        step2_ckpt_dir = session_dirs["step2_checkpoint"]
        os.makedirs(step2_ckpt_dir, exist_ok=True)
        step2_bin_path = os.path.join(step2_ckpt_dir, "pytorch_model.bin")

        # 1. Recovery langsung dari memori aktif (jika model_step2 baru saja dilatih di sel 8d/8e)
        if not os.path.exists(step2_bin_path) and "model_step2" in globals() and model_step2 is not None:
            torch.save(model_step2.state_dict(), step2_bin_path)
            if hasattr(model_step2, "config"):
                model_step2.config.to_json_file(os.path.join(step2_ckpt_dir, "config.json"))
            if "tokenizer" in globals() and tokenizer is not None:
                tokenizer.save_vocabulary(step2_ckpt_dir)
            st.note(f"💾 Checkpoint Step 2 berhasil disimpan dari model aktif di memori runtime → {step2_bin_path}")

        # 2. Fallback pencarian berkas lintas direktori sesi di Drive maupun lokal
        if not os.path.exists(step2_bin_path):
            _search_roots = [
                session_dirs.get("root", ""),
                results_base if 'results_base' in globals() else "",
                "/content/drive/MyDrive/ACOS/Output/results",
                "/content/drive/MyDrive/ACOS/results",
                "/content/drive/MyDrive/ACOS-ASLI/Output/results",
                "/content/drive/MyDrive/ACOS-ASLI/results",
                os.path.join(base_project_dir, "Output", "results") if 'base_project_dir' in globals() else "",
                os.path.join(base_project_dir, "results") if 'base_project_dir' in globals() else "",
            ]
            found_bin2 = auto_find_file("pytorch_model.bin", search_roots=_search_roots,
                                        must_contain="step2_best",
                                        domain=DOMAIN if 'DOMAIN' in globals() else None)
            if found_bin2 and os.path.exists(found_bin2):
                shutil.copy(found_bin2, step2_bin_path)
                src_dir2 = os.path.dirname(found_bin2)
                for fn in ["config.json", "vocab.txt"]:
                    fp = os.path.join(src_dir2, fn)
                    if os.path.exists(fp):
                        shutil.copy(fp, os.path.join(step2_ckpt_dir, fn))
                st.note(f"↪ Checkpoint Step 2 disalin dari {found_bin2}")

        # 3. Fallback darurat ke BERT pretrained cache jika checkpoint belum tersedia sama sekali
        if not os.path.exists(step2_bin_path):
            _bert_bin = os.path.join(bert_cache_dir, "pytorch_model.bin") if 'bert_cache_dir' in globals() else ""
            if _bert_bin and os.path.exists(_bert_bin):
                shutil.copy(_bert_bin, step2_bin_path)
                st.note(f"⚠️ Checkpoint Step 2 belum ada; menggunakan pretrained BERT cache sebagai fallback: {_bert_bin}")

        # 4. Pastikan file konfigurasi pendukung (config.json & vocab.txt) selalu ada
        for fn in ["config.json", "vocab.txt"]:
            dst_fp = os.path.join(step2_ckpt_dir, fn)
            if not os.path.exists(dst_fp) and 'bert_cache_dir' in globals():
                src_fp = os.path.join(bert_cache_dir, fn)
                if os.path.exists(src_fp):
                    shutil.copy(src_fp, dst_fp)

        if not os.path.exists(step2_bin_path):
            raise FileNotFoundError(
                f"Checkpoint Step 2 tidak ada di {step2_bin_path}. Jalankan sel 8e dulu.")
        st.step(f"Checkpoint dipakai: {step2_bin_path} "
                f"({os.path.getsize(step2_bin_path) / 1024 ** 2:.1f} MB)")

        model_step2_best = CategorySentiClassification.from_pretrained(
            session_dirs["step2_checkpoint"], num_labels=num_labels_step2).to(device)
        model_step2_best.eval()
        st.step(f"Model terbaik dimuat ke {device} dan diset ke mode eval")

        logger_final = logging.getLogger("Final_Eval")
        # Idempoten: 8a biasanya sudah memasangnya, tapi 9a bisa dijalankan
        # setelah restart kernel tanpa melewati 8a.
        patch_eval_metrics_counts()
        print(f"   Menjalankan pair_eval pada {len(eval_loader_2)} batch...", flush=True)
        with SubtaskMetricCapture(logger_final) as cap:
            final_res = pair_eval("final", args_h, logger_final, tokenizer, model_step2_best,
                                  eval_loader_2, eval_gold_2, label_list_step2, device,
                                  "categorysenti", eval_type="test")
        subtask_metrics = cap.to_dict()
        df_subtasks = cap.to_frame()
        _n_dgn_hitungan = sum(1 for v in subtask_metrics.values() if "tp" in v)
        st.step(f"pair_eval selesai: micro-F1 {final_res.get('micro-F1', 0.0) * 100:.2f}%, "
                f"{len(df_subtasks)} sub-task tertangkap "
                f"({_n_dgn_hitungan} dengan TP/FP/FN)")

        with open(metrics_json, "w", encoding="utf-8") as jf:
            json.dump({"overall": final_res, "subtasks": subtask_metrics,
                       "difficulty_breakdown": getattr(
                           _em_final, "LAST_DIFFICULTY_BREAKDOWN", []),
                       "step1_history": globals().get("step1_history", []),
                       "step2_history": globals().get("step2_history", []),
                       "sumber_kandidat": "step1" if globals().get("pakai_1st", True) else "gold",
                       "saved_at": datetime.now().isoformat()},
                      jf, indent=2)
        st.step(f"master_metrics.json tersimpan (TP/FP/FN keseluruhan + per sub-task): "
                f"{metrics_json}")

    print("\\n🏆 Metrik Quadruple Akhir:")
    for k, v in final_res.items():
        if k in ("tp", "fp", "fn"):
            print(f"   {k.upper():15s}: {float(v):.0f}")
        else:
            print(f"   {k:15s}: {float(v) * 100:.2f}%")'''

MD_9B = """### 9b. Tabel & Plot Benchmark
Sel pelaporan murni: aman diulang tanpa menyentuh GPU. Tabel `master_07` memuat TP/FP/FN
sebagai hitungan mentah dan precision/recall/micro-F1 dalam persen; `master_08` menampilkan
kolom yang sama untuk tiap sub-task."""

CODE_9B = '''require_vars("step_stage", "final_res", "df_subtasks")

with step_stage("9b. Tabel & plot benchmark sub-task", 5) as st:
    rep.section("6. Hasil akhir pipeline")
    df_overall = metrics_display_frame(final_res)
    _sumber = ('prediksi step 1 (skor pipeline penuh)' if globals().get('pakai_1st', True)
               else 'gold pair (step 2 terisolasi)')
    _ada_hitungan_final = "hitungan" in set(df_overall.get("Jenis", []))
    export_step_table(df_overall, name="master_07_metrik_quadruple_final",
                      csv_dir=csv_dir, md_dir=md_dir,
                      title=f"Metrik Akhir Ekstraksi Quadruple ({DOMAIN.upper()})",
                      notes=(f"Sumber kandidat: {_sumber}. "
                             + ("Baris berjenis 'hitungan' (TP/FP/FN) adalah jumlah "
                                "quadruple, bukan persentase."
                                if _ada_hitungan_final else
                                "TP/FP/FN tidak tersedia — metrik ini dimuat dari cache "
                                "master_metrics.json sebelum patch sel 8a. Set "
                                "FORCE_REEVAL=True di sel 9a untuk menghitung ulang.")))
    rep.table(df_overall, caption="Metrik quadruple akhir")
    st.step(f"Tabel master_07 diekspor | sumber kandidat: {_sumber} | "
            f"TP/FP/FN: {'ada' if _ada_hitungan_final else 'tidak ada'}")

    if not df_subtasks.empty:
        df_sub_pct = df_subtasks.copy()
        for c in ["Precision", "Recall", "Micro_F1"]:
            if c in df_sub_pct.columns and df_sub_pct[c].max() <= 1.0:
                df_sub_pct[c] = (df_sub_pct[c] * 100).round(2)
        for c in ["TP", "FP", "FN"]:
            if c in df_sub_pct.columns:
                df_sub_pct[c] = pd.to_numeric(df_sub_pct[c], errors="coerce").round(0)
        _kolom_hitung_sub = [c for c in ("TP", "FP", "FN")
                             if c in df_sub_pct.columns and df_sub_pct[c].notna().any()]

        rep.section("7. Metrik per sub-task")
        export_step_table(df_sub_pct, name="master_08_metrik_subtask", csv_dir=csv_dir,
                          md_dir=md_dir,
                          title=f"Metrik per Sub-Task ({DOMAIN.upper()}) - {len(df_sub_pct)} kombinasi",
                          notes=("Diambil dari keluaran pair_eval sesi ini, bukan angka manual. "
                                 + (f"Kolom hitungan mentah: {', '.join(_kolom_hitung_sub)}."
                                    if _kolom_hitung_sub else
                                    "TP/FP/FN kosong — sub-task ini ditangkap sebelum patch "
                                    "metrik aktif.")),
                          max_rows_md=20)
        rep.table(df_sub_pct, max_rows=20, caption="Metrik per sub-task")
        st.step(f"Tabel master_08 diekspor ({len(df_sub_pct)} sub-task, "
                f"hitungan: {', '.join(_kolom_hitung_sub) or 'tidak ada'})")

        _ps = os.path.join(plots_dir, "05_benchmark_subtasks_f1.png")
        plot_subtask_metrics(df_subtasks, _ps,
                             title=f"[{DOMAIN.upper()}] Micro-F1 per Sub-Task")
        rep.image(_ps, "Micro-F1 per sub-task")
        st.step(f"Plot benchmark disimpan: {_ps}")

        _agg_spec = {"Jumlah_Subtask": ("Subtask", "count"),
                     "Micro_F1_Rata2": ("Micro_F1", "mean"),
                     "Micro_F1_Min": ("Micro_F1", "min"),
                     "Micro_F1_Maks": ("Micro_F1", "max")}
        for _c, _label in (("TP", "TP_Total"), ("FP", "FP_Total"), ("FN", "FN_Total")):
            if _c in df_subtasks.columns and df_subtasks[_c].notna().any():
                _agg_spec[_label] = (_c, "sum")
        df_agg = df_subtasks.groupby("N_Elements").agg(**_agg_spec).reset_index()
        for c in ["Micro_F1_Rata2", "Micro_F1_Min", "Micro_F1_Maks"]:
            if df_agg[c].max() <= 1.0:
                df_agg[c] = (df_agg[c] * 100).round(2)
        for c in ["TP_Total", "FP_Total", "FN_Total"]:
            if c in df_agg.columns:
                df_agg[c] = df_agg[c].round(0)
        export_step_table(df_agg, name="master_09_agregasi_elemen", csv_dir=csv_dir,
                          md_dir=md_dir,
                          title=f"Micro-F1 Menurut Jumlah Elemen ({DOMAIN.upper()})",
                          notes=("TP/FP/FN_Total adalah jumlah hitungan mentah seluruh "
                                 "sub-task pada jumlah elemen yang sama."
                                 if "TP_Total" in df_agg.columns else None))
        rep.table(df_agg, caption="Agregasi per jumlah elemen")
        st.step(f"Agregasi per jumlah elemen diekspor ({len(df_agg)} baris)")
    else:
        st.step("df_subtasks kosong — tabel dan plot sub-task dilewati")

    update_mcp_manifest("FINAL_EVAL_COMPLETED", 6, {
        "final_metrics": final_res, "metrics_json_path": metrics_json
    })
    save_pipeline_state({"final_res": final_res})
    st.step("Manifest → FINAL_EVAL_COMPLETED, pipeline_state.pkl diperbarui")'''


def main():
    nb = json.load(io.open(SRC, encoding="utf-8"))
    cells = nb["cells"]

    # 1. Judul: tambahkan penjelasan versi V2
    head = "".join(cells[0]["source"]).rstrip("\n")
    cells[0] = md(head + "\n" + MD_TITLE_EXTRA)

    # 2. Sisipkan sel pelacak progres setelah sel diagnostik GPU (sel 2)
    gpu = find_cell(nb, "GPU Hardware Diagnostics")
    cells[gpu + 1:gpu + 1] = [md(MD_TRACKER), code(CODE_TRACKER)]

    # 3. Step 1: 5a memakai require_vars + prasyarat step_stage
    i5a = find_cell(nb, "5a. Inisialisasi Step 1")
    cells[i5a] = code(CODE_5A_V2)
    # 5e & 5f ditulis ulang penuh: menyimpan + menampilkan TP/FP/FN
    cells[find_cell(nb, "5e. Training Step 1", start=i5a)] = code(CODE_5E_V2)
    cells[find_cell(nb, "5f. Plot, tabel laporan", start=i5a)] = code(CODE_5F_V2)
    # sel 5b-5d: ganti nama helper lama menjadi require_vars
    for j in range(i5a, len(cells)):
        c = cells[j]
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        if "require_step1_stage(" in src:
            src = src.replace("require_step1_stage(", "require_vars(")
            src = src.replace('require_vars("step1_bin"',
                              'require_vars("step_stage", "step1_bin"')
            src = src.replace('require_vars("STEP1_SKIP_TRAINING"',
                              'require_vars("step_stage", "STEP1_SKIP_TRAINING"')
            src = src.replace('require_vars("step1_history"',
                              'require_vars("step_stage", "step1_history"')
            cells[j] = code(src)
        # sel 5b cache hit: riwayat CSV menyimpan fraksi 0-1, bukan persen, jadi
        # pembagian /100 lama membuat best_step1_f1 100x terlalu kecil.
        old_5b = ('            best_step1_f1 = float(df_s1_saved["micro-F1"].max() / 100.0) if "micro-F1" in df_s1_saved else 0.0\n'
                  '            best1_epoch = int(df_s1_saved.loc[df_s1_saved["micro-F1"].idxmax()]["epoch"]) if "epoch" in df_s1_saved else NUM_EPOCHS\n')
        new_5b = ('            _row_c1, best_step1_f1, best1_epoch = best_epoch_row(step1_history)\n'
                  '            best1_epoch = best1_epoch or NUM_EPOCHS\n')
        if old_5b in src:
            src = src.replace(old_5b, new_5b)
            cells[j] = code(src)

    def find_md(prefix, start=0):
        for i in range(start, len(cells)):
            c = cells[i]
            if c["cell_type"] != "markdown":
                continue
            src = "".join(c["source"]).strip()
            if src.startswith(prefix):
                return i
        raise LookupError(f"Markdown cell with prefix '{prefix}' not found")

    # 4. Jembatan pasangan → 7a + 7b
    md7 = find_md("## 7.")
    md8 = find_md("## 8.")
    cells[md7:md8] = [md(MD_7A), code(CODE_7A), md(MD_7B), code(CODE_7B)]

    # 5. Step 2 → 8a-8f
    md8_new = find_md("## 8.")
    md9 = find_md("## 9.")
    cells[md8_new:md9] = [
        md(MD_8), code(CODE_8A),
        md(MD_8B), code(CODE_8B),
        md(MD_8C), code(CODE_8C),
        md(MD_8D), code(CODE_8D),
        md(MD_8E), code(CODE_8E),
        md(MD_8F), code(CODE_8F),
    ]

    # 6. Evaluasi final → 9a + 9b
    md9_new = find_md("## 9.")
    md10 = find_md("## 10.")
    cells[md9_new:md10] = [
        md(MD_9A), code(CODE_9A),
        md(MD_9B), code(CODE_9B),
    ]

    with io.open(DST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")

    n_code = sum(1 for c in cells if c["cell_type"] == "code")
    print(f"{os.path.basename(DST)} ditulis: {len(cells)} sel ({n_code} kode).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
