import json
import re
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

nb_path = "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# ==============================================================================
# 1. PATCH CELL 44 (Step 1 Loop)
# ==============================================================================
src44 = "".join(nb['cells'][44]['source'])

# A. Insert epoch start timing inside `for epoch in epoch_bar:`
target_loop_start_1 = "        for epoch in epoch_bar:\n            model_step1.train()"
repl_loop_start_1 = """        for epoch in epoch_bar:
            _epoch_t0_1 = time.time()
            _saved_best_1 = False
            _save_dur_1 = 0.0
            model_step1.train()"""

assert target_loop_start_1 in src44, "Could not find target_loop_start_1 in Cell 44"
src44 = src44.replace(target_loop_start_1, repl_loop_start_1, 1)

# B. Enhance checkpoint save with timing & large GPU marker
target_save_1 = """                torch.save(model_step1.state_dict(), step1_bin)
                model_step1.config.to_json_file(os.path.join(step1_ckpt, "config.json"))
                tokenizer.save_vocabulary(step1_ckpt)
                st.note(f"🔥 Checkpoint terbaik diperbarui → {step1_ckpt}")"""

repl_save_1 = """                _save_t0_1 = time.time()
                torch.save(model_step1.state_dict(), step1_bin)
                model_step1.config.to_json_file(os.path.join(step1_ckpt, "config.json"))
                tokenizer.save_vocabulary(step1_ckpt)
                _save_dur_1 = time.time() - _save_t0_1
                _saved_best_1 = True
                _save_ts_1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                _gpu_marker = "🚀 [LARGE GPU FAST SAVE]" if globals().get("GPU_BENCHMARK_INFO", {}).get("is_large_gpu") else "💾 [SAVE]"
                st.note(f"{_gpu_marker} Checkpoint terbaik Step 1 disimpan pada {_save_ts_1} ({_save_dur_1:.3f}s, F1: {val_f1 * 100:.2f}%) → {step1_ckpt}")
                if "sync_to_gdrive" in globals():
                    sync_to_gdrive(step1_ckpt, "checkpoints/step1_best")"""

assert target_save_1 in src44, "Could not find target_save_1 in Cell 44"
src44 = src44.replace(target_save_1, repl_save_1, 1)

# C. Record epoch in execution_tracker before early stopping check
target_record_1 = """            # ── Early stopping check ──────────────────────────────────────────"""
repl_record_1 = """            # ── Catat metrik & durasi eksekusi ke ExecutionTracker ────────────
            _epoch_dur_1 = time.time() - _epoch_t0_1
            if "execution_tracker" in globals() and execution_tracker is not None:
                execution_tracker.record_epoch(
                    step_name="Step 1 (BERT-CRF)",
                    epoch=epoch,
                    duration_sec=_epoch_dur_1,
                    train_loss=avg_loss,
                    precision=val_res.get('precision', 0.0),
                    recall=val_res.get('recall', 0.0),
                    f1=val_f1,
                    peak_vram_mb=peak_vram,
                    checkpoint_saved=_saved_best_1,
                    save_duration_sec=_save_dur_1,
                    save_path=step1_ckpt if _saved_best_1 else None
                )

            # ── Early stopping check ──────────────────────────────────────────"""

assert target_record_1 in src44, "Could not find target_record_1 in Cell 44"
src44 = src44.replace(target_record_1, repl_record_1, 1)

nb['cells'][44]['source'] = [l + "\n" for l in src44.strip().split("\n")]
print("[OK] Cell 44 (Step 1 Loop) updated successfully.")

# ==============================================================================
# 2. PATCH CELL 46 (Step 1 Report)
# ==============================================================================
src46 = "".join(nb['cells'][46]['source'])
append_46 = """
    # ── Ekspor Rekap Waktu Eksekusi, Profil GPU & Detail Epoch Step 1 (CSV, Excel, Markdown) ──
    if "execution_tracker" in globals() and execution_tracker is not None:
        _rep_dir_1 = os.path.join(session_dirs["root"], "execution_reports")
        _s1_files = execution_tracker.export_summary(
            output_dir=_rep_dir_1,
            session_name=f"ACOS_{DOMAIN.upper()}_Step1",
            gdrive_sync=True
        )
        st.step(f"📊 Laporan waktu eksekusi & GPU Step 1 diekspor: CSV, Excel (.xlsx), Markdown (.md)")
"""

if "_rep_dir_1" not in src46:
    src46 = src46.rstrip() + "\n" + append_46
    nb['cells'][46]['source'] = [l + "\n" for l in src46.strip().split("\n")]
    print("[OK] Cell 46 (Step 1 Report) updated successfully.")
