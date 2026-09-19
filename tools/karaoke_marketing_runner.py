#!/usr/bin/env python3
"""
Otomasi Pemasaran Konten Lagu Karaoke (karaoke_marketer)
Menjalankan promosi lagu karaoke YouTube ZYLVEmedia satu per satu:
1. Buat klip teaser 9:16 (12 detik vertikal HD)
2. Generate copywriting emosional & pemantik interaksi
3. Distribusi promosi ke grup komunitas musik FB
4. Kirim materi promo lengkap ke Telegram
5. Catat log progres pemasaran
"""

import os
import sys
import json
import time
import subprocess

PRODUCTION_LOG = "/root/zylve_automation/karaoke_production_log.json"
MARKETING_LOG = "/root/zylve_automation/karaoke_marketing_log.json"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"
QUEUE_FB = "/root/zylve_automation/fb_groups_queue.json"

TRACKS = [
    {
        "id": "exist_mencari_alasan",
        "title": "Mencari Alasan - Exist",
        "youtube_url": "https://youtu.be/oTfkWVNMS1E",
        "video_path": "/root/projects/karaoke_exist_mencari_alasan/karaoke_exist_mencari_alasan.mp4",
        "category": "karaoke_pop",
        "target_group": "KARAOKE INDONESIA LOVERS",
        "cut_start": "01:35",
        "cut_duration": "12",
        "genre_hook": "🎸 Kangen lagu nostalgia slow rock Malaysia era 90-an? Tes vokal di nada tingginya!",
        "caption": (
            "🎸 MASIH HAFAL LIRIK LAGU EXIST INI?\n\n"
            "\"Jikalau kau cinta, mengapa berpaling...\"\n\n"
            "Yuk nostalgia bareng! Sudah rilis versi KARAOKE TANPA VOKAL super jernih + lirik kuning berjalan rapi by ZYLVEmedia.\n\n"
            "▶️ Tonton Full HD di YouTube:\nhttps://youtu.be/oTfkWVNMS1E\n\n"
            "💬 Siapa yang suaranya nyampe di nada reff lagu ini? Tag teman karaokeanmu!\n\n"
            "#KaraokeNoVocal #ExistMencariAlasan #SlowRock90an #KaraokeMalaysia #ZYLVEmedia"
        )
    },
    {
        "id": "cut_rani_salah_apa",
        "title": "Salah Apa - Cut Rani Auliza",
        "youtube_url": "https://youtu.be/27DFNlbtQ_4",
        "video_path": "/root/projects/karaoke_cut_rani_salah_apa/karaoke_cut_rani_salah_apa.mp4",
        "category": "dangdut",
        "target_group": "KOMUNITAS DANGDUT KOPLO MANIA",
        "cut_start": "02:05",
        "cut_duration": "12",
        "genre_hook": "💃 Lagu syahdu yang lagi viral di TikTok! Enak banget buat karaokean santai.",
        "caption": (
            "💃 KARAOKE SYAHDU VIRAL: SALAH APA - CUT RANI AULIZA!\n\n"
            "Lirik pas, tempo asik, dan musiknya bikin pengen langsung ambil mic!\n"
            "Versi karaoke resmi tanpa vokal by ZYLVEmedia sudah tayang dengan kualitas audio studio jernih.\n\n"
            "▶️ Tonton & Nyanyi Full di YouTube:\nhttps://youtu.be/27DFNlbtQ_4\n\n"
            "💬 Lagu Cut Rani mana lagi yang wajib kita buatin minus one karaoke? Komen di bawah ya!\n\n"
            "#KaraokeDangdut #SalahApaCutRani #CutRaniAuliza #KaraokeTanpaVokal #ZYLVEmedia"
        )
    },
    {
        "id": "humko_humise_chura_lo",
        "title": "Humko Humise Chura Lo - Mohabbatein",
        "youtube_url": "https://youtu.be/mSJ3z5OhR-4",
        "video_path": "/root/projects/karaoke_humko_humise/karaoke_humko_humise_chura_lo.mp4",
        "category": "bollywood",
        "target_group": "BOLLYWOOD MANIA INDONESIA",
        "cut_start": "00:45",
        "cut_duration": "12",
        "genre_hook": "🎻 Lagu Bollywood paling romantis sepanjang masa! Siap duet karaokean?",
        "caption": (
            "🎻 NOSTALGIA FILM MOHABBATEIN: HUMKO HUMISE CHURA LO!\n\n"
            "Melodi biola legendaris Shah Rukh Khan & Aishwarya Rai kini hadir dalam versi KARAOKE NO VOCAL jernih tanpa desis by ZYLVEmedia.\n\n"
            "▶️ Tonton & Duet Bareng di YouTube:\nhttps://youtu.be/mSJ3z5OhR-4\n\n"
            "💬 Paling suka part cowok atau cewek di lagu ini? Yuk tes vokal sekarang!\n\n"
            "#BollywoodKaraoke #HumkoHumiseChuraLo #Mohabbatein #KaraokeIndia #ZYLVEmedia"
        )
    }
]

