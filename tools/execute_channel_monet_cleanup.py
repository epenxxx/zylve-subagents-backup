#!/opt/mikrotik-tools/venv/bin/python3
"""
execute_channel_monet_cleanup.py
Eksekusi Penataan & Pembersihan Channel YouTube ZYLVEmedia Menuju Monetisasi (22 September 2026):
1. Hapus video sampah pemicu Reused Content (ASMR 0 view).
2. Perbaiki metadata & tags 9 video karaoke baru (isi tags kosong, tambah klausa orisinalitas ZYLVEmedia).
3. Buat Playlist Tematik Autoplay untuk melipatgandakan jam tayang penonton.
"""

import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = "/root/zylve_automation/youtube_token.json"

def get_yt():
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Token {TOKEN_PATH} tidak ditemukan.")
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)
    creds = Credentials.from_authorized_user_info(token_data)
    return build("youtube", "v3", credentials=creds)

def step1_delete_spam_videos(yt):
    print("\n--- [LANGKAH 1: PEMBERSIHAN VIDEO SAMPAH ASMR] ---")
    spam_ids = ["49KyuQHiI1s", "Vr1hWTp8UGY"]
    for vid in spam_ids:
        try:
            print(f"[*] Menghapus video pemicu Reused Content (ID: {vid})...")
            yt.videos().delete(id=vid).execute()
            print(f"[✓] Berhasil dihapus permanen: {vid}")
        except Exception as e:
            print(f"[!] Gagal/sudah dihapus {vid}: {e}")

