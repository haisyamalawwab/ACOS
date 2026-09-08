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
  sel 1s    (baru) pemasangan paket `acos_id/` + dua root path
  sel 2     path: indo_root untuk berkas Indonesia, acos_root untuk modul upstream
  sel 3     DOMAIN='appsid', BACKBONE, hyperparameter, root penyimpanan
  sel 4c    (baru) adapter checkpoint IndoBERT + laporan vocab
  sel 4d    (baru) gerbang data Indonesia: taksonomi, split, konversi ACOS,
            generator tokenized_data, gate 2 Inggris
  sel 4/EDA memakai `acos_id.eda.analyze_and_plot_eda_id` untuk domain ID
  sel 5a    patch `get_labels` domain Indonesia sebelum label dibaca
  sel 5d2   (baru) Gate 1 numerik: bobot encoder benar-benar termuat
  sel 6b/6c pemulihan state ikut memulihkan BACKBONE & indo_root

**Dua root.** Berkas Indonesia (dataset, `tokenized_data`, `backbones`,
`results`) berada di `ACOS-IndoBERT/`, sementara modul pipeline
(`Extract-Classify-ACOS/`) dibaca dari repo `ACOS-ASLI/` di folder induk. Notebook
tidak pernah menulis apa pun ke repo itu.

Skrip idempoten: berkas tujuan ditulis ulang dari nol setiap kali dijalankan.
"""
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDO_ROOT = os.path.dirname(HERE)
ACOS_ROOT = os.path.dirname(INDO_ROOT)
V2_DIR = os.path.join(ACOS_ROOT, "notebooks")

# Generator V2 tinggal di repo upstream; V4 berlapis di atasnya tanpa menyalinnya.
if not os.path.isfile(os.path.join(V2_DIR, "_build_staged_v2.py")):
    raise FileNotFoundError(
        f"_build_staged_v2.py tidak ada di {V2_DIR}. Generator V4 berlapis di atas "
        f"V2, jadi repo ACOS-ASLI harus ada di folder induk ACOS-IndoBERT.")
sys.path.insert(0, V2_DIR)

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
| Sumber data | `data/Restaurant-ACOS/` | `data/Apps-ACOS/processed/` → dikonversi di sel 4d |
| Folder sesi | `results/rest16_<ts>/` | `results/appsid_<ts>/` |

Sel baru dibanding V2:

| Sel | Isi | Torch? |
|---|---|---|
| 1s | Sinkronisasi paket `acos_id/` + `sys.path` | tidak |
| 4c | Adapter checkpoint IndoBERT (rekey prefiks `bert.`) + laporan vocab | ya |
| 4d | Gerbang data: taksonomi, split, konversi ACOS, generator `tokenized_data`, gate 2 Inggris | tidak |
| 5d2 | **Gate 1**: bobot encoder dibandingkan numerik dengan checkpoint | ya |

Urutan 4c sebelum 4d disengaja: generator `tokenized_data` memakai vocab
IndoBERT, jadi gerbang data tidak punya tokenizer sebelum adapter selesai.

**Dua kegagalan senyap yang dijaga sel-sel itu.** Pertama, checkpoint IndoBERT
menyimpan key tanpa prefiks `bert.`, sementara loader legacy
(`modeling.py:745`) menetapkan `start_prefix=''` karena `BertForQuadABSA` punya
atribut `self.bert`; tanpa rekey seluruh bobot encoder masuk `missing_keys` dan
logging yang melaporkannya di-comment out (`modeling.py:749-755`) — training
berjalan mulus dengan encoder **acak**. Kedua, `get_labels()` upstream hanya
mengenal `rest*` dan `laptop`; domain lain membuat daftar kategori `None`.
Keduanya diperiksa gate, bukan diasumsikan.

Jalankan sel 1s satu kali setelah setiap restart kernel, sama seperti 1b."""

MD_2B = """### 2c. Dua Root & Paket `acos_id/`

V4 memakai **dua root** yang tidak boleh tertukar:

| Variabel | Isi | Ditulis? |
|---|---|---|
| `indo_root` | `ACOS-IndoBERT/` — dataset, `tokenized_data`, `backbones`, `results` | ya, semuanya |
| `acos_root` | `ACOS-ASLI/` — `Extract-Classify-ACOS/` + data rest16 | **tidak**, baca saja |

Seluruh perbedaan Indonesia ada di paket `acos_id/` di bawah `indo_root`,
**bukan** patch pada `Extract-Classify-ACOS/`. Jalur Inggris karena itu tetap
utuh dan bisa dipakai sebagai kontrol: cukup ganti `DOMAIN` kembali ke `rest16`
di sel 3.

Sel ini berada **setelah** dua sel path di atasnya, bukan sebelum: sel-sel itu
menetapkan `base_project_dir` dan `extract_dir` dari hasil deteksi Drive, dan sel
ini yang menimpanya dengan nilai dua-root yang benar. Kalau urutannya dibalik,
penimpaannya justru yang hilang — tanpa pesan apa pun.

Kelengkapan paket diperiksa per-modul, bukan sekadar `import acos_id`, karena
folder yang tersinkron separuh lolos pemeriksaan paket tetapi gagal beberapa sel
kemudian, jauh dari penyebabnya.

Jalankan sel ini sekali setiap kali kernel di-restart, sama seperti 1b."""

