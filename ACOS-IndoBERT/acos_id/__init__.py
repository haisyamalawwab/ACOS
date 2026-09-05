"""Lapisan Indonesia untuk pipeline ACOS dua tahap (Step 1 co-extraction,
Step 2 category-sentiment) dengan backbone IndoBERT.

Paket ini tinggal di folder terpisah `ACOS-IndoBERT/` dan tidak mengubah satu
berkas pun di repo pipeline Inggris `ACOS-ASLI/`: seluruh perbedaan Indonesia
dipasang lewat patch runtime (`taxonomy.patch_processor_labels`) atau lewat
berkas data baru yang dihasilkan generator. Konsekuensinya pipeline Inggris
rest16/laptop tetap bisa dijalankan sebagai kontrol.

Tata letak folder:

    ACOS-IndoBERT/
      acos_id/          paket ini
      data/Apps-ACOS/   dataset Indonesia (mentah + hasil konversi)
      tokenized_data/   keluaran generator, terpisah dari milik upstream
      backbones/        checkpoint IndoBERT hasil rekey + vocab
      notebooks/        generator + .ipynb V4
      build/            skrip verifikasi & keluaran sementara
      results/          folder sesi bertimestamp (checkpoint, csv, md, plots, logs)

Repo `ACOS-ASLI/` di folder induk dipakai **hanya untuk dibaca**: modul
`Extract-Classify-ACOS/` (modeling, tokenizer, processor, metrik) dan
`data/Restaurant-ACOS/` untuk gate 2.

Modul:

- `taxonomy` — 13 kategori Apps-ACOS, label sekuens, gate vs `label_maps.json`
- `checkpoint` — adapter checkpoint IndoBERT (rekey prefiks `bert.`) + gate bobot
- `build_acos` — konversi `data/Apps-ACOS/processed/*` → format ACOS mentah
- `tokenize_data` — generator `tokenized_data/*_quad_bert.tsv` + `*_pair.tsv`
- `eda` — EDA Indonesia dengan kontrak keluaran identik `colab_utils`
- `selftest` — 5 gate torch-free + Gate 1

Semua modul torch-free kecuali `checkpoint`, yang memang bertugas menyentuh
state_dict.
"""

__all__ = ["taxonomy", "checkpoint", "build_acos", "tokenize_data", "eda", "selftest"]

__version__ = "0.2.0"
