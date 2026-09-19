#!/usr/bin/env python3
import os
import sys
import time
import glob

TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"
LOG_FILE = "/root/logs/karaoke_cleaner.log"

# Direktori & pola file yang dipantau
WATCH_PATTERNS = [
    "/root/video_karaoke_*.mp4",
    "/root/projects/karaoke_*/*.mp4",
    "/root/projects/karaoke_*/*.wav",
    "/root/.gemini/antigravity-cli/scratch/karaoke/*.wav",
    "/root/.gemini/antigravity-cli/scratch/karaoke/bg_video.mp4",
    "/root/.gemini/antigravity-cli/scratch/karaoke/input.mp3",
    "/root/.gemini/antigravity-cli/scratch/karaoke/*.mp4",
    "/root/assets/thumbnail_mutiara/*.jpg",
    "/root/assets/thumbnail_mutiara/*.png",
    "/root/assets/stock_karaoke_koplo/published/*/*.mp4",
    "/root/assets/stock_karaoke_koplo/published/*/*.wav",
    "/root/assets/stock_karaoke_koplo/published/*/*.mp3",
    "/root/assets/stock_karaoke_koplo/published/*/*.jpg",
    "/root/assets/stock_karaoke_koplo/published/*/*.png",
    "/root/assets/stock_karaoke_koplo/published/*/*.webp",
]

# File yang DILARANG dihapus (metadata arsip, skrip, dan konfigurasi)
PRESERVE_EXTENSIONS = [".json", ".md", ".ass", ".py", ".sh", ".log"]

def clean_old_karaoke_files():
    os.makedirs("/root/logs", exist_ok=True)
    now = time.time()
    retention_seconds = 24 * 3600  # 24 Jam
    deleted_files = []
    freed_bytes = 0

    for pattern in WATCH_PATTERNS:
        for file_path in glob.glob(pattern):
            if not os.path.isfile(file_path):
                continue
            
            # Lewati file metadata
            ext = os.path.splitext(file_path)[1].lower()
            if ext in PRESERVE_EXTENSIONS:
                continue

            # Cek umur file
            mtime = os.path.getmtime(file_path)
            age_hours = (now - mtime) / 3600

            if (now - mtime) > retention_seconds:
                try:
                    fsize = os.path.getsize(file_path)
                    os.remove(file_path)
                    freed_bytes += fsize
                    deleted_files.append((file_path, fsize, age_hours))
                except Exception as e:
                    print(f"[!] Gagal hapus {file_path}: {e}")

    log_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Pengecekan cleaner selesai. "
    if deleted_files:
        freed_mb = freed_bytes / (1024 * 1024)
        log_msg += f"Dibersihkan {len(deleted_files)} file (>24 jam pasca-upload). Ruang pulih: {freed_mb:.1f} MB.\n"
        for path, sz, age in deleted_files:
            log_msg += f"  - Hapus: {os.path.basename(path)} ({sz/(1024*1024):.1f} MB, umur: {age:.1f} jam)\n"
        
        # Kirim info ke Telegram jika ada file yang dihapus
        tg_text = (
            f"🧹 **Agent 7 (Storage Cleaner) Berhasil Bersih-Bersih**\n\n"
            f"📁 **Total File Dibersihkan**: {len(deleted_files)} file (>24 jam)\n"
            f"💾 **Ruang Disk Dipulihkan**: {freed_mb:.1f} MB\n"
            f"📌 Metadata (.json, .md, .ass) tetap aman tersimpan."
        )
        os.system(f'python3 {TELEGRAM_SCRIPT} "{tg_text}"')
    else:
        log_msg += "Tidak ada file media karaoke lokal yang melebihi 24 jam.\n"

    print(log_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_msg)

if __name__ == "__main__":
    clean_old_karaoke_files()
