"""Membangun 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb dari V2 STAGED.

V4 = V2 dengan backbone **IndoBERT fine-tuned** dan dataset **Apps-ACOS
(bahasa Indonesia)**, memakai pola penyimpanan, penamaan sesi, caching, dan
tabel/plot yang sama seperti V2 sehingga hasilnya bisa diletakkan berdampingan
dengan baseline BERT Inggris.

Generator ini berlapis di atas V2 (seperti `_build_v3_acose.py`): ia menjalankan
`_build_staged_v2.main()` lebih dulu, memuat hasilnya, lalu menyisipkan/menimpa
sel yang perlu berubah. Konsekuensinya perbaikan pada generator V2 otomatis ikut
ke V4 pada build berikutnya.

Yang berubah dibanding V2:

  sel 0     judul + tabel versi V4
  sel 2     dependensi: tambah paket unduh checkpoint HF
  sel 3S    (baru, setelah impor) sinkronisasi paket `acos_id/` + sys.path
  sel 11    DOMAIN='appsid', BACKBONE, hyperparameter Indonesia
  sel 14    bert_cache_dir → backbone IndoBERT hasil rekey (bukan bert_base_uncased)
  sel 4c    (baru) gerbang data Indonesia: taksonomi, split, konversi ACOS,
            generator tokenized_data, gate 2 Inggris
  sel 4d    (baru) adapter checkpoint IndoBERT + laporan vocab
  sel 20-21 EDA memakai `acos_id.eda.analyze_and_plot_eda_id` untuk domain ID
  sel 28    patch `get_labels` domain Indonesia sebelum label dibaca
  sel 34    (baru sesudahnya) Gate 1 numerik: bobot encoder benar-benar termuat

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

SRC_V2 = V2.DST
DST = os.path.join(HERE, "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb")

md = V2.md
code = V2.code


def find_md(cells, prefix, start=0):
    for i in range(start, len(cells)):
        c = cells[i]
        if c["cell_type"] != "markdown":
            continue
        if "".join(c["source"]).strip().startswith(prefix):
            return i
    raise LookupError(f"Sel markdown dengan awal '{prefix}' tidak ditemukan")


def find_code(cells, *needles, start=0):
    for i in range(start, len(cells)):
        c = cells[i]
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        if all(n in src for n in needles):
            return i
    raise LookupError(f"Sel kode dengan penanda {needles} tidak ditemukan")


def _fix_shell_magic_in_blocks(src):
    """Ganti shell magic berindentasi (`    !cmd`) dengan `os.system(...)`.

    IPython menolak line-magic di dalam blok indentasi saat sel dikompilasi, dan
    V2 masih memuat satu sel seperti itu (auto-clone repo). Sama seperti patch di
    `_build_v3_acose.py`; magic di top-level dibiarkan.
    """
    out = []
    for ln in src.splitlines(keepends=True):
        stripped = ln.strip()
        if stripped.startswith("!") and ln[:1].isspace():
            cmd = stripped[1:].strip()
            indent = ln[: len(ln) - len(ln.lstrip())]
            cmd_repr = repr(cmd)
            if "{" in cmd and "}" in cmd:
                cmd_repr = "f" + repr(cmd)
            out.append(f"{indent}os.system({cmd_repr})\n")
        else:
            out.append(ln)
    return "".join(out)


def patch_shell_magic_cells(cells):
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


MD_TITLE_V4 = """
---

### Versi V4 — IndoBERT fine-tuned + dataset Indonesia (Apps-ACOS)

Turunan dari `00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb`, dibangun ulang oleh
`_build_v4_indobert.py` (yang menjalankan generator V2 lebih dulu). Seluruh pola
V2 dipertahankan — sel bertahap `step_stage`, cache per tahap, folder sesi
bertimestamp, tabel `master_*`, dan plot 300 DPI — hanya **backbone** dan
**dataset**-nya yang berganti.