else:
    print("[SKIP] Cell 46 already has execution report export.")

# ==============================================================================
# 3. PATCH CELL 67 (Step 2 Loop)
# ==============================================================================
src67 = "".join(nb['cells'][67]['source'])

# A. Insert epoch start timing inside `for epoch in epoch_bar:`
target_loop_start_2 = "        for epoch in epoch_bar:\n            model_step2.train()"
repl_loop_start_2 = """        for epoch in epoch_bar:
            _epoch_t0_2 = time.time()
            _saved_best_2 = False
            _save_dur_2 = 0.0
            model_step2.train()"""

assert target_loop_start_2 in src67, "Could not find target_loop_start_2 in Cell 67"
src67 = src67.replace(target_loop_start_2, repl_loop_start_2, 1)

# B. Enhance checkpoint save with timing & large GPU marker
target_save_2 = """                torch.save(model_step2.state_dict(), step2_bin)
                model_step2.config.to_json_file(os.path.join(step2_ckpt, "config.json"))
                tokenizer.save_vocabulary(step2_ckpt)
                st.note(f"🔥 Checkpoint diperbarui (epoch {epoch}, F1 {val_f1 * 100:.2f}%) → {step2_ckpt}")"""

repl_save_2 = """                _save_t0_2 = time.time()
                torch.save(model_step2.state_dict(), step2_bin)
                model_step2.config.to_json_file(os.path.join(step2_ckpt, "config.json"))
                tokenizer.save_vocabulary(step2_ckpt)
                _save_dur_2 = time.time() - _save_t0_2
                _saved_best_2 = True
                _save_ts_2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                _gpu_marker2 = "🚀 [LARGE GPU FAST SAVE]" if globals().get("GPU_BENCHMARK_INFO", {}).get("is_large_gpu") else "💾 [SAVE]"
                st.note(f"{_gpu_marker2} Checkpoint terbaik Step 2 disimpan pada {_save_ts_2} ({_save_dur_2:.3f}s, F1: {val_f1 * 100:.2f}%) → {step2_ckpt}")
                if "sync_to_gdrive" in globals():
                    sync_to_gdrive(step2_ckpt, "checkpoints/step2_best")"""

assert target_save_2 in src67, "Could not find target_save_2 in Cell 67"
src67 = src67.replace(target_save_2, repl_save_2, 1)

# C. Record epoch in execution_tracker before early stopping check
target_record_2 = """            # ── Early stopping check ──────────────────────────────────────────"""
repl_record_2 = """            # ── Catat metrik & durasi eksekusi ke ExecutionTracker ────────────
            _epoch_dur_2 = time.time() - _epoch_t0_2
            if "execution_tracker" in globals() and execution_tracker is not None:
                execution_tracker.record_epoch(
                    step_name="Step 2 (Category-Sentiment)",
                    epoch=epoch,
                    duration_sec=_epoch_dur_2,
                    train_loss=avg_loss,
                    precision=val_res.get('precision', 0.0),
                    recall=val_res.get('recall', 0.0),
                    f1=val_f1,
                    peak_vram_mb=peak_vram2,
                    checkpoint_saved=_saved_best_2,
                    save_duration_sec=_save_dur_2,
                    save_path=step2_ckpt if _saved_best_2 else None
                )

            # ── Early stopping check ──────────────────────────────────────────"""

assert target_record_2 in src67, "Could not find target_record_2 in Cell 67"
src67 = src67.replace(target_record_2, repl_record_2, 1)

nb['cells'][67]['source'] = [l + "\n" for l in src67.strip().split("\n")]
print("[OK] Cell 67 (Step 2 Loop) updated successfully.")

# ==============================================================================
# 4. PATCH CELL 69 (Step 2 Report)
# ==============================================================================
src69 = "".join(nb['cells'][69]['source'])
append_69 = """
    # ── Ekspor Rekap Waktu Eksekusi, Profil GPU & Detail Epoch Step 2 (CSV, Excel, Markdown) ──
    if "execution_tracker" in globals() and execution_tracker is not None:
        _rep_dir_2 = os.path.join(session_dirs["root"], "execution_reports")
        _s2_files = execution_tracker.export_summary(
            output_dir=_rep_dir_2,
            session_name=f"ACOS_{DOMAIN.upper()}_Step2",
            gdrive_sync=True
        )
        st.step(f"📊 Laporan waktu eksekusi & GPU Step 2 diekspor: CSV, Excel (.xlsx), Markdown (.md)")
"""