CODE_2B = '''# ============================================================
#  Dua root: indo_root (ditulis) & acos_root (baca saja)
# ============================================================
ACOS_ID_MODULES = ("taxonomy", "build_acos", "tokenize_data", "checkpoint",
                   "selftest", "eda", "upstream")

import importlib

# Repo GitHub yang memuat kedua folder. Dipakai hanya bila ACOS-IndoBERT belum ada.
ACOS_REPO_URL = "https://github.com/haisyamalawwab/ACOS.git"


def _cari_indo_root():
    """Folder ACOS-IndoBERT: satu-satunya penanda adalah subfolder acos_id/."""
    kandidat = []
    if os.path.exists("/content/drive/MyDrive"):
        kandidat += ["/content/drive/MyDrive/ACOS-IndoBERT",
                     "/content/drive/MyDrive/ACOS/ACOS-IndoBERT",
                     "/content/drive/MyDrive/ACOS-ASLI/ACOS-IndoBERT"]
    _base = globals().get("base_project_dir") or os.path.abspath(".")
    kandidat += [os.path.join(_base, "ACOS-IndoBERT"),
                 os.path.abspath("ACOS-IndoBERT"),
                 os.path.abspath(os.path.join("..", "ACOS-IndoBERT")),
                 os.path.abspath(".")]
    for _d in kandidat:
        if os.path.isdir(os.path.join(_d, "acos_id")):
            return _d
    return None


indo_root = _cari_indo_root()
if indo_root is None:
    _target = os.path.join(globals().get("base_project_dir") or os.path.abspath("."),
                           "ACOS-IndoBERT")
    print(f"📥 ACOS-IndoBERT belum ada. Menyinkronkan ke {_target} ...")
    _tmp = "/tmp/ACOS_clone_indo"
    os.system(f"rm -rf {_tmp}")
    os.system(f"git clone --depth 1 {ACOS_REPO_URL} {_tmp}")
    _src = os.path.join(_tmp, "ACOS-IndoBERT")
    if not os.path.isdir(os.path.join(_src, "acos_id")):
        raise RuntimeError(
            f"folder ACOS-IndoBERT/acos_id tidak ada di {ACOS_REPO_URL}. Unggah "
            f"folder ACOS-IndoBERT/ ke Drive secara manual, lalu ulangi sel ini.")
    os.makedirs(_target, exist_ok=True)
    os.system(f'cp -r "{_src}/." "{_target}/"')
    os.system(f"rm -rf {_tmp}")
    indo_root = _target
    print("✅ ACOS-IndoBERT tersinkron.")

_acos_id_dir = os.path.join(indo_root, "acos_id")
_missing = [f"{_m}.py" for _m in ACOS_ID_MODULES
            if not os.path.isfile(os.path.join(_acos_id_dir, f"{_m}.py"))
            or os.path.getsize(os.path.join(_acos_id_dir, f"{_m}.py")) == 0]
if _missing:
    raise RuntimeError(f"acos_id tidak lengkap di {_acos_id_dir}; hilang: {_missing}")


def _prepend_path(p):
    """Paksa p ke posisi terdepan sys.path walau sudah ada di urutan lebih rendah."""
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)


_prepend_path(indo_root)

for _m in list(sys.modules):
    if _m == "acos_id" or _m.startswith("acos_id."):
        del sys.modules[_m]

acos_id = importlib.import_module("acos_id")
acos_taxonomy = importlib.import_module("acos_id.taxonomy")
acos_selftest = importlib.import_module("acos_id.selftest")
acos_ckpt = importlib.import_module("acos_id.checkpoint")
acos_eda = importlib.import_module("acos_id.eda")
acos_upstream = importlib.import_module("acos_id.upstream")

# Root pipeline Inggris. find_upstream() menuntut keempat berkas kunci ada, jadi
# folder bernama benar tapi kosong ditolak di sini — bukan nanti saat impor
# modeling, di mana pesannya tidak menunjuk penyebabnya.
extract_dir = acos_upstream.ensure_path(
    acos_root=globals().get("base_project_dir"))
acos_root = os.path.dirname(extract_dir)

# Seluruh penyimpanan Indonesia di bawah indo_root; tidak satu pun di bawah
# acos_root, supaya repo pipeline Inggris tetap bersih.
save_dir = indo_root
data_root = os.path.join(indo_root, "data")
tokenized_dir = os.path.join(indo_root, "tokenized_data")
backbones_dir = os.path.join(indo_root, "backbones")
for _d in (data_root, tokenized_dir, backbones_dir,
           os.path.join(indo_root, "results"), os.path.join(indo_root, "build")):
    os.makedirs(_d, exist_ok=True)

print(f"🇮🇩 acos_id v{acos_id.__version__}")
print(f"   indo_root  (tulis) : {indo_root}")
print(f"   acos_root  (baca)  : {acos_root}")
print(f"   extract_dir        : {extract_dir}")
print(f"   data / tokenized   : {data_root} | {tokenized_dir}")
print(f"   Domain Indonesia   : {acos_taxonomy.DOMAIN}")
print(f"   Kategori           : {len(acos_taxonomy.CATEGORIES)} "
      f"→ num_labels Step 2 = {acos_taxonomy.num_labels_step2()}")
print(f"   Label sekuens S1   : {list(acos_taxonomy.SEQ_LABELS)}")
print(f"   Gerbang torch-free : {', '.join(acos_selftest.TORCH_FREE_GATES)}")'''

MD_4C = """### 4c. Adapter Checkpoint IndoBERT

Menyiapkan `bert_cache_dir` berisi `config.json`, `pytorch_model.bin`, dan
`vocab.txt` IndoBERT, dengan state_dict yang sudah **direkey**: setiap key
diberi prefiks `bert.` agar cocok dengan `start_prefix=''` yang dipakai loader
legacy pada kelas yang punya atribut `self.bert`.

Sel ini harus berjalan **sebelum** gerbang data 4d, bukan sesudahnya: generator
`tokenized_data` memakai vocab IndoBERT, jadi gate `tokenized` tidak punya
tokenizer sebelum sel ini selesai.

Idempoten lewat penanda `_rekey.json` di folder yang sama. Penanda itu bukan
kenyamanan: menjalankan rekey dua kali menghasilkan `bert.bert.embeddings...`,
dan hasilnya sama buruknya dengan tidak merekey sama sekali.

Laporan vocab akan menunjukkan `config.vocab_size = 50000` sementara `vocab.txt`
berisi 30.521 token. Itu memang begitu untuk `indobert-base-p1` — matriks
embedding-nya benar-benar 50.000 baris dan id 30.521+ tidak pernah terpakai.
Jangan pernah memakai `config.vocab_size` sebagai jumlah token."""

CODE_4C = '''require_vars("step_stage", "acos_ckpt", "bert_cache_dir", "BACKBONE")

with step_stage("4c. Adapter checkpoint IndoBERT (rekey prefiks bert.)", 5) as st:
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
        export_step_table(df_backbone, name="master_00_backbone_indobert",
                          csv_dir=csv_dir, md_dir=md_dir,
                          title="Adapter Checkpoint IndoBERT")
        rep.section("1b. Backbone & gerbang data")
        rep.table(df_backbone, caption="Backbone & hasil rekey")

        with open(os.path.join(session_dirs["logs"], "backbone_report.json"),
                  "w", encoding="utf-8") as jf:
            json.dump(backbone_report, jf, indent=2, ensure_ascii=False, default=str)
        st.step("backbone_report.json tersimpan; Gate 1 numerik menyusul di sel 5d2")'''

MD_4D = """### 4d. Gerbang Data Indonesia (wajib sebelum training)

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

`tokenized` memakai vocab IndoBERT dari sel 4c, jadi 4c harus sudah selesai.

`gate2_english` memberi toleransi satu kalimat pada `rest16_train_pair.tsv`.
Itu cacat data upstream: `rest16_quad_train.tsv` baris 451 memuat span opini
lebar-nol `3,3`, dan berkas repo memetakan baris itu tidak konsisten antara
`*_quad_bert.tsv` (`3,4`) dan `*_pair.tsv` (`3,5`, plus satu pasangan hilang).
Generator mengikuti berkas quad, yang dipakai Step 1."""

