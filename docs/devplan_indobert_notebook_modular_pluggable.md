# Dev Plan — Notebook IndoBERT Modular, Pluggable, Dinamis (D5 dari PRD)

> Dokumen perencanaan sebelum implementasi notebook.
> Sumber utama: `docs/0004_prd_implementasi_indobert_acos_28082026_0638.md`
> Keputusan pengguna: **Full pipeline + gates (PRD D5)** · **Adapter runtime + file patch opsional** · **Mendukung LANG=en & LANG=id (default en)**

---

## 1. Tujuan

Membuat notebook `.ipynb` **modular, pluggable, dinamis** untuk memigrasikan pipeline
ACOS 2-tahap (co-extraction → category-sentiment classification) dari
`bert-base-uncased` ke **IndoBERT**, yang dapat dijalankan:

- **Google Colab** — target utama, dengan akses & persistensi di **`/content/drive/MyDrive/ACOS-IndoBERT`**.
- **Lokal** (Windows / Linux, tanpa hardcode path) — mode sekunder untuk scaffolding/uji ringan.

Notebook ini adalah deliverable **D5** dari PRD, mencakup pula deliverable D1–D4
(adapter, taksonomi ID, generator tokenized_data, verify gates) sebagai sel-sel/fungsi
yang dapat dijalankan.

### 1.1 Keputusan lokasi (WAJIB — jangan diubah tanpa persetujuan)

> **Poin penting pengguna: seluruh implementasi IndoBERT dipisahkan ke folder lain di LUAR `ACOS-ASLI` —
> termasuk scaffolding kode — dan terpisah dari repositori pipeline English.**

- **Root penyimpanan aktif (semua hasil, sistem file runtime):** `/content/drive/MyDrive/ACOS-IndoBERT` (Colab).
  Di sinilah: `backbones/` (IndoBERT hasil D1), `results/` (session_dirs, checkpoint, `pipeline_state.pkl`,
  `master_metrics.json`, `session_manifest.json`), dan `tokenized_data/` regenerasi.
