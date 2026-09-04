"""Lapisan Indonesia untuk pipeline ACOS dua tahap (Step 1 co-extraction,
Step 2 category-sentiment) dengan backbone IndoBERT.

Paket ini berdiri **di samping** `Extract-Classify-ACOS/` dan tidak mengubah
satu berkas pun di sana: seluruh perbedaan Indonesia dipasang lewat patch
runtime (`taxonomy.patch_processor_labels`) atau lewat berkas data baru yang
dihasilkan generator. Konsekuensinya pipeline Inggris rest16/laptop tetap bisa
dijalankan sebagai kontrol di notebook yang sama.

Modul:

- `taxonomy`  — 13 kategori Apps-ACOS, label sekuens, gate vs `label_maps.json`
- `checkpoint` — adapter checkpoint IndoBERT (rekey prefix `bert.`) + gate bobot
- `build_acos` — konversi `data/Apps-ACOS/processed/*` → format ACOS mentah
- `tokenize_data` — generator `tokenized_data/*_quad_bert.tsv` + `*_pair.tsv`

Semua modul torch-free kecuali `checkpoint`, yang memang bertugas menyentuh
state_dict.
"""

__all__ = ["taxonomy", "checkpoint", "build_acos", "tokenize_data"]

__version__ = "0.1.0"
