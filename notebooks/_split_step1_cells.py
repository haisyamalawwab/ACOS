"""Memecah sel monolitik Step 1 pada 00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb
menjadi enam sel bertahap (5a-5f) yang masing-masing melaporkan progresnya.

Skrip idempoten: bila notebook sudah dipecah (penanda `class step_stage` ada),
skrip berhenti tanpa mengubah apa pun.
"""
import io
import json
import os
import sys

NB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "00_ACOS_Master_Pipeline_Colab_PRO_Resume.ipynb")
MARKER = "class step_stage"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text.rstrip("\n").splitlines(keepends=True)}


MD_HEAD = """## 5. Step 1: Aspect & Opinion Co-Extraction (BERT-CRF)
Tahap ini dipecah menjadi enam sel (5a-5f) agar setiap bagian punya progres dan durasi sendiri,
sehingga kegagalan atau kelambatan bisa dilacak ke satu tahap saja. Jalankan berurutan.

| Sel | Isi | Aman diulang |
|---|---|---|
| 5a | Import, tokenizer, label map, resolusi path checkpoint | ya |
| 5b | Deteksi cache (sesi aktif + sesi lama), keputusan latih/lewati | ya |
| 5c | Data evaluasi + ground truth (`eval_gold_1`) | ya |
| 5d | Instansiasi model, data training, optimizer | ya (mengalokasi ulang VRAM) |
| 5e | Loop training per epoch + checkpoint terbaik | tidak (melatih ulang) |
| 5f | Plot, tabel laporan, manifest, simpan state | ya |

Sel 5c-5e melewati dirinya sendiri secara otomatis saat `STEP1_SKIP_TRAINING` bernilai `True`.
Set `FORCE_RETRAIN_STEP1 = True` di sel 5a untuk memaksa training ulang."""

CODE_5A = '''from modeling import BertForQuadABSA
from bert_utils.tokenization import BertTokenizer
from bert_utils.optimization import BertAdam
from run_classifier_dataset_utils import processors, output_modes
from eval_metrics import pred_eval
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from tqdm.auto import tqdm
import time

# Toggle Melatih Ulang (Set True jika ingin melatih ulang dari awal)
FORCE_RETRAIN_STEP1 = False


class step_stage:
    """Pelacak progres satu sel: judul, langkah bernomor + waktu, durasi akhir.

    Dipakai seluruh sel 5a-5f supaya setiap tahap Step 1 punya jejak sendiri
    saat runtime Colab terputus di tengah pipeline.
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


def require_step1_stage(*names):
    """Menghentikan sel dengan pesan jelas bila sel Step 1 sebelumnya belum dijalankan."""
    missing = [n for n in names if n not in globals()]
    if missing:
        raise RuntimeError(
            f"Variabel {missing} belum ada. Jalankan sel Step 1 sebelumnya "
            f"(mulai dari 5a) sebelum sel ini.")


with step_stage("5a. Inisialisasi Step 1: tokenizer, label, path", 5) as st:
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

    processor_step1 = processors["quad"]()
    label_list_step1 = processor_step1.get_labels(DOMAIN)
    num_labels_step1 = len(label_list_step1[1])
    label_map_seq = {label: i for i, label in enumerate(label_list_step1[1])}
    st.step(f"Label sekuens ({num_labels_step1}): {label_list_step1[1]}")

    # Path Checkpoint & Berkas Prediksi Step 1
    step1_ckpt = session_dirs["step1_checkpoint"]
    step1_bin = os.path.join(step1_ckpt, "pytorch_model.bin")
    step1_csv = os.path.join(session_dirs["csv"], "step1_training_history.csv")
    pred_file = os.path.join(session_dirs["logs"], "pred4pipeline.txt")
    step1_progress_json = os.path.join(session_dirs["logs"], "step1_progress.json")
    os.makedirs(step1_ckpt, exist_ok=True)
    st.step(f"Checkpoint  : {step1_ckpt}")
    st.step(f"Prediksi    : {pred_file} | FORCE_RETRAIN_STEP1={FORCE_RETRAIN_STEP1} | "
            f"epoch target={NUM_EPOCHS}")'''

