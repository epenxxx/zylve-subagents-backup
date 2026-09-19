#!/usr/bin/env python3
"""
shorts_growth_analyst.py
Agent Analis & Optimasi Performa YouTube Shorts ZYLVEmedia02 Menuju 10 Juta Views.

Fokus Analisis:
1. Audit Metrik Live Channel (Views, Pertumbuhan, Rasio Hook)
2. Formula Viral 10M Views (VVSA > 75%, APV > 100%, Loop Seamless, Subtitle Synced)
3. Rekomendasi Modifikasi Naskah, Hook, dan Visual untuk Upload Selanjutnya
4. Integrasi LPU Groq untuk sintesis strategi data riil
"""

import os
import sys
import json
import subprocess
import datetime

sys.path.append("/root/tools")
from groq_fast_engine import fast_chat

CHANNEL_HANDLE = "@zylvemedia02"
ANALYSIS_OUTPUT = "/root/logs/shorts_growth_analysis.json"
TOPIC_QUEUE = "/root/assets/shorts_topic_queue.json"

def fetch_channel_shorts() -> list:
    """Ambil data statistik video Shorts publik terbaru dari channel."""
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        f"https://www.youtube.com/{CHANNEL_HANDLE}/shorts"
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        if proc.returncode == 0:
            data = json.loads(proc.stdout)
            entries = data.get("entries", [])
            shorts_list = []
            for e in entries:
                shorts_list.append({
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "views": e.get("view_count") or 0,
                    "url": f"https://youtube.com/shorts/{e.get('id')}"
                })
            return shorts_list
    except Exception as ex:
        print(f"[!] Warning fetch shorts: {ex}")
    return []

def run_growth_analysis() -> dict:
    """Jalankan audit holistik dan kalkulasi perbaikan menuju 10 juta views."""
    print(f"[*] Mengambil data live Shorts dari {CHANNEL_HANDLE}...")
    shorts = fetch_channel_shorts()
    total_views = sum(s.get("views", 0) for s in shorts)
    
    # Ambil antrean topik
    queue_count = 0
    if os.path.exists(TOPIC_QUEUE):
        try:
            with open(TOPIC_QUEUE, "r") as f:
                queue_count = len(json.load(f))
        except Exception:
            pass

    system_prompt = (
        "Kamu adalah Shorts Growth Architect kelas dunia spesialis algoritma YouTube 2026. "
        "Misi tunggal: Mengakselerasi channel menuju 10.000.000 views dalam waktu sesingkat mungkin untuk tembus YPP. "
        "Evaluasi data metrik live, terapkan Formula 10M Views:\n"
        "1. Hook 3 Detik Pertama (VVSA > 75%)\n"
        "2. Pacing Loop Sempurna (APV > 100%)\n"
        "3. High-RPM US Tier-1 Search Psychology\n"
        "4. Visual Dinamis 60fps & Subtitle ASS Eye-Tracking\n"
        "Output WAJIB JSON murni tanpa markdown dengan format:\n"
        "{\n"
        '  "current_total_views": int,\n'
        '  "views_gap_to_10m": int,\n'
        '  "channel_health_status": "Aggressive Growth" | "Healthy" | "Needs Acceleration",\n'
        '  "hook_retention_score": int,\n'
        '  "top_performing_shorts": string,\n'
        '  "critical_bottlenecks": [string, string],\n'
        '  "viral_action_plan": [string, string, string],\n'
        '  "recommended_next_topic_focus": string\n'
        "}"
    )

    prompt = (
        f"Data Live Shorts Saat Ini ({len(shorts)} Video Terbit):\n"
        f"{json.dumps(shorts, indent=2)}\n\n"
        f"Total Views Terkumpul: {total_views}\n"
        f"Topik Siap di Queue: {queue_count} topik\n"
        "Lakukan audit matematis dan susun rencana perbaikan video:"
    )

    raw = fast_chat(prompt, system_prompt=system_prompt, max_tokens=700)
    result = {}
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(raw[start:end])
    except Exception:
        result = {"raw_analysis": raw}

    result["timestamp"] = datetime.datetime.now().isoformat()
    result["channel"] = CHANNEL_HANDLE
    result["total_shorts_published"] = len(shorts)
    result["total_live_views"] = total_views
    result["videos"] = shorts

    os.makedirs(os.path.dirname(ANALYSIS_OUTPUT), exist_ok=True)
    with open(ANALYSIS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[✓] Hasil audit tersimpan di: {ANALYSIS_OUTPUT}")
    return result

if __name__ == "__main__":
    print("=== [AGENT SHORTS GROWTH ANALYST - ROAD TO 10M VIEWS] ===")
    res = run_growth_analysis()
    print(json.dumps(res, indent=2, ensure_ascii=False))
