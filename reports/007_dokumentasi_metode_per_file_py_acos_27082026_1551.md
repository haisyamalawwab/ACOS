# Dokumentasi Metode & Teknik per File `.py` — Source Code ACOS

Tanggal: 2026-08-27
Objek: seluruh file `.py` di `Extract-Classify-ACOS/` + `colab_utils.py` + `notebooks/colab_utils.py`
Metode: pembacaan statis lengkap setiap file. Tidak dieksekusi (environment Python 3.14 tanpa `torch`).

---

## 0. Peta File & Peran per Tahap

```
┌──────────────────────────────────────────────────────────────────────┐
│                    FILE .py ACOS (per tahap)                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  [Infra]   manager.py            → pemilih GPU (fallback CPU)         │
│            file_utils.py (duplikat)→ cache & download URL              │
│            bert_utils/optimization → BertAdam + jadwal LR             │
│            bert_utils/tokenization  → BertTokenizer (WordPiece)       │
│            bert_utils/__init__.py   → (kosong)                        │
│                                                                       │
│  [Data]    run_classifier_dataset_utils.py                          │
│              → QuadProcessor / CategorySentiProcessor                 │
│              → convert_examples_to_features (step1)                  │
│              → convert_examples_to_features2nd (step2)                │
│            dataset_utils.py        → read_pair_gold (gold step2)      │
│            tokenized_data/get_1st_pairs.py → jembatan cross-product  │
│                                                                       │
│  [Model]  modeling.py (1647 baris)                                   │
│              → port pytorch_pretrained_bert (BertModel dll.)         │
│              → BertForQuadABSA (BERT + CRF + 2 implicit head)        │
│              → CategorySentiClassification (BERT + mean-pool + ML)   │
│                                                                       │
│  [Train]  run_step1.py            → CLI training step 1               │
│            run_step2.py            → CLI training step 2               │
│            run.sh                  → orchestrator 3 langkah           │
│                                                                       │
│  [Eval]   eval_metrics.py          → pred_eval / pair_eval            │
│              → measureQuad (P/R/F1)                                  │
│              → 15 subtask kombinasi elemen                          │
│              → 4 subset implicit/explicit (getTextType)             │
│                                                                       │
│  [Notebook] colab_utils.py (notebooks/ + root)                      │
│              → EDA, plotting, checkpoint, inferensi, wrapper API     │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 1. `manager.py` — GPU Manager

**Peran**: memilih GPU dengan free memory terbesar; fallback aman bila `nvidia-smi` tidak ada.

**Teknik**:
- `check_gpus()`: panggil `nvidia-smi --query-gpu=index`; `False` bila kosong/exception.
- `query_gpu()`: parse `nvidia-smi --query-gpu=index,gpu_name,memory.free,memory.total,power.draw,power.limit,utilization.gpu`.
- Fallback dummy: `[{'index':'0','gpu_name':'GPU-0','memory.free':10000,...}]` bila `nvidia-smi` gagal — skrip tidak menggantung.
- `GPUManager.auto_choice(mode=0)`: pilih GPU dengan `memory.free` terbesar via `_sort_by_memory(by_size=True)`.
- **Catatan**: dipanggil di import-time `run_step1.py`/`run_step2.py` (`gm = GPUManager(); device = gm.auto_choice()`), lalu set `CUDA_VISIBLE_DEVICES`.

**Perubahan porting (lihat laporan 001)**: versi asli `auto_choice` adalah blocking loop yang menunggu GPU dengan free memory ≥ 18; versi ini langsung pilih GPU terbaik.

---

## 2. `bert_utils/tokenization.py` — Tokenizer WordPiece

**Peran**: tokenisasi teks → WordPiece, muat `vocab.txt`.

**Kelas**:
- `BertTokenizer`: end-to-end (BasicTokenizer + WordpieceTokenizer). `tokenize()`, `convert_tokens_to_ids()`, `convert_ids_to_tokens()`, `save_vocabulary()`, `from_pretrained()`.
- `BasicTokenizer`: lower-case, strip accent (NFD Unicode), split punctuation, tokenize CJK (tambah spasi sekitar karakter CJK), clean text (buang control char).
- `WordpieceTokenizer`: greedy longest-match-first; `##` prefix untuk sub-token non-awal; `[UNK]` bila tak cocok / terlalu panjang.

**Perubahan porting**: `PRETRAINED_VOCAB_ARCHIVE_MAP` URL S3 mati → `huggingface.co/.../resolve/main/vocab.txt`. 6-7 entri varian (german/whole-word/squad/mrpc) tetap di `POSITIONAL_EMBEDDINGS_SIZE_MAP` tapi tidak di `VOCAB_ARCHIVE_MAP`.