- **Folder kerja lokal terpisah (di luar repo):** semua scaffolding — notebook `.ipynb`, adapter, taksonomi,
  generator, gates — dibuat di folder terpisah di luar `ACOS-ASLI`, mis. `D:\laragon\www\ACOS-IndoBERT\`
  (atau lokasi yang Anda tentukan). Repo `ACOS-ASLI` **tidak menerima scaffolding maupun artefak run**.
- **Folder repo `D:\laragon\www\ACOS-ASLI`:** dipakai **hanya sebagai referensi baca** (membaca `modeling.py`,
  `colab_utils.py`, dll.) dan tempat dokumen `docs/devplan_*.md`. Tidak ada perubahan kode, tidak ada scaffolding,
  tidak ada checkpoint/backbones/hasil training yang ditulis ke sini.
- **Alasan:** ACOS-ASLI adalah basis pipeline English asli; IndoBERT adalah eksperimen migrasi terpisah dan
  harus berjalan di sandbox-nya sendiri agar tidak mengotori repo / mengganggu pipeline yang sudah ada.
- **Implementasi sistematis:** bukan hanya lokasi file — seluruh variabel `base_project_dir`, `save_dir`,
  `extract_dir` di notebook default ke root kerja terpisah (Colab `ACOS-IndoBERT`, atau folder lokal terpisah),
  dan notebook **menolak** menulis artefak maupun scaffolding ke `ACOS-ASLI` bila dijalankan lokal.

---

## 2. Prinsip desain

| Prinsip | Penerapan |
|---|---|
| **Modular** | Setiap tahap = satu sel dengan fungsi self-contained; helper logic dibundel dalam satu sel "kernel modul" (registry, adapter, gates). Bisa dijalankan sel-per-sel tanpa duplikasi. |
| **Pluggable** | 3 registry dinamis dikontrol dari satu sel konfigurasi: model backbone, domain/taksonomi, dan sumber data (lihat §3). |
| **Dinamis** | Deteksi lingkungan otomatis (lokal vs Colab), path tanpa hardcode, state checkpoint + resume, manifest per-tahap. |
| **Aman untuk upstream** | Default memakai **runtime monkey-patch** — tidak mengubah file upstream. Opsi `APPLY_PERMANENT_PATCH` untuk menulis patch permanen bila diinginkan. |

---

## 3. Registry pluggable

### 3.1 `MODEL_REGISTRY` (backbone)
| Key | Model | URL HF (`resolve/main`) | Rekey? | Status |
|---|---|---|---|---|
| `"indobert"` | `indobenchmark/indobert-base-p1` | config.json, pytorch_model.bin, vocab.txt | ya (tambah prefix `bert.`) | **default target** |
| `"nusabert"` | `LazarusNLP/NusaBERT-base` | model.safetensors (tanpa pytorch_model.bin) | — | pembanding tahap-2 (perlu konversi) |
| `"bert-en"` | `bert-base-uncased` | config.json, pytorch_model.bin, vocab.txt | tidak | kontrol / Gate 2 English |

Satu parameter `BACKBONE` mengganti seluruh alur (adapter → gates → training).

### 3.2 `DOMAIN_REGISTRY` (lang/taksonomi)
| LANG | domain_type | Taksonomi | num_labels Step 2 |
|---|---|---|---|
| `en` | `rest16` | 13 kategori English (upstream) | 39 |
| `id` | `restobookID` | 13 kategori restoran Indonesia (§4, D2) | 39 |

Sentimen tetap `['0','1','2']` → `label_list[0]` = 39 combo, **head tidak berubah dimensi**
sehingga angka bisa dibandingkan langsung dengan baseline English rest16.

### 3.3 `DATA_REGISTRY` (lingkungan)
- **Colab (target utama)** → root & simpan di **`/content/drive/MyDrive/ACOS-IndoBERT`** (bukan `/ACOS`),
  mount otomatis bila ada `google.colab`.
- **Lokal (sekunder / scaffolding)** → folder kerja terpisah di luar repo, mis. `D:\laragon\www\ACOS-IndoBERT\`:
  scaffolding kode + hasil latihan lokal semuanya di sini. Bila `cwd` terdeteksi berada di dalam `ACOS-ASLI`,
  notebook **refuse** dan mengarahkan ke folder kerja terpisah — **repo `ACOS-ASLI` tidak menerima scaffolding
  maupun artefak run** (lihat §1.1).
- Dicatat ke `paths.json` + `session_manifest.json` tiap tahap.

---

## 4. Deliverable & file

Semua file scaffolding (notebook + kode pendukung) dibuat di **folder kerja terpisah di luar repo**,
mis. `D:\laragon\www\ACOS-IndoBERT\`, dan siap di-upload ke Colab.

File scaffolding:
- `00_IndoBERT_Migration_Modular_Pluggable.ipynb` — notebook utama (D5), di-upload & dijalankan di Colab.
- Kode pendukung (adapter/taksonomi/generator/gates) sebagai sel/fungsi di dalam notebook atau file `.py`
  terpisah di folder yang sama.

Sesuai §1.1: **tidak ada scaffolding maupun artefak runtime yang ditulis ke repo `ACOS-ASLI`**.

| # | Bagian (dari PRD) | Implementasi dalam notebook |
|---|---|---|
| D1 | Adapter checkpoint | `prepare_indobert(model_name, target_dir)` — unduh, rekey prefix `bert.`, simpan ulang, lapor key & vocab. Cache di `${save_dir}/backbones/<model>`. |
| D2 | Taksonomi Indonesia | `RESTORAN_ID` 13 kategori + `get_labels_id()`; dipakai saat `LANG='id'`. |
| D3 | Generator tokenized_data | `build_tokenized_data(tokenizer, in_path, out_path)` tokenizer-agnostik; remap span; sisip `[UNK]`; tulis `_build_report.json`. |
| D4 | Verify gates | 3 gate (§6). |
| D5 | Notebook utama | Notebook utuh: setup → adapter → gates → train S1 → pair → train S2 → eval → infer → ringkasan. |

---

## 5. Runtime adapter (monkey-patch) — menjawab bloker PRD

PRD §2.1 & §6 menemukan:
1. `modeling.py:1545` hardcode `nn.Linear(768, ...)` dan `:1608` `nn.Linear(768*2, ...)`
   → harus `config.hidden_size` / `config.hidden_size*2`.
2. Loader `load()` (`modeling.py:745-755`) logging `missing_keys`/`unexpected_keys`
   di-**comment out** → risiko bobot termuat **senyap** (tanpa warning).
3. `bert_utils/tokenization.py:127` `ids.append(self.vocab[token])` → `KeyError` bila OOV,
   tidak ada fallback `[UNK]`.

Patch runtime (scoped, tanpa ubah file):
- Ganti `768` → `config.hidden_size` pada dua posisi saat instantiasi (via replace string
  pada source class sebelum eksekusi, atau wrapper).
- Buka kembali / aktifkan logging `missing_keys`.
- Patch `BertTokenizer.convert_tokens_to_ids` → `self.vocab.get(token, self.vocab['[UNK]'])`.

**Opsional `APPLY_PERMANENT_PATCH`** (default `False`): bila `True`, sel khusus menulis
patch permanen ke file upstream sesuai rekomendasi PRD tabel §5.

---

## 6. Gate verifikasi (wajib)

### Gate 1 — bobot IndoBERT benar-benar termuat (paling penting)
1. Muat model via `from_pretrained(target_dir hasil D1)`.
2. Ambil `bert.embeddings.word_embeddings.weight` dari state_dict pasca-rekey.
3. Bandingkan numerik (`torch.allclose`) dengan `model.bert.embeddings.word_embeddings.weight`.
4. Ulangi untuk `encoder.layer.0.attention.self.query.weight` dan `encoder.layer.11.output.dense.weight`.
5. Assert tidak ada key `bert.*` di `missing_keys`.
LULUS bila ketiganya identik; GAGAL bila salah satu berbeda.

### Gate 2 — regenerasi `tokenized_data` konsisten
1. Jalankan D3 memakai vocab `bert-base-uncased` pada data English.
2. Bandingkan output dengan `tokenized_data/*_quad_bert.tsv` yang ada di repo.
LULUS bila identik atau selisih terjelaskan (mis. hanya baris ber-`[UNK]`).

### Gate 3 — end-to-end tanpa crash
1. Subset kecil (100 train / 20 dev / 20 test), 1 epoch.
2. `run_step1` → pairs → `run_step2` → eval.
LULUS bila selesai tanpa exception dan eval mengeluarkan angka.

---

## 7. Alur cell (target ~30 sel: markdown + code)

1. **MD** judul & roadmap.
2. **MD+code** Setup: mount Drive (Colab), GPU diagnosis, install deps (torchcrf, transformers ringan utk adapter, dll).
3. **MD+code** Path/registry dinamis: `IS_COLAB`, `base_project_dir`, `sys.path`, import `colab_utils` + modul proyek.
4. **MD+code** Konfigurasi pluggable: `BACKBONE`, `LANG`, `DOMAIN_TYPE`, hyperparams, registry, seeding, `setup_timestamped_run_dir`.
5. **MD+code** D1 Adapter IndoBERT.
6. **MD+code** Runtime adapter (monkey-patch) + sel patch permanen opsional.
7. **MD+code** D2 Taksonomi ID (pluggable domain).
8. **MD+code** Gate 1 — bobot termuat.
9. **MD+code** D3 Generator tokenized_data + Gate 2 (English).
10. **MD+code** EDA.
11. **MD+code** State saver (`pipeline_state.pkl` expanded) + recovery.
12. **MD+code** Step 1 training (BERT-CRF) → checkpoint + `pred4pipeline.txt`.
13. **MD+code** Candidate pair bridge → `${DOMAIN}_test_pair_1st.tsv`.
14. **MD+code** Step 2 training (patch KeyError bila LANG=id) → checkpoint.
15. **MD+code** Gate 3 — end-to-end subset kecil.
16. **MD+code** Final eval (`pair_eval` + `SubtaskMetricCapture`, breakdown eksplisit/implisit `measureQuad_imp`), `master_metrics.json`.
17. **MD+code** Live inference dua-tahap.
18. **MD+code** Ringkasan artefak + manifest final.

---

## 8. Hyperparameter awal

| Parameter | Step 1 | Step 2 |
|---|---|---|
| `max_seq_length` | 128 | 128 |
| `train_batch_size` | 24 | 16 |
| `learning_rate` | 2e-5 | 5e-5 |
| `num_train_epochs` | 15 (base) / 1 (Gate 3) | 15 (base) / 1 (Gate 3) |
| `do_lower_case` | ya | ya (IndoBERT p1 uncased) |

`do_lower_case` wajib aktif: `tokenizer_config.json` IndoBERT kosong (`{}`) — tanpa ini
token bermodal besar jadi `[UNK]` dalam jumlah besar.

---

## 9. Metrik & pelaporan

- `eval_metrics.py` dipakai apa adanya (model-agnostik).
- `measureQuad` → metrik quadruple; `measureQuad_imp` + `getTextType` → breakdown
  eksplisit vs implisit (wajib dilaporkan, bagian tersulit anotasi).
- `pair_eval` → mutu pasangan Step 1 terpisah.
- `master_metrics.json` + `session_manifest.json` di akhir.
- Tidak menetapkan target angka F1 (belum ada dataset Indonesia); rest16 English sebagai
  sanity-check pipeline.

---

## 10. Lingkungan eksekusi

- **Utama: Google Colab.** Eksekusi, training, dan semua gate dijalankan di Colab; root aktif
  `/content/drive/MyDrive/ACOS-IndoBERT` (persistensi antar sesi). Kode `.py`/`.ipynb` scaffolding
  tinggal di-upload dari lokal ke Colab.
- **Lokal (Windows)**: hanya untuk membangun/uji ringan scaffolding; tidak ada paket ML yang dibutuhkan
  untuk menulis file. Semua artefak runtime lokal disimpan di luar repo `ACOS-ASLI` (lihat §1.1 & §3.3).
- Repo lokal `ACOS-ASLI` dipakai **hanya sebagai referensi baca** (membaca `modeling.py`, `colab_utils.py`, dll.)
  dan sebagai tempat `docs/devplan_*.md` — **tanpa perubahan pada kode atau artefak run**.

---

## 11. Validasi setelah implementasi

1. Struktur JSON notebook valid (nbformat 4).
2. Setiap code cell lolos `compile()` (tidak ada SyntaxError).
3. Logika registry / adapter / gates diuji dengan skrip Python ringan (tanpa torch penuh bila memungkinkan).

---

## 12. Catatan / risiko

- `NusaBERT-base` hanya rilis `model.safetensors` → jalur legacy `torch.load` tak bisa baca;
  jadikan pembanding tahap-2.
- Rekey wajib: loader legacy menetapkan `start_prefix=''` karena kelas punya `self.bert`,
  dan membutuhkan key `bert.*` — tanpa rekey, bobot encoder termuat acak secara senyap.
- Dataset Indonesia belum ada (bloker F4) → notebook divalidasi pada data English rest16
  sekarang; `LANG=id` siap saat dataset tersedia.