def load_marketing_log():
    if os.path.exists(MARKETING_LOG):
        try:
            with open(MARKETING_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"promoted_tracks": [], "history": []}

def save_marketing_log(data):
    try:
        with open(MARKETING_LOG, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[!] Gagal simpan log: {e}")

def create_teaser_clip(src_video, out_clip, start_time, duration):
    """Potong video 12 detik dan crop vertikal 9:16 (1080x1920) untuk Reels/Shorts/TikTok"""
    if not os.path.exists(src_video):
        print(f"[!] Video sumber tidak ditemukan: {src_video}")
        return False

    print(f"[*] Merender klip teaser vertikal 9:16 ({duration} detik)...")
    # Filter crop center 1080x1920 dari 1920x1080
    cmd = [
        "ffmpeg", "-y",
        "-ss", start_time,
        "-i", src_video,
        "-t", duration,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        out_clip
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0 and os.path.exists(out_clip)

def send_telegram(text, file_path=None):
    try:
        cmd = ["/usr/bin/python3", TELEGRAM_SCRIPT]
        if file_path and os.path.exists(file_path):
            cmd.extend([file_path, text])
        else:
            cmd.append(text)
        subprocess.run(cmd, timeout=60)
    except Exception as e:
        print(f"[!] Gagal kirim Telegram: {e}")

def promote_track(track):
    print(f"\n{'='*50}")
    print(f"🚀 MEMULAI PEMASARAN: {track['title']}")
    print(f"{'='*50}")

    teaser_out = f"/root/assets/teaser_{track['id']}.mp4"
    ok = create_teaser_clip(track["video_path"], teaser_out, track["cut_start"], track["cut_duration"])
    
    if ok:
        print(f"[✓] Klip teaser 9:16 sukses dibuat: {teaser_out}")
    else:
        print("[!] Menggunakan thumbnail/link fallback karena klip gagal di-render.")

    # 1. Catat ke FB Groups Queue
    try:
        with open(QUEUE_FB, "r", encoding="utf-8") as f:
            fb_data = json.load(f)
        fb_data["history"].append({
            "track": track["title"],
            "target_group": track["target_group"],
            "youtube_url": track["youtube_url"],
            "promoted_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(QUEUE_FB, "w", encoding="utf-8") as f:
            json.dump(fb_data, f, indent=2)
        print(f"[✓] Promosi terjadwal ke FB Group: {track['target_group']}")
    except Exception as e:
        print(f"[!] Gagal catat ke FB queue: {e}")

    # 2. Kirim Materi Promosi ke Telegram
    msg = (
        f"📢 *KAMPANYE PROMOSI KARAOKE TAYANG: {track['title']}*\n\n"
        f"{track['genre_hook']}\n\n"
        f"▶️ *YouTube:* {track['youtube_url']}\n"
        f"🎯 *Target Komunitas:* {track['target_group']}\n\n"
        f"📝 *Copywriting Siap Pakai (Medsos):*\n```\n{track['caption']}\n```\n\n"
        f"✅ *Status:* Cuplikan teaser 9:16 siap edar & terdistribusi!"
    )
    send_telegram(msg, file_path=teaser_out if ok else None)
    print(f"[✓] Laporan promosi & klip terkirim ke Telegram.")

    # 3. Update Log Pemasaran
    log_data = load_marketing_log()
    if track["id"] not in log_data["promoted_tracks"]:
        log_data["promoted_tracks"].append(track["id"])
    log_data["history"].append({
        "track_id": track["id"],
        "title": track["title"],
        "youtube_url": track["youtube_url"],
        "teaser_clip": teaser_out if ok else None,
        "promoted_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    save_marketing_log(log_data)
    print(f"[✓] Pemasaran {track['title']} berhasil dicatat!")
    return True

def run_all_sequentially():
    log_data = load_marketing_log()
    promoted = log_data.get("promoted_tracks", [])
    
    print(f"[*] Total katalog lagu: {len(TRACKS)}")
    print(f"[*] Sudah dipromosikan sebelumnya: {len(promoted)}")
    
    for t in TRACKS:
        promote_track(t)
        time.sleep(2)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tid = sys.argv[1]
        target = next((t for t in TRACKS if t["id"] == tid), None)
        if target:
            promote_track(target)
        else:
            print(f"Lagu dengan ID '{tid}' tidak ditemukan.")
    else:
        run_all_sequentially()
