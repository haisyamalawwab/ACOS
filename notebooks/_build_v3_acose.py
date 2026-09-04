"""Membangun 00_ACOS_Master_Pipeline_Colab_V3_ACOSE.ipynb dari V2 STAGED.

V3 = V2 + tahap ACOSE (elemen kelima: emosi). Generator ini tidak mengubah
seluruh sel turunan PRO_Resume/V2; ia:

  1. menjalankan `_build_staged_v2.main()` agar berkas V2 STAGED selalu mutakhir,
  2. memuat hasil V2, menambah penjelasan versi pada judul,
  3. menyisipkan seksi "10. ACOSE" (sel 10a-10e) sebelum demo inferensi,
  4. menomori ulang seksi lama 10→11 (demo inferensi) dan 11→12 (ringkasan).

Tahap ACOSE memakai paket `absa5/` di root repo: bootstrap quad → quint lewat
`LexiconEmotionTagger` (label `emot_id_netral`), persiapan data torch-free,
training dua tahap (ekstraksi span + klasifikasi label factored), evaluasi
end-to-end, dan pelaporan ke kerangka `rep`/`master_*` yang sama dengan V2.

Skrip idempoten: berkas tujuan ditulis ulang dari nol setiap kali dijalankan.
"""
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import _build_staged_v2 as V2  # noqa: E402

SRC_V2 = V2.DST  # 00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb (dihasilkan ulang dulu)
DST = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V3_ACOSE.ipynb")

md = V2.md
code = V2.code


MD_TITLE_ACOSE = """
---

### Versi V3 — ACOSE: elemen kelima (emosi)

Notebook ini adalah turunan dari `00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb`
(dibangun ulang oleh `_build_v3_acose.py`, yang menjalankan generator V2 lebih dulu).
Seluruh tahap V2 tidak diubah. Tambahan V3: **seksi 10 (sel 10a-10e)** yang
menjalankan ACOSE — ekstraksi quintuple aspect-category-opinion-sentiment-
**emotion** dengan paket `absa5/` di root repo.

| Sel | Isi | Torch? | Aman diulang |
|---|---|---|---|
| 10a | Bootstrap quad → quint (leksikon emosi) + ekspor tugas anotasi | tidak | ya (cache) |
| 10b | Konfigurasi run + persiapan data (retokenisasi, remap span, pair file) | tidak | ya (cache) |
| 10c | Training ekstraksi span + klasifikasi label (factored) | ya | cache per tahap |
| 10d | Evaluasi end-to-end quintuple pada test set | ya | ya (`FORCE_REEVAL_ACOSE`) |
| 10e | Tabel, plot, manifest, state | tidak | ya |

**Khusus ACOSE, seluruh hasil disimpan di folder Drive sendiri** -
`/content/drive/MyDrive/ACOSE/<domain>/` (lokal: `Output/ACOSE/<domain>/`) dengan
subfolder `data`, `annotation`, `extraction`, `classification`, `logs`, `csv`,
`md`, `plots`. Lokasinya stabil lintas sesi, sehingga cache sel 10a-10e tidak
tergantung folder sesi ACOS yang aktif.

Keputusan desain yang mengikat tahap ini:

- Tidak ada dataset quintuple publik, jadi kolom emosi di-*bootstrap* lewat
  `LexiconEmotionTagger` dan berstatus **suggested**. Hasil 10c-10d mengukur
  leksikon, bukan model, sampai anotasi manusia (CSV + pedoman yang diekspor
  sel 10a) selesai.
- Label emosi `emot_id_netral` (sedih, marah, cinta, takut, senang + netral).
  Kelas netral wajib: ulasan faktual seperti "harganya wajar" positif tanpa
  muatan emosi, dan fallback sentimen tagger menunjuk ke kelas ini.
- Kepala label **factored** (13 + 3 + 6 = 22 output), bukan joint (13×3×6 =
  234 sel yang sebagian besar kosong pada ~2,5 ribu tuple).
- Dua domain didukung: `rest16` (data quad Inggris, emosi di-bootstrap leksikon,
  status `suggested`) dan `resto_id` (data quint Indonesia di `data/Demo-Resto-ID/`,
  kolom emosi sudah ada, status `annotated`). Domain `laptop` **ditolak** `absa5`
  (taksonomi 121 kategori → 1815 sel label tidak trainable).
- Sel 10a menghitung H(emosi | sentimen) per split. Nilai 0 bit berarti kolom
  emosi cuma penggantian nama sentimen pada data itu — baca verdict-nya sebelum
  menafsirkan metrik 10d."""

MD_10A = """## 10. ACOSE: Ekstraksi Quintuple (ACOS + Emosi)

### 10a. Sumber Data Quint ACOSE
Menyiapkan berkas quint di folder khusus `ACOSE/<domain>/data/` (lihat judul versi
V3). Dua jalur, dipilih otomatis dari `DOMAIN` lewat tabel `DOMAIN_SOURCES`:

| DOMAIN | Sumber | Schema sumber | Kolom emosi | Status |
|---|---|---|---|---|
| `rest16` | `data/Restaurant-ACOS/` | quad | dibuat `LexiconEmotionTagger` | `suggested` |
| `resto_id` | `data/Demo-Resto-ID/` | quint | sudah ada di berkas | `annotated` |

Untuk `rest16` leksikonnya kata pemicu Indonesia sementara datanya Inggris, jadi
hampir semua label datang dari fallback sentimen — sel ini melaporkannya apa adanya
lewat H(emosi | sentimen) dan verdict redundansi, bukan menyembunyikannya. Untuk
`resto_id` kolom emosi dipakai apa adanya (tanpa leksikon) dan kedua angka itu tetap
dihitung dari berkas, sehingga kedua jalur bisa dibandingkan dengan ukuran yang sama.

Output tambahan: CSV tugas anotasi (satu baris per tuple, `emotion_final`
dibiarkan kosong untuk manusia) dan pedoman anotasinya di `ACOSE/<domain>/annotation/`.
Cache: dilewati bila berkas quint sudah ada, kecuali `ACOSE_FORCE_BOOTSTRAP=True`."""