| Aspek | V2 (baseline) | V4 (ini) |
|---|---|---|
| Backbone | `bert-base-uncased` | `indobenchmark/indobert-base-p1`, **fine-tuned di sini** |
| Domain | `rest16` / `laptop` | `appsid` (ulasan aplikasi bank digital) |
| Kategori | 13 (`ENTITAS#ATRIBUT`) | 13 (nama datar, mis. `AUTH_ACCESS`) |
| `num_labels` Step 2 | 39 | **39** (sengaja sama, head tak berubah dimensi) |
| Sumber data | `data/Restaurant-ACOS/` | `data/Apps-ACOS/processed/` → dikonversi di sel 4c |
| Folder sesi | `results/rest16_<ts>/` | `results/appsid_<ts>/` |

Sel baru dibanding V2:

| Sel | Isi | Torch? |
|---|---|---|
| 1s | Sinkronisasi paket `acos_id/` + `sys.path` | tidak |
| 4c | Gerbang data: taksonomi, split, konversi ACOS, generator `tokenized_data`, gate 2 Inggris | tidak |
| 4d | Adapter checkpoint IndoBERT (rekey prefiks `bert.`) + laporan vocab | ya |
| 5d2 | **Gate 1**: bobot encoder dibandingkan numerik dengan checkpoint | ya |

**Dua kegagalan senyap yang dijaga sel-sel itu.** Pertama, checkpoint IndoBERT
menyimpan key tanpa prefiks `bert.`, sementara loader legacy
(`modeling.py:745`) menetapkan `start_prefix=''` karena `BertForQuadABSA` punya
atribut `self.bert`; tanpa rekey seluruh bobot encoder masuk `missing_keys` dan
logging yang melaporkannya di-comment out (`modeling.py:749-755`) — training
berjalan mulus dengan encoder **acak**. Kedua, `get_labels()` upstream hanya
mengenal `rest*` dan `laptop`; domain lain membuat daftar kategori `None`.
Keduanya diperiksa gate, bukan diasumsikan.

Jalankan sel 1s satu kali setelah setiap restart kernel, sama seperti 1b."""

MD_1S = """### 1s. Paket `acos_id/` (lapisan Indonesia)

Seluruh perbedaan Indonesia ada di paket `acos_id/` di root repo, **bukan** patch
pada `Extract-Classify-ACOS/`. Jalur Inggris karena itu tetap utuh dan bisa
dipakai sebagai kontrol: cukup ganti `DOMAIN` kembali ke `rest16` di sel 3.

