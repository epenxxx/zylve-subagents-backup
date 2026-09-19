#!/opt/mikrotik-tools/venv/bin/python3
import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = "/root/zylve_automation/youtube_token.json"
SEO_MD = "/root/assets/thumbnail_mutiara/seo_metadata_youtube.md"
SEO_JSON = "/root/assets/thumbnail_mutiara/seo_metadata_youtube.json"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"
VID_ID = "9VkiGBzz3lo"

NEW_TITLE = "MUTIARA - Laila Ayu ft. Irwan Krisdiyanto (Karaoke by ZYLVEmedia + Lirik) Simpatik Music"

NEW_DESC = """Lagu Mutiara dari Laila Ayu ft. Irwan Krisdiyanto versi instrumen karaoke bersih tanpa vokal. Aransemen asli Simpatik Music, ketukan dan tempo pas buat yang mau latian vokal atau karaokean duet bareng pasangan/teman di rumah.

Audio sudah diatur jernih dengan lirik berjalan tepat di tengah layar biar gampang diikutin.

KREDIT KARYA ASLI:
Lagu: Mutiara
Ciptaan: G Diana
Vokal: Laila Ayu & Irwan Krisdiyanto
Musik: Simpatik Music Official
Pemain Musik:
- Kendang: Guk Matt
- Bass: Kaji Oga
- Lead Gitar: Sodik
- Gitar Ritem: Roy
- Keyboard 1: Aviv
- Keyboard 2: Nopi
- Tamborin: Deby
- Suling: Kabul

Tonton video klip resminya di kanal Simpatik Music:
https://youtube.com/@simpatikmusic

---
LIRIK MUTIARA:

Engkaukah mutiara itu?
Rela kuselami di laut biru
Tingkahmu bagai purnama
Paras bertaburkan cahaya

Mantra apakah yang kau berikan
sehingga bayangmu menghantui?
Selalu terbayang angan
di setiap mimpi malam
Selalu terbayang angan menjadi igauan

Dari ujung kuku hingga ujung rambutku
Mengapa di hati ini lain terasa?
Meski ku tak kenal siapa namamu
sungguh damai hati ini bila bersama

Adakah kenyamanan di hatimu
di saat kau melirik dan memandangku?
Dan seakan kau ingin menyapaku
Oh... apakah ini fatamorgana?
atau hanya khayalan semata?

Mutiara... itu dirimu
Purnama... itu senyummu
Di dalam kalbu terukir indah namamu
Kusimpan rapat di dalam relung hatiku
---

Mau request lagu karaoke lainnya? Tulis judulnya di kolom komentar ya. Kalo suka, bantu like dan share ke temen-temen tongkrongan. Selamat nyanyi!

#karaoke #mutiara #lailaayu #irwankrisdiyanto #simpatikmusic #karaokedangdut #minusone #liriklagu"""

NEW_TAGS = [
    "karaoke mutiara",
    "mutiara karaoke",
    "mutiara laila ayu irwan krisdiyanto karaoke",
    "mutiara by ZYLVEmedia",
    "karaoke mutiara nada asli",
    "karaoke dangdut koplo",
    "karaoke duet mutiara",
    "simpatik music karaoke",
    "lagu mutiara karaoke",
    "mutiara lirik berjalan",
    "karaoke dangdut terbaru"
]

def update_youtube():
    print("[1/3] Otentikasi YouTube Data API v3...")
    with open(TOKEN_PATH) as f:
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

    print(f"[2/3] Memperbarui metadata video {VID_ID} dengan gaya humanis anti-robot...")
    body = {
        "id": VID_ID,
        "snippet": {
            "title": NEW_TITLE,
            "description": NEW_DESC,
            "tags": NEW_TAGS,
            "categoryId": "10",
            "defaultLanguage": "id",
            "defaultAudioLanguage": "id"
        }
    }

    res = yt.videos().update(part="snippet", body=body).execute()
    print("[✓] Update YouTube Berhasil!")
    print("Judul Baru:", res["snippet"]["title"])

    # Update local files
    print("[3/3] Menyimpan berkas lokal & artefak...")
    with open(SEO_MD, "w", encoding="utf-8") as f:
        f.write(f"# Paket SEO YouTube Karaoke (Human-Friendly No AI Slop)\n\n## Judul:\n{NEW_TITLE}\n\n## Deskripsi:\n```text\n{NEW_DESC}\n```\n")
    
    with open(SEO_JSON, "w", encoding="utf-8") as f:
        json.dump({"title": NEW_TITLE, "tags": NEW_TAGS, "description": NEW_DESC}, f, indent=2)

    os.system(f"cp {SEO_MD} {SEO_JSON} /root/.gemini/antigravity-cli/brain/1e762963-a2a4-4982-b3f1-9626ac5bbc2c/")

    # Notifikasi Telegram
    tg_text = (
        f"✍️ **Metadata Video YouTube Diperbarui (Gaya Humanis No-AI-Slop)**\n\n"
        f"🎬 **Judul Baru**: {NEW_TITLE}\n"
        f"🔗 **Link**: https://www.youtube.com/watch?v={VID_ID}\n"
        f"✨ **Karakter**: Santai, luwes, grounded pecinta dangdut asli, bebas template kaku AI."
    )
    os.system(f'python3 {TELEGRAM_SCRIPT} "{tg_text}"')
    os.system('notify-send "Cimoy" "Metadata YouTube diperbarui gaya humanis no-ai-slop" 2>/dev/null || true')
    print("ALL DONE!")

if __name__ == "__main__":
    update_youtube()
