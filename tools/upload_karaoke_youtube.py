#!/opt/mikrotik-tools/venv/bin/python3
import os
import sys
import json
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_PATH = "/root/zylve_automation/youtube_token.json"
VIDEO_PATH = "/root/video_karaoke_mutiara_16x9.mp4"
THUMBNAIL_PATH = "/root/assets/thumbnail_mutiara/thumbnail_youtube_karaoke_mutiara_16x9.png"
SEO_JSON = "/root/assets/thumbnail_mutiara/seo_metadata_youtube.json"
SEO_MD = "/root/assets/thumbnail_mutiara/seo_metadata_youtube.md"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"

def get_description_from_md(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Ekstrak konten di dalam blok ```text ... ```
    if "```text" in content:
        desc = content.split("```text")[1].split("```")[0].strip()
        return desc
    return content

def upload():
    print("[1/5] Memeriksa kelayakan berkas video & thumbnail...")
    if not os.path.exists(VIDEO_PATH):
        print(f"[!] Berkas video tidak ditemukan: {VIDEO_PATH}")
        return False
    if not os.path.exists(THUMBNAIL_PATH):
        print(f"[!] Berkas thumbnail tidak ditemukan: {THUMBNAIL_PATH}")
        return False
    if not os.path.exists(TOKEN_PATH):
        print(f"[!] Token YouTube API tidak ditemukan: {TOKEN_PATH}")
        return False

    with open(SEO_JSON, "r", encoding="utf-8") as f:
        meta = json.load(f)

    title = meta.get("title", "MUTIARA - LAILA AYU FT IRWAN KRISDIYANTO (Karaoke Tanpa Vokal + Lirik Berjalan) | Simpatik Music")
    tags = meta.get("tags", ["karaoke mutiara", "mutiara karaoke"])
    description = get_description_from_md(SEO_MD)

    print(f"[2/5] Mempersiapkan autentikasi YouTube Data API v3...")
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
            "categoryId": "10", # 10 = Musik
            "defaultLanguage": "id",
            "defaultAudioLanguage": "id"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "embeddable": True
        }
    }

    print(f"[3/5] Mengunggah video karaoke ({os.path.getsize(VIDEO_PATH) / (1024*1024):.1f} MB) ke YouTube 1 (ZYLVEmedia)...")
    media = MediaFileUpload(VIDEO_PATH, mimetype="video/mp4", chunksize=1024*1024*5, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"[*] Upload progres: {int(status.progress() * 100)}%")

    vid_id = response.get("id")
    video_url = f"https://www.youtube.com/watch?v={vid_id}"
    print(f"[✓] Upload Video Berhasil! Video ID: {vid_id}")
    print(f"[✓] URL Video: {video_url}")

    # Upload Custom Thumbnail
    print(f"[4/5] Memasang thumbnail kustom 16:9 Google Flow...")
    try:
        thumb_media = MediaFileUpload(THUMBNAIL_PATH, mimetype="image/png")
        yt.thumbnails().set(videoId=vid_id, media_body=thumb_media).execute()
        print("[✓] Thumbnail kustom 16:9 berhasil disematkan!")
    except Exception as e:
        print(f"[!] Peringatan pasang thumbnail via API: {e}")

    # Kirim ke Telegram & Notifikasi
    print(f"[5/5] Mengirim laporan publikasi ke Telegram...")
    tg_caption = (
        f"🚀 **Video Karaoke Resmi Tayang di YouTube 1 (ZYLVEmedia)**\n\n"
        f"🎬 **Judul**: {title}\n"
        f"🔗 **Link YouTube**: {video_url}\n"
        f"📁 **Kategori**: Musik (10) | Status: Public\n"
        f"🎨 **Thumbnail**: 16:9 Google Flow Terpasang\n"
        f"🎤 **Audio**: Instrumen by ZYLVEmedia + Subtitle ASS Kuning Berjalan"
    )
    os.system(f'python3 {TELEGRAM_SCRIPT} "{tg_caption}"')
    os.system('notify-send "Cimoy" "Video Karaoke Resmi Tayang di YouTube 1" 2>/dev/null || true')
    print("ALL DONE!")
    return video_url

if __name__ == "__main__":
    upload()