CODE_4D = '''require_vars("step_stage", "acos_selftest", "acos_taxonomy", "DOMAIN")

# Set True untuk membangun ulang berkas ACOS & tokenized_data dari nol.
FORCE_REBUILD_ID_DATA = False

with step_stage("4d. Gerbang data Indonesia (5 gate torch-free)", 6) as st:
    if not acos_taxonomy.is_id_domain(DOMAIN):
        st.step(f"DOMAIN='{DOMAIN}' bukan domain Indonesia — seluruh gate dilewati")
        st.note("Notebook berjalan sebagai kontrol Inggris; sel 4c & 5d2 juga "
                "melewati dirinya sendiri.")
        id_gate_results = {}
    else:
        if not os.path.exists(os.path.join(bert_cache_dir, "vocab.txt")):
            raise RuntimeError(
                f"vocab.txt belum ada di {bert_cache_dir}. Jalankan sel 4c "
                f"(adapter checkpoint IndoBERT) lebih dulu — generator "
                f"tokenized_data memakai vocab itu.")

        # default_paths() menurunkan seluruh path dari dua root; yang ditimpa di
        # sini hanya bert_cache_dir (nama folder tergantung BACKBONE) dan
        # work_dir (keluaran gate 2 disimpan di folder sesi, bukan build/).
        _paths = acos_selftest.default_paths(indo_root, acos_root)
        _paths["bert_cache_dir"] = bert_cache_dir
        _paths["work_dir"] = os.path.join(session_dirs["logs"], "gates")
        st.step(f"Sumber data   : {_paths['data_root']}")
        st.step(f"Vocab IndoBERT: {_paths['bert_cache_dir']}")
        st.note(f"tokenized_data → {_paths['tokenized_dir']}")
        st.note(f"upstream (baca) → {_paths['extract_dir']}")

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
        export_step_table(df_id_gates, name="master_00b_gerbang_data_id",
                          csv_dir=csv_dir, md_dir=md_dir,
                          title="Gerbang Data Indonesia (Apps-ACOS)")
        rep.table(df_id_gates, caption="Konversi & retokenisasi per split")
        st.step("Tabel master_00b ditulis")

        _gate_json = os.path.join(session_dirs["logs"], "id_gates.json")
        with open(_gate_json, "w", encoding="utf-8") as jf:
            json.dump({k: {"ok": v["ok"], "detail": v["detail"]}
                       for k, v in id_gate_results.items()},
                      jf, indent=2, ensure_ascii=False, default=str)
        st.step(f"Hasil gate → {_gate_json}")
        update_mcp_manifest("ID_DATA_GATES_PASSED", 1,
                            {"n_gate": len(id_gate_results),
                             "num_labels_step2": acos_taxonomy.num_labels_step2()})'''

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
                "prefiks 'bert.' tidak pernah termuat). Jalankan ulang sel 4c dengan "
                "acos_ckpt.prepare_backbone(BACKBONE, bert_cache_dir, force_rekey=True).")
        st.step("Gate 1 LULUS — fine-tuning berjalan di atas bobot IndoBERT terlatih")'''


def apply_patches(cells):
    """Terapkan seluruh perubahan V4 pada daftar sel V2 (in-place)."""
    # 1. Judul.
    head = "".join(cells[0]["source"]).rstrip("\n")
    cells[0] = md(head + "\n" + MD_TITLE_V4)

    # 2. Konfigurasi (sel 3): DOMAIN, BACKBONE, DO_LOWER_CASE.
    i_cfg = find_code(cells, "DOMAIN = \"rest16\"", "NUM_EPOCHS")
    cells[i_cfg] = code(CODE_CONFIG)

    # 3. Sel sesi V2 dipecah pada penanda unduhan BERT: bagian atas (pencarian
    #    sesi lama) diganti supaya hanya mencari di bawah indo_root, bagian bawah
    #    diganti supaya bert_cache_dir ada di indo_root/backbones per backbone.
    i_sess = find_code(cells, "download_bert_pretrained(target_dir=bert_cache_dir)",
                       "session_dirs")
    src = "".join(cells[i_sess]["source"])
    marker = "# 2. Unduh dan cache model pretrained BERT (HuggingFace Hub)"
    if marker not in src:
        raise LookupError("penanda unduhan BERT di sel sesi tidak ditemukan")
    cells[i_sess] = code(CODE_RESULT_ROOTS.strip("\n") + "\n" + CODE_SESSION_TAIL)

    # 4. Sel 2c (dua root + paket acos_id) setelah sel impor colab_utils, bukan
    #    setelah 1b: dua sel path V2 di antaranya menetapkan base_project_dir dan
    #    extract_dir dari deteksi Drive, dan sel ini yang menimpanya dengan nilai
    #    dua-root yang benar. Kalau disisipkan sebelum keduanya, penimpaan itu
    #    justru yang hilang — tanpa pesan apa pun.
    i_utils = find_code(cells, "REQUIRED_UTILS", "colab_utils aktif")
    cells[i_utils + 1:i_utils + 1] = [md(MD_2B), code(CODE_2B)]

    # 5. EDA: pilih jalur Indonesia bila domainnya Indonesia.
    i_eda = find_code(cells, "analyze_and_plot_eda(", "CACHE HIT")
    cells[i_eda] = code(CODE_EDA)

    # 6. Sel 4c & 4d setelah sel diagnostik 4b. Keduanya butuh session_dirs,
    #    csv_dir, rep, dan bert_cache_dir — semuanya sudah ada di titik ini.
    i_diag = find_code(cells, "inspect_acos_drive_structure(")
    cells[i_diag + 1:i_diag + 1] = [md(MD_4C), code(CODE_4C),
                                    md(MD_4D), code(CODE_4D)]

    # 7. Patch taksonomi disisipkan ke sel 5a, tepat sebelum get_labels dipanggil.
    i_5a = find_code(cells, "5a. Inisialisasi Step 1", "processor_step1 = processors")
    src = "".join(cells[i_5a]["source"])
    anchor = "    processor_step1 = processors[\"quad\"]()"
    if anchor not in src:
        raise LookupError("baris processor_step1 di sel 5a tidak ditemukan")
    # Jumlah langkah step_stage harus ikut naik satu; tanpa ini penomoran
    # "n/total" pada cetakan progres jadi salah.
    src = src.replace('with step_stage("5a. Inisialisasi Step 1: tokenizer, patch metrik, '
                      'label, path", 6) as st:',
                      'with step_stage("5a. Inisialisasi Step 1: tokenizer, patch metrik, '
                      'taksonomi ID, label, path", 7) as st:')
    cells[i_5a] = code(src.replace(anchor, CODE_STEP1_INIT_PATCH + anchor))

    # 8. Sel 5d2 (Gate 1) setelah sel 5d yang memuat model_step1. Harus sesudah,
    #    bukan sebelum: gate membandingkan model yang sudah di-from_pretrained.
    i_5d = find_code(cells, "5d. Model BERT-CRF", "BertForQuadABSA.from_pretrained")
    cells[i_5d + 1:i_5d + 1] = [md(MD_5D2), code(CODE_5D2)]

    # 9. ensure_objects(): patch taksonomi juga di sini, karena setelah restart
    #    kernel sel 7a/8a/8c/9a bisa menjadi sel pertama yang berjalan.
    i_ens = find_code(cells, "def ensure_objects():")
    src = "".join(cells[i_ens]["source"])
    if CODE_ENSURE_ANCHOR not in src:
        raise LookupError("penanda blok label di ensure_objects tidak ditemukan")
    cells[i_ens] = code(src.replace(CODE_ENSURE_ANCHOR,
                                    CODE_ENSURE_PATCH + CODE_ENSURE_ANCHOR))

    # 10. Sel pemulihan state & ensure_objects masih menyusun bert_cache_dir dari
    #     base_project_dir + "bert_base_uncased". Untuk domain Indonesia itu
    #     memuat vocab yang salah tanpa pesan apa pun — tokenizer jalan, tapi
    #     hampir seluruh token Indonesia jadi [UNK]. Diarahkan ke
    #     indo_root/backbones/<backbone>, dengan indo_root ikut dari state.
    i_recover = find_code(cells, "target_state_path", "pipe_state.get")
    for i in (i_ens, i_recover):
        src = "".join(cells[i]["source"])
        cells[i] = code(src.replace(
            'os.path.join(base_project_dir, "bert_base_uncased")',
            'os.path.join(pipe_state.get("indo_root", base_project_dir), "backbones",\n'
            '                                     _backbone_dirname(pipe_state.get("BACKBONE")))'
        ).replace(
            'os.path.join(\n                g.get("base_project_dir", "."), "bert_base_uncased")',
            'os.path.join(\n'
            '                g.get("indo_root") or g.get("base_project_dir", "."),\n'
            '                "backbones", _backbone_dirname(g.get("BACKBONE")))'
        ))

    # 11. BACKBONE dan indo_root ikut disimpan ke pipeline_state.pkl lalu
    #     dipulihkan. Sel pemulihan (patch 10) membacanya; tanpa disimpan,
    #     `pipe_state.get` mengembalikan None, _backbone_dirname jatuh ke folder
    #     Inggris, dan tokenizer memuat vocab yang salah — gejalanya hanya F1
    #     rendah.
    i_save = find_code(cells, "def save_pipeline_state(")
    src = "".join(cells[i_save]["source"])
    anchor = '        "DOMAIN": DOMAIN,'
    if anchor not in src:
        raise LookupError("kunci DOMAIN di state_data tidak ditemukan")
    cells[i_save] = code(src.replace(
        anchor,
        anchor
        + '\n        "BACKBONE": globals().get("BACKBONE", "bert-en"),'
        + '\n        "indo_root": globals().get("indo_root", base_project_dir),'
        + '\n        "acos_root": globals().get("acos_root", base_project_dir),'
        + '\n        "tokenized_dir": globals().get("tokenized_dir", ""),'))

    src = "".join(cells[i_recover]["source"])
    anchor = '    DOMAIN = pipe_state.get("DOMAIN", "rest16")'
    if anchor not in src:
        raise LookupError("baris pemulihan DOMAIN tidak ditemukan")
    cells[i_recover] = code(src.replace(
        anchor,
        anchor
        + '\n    BACKBONE = pipe_state.get("BACKBONE", "bert-en")'
        + '\n    indo_root = pipe_state.get("indo_root", base_project_dir)'
        + '\n    tokenized_dir = pipe_state.get("tokenized_dir") or os.path.join('
        + 'indo_root, "tokenized_data")'))

    # 12. Contoh inferensi live: teks Inggris pada model Indonesia menghasilkan
    #     demo yang menyesatkan (hampir semua token jadi [UNK]).
    i_infer = find_code(cells, "def analyze_review_quadruples(")
    src = "".join(cells[i_infer]["source"])
    if CODE_SAMPLE_ANCHOR not in src:
        raise LookupError("baris sample_review tidak ditemukan")
    cells[i_infer] = code(src.replace(CODE_SAMPLE_ANCHOR, CODE_SAMPLE_REVIEW))

    # 13. Sumber tokenized_data. Processor upstream menyusun path sendiri
    #     (`os.path.join(data_dir, "tokenized_data/" + domain + "_..._quad_bert.tsv")`),
    #     jadi yang diganti adalah argumen `data_dir`-nya: `tokenized_base` —
    #     `indo_root` untuk domain Indonesia, `extract_dir` untuk kontrol Inggris.
    #     Tanpa ini Step 1 membaca folder tokenized_data milik repo upstream, yang
    #     tidak memuat berkas appsid_* sama sekali (FileNotFoundError di 5c) — atau
    #     lebih buruk, memuatnya bila seseorang pernah menyalinnya ke sana.
    n_tb = 0
    for i, c in enumerate(cells):
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        baru = (src
                .replace('os.path.join(extract_dir, "tokenized_data"',
                         'os.path.join(tokenized_base, "tokenized_data"')
                .replace('get_dev_examples(extract_dir, DOMAIN)',
                         'get_dev_examples(tokenized_base, DOMAIN)')
                .replace('get_train_examples(extract_dir, DOMAIN)',
                         'get_train_examples(tokenized_base, DOMAIN)')
                .replace('os.path.join(extract_dir, "tokenized_data",\n',
                         'os.path.join(tokenized_base, "tokenized_data",\n'))
        if baru != src:
            cells[i] = code(baru)
            n_tb += 1
    if n_tb == 0:
        raise LookupError("tidak ada rujukan tokenized_data yang dialihkan")

    # 14. Resume training per-epoch (rolling checkpoint + optimizer state): sel
    #      deteksi 5b/8b membaca step1/2_resume.json (+ menyalin checkpoint epoch
    #      terakhir dari sesi lama), sel training 5e/8e merestorasi bobot +
    #      optimizer lalu melanjutkan dari epoch berikutnya. Keempat sel diganti
    #      utuh dengan versi teruji di .ipynb V4 — pola yang sama dengan penulisan
    #      ulang sel lain di generator ini. Dibangkitkan/diperbarui oleh
    #      `ACOS-IndoBERT/build/_port_resume_to_v4.py`.
    for _needles, _full in RESUME_SPECS:
        cells[find_code(cells, *_needles)] = code(_full)

    return cells, {"n_sel_tokenized_base": n_tb}


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

# Early Stopping: berhenti jika F1 tidak membaik selama N epoch berturut-turut
# (menghemat waktu Colab saat training sudah plateau). Set PATIENCE = 0 untuk
# menonaktifkan early stopping.
PATIENCE = 5
MIN_EPOCHS_BEFORE_STOP = 5  # Training minimal jalan N epoch dulu sebelum early stopping aktif

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

# Satu folder cache per backbone. Bukan kenyamanan: kalau IndoBERT dan
# bert-base-uncased berbagi folder, checkpoint yang satu menimpa yang lain dan
# tokenizer tetap memuat vocab yang salah tanpa pesan error — seluruh token
# Indonesia menjadi [UNK] dan yang terlihat hanya F1 rendah.
BACKBONE_DIRNAME = {
    "indobert": "indobert_base_p1",
    "indobert-large": "indobert_large_p1",
    "bert-en": "bert_base_uncased",
}


def _backbone_dirname(backbone=None):
    """Nama folder cache untuk sebuah backbone; dipakai juga sel pemulihan state."""
    key = backbone or globals().get("BACKBONE") or "bert-en"
    return BACKBONE_DIRNAME.get(key, str(key).replace("-", "_"))


# `tokenized_base` adalah argumen `data_dir` yang diberikan ke processor upstream.
# Processor menyusun sendiri `<data_dir>/tokenized_data/<domain>_..._quad_bert.tsv`,
# jadi satu variabel ini yang menentukan Step 1/Step 2 membaca berkas Indonesia di
# indo_root atau berkas Inggris di repo upstream — tanpa menyalin apa pun ke sana.
tokenized_base = indo_root if _IS_ID_DOMAIN else extract_dir
print(f"📚 tokenized_base : {tokenized_base}")

# Reproducibility seeding
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

active_save_dir = indo_root

# Sesi dilanjutkan bila ada artefak tersimpan; set False untuk memaksa sesi baru.
RESUME_LAST_SESSION = True

# 1. Direktori sesi. Seluruhnya di bawah indo_root — repo pipeline Inggris tidak
#    pernah menerima artefak run.
results_base = os.path.join(indo_root, "results")

print(f"🇮🇩 Domain   : {DOMAIN} ({'Indonesia' if _IS_ID_DOMAIN else 'Inggris (kontrol)'})")
print(f"🧠 Backbone : {BACKBONE}")
print(f"📁 Sesi     : {results_base}/{DOMAIN}_<timestamp>/")'''