MD_5B = """### 5b. Deteksi Cache Step 1
Memeriksa artefak sesi aktif, lalu menarik checkpoint dari sesi lama bila perlu.
Hasilnya adalah `STEP1_SKIP_TRAINING`, satu-satunya penentu apakah sel 5c-5e berjalan."""

CODE_5B = '''require_step1_stage("step1_bin", "pred_file", "step1_csv", "FORCE_RETRAIN_STEP1")

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
            best_step1_f1 = float(df_s1_saved["micro-F1"].max() / 100.0) if "micro-F1" in df_s1_saved else 0.0
            best1_epoch = int(df_s1_saved.loc[df_s1_saved["micro-F1"].idxmax()]["epoch"]) if "epoch" in df_s1_saved else NUM_EPOCHS
            st.step(f"Riwayat tersimpan: {len(df_s1_saved)} epoch, terbaik epoch {best1_epoch}")
            if len(df_s1_saved) < NUM_EPOCHS:
                st.note(f"⚠️ Riwayat hanya {len(df_s1_saved)}/{NUM_EPOCHS} epoch — checkpoint ini "
                        f"berasal dari run yang terhenti. Set FORCE_RETRAIN_STEP1=True bila "
                        f"ingin melatih penuh.")
        else:
            step1_history = []
            best_step1_f1 = 0.0
            best1_epoch = NUM_EPOCHS
            st.step("Riwayat CSV tidak ada — metrik per epoch tidak bisa dilaporkan")'''

MD_5C = """### 5c. Data Evaluasi & Ground Truth
Membangun `eval_loader_1` dan `eval_gold_1`. `eval_gold_1` memakai `aspect_input_ids` hasil
fitur, bukan id token mentah; memakai id mentah menggeser teks `pred4pipeline.txt` satu token
dan mengosongkan kalimat satu kata."""