CODE_10A = '''require_vars("step_stage", "base_project_dir", "DOMAIN", "rep")

# Paket absa5 ada di root repo; pastikan bisa diimpor secara otomatis & robust.
def _ensure_absa5(base_dir):
    import importlib, os, shutil, subprocess, sys
    try:
        import absa5
        return
    except ImportError:
        pass

    cands = [base_dir] if base_dir else []
    cands.extend([
        os.path.join(base_dir, "ACOS") if base_dir else None,
        "/content/drive/MyDrive/ACOS",
        "/content/drive/MyDrive/ACOS-ASLI",
        "/content/ACOS",
        "/content",
        os.path.abspath("."),
        os.path.abspath(".."),
    ])
    for cand in cands:
        if cand and os.path.isdir(os.path.join(cand, "absa5")):
            if cand not in sys.path:
                sys.path.insert(0, cand)
            try:
                import absa5
                print(f"✅ Paket absa5 berhasil dimuat dari: {cand}")
                return
            except ImportError:
                pass

    print("⚠️ Paket absa5 belum ada di direktori lokal / Google Drive.")
    print("📥 Mengunduh paket absa5 dari GitHub ke direktori proyek...")
    tmp_clone = "/tmp/ACOS_absa5_clone"
    if os.path.exists(tmp_clone):
        shutil.rmtree(tmp_clone, ignore_errors=True)
    subprocess.run(["git", "clone", "--depth", "1", "https://github.com/haisyamalawwab/ACOS.git", tmp_clone], check=True)
    src_absa5 = os.path.join(tmp_clone, "absa5")
    if os.path.isdir(src_absa5):
        target = base_dir if (base_dir and os.path.isdir(base_dir)) else os.path.abspath(".")
        dst_absa5 = os.path.join(target, "absa5")
        shutil.copytree(src_absa5, dst_absa5, dirs_exist_ok=True)
        if target not in sys.path:
            sys.path.insert(0, target)
        print(f"✅ Paket absa5 berhasil disinkronkan ke: {dst_absa5}")
    shutil.rmtree(tmp_clone, ignore_errors=True)

_ensure_absa5(base_project_dir)

from absa5 import get_schema
from absa5.data import read_records, write_records
from absa5.emotion import (
    LexiconEmotionTagger,
    export_annotation_tasks,
    extend_file,
    sentiment_redundancy,
)
from absa5.selftest import run_gates
from absa5.taxonomy import EMOTIONS

# Toggle: True = bootstrap ulang meski berkas quint sudah ada.
ACOSE_FORCE_BOOTSTRAP = False
# Label emosi: EmoT + kelas netral eksplisit; fallback sentimen tagger
# menunjuk ke 'netral', jadi label set tanpa kelas itu akan ditolak tagger.
ACOSE_EMOTION_SET = "emot_id_netral"

# Sumber data per domain. `schema` menentukan jalur yang dipakai sel ini:
#   quad  -> kolom emosi belum ada, dibuat oleh leksikon (status suggested)
#   quint -> kolom emosi sudah ada di berkas (status annotated, tanpa leksikon)
DOMAIN_SOURCES = {
    "rest16": {"dir": "Restaurant-ACOS", "schema": "quad", "category_set": "rest16"},
    "resto_id": {"dir": "Demo-Resto-ID", "schema": "quint", "category_set": "resto_id"},
}

with step_stage("10a. Sumber data quint ACOSE (bootstrap emosi bila perlu)", 9) as st:
    if DOMAIN not in DOMAIN_SOURCES:
        raise RuntimeError(
            f"ACOSE mendukung DOMAIN {sorted(DOMAIN_SOURCES)}; '{DOMAIN}' tidak ada. "
            f"Domain 'laptop' khususnya ditolak absa5: taksonomi 121 kategori "
            f"membuat ruang label 121x3x6 = 1815 sel yang tidak trainable pada "
            f"jumlah data semacam ini.")
    _srcspec = DOMAIN_SOURCES[DOMAIN]
    ACOSE_CATEGORY_SET = _srcspec["category_set"]
    ACOSE_SOURCE_SCHEMA = _srcspec["schema"]
    raw_dir_src = os.path.join(base_project_dir, "data", _srcspec["dir"])

    # Khusus ACOSE: seluruh hasil disimpan di folder Drive "ACOSE" yang berdiri
    # sendiri (stabil lintas sesi), bukan di dalam folder sesi pipeline ACOS.
    if os.path.exists("/content/drive/MyDrive"):
        acose_save_dir = "/content/drive/MyDrive/ACOSE"
    else:
        acose_save_dir = os.path.join(base_project_dir, "Output", "ACOSE")
    acose_root = os.path.join(acose_save_dir, DOMAIN)
    acose_raw_dir = os.path.join(acose_root, "data")
    acose_annot_dir = os.path.join(acose_root, "annotation")
    acose_logs_dir = os.path.join(acose_root, "logs")
    acose_csv_dir = os.path.join(acose_root, "csv")
    acose_md_dir = os.path.join(acose_root, "md")
    acose_plots_dir = os.path.join(acose_root, "plots")
    for _d in (acose_raw_dir, acose_annot_dir, acose_logs_dir, acose_csv_dir,
               acose_md_dir, acose_plots_dir):
        os.makedirs(_d, exist_ok=True)

    # Gerbang kesehatan absa5 sebelum dipakai: paket sudah terimpor di atas,
    # tetapi kegagalan persiapan/skim data bisa lolos diam-diam (pola yang sama
    # dengan bug colab_utils). Jalankan selftest torch-free yang relevan dengan
    # cepat; kalau ada yang gagal, proses berhenti di sini, bukan di tengah run.
    _g_ok, _g_res = run_gates(
        base_project_dir, only=["torch_free", "prepare", "decode", "features"])
    for _g in _g_res:
        if not _g.passed:
            raise RuntimeError(
                f"selftest absa5 gagal '{_g.name}': "
                + "; ".join(getattr(_g, "messages", []) or []))
    st.step(f"Selftest absa5 ({len(_g_res)} gerbang) LULUS di {base_project_dir}")

    emotion_labels = list(EMOTIONS.get(ACOSE_EMOTION_SET))
    if ACOSE_SOURCE_SCHEMA == "quad":
        tagger = LexiconEmotionTagger(label_set=ACOSE_EMOTION_SET)
        st.step(f"Sumber quad → emosi dibuat leksikon '{tagger.name}' (status "
                f"suggested) | label ({len(emotion_labels)}): "
                f"{', '.join(emotion_labels)}")
    else:
        tagger = None
        st.step(f"Sumber sudah quint → kolom emosi dipakai apa adanya (status "
                f"annotated, tanpa leksikon) | label ({len(emotion_labels)}): "
                f"{', '.join(emotion_labels)}")

    # Penanda identitas folder (singkat): folder ACOSE adalah hasil ABSA5
    # Quintuple Extraction, bukan ACOS 4-elemen biasa.
    _acose_tag = ("ABSA5 Quintuple Extraction "
                  "(Aspect, Category, Opinion, Sentiment, Emotion)")
    with open(os.path.join(acose_root, "_ACOSE.txt"), "w", encoding="utf-8") as _mf:
        _mf.write(_acose_tag + chr(10))

    def _report_from_quint(path):
        """Laporan setara extend_file untuk berkas yang SUDAH quint.

        Tanpa ini, jalur data teranotasi tidak punya distribusi emosi maupun
        H(emosi | sentimen) — dua angka yang menentukan apakah elemen kelima
        layak dilatih, jadi keduanya dihitung dari berkas apa adanya.
        """
        recs = read_records(path, get_schema("quint"))
        dist, joint, n = {}, {}, 0
        for _rec in recs:
            for _t in _rec.tuples:
                _e = str(_t.get("emotion"))
                dist[_e] = dist.get(_e, 0) + 1
                _k = (str(_t.get("sentiment")), _e)
                joint[_k] = joint.get(_k, 0) + 1
                n += 1
        out = {"rows": len(recs), "tuples": n,
               "distribution": dict(sorted(dist.items())),
               "tagger": "none (berkas sumber sudah quint)",
               "status": "annotated",
               "warning": ("kolom emosi berasal dari berkas sumber; pastikan "
                           "provenance-nya tercatat sebelum dipublikasikan"),
               "input": path, "output": path}
        out.update(sentiment_redundancy(joint))
        return out

    quint_files, acose_bootstrap_reports = {}, {}
    for split in ("train", "dev", "test"):
        src = os.path.join(raw_dir_src,
                           f"{DOMAIN}_{ACOSE_SOURCE_SCHEMA}_{split}.tsv")
        dst = os.path.join(acose_raw_dir, f"{DOMAIN}_quint_{split}.tsv")
        rep_path = os.path.join(acose_raw_dir, f"_bootstrap_{split}.json")
        if not os.path.exists(src):
            raise FileNotFoundError(f"Berkas sumber tidak ada: {src}")
        if os.path.exists(dst) and os.path.exists(rep_path) and not ACOSE_FORCE_BOOTSTRAP:
            with open(rep_path, "r", encoding="utf-8") as jf:
                acose_bootstrap_reports[split] = json.load(jf)
            st.step(f"[CACHE HIT] {os.path.basename(dst)} sudah ada "
                    f"({acose_bootstrap_reports[split]['rows']} baris)")
        elif ACOSE_SOURCE_SCHEMA == "quad":
            acose_bootstrap_reports[split] = extend_file(
                src, dst, tagger=tagger, report_path=rep_path)
            _r = acose_bootstrap_reports[split]
            st.step(f"{os.path.basename(dst)}: {_r['rows']} baris, {_r['tuples']} tuple "
                    f"→ {_r['distribution']}")
        else:
            # Berkas sudah quint: salin ke folder ACOSE lewat pembacaan skema,
            # bukan copy byte, supaya berkas cacat tertangkap di sini.
            _recs = read_records(src, get_schema("quint"))
            write_records(dst, _recs, get_schema("quint"))
            acose_bootstrap_reports[split] = _report_from_quint(dst)
            with open(rep_path, "w", encoding="utf-8") as jf:
                json.dump(acose_bootstrap_reports[split], jf, indent=2,
                          ensure_ascii=False)
            _r = acose_bootstrap_reports[split]
            st.step(f"{os.path.basename(dst)}: {_r['rows']} baris, {_r['tuples']} tuple "
                    f"(sudah quint) → {_r['distribution']}")
        quint_files[split] = dst

    st.step("H(emosi | sentimen): "
            + "; ".join(f"{s} {acose_bootstrap_reports[s]['conditional_entropy_bits']:.3f} bit"
                        for s in ("train", "dev", "test")))
    _verdict = acose_bootstrap_reports["train"]["redundancy_verdict"]
    st.note("⚠️ Verdict (train): " + _verdict)
    st.note("⚠️ " + acose_bootstrap_reports["train"]["warning"])

    # Tugas anotasi dari split test: CSV satu baris per tuple dengan kolom
    # emotion_final kosong + pedoman anotasinya, untuk validasi manusia.
    _annot_csv = os.path.join(acose_annot_dir, f"{DOMAIN}_emotion_annotation_tasks.csv")
    acose_annot_report = export_annotation_tasks(
        read_records(quint_files["test"], get_schema("quint")),
        _annot_csv, tagger=tagger, emotion_set=ACOSE_EMOTION_SET)
    st.step(f"Tugas anotasi: {acose_annot_report['rows']} baris → {_annot_csv}")

    rep.section("8. ACOSE: sumber data quint & informasi emosi")
    rep.kv({
        "label_set": ACOSE_EMOTION_SET,
        "label": ", ".join(emotion_labels),
        "sumber": f"{os.path.basename(raw_dir_src)} (schema {ACOSE_SOURCE_SCHEMA})",
        "tagger": acose_bootstrap_reports["train"]["tagger"],
        "status": acose_bootstrap_reports["train"]["status"],
        "H_emosi_sentimen_train": f"{acose_bootstrap_reports['train']['conditional_entropy_bits']:.3f} bit",
        "verdict": _verdict,
        "tugas_anotasi": _annot_csv,
    })
    rep.text(acose_bootstrap_reports["train"]["warning"])

    df_emosi = pd.DataFrame([
        {"Split": s,
         **{lab: acose_bootstrap_reports[s]["distribution"].get(lab, 0)
            for lab in emotion_labels},
         "Total_Tuple": acose_bootstrap_reports[s]["tuples"],
         "H_bit": round(acose_bootstrap_reports[s]["conditional_entropy_bits"], 3)}
        for s in ("train", "dev", "test")
    ])
    export_step_table(df_emosi, name="master_10_acose_distribusi_emosi",
                      csv_dir=acose_csv_dir, md_dir=acose_md_dir,
                      title=f"Distribusi Emosi per Split ({DOMAIN.upper()})",
                      notes=(f"Sumber: {os.path.basename(raw_dir_src)}, schema "
                             f"{ACOSE_SOURCE_SCHEMA}, status "
                             f"{acose_bootstrap_reports['train']['status']}. "
                             f"H_bit = H(emosi | sentimen); 0 berarti kolom emosi "
                             f"tidak menambah informasi. Verdict train: " + _verdict))
    rep.table(df_emosi, caption="Distribusi emosi & H(emosi | sentimen) per split")
    st.step("Tabel master_10_acose_distribusi_emosi diekspor")

    update_mcp_manifest("ACOSE_BOOTSTRAPPED", 7, {
        "acose_label_set": ACOSE_EMOTION_SET,
        "acose_source_schema": ACOSE_SOURCE_SCHEMA,
        "acose_emotion_status": acose_bootstrap_reports["train"]["status"],
        "acose_redundancy_bits": acose_bootstrap_reports["train"]["conditional_entropy_bits"],
        "acose_annotation_tasks": acose_annot_report["rows"],
    })
    save_pipeline_state({"acose_quint_files": quint_files})
    st.step("Manifest → ACOSE_BOOTSTRAPPED, pipeline_state.pkl diperbarui")'''