if "_rep_dir_2" not in src69:
    src69 = src69.rstrip() + "\n" + append_69
    nb['cells'][69]['source'] = [l + "\n" for l in src69.strip().split("\n")]
    print("[OK] Cell 69 (Step 2 Report) updated successfully.")
else:
    print("[SKIP] Cell 69 already has execution report export.")

# ==============================================================================
# 5. PATCH CELL 79 (Final Audit & Consolidated Export)
# ==============================================================================
cell79_code = """# Audit akhir seluruh artefak tersimpan di Google Drive / lokal & Ekspor Final Benchmark
print("=" * 78)
print(f"🏁 AUDIT ARTEFAK SESI AKTIF [{DOMAIN.upper()}]")
print("=" * 78)
print(f"📁 Lokasi Penyimpanan: {session_dirs.get('root')}")
is_drive_saved = "/content/drive/MyDrive" in session_dirs.get("root", "")
print(f"🛡️  Persistensi Google Drive: {'✅ TERSIMPAN DI DRIVE' if is_drive_saved or globals().get('GDRIVE_MOUNTED') else '⚠️ LOKAL / EPHEMERAL'}\\n")

all_saved_files = []
for sub_name, sub_path in session_dirs.items():
    if sub_name == "root" or not os.path.isdir(sub_path):
        continue
    for root, dirs, files in os.walk(sub_path):
        for f in sorted(files):
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)
            all_saved_files.append({
                "Subfolder": sub_name,
                "File": f,
                "Size": f"{sz / 1024:.1f} KB" if sz < 1024*1024 else f"{sz / (1024**2):.2f} MB",
                "Path": fp
            })

df_audit = pd.DataFrame(all_saved_files)
if not df_audit.empty:
    print(f"📦 Total {len(df_audit)} file berhasil diamankan di sesi ini:")
    for sf, grp in df_audit.groupby("Subfolder"):
        print(f"\\n📂 [{sf.upper()}] ({len(grp)} file):")
        for r in grp.itertuples():
            print(f"   - {r.File:<42} ({r.Size})")
else:
    print("⚠️ Belum ada file tersimpan di subfolder sesi.")

# ── Ekspor Konsolidasi Laporan Waktu Eksekusi, Profil GPU & Detail Epoch (CSV, Excel, Markdown) ──
if "execution_tracker" in globals() and execution_tracker is not None:
    final_rep_dir = os.path.join(session_dirs["root"], "final_reports")
    final_files = execution_tracker.export_summary(
        output_dir=final_rep_dir,
        session_name=f"ACOS_Master_Pipeline_{DOMAIN.upper()}",
        gdrive_sync=True
    )
    print("\\n" + "=" * 78)
    print("⏱️  REKAP WAKTU EKSEKUSI & PROFIL GPU SELESAI DIEKSPOR:")
    print("=" * 78)
    print(f"📄 CSV Summary     : {final_files['csv']}")
    print(f"📊 Excel Workbook  : {final_files['excel']}")
    print(f"📝 Markdown Report : {final_files['md']}")

    # Render tampilan tabel Markdown di output notebook
    try:
        from IPython.display import display, Markdown
        with open(final_files['md'], "r", encoding="utf-8") as _f_md:
            display(Markdown(_f_md.read()))
    except Exception as _e_disp:
        pass

# ── Cadangkan Seluruh Folder Sesi ke Google Drive jika Aktif ──
if globals().get("GDRIVE_MOUNTED") and "sync_to_gdrive" in globals():
    print("\\n☁️  Menyinkronkan seluruh folder sesi ke Google Drive...")
    _sess_folder_name = os.path.basename(os.path.normpath(session_dirs["root"]))
    _drive_ok = sync_to_gdrive(session_dirs["root"], f"sessions/{_sess_folder_name}")
    if _drive_ok:
        print(f"✅ Sesi lengkap tersimpan di Google Drive: {GDRIVE_BACKUP_DIR}/sessions/{_sess_folder_name}")
    else:
        print("⚠️ Sinkronisasi sesi penuh ke Google Drive mengalami kendala.")
print("=" * 78)
"""

nb['cells'][79]['source'] = [l + "\n" for l in cell79_code.strip().split("\n")]
print("[OK] Cell 79 (Final Audit & Export) updated successfully.")

# Save final updated notebook
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("\n🎉 ALL UPDATES APPLIED TO 00_ACOS_Master_Pipeline_Colab_V4_INDOBERT_run08092026.ipynb SUCCESSFULLY!")
