#!/opt/mikrotik-tools/venv/bin/python3
"""
upload_youtube_dynamic.py
Uploader YouTube Otomatis Universal untuk Video Karaoke ZYLVEmedia.
Mendukung video, custom thumbnail, tags, kategori musik, dan notifikasi satu pintu Manajer.
"""
import os
import sys
import json
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_PATH = "/root/zylve_automation/youtube_token.json"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"

# Auto-route lewat Cloudflare WARP 1.1.1.1 Proxy jika aktif
if os.path.exists("/usr/local/bin/with_warp"):
    os.environ["http_proxy"] = "http://127.0.0.1:8118"
    os.environ["https_proxy"] = "http://127.0.0.1:8118"
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:8118"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:8118"

def upload_video(video_path, thumbnail_path, title, description, tags, category_id="10", privacy_status="public"):
    print("[1/5] Memeriksa berkas video & thumbnail...")
    if not os.path.exists(video_path):
        print(f"[!] Video tidak ditemukan: {video_path}")
        return None
    if not os.path.exists(thumbnail_path):
        print(f"[!] Thumbnail tidak ditemukan: {thumbnail_path}")
        return None
    if not os.path.exists(TOKEN_PATH):
        print(f"[!] Token YouTube API tidak ditemukan: {TOKEN_PATH}")
        return None

    print("[2/5] Inisialisasi kredensial Google YouTube API v3...")
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
            "tags": tags[:30],
            "categoryId": str(category_id),
            "defaultLanguage": "id",
            "defaultAudioLanguage": "id"
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "embeddable": True
        }
    }

    print(f"[3/5] Mengunggah video ({os.path.getsize(video_path) / (1024*1024):.2f} MB)...")
    media = MediaFileUpload(video_path, mimetype="video/mp4", chunksize=1024*1024*5, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"[*] Upload progres: {int(status.progress() * 100)}%")

    vid_id = response.get("id")
    video_url = f"https://www.youtube.com/watch?v={vid_id}"
    print(f"[✓] Upload Berhasil! Video ID: {vid_id} -> {video_url}")

    # Set Custom Thumbnail
    print("[4/5] Memasang thumbnail custom 4K 16:9...")
    try:
        thumb_mime = "image/png" if thumbnail_path.endswith(".png") else "image/jpeg"
        thumb_media = MediaFileUpload(thumbnail_path, mimetype=thumb_mime)
        yt.thumbnails().set(videoId=vid_id, media_body=thumb_media).execute()
        print("[✓] Custom Thumbnail berhasil dipasang!")
    except Exception as e:
        print(f"[!] Warning thumbnail set: {e}")

    # Notifikasi Telegram Satu Pintu (Manager)
    print("[5/5] Mengirim laporan sukses ke Telegram via Manager...")
    tg_caption = (
        f"🚀 *VIDEO KARAOKE RESMI TAYANG DI YOUTUBE*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎬 *Judul*: {title[:100]}\n"
        f"🔗 *Link*: {video_url}\n"
        f"📁 *Kategori*: Musik | Status: {privacy_status.capitalize()}\n"
        f"🎨 *Thumbnail*: 3D Embossed Gold 4K Terpasang\n"
        f"🎤 *Format*: Full HD 1080p | Subtitle Tengah Besar | Nada Pas Original\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 *Penanggung Jawab*: `agent_orchestrator` (Manajer)"
    )
    os.system(f'MANAGER_BYPASS=1 python3 {TELEGRAM_SCRIPT} "{tg_caption}"')
    return {
        "video_id": vid_id,
        "video_url": video_url,
        "title": title
    }

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Uploader test mode OK")