MD_10B = """### 10b. Konfigurasi Run & Persiapan Data ACOSE
Membentuk `RunConfig` absa5 (schema `quint`, kepala label factored, backbone =
cache BERT yang sama dengan Step 1/2) lalu `prepare_data`: retokenisasi,
remap span ke subword, dan pembentukan pair file per split. Torch-free.
Cache: bila `_prepare.json` sudah ada, artefak dimuat tanpa menghitung ulang."""

CODE_10B = '''require_vars("step_stage", "acose_root", "acose_raw_dir", "bert_cache_dir",
             "ACOSE_CATEGORY_SET", "ACOSE_EMOTION_SET",
             "MAX_SEQ_LENGTH", "NUM_EPOCHS", "SEED")

if "absa5" not in sys.modules and "_ensure_absa5" in globals():
    _ensure_absa5(base_project_dir if "base_project_dir" in globals() else None)

from absa5 import RunConfig
from absa5.config import (
    DataConfig,
    EncoderConfig,
    HeadConfig,
    TokenizerConfig,
    TrainConfig,
)
from absa5.models import head_size_report
from absa5.pipeline import DataArtifacts, prepare_data

ACOSE_EPOCHS = NUM_EPOCHS
ACOSE_BATCH_SIZE = 16
ACOSE_EVAL_BATCH_SIZE = 32
ACOSE_LR = 2e-5

with step_stage("10b. Konfigurasi run ACOSE + persiapan data quint", 6) as st:
    cfg_acose = RunConfig(
        name=f"acose_{DOMAIN}",
        output_dir=acose_root,
        notes="ACOSE quintuple dari master pipeline Colab V3 (emosi masih suggested)",
        data=DataConfig(
            raw_dir=acose_raw_dir, work_dir=acose_root, domain=DOMAIN,
            schema="quint", category_set=ACOSE_CATEGORY_SET, sentiment_set="acos",
            emotion_set=ACOSE_EMOTION_SET, max_seq_length=MAX_SEQ_LENGTH,
        ),
        tokenizer=TokenizerConfig(kind="wordpiece", path=bert_cache_dir,
                                  do_lower_case=True),
        encoder=EncoderConfig(kind="bert", model_name_or_path=bert_cache_dir),
        heads=HeadConfig(label_mode="factored"),
        train=TrainConfig(epochs=ACOSE_EPOCHS, train_batch_size=ACOSE_BATCH_SIZE,
                          eval_batch_size=ACOSE_EVAL_BATCH_SIZE, learning_rate=ACOSE_LR,
                          warmup_proportion=0.1, seed=SEED),
    )
    cfg_acose.to_json(os.path.join(acose_root, "run_config.json"))
    _heads = head_size_report(cfg_acose)
    st.step(f"RunConfig siap → {os.path.join(acose_root, 'run_config.json')} | "
            f"kepala label factored {_heads['factored']['outputs']} output "
            f"(joint {_heads['joint']['outputs']}, tidak dipakai)")

    _prepare_json = os.path.join(cfg_acose.data.work_dir, cfg_acose.name, "_prepare.json")
    if os.path.exists(_prepare_json):
        with open(_prepare_json, "r", encoding="utf-8") as jf:
            artifacts_acose = DataArtifacts(**json.load(jf))
        st.step(f"[CACHE HIT] artefak data dimuat dari {_prepare_json}")
    else:
        artifacts_acose = prepare_data(cfg_acose)
        st.step("prepare_data selesai (retokenisasi + remap span + pair file)")

    for split in ("train", "dev", "test"):
        _r = artifacts_acose.reports.get(split, {})
        _rp = artifacts_acose.reports.get(f"{split}_pairs", {})
        st.step(f"{split}: {_r.get('rows', '?')} baris | unk_ratio "
                f"{_r.get('unk_ratio', 0.0) * 100:.2f}% | span_repair "
                f"{_r.get('span_repair_count', 0)} | pairs {_rp.get('pairs', '?')} "
                f"(multi-label {_rp.get('multi_label_pairs', '?')})")

    _lr = artifacts_acose.label_report or {}
    if _lr.get("joint_size"):
        st.note(f"Ruang label joint: {_lr['joint_cells_seen']}/{_lr['joint_size']} sel "
                f"terpakai ({_lr.get('joint_coverage', 0.0) * 100:.1f}%), "
                f"{_lr.get('joint_cells_below_10', 0)} sel berisi <10 contoh — "
                f"ini alasan kepala factored dipakai.")

    update_mcp_manifest("ACOSE_DATA_PREPARED", 7, {
        "acose_work_dir": artifacts_acose.work_dir,
        "acose_head_outputs": _heads["factored"]["outputs"],
    })
    st.step("Manifest → ACOSE_DATA_PREPARED")

    # Konstanta path checkpoint ACOSE didefinisikan di sini, bukan di 10c:
    # sel 10d dan 10e memakainya, dan 10c bisa dilewati saat cache hit
    # (pola yang sama dengan args_h yang wajib ada di 8a, bukan 8d).
    acose_extr_dir = os.path.join(acose_root, "extraction")
    acose_cls_dir = os.path.join(acose_root, "classification")
    acose_extr_log = os.path.join(acose_extr_dir, "train_log.json")
    acose_cls_log = os.path.join(acose_cls_dir, "train_log.json")
    acose_progress_json = os.path.join(acose_logs_dir, "acose_progress.json")'''

