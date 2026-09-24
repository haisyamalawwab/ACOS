"""Cross-validation dan split ratio custom untuk dataset Apps-ACOS.

Dua fitur utama:

1. ``build_kfold_splits()``: Generate K-Fold splits (5 atau 10 fold) pada level
   ``review_id`` — semua klausa dari satu ulasan masuk ke fold yang sama,
   sehingga tidak ada data leakage antar fold.

2. ``build_with_ratio()``: Build dataset dengan rasio train:dev:test custom
   (misal 80:10:10, 70:15:15, 60:20:20) tanpa mengubah split original.

3. ``ExperimentGrid``: Kelas utilitas untuk mendaftarkan dan menjalankan
   kombinasi eksperimen (epoch × split × fold) secara otomatis, satu per satu
   atau sekaligus.

Contoh penggunaan minimal di notebook:

    from acos_id.cross_val import build_kfold_splits, build_with_ratio, ExperimentGrid

    # 1. Generate 5-fold splits
    info = build_kfold_splits(
        processed_dir=os.path.join(data_root, "Apps-ACOS", "processed"),
        out_base=os.path.join(data_root, "Apps-ACOS", "cv_5fold"),
        n_splits=5, seed=42,
    )

    # 2. Build split 80:20
    build_with_ratio(
        processed_dir=..., out_dir=...,
        train_ratio=0.8, dev_ratio=0.1, seed=42,
    )

    # 3. Daftarkan grid eksperimen
    grid = ExperimentGrid()
    grid.add_epochs([50, 75, 100])
    grid.add_ratios([(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)])
    grid.add_cv(n_splits=5, n_folds=5)
    grid.add_cv(n_splits=10, n_folds=10)
    for cfg in grid:
        print(cfg)   # {"type": "ratio", "epochs": 50, "train": 0.8, ...}
"""
from __future__ import annotations

import collections
import csv
import json
import os
import random
import sys
from typing import Iterator, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers (disalin minimal dari build_acos agar modul mandiri)
# ──────────────────────────────────────────────────────────────────────────────

import re as _re

_TOKEN_RE = _re.compile(r"\w+|[^\w\s]", _re.UNICODE)
csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))


def _tokenize(text: str) -> list:
    return _TOKEN_RE.findall(text.lower())


def _find_span(haystack, needle, prefer_from=0):
    n = len(needle)
    if n == 0 or n > len(haystack):
        return None
    first = None
    for i in range(len(haystack) - n + 1):
        if haystack[i:i + n] == needle:
            if first is None:
                first = i
            if i >= prefer_from:
                return i
    return first


def _read_all_review_ids(processed_dir: str) -> List[str]:
    """Kumpulkan seluruh review_id unik dari stage2_*.jsonl, urutan deterministik."""
    ids: set = set()
    for fname in ("stage2_train.jsonl", "stage2_val.jsonl", "stage2_test.jsonl"):
        path = os.path.join(processed_dir, fname)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    ids.add(json.loads(line)["review_id"])
    return sorted(ids)   # sort untuk deterministik sebelum shuffle


def _group_quintuples(processed_dir: str) -> collections.OrderedDict:
    path = os.path.join(processed_dir, "quintuples_weak.csv")
    groups: collections.OrderedDict = collections.OrderedDict()
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            groups.setdefault((row["review_id"], row["clause"]), []).append(row)
    return groups