CODE_5C = '''require_step1_stage("STEP1_SKIP_TRAINING", "label_map_seq", "tokenizer")

if STEP1_SKIP_TRAINING:
    print("⏩ 5c dilewati — memakai artefak Step 1 dari cache (lihat sel 5b).")
else:
    with step_stage("5c. Data evaluasi test + ground truth", 5) as st:
        eval_examples_1 = processor_step1.get_dev_examples(extract_dir, DOMAIN)
        st.step(f"{len(eval_examples_1):,} contoh test dibaca dari "
                f"tokenized_data/{DOMAIN}_test_quad_bert.tsv")

        eval_features_1 = features_step1(eval_examples_1, label_list_step1, MAX_SEQ_LENGTH,
                                         tokenizer, output_modes["quad"], "quad")
        st.step(f"{len(eval_features_1):,} fitur dibentuk (max_seq_length={MAX_SEQ_LENGTH})")

        ev_ids = torch.tensor([f.aspect_input_ids for f in eval_features_1], dtype=torch.long)
        ev_mask = torch.tensor([f.aspect_input_mask for f in eval_features_1], dtype=torch.long)
        ev_seg = torch.tensor([f.aspect_segment_ids for f in eval_features_1], dtype=torch.long)
        ev_lbl = torch.tensor([f.aspect_ids for f in eval_features_1], dtype=torch.long)
        ev_imp_a = torch.tensor([f.exist_imp_aspect for f in eval_features_1], dtype=torch.long)
        ev_imp_o = torch.tensor([f.exist_imp_opinion for f in eval_features_1], dtype=torch.long)
        ev_len = torch.tensor([f.tokens_len for f in eval_features_1], dtype=torch.long)
        eval_data_1 = TensorDataset(ev_len, ev_ids, ev_mask, ev_lbl, ev_seg, ev_imp_a, ev_imp_o)

        pin_mem = torch.cuda.is_available()
        num_work = 0 if sys.platform.startswith('win') else 2
        eval_loader_1 = DataLoader(
            eval_data_1, sampler=SequentialSampler(eval_data_1),
            batch_size=16, pin_memory=pin_mem, num_workers=num_work
        )
        st.step(f"eval_loader_1 siap: {len(eval_loader_1)} batch × 16 "
                f"(pin_memory={pin_mem}, workers={num_work})")

        # Ground truth: input_text wajib memakai aspect_input_ids hasil feature
        # ([CLS] .. [CLS] + zero-pad). pred_eval menulis pred4pipeline.txt dari
        # ids_to_token[1:tokens_len-1]; id token mentah menggeser teks satu token.
        gold_tsv = os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_quad_bert.tsv")
        with open(gold_tsv, "r", encoding="utf-8") as f:
            gold_lines = f.readlines()

        eval_gold_labels = []
        n_imp_a = n_imp_o = 0
        for line in tqdm(gold_lines, desc="   Parsing gold quad", unit="baris", leave=False):
            line = line.strip().split("\\t")
            aspect_labels = [label_map_seq['O'] for _ in range(MAX_SEQ_LENGTH)]
            cur_imp_a, cur_imp_o = 0, 0
            for quad in line[1:]:
                cur_aspect, cur_opinion = quad.split(' ')[0], quad.split(' ')[-1]
                a_st, a_ed = int(cur_aspect.split(',')[0]), int(cur_aspect.split(',')[1])
                if a_ed != -1:
                    aspect_labels[a_st] = label_map_seq['B-A']
                    for i in range(a_st + 1, a_ed):
                        aspect_labels[i] = label_map_seq['I-A']
                else:
                    cur_imp_a = 1
                o_st, o_ed = int(cur_opinion.split(',')[0]), int(cur_opinion.split(',')[1])
                if o_ed != -1:
                    aspect_labels[o_st] = label_map_seq['B-O']
                    for i in range(o_st + 1, o_ed):
                        aspect_labels[i] = label_map_seq['I-O']
                else:
                    cur_imp_o = 1
            eval_gold_labels += [aspect_labels, cur_imp_a, cur_imp_o]
            n_imp_a += cur_imp_a
            n_imp_o += cur_imp_o
        st.step(f"Gold terbentuk untuk {len(gold_lines):,} kalimat "
                f"(implicit aspect: {n_imp_a}, implicit opinion: {n_imp_o})")

        eval_gold_1 = [ev_ids.numpy().tolist(), eval_gold_labels]
        assert len(eval_gold_labels) == 3 * len(eval_features_1), (
            f"Gold ({len(eval_gold_labels) // 3} kalimat) tidak sejajar dengan fitur "
            f"({len(eval_features_1)}). pred_eval akan salah memetakan prediksi.")
        st.step("eval_gold_1 sejajar dengan eval_loader_1 — siap dipakai pred_eval")'''

MD_5D = """### 5d. Model, Data Training & Optimizer
Mengalokasikan VRAM untuk `BertForQuadABSA` dan menyiapkan `BertAdam`.
Jalankan ulang sel ini bila ingin mereset bobot ke pretrained sebelum melatih lagi."""

