# ============================================================================
# 4b. Diagnostik Lokasi Dataset & Tokenized Data (cepat, lokal-dulu)
#
# Versi lama melakukan os.walk("/content") tanpa batas. Karena /content memuat
# titik mount Drive, satu sel itu menelusuri SELURUH Drive lewat FUSE (satu
# panggilan jaringan per folder) dan subfolder ACOS ikut dijelajahi dua kali,
# sehingga hasilnya tercetak ganda dan berjalan >8 menit.
#
# Versi ini memeriksa jalur yang sudah diketahui lebih dulu. Bila lengkap, tidak
# ada penjelajahan sama sekali. Penjelajahan hanya terjadi sebagai cadangan,
# dengan batas kedalaman dan berhenti pada temuan pertama.
# ============================================================================
require_vars("step_stage", "base_project_dir", "data_root", "extract_dir", "DOMAIN")

DIAG_MAX_DEPTH = 3          # kedalaman maksimum saat pencarian cadangan
DIAG_SHOW_SAMPLE = 4        # jumlah nama berkas contoh yang ditampilkan

# Berkas ter-tokenisasi yang benar-benar dibaca pipeline untuk domain aktif.
_TOK_WAJIB = [
    f"{DOMAIN}_train_quad_bert.tsv",
    f"{DOMAIN}_test_quad_bert.tsv",
    f"{DOMAIN}_train_pair.tsv",
    f"{DOMAIN}_test_pair.tsv",
]


def _is_data_dir(path):
    """Direktori dataset mentah: memuat Restaurant-ACOS atau Laptop-ACOS."""
    if not os.path.isdir(path):
        return False
    return any(os.path.isdir(os.path.join(path, d))
               for d in ("Restaurant-ACOS", "Laptop-ACOS", "Demo-Resto-ID"))


def _is_tok_dir(path):
    """Direktori tokenized_data yang memuat minimal satu berkas domain aktif."""
    if not os.path.isdir(path):
        return False
    try:
        isi = set(os.listdir(path))
    except OSError:
        return False
    return any(f in isi for f in _TOK_WAJIB)


def _scan_terbatas(akar, uji_data, uji_tok, maks_kedalaman=DIAG_MAX_DEPTH, counter=None):
    """Satu os.walk berbatas yang mencari kedua target sekaligus.

    Mencari data dan tokenized_data dalam SATU penjelajahan, bukan dua: di Drive
    setiap folder adalah satu panggilan jaringan, jadi dua walk berarti dua kali
    biaya. Memangkas folder berat, membatasi kedalaman, dan keluar begitu kedua
    target ketemu.
    """
    hit_data = hit_tok = None
    if not os.path.isdir(akar):
        return None, None
    akar = os.path.abspath(akar)
    lewati = {".git", "__pycache__", ".ipynb_checkpoints", "node_modules",
              ".cache", "sample_data", "drive", "results", "checkpoints",
              "bert_base_uncased", "__MACOSX", ".venv", "venv"}
    for root, dirs, _files in os.walk(akar):
        if counter is not None:
            counter[0] += 1
        if hit_data is None and uji_data(root):
            hit_data = root
        if hit_tok is None and uji_tok(root):
            hit_tok = root
        if hit_data and hit_tok:
            dirs[:] = []
            break
        dirs[:] = [d for d in dirs if d not in lewati and not d.startswith(".")]
        if root.count(os.sep) - akar.count(os.sep) >= maks_kedalaman:
            dirs[:] = []
    return hit_data, hit_tok


