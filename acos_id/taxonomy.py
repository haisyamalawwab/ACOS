"""Taksonomi domain Indonesia (Apps-ACOS) untuk pipeline ACOS dua tahap.

Sumber label adalah `data/Apps-ACOS/processed/label_maps.json`. Modul ini
menuliskan ulang daftar itu sebagai konstanta agar pipeline tidak bergantung
pada berkas yang bisa berubah, lalu menyediakan `verify_against_label_maps()`
yang membandingkan keduanya. Kalau dataset diperbarui dengan kategori baru,
gate itu gagal — bukan training yang menghasilkan angka salah secara senyap.

Jumlah kategori dijaga **13**, sama dengan rest16, sehingga `num_labels` Step 2
tetap 13 x 3 = 39 dan dimensi head tidak berubah terhadap baseline Inggris.
"""
from __future__ import annotations

import json
import os

DOMAIN = "appsid"
"""Nilai `--domain_type` / `DOMAIN` untuk dataset ini.

Dipakai sebagai prefiks nama berkas (`appsid_quad_train.tsv`) dan nama folder
sesi (`appsid_<timestamp>`), yang membuat `find_resumable_session()` tidak
pernah menukar sesi Indonesia dengan sesi rest16/laptop.
"""

DATASET_DIRNAME = "Apps-ACOS"
"""Folder sumber mentah di bawah `data/`."""

CATEGORIES = (
    "ONBOARDING_KYC",
    "AUTH_ACCESS",
    "TRANSACTION_TRANSFER",
    "APP_PERFORMANCE",
    "UI_UX_DESIGN",
    "FEES_CHARGES",
    "INTEREST_RETURNS",
    "CUSTOMER_SERVICE",
    "SECURITY_FRAUD",
    "FEATURES_PRODUCT",
    "PROMO_MARKETING",
    "NOTIFICATION_INFO",
    "ACCOUNT_MANAGEMENT",
)
"""13 kategori aspek ulasan aplikasi perbankan digital.

Berbeda dari rest16 yang memakai pola `ENTITAS#ATRIBUT`, dataset ini memakai
nama datar tanpa `#`. Itu penting: `eval_metrics.py:226` memecah label gabungan
dengan `ele.split('#')` lalu menyatukan kembali semua bagian kecuali yang
terakhir sebagai kategori, jadi kategori tanpa `#` justru jalur paling aman.
"""

SENTIMENTS = ("0", "1", "2")
"""Encoding upstream: 0 negatif, 1 netral, 2 positif (Cai 2021)."""

SENTIMENT_FROM_NAME = {"negative": "0", "neutral": "1", "positive": "2"}
"""Peta kolom `sentiment` dataset ke encoding upstream."""

SENTIMENT_TO_NAME = {"0": "negatif", "1": "netral", "2": "positif"}

EMOTIONS = (
    "joy",
    "trust",
    "anger",
    "sadness",
    "fear",
    "disgust",
    "neutral",
)
"""7 kelas emosi. Hanya dipakai jalur quintuple (absa5/ACOSE), bukan Step 1/2."""

BIO_TAGS = ("O", "B-ASP", "I-ASP", "B-OPN", "I-OPN")
"""Tag BIO dataset. Padanan upstream ada di `SEQ_LABELS`."""

SEQ_LABELS = ("[CLS]", "O", "I-A", "B-A", "I-O", "B-O")
"""Label sekuens Step 1 upstream (`run_classifier_dataset_utils.py:172`).

Urutannya tidak boleh diubah: `self.crf_num = 6` di `modeling.py:1541`
mengasumsikan tepat 6 tag, dan indeksnya masuk ke CRF.
"""

BIO_TO_SEQ = {
    "O": "O",
    "B-ASP": "B-A",
    "I-ASP": "I-A",
    "B-OPN": "B-O",
    "I-OPN": "I-O",
}
"""Peta tag dataset ke tag upstream."""

NULL_TERM = "[NULL]"
"""Penanda implisit di dataset; di format ACOS menjadi span `-1,-1`."""

IMPLICIT_SPAN = "-1,-1"


def catsenti_labels() -> list:
    """39 label gabungan `KATEGORI#SENTIMEN` dalam urutan yang dipakai head Step 2.

    Urutan mengikuti `CategorySentiProcessor.get_labels()` upstream: kategori
    di lingkar luar, sentimen di lingkar dalam.
    """
    return [f"{cat}#{senti}" for cat in CATEGORIES for senti in SENTIMENTS]


