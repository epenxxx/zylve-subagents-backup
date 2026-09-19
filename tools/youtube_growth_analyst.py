#!/opt/mikrotik-tools/venv/bin/python3
"""
Subagen Analis Pertumbuhan & Monetisasi YouTube 1 (karaoke_growth_analyst)
Tugas:
1. Audit performa channel YouTube 1 (views, subscribers, watch time retention).
2. Analisa lagu-lagu karaoke paling dicari & trending (Indonesia + Internasional/India/Pop/Dangdut).
3. Beri masukan rekomendasi presisi ke Agent 1 (karaoke_song_researcher).
4. Susun daftar antrean lagu prioritas (high search volume, high monet potential).
"""

import os
import sys
import json
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = "/root/zylve_automation/youtube_token.json"
FEEDBACK_FILE = "/root/zylve_automation/karaoke_agent1_feedback.json"
REPORT_MD = "/root/zylve_automation/youtube_growth_report.md"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"

# Kueri riset tren karaoke (Indonesia + Global)
SEARCH_BENCHMARKS = [
    "karaoke indonesia lirik tanpa vokal",
    "karaoke pop indonesia terpopuler",
    "karaoke dangdut koplo viral",
    "bollywood karaoke no vocal with lyrics",
    "english pop acoustic karaoke no vocal"
]

def analyze_channel(yt):
    print("[1/3] Mengambil data statistik channel YouTube 1...")
    ch_req = yt.channels().list(part="snippet,statistics,contentDetails", mine=True)
    ch_res = ch_req.execute()
    item = ch_res["items"][0]
    
    stats = {
        "title": item["snippet"]["title"],
        "id": item["id"],
        "subscribers": int(item["statistics"].get("subscriberCount", 0)),
        "views": int(item["statistics"].get("viewCount", 0)),
        "video_count": int(item["statistics"].get("videoCount", 0)),
        "uploads_playlist": item["contentDetails"]["relatedPlaylists"]["uploads"]
    }
    
    # Ambil 10 video terakhir
    pl_req = yt.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=stats["uploads_playlist"],
        maxResults=10
    )
    pl_res = pl_req.execute()
    video_ids = [v["contentDetails"]["videoId"] for v in pl_res.get("items", [])]
    
    recent_videos = []
    if video_ids:
        v_req = yt.videos().list(part="snippet,statistics", id=",".join(video_ids))
        v_res = v_req.execute()
        for v in v_res.get("items", []):
            recent_videos.append({
                "id": v["id"],
                "title": v["snippet"]["title"],
                "views": int(v["statistics"].get("viewCount", 0)),
                "likes": int(v["statistics"].get("likeCount", 0)),
                "comments": int(v["statistics"].get("commentCount", 0)),
                "published_at": v["snippet"]["publishedAt"]
            })
    return stats, recent_videos

def research_trending_karaoke(yt):
    print("[2/3] Menganalisa tren lagu karaoke bervolume tinggi (ID & Global)...")
    recommendations = []
    seen_titles = set()
    
    for q in SEARCH_BENCHMARKS:
        try:
            res = yt.search().list(
                part="snippet",
                q=q,
                type="video",
                order="viewCount",
                maxResults=4
            ).execute()
            
            for item in res.get("items", []):
                t = item["snippet"]["title"]
                vid = item["id"]["videoId"]
                clean_title = t.replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&")
                if clean_title not in seen_titles:
                    seen_titles.add(clean_title)
                    recommendations.append({
                        "query_origin": q,
                        "reference_title": clean_title,
                        "reference_id": vid,
                        "channel": item["snippet"]["channelTitle"]
                    })
        except Exception as e:
            print(f"[!] Error querying {q}: {e}")
            
    return recommendations