CODE_5D = '''require_step1_stage("STEP1_SKIP_TRAINING")

if STEP1_SKIP_TRAINING:
    print("⏩ 5d dilewati — model dan optimizer tidak diperlukan saat cache hit.")
else:
    require_step1_stage("eval_loader_1", "eval_gold_1")
    with step_stage("5d. Model BERT-CRF, data training, optimizer", 5) as st:
        model_step1 = BertForQuadABSA.from_pretrained(
            bert_cache_dir, num_labels=num_labels_step1).to(device)
        _n_par = sum(p.numel() for p in model_step1.parameters())
        _vram = torch.cuda.memory_allocated(device) / 1024 ** 2 if torch.cuda.is_available() else 0.0
        st.step(f"Model dimuat ke {device}: {_n_par / 1e6:.1f} M parameter, "
                f"VRAM terpakai {_vram:.0f} MB")

        train_examples_1 = processor_step1.get_train_examples(extract_dir, DOMAIN)
        st.step(f"{len(train_examples_1):,} contoh training dibaca")

        train_features_1 = features_step1(train_examples_1, label_list_step1, MAX_SEQ_LENGTH,
                                          tokenizer, output_modes["quad"], "quad")
        tr_data_1 = TensorDataset(
            torch.tensor([f.tokens_len for f in train_features_1], dtype=torch.long),
            torch.tensor([f.aspect_input_ids for f in train_features_1], dtype=torch.long),
            torch.tensor([f.aspect_input_mask for f in train_features_1], dtype=torch.long),
            torch.tensor([f.aspect_ids for f in train_features_1], dtype=torch.long),
            torch.tensor([f.aspect_segment_ids for f in train_features_1], dtype=torch.long),
            torch.tensor([f.exist_imp_aspect for f in train_features_1], dtype=torch.long),
            torch.tensor([f.exist_imp_opinion for f in train_features_1], dtype=torch.long)
        )
        train_loader_1 = DataLoader(
            tr_data_1, sampler=RandomSampler(tr_data_1),
            batch_size=STEP1_BATCH_SIZE, pin_memory=pin_mem, num_workers=num_work
        )
        st.step(f"train_loader_1 siap: {len(train_loader_1)} batch × {STEP1_BATCH_SIZE}")

        num_train_steps_1 = len(train_loader_1) * NUM_EPOCHS
        param_opt = list(model_step1.named_parameters())
        no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
        opt_grouped = [
            {'params': [p for n, p in param_opt if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
            {'params': [p for n, p in param_opt if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]
        optimizer_1 = BertAdam(opt_grouped, lr=STEP1_LR, warmup=0.1, t_total=num_train_steps_1)
        st.step(f"BertAdam siap: lr={STEP1_LR}, warmup=0.1, t_total={num_train_steps_1:,} step")

        class ArgsH:
            def __init__(self):
                self.output_dir = session_dirs["logs"]
                self.max_seq_length = MAX_SEQ_LENGTH

        args_h = ArgsH()
        import logging
        logger = logging.getLogger("Step1")
        st.step(f"args_h siap — pred_eval akan menulis pred4pipeline.txt ke {args_h.output_dir}")'''

MD_5E = """### 5e. Loop Training Step 1
Progres berjalan di tiga tingkat: bar epoch (ETA total), bar batch (loss berjalan), dan
ringkasan satu baris per epoch. Setiap epoch juga menulis `csv/step1_training_history.csv`,
`logs/step1_progress.json`, dan `session_manifest.json`, jadi progres tetap terbaca dari
berkas kalau tab Colab tertutup."""

CODE_5E = '''require_step1_stage("STEP1_SKIP_TRAINING")

if STEP1_SKIP_TRAINING:
    print("⏩ 5e dilewati — training Step 1 tidak dijalankan (cache hit).")
    print(f"   Micro-F1 terbaik tersimpan: {best_step1_f1 * 100:.2f}% (epoch {best1_epoch})")
else:
    require_step1_stage("model_step1", "optimizer_1", "train_loader_1", "eval_loader_1")
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

            peak_vram = torch.cuda.max_memory_allocated(device) / (1024 ** 2) if torch.cuda.is_available() else 0.0
            st.step(f"Epoch {epoch:02d} | loss {avg_loss:.4f} | test micro-F1 {val_f1 * 100:.2f}% "
                    f"| P {val_res.get('precision', 0.0) * 100:.2f}% "
                    f"| R {val_res.get('recall', 0.0) * 100:.2f}% | peak VRAM {peak_vram:.0f} MB")

            step1_history.append({
                "epoch": epoch, "loss": avg_loss,
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
            with open(step1_progress_json, "w", encoding="utf-8") as pf:
                json.dump({"stage": "STEP1_TRAINING", "epoch": epoch, "total_epochs": NUM_EPOCHS,
                           "last_loss": avg_loss, "last_micro_f1": val_f1,
                           "best_micro_f1": best_step1_f1, "best_epoch": best1_epoch,
                           "peak_vram_mb": round(peak_vram, 2),
                           "updated_at": datetime.now().isoformat()}, pf, indent=2)
            update_mcp_manifest("STEP1_TRAINING", 3, {
                "step1_epoch_progress": f"{epoch}/{NUM_EPOCHS}",
                "step1_best_micro_f1": float(best_step1_f1 * 100),
                "step1_best_epoch": best1_epoch,
            })
            epoch_bar.set_postfix(best_f1=f"{best_step1_f1 * 100:.2f}%", loss=f"{avg_loss:.4f}")
        epoch_bar.close()

        print(f"🏁 Training selesai. Micro-F1 terbaik {best_step1_f1 * 100:.2f}% "
              f"pada epoch {best1_epoch}.", flush=True)'''

