#!/opt/mikrotik-tools/venv/bin/python3
"""
Pipeline Otomatis Produksi & Penjadwalan Karaoke 3x Sehari (Agent 1 s/d Agent 6)
Jadwal Upload:
- Slot 1: 11:00 WIB (Siang)
- Slot 2: 16:30 WIB (Sore)
- Slot 3: 20:00 WIB (Malam)
"""

import os
import sys
import json
import time
import subprocess
import glob
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

FEEDBACK_FILE = "/root/zylve_automation/karaoke_agent1_feedback.json"
QUEUE_DIR = "/root/assets/stock_karaoke_koplo/queue"
PUBLISHED_DIR = "/root/assets/stock_karaoke_koplo/published"
TOKEN_PATH = "/root/zylve_automation/youtube_token.json"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"
LOG_FILE = "/root/logs/karaoke_auto_producer.log"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_slot_upload():
    log("=== Eksekusi Slot Upload Karaoke YouTube 1 (3x Sehari) ===")
    
    # 1. Pastikan feedback analis terupdate
    if os.path.exists("/root/tools/youtube_growth_analyst.py"):
        try:
            subprocess.run(["/opt/mikrotik-tools/venv/bin/python3", "/root/tools/youtube_growth_analyst.py"], check=True)
            log("[✓] Analis pertumbuhan YouTube 1 sukses sinkron data pasar.")
        except Exception as e:
            log(f"[!] Warning jalankan growth analyst: {e}")

    # 2. Cek apakah ada antrean di folder queue
    # Menggunakan scheduler yang sudah terverifikasi
    res = subprocess.run(["/opt/mikrotik-tools/venv/bin/python3", "/root/tools/karaoke_auto_scheduler.py"], capture_output=True, text=True)
    log(res.stdout)
    if res.stderr:
        log(f"Error output: {res.stderr}")

if __name__ == "__main__":
    run_slot_upload()