MD_10C = """### 10c. Training ACOSE: Ekstraksi Span + Klasifikasi Label
Dua tahap `absa5` di atas backbone yang sama dengan Step 1/2 (cache BERT),
dengan gerbang verifikasi bobot numerik dari `absa5.encoders` — encoder yang
gagal termuat tidak bisa lolos diam-diam.

Catatan: loop training `absa5.engine` tidak meng-emit progres per epoch secara
langsung, jadi sel ini mencetak riwayat per epoch **setelah** tahap selesai
(metrik dev per epoch tetap terekam di `train_log.json`). Cache per tahap:
bila `extraction/train_log.json` dan `classification/train_log.json` sudah ada,
sel dilewati kecuali `ACOSE_FORCE_RETRAIN=True`."""

CODE_10C = '''require_vars("step_stage", "cfg_acose", "artifacts_acose", "bert_cache_dir",
             "device", "acose_logs_dir", "acose_extr_log", "acose_cls_log")

if "absa5" not in sys.modules and "_ensure_absa5" in globals():
    _ensure_absa5(base_project_dir if "base_project_dir" in globals() else None)

from absa5.engine import train_classification, train_extraction
from absa5.features import build_encoders
from absa5.models import build_classification_model, build_extraction_model
from absa5.pipeline import load_prepared
from absa5.schema import get_schema

# Toggle: True = latih ulang kedua tahap ACOSE meski train_log.json sudah ada.
ACOSE_FORCE_RETRAIN = False

_acose_extr_done = os.path.exists(acose_extr_log)
_acose_cls_done = os.path.exists(acose_cls_log)
ACOSE_SKIP_TRAINING = (not ACOSE_FORCE_RETRAIN) and _acose_extr_done and _acose_cls_done

if ACOSE_SKIP_TRAINING:
    with step_stage("10c. Training ACOSE — cache hit", 2) as st:
        with open(acose_extr_log, "r", encoding="utf-8") as jf:
            _ext_log = json.load(jf)
        with open(acose_cls_log, "r", encoding="utf-8") as jf:
            _cls_log = json.load(jf)
        st.step(f"[CACHE HIT] ekstraksi: span F1 {_ext_log['best_metric']:.2%} "
                f"(epoch {_ext_log['best_epoch'] + 1}) → {acose_extr_dir}")
        st.step(f"[CACHE HIT] klasifikasi: label F1 {_cls_log['best_metric']:.2%} "
                f"(epoch {_cls_log['best_epoch'] + 1}) → {acose_cls_dir}")
    print("⏩ 10c dilewati — kedua checkpoint ACOSE sudah ada. "
          "Set ACOSE_FORCE_RETRAIN=True untuk melatih ulang.")
else:
    with step_stage("10c. Training ACOSE — persiapan model & data", 4) as st:
        tokenizer_acose = cfg_acose.tokenizer.build()
        st.step(f"Tokenizer wordpiece dimuat dari {cfg_acose.tokenizer.path}")

        schema_acose = get_schema(cfg_acose.data.schema)
        spaces_acose = cfg_acose.label_spaces()
        ext_encoder, cls_encoder = build_encoders(
            tokenizer_acose, schema_acose, spaces_acose,
            max_seq_length=cfg_acose.data.max_seq_length,
            tagging=cfg_acose.data.tagging,
        )
        st.step(f"Encoder fitur: {ext_encoder.num_tags} tag sekuens | ruang label "
                f"{spaces_acose.sizes()}")

        train_records_ac, _ = load_prepared(cfg_acose, artifacts_acose, "train")
        dev_records_ac, dev_pairs_ac = load_prepared(cfg_acose, artifacts_acose, "dev")
        st.step(f"Data: {len(train_records_ac)} train / {len(dev_records_ac)} dev record")

        model_ext_ac, info_ext = build_extraction_model(
            cfg_acose, ext_encoder, checkpoint_dir=bert_cache_dir, verify=True)
        _n_ext = sum(p.numel() for p in model_ext_ac.parameters())
        _wc = info_ext.get("weight_check", {})
        st.step(f"Model ekstraksi: {_n_ext / 1e6:.1f} M parameter | gerbang bobot: "
                f"{'LOLOS — ' + _wc['messages'][0] if _wc.get('passed') else 'GAGAL'}")

        model_cls_ac, info_cls = build_classification_model(
            cfg_acose, cls_encoder, checkpoint_dir=bert_cache_dir, verify=True)
        _wc2 = info_cls.get("weight_check", {})
        st.step(f"Model klasifikasi siap | gerbang bobot: "
                f"{'LOLOS' if _wc2.get('passed') else 'GAGAL'}")

    with step_stage(f"10c. Training ekstraksi span — {ACOSE_EPOCHS} epoch pada {device}",
                    cfg_acose.train.epochs) as st:
        outcome_ext_ac = train_extraction(
            model_ext_ac, cfg_acose,
            ext_encoder.encode_all(train_records_ac),
            ext_encoder.encode_all(dev_records_ac),
            ext_encoder, output_dir=acose_extr_dir, device=device)
        for _rec in outcome_ext_ac.history:
            st.step(f"epoch {_rec['epoch'] + 1:02d} | loss {_rec['train_loss']:.4f} "
                    f"| span F1 {_rec['dev_span_f1']:.2%} "
                    f"| implisit {_rec['dev_implicit']}")
        write_stage_progress(acose_progress_json, stage="ACOSE_EXTRACTION",
                             best_span_f1=outcome_ext_ac.best_metric,
                             best_epoch=outcome_ext_ac.best_epoch + 1,
                             epochs=cfg_acose.train.epochs)
        st.note(f"🔥 Span F1 terbaik {outcome_ext_ac.best_metric:.2%} "
                f"(epoch {outcome_ext_ac.best_epoch + 1}) → {acose_extr_dir}")
        update_mcp_manifest("ACOSE_EXTRACTION_TRAINED", 7, {
            "acose_best_span_f1": float(outcome_ext_ac.best_metric),
            "acose_best_span_epoch": outcome_ext_ac.best_epoch + 1,
        })

    with step_stage(f"10c. Training klasifikasi label — {ACOSE_EPOCHS} epoch pada {device}",
                    cfg_acose.train.epochs) as st:
        _, train_pairs_ac = load_prepared(cfg_acose, artifacts_acose, "train")
        outcome_cls_ac = train_classification(
            model_cls_ac, cfg_acose,
            cls_encoder.encode_all(train_pairs_ac),
            cls_encoder.encode_all(dev_pairs_ac),
            cls_encoder, spaces_acose, output_dir=acose_cls_dir, device=device)
        for _rec in outcome_cls_ac.history:
            _perf = _rec.get("dev_per_element_f1", {})
            _perf_txt = " ".join(f"{k} {v:.2%}" for k, v in sorted(_perf.items()))
            st.step(f"epoch {_rec['epoch'] + 1:02d} | loss {_rec['train_loss']:.4f} "
                    f"| label F1 {_rec['dev_label_f1']:.2%} | {_perf_txt}")
        write_stage_progress(acose_progress_json, stage="ACOSE_CLASSIFICATION",
                             best_label_f1=outcome_cls_ac.best_metric,
                             best_epoch=outcome_cls_ac.best_epoch + 1,
                             epochs=cfg_acose.train.epochs)
        st.note(f"🔥 Label F1 terbaik {outcome_cls_ac.best_metric:.2%} "
                f"(epoch {outcome_cls_ac.best_epoch + 1}) → {acose_cls_dir}")
        update_mcp_manifest("ACOSE_CLASSIFICATION_TRAINED", 7, {
            "acose_best_label_f1": float(outcome_cls_ac.best_metric),
            "acose_best_label_epoch": outcome_cls_ac.best_epoch + 1,
        })

    print(f"🏁 Training ACOSE selesai: span F1 {outcome_ext_ac.best_metric:.2%}, "
          f"label F1 {outcome_cls_ac.best_metric:.2%}.")'''