def _build_lines_from_id_map(processed_dir: str, id_to_split: dict,
                              categories: set, sentiment_map: dict,
                              implicit_span: str, null_term: str) -> tuple:
    """Konversi quintuples → baris ACOS untuk mapping id_to_split custom."""
    groups = _group_quintuples(processed_dir)
    lines: dict = {"train": [], "dev": [], "test": []}
    rep = collections.Counter()
    unknown_cat = collections.Counter()

    for (rid, clause), rows in groups.items():
        split = id_to_split.get(rid)
        if split is None:
            rep["klausa_dibuang_tanpa_split"] += 1
            continue

        tokens = _tokenize(clause)
        if not tokens:
            rep["klausa_dibuang_kosong"] += 1
            continue

        quads = []
        for row in rows:
            cat = row["category"]
            if cat not in categories:
                unknown_cat[cat] += 1
                rep["tuple_dibuang_kategori_asing"] += 1
                continue
            senti = sentiment_map.get(row["sentiment"])
            if senti is None:
                rep["tuple_dibuang_sentimen_asing"] += 1
                continue

            asp_raw, opi_raw = row["aspect"], row["opinion"]
            if asp_raw == null_term:
                asp_span = implicit_span
                asp_end = 0
                rep["aspek_implisit"] += 1
            else:
                at = _tokenize(asp_raw)
                st = _find_span(tokens, at)
                if st is None:
                    rep["tuple_dibuang_aspek_tak_ditemukan"] += 1
                    continue
                asp_span = f"{st},{st + len(at)}"
                asp_end = st + len(at)
                rep["aspek_eksplisit"] += 1

            if opi_raw == null_term:
                opi_span = implicit_span
                rep["opini_implisit"] += 1
            else:
                ot = _tokenize(opi_raw)
                st = _find_span(tokens, ot, prefer_from=asp_end)
                if st is None:
                    rep["tuple_dibuang_opini_tak_ditemukan"] += 1
                    continue
                opi_span = f"{st},{st + len(ot)}"
                rep["opini_eksplisit"] += 1

            quad = f"{asp_span} {cat} {senti} {opi_span}"
            if quad not in quads:
                quads.append(quad)
            else:
                rep["tuple_duplikat_digabung"] += 1

        if not quads:
            rep["klausa_dibuang_tanpa_tuple_valid"] += 1
            continue

        text = " ".join(tokens)
        lines[split].append(text + "\t" + "\t".join(quads))
        rep[f"baris_{split}"] += 1
        rep[f"tuple_{split}"] += len(quads)

    report = dict(rep)
    report["kategori_asing"] = dict(unknown_cat)
    return lines, report


def _write_tsv_files(lines_by_split: dict, out_dir: str,
                     domain: str = "appsid") -> dict:
    """Tulis appsid_quad_<split>.tsv ke out_dir."""
    os.makedirs(out_dir, exist_ok=True)
    written = {}
    for split, lines in lines_by_split.items():
        path = os.path.join(out_dir, f"{domain}_quad_{split}.tsv")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for line in lines:
                fh.write(line + "\n")
        written[split] = path
    return written


def _load_taxonomy():
    """Import lazy dari taxonomy agar modul tetap bisa diimpor tanpa torch."""
    try:
        from .taxonomy import (
            CATEGORIES, DOMAIN, IMPLICIT_SPAN, NULL_TERM, SENTIMENT_FROM_NAME,
        )
        return CATEGORIES, DOMAIN, IMPLICIT_SPAN, NULL_TERM, SENTIMENT_FROM_NAME
    except ImportError:
        # Fallback nilai default Apps-ACOS bila dijalankan di luar paket
        CATEGORIES = [
            "AUTH_ACCESS", "APP_STABILITY", "APP_PERFORMANCE",
            "UI_DESIGN", "FEATURE_COMPLETENESS", "DATA_SECURITY",
            "TRANSACTION_SUCCESS", "NOTIFICATION_SYSTEM", "CUSTOMER_SUPPORT",
            "UPDATE_MAINTENANCE", "INTERNET_CONNECTIVITY", "DEVICE_COMPATIBILITY",
            "GENERAL",
        ]
        DOMAIN = "appsid"
        IMPLICIT_SPAN = "-1,-1"
        NULL_TERM = "NULL"
        SENTIMENT_FROM_NAME = {"positive": 2, "neutral": 1, "negative": 0}
        return CATEGORIES, DOMAIN, IMPLICIT_SPAN, NULL_TERM, SENTIMENT_FROM_NAME


# ──────────────────────────────────────────────────────────────────────────────
# Fitur 1: Split Ratio Custom
# ──────────────────────────────────────────────────────────────────────────────