---

## 3. `bert_utils/optimization.py` — BertAdam & Jadwal LR

**Peran**: optimizer Adam kustom BERT + jadwal learning rate.

**Kelas jadwal LR** (`_LRSchedule` ABC):
- `ConstantLR`, `WarmupConstantSchedule`, `WarmupLinearSchedule` (dipakai default), `WarmupCosineSchedule`, `WarmupCosineWithHardRestartsSchedule`, `WarmupCosineWithWarmupRestartsSchedule`.

**BertAdam**:
- Parameter: `lr`, `warmup` (fraksi `t_total`), `t_total` (total step), `schedule` (default `'warmup_linear'`), `b1=0.9`, `b2=0.999`, `e=1e-6`, `weight_decay=0.01`, `max_grad_norm=1.0`.
- **Weight decay fix**: tidak menambah L2 ke loss, tapi `update += weight_decay * p.data` (decouple, tidak interaksi m/v) — ini implementasi AdamW-style yang benar.
- `step()`: EMA gradient (m, v), clip grad per-param (`max_grad_norm`), `update = next_m / (next_v.sqrt() + e)`, lalu `p.data -= lr_scheduled * update`.
- **Tanpa bias correction** (komentar eksplisit di kode).

---

## 4. `file_utils.py` (duplikat `bert_utils/file_utils.py`)

**Peran**: cache & download file via URL (HTTP/S3).

**Fungsi kunci**: `cached_path(url, cache_dir)` — resolve URL → file lokal cache; `url_to_filename()`, `http_get()`, `s3_get()` (bila `boto3` ada).

**Temuan**: `diff -q` konfirmasi **byte-identik** dengan `bert_utils/file_utils.py`. `modeling.py` impor top-level (`from file_utils import cached_path`), `tokenization.py` impor dari package (`from .file_utils import cached_path`). Duplikasi potensial sumber konflik bila salah satu diedit.

---

## 5. `run_classifier_dataset_utils.py` — Data Processor & Feature Conversion

**Peran**: definisi processor task + konversi contoh → fitur tensor.

**Kelas processor**:
- `QuadProcessor` (task `quad`): baca `{domain}_{train,dev,test}_quad_bert.tsv`; label = `[sentiment(3), seqlabs(6: '[CLS]','O','I-A','B-A','I-O','B-O')]`.
- `CategorySentiProcessor` (task `categorysenti`): baca `{domain}_{train,dev,test}_pair.tsv`; label gabungan `CATEGORY#SENTIMENT` (rest16: 13×3=39, laptop: 121×3=363); `_test_pair_1st.tsv` untuk dev (prediksi step 1).

**Feature conversion**:
- `convert_examples_to_features` (step 1): bangun `aspect_labels` (B-A/I-A/B-O/I-O), `[CLS]`+tokens+`[CLS]`, pad ke `max_seq_length`, flag `exist_imp_aspect`/`exist_imp_opinion`. Output `InputFeatures` (7 field).
- `convert_examples_to_features2nd` (step 2): parse `text####aspan ospan`, bangun `candidate_aspect`/`candidate_opinion` (binary mask span), `label_id` multi-label. Implicit aspect → `a_ed=0`; implicit opinion → posisi `[SEP]`.

**Alias kompatibilitas**: `convert_examples_to_features_categorysenti = convert_examples_to_features2nd` (baris 575) — ditambahkan agar notebook bisa memanggil nama alias.

**Metrik helper**: `acc_and_f1` (micro/macro F1, hamming loss), `compute_metrics`.

**Bug upstream**: `_create_examples` baris 186-188 `except: pdb.set_trace()` bila `line[0]` gagal — menggantung run non-interaktif (P2, laporan 001).

---

## 6. `dataset_utils.py` — Pembaca Gold Pair

**Peran**: baca `{domain}_test_pair.tsv` / `_dev_pair.tsv` → gold category-sentiment.

**Fungsi**:
- `read_pair_gold(f, args)`: key = `text+aspect span+opinion span`; value = list `CATEGORY#SENTIMENT`. Tokenisasi via `BertTokenizer.from_pretrained(args.bert_model)`.
- `read_triplet_gold(f, args)`: varian triplet (tidak dipakai di pipeline utama).

**Catatan**: `args.max_seq_length` tidak dipakai (komentar padding dihapus); text di-tokenisasi tanpa pad ke `max_seq_length`.