MD_10D = """### 10d. Evaluasi End-to-End Quintuple
Prediksi span dari checkpoint ekstraksi terbaik → cross-product kandidat →
prediksi label (termasuk emosi) → skor `absa5.metrics.evaluate` dengan semua
subset elemen (hingga 5 elemen) dan bucket implisitnya. Hasil di-cache ke
`<ACOSE>/<domain>/logs/acose_metrics.json`; set `FORCE_REEVAL_ACOSE = True`
untuk menghitung ulang."""

CODE_10D = '''require_vars("step_stage", "cfg_acose", "artifacts_acose", "bert_cache_dir",
             "device", "acose_logs_dir")

if "absa5" not in sys.modules and "_ensure_absa5" in globals():
    _ensure_absa5(base_project_dir if "base_project_dir" in globals() else None)

from absa5.data import cross_product_pairs
from absa5.engine import evaluate_end_to_end, predict_labels, predict_spans
from absa5.features import build_encoders
from absa5.models import build_classification_model, build_extraction_model
from absa5.pipeline import load_prepared
from absa5.schema import get_schema

# Toggle: True = evaluasi ulang meski acose_metrics.json sudah ada.
FORCE_REEVAL_ACOSE = False
acose_metrics_json = os.path.join(acose_logs_dir, "acose_metrics.json")


def _pairs_from_span_preds_ac(span_preds, span_elements):
    """Cross-product span prediksi menjadi kandidat pair (sama dengan pipeline.run)."""
    out = []
    for pred in span_preds:
        groups = [list(pred["spans"].get(n) or [(-1, -1)]) for n in span_elements]
        out.extend(cross_product_pairs(str(pred["text"]), groups))
    return out


with step_stage("10d. Evaluasi end-to-end quintuple ACOSE", 6) as st:
    if not FORCE_REEVAL_ACOSE and os.path.exists(acose_metrics_json):
        with open(acose_metrics_json, "r", encoding="utf-8") as jf:
            acose_eval_dict = json.load(jf)
        acose_table = acose_eval_dict.get("table", "")
        st.step(f"[CACHE HIT] {len(acose_eval_dict.get('by_subset', {}))} sub-task, "
                f"{len(acose_eval_dict.get('by_bucket', {}))} bucket dimuat dari "
                f"{acose_metrics_json}")
    else:
        if not (os.path.exists(acose_extr_log) and os.path.exists(acose_cls_log)):
            raise RuntimeError(
                "Checkpoint ACOSE belum ada. Jalankan sel 10c (training) lebih dulu.")

        tokenizer_acose = cfg_acose.tokenizer.build()
        schema_acose = get_schema(cfg_acose.data.schema)
        spaces_acose = cfg_acose.label_spaces()
        ext_encoder, cls_encoder = build_encoders(
            tokenizer_acose, schema_acose, spaces_acose,
            max_seq_length=cfg_acose.data.max_seq_length,
            tagging=cfg_acose.data.tagging,
        )
        # Checkpoint di direktori ini adalah bobot terbaik yang disimpan 10c,
        # jadi verifikasi ulang terhadap berkas yang sama hanya membuang waktu.
        model_ext_best, _ = build_extraction_model(
            cfg_acose, ext_encoder, checkpoint_dir=acose_extr_dir, verify=False)
        model_cls_best, _ = build_classification_model(
            cfg_acose, cls_encoder, checkpoint_dir=acose_cls_dir, verify=False)
        st.step("Checkpoint terbaik tahap 10c dimuat ke " + device)

        test_records_ac, _ = load_prepared(cfg_acose, artifacts_acose, "test")
        st.step(f"{len(test_records_ac)} baris test dimuat")

        span_preds_ac = predict_spans(
            model_ext_best, ext_encoder.encode_all(test_records_ac),
            ext_encoder, cfg_acose, device=device)
        candidates_ac = _pairs_from_span_preds_ac(span_preds_ac, schema_acose.spans)
        st.step(f"{len(candidates_ac):,} pasangan kandidat dari prediksi span")

        label_sets_ac = predict_labels(
            model_cls_best, cls_encoder.encode_all(candidates_ac),
            spaces_acose, cfg_acose, device=device)
        st.step("Label (kategori, sentimen, emosi) diprediksi untuk semua kandidat")

        evaluation_ac = evaluate_end_to_end(
            candidates_ac, label_sets_ac, test_records_ac, schema_acose,
            max_subset_size=5)
        acose_eval_dict = evaluation_ac.as_dict()
        acose_table = evaluation_ac.table()
        acose_eval_dict.update({
            "table": acose_table,
            "candidates": len(candidates_ac),
            "redundancy_verdict": acose_bootstrap_reports["train"]["redundancy_verdict"],
            "emotion_label_set": ACOSE_EMOTION_SET,
            "saved_at": datetime.now().isoformat(),
        })
        with open(acose_metrics_json, "w", encoding="utf-8") as jf:
            json.dump(acose_eval_dict, jf, indent=2, ensure_ascii=False)
        st.step(f"Quintuple micro-F1 {evaluation_ac.overall.f1 * 100:.2f}% "
                f"({len(acose_eval_dict['by_subset'])} sub-task) → {acose_metrics_json}")

    print("\\n🏆 Tabel evaluasi end-to-end ACOSE (quintuple):")
    print(acose_table)'''

