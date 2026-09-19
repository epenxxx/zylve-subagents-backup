#!/usr/bin/env python3
"""
comment_engager.py
Subagen Pembalas Komentar Netizen Otomatis ZYLVEmedia.
Menghasilkan balasan humanis, ramah, dan solutif berbasis Groq LPU (<0.3 detik).
"""

import sys
import os
import json

# Gunakan fungsi fast_chat dari groq_fast_engine
sys.path.append("/root/tools")
from groq_fast_engine import fast_chat

def generate_reply(user_comment: str, content_context: str = "Berita Faktual ZYLVEmedia") -> str:
    """Buat balasan komentar netizen yang ramah, santun, dan menaikkan engagement."""
    system_prompt = (
        "Kamu adalah Admin Komunitas ZYLVEmedia yang ramah, sopan, luwes, dan cerdas. "
        "Tugasmu membalas komentar netizen di media sosial (TikTok / YouTube). "
        "Aturan:\n"
        "1. Bahasa Indonesia santun, natural, seperti manusia asli (anti-robot).\n"
        "2. Jangan gunakan kata klise bot ('Terima kasih atas komentar Anda').\n"
        "3. Tanggapi poin yang mereka sebutkan dengan empati atau pertanyaan diskusi ringan.\n"
        "4. Panjang maksimal 2 kalimat pendek (15-25 kata)."
    )
    prompt = (
        f"Konteks Konten: {content_context}\n"
        f"Komentar Netizen: \"{user_comment}\"\n"
        "Buat 1 balasan terbaik:"
    )
    return fast_chat(prompt, system_prompt=system_prompt, max_tokens=100)

if __name__ == "__main__":
    test_comment = sys.argv[1] if len(sys.argv) > 1 else "Parah banget ya, masa gara-gara cemburu sampai tega bunuh pacar sendiri!"
    context = sys.argv[2] if len(sys.argv) > 2 else "Kasus Pembunuhan Wanita di Serang"
    
    print(f"[*] Komentar Netizen: {test_comment}")
    print(f"[*] Konteks: {context}")
    reply = generate_reply(test_comment, context)
    print(f"\n[✓] Balasan Admin ZYLVEmedia:\n\"{reply}\"")