---

## 7. `tokenized_data/get_1st_pairs.py` — Jembatan Step 1 → Step 2

**Peran**: parse `pred4pipeline.txt`, bangun cross-product aspect × opinion → `{domain}_test_pair_1st.tsv`.

**Algoritma**:
1. Baca `pred4pipeline.txt` (kolom text + tag `a-start,end`/`o-start,end`).
2. Pisahkan span aspect (`a-`) dan opinion (`o-`).
3. Fallback implicit: bila asp kosong → `['-1,-1']`; bila opi kosong → `['-1,-1']`.
4. Cross-product: untuk tiap `(pa, po)` tulis `text####pa po`.
5. `os.makedirs(..., exist_ok=True)` + `encoding='utf-8'`.

**Mode 3-argumen**: `pred_file domain out_file` eksplisit (bila `len(sys.argv) > 3`), sebaliknya mode 2-argumen `base_dir domain` dengan fallback 3 lokasi output.

**Bug porting (laporan 001)**: output ke `BASE_DIR/tokenized_data` vs `run_step2.py` baca dari `DATA_DIR/tokenized_data` — bisa silent mismatch bila beda.

---

## 8. `modeling.py` — Port BERT + 2 Head Task (1647 baris)

**Peran**: definisi arsitektur BERT (port `pytorch_pretrained_bert`) + 2 model task ACOS.

**Bagian BERT (port)**: `BertConfig`, `BertEmbeddings`, `BertSelfAttention`, `BertSelfOutput`, `BertAttention`, `BertIntermediate`, `BertOutput`, `BertLayer`, `BertEncoder`, `BertPooler`, `BertPreTrainedModel` (+ `from_pretrained` dengan download/cache), `TwoBertPreTrainedModel` (varian dual-BERT, tak dipakai). Plus utilitas: `prune_linear_layer`, `load_tf_weights_in_bert`, `gelu`, `swish`.

**Bagian layer tambahan**: `self_attention_layer` (attention softmax eksplois), `CNNLayer`, `RNN_layer` (GRU/LSTM/RNN bi-direksional + pack_padded), `DenseLayer`, `MultiheadAttentionLayer`, `TransformerLayer`.

### Head 1 — `BertForQuadABSA` (Step 1: co-extraction)
```
input_ids → BertModel → (sequence_output [B,L,768], pooled [B,768])
                                │
                ┌───────────────┼────────────────┐
                │               │                │
   dense_output(Dropout→Linear(768→6))  imp_asp_clf     imp_opi_clf
                │               (CLS→2)         (last_SEP→2)
            CRF(6)              │                │
        (B-A/I-A/B-O/I-O/      CE loss          CE loss
         [CLS]/O)
              │
        ae_loss (CRF NLL)
                │
   total_loss = ae_loss + imp_aspect_loss + imp_opinion_loss
   return [total_loss], [pred_tags, imp_aspect_exist, imp_opinion_exist]
```
- `crf_num = 6`; `CRF(batch_first=True)` dari `torchcrf`.
- Implicit aspect dibaca dari `pooled_output` (token `[CLS]`).
- Implicit opinion dibaca dari `pooled_outputs[..., sum(mask)-1]` (token `[SEP]` terakhir).
- Loss: CRF NLL (`reduction='mean'`) + 2× `CrossEntropyLoss`.

### Head 2 — `CategorySentiClassification` (Step 2: klasifikasi)
```
input_ids[:, :max_seq_len] → BertModel → pooled_outputs [B,L,768]
                                                │
   ┌───────────────────────────────────────────┴──────────────────────┐
   │ candidate_aspect [B,L] (mask)    candidate_opinion [B,L] (mask)  │
   │   mean-pool span → aspect_rep [B,768]   mean-pool → opinion_rep │
   │            (sum + zero-guard)                                    │
   └──────────────────────────────────────────────────┬───────────────┘
                         fused = cat([aspect_rep, opinion_rep]) [B,1536]
                         classifier: Linear(1536 → num_labels)
                         BCEWithLogitsLoss (multi-label)
   return [loss], [fused_feature]
```
- Mean-pool span: `sum(mask*hidden) / sum(mask)` dengan guard nol (`sum + eq(0)`) menghindari div-by-zero.
- `num_labels`: 39 (rest16) / 363 (laptop).
- Classifier: `Linear(768*2 → num_labels)` (versi 1-layer; versi 2-layer di-comment).
- Loss `BCEWithLogitsLoss` multi-label.

---

## 9. `run_step1.py` — CLI Training Step 1

