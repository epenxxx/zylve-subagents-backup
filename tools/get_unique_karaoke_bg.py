#!/usr/bin/env python3
"""
Pengelola Rotasi Background Video Karaoke Unik (Agent 3)
Memastikan setiap lagu karaoke menggunakan video background berbeda
(anti-duplikat, rotasi otomatis, bebas background sama).
"""
import os
import sys
import json
import glob

BG_DIR = "/root/assets/stock_karaoke_koplo/backgrounds"
HISTORY_FILE = "/root/assets/stock_karaoke_koplo/backgrounds_history.json"
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "YOUR_PEXELS_API_KEY")

def download_pexels_nature_bg(query: str = "nature sunset landscape") -> str:
    """Unduh video alam hangat 1080p resmi via Pexels API."""
    import urllib.request
    import random
    os.makedirs(BG_DIR, exist_ok=True)
    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation=landscape&size=medium&per_page=15"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": PEXELS_API_KEY,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            videos = data.get("videos", [])
            if not videos:
                return None
            vid = random.choice(videos)
            vid_id = vid.get("id")
            # Cari video file 1080p atau hd
            files = vid.get("video_files", [])
            target_file = None
            for f in files:
                if f.get("width") == 1920 and f.get("height") == 1080:
                    target_file = f
                    break
            if not target_file and files:
                target_file = files[0]
            
            if target_file and target_file.get("link"):
                out_name = f"nature_warm_pexels_{vid_id}.mp4"
                out_path = os.path.join(BG_DIR, out_name)
                if not os.path.exists(out_path):
                    print(f"[*] Mengunduh background Pexels 1080p: {out_name}...")
                    dl_req = urllib.request.Request(target_file["link"], headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(dl_req, timeout=40) as dl_resp, open(out_path, "wb") as out_f:
                        out_f.write(dl_resp.read())
                    print(f"[✓] Berhasil unduh: {out_name}")
                return out_path
    except Exception as e:
        print(f"[!] Error unduh Pexels API: {e}")
    return None

def get_next_unique_background(song_title=""):
    os.makedirs(BG_DIR, exist_ok=True)
    raw_bgs = sorted(glob.glob(os.path.join(BG_DIR, "*.mp4")))
    
    # ATURAN MUTLAK: Footage pemandangan alam asli bernuansa warna hangat (DILARANG neon & panggung sintetis)
    nature_keywords = ["nature", "waterfall", "mountain", "forest", "flowers", "landscape", "beach", "lake"]
    warm_keywords = ["warm", "sunset", "golden", "sunrise", "senja"]
    
    # Prioritaskan pemandangan alam bernuansa hangat
    warm_nature_bgs = [
        b for b in raw_bgs 
        if any(w in os.path.basename(b).lower() for w in warm_keywords)
        and not any(bad in os.path.basename(b).lower() for bad in ["neon", "stage", "panggung"])
    ]
    
    # Cadangan: pemandangan alam umum jika warm belum cukup
    all_nature_bgs = [
        b for b in raw_bgs 
        if any(k in os.path.basename(b).lower() for k in nature_keywords)
        and not any(bad in os.path.basename(b).lower() for bad in ["neon", "stage", "panggung"])
    ]
    
    candidates = warm_nature_bgs if warm_nature_bgs else all_nature_bgs
    if not candidates:
        candidates = raw_bgs

    if not candidates:
        print(f"[*] Stok background habis, mengunduh otomatis via Pexels API...")
        new_bg = download_pexels_nature_bg()
        if new_bg:
            candidates = [new_bg]
        else:
            print(f"[!] Tidak ada file background di {BG_DIR}")
            return None

    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    last_used = history[-1].get("bg_file") if history else None

    # Pilih yang bukan last_used untuk mencegah duplikat berurutan
    available = [b for b in candidates if b != last_used]
    if not available:
        available = candidates

    # Hitung frekuensi penggunaan
    usage_count = {b: 0 for b in candidates}
    for item in history:
        b = item.get("bg_file")
        if b in usage_count:
            usage_count[b] += 1

    # Urutkan berdasarkan frekuensi terkecil, lalu acak (random) di antara frekuensi terendah
    import random
    min_freq = min(usage_count.get(b, 0) for b in available)
    least_used_bgs = [b for b in available if usage_count.get(b, 0) == min_freq]
    selected_bg = random.choice(least_used_bgs)

    # Catat ke history
    history.append({
        "song_title": song_title,
        "bg_file": selected_bg,
        "bg_name": os.path.basename(selected_bg)
    })
    # Simpan maks 50 entri riwayat
    history = history[-50:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print(f"[✓] Background Video Unik Terpilih: {os.path.basename(selected_bg)}")
    return selected_bg

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "Unknown Song"
    bg = get_next_unique_background(title)
    if bg:
        print(bg)