MD_10E = """### 10e. Tabel, Plot & State ACOSE
Sel pelaporan murni (tanpa torch): tabel metrik per sub-task dan bucket
implisit ke `master_11`/`master_12`, plot distribusi emosi dan F1 sub-task,
lalu manifest dan `pipeline_state.pkl`. Semua berkas laporan ditulis ke folder
`ACOSE/<domain>/{csv,md,plots,logs}` di Drive, terpisah dari sesi ACOS. Aman diulang."""

CODE_10E = '''require_vars("step_stage", "acose_root", "acose_raw_dir", "emotion_labels",
             "acose_bootstrap_reports", "acose_metrics_json",
             "acose_logs_dir", "acose_csv_dir", "acose_md_dir", "acose_plots_dir")

with step_stage("10e. Tabel, plot & state ACOSE", 7) as st:
    if not os.path.exists(acose_metrics_json):
        raise RuntimeError(
            f"{acose_metrics_json} belum ada. Jalankan sel 10d (evaluasi) lebih dulu.")
    with open(acose_metrics_json, "r", encoding="utf-8") as jf:
        _m_ac = json.load(jf)

    # Bila kernel di-restart setelah 10a, laporan bootstrap dimuat ulang dari disk.
    if "train" not in acose_bootstrap_reports:
        acose_bootstrap_reports = {}
        for _s in ("train", "dev", "test"):
            _bp = os.path.join(acose_raw_dir, f"_bootstrap_{_s}.json")
            if os.path.exists(_bp):
                with open(_bp, "r", encoding="utf-8") as jf:
                    acose_bootstrap_reports[_s] = json.load(jf)

    rep.section("9. ACOSE: hasil evaluasi quintuple (emosi)")

    _ov = _m_ac.get("overall", {})
    rep.kv({
        "quintuple_micro_F1": f"{_ov.get('f1', 0.0) * 100:.2f}%",
        "precision": f"{_ov.get('precision', 0.0) * 100:.2f}%",
        "recall": f"{_ov.get('recall', 0.0) * 100:.2f}%",
        "kandidat_pasangan": _m_ac.get("candidates", "?"),
        "label_emosi": _m_ac.get("emotion_label_set", ACOSE_EMOTION_SET),
        "verdict_redundansi": _m_ac.get("redundancy_verdict", ""),
    })
    rep.text("Pengingat: kolom emosi berstatus suggested (leksikon, belum divalidasi "
             "manusia). Angka ini mengukur leksikon + model, bukan kualitas anotasi.")
    st.step("Ringkasan quintuple ditulis ke laporan")

    df_sub_ac = pd.DataFrame([
        {"Subtask": k, "N_Elemen": len(k.split("+")),
         "TP": round(v.get("tp", float("nan"))), "FP": round(v.get("fp", float("nan"))),
         "FN": round(v.get("fn", float("nan"))),
         "Precision_%": round(v.get("precision", 0.0) * 100, 2),
         "Recall_%": round(v.get("recall", 0.0) * 100, 2),
         "Micro_F1_%": round(v.get("f1", 0.0) * 100, 2),
         "Support": round(v.get("support", 0.0))}
        for k, v in _m_ac.get("by_subset", {}).items()
    ])
    if not df_sub_ac.empty:
        df_sub_ac = df_sub_ac.sort_values(["N_Elemen", "Subtask"]).reset_index(drop=True)
        export_step_table(df_sub_ac, name="master_11_acose_metrik_subset",
                          csv_dir=acose_csv_dir, md_dir=acose_md_dir,
                          title=f"Metrik Quintuple per Sub-Task ({DOMAIN.upper()})",
                          notes=("Proyeksi tuple ke subset elemen; subtask 5 elemen adalah "
                                 "quintuple penuh. Emosi dari leksikon (suggested)."),
                          max_rows_md=35)
        rep.table(df_sub_ac, max_rows=35, caption="Metrik quintuple per sub-task")
        st.step(f"Tabel master_11_acose_metrik_subset diekspor ({len(df_sub_ac)} sub-task)")

    df_bucket_ac = pd.DataFrame([
        {"Bucket": k,
         "Precision_%": round(v.get("precision", 0.0) * 100, 2),
         "Recall_%": round(v.get("recall", 0.0) * 100, 2),
         "Micro_F1_%": round(v.get("f1", 0.0) * 100, 2),
         "Support": round(v.get("support", 0.0))}
        for k, v in _m_ac.get("by_bucket", {}).items()
    ])
    if not df_bucket_ac.empty:
        export_step_table(df_bucket_ac, name="master_12_acose_bucket_implisit",
                          csv_dir=acose_csv_dir, md_dir=acose_md_dir,
                          title=f"Metrik Quintuple per Bucket Implisit ({DOMAIN.upper()})",
                          notes="Bucket pada tuple penuh 5 elemen (explicit vs implicit).")
        rep.table(df_bucket_ac, caption="Metrik quintuple per bucket implisit")
        st.step(f"Tabel master_12_acose_bucket_implisit diekspor ({len(df_bucket_ac)} bucket)")

    # Plot 1: distribusi emosi hasil bootstrap per split.
    _pl1 = os.path.join(acose_plots_dir, "06_acose_emotion_distribution.png")
    df_emosi_plot = pd.DataFrame([
        {"Split": s.capitalize(),
         **{lab: acose_bootstrap_reports[s]["distribution"].get(lab, 0)
            for lab in emotion_labels}}
        for s in ("train", "dev", "test") if s in acose_bootstrap_reports
    ])
    if not df_emosi_plot.empty:
        df_emosi_plot.set_index("Split").plot(
            kind="bar", figsize=(9, 5), width=0.75, edgecolor="black", alpha=0.88)
        plt.title(f"[{DOMAIN.upper()}] Distribusi Emosi Hasil Bootstrap (suggested)",
                  fontsize=12, fontweight="bold")
        plt.ylabel("Jumlah tuple")
        plt.xticks(rotation=0)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(_pl1, dpi=300)
        plt.show()
        plt.close()
        rep.image(_pl1, "Distribusi emosi hasil bootstrap per split")
        st.step(f"Plot distribusi emosi disimpan: {_pl1}")

    # Plot 2: micro-F1 per sub-task, dikelompokkan jumlah elemen.
    if not df_sub_ac.empty:
        _pl2 = os.path.join(acose_plots_dir, "07_acose_subset_f1.png")
        _df_top = df_sub_ac.sort_values("Micro_F1_%", ascending=False).head(15)
        plt.figure(figsize=(10, 6))
        _colors = plt.cm.viridis(_df_top["N_Elemen"] / max(df_sub_ac["N_Elemen"].max(), 1))
        _b = plt.barh(_df_top["Subtask"], _df_top["Micro_F1_%"], color=_colors,
                      edgecolor="black", alpha=0.88)
        for _bar, _v in zip(_b, _df_top["Micro_F1_%"]):
            plt.text(_v + 0.5, _bar.get_y() + _bar.get_height() / 2, f"{_v:.1f}%",
                     va="center", fontsize=8)
        plt.xlabel("Micro-F1 (%)")
        plt.title(f"[{DOMAIN.upper()}] ACOSE: Micro-F1 per Sub-Task (15 teratas)",
                  fontsize=12, fontweight="bold")
        plt.xlim(0, min(105, max(100, _df_top["Micro_F1_%"].max() + 10)))
        plt.gca().invert_yaxis()
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(_pl2, dpi=300)
        plt.show()
        plt.close()
        rep.image(_pl2, "Micro-F1 per sub-task quintuple")
        st.step(f"Plot F1 sub-task disimpan: {_pl2}")

    # Ringkasan run satu berkas: konfigurasi, data, riwayat training, metrik.
    acose_run_json = os.path.join(acose_logs_dir, "acose_run_result.json")
    _hist_ext, _hist_cls = [], []
    for _lg, _d in ((acose_extr_log, "extraction"), (acose_cls_log, "classification")):
        if os.path.exists(_lg):
            with open(_lg, "r", encoding="utf-8") as jf:
                _log = json.load(jf)
                if _d == "extraction":
                    _hist_ext = _log.get("history", [])
                else:
                    _hist_cls = _log.get("history", [])
    with open(acose_run_json, "w", encoding="utf-8") as jf:
        json.dump({
            "schema": "quint",
            "domain": DOMAIN,
            "emotion_label_set": ACOSE_EMOTION_SET,
            "emosi_status": "suggested (leksikon, belum divalidasi manusia)",
            "redundancy": {s: {
                "conditional_entropy_bits": acose_bootstrap_reports[s]["conditional_entropy_bits"],
                "verdict": acose_bootstrap_reports[s]["redundancy_verdict"],
            } for s in acose_bootstrap_reports},
            "label_mode": cfg_acose.heads.label_mode,
            "epochs": cfg_acose.train.epochs,
            "extraction_history": _hist_ext,
            "classification_history": _hist_cls,
            "overall": _m_ac.get("overall", {}),
            "candidates": _m_ac.get("candidates"),
            "metrics_json": acose_metrics_json,
            "run_config": os.path.join(acose_root, "run_config.json"),
            "saved_at": datetime.now().isoformat(),
        }, jf, indent=2, ensure_ascii=False)
    st.step(f"Ringkasan run ACOSE → {acose_run_json}")

    update_mcp_manifest("ACOSE_COMPLETED", 7, {
        "acose_quint_micro_f1": float(_ov.get("f1", 0.0) * 100),
        "acose_candidates": _m_ac.get("candidates", 0),
        "acose_metrics_json": acose_metrics_json,
    })
    save_pipeline_state({
        "acose_quint_micro_f1": _ov.get("f1", 0.0),
        "acose_best_span_f1": (globals().get("outcome_ext_ac").best_metric
                               if globals().get("outcome_ext_ac") else None),
        "acose_best_label_f1": (globals().get("outcome_cls_ac").best_metric
                                if globals().get("outcome_cls_ac") else None),
    })
    st.step("Manifest → ACOSE_COMPLETED, pipeline_state.pkl diperbarui")'''