CODE_RESULT_ROOTS = '''
# Kandidat lokasi pencarian sesi terdahulu. Hanya di bawah indo_root: sesi milik
# pipeline Inggris memakai folder lain dan tidak boleh ikut dipilih, karena
# checkpoint-nya memakai vocab yang berbeda.
candidate_result_roots = [
    results_base,
    os.path.join(indo_root, "Output", "results"),
    "/content/drive/MyDrive/ACOS-IndoBERT/results",
    "/content/drive/MyDrive/ACOS/ACOS-IndoBERT/results",
    "/content/drive/MyDrive/ACOS-ASLI/ACOS-IndoBERT/results",
]

_resume_root = find_resumable_session(candidate_result_roots, DOMAIN) if RESUME_LAST_SESSION else None
if _resume_root:
    session_dirs = session_dirs_from_root(_resume_root)
    print(f"♻️ Melanjutkan sesi tersimpan: {_resume_root}")
    print(f"   Artefak kunci terdeteksi: {session_cache_score(_resume_root)}/6")
else:
    session_dirs = setup_timestamped_run_dir(base_dir=results_base, domain=DOMAIN)

# Verifikasi integritas dan izin simpan sesi
verify_session_save_paths(session_dirs, domain=DOMAIN)
'''

CODE_SESSION_TAIL = '''
# 2. Backbone cache di bawah indo_root/backbones, satu folder per backbone
#    (nama dari _backbone_dirname() di sel 3). Isinya diunduh & direkey di sel 4c
#    — di sini hanya path-nya yang ditetapkan.
bert_cache_dir = os.path.join(backbones_dir, _backbone_dirname(BACKBONE))
os.makedirs(bert_cache_dir, exist_ok=True)

if BACKBONE == "bert-en":
    # Jalur kontrol: fungsi V2 apa adanya, tanpa rekey.
    download_bert_pretrained(target_dir=bert_cache_dir)
else:
    _n_ada = sum(1 for _f in ("config.json", "pytorch_model.bin", "vocab.txt")
                 if os.path.exists(os.path.join(bert_cache_dir, _f)))
    print(f"🧠 Backbone dir : {bert_cache_dir} ({_n_ada}/3 berkas ada)")
    print("   Unduh & rekey dilakukan di sel 4c (jangan pakai download_bert_pretrained "
          "untuk IndoBERT — fungsi itu selalu mengunduh bert-base-uncased).")

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
        data_dir=data_root,
        domain=DOMAIN,
        output_plots_dir=plots_dir,
        output_csv_dir=csv_dir,
    )
else:
    # Kontrol Inggris: data rest16/laptop dibaca dari repo ACOS-ASLI.
    print("📊 Menjalankan Analisis Data Eksploratif (EDA)...")
    df_stats, df_records = analyze_and_plot_eda(
        data_dir=acos_root,
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

CODE_ENSURE_PATCH = '''    # Domain Indonesia harus dipatch DI SINI juga, bukan hanya di sel 5a.
    # ensure_objects() dipanggil dari sel 7a, 8a, 8c, 9a dan 10; setelah restart
    # kernel salah satu dari sel itu bisa jadi yang pertama berjalan, dan
    # CategorySentiProcessor.get_labels("appsid") tanpa patch mengembalikan
    # `l = None` lalu meledak di `for cate in l` — TypeError yang jauh dari
    # penyebabnya. QuadProcessor tidak terpengaruh (ia mengabaikan domain_type),
    # jadi gejalanya hanya muncul di Step 2.
    if str(g.get("DOMAIN", "")).lower().startswith("apps"):
        try:
            import acos_id.taxonomy as _tax
        except ModuleNotFoundError:
            raise RuntimeError(
                "DOMAIN Indonesia tetapi paket acos_id belum ada di sys.path. "
                "Jalankan sel 1s lebih dulu.")
        from run_classifier_dataset_utils import processors as _procs
        _tax.patch_processor_labels(_procs)

