"""Uji pembentuk fitur upstream pada data Indonesia, tanpa torch.

`run_classifier_dataset_utils` mengimpor seaborn, sklearn, dan scipy di tingkat
modul padahal `convert_examples_to_features` tidak memakainya, jadi impor itu
distub. Yang diuji adalah fungsi asli — bukan salinan — supaya konvensi span,
penempatan `[CLS]`, dan pembentukan `candidate_aspect` benar-benar terverifikasi
pada berkas `tokenized_data/appsid_*` yang sudah dibuat.

Pemakaian: python build/_verify_id_features.py [n_contoh]
"""
import collections
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def stub_scientific_imports():
    """Stub seaborn/sklearn/scipy: dipakai modul upstream untuk metrik, bukan fitur."""
    if "seaborn" not in sys.modules:
        sys.modules["seaborn"] = types.ModuleType("seaborn")

    if "sklearn" not in sys.modules:
        sk = types.ModuleType("sklearn")
        met = types.ModuleType("sklearn.metrics")
        for fn in ("precision_score", "recall_score", "f1_score", "hamming_loss",
                   "accuracy_score", "classification_report", "confusion_matrix",
                   "matthews_corrcoef"):
            setattr(met, fn, lambda *a, **k: 0.0)
        sk.metrics = met
        sys.modules["sklearn"] = sk
        sys.modules["sklearn.metrics"] = met

    if "scipy" not in sys.modules:
        sp = types.ModuleType("scipy")
        st = types.ModuleType("scipy.stats")
        st.pearsonr = lambda *a, **k: (0.0, 0.0)
        st.spearmanr = lambda *a, **k: (0.0, 0.0)
        sp.stats = st
        sys.modules["scipy"] = sp
        sys.modules["scipy.stats"] = st


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    limit = int(argv[0]) if argv else 500

    stub_scientific_imports()
    sys.path.insert(0, INDO_ROOT)

    from acos_id import taxonomy as T
    from acos_id import upstream

    extract_dir = upstream.ensure_path()
    from bert_utils.tokenization import BertTokenizer
    from run_classifier_dataset_utils import (convert_examples_to_features,
                                              convert_examples_to_features2nd,
                                              output_modes, processors)

    vocab_dir = os.path.join(INDO_ROOT, "backbones", "indobert_base_p1")
    if not os.path.exists(os.path.join(vocab_dir, "vocab.txt")):
        print(f"❌ vocab IndoBERT tidak ada di {vocab_dir}")
        return 1

    print(f"indo_root   : {INDO_ROOT}")
    print(f"extract_dir : {extract_dir} (baca saja)")
    print("patch get_labels:", T.patch_processor_labels(processors))
    tk = BertTokenizer.from_pretrained(vocab_dir, do_lower_case=True)
    print(f"tokenizer   : {len(tk.vocab):,} entri\n")

    # Processor menyusun sendiri `<data_dir>/tokenized_data/...`, jadi yang
    # diberikan adalah indo_root — bukan extract_dir, yang tidak memuat berkas
    # appsid_* sama sekali.
    tokenized_base = INDO_ROOT
    ok = True

    # --- Step 1 -------------------------------------------------------------
    p1 = processors["quad"]()
    ll1 = p1.get_labels(T.DOMAIN)
    ex1 = p1.get_dev_examples(extract_dir, T.DOMAIN)[:limit]
    f1 = convert_examples_to_features(ex1, ll1, 128, tk, output_modes["quad"], "quad")
    tags = collections.Counter()
    for f in f1:
        tags.update(f.aspect_labels)
    unk_id = tk.vocab["[UNK]"]
    n_unk = sum(1 for f in f1 for i in f.aspect_input_ids[:f.tokens_len] if i == unk_id)
    n_tok = sum(f.tokens_len for f in f1)

    print(f"STEP 1  {len(ex1)} contoh → {len(f1)} fitur")
    print(f"  implisit : aspek {sum(f.exist_imp_aspect for f in f1)}, "
          f"opini {sum(f.exist_imp_opinion for f in f1)}")
    print(f"  tag      : {dict(tags)}")
    print(f"  [UNK]    : {n_unk}/{n_tok} token ({n_unk / n_tok:.3%})")

    if not {"B-A", "I-A", "B-O", "I-O"} <= set(tags):
        print("  ❌ ada jenis tag span yang tidak pernah muncul — span tidak terbaca")
        ok = False
    if n_unk / n_tok > 0.01:
        print(f"  ❌ [UNK] {n_unk / n_tok:.2%} > 1% — vocab kemungkinan salah")
        ok = False

    # Rekonstruksi satu contoh: tag harus menandai token yang benar.
    f, ex = f1[0], ex1[0]
    toks = ex.text_a.split()
    span_tags = [(t, w) for t, w in zip(f.aspect_labels, toks) if t != "O"]
    print(f"  contoh   : {' '.join(toks[:12])}{'...' if len(toks) > 12 else ''}")
    print(f"             quad={ex.label}")
    print(f"             tag≠O={span_tags}")
    if len(f.aspect_labels) != min(len(toks), 126):
        print(f"  ❌ jumlah tag ({len(f.aspect_labels)}) ≠ jumlah token ({len(toks)})")
        ok = False

    # --- Step 2 -------------------------------------------------------------
    p2 = processors["categorysenti"]()
    ll2 = p2.get_labels(T.DOMAIN)
    ex2 = p2.get_train_examples(extract_dir, T.DOMAIN)[:limit]
    f2 = convert_examples_to_features2nd(ex2, ll2, 128, tk, output_modes["categorysenti"])
    n_pos = sum(sum(f.label_id) for f in f2)
    n_a = sum(1 for f in f2 if sum(f.candidate_aspect) > 0)
    n_o = sum(1 for f in f2 if sum(f.candidate_opinion) > 0)

    print(f"\nSTEP 2  {len(ex2)} pasangan → {len(f2)} fitur, num_labels={len(ll2[0])}")
    print(f"  label positif rata-rata : {n_pos / len(f2):.3f} dari {len(ll2[0])}")
    print(f"  candidate_aspect terisi : {n_a}/{len(f2)}")
    print(f"  candidate_opinion terisi: {n_o}/{len(f2)}")

    if len(ll2[0]) != 39:
        print(f"  ❌ num_labels {len(ll2[0])} ≠ 39 — head berubah dimensi vs baseline")
        ok = False
    if n_pos == 0:
        print("  ❌ tidak ada label positif — category_senti_map tidak cocok dengan data")
        ok = False
    if n_a == 0 or n_o == 0:
        print("  ❌ candidate_aspect/opinion selalu kosong — span pair tidak terbaca")
        ok = False

    # Semua label di berkas pair harus ada di label_list, kalau tidak
    # `category_senti_map[ele]` melempar KeyError di tengah epoch.
    known = set(ll2[0])
    asing = collections.Counter()
    for ex in ex2:
        for lab in (ex.label[0].split() if ex.label else []):
            if lab not in known:
                asing[lab] += 1
    print(f"  label di luar taksonomi : {dict(asing) or 'tidak ada'}")
    if asing:
        print("  ❌ label asing akan memicu KeyError di convert_examples_to_features2nd")
        ok = False

    print("\n" + ("✅ Pembentuk fitur upstream menerima data Indonesia."
                  if ok else "❌ Ada masalah, lihat tanda ❌ di atas."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
