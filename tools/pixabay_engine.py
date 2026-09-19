#!/usr/bin/env python3
"""
Pixabay Engine ZYLVEmedia
Pencarian & Unduh Stok Video Alam 1080p & Musik Royalty-Free Otomatis.
"""

import os
import sys
import json
import urllib.request
import urllib.parse

KEY_FILE = "/root/.config/pixabay/api_key"

def get_api_key():
    key = os.getenv("PIXABAY_API_KEY")
    if key and key.strip():
        return key.strip()
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    return None

def download_video(query="nature landscape sunset", output_path="/root/assets/pixabay_bg.mp4", orientation="horizontal", min_duration=10):
    key = get_api_key()
    if not key:
        raise ValueError("API Key Pixabay tidak ditemukan.")

    params = {
        "key": key,
        "q": query,
        "video_type": "film",
        "orientation": orientation,
        "per_page": 10,
        "safesearch": "true"
    }
    url = f"https://pixabay.com/api/videos/?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    hits = data.get("hits", [])
    if not hits:
        raise RuntimeError(f"Tidak ada video Pixabay ditemukan untuk kueri '{query}'.")

    # Pilih video dengan durasi memadai dan resolusi terbaik (large / medium)
    chosen_url = None
    for item in hits:
        if item.get("duration", 0) >= min_duration:
            videos = item.get("videos", {})
            # Cek large -> medium -> small
            for res in ["large", "medium", "small"]:
                if res in videos and videos[res].get("url"):
                    chosen_url = videos[res]["url"]
                    break
            if chosen_url:
                break

    if not chosen_url and hits:
        # Fallback ke video pertama
        videos = hits[0].get("videos", {})
        chosen_url = videos.get("medium", {}).get("url") or videos.get("small", {}).get("url")

    if not chosen_url:
        raise RuntimeError("Gagal mendapatkan link download video dari respons Pixabay.")

    print(f"[*] Mengunduh video dari Pixabay: {chosen_url}...")
    req_dl = urllib.request.Request(chosen_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req_dl, timeout=60) as resp_dl:
        with open(output_path, "wb") as f:
            f.write(resp_dl.read())

    print(f"[✓] Sukses mengunduh video Pixabay ke: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "calm river forest"
    out = sys.argv[2] if len(sys.argv) > 2 else "/root/assets/test_pixabay.mp4"
    res = download_video(q, out)
    print("Hasil:", res)
