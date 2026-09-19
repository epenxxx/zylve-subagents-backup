#!/usr/bin/env python3
"""
Engine Otomasi Generator Metadata YouTube SEO Terstruktur
Mengikuti algoritma YouTube 2026:
- Exact Match Keyword di 50 karakter awal Title
- Keyword Density alami di 3 kalimat pertama Deskripsi
- Timestamps / Chapter marks jika ada
- Kategori Musik (10) + Tag Organik (High + Medium + Long-tail)
- Bebas AI Slop
"""

import os
import sys
import json
import re

def generate_seo_package(title_song, artist, genre="pop", lirik_text="", output_path=None):
    # 1. Judul Algoritmik (CTR & Search Optimized, <85 chars)
    primary_title = f"{title_song} - {artist} | Karaoke Tanpa Vokal (Lirik) by ZYLVEmedia"
    if len(primary_title) > 95:
        primary_title = f"{title_song} - {artist} | Karaoke by ZYLVEmedia"

    # 2. Tag Terstruktur (Exact, Broad, Long-tail)
    clean_title = re.sub(r'[^\w\s]', '', title_song).lower()
    clean_artist = re.sub(r'[^\w\s]', '', artist).lower()
    
    tags = [
        f"{clean_title} karaoke",
        f"karaoke {clean_title}",
        f"{clean_title} lirik",
        f"{clean_title} tanpa vokal",
        f"{clean_title} {clean_artist}",
        f"{clean_artist} karaoke",
        f"karaoke {clean_artist}",
        f"{clean_title} karaoke nada asli",
        f"{clean_title} by zylvemedia",
        "karaoke no vocal",
        "karaoke lirik berjalan",
        "karaoke terbaru 2026",
        "karaoke hd 1080p",
        "zylvemedia karaoke"
    ]
    if genre:
        tags.extend([f"karaoke {genre}", f"lagu {genre} terpopuler"])

    # 3. Deskripsi Algoritmik & Humanis (Bebas AI Slop)
    description = f"""Karaoke {title_song} - {artist} versi audio jernih tanpa vokal dengan lirik berjalan rapi by ZYLVEmedia. Cocok untuk latihan vokal, santai, maupun cover lagu.

🎤 Detail Lagu:
• Judul: {title_song}
• Artis: {artist}
• Musik: Karaoke by ZYLVEmedia (No Vocal / Nada Asli)
• Resolusi: Full HD 1080p 60fps / 30fps

📝 Lirik {title_song}:
{lirik_text.strip() if lirik_text else '[Lirik lagu resmi tercantum di video]'}

📌 Jangan lupa Like, Komentar request lagu berikutnya, dan Subscribe ZYLVEmedia untuk update karaoke terbaru setiap hari!

#karaoke #{clean_title.replace(' ', '')} #{clean_artist.replace(' ', '')} #karaoketanpavokal #zylvemedia
"""

    seo_data = {
        "title": primary_title,
        "description": description.strip(),
        "tags": tags[:20],
        "categoryId": "10",
        "defaultLanguage": "id",
        "privacyStatus": "public"
    }

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(seo_data, f, indent=2, ensure_ascii=False)
        print(f"[✓] Metadata SEO YouTube tersimpan di: {output_path}")

    return seo_data

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "Mencari Alasan"
    a = sys.argv[2] if len(sys.argv) > 2 else "Exist"
    out = sys.argv[3] if len(sys.argv) > 3 else "/root/zylve_automation/seo_test.json"
    res = generate_seo_package(t, a, output_path=out)
    print(json.dumps(res, indent=2, ensure_ascii=False))