def label_list_step1() -> list:
    """`[sentiment_names, seqlabs]` seperti `QuadProcessor.get_labels()`.

    Elemen pertama tidak dipakai Step 1 (hanya elemen ke-2 yang jadi label CRF),
    tetapi bentuknya dipertahankan agar `convert_examples_to_features()` yang
    membaca `label_list[0]` dan `label_list[1]` tetap bekerja apa adanya.
    """
    return [["negative", "neutral", "positive"], list(SEQ_LABELS)]


def label_list_step2() -> list:
    """`[catsenti]` seperti `CategorySentiProcessor.get_labels()`."""
    return [catsenti_labels()]


def num_labels_step1() -> int:
    return len(SEQ_LABELS)


def num_labels_step2() -> int:
    return len(catsenti_labels())


def is_id_domain(domain_type: str) -> bool:
    """True untuk domain Indonesia yang ditangani modul ini."""
    return str(domain_type).lower().startswith("apps")


def label_maps_path(data_root: str) -> str:
    """Lokasi `label_maps.json` di bawah sebuah folder `data/`."""
    return os.path.join(data_root, DATASET_DIRNAME, "processed", "label_maps.json")


def verify_against_label_maps(data_root: str) -> dict:
    """Bandingkan konstanta modul ini dengan `label_maps.json` dataset.

    Mengembalikan laporan; `ok=False` bila ada selisih. Ini gate taksonomi:
    kategori yang bertambah/berubah nama harus menghentikan pipeline, karena
    `num_labels` Step 2 dan indeks head bergantung pada urutan daftar ini.
    """
    path = label_maps_path(data_root)
    report = {"path": path, "ok": False, "exists": os.path.exists(path), "diff": []}
    if not report["exists"]:
        report["diff"].append(f"label_maps.json tidak ada di {path}")
        return report

    with open(path, encoding="utf-8") as fh:
        maps = json.load(fh)

    checks = (
        ("categories", list(CATEGORIES)),
        ("sentiments", ["negative", "neutral", "positive"]),
        ("emotions", list(EMOTIONS)),
        ("bio_tags", list(BIO_TAGS)),
    )
    for key, expected in checks:
        actual = maps.get(key)
        if actual is None:
            report["diff"].append(f"{key}: tidak ada di label_maps.json")
        elif key in ("sentiments", "emotions", "bio_tags"):
            # urutan kolom ini tidak menentukan indeks head, jadi set-comparison
            if set(actual) != set(expected):
                report["diff"].append(
                    f"{key}: {sorted(set(actual) ^ set(expected))} beda")
        elif list(actual) != expected:
            if set(actual) == set(expected):
                report["diff"].append(
                    f"{key}: isi sama tapi URUTAN beda — indeks head Step 2 akan bergeser")
            else:
                report["diff"].append(
                    f"{key}: {sorted(set(actual) ^ set(expected))} beda")

    if maps.get("null_term") not in (None, NULL_TERM):
        report["diff"].append(
            f"null_term: {maps.get('null_term')!r} != {NULL_TERM!r}")

    report["n_categories"] = len(CATEGORIES)
    report["n_catsenti"] = num_labels_step2()
    report["ok"] = not report["diff"]
    return report


def patch_processor_labels(processors: dict) -> dict:
    """Ajari `QuadProcessor`/`CategorySentiProcessor` mengenal domain Indonesia.

    Upstream `get_labels()` bercabang pada `domain_type.startswith('rest')` dan
    `== 'laptop'`; domain lain membuat `l` tetap `None` lalu `for cate in l`
    melempar `TypeError`. Patch ini menambah cabang tanpa menyentuh berkas
    upstream, sehingga pipeline Inggris tetap bisa dijalankan sebagai kontrol.
    """
    quad_cls = processors["quad"]
    cs_cls = processors["categorysenti"]

    if getattr(cs_cls, "_acos_id_patched", False):
        return {"patched": False, "reason": "sudah dipatch di sesi ini"}

    orig_quad = quad_cls.get_labels
    orig_cs = cs_cls.get_labels

    def quad_get_labels(self, domain_type):
        if is_id_domain(domain_type):
            return label_list_step1()
        return orig_quad(self, domain_type)

    def cs_get_labels(self, domain_type):
        if is_id_domain(domain_type):
            return label_list_step2()
        return orig_cs(self, domain_type)

    quad_cls.get_labels = quad_get_labels
    cs_cls.get_labels = cs_get_labels
    cs_cls._acos_id_patched = True
    quad_cls._acos_id_patched = True
    return {
        "patched": True,
        "domain": DOMAIN,
        "num_labels_step1": num_labels_step1(),
        "num_labels_step2": num_labels_step2(),
    }
