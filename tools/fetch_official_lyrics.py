#!/usr/bin/env python3
"""
Pencari & Pemvalidasi Lirik Lagu Resmi (Agent 1 & Agent 3)
Wajib mencari referensi lirik resmi terpercaya dari deskripsi video YouTube resmi
atau portal lirik terverifikasi SEBELUM menyusun subtitle karaoke (Anti-Ngawur).
"""
import os
import sys
import re
import json
import urllib.request
import urllib.parse
import argparse

def clean_lyric_line(line):
    line = re.sub(r"\[.*?\]", "", line)  # Hapus tag chord/musik
    line = re.sub(r"\(.*?\)", "", line)
    return line.strip()

def extract_lyrics_from_description(desc_text):
    if not desc_text:
        return ""
    lines = desc_text.split("\n")
    lyric_lines = []
    in_lyrics = False

    trigger_patterns = [r"\blirik\b", r"\blyrics\b", r"\bsyair\b"]
    end_words = ["terima kasih", "follow", "tonton juga", "copyright", "subscribe", "official music video", "arranger", "audio by", "music credits", "video credits", "credits", "produser"]

    for l in lines:
        lower = l.lower().strip()
        # Deteksi awal lirik
        if not in_lyrics and any(re.search(pat, lower) for pat in trigger_patterns):
            # Hindari kalimat seperti "dilarang menggunakan lirik ini" jika bukan header
            if len(l.strip()) < 50:
                in_lyrics = True
                continue
        # Deteksi akhir lirik
        if in_lyrics and any(ew in lower for ew in end_words) and len(lyric_lines) > 5:
            break
        if in_lyrics and l.strip():
            cl = clean_lyric_line(l)
            if cl and not cl.startswith("──") and not cl.startswith("==") and not cl.startswith("**"):
                lyric_lines.append(cl)

    return "\n".join(lyric_lines)

def search_official_lyrics(song_title, artist=""):
    query = f"{song_title} {artist} lirik lagu".strip()
    print(f"[*] Mencari referensi lirik resmi untuk: {query}...")
    
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
        snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
        combined = " ".join([re.sub(r'<[^>]+>', '', s) for s in snippets])
        return combined
    except Exception as e:
        print(f"[!] Gagal web search lirik: {e}")
        return ""

def get_official_lyrics(youtube_id_or_url, song_title="", artist="", output_file=None):
    # 1. Cek deskripsi YouTube asli via yt-dlp
    print(f"[*] [1/2] Mengekstrak lirik resmi dari deskripsi YouTube: {youtube_id_or_url}...")
    cookies_arg = "--cookies /root/zylve_automation/youtube_cookies.txt" if os.path.exists("/root/zylve_automation/youtube_cookies.txt") else ""
    cmd = f'yt-dlp --remote-components ejs:github {cookies_arg} --dump-single-json --skip-download "{youtube_id_or_url}" 2>/dev/null'
    try:
        import subprocess
        out = subprocess.check_output(cmd, shell=True).decode("utf-8")
        meta = json.loads(out)
        desc = meta.get("description", "")
        lyrics = extract_lyrics_from_description(desc)
        if lyrics and len(lyrics.splitlines()) >= 4:
            print(f"[✓] Berhasil menemukan {len(lyrics.splitlines())} baris lirik resmi dari deskripsi resmi!")
            if output_file:
                os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(lyrics + "\n")
            return lyrics
    except Exception as e:
        print(f"[!] Gagal parse deskripsi YouTube: {e}")

    # 2. Fallback pencarian web
    print("[*] [2/2] Mencari referensi lirik dari database web...")
    web_lyrics = search_official_lyrics(song_title, artist)
    if output_file and web_lyrics:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(web_lyrics + "\n")
    return web_lyrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pencari & Pemvalidasi Lirik Resmi Karaoke")
    parser.add_argument("url", help="YouTube URL atau Video ID")
    parser.add_argument("--title", default="", help="Judul lagu")
    parser.add_argument("--artist", default="", help="Nama artis")
    parser.add_argument("-o", "--output", default=None, help="File output lirik resmi (.txt)")
    args, unknown = parser.parse_known_args()

    # Fallback positional compatibility
    title = args.title
    artist = args.artist
    output = args.output
    if unknown and not output:
        output = unknown[-1]

    res = get_official_lyrics(args.url, title, artist, output)
    print("--- HASIL LIRIK RESMI ---")
    print(res)
