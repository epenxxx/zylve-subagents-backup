#!/opt/mikrotik-tools/venv/bin/python3
"""
Batch Renderer Stok Video Karaoke YouTube 1 (3 Video Setiap Jam 08:00 Pagi)
Anti-Duplikasi Ketat: Memeriksa riwayat karaoke_production_log.json
"""

import os
import sys
import json
import time
import subprocess
import glob
import re

QUEUE_DIR = "/root/assets/stock_karaoke_koplo/queue"
FEEDBACK_FILE = "/root/zylve_automation/karaoke_agent1_feedback.json"
HISTORY_LOG = "/root/zylve_automation/karaoke_production_log.json"
LOG_FILE = "/root/logs/karaoke_stock_render.log"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    full = f"[{ts}] {msg}"
    print(full)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full + "\n")

def normalize_title(title):
    t = title.lower()
    t = re.sub(r"\[.*?\]|\(.*?\)", "", t)
    t = re.sub(r"[^\w\s]", "", t)
    return " ".join(t.split())

def is_duplicate(title, ref_id, history):
    clean = normalize_title(title)
    if ref_id and ref_id in history.get("processed_ids", []):
        return True
    for item in history.get("processed_titles", []):
        if item in clean or clean in item:
            return True
    return False

def run_batch_render():
    log("=== MEMULAI BATCH RENDER 3 STOK KARAOKE (08:00 PAGI) ===")
    os.makedirs(QUEUE_DIR, exist_ok=True)

    # 1. Update analisis tren
    if os.path.exists("/root/tools/youtube_growth_analyst.py"):
        try:
            subprocess.run(["/opt/mikrotik-tools/venv/bin/python3", "/root/tools/youtube_growth_analyst.py"], check=True)
            log("[✓] Analisis tren YouTube terupdate.")
        except Exception as e:
            log(f"[!] Error growth analyst: {e}")

    if not os.path.exists(FEEDBACK_FILE):
        log("[!] File feedback tidak ditemukan.")
        return False

    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        fb_data = json.load(f)

    # Muat log anti duplikasi
    history = {"processed_titles": [], "processed_ids": [], "history": []}
    if os.path.exists(HISTORY_LOG):
        with open(HISTORY_LOG, "r", encoding="utf-8") as f:
            history = json.load(f)

    pool = fb_data.get("recommended_songs_pool", [])
    if not pool:
        log("[!] Pool lagu kosong.")
        return False

    log(f"[*] Melakukan filter anti-duplikasi pada {len(pool)} rekomendasi lagu...")

    selected_songs = []
    for item in pool:
        ref_title = item.get("reference_title", "")
        ref_id = item.get("reference_id", "")
        if is_duplicate(ref_title, ref_id, history):
            log(f"[-] LEWATI (Sudah pernah dibuat / duplikat): {ref_title}")
            continue
        selected_songs.append(item)
        if len(selected_songs) >= 3:
            break

    if not selected_songs:
        log("[!] Tidak ada lagu baru yang lolos filter anti-duplikasi!")
        return False

    log(f"[✓] Terpilih {len(selected_songs)} lagu baru unik bebas duplikat.")

    rendered_count = 0
    for item in selected_songs:
        ref_title = item.get("reference_title", "Karaoke Song")
        ref_id = item.get("reference_id", "")
        log(f"[*] Memproses stok {rendered_count + 1}/3: {ref_title} (ID: {ref_id})")

        clean_norm = normalize_title(ref_title)
        folder_slug = clean_norm.replace(" ", "_")[:30]
        project_folder = os.path.join(QUEUE_DIR, f"stock_{int(time.time())}_{folder_slug}")
        os.makedirs(project_folder, exist_ok=True)

        meta = {
            "title": f"{ref_title} | Karaoke by ZYLVEmedia",
            "reference_id": ref_id,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ready_in_queue"
        }
        with open(os.path.join(project_folder, "metadata.json"), "w", encoding="utf-8") as mf:
            json.dump(meta, mf, indent=2)

        # Catat ke log anti-duplikasi
        history["processed_titles"].append(clean_norm)
        if ref_id:
            history["processed_ids"].append(ref_id)
        history["history"].append({
            "title": ref_title,
            "reference_id": ref_id,
            "added_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "folder": project_folder
        })
        rendered_count += 1

    with open(HISTORY_LOG, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    log(f"[✓] Batch render tuntas. {rendered_count} stok lagu unik terdaftar di queue & dicatat di {HISTORY_LOG}.")

    if os.path.exists(TELEGRAM_SCRIPT):
        os.system(f'/opt/mikrotik-tools/venv/bin/python3 "{TELEGRAM_SCRIPT}" "✅ <b>Batch Render Sukses (Anti-Duplikat)!</b>\n3 Stok lagu unik resmi dicatat ke log & antrean YouTube 1." 2>/dev/null || true')

if __name__ == "__main__":
    run_batch_render()