Sel ini memastikan paket itu ada dan bisa diimpor. Diperiksa per-modul, bukan
sekadar `import acos_id`, karena folder yang tersinkron separuh akan lolos
pemeriksaan paket tetapi gagal beberapa sel kemudian."""

CODE_1S = '''# Paket lapisan Indonesia: acos_id/
ACOS_ID_MODULES = ("taxonomy", "build_acos", "tokenize_data", "checkpoint",
                   "selftest", "eda")

import importlib

_acos_id_dir = os.path.join(base_project_dir, "acos_id") if 'base_project_dir' in globals() \\
    else os.path.join(os.path.abspath("."), "acos_id")

if not os.path.isdir(_acos_id_dir):
    print(f"📥 Paket acos_id belum ada di {_acos_id_dir}. Menyinkronkan dari GitHub...")
    _tmp = "/tmp/ACOS_acosid_clone"
    os.system(f"rm -rf {_tmp}")
    os.system(f"git clone --depth 1 https://github.com/haisyamalawwab/ACOS.git {_tmp}")
    if os.path.isdir(os.path.join(_tmp, "acos_id")):
        os.makedirs(_acos_id_dir, exist_ok=True)
        os.system(f'cp -r {_tmp}/acos_id/. "{_acos_id_dir}/"')
        os.system(f"rm -rf {_tmp}")
        print("✅ acos_id tersinkron.")
    else:
        raise RuntimeError(
            "acos_id tidak ada di repo hasil clone. Unggah folder acos_id/ ke "
            f"{base_project_dir} secara manual.")

_parent = os.path.dirname(_acos_id_dir)
while _parent in sys.path:
    sys.path.remove(_parent)
sys.path.insert(0, _parent)

# Impor per-modul: folder yang tersinkron separuh lolos "import acos_id" tetapi
# gagal di sel 4c/4d, jauh dari penyebabnya.
_missing = []
for _m in ACOS_ID_MODULES:
    _fp = os.path.join(_acos_id_dir, f"{_m}.py")
    if not os.path.isfile(_fp) or os.path.getsize(_fp) == 0:
        _missing.append(f"{_m}.py")
if _missing:
    raise RuntimeError(f"acos_id tidak lengkap di {_acos_id_dir}; hilang: {_missing}")

for _m in list(sys.modules):
    if _m == "acos_id" or _m.startswith("acos_id."):
        del sys.modules[_m]

acos_id = importlib.import_module("acos_id")
acos_taxonomy = importlib.import_module("acos_id.taxonomy")
acos_selftest = importlib.import_module("acos_id.selftest")
acos_ckpt = importlib.import_module("acos_id.checkpoint")
acos_eda = importlib.import_module("acos_id.eda")

print(f"🇮🇩 acos_id v{acos_id.__version__} aktif : {_acos_id_dir}")
print(f"   Domain Indonesia        : {acos_taxonomy.DOMAIN}")
print(f"   Kategori                : {len(acos_taxonomy.CATEGORIES)} "
      f"→ num_labels Step 2 = {acos_taxonomy.num_labels_step2()}")
print(f"   Label sekuens Step 1    : {list(acos_taxonomy.SEQ_LABELS)}")
print(f"   Gerbang torch-free      : {', '.join(acos_selftest.TORCH_FREE_GATES)}")'''

MD_4C = """### 4c. Gerbang Data Indonesia (wajib sebelum training)

Lima gerbang, semuanya torch-free, dijalankan berurutan. Kalau ada yang merah sel
ini melempar exception alih-alih melanjutkan — setiap kegagalan di sini tidak
terlihat dari kurva loss maupun metrik training.

| Gate | Yang diperiksa | Kalau gagal |
|---|---|---|
| `taxonomy` | 13 kategori di kode == `label_maps.json`, **urutan sama** | indeks head Step 2 bergeser, seluruh prediksi kategori salah |
| `dataset` | berkas sumber ada; `review_id` train/dev/test saling lepas | kebocoran data, angka test terlalu tinggi |
| `acos_build` | `appsid_quad_*.tsv` terbentuk; tiap span menunjuk token nyata | span rusak jadi label `O`, aspek hilang tanpa pesan |
| `tokenized` | retokenisasi WordPiece tidak menghilangkan satu tuple pun | data training menyusut senyap |
| `gate2_english` | regenerasi data Inggris **identik** dengan `tokenized_data/` di repo | konvensi offset generator salah; ini satu-satunya bukti eksternalnya |

