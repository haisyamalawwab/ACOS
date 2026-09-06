# 025 — Dev Log: Beban Pelatihan di T4 — BERT vs IndoBERT (dua backbone)

> Tanggal: 5 September 2026
> Status: **analisis desain** — belum ada pelatihan dijalankan di mesin ini
> Koreksi: revisi dari versi sebelumnya yang keliru membandingkan "base vs
> fine-tuned" dalam satu model. Perbandingan yang benar adalah **dua backbone
> berbeda**: `bert-base-uncased` (baseline) vs `indobert-base-p1` (target).

---

## 1. Dua backbone yang dibandingkan

| | BERT (baseline) | IndoBERT (target) |
|---|---|---|
| HF ID | `bert-base-uncased` | `indobenchmark/indobert-base-p1` |
| Bahasa | Inggris | Indonesia |
| Vocab (`config.vocab_size`) | 30.522 | 50.000 |
| Token terpakai di `vocab.txt` | 30.522 | 30.521 |
| Arsitektur encoder | 12 layer, 768 hidden, 12 head | **sama persis** |

Keduanya arsitektur BERT-base. Encoder (12 transformer layer) identik ukurannya.
Perbedaannya hanya di lapisan embedding, karena `vocab_size` IndoBERT lebih besar.

---

## 2. Dampak pada beban pelatihan

Perbedaan `vocab_size` hanya membengkakkan **lapisan embedding** (± 15 M parameter
tambahan), bukan encoder. Karena encoder identik dan justru bagian yang paling banyak
komputasi, perbedaan beban per step di T4 **kecil** — order ± 12–15 % total parameter,
tetapi dampak nyata pada waktu step lebih kecil dari itu.

Karena itu, untuk durasi di T4:

- BERT dan IndoBERT dilatih dengan **strategi yang sama** (full fine-tune di V4),
  sehingga kecepatan per epoch-nya **hampir sama**.
- "Lama" yang dirasakan **bukan** karena IndoBERT vs BERT, melainkan karena strategi
  full fine-tune 12 layer + 15 epoch (lihat §3).

---

## 3. Yang sebenarnya menentukan lama di T4

Faktor penentu durasi, terlepas dari backbone:

| Faktor | Pengaruh |
|---|---|
| Full fine-tune (train seluruh encoder) | terbesar — 12 layer di-backprop |
| `NUM_EPOCHS = 15` (paper 30) | linier terhadap total waktu |
| `STEP1/2_BATCH_SIZE` | memengaruhi jumlah step & VRAM |
| fp16 + gradient accumulation | hemat VRAM, percepat step |

Tuas penurun beban terbesar untuk Colab Free adalah **freeze encoder** (train head
saja), bukan mengganti backbone. Mengganti BERT ↔ IndoBERT tidak menyelesaikan
masalah durasi, karena keduanya sama-sama full-train encoder.

---

## 4. Kejujuran

- Angka ±15 M parameter tambahan adalah estimasi dari selisih `vocab_size`
  (50.000 vs 30.522), bukan hasil ukur di mesin ini.
- Tidak ada pelatihan dijalankan di sini; mesin lokal tanpa torch/transformers.
- Kesimpulan inti: perbedaan beban BERT vs IndoBERT di T4 kecil (arsitektur sama,
  beda hanya embedding); yang menentukan durasi adalah strategi training, bukan
  pilihan backbone.
