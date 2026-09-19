#!/usr/bin/env python3
"""
multiclip_shorts_builder.py
Engine Pembuat Video Latar Multi-Clip Dinamis untuk YouTube Shorts ZYLVEmedia.
Mengunduh 3-6 klip video berbeda (Pexels + Pixabay) sesuai topik,
memotong per 3-6 detik, dan menggabungkannya secara dinamis (anti-bosan, retensi tinggi).
"""

import os
import sys
import json
import time
import random
import urllib.request
import urllib.parse
import subprocess

PEXELS_KEY = os.getenv("PEXELS_API_KEY", "YOUR_PEXELS_API_KEY")

def get_pixabay_key():
    key_file = "/root/.config/pixabay/api_key"
    if os.path.exists(key_file):
        with open(key_file) as f:
            return f.read().strip()
    return os.getenv("PIXABAY_API_KEY", "56578468-4f1f52a61a851d4a67fc3c8eb")

def fetch_pexels_videos(query, count=3):
    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation=portrait&per_page=15"
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY, "User-Agent": "Mozilla/5.0"})
    links = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for v in data.get("videos", []):
                for f in v.get("video_files", []):
                    if f.get("width") == 1080 and f.get("height") == 1920:
                        links.append(f.get("link"))
                        break
                if len(links) >= count:
                    break
            if len(links) < count:
                for v in data.get("videos", []):
                    files = v.get("video_files", [])
                    if files and files[0].get("link") not in links:
                        links.append(files[0].get("link"))
                    if len(links) >= count:
                        break
    except Exception as e:
        print(f"[!] Warning Pexels fetch: {e}")
    return links

def fetch_pixabay_videos(query, count=3):
    key = get_pixabay_key()
    url = f"https://pixabay.com/api/videos/?key={key}&q={urllib.parse.quote(query)}&video_type=film&per_page=15&safesearch=true"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    links = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for hit in data.get("hits", []):
                videos = hit.get("videos", {})
                for res in ["large", "medium", "small"]:
                    if res in videos and videos[res].get("url"):
                        links.append(videos[res]["url"])
                        break
                if len(links) >= count:
                    break
    except Exception as e:
        print(f"[!] Warning Pixabay fetch: {e}")
    return links

def build_multiclip_background(queries, total_duration, workdir, clip_duration=4.5):
    """
    Membuat video latar gabungan dari beberapa klip video berbeda.
    Setiap klip dipotong ~clip_duration detik dan di-scale/crop ke 1080x1920 30fps.
    """
    os.makedirs(workdir, exist_ok=True)
    needed_clips = max(3, int(total_duration / clip_duration) + 1)
    print(f"[*] Menyiapkan {needed_clips} scene klip video multi-cut (durasi total: {total_duration:.1f}s)...")

    # Kumpulkan variasi link dari Pexels & Pixabay
    all_links = []
    for q in queries:
        all_links.extend(fetch_pexels_videos(q, count=2))
        all_links.extend(fetch_pixabay_videos(q, count=2))
        if len(all_links) >= needed_clips * 2:
            break

    # Hilangkan duplikat
    unique_links = list(dict.fromkeys(all_links))
    random.shuffle(unique_links)

    if not unique_links:
        raise RuntimeError("Gagal mengunduh klip video dari Pexels maupun Pixabay.")

    downloaded_clips = []
    for i, link in enumerate(unique_links[:needed_clips]):
        raw_path = os.path.join(workdir, f"raw_clip_{i}.mp4")
        norm_path = os.path.join(workdir, f"norm_clip_{i}.mp4")
        try:
            print(f"[*] Mengunduh Scene #{i+1}...")
            dl_req = urllib.request.Request(link, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(dl_req, timeout=30) as resp, open(raw_path, "wb") as f:
                f.write(resp.read())

            # Normalisasi video: scale/crop ke 1080x1920, 30fps, hilangkan audio, potong clip_duration
            cmd = [
                "ffmpeg", "-y", "-ss", "1",
                "-i", raw_path,
                "-t", str(clip_duration),
                "-filter_complex",
                "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1",
                "-c:v", "libx264", "-preset", "ultrafast", "-an",
                norm_path
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            if os.path.exists(norm_path) and os.path.getsize(norm_path) > 1000:
                downloaded_clips.append(norm_path)
        except Exception as e:
            print(f"[!] Gagal proses clip #{i+1}: {e}")

    if not downloaded_clips:
        raise RuntimeError("Tidak ada klip video yang berhasil dinormalisasi.")

    print(f"[✓] {len(downloaded_clips)} scene klip video berhasil diproses.")

    # Gabungkan semua klip menggunakan FFmpeg concat demuxer
    concat_list = os.path.join(workdir, "concat_list.txt")
    with open(concat_list, "w") as f:
        # Loop klip sampai memenuhi total_duration
        current_len = 0
        idx = 0
        while current_len < total_duration:
            clip = downloaded_clips[idx % len(downloaded_clips)]
            f.write(f"file '{clip}'\n")
            current_len += clip_duration
            idx += 1

    merged_bg = os.path.join(workdir, "multiclip_background.mp4")
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-t", str(total_duration),
        "-c", "copy",
        merged_bg
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)
    print(f"[✓] Background Multi-Clip Berhasil Digabungkan: {merged_bg} ({os.path.getsize(merged_bg)} bytes)")
    return merged_bg

if __name__ == "__main__":
    queries = sys.argv[1].split(",") if len(sys.argv) > 1 else ["deep ocean", "space nebula", "volcano erupting"]
    out = build_multiclip_background(queries, 15.0, "/tmp/test_multiclip", clip_duration=4.0)
    print("Selesai:", out)