def build_feedback_and_report(stats, recent_videos, trending):
    print("[3/3] Meracik feedback tajam untuk Agent 1 dan laporan monetisasi...")
    
    # Kebutuhan monetisasi YouTube Partner Program (YPP)
    subs_needed = max(0, 1000 - stats["subscribers"])
    
    # Masukan strategi konkrit
    growth_tips = [
        "Jaga konsistensi 3x sehari pada jam prime karaoke (11:00, 16:30, 20:00 WIB).",
        "Wajib nada standar & by ZYLVEmedia bersih bebas sisa vokal (ZeroGPU Hugging Face).",
        "Subtitle ASS lirik berjalan kuning wajib font 76 tengah bawah agar ramah layar HP & TV.",
        "Thumbnail wajib teks 3D emas 'KARAOKE' + badge 'NO VOCAL' + mikrofon vintage + rasio 16:9.",
        "Diversifikasi genre: 1 Pop/Galau Indo, 1 Dangdut Koplo, 1 Bollywood/Western per hari untuk jangkau audiens internasional (RPM lebih tinggi)."
    ]
    
    feedback_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "channel_summary": stats,
        "monetization_status": {
            "subs_current": stats["subscribers"],
            "subs_target": 1000,
            "subs_gap": subs_needed,
            "status": "Monetized Sub Ready" if stats["subscribers"] >= 1000 else f"Kurang {subs_needed} subs"
        },
        "growth_recommendations_for_agent1": growth_tips,
        "recommended_songs_pool": trending[:15]
    }
    
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback_data, f, indent=2, ensure_ascii=False)
        
    md_content = f"""# Laporan Pertumbuhan & Rekomendasi Monetisasi YouTube 1
**Waktu Analisa**: {time.strftime('%Y-%m-%d %H:%M:%S')} WIB  
**Channel**: [{stats['title']}](https://youtube.com/channel/{stats['id']})  
**Subscribers**: {stats['subscribers']} | **Total Views**: {stats['views']} | **Total Videos**: {stats['video_count']}

---

## 1. Analisa Menuju Monetisasi Kilat (YPP)
- **Subscribers**: {stats['subscribers']} / 1000 ({'Lolos 1000 subs!' if stats['subscribers'] >= 1000 else f'Kurang {subs_needed}'})
- **Fokus Utama**: Menambah jam tayang (Watch Time 4.000 Jam) melalui retensi karaoke penuh (lagu 3-5 menit diputar berulang).
- **Target Produksi**: 3 Video Karaoke Sehari (Pagi 11:00, Sore 16:30, Malam 20:00).

---

## 2. Instruksi & Masukan Presisi untuk Agent 1 (karaoke_song_researcher)
{chr(10).join(f"- {tip}" for tip in growth_tips)}

---

## 3. Top Tren Lagu Karaoke Terfilter (Siap Dieksekusi Agent 1)
| No | Referensi Judul Lagu Populer | Kategori / Target Audiens |
|---|---|---|
"""
    for i, t in enumerate(trending[:10], 1):
        md_content += f"| {i} | {t['reference_title']} | {t['query_origin']} |\n"
        
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"[✓] Feedback tersimpan di {FEEDBACK_FILE}")
    print(f"[✓] Laporan markdown tersimpan di {REPORT_MD}")

def main():
    if not os.path.exists(TOKEN_PATH):
        print(f"ERROR: {TOKEN_PATH} tidak ditemukan.")
        sys.exit(1)
        
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    yt = build("youtube", "v3", credentials=creds)
    
    stats, recent_videos = analyze_channel(yt)
    trending = research_trending_karaoke(yt)
    build_feedback_and_report(stats, recent_videos, trending)
    
    # Kirim info ringkas ke Telegram
    if os.path.exists(TELEGRAM_SCRIPT):
        tg_msg = (
            f"📊 <b>Analisa YouTube 1 & Rekomendasi Agent 1 Selesai!</b>\n\n"
            f"<b>Channel:</b> {stats['title']}\n"
            f"<b>Subs:</b> {stats['subscribers']} | <b>Videos:</b> {stats['video_count']}\n"
            f"<b>Rekomendasi:</b> 3 slot postingan terjadwal per hari aktif.\n"
            f"<b>Feedback Agent 1:</b> Siap di {FEEDBACK_FILE}"
        )
        os.system(f'/opt/mikrotik-tools/venv/bin/python3 "{TELEGRAM_SCRIPT}" "{tg_msg}" 2>/dev/null || true')

if __name__ == "__main__":
    main()