def step2_optimize_karaoke_metadata(yt):
    print("\n--- [LANGKAH 2: OPTIMASI METADATA & TAGS 9 VIDEO KARAOKE] ---")
    
    # Mapping optimasi video karaoke
    metadata_map = {
        "TbdpcWoHxjk": {
            "title": "DIRANTAI DIGELANGI RINDU - HAPPY ASMARA | Karaoke Nada Asli (Lirik) by ZYLVEmedia",
            "tags": [
                "dirantai digelangi rindu karaoke", "happy asmara karaoke", "karaoke happy asmara dirantai digelangi rindu",
                "karaoke dangdut koplo", "karaoke nada asli", "karaoke tanpa vokal", "lirik berjalan karaoke",
                "happy asmara terbaru", "dangdut koplo viral", "lagu dangdut karaoke", "karaoke hd 1080p",
                "zylvemedia karaoke", "lirik dirantai digelangi rindu", "karaoke minus one", "nada pas wanita",
                "karaoke indonesia", "lagu rindu karaoke", "dangdut campursari", "karaoke full lirik"
            ]
        },
        "UgbyrD1lGxA": {
            "title": "SALAH APA - IPANK | Karaoke Pop Minang Nada Asli (Lirik Berjalan) by ZYLVEmedia",
            "tags": [
                "salah apa ipank karaoke", "karaoke ipank salah apa", "ipank karaoke pop minang",
                "karaoke pop minang", "lagu minang karaoke", "karaoke tanpa vokal", "lirik berjalan",
                "karaoke nada asli", "ipank lagu terbaru", "karaoke zylvemedia", "lagu melayu karaoke",
                "karaoke minus one", "ipank official karaoke", "karaoke hd 1080p", "nada pas pria"
            ]
        },
        "9VkiGBzz3lo": {
            "title": "MUTIARA - Laila Ayu ft. Irwan Krisdiyanto | Karaoke Duet Dangdut (Lirik) by ZYLVEmedia",
            "tags": [
                "karaoke mutiara", "mutiara laila ayu irwan", "karaoke dangdut koplo", "karaoke duet mutiara",
                "karaoke nada asli", "laila ayu ft irwan", "dangdut koplo karaoke", "karaoke tanpa vokal",
                "karaoke lirik berjalan", "simpatik music", "zylvemedia karaoke", "karaoke minus one"
            ]
        },
        "3YbgSFSxIi4": {
            "title": "MUTIARA - IPANK | Karaoke Pop Melayu Nada Asli (Lirik Berjalan) by ZYLVEmedia",
            "tags": [
                "ipank mutiara karaoke", "karaoke ipank mutiara", "ipank pop melayu", "karaoke melayu",
                "karaoke nada asli", "karaoke tanpa vokal", "lirik berjalan", "ipank terbaru", "zylvemedia karaoke"
            ]
        },
        "kIFJd9dQLvs": {
            "title": "SALAH APA - Laila Ayu ft. Irwan Krisdiyanto | Karaoke Koplo (Lirik) by ZYLVEmedia",
            "tags": [
                "salah apa karaoke", "karaoke salah apa laila ayu", "karaoke koplo", "dangdut koplo karaoke",
                "irwan krisdiyanto karaoke", "karaoke tanpa vokal", "lirik berjalan", "zylvemedia"
            ]
        },
        "pdh04oiJZJ8": {
            "title": "PERCERAIAN LARA - IPANK | Karaoke Pop Minang Nada Asli (Lirik) by ZYLVEmedia",
            "tags": [
                "perceraian lara ipank karaoke", "karaoke perceraian lara", "lagu minang karaoke",
                "ipank karaoke", "karaoke tanpa vokal", "lirik berjalan", "zylvemedia karaoke"
            ]
        },
        "FhSWdQ0H7x0": {
            "title": "KAMU - KANGEN BAND | Karaoke Pop Melayu Nada Asli (Lirik) by ZYLVEmedia",
            "tags": [
                "kamu kangen band karaoke", "kangen band kamu karaoke", "karaoke kangen band",
                "pop melayu karaoke", "andika mahesa karaoke", "karaoke tanpa vokal", "lirik berjalan", "zylvemedia"
            ]
        },
        "qU88HbJ7T7A": {
            "title": "HELIKOPTER TURUN KE PADANG - SABRINAAA | Karaoke Versi Kenong (Lirik) by ZYLVEmedia",
            "tags": [
                "helikopter turun ke padang karaoke", "sabrinaaa karaoke", "karaoke kenong",
                "karaoke viral tiktok", "karaoke tanpa vokal", "lirik berjalan", "zylvemedia karaoke"
            ]
        },
        "27DFNlbtQ_4": {
            "title": "Salah Apa - Cut Rani Auliza | Karaoke Dangdut Syahdu (Lirik) by ZYLVEmedia",
            "tags": [
                "cut rani auliza salah apa karaoke", "karaoke cut rani", "dangdut syahdu karaoke",
                "karaoke nada asli", "karaoke tanpa vokal", "lirik berjalan", "zylvemedia karaoke"
            ]
        }
    }

    klausa_orisinal = (
        "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎤 INFORMASI KARYA & PRODUKSI KARAOKE (ZYLVEmedia):\n"
        "• Seluruh sajian audio instrumen bebas vokal diproses dan dimastering secara mandiri oleh Studio ZYLVEmedia.\n"
        "• Video latar menggunakan rekaman visual alam sinematik berlisensi resmi berkualitas Full HD.\n"
        "• Penyajian subtitle lirik sinkron dirancang khusus untuk kenyamanan latihan vokal & pecinta karaoke.\n"
        "• Hak cipta lagu dan komposisi musik tetap milik pencipta/label resmi terkait.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    for vid, meta in metadata_map.items():
        try:
            print(f"[*] Mengambil data video {vid}...")
            v_res = yt.videos().list(part="snippet", id=vid).execute()
            items = v_res.get("items", [])
            if not items:
                print(f"[!] Video {vid} tidak ditemukan.")
                continue

            snippet = items[0]["snippet"]
            curr_desc = snippet.get("description", "")
            
            # Tambahkan klausa orisinal jika belum ada
            if "ZYLVEmedia Karaoke Studio" not in curr_desc and "INFORMASI KARYA & PRODUKSI KARAOKE" not in curr_desc:
                new_desc = curr_desc.strip() + klausa_orisinal
            else:
                new_desc = curr_desc

            # Update snippet
            snippet["title"] = meta["title"]
            snippet["tags"] = meta["tags"]
            snippet["description"] = new_desc

            print(f"[*] Mengupdate video: {meta['title'][:45]}... (Tags: {len(meta['tags'])})")
            yt.videos().update(
                part="snippet",
                body={
                    "id": vid,
                    "snippet": snippet
                }
            ).execute()
            print(f"[✓] Berhasil diupdate: {vid}")
        except Exception as e:
            print(f"[❌] Gagal update {vid}: {e}")

def step3_create_autoplay_playlists(yt):
    print("\n--- [LANGKAH 3: PEMBUATAN PLAYLIST TEMATIK AUTOPLAY] ---")
    playlists_config = [
        {
            "title": "Karaoke Dangdut & Koplo Terpopuler - ZYLVEmedia",
            "desc": "Kumpulan lagu karaoke dangdut koplo terpopuler dengan lirik berjalan dan nada asli untuk latihan vokal.",
            "videos": ["TbdpcWoHxjk", "27DFNlbtQ_4", "9VkiGBzz3lo", "kIFJd9dQLvs", "qU88HbJ7T7A"]
        },
        {
            "title": "Karaoke Pop Melayu & Minang Syahdu - ZYLVEmedia",
            "desc": "Koleksi karaoke lagu pop Minang dan Melayu syahdu nada pas dan lirik berjalan by ZYLVEmedia.",
            "videos": ["UgbyrD1lGxA", "pdh04oiJZJ8", "3YbgSFSxIi4", "FhSWdQ0H7x0"]
        }
    ]

    for pl in playlists_config:
        try:
            print(f"[*] Membuat playlist: {pl['title']}...")
            pl_body = {
                "snippet": {
                    "title": pl["title"],
                    "description": pl["desc"],
                    "defaultLanguage": "id"
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
            pl_res = yt.playlists().insert(part="snippet,status", body=pl_body).execute()
            pl_id = pl_res["id"]
            print(f"[✓] Playlist berhasil dibuat (ID: {pl_id})")

            for vid in pl["videos"]:
                try:
                    yt.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": pl_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": vid
                                }
                            }
                        }
                    ).execute()
                    print(f"    + Video {vid} ditambahkan ke playlist.")
                except Exception as ve:
                    print(f"    - Gagal tambah video {vid}: {ve}")
        except Exception as e:
            print(f"[!] Gagal buat playlist {pl['title']}: {e}")

if __name__ == "__main__":
    yt_client = get_yt()
    step1_delete_spam_videos(yt_client)
    step2_optimize_karaoke_metadata(yt_client)
    step3_create_autoplay_playlists(yt_client)
    print("\n[🎯] SEMUA EKSEKUSI PEMULIHAN CHANNEL TUNTAS!")