**Peran**: entry-point CLI untuk training + evaluasi `BertForQuadABSA`.

**Alur `main()`**:
1. Parse argparse (`--data_dir`, `--bert_model`, `--task_name`, `--domain_type`, `--model_type`, `--do_train`, `--do_eval`, hyperparam).
2. `GPUManager().auto_choice()` di import-time → set `CUDA_VISIBLE_DEVICES`.
3. Init tokenizer, processor, label_list; `model_dict = {'quad': BertForQuadABSA}`.
4. **Eval gold** (bila `do_eval`): baca `test_quad_bert.tsv`, bangun `aspect_labels` gold + flag implicit.
5. Convert examples → features → `TensorDataset` → `DataLoader`.
6. **Train** (bila `do_train`): loop `trange(num_train_epochs)`:
   - Forward `model(...)` → `losses, logits`; `loss = losses[0]`.
   - `loss.backward()`; `BertAdam.step()`; `zero_grad()`.
   - Per epoch: `pred_eval(eval_type='valid')`; bila F1 baru > max → save state_dict + config + vocab; lalu `pred_eval(eval_type='test')`.
7. Tulis `Test_results.txt`.

**Bug upstream (P2)**: baris 420-428 `ae_loss` undefined di jalur `gradient_accumulation_steps > 1`/`--fp16` — `NameError` bila aktif. Default `run.sh` (grad_accum=1, no fp16) tak terkena.

---

## 10. `run_step2.py` — CLI Training Step 2

**Peran**: entry-point CLI untuk training + evaluasi `CategorySentiClassification`.

**Alur `main()`** (paralel `run_step1.py`):
1. Argparse serupa; `model_dict = {'categorysenti': CategorySentiClassification}`.
2. Eval gold via `read_pair_gold` (`test_pair.tsv`).
3. Train: forward `model(tokenizer, _e, ...)` → `losses, logits`; `loss = losses[0]`; backward.
4. Per epoch: `pair_eval(eval_type='valid')`; save saat F1 baru; `pair_eval(eval_type='test')`.
5. Tulis `Test_results.txt`.

**Catatan**: `pair_eval` memanggil `model(tokenizer, _e, ...)` — signature beda dari step 1 (butuh tokenizer + epoch). Seed default 13 (bukan 42).

---

## 11. `eval_metrics.py` — Metrik Evaluasi

**Peran**: evaluasi prediksi vs gold; tulis `pred4pipeline.txt`/`result.txt`.

**Fungsi inti**:
- `measureQuad(pred, gold)`: TP/FP/FN level kalimat (key = text join id). Return `precision/recall/micro-F1`.
- `pred_eval(...)` (step 1): decode tag CRF → span via regex `r'32*'` (aspect, B-A=3/I-A=2) dan `r'54*'` (opinion, B-O=5/I-O=4); offset −1 karena `[CLS]`; tulis `pred4pipeline.txt` (test) / `valid.txt`.
- `pair_eval(...)` (step 2): decode `candidate_aspect`/`candidate_opinion` via regex `r'11*'`; kategorisasi pasangan; `measureQuad` per pasangan.
- `getTextType(gold)`: klasifikasi tiap kalimat ke subset 0-4 (explicit-explicit, implicit-explicit, explicit-implicit, implicit-implicit, overall).
- `measureQuad_imp(pred, gold, text_type)`: P/R/F1 per subset 0-4.

**15 subtask**: loop `comb_choice in range(1, 1<<4)` (16-1=15 kombinasi elemen `[category, sentiment, aspect, opinion]`); tiap kombinasi → `measureQuad_imp` per subset. Hasil hanya ditulis ke `logger.info` + `return res` keseluruhan — itulah sebabnya notebook butuh `SubtaskMetricCapture` untuk menangkapnya.

**Bug/quirk**: `pair_eval` return `{'precision':p,'recall':r,'micro-F1':f}` **selalu nilai subset terakhir** (i=4) karena return di luar loop — lihat baris 215-221 `measureQuad_imp` (return pakai variabel `p,r,f` terakhir).

---

## 12. `run.sh` — Orchestrator

**Alur 3 langkah**:
1. `python run_step1.py` (task `quad`, model `quad`, 30 epoch, LR 2e-5, batch 24).
2. `python tokenized_data/get_1st_pairs.py $BASE_DIR $DOMAIN`.
3. `python run_step2.py` (task `categorysenti`, 30 epoch, LR 5e-5, batch 16).

**Catatan**: path absolut `/mnt/nfs-storage-titan/...` environment penulis asli — harus diedit manual.

