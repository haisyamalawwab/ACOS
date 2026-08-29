# Laporan Pengembangan: Analisis & Solusi Error `KeyError: '##m !'` pada Step 2 Training Loop

**Nomor Dokumen:** `reports/018_analisis_dan_perbaikan_error_keyerror_step2_eval_metrics_29082026_0915.md`  
**Tanggal:** 2026-08-29 09:15 WIB  
**Status:** Terselesaikan (Fixed & Verified)  
**Objek Perbaikan:**
- [`Extract-Classify-ACOS/eval_metrics.py`](file:///d:/laragon/www/ACOS-ASLI/Extract-Classify-ACOS/eval_metrics.py)
- [`notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb)
- [`notebooks/_build_staged_v2.py`](file:///d:/laragon/www/ACOS-ASLI/notebooks/_build_staged_v2.py)

---

## 1. Ringkasan Eksekutif

Pada eksekusi pipeline ACOS versi bertahap ([`00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb)) di lingkungan Google Colab, proses mengalami kegagalan (*crash*) pada sel training Step 2 (**8e: Loop Training Step 2 Category-Sentiment** / nomor eksekusi `[24]`).

Error yang terjadi adalah `KeyError: '##m !'` yang berasal dari modul evaluasi [`Extract-Classify-ACOS/eval_metrics.py`](file:///d:/laragon/www/ACOS-ASLI/Extract-Classify-ACOS/eval_metrics.py) saat menjalankan fungsi `pair_eval(..., eval_type='test')` di akhir Epoch 1.

Laporan ini mendokumentasikan akar penyebab kegagalan, analisis teknis, implementasi perbaikan pada *source code*, pembersihan struktur sel notebook, serta hasil verifikasi lokal.

---

## 2. Bukti & Jejak Error (Traceback)

Berikut adalah rekaman error dari output eksekusi sel `[24]` (cell index 45):

```text
Epoch 01: evaluasi pasangan (152 batch)...
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
/tmp/ipykernel_809/1345735022.py in <cell line: 0>()
     38             print(f"   Epoch {epoch:02d}: evaluasi pasangan ({len(eval_loader_2)} batch)...",
     39                   flush=True)
---> 40             val_res = pair_eval(epoch, args_h, logger2, tokenizer, model_step2, eval_loader_2,
     41                                 eval_gold_2, label_list_step2, device, "categorysenti",
     42                                 eval_type='test')

/content/drive/MyDrive/ACOS/Extract-Classify-ACOS/eval_metrics.py in pair_eval(_e, args, logger, tokenizer, model, dataloader, gold, label_list, device, task_name, eval_type)
    354                         cur_subs.append(cur_sub)
    355                 sub_golds[cur_key] = cur_subs
--> 356             sub_res = measureQuad_imp(sub_preds, sub_golds, text_type)
    357             subtask_name = ' '.join(index_to_name[ele] for ele in exist_index)

/content/drive/MyDrive/ACOS/Extract-Classify-ACOS/eval_metrics.py in measureQuad_imp(pred, gold, text_type)
    198 
    199     for text in pred:
--> 200         for dt in text_type[text]:
    201             cnt = 0
    202             if text in gold:

KeyError: '##m !'
```

---

## 3. Analisis Akar Masalah (Root Cause Analysis)

### 3.1 Konstruksi Kamus `text_type` vs `pred`
1. **Pembangunan `text_type`**:  
   Fungsi `getTextType(quad_golds)` di [`Extract-Classify-ACOS/eval_metrics.py`](file:///d:/laragon/www/ACOS-ASLI/Extract-Classify-ACOS/eval_metrics.py) hanya membangun indeks tipe kalimat (eksplisit-eksplisit `0`, implisit-eksplisit `1`, eksplisit-implisit `2`, implisit-implisit `3`, keseluruhan `4`) berdasarkan kunci kalimat yang ada di dalam *ground truth* (`gold`).
   
2. **Sumber Prediksi Pasangan (`pred`)**:  
   Pada Step 2 (evaluasi pipeline penuh), `eval_loader_2` dibangun dari berkas `_test_pair_1st.tsv` (yang dihasilkan dari prediksi Step 1).  
   Ketika tokenisasi BERT memecah kalimat tertentu (contoh: kalimat ulasan *"yu ##m !"* atau pecahan *subword* wordpiece), jika Step 1 menghasilkan prediksi token yang tidak sepenuhnya identik atau terpotong sebagai kunci teks terpisah seperti `'##m !'`, maka `'##m !'` akan masuk ke dalam kamus `pred`.

3. **Titik Kegagalan**:  
   Pada `measureQuad_imp`:
   ```python
   for text in pred:
       for dt in text_type[text]:  # <--- CRASH: text tidak ada di text_type
   ```
   Kode di atas secara keliru mengasumsikan bahwa **setiap teks yang ada di `pred` pasti ada di `gold` / `text_type`**.  
   Ketika teks tidak terdaftar di `gold`, pemanggilan langsung `text_type[text]` memicu `KeyError`.

---

## 4. Solusi & Perbaikan yang Diterapkan

### 4.1 Perbaikan pada Core Engine (`eval_metrics.py`)
Pada [`Extract-Classify-ACOS/eval_metrics.py`](file:///d:/laragon/www/ACOS-ASLI/Extract-Classify-ACOS/eval_metrics.py):
1. Mengubah akses `text_type[text]` menjadi `text_type.get(text, [4])`.  
   Jika `text` tidak ditemukan di *ground truth*, fungsi akan menganggapnya sebagai kategori agregat/keseluruhan (`dt=4`) dan mencatat prediksi tersebut sebagai *false positive* (`fp[4] += len(pred[text])`), tanpa melempar exception.
2. Mengamankan penulisan log `ids_to_token` pada akhir `pair_eval` menggunakan `ids_to_token.get(key, str(key))`.

```python
def measureQuad_imp(pred, gold, text_type):
    tp = [.0, .0, .0, .0, .0]
    fp = [.0, .0, .0, .0, .0]
    fn = [.0, .0, .0, .0, .0]

    for text in pred:
        target_dts = text_type.get(text, [4])
        for dt in target_dts:
            cnt = 0
            if text in gold:
                for pair in pred[text]:
                    if pair in gold[text]:
                        cnt += 1
            tp[dt] += cnt
            fp[dt] += len(pred[text])-cnt
            if text in gold:
                fn[dt] += len(gold[text])-cnt
    for text in gold:
        target_dts = text_type.get(text, [4])
        for dt in target_dts:
            if text not in pred:
                fn[dt] += len(gold[text])

    for i in range(5):
        print("tp: {}. fp: {}. fn: {}.".format(tp[i], fp[i], fn[i]))
        p = 0 if tp[i] + fp[i] == 0 else 1.*tp[i] / (tp[i] + fp[i])
        r = 0 if tp[i] + fn[i] == 0 else 1.*tp[i] / (tp[i] + fn[i])
        f = 0 if p + r == 0 else 2 * p * r / (p + r)
        print(i, ': ', {'precision':p, 'recall':r, 'micro-F1':f})
    return {'precision':p, 'recall':r, 'micro-F1':f}
```

---

### 4.2 Patch Defensif di Sel 8a Notebook
Pada sel **8a: Inisialisasi Step 2** ([`notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb) & [`notebooks/_build_staged_v2.py`](file:///d:/laragon/www/ACOS-ASLI/notebooks/_build_staged_v2.py)), ditambahkan mekanisme patch *in-memory* `_safe_measureQuad_imp` ke modul `eval_metrics`:

```python
# Patch evaluasi defensif: cegah KeyError jika pred memuat token/teks di luar gold
import eval_metrics as _em

def _safe_measureQuad_imp(pred, gold, text_type):
    tp = [.0, .0, .0, .0, .0]
    fp = [.0, .0, .0, .0, .0]
    fn = [.0, .0, .0, .0, .0]
    for text in pred:
        target_dts = text_type.get(text, [4])
        for dt in target_dts:
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
        target_dts = text_type.get(text, [4])
        for dt in target_dts:
            if text not in pred:
                fn[dt] += len(gold[text])
    for i in range(5):
        print("tp: {}. fp: {}. fn: {}.".format(tp[i], fp[i], fn[i]))
        p = 0 if tp[i] + fp[i] == 0 else 1.0 * tp[i] / (tp[i] + fp[i])
        r = 0 if tp[i] + fn[i] == 0 else 1.0 * tp[i] / (tp[i] + fn[i])
        f = 0 if p + r == 0 else 2 * p * r / (p + r)
        print(i, ': ', {'precision': p, 'recall': r, 'micro-F1': f})
    return {'precision': p, 'recall': r, 'micro-F1': f}

_em.measureQuad_imp = _safe_measureQuad_imp
st.step("eval_metrics.measureQuad_imp dipatch (defensif terhadap OOV/mismatched text)")
```

Ini memastikan notebook yang berjalan di sesi Colab yang sudah aktif tetap aman dari crash meskipun modul `eval_metrics` sudah ter-load di memori kernel sebelumnya.

---

### 4.3 Pembersihan Struktur & Builder Notebook (`_build_staged_v2.py`)
Skrip builder [`notebooks/_build_staged_v2.py`](file:///d:/laragon/www/ACOS-ASLI/notebooks/_build_staged_v2.py) diperbaiki pada bagian penggantian section:
- Menggunakan fungsi pemetaan header `find_md(prefix)` untuk mengganti seluruh blok lama Section 7, 8, dan 9 secara atomik.
- Menghilangkan sel-sel duplikat/sisa eksekusi lama.
- Total sel pada notebook akhir menjadi **72 sel terstruktur rapi (44 sel kode)**.
- Sel training Step 2 (**8e**) di-reset ke kondisi awal tanpa output error dan siap dijalankan ulang.

---

## 5. Hasil Verifikasi & Pengujian

1. **Uji Logika Algoritma `measureQuad_imp`**:
   - Dijalankan pengujian lokal dengan data buatan yang sengaja memuat kunci teks tidak terdaftar (`'##m !'`).
   - **Hasil:** Sukses tanpa KeyError. Precision, Recall, dan Micro-F1 terhitung dengan benar (Subset 4 menangani false positives).
   
2. **Uji Rebuild Idempoten**:
   - Skrip `python notebooks/_build_staged_v2.py` dieksekusi.
   - **Hasil:** Berkas `00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb` ter-generate sempurna dengan status exit 0.

3. **Status Git & Integritas File**:
   - Semua modul Python dan notebook berada dalam keadaan sinkron dan konsisten.

---

## 6. Rekomendasi Tindak Lanjut

1. **Eksekusi Lanjutan di Google Colab**:
   - Pengguna dapat langsung menjalankan notebook [`notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb`](file:///d:/laragon/www/ACOS-ASLI/notebooks/00_ACOS_Master_Pipeline_Colab_V2_STAGED.ipynb).
   - Sel **8a** akan memuat patch tokenizer dan patch evaluasi defensif.
   - Sel **8e** akan menjalankan training Step 2 hingga selesai (15 epoch) tanpa terhenti oleh `KeyError`.
2. **Evaluasi Final (Section 9)**:
   - Setelah training Step 2 selesai, sel 9a akan mengekstrak metrik 15 sub-tugas dan menyimpannya ke `master_metrics.json`.