def find_md(cells, prefix, start=0):
    for i in range(start, len(cells)):
        c = cells[i]
        if c["cell_type"] != "markdown":
            continue
        src = "".join(c["source"]).strip()
        if src.startswith(prefix):
            return i
    raise LookupError(f"Sel markdown dengan awal '{prefix}' tidak ditemukan")


def _fix_shell_magic_in_blocks(src):
    """Ganti baris shell magic ( !cmd ) yang berindentasi di dalam blok if/for
    dengan os.system(cmd).

    Colab/IPython menolak line-magic di dalam blok indentasi (SyntaxError saat
    sel dikompilasi), jadi sel infrastruktur seperti clone repo harus memakai
    pemanggilan Python. Dipilih os.system karena `os` pasti sudah diimpor di
    sel-sel tersebut; baris magic di top-level (tanpa indentasi) dibiarkan.
    """
    out = []
    for ln in src.splitlines(keepends=True):
        stripped = ln.strip()
        if stripped.startswith("!") and ln[:1].isspace():
            cmd = stripped[1:].strip()
            indent = ln[: len(ln) - len(ln.lstrip())]
            # Jika command memuat ekspresi f-string ({var}), pertahankan
            # interpolasinya dengan menjadikannya f-string. Kalau tidak ada
            # kurung kurawal, apa adanya.
            cmd_repr = repr(cmd)
            if "{" in cmd and "}" in cmd:
                cmd_repr = "f" + repr(cmd)
            out.append(f"{indent}os.system({cmd_repr})\n")
        else:
            out.append(ln)
    return "".join(out)