with step_stage("4b. Diagnostik lokasi dataset (lokal dulu, scan hanya bila perlu)", 5) as st:
    _n_scan = [0]

    # ---- 1. Kandidat langsung: tanpa penjelajahan, hanya os.path.isdir -------
    _kand_data = [
        data_root,
        os.path.join(base_project_dir, "data"),
        os.path.join(extract_dir, "data"),
    ]
    _kand_tok = [
        os.path.join(extract_dir, "tokenized_data"),
        os.path.join(base_project_dir, "tokenized_data"),
        os.path.join(base_project_dir, "Extract-Classify-ACOS", "tokenized_data"),
    ]

    data_dir_found = next((p for p in _kand_data if _is_data_dir(p)), None)
    tokenized_dir_found = next((p for p in _kand_tok if _is_tok_dir(p)), None)

    _sumber = "jalur langsung (tanpa penjelajahan)"
    st.step(f"Kandidat langsung diperiksa: {len(_kand_data)} lokasi data, "
            f"{len(_kand_tok)} lokasi tokenized_data")

    # ---- 2. Cadangan: hanya untuk yang belum ketemu --------------------------
    if data_dir_found is None or tokenized_dir_found is None:
        _akar_scan = [base_project_dir, extract_dir]
        # Jalur Drive/Colab ditambahkan hanya bila memang di Colab, dan selalu
        # sebagai subfolder ACOS — bukan "/content" yang memuat seluruh Drive.
        if globals().get("HAS_DRIVE"):
            _akar_scan.append("/content/drive/MyDrive/ACOS")
        if globals().get("IS_COLAB"):
            _akar_scan.append("/content/ACOS")
        # Hook untuk pengujian lokal; tidak berpengaruh di Colab.
        _akar_scan += globals().get("_TEST_DRIVE_ROOTS", [])

        # Buang duplikat DAN akar yang sudah tercakup akar lain (inilah yang
        # dulu menyebabkan hasil tercetak dua kali).
        _bersih = []
        for _a in _akar_scan:
            if not _a or not os.path.isdir(_a):
                continue
            _a = os.path.abspath(_a)
            if any(_a == _b or _a.startswith(_b + os.sep) for _b in _bersih):
                continue
            _bersih = [_b for _b in _bersih if not _b.startswith(_a + os.sep)]
            _bersih.append(_a)

        st.note(f"Belum lengkap → scan cadangan di {len(_bersih)} akar "
                f"(maks {DIAG_MAX_DEPTH} tingkat): {_bersih}")
        for _a in _bersih:
            _d, _t = _scan_terbatas(_a, _is_data_dir, _is_tok_dir, counter=_n_scan)
            data_dir_found = data_dir_found or _d
            tokenized_dir_found = tokenized_dir_found or _t
            if data_dir_found and tokenized_dir_found:
                break
        _sumber = f"scan terbatas ({_n_scan[0]} direktori dikunjungi)"

    n_dirs_scanned = _n_scan[0]
    st.step(f"Sumber hasil: {_sumber}")

    # ---- 3. Laporkan sekali, bukan sekali per akar ---------------------------
    if data_dir_found:
        _sub = sorted(d for d in os.listdir(data_dir_found)
                      if os.path.isdir(os.path.join(data_dir_found, d)))
        st.step(f"✅ Dataset mentah  : {data_dir_found}")
        st.note(f"Domain tersedia: {_sub}")
    else:
        st.step("❌ Dataset mentah TIDAK ditemukan (Restaurant-ACOS / Laptop-ACOS)")

    if tokenized_dir_found:
        _isi = sorted(os.listdir(tokenized_dir_found))
        _ada = [f for f in _TOK_WAJIB if f in _isi]
        _hilang = [f for f in _TOK_WAJIB if f not in _isi]
        st.step(f"✅ tokenized_data  : {tokenized_dir_found} ({len(_isi)} berkas)")
        st.note(f"Sampel: {_isi[:DIAG_SHOW_SAMPLE]}")
        st.note(f"Berkas {DOMAIN} wajib: {len(_ada)}/{len(_TOK_WAJIB)} ada"
                + (f" — HILANG: {_hilang}" if _hilang else ""))
    else:
        st.step(f"❌ tokenized_data untuk domain '{DOMAIN}' TIDAK ditemukan")

    # ---- 4. Verifikasi bahwa temuan cocok dengan yang dipakai pipeline -------
    _tok_dipakai = os.path.join(extract_dir, "tokenized_data")
    data_layout_ok = bool(data_dir_found) and bool(tokenized_dir_found)

    if tokenized_dir_found and os.path.abspath(tokenized_dir_found) != os.path.abspath(_tok_dipakai):
        data_layout_ok = False
        st.note(f"⚠️ Pipeline membaca dari {_tok_dipakai}, tetapi berkas ada di "
                f"{tokenized_dir_found}. Sel Step 1/Step 2 akan gagal — salin atau "
                f"sesuaikan extract_dir.")

    st.step("Tata letak data siap dipakai" if data_layout_ok
            else "Tata letak data BERMASALAH — perbaiki sebelum menjalankan Step 1")
