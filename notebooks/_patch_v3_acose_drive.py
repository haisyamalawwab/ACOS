# Patch one-shot: pindahkan seluruh keluaran ACOSE ke folder Drive "ACOSE".
# Dijalankan sekali terhadap _build_v3_acose.py lalu dihapus.
import io

F = "_build_v3_acose.py"
src = io.open(F, encoding="utf-8").read()
applied, skipped = [], []

def rep(tag, old, new):
    global src
    if new in src:
        skipped.append(tag)
        return
    if old not in src:
        raise SystemExit(f"[GAGAL] {tag}: anchor tidak ketemu:\n{old!r}")
    src = src.replace(old, new)
    applied.append(tag)

# 1. Judul: penjelasan lokasi penyimpanan khusus ACOSE
rep("judul-lokasi",
    "Keputusan desain yang mengikat tahap ini:",
    """**Khusus ACOSE, seluruh hasil disimpan di folder Drive sendiri** -
`/content/drive/MyDrive/ACOSE/<domain>/` (lokal: `Output/ACOSE/<domain>/`) dengan
subfolder `data`, `annotation`, `extraction`, `classification`, `logs`, `csv`,
`md`, `plots`. Lokasinya stabil lintas sesi, sehingga cache sel 10a-10e tidak
tergantung folder sesi ACOS yang aktif.

Keputusan desain yang mengikat tahap ini:""")

# 2. MD 10a: deskripsi lokasi
rep("md10a-lokasi",
    "menulis berkas quint ke\n`<sesi>/acose/data/`.",
    "menulis berkas quint ke folder khusus\n`ACOSE/<domain>/data/` di Drive (lihat judul versi V3).")
rep("md10a-annot",
    "pedoman anotasinya di `<sesi>/acose/annotation/`.",
    "pedoman anotasinya di `ACOSE/<domain>/annotation/`.")

# 3. 10a: require_vars tanpa csv_dir/md_dir/session_dirs
rep("10a-require",
    'require_vars("step_stage", "session_dirs", "base_project_dir", "DOMAIN",\n             "rep", "csv_dir", "md_dir")',
    'require_vars("step_stage", "base_project_dir", "DOMAIN", "rep")')

# 4. 10a: blok direktori berbasis folder ACOSE di Drive
rep("10a-dirs",
    '''    acose_root = os.path.join(session_dirs["root"], "acose")
    acose_raw_dir = os.path.join(acose_root, "data")
    acose_annot_dir = os.path.join(acose_root, "annotation")
    for _d in (acose_raw_dir, acose_annot_dir):
        os.makedirs(_d, exist_ok=True)''',
    '''    # Khusus ACOSE: seluruh hasil disimpan di folder Drive "ACOSE" yang berdiri
    # sendiri (stabil lintas sesi), bukan di dalam folder sesi pipeline ACOS.
    if os.path.exists("/content/drive/MyDrive"):
        acose_save_dir = "/content/drive/MyDrive/ACOSE"
    else:
        acose_save_dir = os.path.join(base_project_dir, "Output", "ACOSE")
    acose_root = os.path.join(acose_save_dir, DOMAIN)
    acose_raw_dir = os.path.join(acose_root, "data")
    acose_annot_dir = os.path.join(acose_root, "annotation")
    acose_logs_dir = os.path.join(acose_root, "logs")
    acose_csv_dir = os.path.join(acose_root, "csv")
    acose_md_dir = os.path.join(acose_root, "md")
    acose_plots_dir = os.path.join(acose_root, "plots")
    for _d in (acose_raw_dir, acose_annot_dir, acose_logs_dir, acose_csv_dir,
               acose_md_dir, acose_plots_dir):
        os.makedirs(_d, exist_ok=True)''')

# 5. 10a: tabel ke csv/md milik ACOSE
rep("10a-export",
    '''    export_step_table(df_emosi, name="master_10_acose_distribusi_emosi", csv_dir=csv_dir,
                      md_dir=md_dir,''',
    '''    export_step_table(df_emosi, name="master_10_acose_distribusi_emosi",
                      csv_dir=acose_csv_dir, md_dir=acose_md_dir,''')

