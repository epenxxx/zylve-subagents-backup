#!/usr/bin/env python3
"""
performance_auditor.py
Subagen Audit Kinerja Konten ZYLVEmedia.
Menganalisis log penayangan TikTok & YouTube serta merumuskan rekomendasi jam tayang terbaik.
"""

import sys
import os
import json
import datetime

sys.path.append("/root/tools")
from groq_fast_engine import fast_chat

BERITA_LOG = "/root/zylve_automation/berita_log.md"
KARAOKE_LOG = "/root/zylve_automation/karaoke_marketing_log.json"

def audit_recent_performance() -> dict:
    """Audit postingan terbaru dan rekomendasikan strategi tayang berikutnya."""
    # Baca log berita
    recent_news = []
    if os.path.exists(BERITA_LOG):
        try:
            with open(BERITA_LOG, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip().startswith("| 2026")]
                recent_news = lines[-5:]
        except Exception:
            pass

    # Baca log karaoke
    karaoke_data = []
    if os.path.exists(KARAOKE_LOG):
        try:
            with open(KARAOKE_LOG, "r", encoding="utf-8") as f:
                karaoke_data = json.load(f)
        except Exception:
            pass

    system_prompt = (
        "Kamu adalah Direktur Strategi Konten & Analisis Algoritma ZYLVEmedia. "
        "Evaluasi log konten yang baru tayang, lalu berikan kesimpulan performa dan panduan aksi konkret. "
        "Output WAJIB format JSON valid dengan keys:\n"
        "1. 'health_score': int (1-100)\n"
        "2. 'top_performing_niche': string\n"
        "3. 'optimal_next_slot': string (waktu dan slot rekomendasi)\n"
        "4. 'actionable_advice': array 3 rekomendasi strategi konkret."
    )
    prompt = (
        f"Data Berita Terkini:\n{json.dumps(recent_news, indent=2)}\n\n"
        f"Data Pemasaran Karaoke:\n{json.dumps(karaoke_data, indent=2)}\n\n"
        "Buat hasil audit performa:"
    )
    
    raw = fast_chat(prompt, system_prompt=system_prompt, max_tokens=600)
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except Exception:
        pass
    return {"raw_output": raw}

if __name__ == "__main__":
    print("=== [AUDIT PERFORMA & REKOMENDASI KONTEN ZYLVEmedia] ===")
    res = audit_recent_performance()
    print(json.dumps(res, indent=2, ensure_ascii=False))