'''

CODE_ENSURE_ANCHOR = "    # 3) Label lists & num_labels (cari dari JSON tersimpan jika belum ada)"

CODE_SAMPLE_REVIEW = '''# Contoh Pengujian Live Review — dipilih menurut bahasa domain.
SAMPLE_REVIEWS = {
    "appsid": "transfer nya cepat tapi aplikasi sering error saat buka menu",
    "rest16": "The sushi was fresh and delicious, but the service was slow.",
    "laptop": "The battery life is great but the keyboard feels cheap.",
}
sample_review = SAMPLE_REVIEWS.get(DOMAIN, SAMPLE_REVIEWS["appsid"])'''

CODE_SAMPLE_ANCHOR = ('# Contoh Pengujian Live Review\n'
                      'sample_review = "The sushi was fresh and delicious, '
                      'but the service was slow."')



# ── Resume training per-epoch (port dari patch manual .ipynb V4) ───────────
# Diport oleh ACOS-IndoBERT/build/_port_resume_to_v4.py. Keempat sel diganti
# UTUH dengan isi versi teruji di .ipynb: sel deteksi 5b/8b membaca
# step1/2_resume.json, sel training 5e/8e merestorasi bobot+optimizer lalu
# melanjutkan dari epoch berikutnya (rolling checkpoint per epoch).
RESUME_SPECS = [
    (("""step1_already_done = os.path.exists(step1_bin)""", """STEP1_SKIP_TRAINING = (not FORCE_RETRAIN_STEP1)"""),
     """require_vars("step_stage", "step1_bin", "pred_file", "step1_csv", "FORCE_RETRAIN_STEP1")

with step_stage("5b. Deteksi cache Step 1 (sesi aktif lalu sesi lama)", 4) as st:
    step1_already_done = os.path.exists(step1_bin) and os.path.exists(pred_file)
    st.step("Sesi aktif — model: {} | pred4pipeline: {}".format(
        f"{os.path.getsize(step1_bin) / 1024 ** 2:.1f} MB" if os.path.exists(step1_bin) else "belum ada",
        f"{sum(1 for _ in open(pred_file, encoding='utf-8'))} baris" if os.path.exists(pred_file) else "belum ada"))

    if step1_already_done:
        st.step("Pencarian sesi lama dilewati (artefak sesi aktif sudah lengkap)")
    else:
        found_bin = auto_find_file("pytorch_model.bin", must_contain="step1_best", search_roots=[
            results_base if 'results_base' in globals() else "",
            "/content/drive/MyDrive/ACOS/Output/results",
            os.path.join(base_project_dir, "Output", "results"),
        ])
        if found_bin and "step1_best" in found_bin:
            src_dir = os.path.dirname(found_bin)
            st.step(f"Checkpoint sesi sebelumnya ditemukan: {src_dir}")
            for fn in ["pytorch_model.bin", "config.json", "vocab.txt"]:
                fp = os.path.join(src_dir, fn)
                if os.path.exists(fp):
                    shutil.copy(fp, os.path.join(step1_ckpt, fn))
                    st.note(f"↪ {fn} ({os.path.getsize(fp) / 1024 ** 2:.1f} MB) disalin ke sesi aktif")
            found_pred = auto_find_file("pred4pipeline.txt")
            if found_pred:
                shutil.copy(found_pred, pred_file)
                st.note(f"↪ pred4pipeline.txt disalin dari {found_pred}")
            found_csv = auto_find_file("step1_training_history.csv")
            if found_csv:
                shutil.copy(found_csv, step1_csv)
                st.note(f"↪ step1_training_history.csv disalin dari {found_csv}")
            step1_already_done = os.path.exists(step1_bin) and os.path.exists(pred_file)
        else:
            st.step("Tidak ada checkpoint step1_best di sesi mana pun")

    STEP1_SKIP_TRAINING = (not FORCE_RETRAIN_STEP1) and step1_already_done
    st.step("Keputusan: " + ("CACHE HIT → sel 5c-5e dilewati"
                             if STEP1_SKIP_TRAINING else
                             f"TRAINING dijalankan ({NUM_EPOCHS} epoch)"))

    if STEP1_SKIP_TRAINING:
        print(f"⏩ [CACHE HIT] Model Step 1 : {step1_ckpt}")
        print(f"⏩ [CACHE HIT] Prediksi     : {pred_file}")
        if os.path.exists(step1_csv):
            df_s1_saved = pd.read_csv(step1_csv)
            step1_history = df_s1_saved.to_dict('records')
            _row_c1, best_step1_f1, best1_epoch = best_epoch_row(step1_history)
            best1_epoch = best1_epoch or NUM_EPOCHS
            st.step(f"Riwayat tersimpan: {len(df_s1_saved)} epoch, terbaik epoch {best1_epoch}")
            if len(df_s1_saved) < NUM_EPOCHS:
                st.note(f"⚠️ Riwayat hanya {len(df_s1_saved)}/{NUM_EPOCHS} epoch — checkpoint ini "
                        f"berasal dari run yang terhenti. Set FORCE_RETRAIN_STEP1=True bila "
                        f"ingin melatih penuh.")
        else:
            step1_history = []
            best_step1_f1 = 0.0
            best1_epoch = NUM_EPOCHS
            st.step("Riwayat CSV tidak ada — metrik per epoch tidak bisa dilaporkan")
# ── Resume Epoch: cek apakah training Step 1 terhenti di tengah jalan ────────
step1_resume_json = os.path.join(session_dirs["logs"], "step1_resume.json")
STEP1_RESUME_EPOCH = 0  # epoch terakhir yang selesai (0 = belum ada / baru)

if (not STEP1_SKIP_TRAINING) and (not FORCE_RETRAIN_STEP1):
    if not os.path.exists(step1_resume_json):
        _found_resume = auto_find_file("step1_resume.json", search_roots=[
            results_base if 'results_base' in globals() else "",
            "/content/drive/MyDrive/ACOS/Output/results",
            os.path.join(base_project_dir, "Output", "results"),
        ])
        if _found_resume and os.path.exists(_found_resume):
            try:
                _rj_prev = json.load(open(_found_resume, encoding="utf-8"))
                _last_prev = int(_rj_prev.get("last_completed_epoch", 0))
                _prev_session_root = os.path.dirname(os.path.dirname(_found_resume))
                _prev_epoch_dir = os.path.join(_prev_session_root, "checkpoints", f"step1_epoch_{_last_prev}")
                if os.path.isdir(_prev_epoch_dir):
                    _tgt_epoch_dir = os.path.join(session_dirs["checkpoints"], f"step1_epoch_{_last_prev}")
                    os.makedirs(_tgt_epoch_dir, exist_ok=True)
                    for _f in os.listdir(_prev_epoch_dir):
                        shutil.copy(os.path.join(_prev_epoch_dir, _f), os.path.join(_tgt_epoch_dir, _f))
                    shutil.copy(_found_resume, step1_resume_json)
                    print(f"↪ [RESUME] Menyalin resume checkpoint dari sesi lama: epoch {_last_prev}")
            except Exception as _e_copy:
                print(f"⚠️ Gagal menyalin resume dari sesi lama: {_e_copy}")

    if os.path.exists(step1_resume_json):
        try:
            _rj = json.load(open(step1_resume_json, encoding="utf-8"))
            _last = int(_rj.get("last_completed_epoch", 0))
            _total = int(_rj.get("total_epochs", NUM_EPOCHS))
            _epoch_ckpt_check = os.path.join(
                session_dirs["checkpoints"], f"step1_epoch_{_last}")
            _epoch_bin_check  = os.path.join(_epoch_ckpt_check, "pytorch_model.bin")
            if _total != NUM_EPOCHS:
                print(f"⚠️  [RESUME] NUM_EPOCHS berubah ({_total}→{NUM_EPOCHS}). "
                      f"Resume diabaikan — training dari awal.")
            elif _last > 0 and _last < NUM_EPOCHS and os.path.exists(_epoch_bin_check):
                STEP1_RESUME_EPOCH = _last
                print(f"♻️  [RESUME] Step 1 terhenti di epoch {_last}/{NUM_EPOCHS}. "
                      f"Akan dilanjutkan dari epoch {_last + 1}.")
            elif _last >= NUM_EPOCHS:
                print(f"✅ [RESUME] step1_resume.json menunjukkan training sudah "
                      f"selesai ({_last}/{NUM_EPOCHS} epoch).")
        except Exception as _re:
            print(f"⚠️  Tidak bisa membaca step1_resume.json: {_re}. Training dari awal.")

elif STEP1_SKIP_TRAINING:
    if os.path.exists(step1_resume_json):
        try:
            _rj_info = json.load(open(step1_resume_json, encoding="utf-8"))
            _ep_info = _rj_info.get("last_completed_epoch", "?")
            print(f"ℹ️  step1_resume.json ada (epoch {_ep_info}/{NUM_EPOCHS}) "
                  f"— diabaikan karena cache hit sudah lengkap.")
        except Exception:
            pass

if STEP1_RESUME_EPOCH > 0:
    STEP1_SKIP_TRAINING = False  # paksa jalankan training (lanjut dari epoch berikutnya)
    print(f"   → STEP1_SKIP_TRAINING di-override: training akan lanjut dari "
          f"epoch {STEP1_RESUME_EPOCH + 1}.")
"""),
    (("""step2_already_done = os.path.exists(step2_bin)""", """STEP2_SKIP_TRAINING = (not FORCE_RETRAIN_STEP2)"""),
     """require_vars("step_stage", "step2_bin", "step2_csv", "FORCE_RETRAIN_STEP2")

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
            st.step("Riwayat CSV tidak ada — metrik per epoch tidak bisa dilaporkan")
# ── Resume Epoch: cek apakah training Step 2 terhenti di tengah jalan ────────
step2_resume_json = os.path.join(session_dirs["logs"], "step2_resume.json")
STEP2_RESUME_EPOCH = 0  # epoch terakhir yang selesai (0 = belum ada / baru)

if (not STEP2_SKIP_TRAINING) and (not FORCE_RETRAIN_STEP2):
    if not os.path.exists(step2_resume_json):
        _found_resume2 = auto_find_file("step2_resume.json", search_roots=[
            results_base if 'results_base' in globals() else "",
            "/content/drive/MyDrive/ACOS/Output/results",
            os.path.join(base_project_dir, "Output", "results"),
        ])
        if _found_resume2 and os.path.exists(_found_resume2):
            try:
                _rj2_prev = json.load(open(_found_resume2, encoding="utf-8"))
                _last2_prev = int(_rj2_prev.get("last_completed_epoch", 0))
                _prev_session_root2 = os.path.dirname(os.path.dirname(_found_resume2))
                _prev_epoch_dir2 = os.path.join(_prev_session_root2, "checkpoints", f"step2_epoch_{_last2_prev}")
                if os.path.isdir(_prev_epoch_dir2):
                    _tgt_epoch_dir2 = os.path.join(session_dirs["checkpoints"], f"step2_epoch_{_last2_prev}")
                    os.makedirs(_tgt_epoch_dir2, exist_ok=True)
                    for _f in os.listdir(_prev_epoch_dir2):
                        shutil.copy(os.path.join(_prev_epoch_dir2, _f), os.path.join(_tgt_epoch_dir2, _f))
                    shutil.copy(_found_resume2, step2_resume_json)
                    print(f"↪ [RESUME] Menyalin resume checkpoint Step 2 dari sesi lama: epoch {_last2_prev}")
            except Exception as _e_copy2:
                print(f"⚠️ Gagal menyalin resume Step 2 dari sesi lama: {_e_copy2}")

    if os.path.exists(step2_resume_json):
        try:
            _rj2 = json.load(open(step2_resume_json, encoding="utf-8"))
            _last2  = int(_rj2.get("last_completed_epoch", 0))
            _total2 = int(_rj2.get("total_epochs", NUM_EPOCHS))
            _epoch_ckpt_check2 = os.path.join(
                session_dirs["checkpoints"], f"step2_epoch_{_last2}")
            _epoch_bin_check2  = os.path.join(_epoch_ckpt_check2, "pytorch_model.bin")
            if _total2 != NUM_EPOCHS:
                print(f"⚠️  [RESUME] NUM_EPOCHS berubah ({_total2}→{NUM_EPOCHS}). "
                      f"Resume Step 2 diabaikan — training dari awal.")
            elif _last2 > 0 and _last2 < NUM_EPOCHS and os.path.exists(_epoch_bin_check2):
                STEP2_RESUME_EPOCH = _last2
                print(f"♻️  [RESUME] Step 2 terhenti di epoch {_last2}/{NUM_EPOCHS}. "
                      f"Akan dilanjutkan dari epoch {_last2 + 1}.")
            elif _last2 >= NUM_EPOCHS:
                print(f"✅ [RESUME] step2_resume.json menunjukkan training sudah "
                      f"selesai ({_last2}/{NUM_EPOCHS} epoch).")
        except Exception as _re2:
            print(f"⚠️  Tidak bisa membaca step2_resume.json: {_re2}. Training dari awal.")

elif STEP2_SKIP_TRAINING:
    if os.path.exists(step2_resume_json):
        try:
            _rj2_info = json.load(open(step2_resume_json, encoding="utf-8"))
            _ep2_info = _rj2_info.get("last_completed_epoch", "?")
            print(f"ℹ️  step2_resume.json ada (epoch {_ep2_info}/{NUM_EPOCHS}) "
                  f"— diabaikan karena cache hit sudah lengkap.")
        except Exception:
            pass

if STEP2_RESUME_EPOCH > 0:
    STEP2_SKIP_TRAINING = False  # paksa jalankan training (lanjut dari epoch berikutnya)
    print(f"   → STEP2_SKIP_TRAINING di-override: training akan lanjut dari "
          f"epoch {STEP2_RESUME_EPOCH + 1}.")
"""),
    (("""5e. Training Step 1 BERT-CRF""", """optimizer_1.step()"""),
     """require_vars("step_stage", "STEP1_SKIP_TRAINING")

if STEP1_SKIP_TRAINING:
    print("⏩ 5e dilewati — training Step 1 tidak dijalankan (cache hit).")
    print(f"   Micro-F1 terbaik tersimpan: {best_step1_f1 * 100:.2f}% (epoch {best1_epoch})")
else:
    require_vars("model_step1", "optimizer_1", "train_loader_1", "eval_loader_1")
    with step_stage(f"5e. Training Step 1 BERT-CRF — {NUM_EPOCHS} epoch pada {device}",
                    NUM_EPOCHS) as st:
        # ── Resume State ─────────────────────────────────────────────────────
        step1_resume_json = os.path.join(session_dirs["logs"], "step1_resume.json")
        start_epoch    = 1
        best_step1_f1  = 0.0
        best1_epoch    = 1
        step1_history  = []
        epochs_since_best_1 = 0  # Counter untuk early stopping
        early_stopped_step1 = False  # Flag apakah training berhenti karena early stopping

        _resume_ep = globals().get("STEP1_RESUME_EPOCH", 0)
        if _resume_ep > 0 and not FORCE_RETRAIN_STEP1:
            _epoch_ckpt_r = os.path.join(
                session_dirs["checkpoints"], f"step1_epoch_{_resume_ep}")
            _model_path_r = os.path.join(_epoch_ckpt_r, "pytorch_model.bin")
            _opt_path_r   = os.path.join(_epoch_ckpt_r, "optimizer.pt")
            try:
                model_step1.load_state_dict(
                    torch.load(_model_path_r, map_location=device))
                st.note(f"✅ Bobot model direstorasi dari epoch {_resume_ep}")
                if os.path.exists(_opt_path_r):
                    optimizer_1.load_state_dict(
                        torch.load(_opt_path_r, map_location="cpu"))
                    st.note(f"✅ Optimizer state direstorasi dari epoch {_resume_ep}")
                else:
                    st.note(f"⚠️  optimizer.pt tidak ada — optimizer mulai baru "
                            f"(bobot model tetap dari epoch {_resume_ep})")
                _rj_r = json.load(open(step1_resume_json, encoding="utf-8"))
                step1_history = _rj_r.get("history", [])
                best_step1_f1 = float(_rj_r.get("best_micro_f1", 0.0))
                best1_epoch   = int(_rj_r.get("best_epoch", 1))
                start_epoch   = _resume_ep + 1
                st.step(f"♻️  Resume dari epoch {_resume_ep} → mulai epoch {start_epoch} "
                        f"| best F1 sejauh ini: {best_step1_f1 * 100:.2f}% "
                        f"(epoch {best1_epoch})")
            except Exception as _load_err:
                st.note(f"❌ Gagal load resume checkpoint: {_load_err}. "
                        f"Training dimulai dari awal (epoch 1).")
                start_epoch   = 1
                best_step1_f1 = 0.0
                best1_epoch   = 1
                step1_history = []
        else:
            st.step("Memulai training baru dari epoch 1")
        # ─────────────────────────────────────────────────────────────────────

        epoch_bar = tqdm(range(start_epoch, NUM_EPOCHS + 1), desc="Step 1 epoch",
                         unit="epoch", initial=start_epoch - 1, total=NUM_EPOCHS)
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
                epochs_since_best_1 = 0  # Reset counter early stopping
                torch.save(model_step1.state_dict(), step1_bin)
                model_step1.config.to_json_file(os.path.join(step1_ckpt, "config.json"))
                tokenizer.save_vocabulary(step1_ckpt)
                st.note(f"🔥 Checkpoint terbaik diperbarui → {step1_ckpt}")
            else:
                epochs_since_best_1 += 1  # Increment counter early stopping

            # ── Rolling epoch checkpoint (resume per-epoch) ───────────────────
            _epoch_ckpt_dir = os.path.join(
                session_dirs["checkpoints"], f"step1_epoch_{epoch}")
            os.makedirs(_epoch_ckpt_dir, exist_ok=True)
            torch.save(model_step1.state_dict(),
                       os.path.join(_epoch_ckpt_dir, "pytorch_model.bin"))
            torch.save(optimizer_1.state_dict(),
                       os.path.join(_epoch_ckpt_dir, "optimizer.pt"))
            st.note(f"💾 Rolling checkpoint epoch {epoch} disimpan")

            # Hapus rolling checkpoint epoch sebelumnya (hemat storage)
            _prev_epoch_dir = os.path.join(
                session_dirs["checkpoints"], f"step1_epoch_{epoch - 1}")
            if epoch > start_epoch and os.path.isdir(_prev_epoch_dir):
                shutil.rmtree(_prev_epoch_dir, ignore_errors=True)
                st.note(f"🗑️  Rolling checkpoint epoch {epoch - 1} dihapus")

            # ── Early stopping check ──────────────────────────────────────────
            if (PATIENCE > 0 and epoch >= MIN_EPOCHS_BEFORE_STOP and 
                epochs_since_best_1 >= PATIENCE):
                st.note(f"⏹️ Early stopping: F1 tidak membaik selama {PATIENCE} epoch "
                        f"(terbaik di epoch {best1_epoch}, F1 {best_step1_f1 * 100:.2f}%)")
                early_stopped_step1 = True
                break
            # ─────────────────────────────────────────────────────────────────

            # Update resume JSON setiap akhir epoch
            with open(step1_resume_json, "w", encoding="utf-8") as _rjfw:
                json.dump({
                    "last_completed_epoch": epoch,
                    "total_epochs": NUM_EPOCHS,
                    "best_micro_f1": best_step1_f1,
                    "best_epoch": best1_epoch,
                    "history": step1_history,
                    "early_stopped": early_stopped_step1,
                    "stopped_at_epoch": epoch if early_stopped_step1 else None,
                    "saved_at": datetime.now().isoformat(),
                }, _rjfw, indent=2)
            # ─────────────────────────────────────────────────────────────────

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

        # Hapus rolling checkpoint setelah training selesai penuh
        _last_rolling_dir = os.path.join(
            session_dirs["checkpoints"], f"step1_epoch_{NUM_EPOCHS}")
        if os.path.isdir(_last_rolling_dir):
            shutil.rmtree(_last_rolling_dir, ignore_errors=True)
            st.note(f"🗑️  Rolling checkpoint epoch final dihapus (training selesai penuh)")

        if early_stopped_step1:
            print(f"⏹️ Training berhenti (early stopping) di epoch {epoch}. "
                  f"Micro-F1 terbaik {best_step1_f1 * 100:.2f}% pada epoch {best1_epoch}.", 
                  flush=True)
        else:
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
        "early_stopped": globals().get("early_stopped_step1", False),
        "stopped_at_epoch": epoch if globals().get("early_stopped_step1", False) else None,
        "best_micro_f1_pct": round(_best_f1_1 * 100, 2),
        "best_row": _best_row1,
        "history": globals().get("step1_history", []),
        "checkpoint": step1_ckpt,
        "csv": step1_csv,
        "saved_at": datetime.now().isoformat(),
    }, _jf, indent=2)
print(f"🧾 Ringkasan run Step 1 (termasuk TP/FP/FN per epoch) → {step1_run_json}")"""),
    (("""8e. Training Step 2 Category-Sentiment""", """optimizer_2.step()"""),
     """require_vars("step_stage", "STEP2_SKIP_TRAINING")

if STEP2_SKIP_TRAINING:
    print("⏩ 8e dilewati — training Step 2 tidak dijalankan (cache hit).")
    print(f"   Micro-F1 terbaik tersimpan: {best_step2_f1 * 100:.2f}% (epoch {best2_epoch})")
else:
    require_vars("model_step2", "optimizer_2", "train_loader_2", "eval_loader_2")
    with step_stage(f"8e. Training Step 2 Category-Sentiment — {NUM_EPOCHS} epoch pada {device}",
                    NUM_EPOCHS) as st:
        # ── Resume State ─────────────────────────────────────────────────────
        step2_resume_json = os.path.join(session_dirs["logs"], "step2_resume.json")
        start_epoch2   = 1
        best_step2_f1  = 0.0
        best2_epoch    = 1
        step2_history  = []
        epochs_since_best_2 = 0  # Counter untuk early stopping
        early_stopped_step2 = False  # Flag apakah training Step 2 berhenti karena early stopping

        _resume_ep2 = globals().get("STEP2_RESUME_EPOCH", 0)
        if _resume_ep2 > 0 and not FORCE_RETRAIN_STEP2:
            _epoch_ckpt_r2 = os.path.join(
                session_dirs["checkpoints"], f"step2_epoch_{_resume_ep2}")
            _model_path_r2 = os.path.join(_epoch_ckpt_r2, "pytorch_model.bin")
            _opt_path_r2   = os.path.join(_epoch_ckpt_r2, "optimizer.pt")
            try:
                model_step2.load_state_dict(
                    torch.load(_model_path_r2, map_location=device))
                st.note(f"✅ Bobot model Step 2 direstorasi dari epoch {_resume_ep2}")
                if os.path.exists(_opt_path_r2):
                    optimizer_2.load_state_dict(
                        torch.load(_opt_path_r2, map_location="cpu"))
                    st.note(f"✅ Optimizer state Step 2 direstorasi dari epoch {_resume_ep2}")
                else:
                    st.note(f"⚠️  optimizer.pt tidak ada — optimizer Step 2 mulai baru "
                            f"(bobot model tetap dari epoch {_resume_ep2})")
                _rj_r2 = json.load(open(step2_resume_json, encoding="utf-8"))
                step2_history = _rj_r2.get("history", [])
                best_step2_f1 = float(_rj_r2.get("best_micro_f1", 0.0))
                best2_epoch   = int(_rj_r2.get("best_epoch", 1))
                start_epoch2  = _resume_ep2 + 1
                st.step(f"♻️  Resume Step 2 dari epoch {_resume_ep2} → mulai epoch {start_epoch2} "
                        f"| best F1 sejauh ini: {best_step2_f1 * 100:.2f}% "
                        f"(epoch {best2_epoch})")
            except Exception as _load_err2:
                st.note(f"❌ Gagal load resume checkpoint Step 2: {_load_err2}. "
                        f"Training dimulai dari awal (epoch 1).")
                start_epoch2  = 1
                best_step2_f1 = 0.0
                best2_epoch   = 1
                step2_history = []
        else:
            st.step("Memulai training Step 2 baru dari epoch 1")
        # ─────────────────────────────────────────────────────────────────────

        epoch_bar = tqdm(range(start_epoch2, NUM_EPOCHS + 1), desc="Step 2 epoch",
                         unit="epoch", initial=start_epoch2 - 1, total=NUM_EPOCHS)
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
                    epochs_since_best_2 = 0  # Reset counter early stopping
                else:
                    epochs_since_best_2 += 1  # Increment counter early stopping
                torch.save(model_step2.state_dict(), step2_bin)
                model_step2.config.to_json_file(os.path.join(step2_ckpt, "config.json"))
                tokenizer.save_vocabulary(step2_ckpt)
                st.note(f"🔥 Checkpoint diperbarui (epoch {epoch}, F1 {val_f1 * 100:.2f}%) → {step2_ckpt}")
            else:
                epochs_since_best_2 += 1  # Increment counter early stopping

            # ── Rolling epoch checkpoint (resume per-epoch) ───────────────────
            _epoch_ckpt_dir2 = os.path.join(
                session_dirs["checkpoints"], f"step2_epoch_{epoch}")
            os.makedirs(_epoch_ckpt_dir2, exist_ok=True)
            torch.save(model_step2.state_dict(),
                       os.path.join(_epoch_ckpt_dir2, "pytorch_model.bin"))
            torch.save(optimizer_2.state_dict(),
                       os.path.join(_epoch_ckpt_dir2, "optimizer.pt"))
            st.note(f"💾 Rolling checkpoint Step 2 epoch {epoch} disimpan")

            # Hapus rolling checkpoint epoch sebelumnya (hemat storage)
            _prev_epoch_dir2 = os.path.join(
                session_dirs["checkpoints"], f"step2_epoch_{epoch - 1}")
            if epoch > start_epoch2 and os.path.isdir(_prev_epoch_dir2):
                shutil.rmtree(_prev_epoch_dir2, ignore_errors=True)
                st.note(f"🗑️  Rolling checkpoint Step 2 epoch {epoch - 1} dihapus")

            # ── Early stopping check ──────────────────────────────────────────
            if (PATIENCE > 0 and epoch >= MIN_EPOCHS_BEFORE_STOP and 
                epochs_since_best_2 >= PATIENCE):
                st.note(f"⏹️ Early stopping: F1 Step 2 tidak membaik selama {PATIENCE} epoch "
                        f"(terbaik di epoch {best2_epoch}, F1 {best_step2_f1 * 100:.2f}%)")
                early_stopped_step2 = True
                break
            # ─────────────────────────────────────────────────────────────────

            # Update resume JSON setiap akhir epoch
            with open(step2_resume_json, "w", encoding="utf-8") as _rjfw2:
                json.dump({
                    "last_completed_epoch": epoch,
                    "total_epochs": NUM_EPOCHS,
                    "best_micro_f1": best_step2_f1,
                    "best_epoch": best2_epoch,
                    "history": step2_history,
                    "early_stopped": early_stopped_step2,
                    "stopped_at_epoch": epoch if early_stopped_step2 else None,
                    "saved_at": datetime.now().isoformat(),
                }, _rjfw2, indent=2)
            # ─────────────────────────────────────────────────────────────────

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

        # Hapus rolling checkpoint setelah training selesai penuh
        _last_rolling_dir2 = os.path.join(
            session_dirs["checkpoints"], f"step2_epoch_{NUM_EPOCHS}")
        if os.path.isdir(_last_rolling_dir2):
            shutil.rmtree(_last_rolling_dir2, ignore_errors=True)
            st.note(f"🗑️  Rolling checkpoint Step 2 epoch final dihapus (training selesai penuh)")

        if not os.path.exists(step2_bin):
            torch.save(model_step2.state_dict(), step2_bin)
            model_step2.config.to_json_file(os.path.join(step2_ckpt, "config.json"))
            tokenizer.save_vocabulary(step2_ckpt)
            st.note(f"💾 Checkpoint final Step 2 disimpan → {step2_ckpt}")

        if early_stopped_step2:
            print(f"⏹️ Training Step 2 berhenti (early stopping) di epoch {epoch}. "
                  f"Micro-F1 terbaik {best_step2_f1 * 100:.2f}% pada epoch {best2_epoch}.", 
                  flush=True)
        else:
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
        "early_stopped": globals().get("early_stopped_step2", False),
        "stopped_at_epoch": epoch if globals().get("early_stopped_step2", False) else None,
        "best_row": _best_row2,
        "history": globals().get("step2_history", []),
        "checkpoint": step2_ckpt,
        "csv": step2_csv,
        "sumber_kandidat": "step1" if globals().get("pakai_1st", True) else "gold",
        "saved_at": datetime.now().isoformat(),
    }, _jf, indent=2)
print(f"🧾 Ringkasan run Step 2 (termasuk TP/FP/FN per epoch) → {step2_run_json}")"""),
]


def main():
    # 1. V2 dibangun ulang dulu agar V4 berdiri di atas V2 mutakhir. Generator V2
    #    menulis ke repo upstream, jadi tidak ada perubahan V4 yang bocor ke sana.
    V2.main()

    nb = json.load(io.open(SRC_V2, encoding="utf-8"))
    cells = nb["cells"]

    n_fix = patch_shell_magic_cells(cells)
    if n_fix:
        print(f"  [patch] {n_fix} sel V2 dengan shell-magic berindentasi → os.system")

    _, info = apply_patches(cells)
    print(f"  [patch] {info['n_sel_tokenized_base']} sel dialihkan ke tokenized_base")

    with io.open(DST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")

    n_code = sum(1 for c in cells if c["cell_type"] == "code")
    digest = hashlib.md5(open(DST, "rb").read()).hexdigest()
    print(f"{os.path.basename(DST)} ditulis: {len(cells)} sel ({n_code} kode). MD5 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