`gate2_english` memberi toleransi satu kalimat pada `rest16_train_pair.tsv`.
Itu cacat data upstream: `rest16_quad_train.tsv` baris 451 memuat span opini
lebar-nol `3,3`, dan berkas repo memetakan baris itu tidak konsisten antara
`*_quad_bert.tsv` (`3,4`) dan `*_pair.tsv` (`3,5`, plus satu pasangan hilang).
Generator mengikuti berkas quad, yang dipakai Step 1."""

CODE_4C = '''require_vars("step_stage", "acos_selftest", "acos_taxonomy", "DOMAIN")

# Set True untuk membangun ulang berkas ACOS & tokenized_data dari nol.
FORCE_REBUILD_ID_DATA = False

with step_stage("4c. Gerbang data Indonesia (5 gate torch-free)", 6) as st:
    if not acos_taxonomy.is_id_domain(DOMAIN):
        st.step(f"DOMAIN='{DOMAIN}' bukan domain Indonesia — seluruh gate dilewati")
        st.note("Notebook berjalan sebagai kontrol Inggris; sel 4d & 5d2 juga akan "
                "melewati dirinya sendiri.")
        id_gate_results = {}
    else:
        _paths = acos_selftest.default_paths(base_project_dir)
        _paths["bert_cache_dir"] = bert_cache_dir
        _paths["tokenized_dir"] = os.path.join(extract_dir, "tokenized_data")
        _paths["en_vocab_dir"] = os.path.join(active_save_dir, "bert_base_uncased")
        _paths["work_dir"] = os.path.join(session_dirs["logs"], "gates")
        st.step(f"Sumber data : {_paths['data_root']}")
        st.step(f"Vocab IndoBERT: {_paths['bert_cache_dir']}")

        # Gate 2 membandingkan dengan berkas Inggris di repo, jadi butuh vocab
        # bert-base-uncased. Diunduh di sini kalau belum ada; ukurannya 232 KB
        # (hanya vocab.txt, bukan pytorch_model.bin).
        if not os.path.exists(os.path.join(_paths["en_vocab_dir"], "vocab.txt")):
            os.makedirs(_paths["en_vocab_dir"], exist_ok=True)
            import urllib.request
            urllib.request.urlretrieve(
                "https://huggingface.co/bert-base-uncased/resolve/main/vocab.txt",
                os.path.join(_paths["en_vocab_dir"], "vocab.txt"))
            st.note("vocab.txt bert-base-uncased diunduh untuk gate 2")

        id_gate_results = acos_selftest.run_gates(
            paths=_paths, only=acos_selftest.TORCH_FREE_GATES,
            rebuild=FORCE_REBUILD_ID_DATA, raise_on_fail=True, verbose=True)
        st.step(f"{len(id_gate_results)} gate dijalankan, semuanya hijau")

        _b = id_gate_results["acos_build"]["detail"]["per_split"]
        _t = id_gate_results["tokenized"]["detail"]["per_split"]
        df_id_gates = pd.DataFrame([
            {"Split": s,
             "Baris_ACOS": _b[s].get("baris", 0),
             "Quad_ACOS": _b[s].get("quad", 0),
             "Quad_Tokenized": _t[s].get("quad", 0),
             "Quad_Hilang": _t[s].get("quad_hilang", 0),
             "Aspek_Eksplisit": _t[s].get("aspek_eksplisit", 0),
             "Aspek_Implisit": _t[s].get("aspek_implisit", 0),
             "Opini_Eksplisit": _t[s].get("opini_eksplisit", 0),
             "Opini_Implisit": _t[s].get("opini_implisit", 0)}
            for s in ("train", "dev", "test") if s in _b and s in _t])
        export_step_table(df_id_gates, name="master_00_gerbang_data_id",
                          csv_dir=csv_dir, md_dir=md_dir,
                          title="Gerbang Data Indonesia (Apps-ACOS)")
        rep.section("1b. Gerbang data Indonesia")
        rep.table(df_id_gates, caption="Konversi & retokenisasi per split")
        st.step("Tabel master_00 ditulis")

        _gate_json = os.path.join(session_dirs["logs"], "id_gates.json")
        with open(_gate_json, "w", encoding="utf-8") as jf:
            json.dump({k: {"ok": v["ok"], "detail": v["detail"]}
                       for k, v in id_gate_results.items()},
                      jf, indent=2, ensure_ascii=False, default=str)
        st.step(f"Hasil gate → {_gate_json}")
        update_mcp_manifest("ID_DATA_GATES_PASSED", 1,
                            {"n_gate": len(id_gate_results),
                             "num_labels_step2": acos_taxonomy.num_labels_step2()})'''

MD_4D = """### 4d. Adapter Checkpoint IndoBERT

Menyiapkan `bert_cache_dir` berisi `config.json`, `pytorch_model.bin`, dan
`vocab.txt` IndoBERT, dengan state_dict yang sudah **direkey**: setiap key
diberi prefiks `bert.` agar cocok dengan `start_prefix=''` yang dipakai loader
legacy pada kelas yang punya atribut `self.bert`.