MD_5F = """### 5f. Plot, Tabel & Penyimpanan State Step 1
Sel pelaporan: aman dijalankan ulang, baik setelah training maupun setelah cache hit."""

CODE_5F = '''require_step1_stage("step1_history", "best_step1_f1", "best1_epoch")

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
    df_s1 = pd.DataFrame(step1_history)
    if not df_s1.empty:
        df_s1_pct = df_s1.copy()
        for c in ["precision", "recall", "micro-F1"]:
            if c in df_s1_pct.columns and df_s1_pct[c].max() <= 1.0:
                df_s1_pct[c] = (df_s1_pct[c] * 100).round(2)
        export_step_table(df_s1_pct, name="master_03_step1_riwayat", csv_dir=csv_dir, md_dir=md_dir,
                          title=f"Riwayat Training Step 1 ({DOMAIN.upper()})",
                          notes="Metrik dihitung pada test set tiap epoch.",
                          max_rows_md=NUM_EPOCHS)
        rep.table(df_s1_pct, max_rows=NUM_EPOCHS, caption="Metrik step 1 per epoch")
        st.step("Tabel master_03_step1_riwayat diekspor ke csv/ dan md/")

        best1 = df_s1_pct.loc[df_s1_pct["micro-F1"].idxmax()]
        rep.kv({
            "epoch_terbaik": int(best1.get("epoch", best1_epoch)),
            "micro-F1_terbaik": f"{float(best1['micro-F1']):.2f}%",
            "checkpoint": step1_ckpt,
        })
        st.step(f"Micro-F1 terbaik {float(best1['micro-F1']):.2f}% "
                f"(epoch {int(best1.get('epoch', best1_epoch))})")
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


def main():
    nb = json.load(io.open(NB, encoding="utf-8"))
    whole = json.dumps(nb)
    if MARKER in whole:
        print("Notebook sudah dipecah (penanda step_stage ditemukan). Tidak ada perubahan.")
        return 0

    target = None
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell["source"])
        if cell["cell_type"] == "code" and "FORCE_RETRAIN_STEP1 = False" in src \
                and "eval_gold_labels" in src and "for epoch in range(1, NUM_EPOCHS + 1)" in src:
            target = i
            break
    if target is None:
        print("Sel monolitik Step 1 tidak ditemukan. Batal.", file=sys.stderr)
        return 1

    head_md = target - 1 if nb["cells"][target - 1]["cell_type"] == "markdown" else None
    new_cells = [
        code(CODE_5A),
        md(MD_5B), code(CODE_5B),
        md(MD_5C), code(CODE_5C),
        md(MD_5D), code(CODE_5D),
        md(MD_5E), code(CODE_5E),
        md(MD_5F), code(CODE_5F),
    ]
    nb["cells"][target:target + 1] = new_cells
    if head_md is not None:
        nb["cells"][head_md] = md(MD_HEAD)

    with io.open(NB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"Sel {target} dipecah menjadi {len(new_cells)} sel. Total sel kini {len(nb['cells'])}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
