"""Kebijakan folder sesi V4.3: DDMMYYYY_HM + jendela 60 menit.

Aturan (disepakati dari permintaan "DDMMYYYY_HM terdekat, rentang 1 jam"):
- Nama folder: <domain>_DDMMYYYY_HHMM (presisi menit, cth appsid_12092026_1045).
  Format lama <domain>_DDMMYYYY_HHMMSS tetap dibaca (audit 08092026_150437).
- Saat startup: cari sesi domain yang sama dengan selisih waktu <= 60 menit
  dari sekarang (yang terbaru). Ketemu -> PAKAI ULANG (lanjutkan run Colab
  yang terputus; tabel/csv/grafik/pickle/json tetap satu paket laporan).
  Tidak ketemu -> BUAT BARU.
- Tabrakan menit (dua run dalam 1 menit): tambah suffix _01, _02.
- RESUME_LAST_SESSION=False atau FORCE_NEW_SESSION=True selalu buat baru.
- SESSION_REUSE_WINDOW_MIN=0 berarti selalu buat baru (mode arsip per-run).

Torch-free. Satu-satunya dependensi: os/datetime/json.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

SESSION_TIME_FMT = "%d%m%Y_%H%M"
SESSION_TIME_FMT_LEGACY = "%d%m%Y_%H%M%S"
DEFAULT_REUSE_WINDOW_MIN = 60

SUBFOLDERS = ("checkpoints", "plots", "csv", "md", "logs", "reports")
REPORT_SUBFOLDERS = ("csv", "plots", "md", "logs", "reports")


def format_session_stamp(now: datetime | None = None) -> str:
    return (now or datetime.now()).strftime(SESSION_TIME_FMT)


def parse_session_time(folder_name: str, domain: str) -> datetime | None:
    if not folder_name.startswith(domain + "_"):
        return None
    stamp = folder_name[len(domain) + 1:]
    stamp = stamp.split("_")[0] + (
        "_" + stamp.split("_")[1] if len(stamp.split("_")) > 1 else "")
    for fmt in (SESSION_TIME_FMT, SESSION_TIME_FMT_LEGACY):
        try:
            return datetime.strptime(stamp, fmt)
        except ValueError:
            continue
    return None


def list_domain_sessions(base_dir: str, domain: str) -> list:
    found = []
    if not base_dir or not os.path.isdir(base_dir):
        return found
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if not os.path.isdir(path):
            continue
        stamp = parse_session_time(name, domain)
        if stamp is not None:
            found.append({"name": name, "path": path, "time": stamp})
    found.sort(key=lambda s: s["time"])
    return found


def find_nearest_session(base_dir: str, domain: str,
                         now: datetime | None = None,
                         max_minutes: int = DEFAULT_REUSE_WINDOW_MIN) -> dict | None:
    """Sesi terbaru dalam jendela waktu (default 60 mnt ke belakang)."""
    now = now or datetime.now()
    best = None
    for sess in list_domain_sessions(base_dir, domain):
        delta = (now - sess["time"]).total_seconds() / 60.0
        if 0 <= delta <= max_minutes:
            if best is None or sess["time"] > best["time"]:
                best = dict(sess, delta_min=delta)
    return best


def session_dirs_from_root(run_dir: str) -> dict:
    dirs = {
        "root": run_dir,
        "checkpoints": os.path.join(run_dir, "checkpoints"),
        "step1_checkpoint": os.path.join(run_dir, "checkpoints", "step1_best"),
        "step2_checkpoint": os.path.join(run_dir, "checkpoints", "step2_best"),
        "plots": os.path.join(run_dir, "plots"),
        "csv": os.path.join(run_dir, "csv"),
        "md": os.path.join(run_dir, "md"),
        "logs": os.path.join(run_dir, "logs"),
        "reports": os.path.join(run_dir, "reports"),
    }
    for path in dirs.values():
        os.makedirs(path, exist_ok=True)
    return dirs


def _unique_session_root(base_dir: str, domain: str, stamp: str) -> str:
    root = os.path.join(base_dir, "%s_%s" % (domain, stamp))
    if not os.path.exists(root):
        return root
    suffix = 1
    while True:
        cand = "%s_%02d" % (root, suffix)
        if not os.path.exists(cand):
            return cand
        suffix += 1


def ensure_session_dir(base_dir: str, domain: str,
                       now: datetime | None = None,
                       max_reuse_minutes: int = DEFAULT_REUSE_WINDOW_MIN,
                       resume: bool = True, force_new: bool = False) -> tuple:
    """Titik masuk utama. Kembalikan (session_dirs, meta)."""
    now = now or datetime.now()
    os.makedirs(base_dir, exist_ok=True)
    meta = {"domain": domain, "base_dir": os.path.abspath(base_dir),
            "now": now.isoformat(timespec="minutes"),
            "window_min": max_reuse_minutes, "reused": False}
    nearest = None
    if resume and not force_new and max_reuse_minutes > 0:
        nearest = find_nearest_session(base_dir, domain, now, max_reuse_minutes)
    if nearest is not None:
        meta.update({"reused": True, "root": nearest["path"],
                     "nearest": nearest["name"],
                     "delta_min": round(nearest["delta_min"], 1),
                     "reason": "reuse dalam jendela %d mnt" % max_reuse_minutes})
        return session_dirs_from_root(nearest["path"]), meta
    stamp = format_session_stamp(now)
    root = _unique_session_root(base_dir, domain, stamp)
    meta.update({"root": root, "stamp": stamp,
                 "reason": "baru (force_new=%s)" % force_new if force_new
                 else "baru (tidak ada sesi <= %d mnt)" % max_reuse_minutes})
    return session_dirs_from_root(root), meta


def write_session_manifest(session_dirs: dict, meta: dict,
                           extra: dict | None = None) -> str:
    manifest = dict(meta)
    if extra:
        manifest.update(extra)
    manifest["session_root"] = session_dirs["root"]
    manifest["subfolders"] = {k: v for k, v in session_dirs.items() if k != "root"}
    path = os.path.join(session_dirs["root"], "session_manifest.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False, default=str)
    return path


def write_report_index(session_dirs: dict) -> str:
    """Indeks artefak laporan: tabel/csv, grafik, pickle, json."""
    root = session_dirs["root"]
    lines = ["# Indeks Artefak Laporan", "",
             "Root sesi: `%s`" % root, "",
             "| Jenis | Folder | Jumlah berkas |",
             "|---|---|---|"]
    kinds = (("tabel/csv", "csv", ".csv"), ("grafik", "plots", ".png"),
             ("laporan md", "md", ".md"), ("log/json", "logs", ".json"),
             ("pickle/state", "root", ".pkl"))
    for label, key, ext in kinds:
        folder = root if key == "root" else session_dirs.get(key, "")
        count = 0
        if folder and os.path.isdir(folder):
            count = sum(1 for f in os.listdir(folder)
                        if f.lower().endswith(ext))
        lines.append("| %s | `%s` | %d |" % (label, key, count))
    path = os.path.join(session_dirs.get("reports", root), "REPORT_INDEX.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path