# 6. 10b: progress json ke logs ACOSE
rep("10b-progress",
    'acose_progress_json = os.path.join(session_dirs["logs"], "acose_progress.json")',
    'acose_progress_json = os.path.join(acose_logs_dir, "acose_progress.json")')

# 7. 10c: require tanpa session_dirs
rep("10c-require",
    '''require_vars("step_stage", "cfg_acose", "artifacts_acose", "bert_cache_dir",
             "device", "session_dirs", "acose_extr_log", "acose_cls_log")''',
    '''require_vars("step_stage", "cfg_acose", "artifacts_acose", "bert_cache_dir",
             "device", "acose_logs_dir", "acose_extr_log", "acose_cls_log")''')

# 8. 10d: require + metrics json ke logs ACOSE
rep("10d-require",
    '''require_vars("step_stage", "cfg_acose", "artifacts_acose", "bert_cache_dir",
             "device", "session_dirs")''',
    '''require_vars("step_stage", "cfg_acose", "artifacts_acose", "bert_cache_dir",
             "device", "acose_logs_dir")''')
rep("10d-metrics",
    'acose_metrics_json = os.path.join(session_dirs["logs"], "acose_metrics.json")',
    'acose_metrics_json = os.path.join(acose_logs_dir, "acose_metrics.json")')

# 9. 10d MD: lokasi cache
rep("md10d-cache",
    "Hasil di-cache ke\n`logs/acose_metrics.json`; set `FORCE_REEVAL_ACOSE = True` untuk menghitung ulang.",
    "Hasil di-cache ke\n`<ACOSE>/<domain>/logs/acose_metrics.json`; set `FORCE_REEVAL_ACOSE = True`\nuntuk menghitung ulang.")

# 10. 10e: require_vars + semua keluaran ke folder ACOSE
rep("10e-require",
    '''require_vars("step_stage", "acose_root", "acose_raw_dir", "emotion_labels",
             "acose_bootstrap_reports", "acose_metrics_json", "session_dirs",
             "csv_dir", "md_dir", "plots_dir")''',
    '''require_vars("step_stage", "acose_root", "acose_raw_dir", "emotion_labels",
             "acose_bootstrap_reports", "acose_metrics_json",
             "acose_logs_dir", "acose_csv_dir", "acose_md_dir", "acose_plots_dir")''')
rep("10e-export11",
    '''        export_step_table(df_sub_ac, name="master_11_acose_metrik_subset",
                          csv_dir=csv_dir, md_dir=md_dir,''',
    '''        export_step_table(df_sub_ac, name="master_11_acose_metrik_subset",
                          csv_dir=acose_csv_dir, md_dir=acose_md_dir,''')
rep("10e-export12",
    '''        export_step_table(df_bucket_ac, name="master_12_acose_bucket_implisit",
                          csv_dir=csv_dir, md_dir=md_dir,''',
    '''        export_step_table(df_bucket_ac, name="master_12_acose_bucket_implisit",
                          csv_dir=acose_csv_dir, md_dir=acose_md_dir,''')
rep("10e-plot1",
    '_pl1 = os.path.join(plots_dir, "06_acose_emotion_distribution.png")',
    '_pl1 = os.path.join(acose_plots_dir, "06_acose_emotion_distribution.png")')
rep("10e-plot2",
    '_pl2 = os.path.join(plots_dir, "07_acose_subset_f1.png")',
    '_pl2 = os.path.join(acose_plots_dir, "07_acose_subset_f1.png")')
rep("10e-runjson",
    'acose_run_json = os.path.join(session_dirs["logs"], "acose_run_result.json")',
    'acose_run_json = os.path.join(acose_logs_dir, "acose_run_result.json")')

# 11. 10e MD: lokasi tabel/plot
rep("md10e-lokasi",
    "lalu manifest dan `pipeline_state.pkl`. Aman diulang.",
    "lalu manifest dan `pipeline_state.pkl`. Semua berkas laporan ditulis ke folder\n`ACOSE/<domain>/{csv,md,plots,logs}` di Drive, terpisah dari sesi ACOS. Aman diulang.")

io.open(F, "w", encoding="utf-8", newline="").write(src)
print("diterapkan:", len(applied), applied)
print("sudah ada (dilewati):", len(skipped), skipped)
