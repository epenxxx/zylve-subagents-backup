#!/opt/mikrotik-tools/venv/bin/python3
import os
import sys
import json
import time
import shutil
import glob
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_PATH = "/root/zylve_automation/youtube_token.json"
QUEUE_DIR = "/root/assets/stock_karaoke_koplo/queue"
PUBLISHED_DIR = "/root/assets/stock_karaoke_koplo/published"
LOG_FILE = "/root/logs/karaoke_upload.log"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{ts}] {msg}"
    print(full_msg)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

def get_next_queued_project():
    if not os.path.exists(QUEUE_DIR):
        os.makedirs(QUEUE_DIR, exist_ok=True)
        return None

    # Cari subdirektori di antrean
    items = sorted([os.path.join(QUEUE_DIR, d) for d in os.listdir(QUEUE_DIR) if os.path.isdir(os.path.join(QUEUE_DIR, d))])
    for item in items:
        # Validasi berkas inti
        video_files = glob.glob(os.path.join(item, "*.mp4"))
        meta_files = glob.glob(os.path.join(item, "*.json"))
        if video_files and meta_files:
            return item
    return None

def run_scheduler():
    log("=== Memulai Eksekutor Penjadwalan Upload Karaoke Dangdut Koplo 2x Sehari ===")
    project_dir = get_next_queued_project()
    if not project_dir:
        log("[!] Antrean stok karaoke kosong! Tidak ada video yang siap diunggah saat ini.")
        return False

    project_name = os.path.basename(project_dir)
    log(f"[*] Menemukan stok video dalam antrean: {project_name}")

    video_path = os.path.join(project_dir, "video.mp4")
    if not os.path.exists(video_path):
        video_files = [f for f in glob.glob(os.path.join(project_dir, "*.mp4")) if "test" not in f]
        video_path = video_files[0]

    thumb_path = os.path.join(project_dir, "thumbnail.jpg")
    if not os.path.exists(thumb_path):
        thumb_files = [f for f in glob.glob(os.path.join(project_dir, "*.jpg")) if "raw" not in f] or glob.glob(os.path.join(project_dir, "*.png"))
        thumb_path = thumb_files[0] if thumb_files else None

    meta_files = glob.glob(os.path.join(project_dir, "*.json"))
    meta_path = meta_files[0]

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    title = meta.get("title", f"KARAOKE DANGDUT KOPLO - {project_name}")
    tags = meta.get("tags", ["karaoke koplo", "dangdut koplo", "karaoke tanpa vokal"])
    
    # Ambil deskripsi
    desc_files = glob.glob(os.path.join(project_dir, "*.md"))
    if desc_files:
        with open(desc_files[0], "r", encoding="utf-8") as df:
            c = df.read()
            if "```text" in c:
                description = c.split("```text")[1].split("```")[0].strip()
            else:
                description = c.strip()
    else:
        description = meta.get("description", f"Karaoke Dangdut Koplo {title} tanpa vokal.")

    if not os.path.exists(TOKEN_PATH):
        log(f"[!] Token YouTube API tidak ditemukan di {TOKEN_PATH}")
        return False

    log("[1/4] Mengautentikasi ke YouTube Data API v3...")
    with open(TOKEN_PATH, "r") as f:
        t = json.load(f)

    creds = Credentials(
        token=t.get("token"),
        refresh_token=t.get("refresh_token"),
        token_uri=t.get("token_uri"),
        client_id=t.get("client_id"),
        client_secret=t.get("client_secret"),
        scopes=t.get("scopes")
    )
    yt = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags[:20],
            "categoryId": "10",  # Kategori Musik
            "defaultLanguage": "id",
            "defaultAudioLanguage": "id"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "embeddable": True
        }
    }

    fsize_mb = os.path.getsize(video_path) / (1024 * 1024)
    log(f"[2/4] Mengunggah video ({fsize_mb:.1f} MB) ke YouTube 1 (ZYLVEmedia)...")
    media = MediaFileUpload(video_path, mimetype="video/mp4", chunksize=1024*1024*5, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            log(f"[*] Upload progres: {int(status.progress() * 100)}%")

    vid_id = response.get("id")
    video_url = f"https://www.youtube.com/watch?v={vid_id}"
    log(f"[✓] Berhasil upload! Video ID: {vid_id} | Link: {video_url}")

    # Pasang thumbnail
    if thumb_path and os.path.exists(thumb_path):
        log(f"[3/4] Memasang thumbnail kustom 16:9 Google Flow...")
        try:
            mime = "image/jpeg" if thumb_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
            thumb_media = MediaFileUpload(thumb_path, mimetype=mime)
            yt.thumbnails().set(videoId=vid_id, media_body=thumb_media).execute()
            log("[✓] Thumbnail 16:9 kustom resmi terpasang!")
        except Exception as e:
            log(f"[!] Gagal pasang thumbnail kustom: {e}")

    # Catat ke metadata dan pindah ke published
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    dest_dir = os.path.join(PUBLISHED_DIR, project_name)
    meta["published_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    meta["video_id"] = vid_id
    meta["youtube_url"] = video_url
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    shutil.move(project_dir, dest_dir)
    log(f"[✓] Direktori proyek dipindahkan ke arsip: {dest_dir}")

    # Kirim laporan Telegram
    log("[4/4] Mengirim notifikasi publikasi ke Telegram...")
    tg_caption = (
        f"🚀 **Jadwal Tayang Otomatis 2x Sehari: Dangdut Koplo Tayang!**\n\n"
        f"🎬 **Judul**: {title}\n"
        f"🔗 **Link YouTube**: {video_url}\n"
        f"📁 **Kategori**: Musik (10) | Status: Public\n"
        f"🎨 **Thumbnail**: 16:9 Google Flow Terpasang\n"
        f"🎤 **Format**: 1080p 30fps VAAPI + Subtitle ASS Kuning Berjalan"
    )
    os.system(f'python3 {TELEGRAM_SCRIPT} "{tg_caption}"')
    os.system('notify-send "Cimoy" "Upload Terjadwal Dangdut Koplo Sukses Tayang" 2>/dev/null || true')
    return True

if __name__ == "__main__":
    run_scheduler()
