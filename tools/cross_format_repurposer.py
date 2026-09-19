#!/usr/bin/env python3
"""
cross_format_repurposer.py
Subagen Pembuat Paket Multi-Format ZYLVEmedia.
Mengonversi 1 konten menjadi 5 format omnichannel dalam hitungan detik via Groq / Gemini API.
"""

import sys
import os
import json

sys.path.append("/root/tools")
from groq_fast_engine import fast_chat

def repurpose_content(title: str, summary: str, source: str = "ZYLVEmedia") -> dict:
    """Mengubah 1 materi berita/konten menjadi 5 format media lengkap."""
    system_prompt = (
        "Kamu adalah Maestro Konten Omnichannel ZYLVEmedia. "
        "Ubah bahan berita menjadi 5 format publikasi berbeda. "
        "Output WAJIB format JSON valid dengan keys:\n"
        "1. 'reels_script': Script video 8-12 detik (durasi minimal 8 detik), format narasi vokal padat.\n"
        "2. 'twitter_thread': Array 3 cuitan runtut menarik.\n"
        "3. 'telegram_broadcast': Teks broadcast Telegram elegan dengan emoji rapi.\n"
        "4. 'ig_caption': Caption storytelling Instagram lengkap hashtag.\n"
        "5. 'seo_meta_desc': Ringkasan SEO Google maksimal 155 karakter."
    )
    prompt = (
        f"Judul: {title}\n"
        f"Ringkasan/Fakta: {summary}\n"
        f"Sumber: {source}\n\n"
        "Hasilkan format JSON:"
    )
    raw = fast_chat(prompt, system_prompt=system_prompt, max_tokens=800)
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except Exception:
        pass
    return {"raw_output": raw}

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "Bukan Bunuh Diri, Wanita di Serang Tewas Dibunuh Pacar"
    s = sys.argv[2] if len(sys.argv) > 2 else "Polisi mengungkap motif pembunuhan berencana karena cemburu buta setelah olah TKP."
    
    print(f"[*] Repurposing: {t}")
    res = repurpose_content(t, s)
    print(json.dumps(res, indent=2, ensure_ascii=False))