---

## 13. `colab_utils.py` — Helper Notebook

**Peran**: EDA, plotting, checkpoint, inferensi, wrapper adaptasi API.

**Fungsi inti** (lihat laporan 002 §3.1 untuk detail):
- `setup_timestamped_run_dir()` → `results/<domain>_<DDMMYYYY_HMS>/{plots,csv,md,logs,checkpoints/{step1,step2}_best}`.
- `download_bert_pretrained()` → cache 3 file HF Hub.
- `analyze_and_plot_eda()` → 4 plot + 2 CSV.
- `plot_training_history()` → kurva loss/metric + CSV.
- `export_benchmark_tables_and_plots()` → bar 15 subtask + bar 4 subset.
- `display_quadruple_dataframe()` → styled DataFrame.

**Wrapper adaptasi API** (fix laporan 002):
- `features_step1`/`features_step2` — menyerap kwarg `domain_type` berlebih.
- `pair_examples_from_file` — baca pair file mana pun → `InputExample2nd`.
- `resolve_eval_pair_file` — pilih `_test_pair_1st.tsv` atau fallback `_test_pair.tsv`.
- `unpack_model_output` — ambil skalar loss dari `([loss],[logits])`.

**Helper laporan**:
- `df_to_markdown` — DataFrame → tabel MD tanpa `tabulate`.
- `export_step_table` — simpan CSV + MD + tampil.
- `MarkdownReport` — akumulator (section/text/kv/table/code/image/save).
- `SubtaskMetricCapture` — tangkap metrik 15 subtask dari log `pair_eval`.
- `plot_subtask_metrics` — bar chart Micro-F1 per subtask.

**Inferensi dua-tahap** (`analyze_review_quadruples` di notebook, memakai helper): tokenize → Step1 CRF span (regex `32*`/`54*`) → deteksi implicit → Step2 klasifikasi → DataFrame terurut skor logit.

---

## 14. Pola Teknis Lintas-File

| Pola | File | Penerapan |
|------|------|-----------|
| **Port legacy BERT** | modeling.py, tokenization.py, optimization.py | Reimplementasi `pytorch_pretrained_bert` (pre-`transformers`), bukan pakai lib modern |
| **Weight decay decouple** | optimization.py | `update += weight_decay * p.data` (AdamW-style) |
| **Regex span decode** | eval_metrics.py | `r'32*'` aspect, `r'54*'` opinion — offset −1 krn `[CLS]` |
| **Mean-pool dengan guard** | modeling.py | `sum + eq(0)` hindari div-by-zero |
| **Multi-loss joint** | modeling.py (BertForQuadABSA) | CRF + 2×CE dalam satu forward |
| **Silent metric capture** | colab_utils.py | `SubtaskMetricCapture` tangkap log karena `pair_eval` tak return per-subtask |
| **Fallback berlapis** | manager.py, get_1st_pairs.py, colab_utils.py | GPU dummy, 3 lokasi output, fallback import |

---

## 15. Catatan Kritis Lintas-File

1. **`pair_eval` return hanya nilai subset terakhir (i=4)** — `measureQuad_imp` return di luar loop subset; `res` final = nilai subset 4 (overall). Ini quirk penting: metrik "overall" yang dilaporkan `run_step2.py` sebenarnya = nilai subset 4, bukan agregat semua subset. (Tapi karena subset 4 = "kalimat apa pun", secara semantik mendekati overall.)
2. **Bug `ae_loss`** (run_step1.py:422,426) — tak terkena default tapi blocker bila grad_accum/fp16 aktif.
3. **Duplikasi `file_utils.py`** — byte-identik; konflik bila satu diedit.
4. **Path mismatch jembatan** — `get_1st_pairs.py` output ke `BASE_DIR`, `run_step2.py` baca dari `DATA_DIR`; silent mismatch.
5. **`pdb.set_trace()`** di `run_classifier_dataset_utils.py:179` — menggantung run batch.
6. **15 subtask tidak terstruktur di output** — `pair_eval` tulis ke logger; butuh `SubtaskMetricCapture` untuk diakses programmatically.
7. **Tokenizer dipakai di `dataset_utils.read_pair_gold`** — instansiasi per-panggilan (bukan cache); potensial lambat bila dipanggil berulang.
8. **`TwoBertPreTrainedModel` & layer tak terpakai** (`CNNLayer`, `RNN_layer`, `MultiheadAttentionLayer`, `TransformerLayer`) — dead code di modeling.py; dipertahankan dari port asli.