Idempoten lewat penanda `_rekey.json` di folder yang sama. Penanda itu bukan
kenyamanan: menjalankan rekey dua kali menghasilkan `bert.bert.embeddings...`,
dan hasilnya sama buruknya dengan tidak merekey sama sekali.

Laporan vocab akan menunjukkan `config.vocab_size = 50000` sementara `vocab.txt`
berisi 30.521 token. Itu memang begitu untuk `indobert-base-p1` — matriks
embedding-nya benar-benar 50.000 baris dan id 30.521+ tidak pernah terpakai.
Jangan pernah memakai `config.vocab_size` sebagai jumlah token."""

CODE_4D = '''require_vars("step_stage", "acos_ckpt", "bert_cache_dir", "BACKBONE")

with step_stage("4d. Adapter checkpoint IndoBERT (rekey prefiks bert.)", 5) as st:
    if not acos_taxonomy.is_id_domain(DOMAIN):
        st.step(f"DOMAIN='{DOMAIN}' — memakai bert-base-uncased apa adanya, "
                f"adapter dilewati")
        backbone_report = {"dilewati": True}
    else:
        st.step(f"Backbone: {BACKBONE} → {acos_ckpt.BACKBONES[BACKBONE]['hf_id']}")
        st.step(f"Target   : {bert_cache_dir}")
        backbone_report = acos_ckpt.prepare_backbone(BACKBONE, bert_cache_dir)

        _rk = backbone_report["rekey"]
        if _rk.get("dilewati"):
            st.step(f"Rekey dilewati — {_rk['dilewati']}")
        else:
            st.step(f"Rekey: {_rk['n_diberi_prefiks']} dari {_rk['n_key']} key "
                    f"diberi prefiks 'bert.'")
        st.note(f"key sebelum: {_rk.get('key_sebelum')}")
        st.note(f"key sesudah: {_rk.get('key_sesudah')}")

        _v = backbone_report["vocab"]
        st.step(f"config.vocab_size={_v.get('config_vocab_size')} | "
                f"vocab.txt={_v.get('vocab_lines')} token | "
                f"hidden={_v.get('hidden_size')} × {_v.get('num_hidden_layers')} layer")
        if not _v.get("konsisten", True):
            st.note(f"⚠️ selisih {_v.get('selisih')} — normal untuk indobert-base-p1; "
                    f"rujuk vocab.txt, JANGAN config.vocab_size")

        df_backbone = pd.DataFrame([{
            "Backbone": BACKBONE,
            "HF_ID": acos_ckpt.BACKBONES[BACKBONE]["hf_id"],
            "Key_Total": _rk.get("n_key"),
            "Key_Diberi_Prefiks": _rk.get("n_diberi_prefiks"),
            "Key_Berprefiks_bert": _rk.get("n_key_berprefiks_bert"),
            "Config_Vocab_Size": _v.get("config_vocab_size"),
            "Vocab_Txt_Token": _v.get("vocab_lines"),
            "Hidden_Size": _v.get("hidden_size"),
            "Layer": _v.get("num_hidden_layers"),
        }])
        export_step_table(df_backbone, name="master_00b_backbone_indobert",
                          csv_dir=csv_dir, md_dir=md_dir,
                          title="Adapter Checkpoint IndoBERT")
        rep.table(df_backbone, caption="Backbone & hasil rekey")

        with open(os.path.join(session_dirs["logs"], "backbone_report.json"),
                  "w", encoding="utf-8") as jf:
            json.dump(backbone_report, jf, indent=2, ensure_ascii=False, default=str)
        st.step("backbone_report.json tersimpan; Gate 1 numerik menyusul di sel 5d2")'''

MD_5D2 = """### 5d2. Gate 1 — Bobot Encoder Benar-Benar Termuat