def build_with_ratio(
    processed_dir: str,
    out_dir: str,
    *,
    train_ratio: float = 0.8,
    dev_ratio: float = 0.1,
    seed: int = 42,
    domain: str = None,
    report_path: str = None,
) -> dict:
    """Build dataset dengan rasio train:dev:test custom.

    Seluruh ``review_id`` dari stage2_*.jsonl dikumpulkan, diacak secara
    deterministik, lalu dibagi sesuai rasio. Klausa dari review yang sama
    selalu masuk ke split yang sama (tidak ada leakage).

    Args:
        processed_dir : folder ``Apps-ACOS/processed/`` (berisi stage2_*.jsonl
                        dan quintuples_weak.csv).
        out_dir       : folder output untuk file TSV yang dihasilkan.
        train_ratio   : proporsi review untuk train (default 0.8 = 80%).
        dev_ratio     : proporsi review untuk dev (default 0.1 = 10%).
                        Sisa otomatis menjadi test.
        seed          : random seed untuk reproducibility.
        domain        : nama domain untuk nama file (default: dari taxonomy).
        report_path   : path untuk menyimpan laporan JSON (opsional).

    Returns:
        dict laporan berisi jumlah baris per split, path file, dll.

    Example::

        build_with_ratio(
            processed_dir="data/Apps-ACOS/processed",
            out_dir="data/Apps-ACOS/split_8020",
            train_ratio=0.8, dev_ratio=0.1, seed=42,
        )
        # → data/Apps-ACOS/split_8020/appsid_quad_train.tsv  (≈80% review)
        # → data/Apps-ACOS/split_8020/appsid_quad_dev.tsv    (≈10% review)
        # → data/Apps-ACOS/split_8020/appsid_quad_test.tsv   (≈10% review)
    """
    CATEGORIES, DOMAIN, IMPLICIT_SPAN, NULL_TERM, SENTIMENT_FROM_NAME = _load_taxonomy()
    if domain is None:
        domain = DOMAIN

    test_ratio = 1.0 - train_ratio - dev_ratio
    assert test_ratio > 0, (
        f"train_ratio ({train_ratio}) + dev_ratio ({dev_ratio}) harus < 1.0")

    # 1. Kumpulkan & acak review_id
    all_ids = _read_all_review_ids(processed_dir)
    rng = random.Random(seed)
    rng.shuffle(all_ids)

    n = len(all_ids)
    n_train = int(n * train_ratio)
    n_dev = int(n * dev_ratio)
    n_test = n - n_train - n_dev

    train_ids = set(all_ids[:n_train])
    dev_ids = set(all_ids[n_train:n_train + n_dev])
    test_ids = set(all_ids[n_train + n_dev:])

    id_to_split: dict = {}
    for rid in train_ids:
        id_to_split[rid] = "train"
    for rid in dev_ids:
        id_to_split[rid] = "dev"
    for rid in test_ids:
        id_to_split[rid] = "test"

    # 2. Build baris ACOS
    lines, rep = _build_lines_from_id_map(
        processed_dir, id_to_split,
        set(CATEGORIES), SENTIMENT_FROM_NAME, IMPLICIT_SPAN, NULL_TERM,
    )

    # 3. Tulis TSV
    written = _write_tsv_files(lines, out_dir, domain=domain)

    # 4. Laporan
    report = {
        "type": "ratio_split",
        "domain": domain,
        "seed": seed,
        "train_ratio": train_ratio,
        "dev_ratio": dev_ratio,
        "test_ratio": round(test_ratio, 4),
        "total_reviews": n,
        "reviews_per_split": {
            "train": n_train, "dev": n_dev, "test": n_test,
        },
        "berkas": written,
        "stats": rep,
    }

    if report_path is None:
        label = f"r{int(train_ratio*100)}{int(dev_ratio*100)}{int(test_ratio*100)}"
        report_path = os.path.join(out_dir, f"_build_report_{label}.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False, sort_keys=True)
    report["laporan"] = report_path

    _print_ratio_summary(report)
    return report


def _print_ratio_summary(report: dict):
    tr = report["train_ratio"]
    dv = report["dev_ratio"]
    ts = report["test_ratio"]
    n = report["total_reviews"]
    print(f"✅ Split {int(tr*100)}:{int(dv*100)}:{int(ts*100)} — "
          f"{n} review → train={report['reviews_per_split']['train']}, "
          f"dev={report['reviews_per_split']['dev']}, "
          f"test={report['reviews_per_split']['test']}")
    for split in ("train", "dev", "test"):
        b = report["stats"].get(f"baris_{split}", 0)
        t = report["stats"].get(f"tuple_{split}", 0)
        print(f"   {split:5s}: {b:6,} baris, {t:7,} tuple → {report['berkas'][split]}")


# ──────────────────────────────────────────────────────────────────────────────
# Fitur 2: K-Fold Cross Validation
# ──────────────────────────────────────────────────────────────────────────────

def build_kfold_splits(
    processed_dir: str,
    out_base: str,
    *,
    n_splits: int = 5,
    dev_ratio: float = 0.1,
    seed: int = 42,
    domain: str = None,
    build_tsv: bool = True,
) -> dict:
    """Generate K-Fold splits dari seluruh review_id.

    CV dilakukan pada level **review_id** (bukan klausa), sehingga semua
    klausa dari satu ulasan selalu masuk ke fold yang sama dan tidak ada
    data leakage.

    Setiap fold menghasilkan:
    - ``fold_N/appsid_quad_train.tsv`` — semua fold kecuali fold ke-N
    - ``fold_N/appsid_quad_dev.tsv``   — 10% dari bagian train (subsampling)
    - ``fold_N/appsid_quad_test.tsv``  — fold ke-N (fold yang ditahan)

    Args:
        processed_dir : folder ``Apps-ACOS/processed/``.
        out_base      : folder output, mis. ``data/Apps-ACOS/cv_5fold/``.
        n_splits      : jumlah fold (5 atau 10).
        dev_ratio     : proporsi dev dari bagian train setiap fold.
        seed          : random seed.
        domain        : nama domain untuk nama file.
        build_tsv     : jika True, langsung tulis TSV; jika False hanya
                        simpan mapping JSON (untuk debug / tokenisasi terpisah).

    Returns:
        dict berisi info setiap fold::

            {
                "n_splits": 5,
                "total_reviews": 12345,
                "folds": {
                    "fold_1": {"train": 9876, "dev": 987, "test": 1234,
                               "dir": "...", "tsv": {...}},
                    ...
                }
            }
    """
    CATEGORIES, DOMAIN, IMPLICIT_SPAN, NULL_TERM, SENTIMENT_FROM_NAME = _load_taxonomy()
    if domain is None:
        domain = DOMAIN

    # 1. Kumpulkan & acak review_id
    all_ids = _read_all_review_ids(processed_dir)
    rng = random.Random(seed)
    rng.shuffle(all_ids)
    n = len(all_ids)

    # 2. Buat fold indices manual (tanpa sklearn agar tidak bergantung dependensi baru)
    fold_size = n // n_splits
    fold_indices = []
    start = 0
    for i in range(n_splits):
        # Fold terakhir mendapat sisa
        end = start + fold_size + (1 if i < n % n_splits else 0)
        fold_indices.append(list(range(start, end)))
        start = end

    os.makedirs(out_base, exist_ok=True)
    report = {
        "n_splits": n_splits,
        "total_reviews": n,
        "dev_ratio": dev_ratio,
        "seed": seed,
        "domain": domain,
        "folds": {},
    }

    print(f"\n📂 K-Fold CV ({n_splits} fold) — {n} review total")
    print(f"   Folder output: {out_base}\n")

    for fold_idx in range(1, n_splits + 1):
        fold_dir = os.path.join(out_base, f"fold_{fold_idx}")
        os.makedirs(fold_dir, exist_ok=True)

        # Test = fold ke-(fold_idx - 1)
        test_idx = fold_indices[fold_idx - 1]
        train_val_idx = []
        for i, fi in enumerate(fold_indices):
            if i != (fold_idx - 1):
                train_val_idx.extend(fi)

        test_ids = set(all_ids[i] for i in test_idx)

        # Dev = dev_ratio dari train_val, deterministik
        n_dev = int(len(train_val_idx) * dev_ratio)
        dev_ids = set(all_ids[i] for i in train_val_idx[:n_dev])
        train_ids = set(all_ids[i] for i in train_val_idx[n_dev:])

        id_to_split: dict = {}
        for rid in train_ids:
            id_to_split[rid] = "train"
        for rid in dev_ids:
            id_to_split[rid] = "dev"
        for rid in test_ids:
            id_to_split[rid] = "test"

        # Simpan mapping JSON
        mapping_path = os.path.join(fold_dir, "id_to_split.json")
        with open(mapping_path, "w", encoding="utf-8") as fh:
            json.dump(id_to_split, fh, indent=2)

        fold_info: dict = {
            "train_reviews": len(train_ids),
            "dev_reviews": len(dev_ids),
            "test_reviews": len(test_ids),
            "dir": fold_dir,
            "mapping": mapping_path,
        }

        # Build TSV (opsional)
        if build_tsv:
            lines, rep = _build_lines_from_id_map(
                processed_dir, id_to_split,
                set(CATEGORIES), SENTIMENT_FROM_NAME, IMPLICIT_SPAN, NULL_TERM,
            )
            written = _write_tsv_files(lines, fold_dir, domain=domain)
            fold_info["tsv"] = written
            fold_info["baris"] = {
                s: rep.get(f"baris_{s}", 0) for s in ("train", "dev", "test")
            }
            fold_info["tuple"] = {
                s: rep.get(f"tuple_{s}", 0) for s in ("train", "dev", "test")
            }
            _print_fold_summary(fold_idx, fold_info)

        report["folds"][f"fold_{fold_idx}"] = fold_info

    # Simpan laporan keseluruhan
    rpt_path = os.path.join(out_base, "_cv_report.json")
    with open(rpt_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False, sort_keys=True)
    report["laporan"] = rpt_path
    print(f"\n📊 Laporan CV disimpan: {rpt_path}")
    return report


def _print_fold_summary(fold_idx: int, info: dict):
    b = info.get("baris", {})
    print(f"  Fold {fold_idx:2d} → "
          f"train: {info['train_reviews']:5} review ({b.get('train', '?'):6} baris) | "
          f"dev: {info['dev_reviews']:4} review ({b.get('dev', '?'):5} baris) | "
          f"test: {info['test_reviews']:4} review ({b.get('test', '?'):5} baris)")


# ──────────────────────────────────────────────────────────────────────────────
# Fitur 3: ExperimentGrid — Daftar Kombinasi Eksperimen
# ──────────────────────────────────────────────────────────────────────────────

class ExperimentGrid:
    """Registry kombinasi eksperimen: epoch × split-ratio × CV-fold.

    Gunakan sebagai iterable; setiap item adalah dict konfigurasi satu run.

    Example::

        grid = ExperimentGrid()
        grid.add_epochs([50, 75, 100])
        grid.add_ratios([(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)])
        grid.add_cv(n_splits=5)
        grid.add_cv(n_splits=10)

        for cfg in grid:
            print(cfg)
        # Output contoh:
        # {"type":"ratio", "epochs":50, "train_ratio":0.8, "dev_ratio":0.1, ...}
        # {"type":"ratio", "epochs":50, "train_ratio":0.7, "dev_ratio":0.15, ...}
        # ...
        # {"type":"cv", "epochs":50, "n_splits":5, "fold_idx":1, ...}
        # ...

    Attributes:
        experiments : list semua konfigurasi yang sudah didaftarkan.
    """

    def __init__(self):
        self._epoch_list: List[int] = []
        self._ratio_list: List[Tuple[float, float]] = []
        self._cv_list: List[dict] = []
        self.experiments: List[dict] = []
        self._built = False

    def add_epochs(self, epochs: List[int]):
        """Daftarkan daftar epoch yang akan dicoba."""
        self._epoch_list = list(epochs)
        self._built = False
        return self

    def add_ratios(self, ratios: List[Tuple[float, float]]):
        """Daftarkan daftar (train_ratio, dev_ratio) yang akan dicoba.

        Args:
            ratios: list tuple (train_ratio, dev_ratio). Misal:
                    [(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)]
        """
        self._ratio_list = list(ratios)
        self._built = False
        return self

    def add_cv(self, n_splits: int, n_folds: Optional[int] = None):
        """Daftarkan satu konfigurasi K-Fold CV.

        Args:
            n_splits : jumlah fold (misal 5 atau 10).
            n_folds  : berapa fold yang dijalankan (default: semua = n_splits).
        """
        self._cv_list.append({
            "n_splits": n_splits,
            "n_folds": n_folds or n_splits,
        })
        self._built = False
        return self

    def _build(self):
        """Susun semua kombinasi ke self.experiments."""
        self.experiments = []
        epochs = self._epoch_list or [50]

        # Kombinasi ratio × epoch
        for epochs_val in epochs:
            for train_r, dev_r in self._ratio_list:
                test_r = round(1.0 - train_r - dev_r, 4)
                label = f"split_{int(train_r*100)}{int(dev_r*100)}{int(test_r*100)}"
                self.experiments.append({
                    "type": "ratio",
                    "run_id": f"{label}_ep{epochs_val}",
                    "epochs": epochs_val,
                    "train_ratio": train_r,
                    "dev_ratio": dev_r,
                    "test_ratio": test_r,
                    "result_suffix": f"{label}/ep{epochs_val}",
                })

        # Kombinasi CV × epoch × fold
        for cv_cfg in self._cv_list:
            n_splits = cv_cfg["n_splits"]
            n_folds = cv_cfg["n_folds"]
            for epochs_val in epochs:
                for fold_idx in range(1, n_folds + 1):
                    self.experiments.append({
                        "type": "cv",
                        "run_id": f"cv{n_splits}fold_fold{fold_idx}_ep{epochs_val}",
                        "epochs": epochs_val,
                        "n_splits": n_splits,
                        "fold_idx": fold_idx,
                        "result_suffix": f"cv_{n_splits}fold/fold_{fold_idx}/ep{epochs_val}",
                    })

        self._built = True

    def __iter__(self) -> Iterator[dict]:
        if not self._built:
            self._build()
        return iter(self.experiments)

    def __len__(self) -> int:
        if not self._built:
            self._build()
        return len(self.experiments)

    def summary(self) -> str:
        """Ringkasan teks semua eksperimen yang terdaftar."""
        if not self._built:
            self._build()
        lines = [f"📋 ExperimentGrid — {len(self.experiments)} total run"]
        ratio_runs = [e for e in self.experiments if e["type"] == "ratio"]
        cv_runs = [e for e in self.experiments if e["type"] == "cv"]
        if ratio_runs:
            lines.append(f"   Split-ratio runs : {len(ratio_runs)}")
            for cfg in ratio_runs:
                lines.append(
                    f"     {cfg['run_id']:35s} → epochs={cfg['epochs']}, "
                    f"train={int(cfg['train_ratio']*100)}% "
                    f"dev={int(cfg['dev_ratio']*100)}% "
                    f"test={int(cfg['test_ratio']*100)}%"
                )
        if cv_runs:
            lines.append(f"   CV runs          : {len(cv_runs)}")
            for cfg in cv_runs:
                lines.append(
                    f"     {cfg['run_id']:35s} → epochs={cfg['epochs']}, "
                    f"{cfg['n_splits']}-fold, fold {cfg['fold_idx']}"
                )
        return "\n".join(lines)

    def print_summary(self):
        print(self.summary())


# ──────────────────────────────────────────────────────────────────────────────
# Utilitas: Helper untuk notebook — tokenisasi semua split/fold
# ──────────────────────────────────────────────────────────────────────────────

def tokenize_all_splits(
    tokenizer,
    data_base: str,
    tokenized_base: str,
    *,
    domain: str = "appsid",
    ratio_labels: Optional[List[str]] = None,
    cv_configs: Optional[List[dict]] = None,
    force: bool = False,
):
    """Tokenisasi TSV mentah untuk semua split ratio dan semua fold CV.

    Memanggil ``acos_id.tokenize_data.build_split`` untuk setiap kombinasi.

    Args:
        tokenizer      : BertTokenizer yang sudah dimuat.
        data_base      : folder induk berisi subfolder split (mis. data/Apps-ACOS/).
        tokenized_base : folder induk output tokenized (mis. tokenized_data/).
        domain         : nama domain.
        ratio_labels   : list label subfolder ratio, mis. ["split_801010",
                         "split_701515", "split_602020"]. None = tidak ada.
        cv_configs     : list dict {"n_splits": 5, "n_folds": 5}. None = tidak ada.
        force          : jika True, timpa file yang sudah ada.
    """
    from .tokenize_data import build_split

    jobs = []

    # Jobs split ratio
    for label in (ratio_labels or []):
        for split in ("train", "dev", "test"):
            in_path = os.path.join(data_base, label, f"{domain}_quad_{split}.tsv")
            out_dir = os.path.join(tokenized_base, label)
            quad_out = os.path.join(out_dir, f"{domain}_{split}_quad_bert.tsv")
            pair_out = os.path.join(out_dir, f"{domain}_{split}_pair.tsv")
            jobs.append((f"{label}/{split}", in_path, quad_out, pair_out))

    # Jobs CV fold
    for cv_cfg in (cv_configs or []):
        n_splits = cv_cfg["n_splits"]
        n_folds = cv_cfg.get("n_folds", n_splits)
        cv_label = f"cv_{n_splits}fold"
        for fold_idx in range(1, n_folds + 1):
            for split in ("train", "dev", "test"):
                in_path = os.path.join(
                    data_base, cv_label, f"fold_{fold_idx}",
                    f"{domain}_quad_{split}.tsv")
                out_dir = os.path.join(
                    tokenized_base, cv_label, f"fold_{fold_idx}")
                quad_out = os.path.join(out_dir, f"{domain}_{split}_quad_bert.tsv")
                pair_out = os.path.join(out_dir, f"{domain}_{split}_pair.tsv")
                jobs.append((
                    f"{cv_label}/fold_{fold_idx}/{split}",
                    in_path, quad_out, pair_out))

    total = len(jobs)
    print(f"\n🔤 Tokenisasi {total} file TSV...\n")
    for idx, (label, in_path, quad_out, pair_out) in enumerate(jobs, 1):
        if not os.path.exists(in_path):
            print(f"  [{idx:3d}/{total}] ⚠️  Tidak ada: {in_path}")
            continue
        if not force and os.path.exists(quad_out):
            print(f"  [{idx:3d}/{total}] ⏩ Cache hit: {quad_out}")
            continue
        os.makedirs(os.path.dirname(quad_out), exist_ok=True)
        rep = build_split(tokenizer, in_path, quad_out, pair_out)
        print(f"  [{idx:3d}/{total}] ✅ {label}: "
              f"{rep.get('baris', 0):,} baris, {rep.get('quad', 0):,} quad")

    print(f"\n✅ Tokenisasi selesai ({total} file diproses).")


# ──────────────────────────────────────────────────────────────────────────────
# CLI minimal
# ──────────────────────────────────────────────────────────────────────────────

def main(argv=None):
    """CLI demo: generate 5-fold dan build_with_ratio 80:10:10.

    Usage::
        python -m acos_id.cross_val [processed_dir] [out_base]
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = argv[0] if len(argv) > 0 else os.path.join(
        root, "data", "Apps-ACOS", "processed")
    out_base = argv[1] if len(argv) > 1 else os.path.join(
        root, "data", "Apps-ACOS")

    print("=== Build split ratio 80:10:10 ===")
    build_with_ratio(
        processed_dir, os.path.join(out_base, "split_801010"),
        train_ratio=0.8, dev_ratio=0.1, seed=42,
    )

    print("\n=== Build 5-Fold CV ===")
    build_kfold_splits(
        processed_dir, os.path.join(out_base, "cv_5fold"),
        n_splits=5, seed=42,
    )

    print("\n=== ExperimentGrid Demo ===")
    grid = ExperimentGrid()
    grid.add_epochs([50, 75, 100])
    grid.add_ratios([(0.8, 0.1), (0.7, 0.15), (0.6, 0.2)])
    grid.add_cv(n_splits=5)
    grid.add_cv(n_splits=10)
    grid.print_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
