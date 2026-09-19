#!/usr/bin/env python3
"""
bilibili_video_analyzer.py - Agent Bilibili: Pre-Upload Video Quality & Safety Analyzer
Memeriksa integritas teknis, standar algoritma Bilibili, kepatuhan VAAPI, dan filter konten sebelum video diunggah.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Daftar kata sensitif / pemicu review lambat di platform Bilibili
SENSITIVE_WORDS = [
    "vpn", "翻墙", "梯子", "博彩", "赌博", "涉黄", "血腥", "暴恐", "反动", "政治",
    "微信私聊", "加微信", "兼职刷单", "代孕", "毒品"
]

# Kata kunci pemicu interaksi danmaku & retensi Bilibili
ENGAGEMENT_TRIGGERS = [
    "前方高能", "三连", "点赞", "投币", "收藏", "弹幕", "下期见", "你觉得", "欢迎讨论"
]

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        return res.stdout.strip(), res.stderr.strip(), res.returncode
    except Exception as e:
        return "", str(e), 1

def analyze_video(file_path, title="", description="", tags=None):
    if not os.path.exists(file_path):
        return {"status": "FAIL", "reason": f"File tidak ditemukan: {file_path}"}

    report = {
        "file": file_path,
        "title": title,
        "verdict": "PASS",
        "scores": {},
        "technical": {},
        "algorithm_check": {},
        "warnings": [],
        "errors": []
    }

    # 1. FFprobe Technical Check
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=codec_name,codec_type,width,height,r_frame_rate",
        "-of", "json", file_path
    ]
    stdout, stderr, rc = run_cmd(probe_cmd)
    if rc != 0:
        report["verdict"] = "FAIL"
        report["errors"].append(f"Gagal membaca ffprobe: {stderr}")
        return report

    try:
        probe_data = json.loads(stdout)
    except Exception as e:
        report["verdict"] = "FAIL"
        report["errors"].append(f"Gagal parse JSON ffprobe: {e}")
        return report

    streams = probe_data.get("streams", [])
    format_info = probe_data.get("format", {})

    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    if not v_stream:
        report["verdict"] = "FAIL"
        report["errors"].append("Tidak ditemukan stream video valid!")
        return report

    width = int(v_stream.get("width", 0))
    height = int(v_stream.get("height", 0))
    v_codec = v_stream.get("codec_name", "")
    duration = float(format_info.get("duration", 0.0))
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    report["technical"] = {
        "resolution": f"{width}x{height}",
        "aspect_ratio": "16:9" if (height > 0 and abs(width/height - 16/9) < 0.05) else ("9:16" if (width > 0 and abs(height/width - 16/9) < 0.05) else "Custom"),
        "video_codec": v_codec,
        "audio_codec": a_stream.get("codec_name", "none") if a_stream else "none",
        "duration_seconds": round(duration, 2),
        "file_size_mb": round(file_size_mb, 2)
    }

    # Cek Rasio & Resolusi Ideal Bilibili
    if report["technical"]["aspect_ratio"] != "16:9":
        report["warnings"].append("Rasio video bukan 16:9 (disarankan untuk video landscape Bilibili utama).")

    if height < 720:
        report["warnings"].append("Resolusi di bawah 720p, berpotensi menurunkan kualitas penayangan.")

    # Cek Codec (Optimal: h264 / hevc via VAAPI)
    if v_codec not in ["h264", "hevc"]:
        report["warnings"].append(f"Codec '{v_codec}' kurang optimal untuk Bilibili. Gunakan h264 atau hevc.")

    # Cek Durasi Algoritma
    if duration < 60:
        report["warnings"].append("Durasi < 1 menit; sulit mendapatkan koin/retensi mid-form Bilibili.")
    elif 180 <= duration <= 480:
        report["algorithm_check"]["duration_zone"] = "OPTIMAL (3-8 menit - Sweet spot retensi & Sanlian)"
    else:
        report["algorithm_check"]["duration_zone"] = "ACCEPTABLE"

    # 2. Audio Loudness & Clipping Check
    loudness_cmd = [
        "ffmpeg", "-i", file_path, "-af", "ebur128=framelog=verbose",
        "-f", "null", "-"
    ]
    _, stderr_loud, _ = run_cmd(loudness_cmd)
    lufs_line = [l for l in stderr_loud.split("\n") if "I:" in l and "LUFS" in l]
    if lufs_line:
        report["technical"]["integrated_loudness"] = lufs_line[-1].strip()

    # 3. Content Safety & Metadata Check
    all_text = f"{title} {description} {' '.join(tags or [])}".lower()
    detected_sensitive = [w for w in SENSITIVE_WORDS if w in all_text]
    if detected_sensitive:
        report["verdict"] = "FAIL"
        report["errors"].append(f"Ditemukan kata berisiko shadowban/penolakan sensor Bilibili: {detected_sensitive}")

    # Engagement triggers
    detected_triggers = [w for w in ENGAGEMENT_TRIGGERS if w in all_text]
    report["algorithm_check"]["engagement_triggers_found"] = detected_triggers
    if not detected_triggers:
        report["warnings"].append("Tidak terdeteksi ajakan interaksi (Danmaku/Sanlian/Diskusi) pada teks.")

    if report["errors"]:
        report["verdict"] = "FAIL"
    elif report["warnings"]:
        report["verdict"] = "PASS_WITH_WARNINGS"
    else:
        report["verdict"] = "PASS"

    return report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan: python3 bilibili_video_analyzer.py <path_video.mp4> [judul] [deskripsi]")
        sys.exit(1)

    video_file = sys.argv[1]
    video_title = sys.argv[2] if len(sys.argv) > 2 else ""
    video_desc = sys.argv[3] if len(sys.argv) > 3 else ""

    result = analyze_video(video_file, video_title, video_desc)
    print(json.dumps(result, indent=2, ensure_ascii=False))