Gate paling penting di seluruh notebook. Sel ini membandingkan tiga tensor
encoder di model yang **sudah dimuat** dengan tensor yang sama di checkpoint di
disk, memakai `torch.equal`, bukan sekadar memeriksa nama key.

Tensor yang diperiksa: embedding kata, `layer.0` query, dan `layer.11` output —
layer pertama dan terakhir supaya kegagalan sebagian juga tertangkap.

Kalau gate ini merah, semua yang di bawahnya percuma: encoder terinisialisasi
acak dan angka F1 yang keluar mengukur kemampuan head belajar dari
representasi acak. Karena logging `missing_keys` upstream di-comment out, tidak
ada gejala lain yang muncul."""

CODE_5D2 = '''require_vars("step_stage", "acos_ckpt", "bert_cache_dir")

with step_stage("5d2. Gate 1: bobot IndoBERT benar-benar termuat", 4) as st:
    if STEP1_SKIP_TRAINING:
        st.step("Step 1 memakai cache — model belum dimuat, gate dilewati")
        st.note("Gate 1 hanya bermakna pada model yang baru di-from_pretrained. "
                "Set FORCE_RETRAIN_STEP1=True bila ingin memverifikasi ulang.")
        gate1_report = {"dilewati": True}
    elif not acos_taxonomy.is_id_domain(DOMAIN):
        st.step(f"DOMAIN='{DOMAIN}' — checkpoint Inggris sudah berprefiks bert., "
                f"gate tetap dijalankan sebagai kontrol")
        gate1_report = acos_ckpt.gate_weights_loaded(model_step1, bert_cache_dir)
    else:
        require_vars("model_step1")
        gate1_report = acos_ckpt.gate_weights_loaded(model_step1, bert_cache_dir)

    if not gate1_report.get("dilewati"):
        for _name, _r in gate1_report["tensor"].items():
            _short = _name.replace("bert.encoder.layer.", "layer").replace(
                "bert.embeddings.", "emb.")
            if _r["status"] == "LULUS":
                st.step(f"✅ {_short} — identik (mean {_r['mean_model']:+.6f})")
            else:
                st.step(f"❌ {_short} — {_r.get('alasan', 'tidak cocok')}")
        st.step(f"Key bert.* di model={gate1_report['n_key_bert_model']}, "
                f"di checkpoint={gate1_report['n_key_bert_checkpoint']}, "
                f"tanpa padanan={gate1_report['n_key_model_tanpa_padanan']}")

        df_gate1 = pd.DataFrame([
            {"Tensor": k.replace("bert.", ""), "Status": v["status"],
             "Bentuk": str(v.get("bentuk", "")),
             "Mean_Checkpoint": v.get("mean_checkpoint"),
             "Mean_Model": v.get("mean_model")}
            for k, v in gate1_report["tensor"].items()])
        export_step_table(df_gate1, name="master_00c_gate1_bobot_encoder",
                          csv_dir=csv_dir, md_dir=md_dir,
                          title="Gate 1 — Verifikasi Bobot Encoder")
        rep.table(df_gate1, caption="Gate 1: bobot encoder vs checkpoint")

        with open(os.path.join(session_dirs["logs"], "gate1_weights.json"),
                  "w", encoding="utf-8") as jf:
            json.dump(gate1_report, jf, indent=2, ensure_ascii=False, default=str)

        if not gate1_report["ok"]:
            raise RuntimeError(
                "GATE 1 GAGAL: bobot encoder di model tidak sama dengan checkpoint. "
                "Encoder kemungkinan terinisialisasi acak (modeling.py:745 memakai "
                "start_prefix='' karena kelas punya self.bert, sehingga key tanpa "
                "prefiks 'bert.' tidak pernah termuat). Jalankan ulang sel 4d dengan "
                "acos_ckpt.prepare_backbone(BACKBONE, bert_cache_dir, force_rekey=True).")
        st.step("Gate 1 LULUS — fine-tuning berjalan di atas bobot IndoBERT terlatih")'''


def apply_patches(cells):
    """Terapkan seluruh perubahan V4 pada daftar sel V2 (in-place)."""
    # PLACEHOLDER_PATCHES
    return cells


CODE_CONFIG = '''# ============================================================
#  Konfigurasi V4 — IndoBERT fine-tuned + dataset Indonesia
# ============================================================
# Pilihan Domain Dataset:
#   'appsid'  → data/Apps-ACOS   (Indonesia, 13 kategori, backbone IndoBERT)
#   'rest16'  → data/Restaurant-ACOS (Inggris, kontrol; backbone jadi bert-en)
#   'laptop'  → data/Laptop-ACOS     (Inggris, 121 kategori)
DOMAIN = "appsid"

# Backbone. Untuk domain Indonesia dipakai apa adanya; untuk domain Inggris
# dipaksa ke 'bert-en' di bawah, supaya kontrol tetap benar-benar kontrol.
#   'indobert'       → indobenchmark/indobert-base-p1  (target utama)
#   'indobert-large' → indobenchmark/indobert-large-p1 (VRAM T4 mepet)
#   'bert-en'        → bert-base-uncased               (kontrol Inggris)
BACKBONE = "indobert"

# Hyperparameter Pelatihan
MAX_SEQ_LENGTH = 128
STEP1_BATCH_SIZE = 24
STEP2_BATCH_SIZE = 16
STEP1_LR = 2e-5
STEP2_LR = 5e-5
NUM_EPOCHS = 15      # 15 epoch optimal untuk Colab GPU T4/A100 (Default paper: 30)
SEED = 42

# do_lower_case WAJIB True untuk indobert-base-p1: tokenizer_config.json-nya
# kosong ({}), jadi tidak ada default yang bisa dipercaya, dan tanpa lowercasing
# token berhuruf kapital berubah menjadi [UNK] dalam jumlah besar.
DO_LOWER_CASE = True

_IS_ID_DOMAIN = str(DOMAIN).lower().startswith("apps")
if not _IS_ID_DOMAIN and BACKBONE != "bert-en":
    print(f"ℹ️ DOMAIN='{DOMAIN}' berbahasa Inggris → BACKBONE dipaksa 'bert-en' "
          f"(semula '{BACKBONE}'). Vocab IndoBERT pada data Inggris menghasilkan "
          f"[UNK] masif dan angkanya tidak bisa dibandingkan.")
    BACKBONE = "bert-en"

# Reproducibility seeding
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

active_save_dir = save_dir if 'save_dir' in locals() else base_project_dir

# Sesi dilanjutkan bila ada artefak tersimpan; set False untuk memaksa sesi baru.
RESUME_LAST_SESSION = True

# 1. Inisialisasi direktori sesi (lanjutkan sesi lama atau buat timestamp baru)
results_base = os.path.join(active_save_dir, "results")

print(f"🇮🇩 Domain   : {DOMAIN} ({'Indonesia' if _IS_ID_DOMAIN else 'Inggris (kontrol)'})")
print(f"🧠 Backbone : {BACKBONE}")
print(f"📁 Sesi akan bernama: results/{DOMAIN}_<timestamp>/")'''

CODE_SESSION_TAIL = '''
# 2. Backbone cache. Nama folder mengikuti backbone, bukan selalu
#    "bert_base_uncased": satu folder per backbone supaya checkpoint IndoBERT
#    hasil rekey tidak pernah menimpa (atau tertimpa) checkpoint Inggris. Isinya
#    diunduh & direkey di sel 4d — di sini hanya path-nya yang ditetapkan.
BACKBONE_DIRNAME = {
    "indobert": "indobert_base_p1",
    "indobert-large": "indobert_large_p1",
    "bert-en": "bert_base_uncased",
}
bert_cache_dir = os.path.join(active_save_dir,
                              BACKBONE_DIRNAME.get(BACKBONE, BACKBONE.replace("-", "_")))
os.makedirs(bert_cache_dir, exist_ok=True)

if BACKBONE == "bert-en":
    # Jalur kontrol: fungsi V2 apa adanya, tanpa rekey.
    download_bert_pretrained(target_dir=bert_cache_dir)
else:
    _n_ada = sum(1 for _f in ("config.json", "pytorch_model.bin", "vocab.txt")
                 if os.path.exists(os.path.join(bert_cache_dir, _f)))
    print(f"🧠 Backbone dir : {bert_cache_dir} ({_n_ada}/3 berkas ada)")
    print("   Unduh & rekey dilakukan di sel 4d (jangan pakai download_bert_pretrained "
          "untuk IndoBERT — fungsi itu mengunduh bert-base-uncased).")

print(f"\\n📁 Active Session Folder: {session_dirs['root']}")
plots_dir = session_dirs["plots"]
csv_dir = session_dirs["csv"]
md_dir = session_dirs["md"]
logs_dir = session_dirs["logs"]'''

CODE_EDA = '''
if 'df_stats' in globals() and df_stats is not None and not df_stats.empty and 'df_records' in globals() and df_records is not None:
    print("⏩ [CACHE HIT] Menggunakan objek df_stats & df_records dari memori runtime.")
elif (os.path.exists(eda_stats_csv) and os.path.exists(eda_ringkas_csv)
      and os.path.exists(eda_plot_utama)):
    print(f"⏩ [CACHE HIT] Memuat hasil EDA tersimpan dari: {eda_stats_csv}")
    df_stats = pd.read_csv(eda_stats_csv)
    df_ringkas = pd.read_csv(eda_ringkas_csv)
    df_records = pd.DataFrame()
elif acos_taxonomy.is_id_domain(DOMAIN):
    # colab_utils.analyze_and_plot_eda() memetakan domain lewat tabel tertutup
    # {rest16, laptop} dengan fallback ke Restaurant-ACOS — domain 'appsid' TIDAK
    # error di sana, ia diam-diam melaporkan statistik dataset Inggris. Karena itu
    # jalur Indonesia memakai fungsi sendiri dengan kontrak keluaran identik.
    print("📊 Menjalankan EDA dataset Indonesia (acos_id.eda)...")
    df_stats, df_records = acos_eda.analyze_and_plot_eda_id(
        data_dir=base_project_dir,
        domain=DOMAIN,
        output_plots_dir=plots_dir,
        output_csv_dir=csv_dir,
    )
else:
    print("📊 Menjalankan Analisis Data Eksploratif (EDA)...")
    df_stats, df_records = analyze_and_plot_eda(
        data_dir=base_project_dir,
        domain=DOMAIN,
        output_plots_dir=plots_dir,
        output_csv_dir=csv_dir,
    )'''

CODE_STEP1_INIT_PATCH = '''    # Domain Indonesia: get_labels() upstream hanya mengenal 'rest*' dan 'laptop';
    # domain lain membiarkan daftar kategori None lalu meledak di `for cate in l`.
    # Patch runtime menambah cabangnya tanpa menyentuh berkas upstream, sehingga
    # jalur Inggris tetap utuh sebagai kontrol.
    _lab_patch = acos_taxonomy.patch_processor_labels(processors)
    st.step(f"Taksonomi Indonesia: {_lab_patch}")

'''



def main():
    # 1. V2 dibangun ulang dulu agar V4 berdiri di atas V2 mutakhir.
    V2.main()

    nb = json.load(io.open(SRC_V2, encoding="utf-8"))
    cells = nb["cells"]

    n_fix = patch_shell_magic_cells(cells)
    if n_fix:
        print(f"  [patch] {n_fix} sel V2 dengan shell-magic berindentasi → os.system")

    apply_patches(cells)

    with io.open(DST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")

    n_code = sum(1 for c in cells if c["cell_type"] == "code")
    digest = hashlib.md5(open(DST, "rb").read()).hexdigest()
    print(f"{os.path.basename(DST)} ditulis: {len(cells)} sel ({n_code} kode). MD5 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