def patch_shell_magic_cells(cells):
    """Timpa sel kode apa pun (warisan V2) yang memakai shell magic berindentasi
    dengan versi subprocess — mencegah SyntaxError saat sel dikompilasi di Colab.
    """
    n = 0
    for c in cells:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        if any(ln.lstrip().startswith("!") and ln[:1].isspace()
               for ln in src.splitlines()):
            c["source"] = _fix_shell_magic_in_blocks(src)
            n += 1
    return n


def main():
    # 1. V2 STAGED dibangun ulang dulu agar V3 selalu berdiri di atas V2 mutakhir.
    V2.main()

    nb = json.load(io.open(SRC_V2, encoding="utf-8"))
    cells = nb["cells"]

    # 1b. Perbaikan warisan V2: shell-magic berindentasi di dalam blok if/for
    #     akan membuat sel gagal dikompilasi di Colab (SyntaxError). Ganti ke
    #     os.system supaya sel infrastruktur (clone/sync) tetap valid. V2 tidak
    #     disentuh; hanya salinan V3 yang dipatch.
    n_fix = patch_shell_magic_cells(cells)
    if n_fix:
        print(f"  [patch] {n_fix} sel V2 dengan shell-magic berindentasi dikonversi ke os.system")

    # 2. Judul: tambahkan penjelasan versi V3.
    head = "".join(cells[0]["source"]).rstrip("\n")
    cells[0] = md(head + "\n" + MD_TITLE_ACOSE)

    # 3. Penomoran ulang seksi lama (urutan penting: 11→12 dulu, baru 10→11).
    i_sum = find_md(cells, "## 11.")
    cells[i_sum] = md("".join(cells[i_sum]["source"]).replace("## 11.", "## 12."))
    i_live = find_md(cells, "## 10.")
    cells[i_live] = md("".join(cells[i_live]["source"]).replace("## 10.", "## 11."))

    # 4. Sisipkan seksi ACOSE sebelum demo inferensi (kini "## 11.").
    i_live = find_md(cells, "## 11.")
    cells[i_live:i_live] = [
        md(MD_10A), code(CODE_10A),
        md(MD_10B), code(CODE_10B),
        md(MD_10C), code(CODE_10C),
        md(MD_10D), code(CODE_10D),
        md(MD_10E), code(CODE_10E),
    ]

    with io.open(DST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")

    n_code = sum(1 for c in cells if c["cell_type"] == "code")
    digest = hashlib.md5(open(DST, "rb").read()).hexdigest()
    print(f"{os.path.basename(DST)} ditulis: {len(cells)} sel ({n_code} kode). MD5 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
