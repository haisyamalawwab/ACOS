"""Sinkronisasi hasil ke Google Drive standar (opsional, best-effort)."""
from __future__ import annotations

import os
import shutil

URL = "https://drive.google.com/drive/folders/1AEzC-dncJAweHPHUPdnFfPHxbsCa83_K"
ACOS_INDO = "/content/drive/MyDrive/ACOS/ACOS-IndoBERT"
SUBDIR = "ACOS_V51_BACKUP"


def detect(subdir: str = SUBDIR) -> dict:
    """Kembalikan {mounted, backup_dir, acos_indo, url}."""
    mounted = os.path.exists("/content/drive/MyDrive")
    backup = os.path.join("/content/drive/MyDrive", subdir) if mounted else None
    if mounted:
        os.makedirs(backup, exist_ok=True)
        os.makedirs(ACOS_INDO, exist_ok=True)
    return {"mounted": mounted, "backup_dir": backup, "acos_indo": ACOS_INDO, "url": URL}


def sync(source: str, target_sub: str = "", *, enabled: bool = True, backup_dir: str | None = None) -> str | None:
    """Mirror file/dir ke backup Drive; kembalikan dest atau None bila skip/gagal."""
    if not enabled or not backup_dir or not os.path.exists(source):
        return None
    try:
        dest_root = os.path.join(backup_dir, target_sub) if target_sub else backup_dir
        os.makedirs(dest_root, exist_ok=True)
        if os.path.isdir(source):
            dest = os.path.join(dest_root, os.path.basename(source.rstrip("/")))
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
            return dest
        shutil.copy2(source, dest_root)
        return os.path.join(dest_root, os.path.basename(source))
    except Exception:
        return None
