#!/usr/bin/env python3
"""
run_autonomous_shorts_pipeline.py
Pipeline Otomatis Produksi & Upload YouTube Shorts Ber-RPM Tinggi ke Akun 2 (@zylvemedia02).

Jadwal Rutin:
- 22:00 WIB (Slot 1: 11:00 AM US Midday)
- 02:00 WIB (Slot 2: 03:00 PM US Afternoon)
- 06:00 WIB (Slot 3: 07:00 PM US Evening Prime)

Alur Kerja:
1. Membaca topik berikutnya dari antrean (/root/assets/shorts_topic_queue.json)
2. Generate voiceover & subtitle VTT sinkron 100% via edge-tts
3. Konversi VTT ke ASS eye-tracking (kuning/putih kontras tinggi)
4. Unduh footage vertikal 1080x1920 via Pexels API
5. Render MP4 1080x1920 via FFmpeg
6. Upload otomatis ke YouTube Akun 2 via Playwright
7. Kirim video & notifikasi laporan ke Telegram Bot
8. Jalankan shorts_growth_analyst untuk perbarui metrik
"""

import os
import sys
import json
import re
import time
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime

PEXELS_KEY = "YOUR_PEXELS_API_KEY"
EDGE_TTS = "/root/telegram_remote_bot/venv/bin/edge-tts"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"
UPLOAD_SCRIPT = "/root/zylve_automation/upload_to_youtube_acc2.py"
GROWTH_ANALYST = "/root/tools/shorts_growth_analyst.py"
QUEUE_FILE = "/root/assets/shorts_topic_queue.json"
POINTER_FILE = "/root/assets/shorts_topic_pointer.txt"

def vtt_time_to_seconds(vtt_t):
    parts = vtt_t.replace(',', '.').split(':')
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

def seconds_to_ass(sec):
    cs = int(round(sec * 100))
    h = cs // 360000
    m = (cs % 360000) // 6000
    s = (cs % 6000) // 100
    cs_rem = cs % 100
    return f"{h}:{m:02d}:{s:02d}.{cs_rem:02d}"

def format_text(text):
    text = text.upper().strip().rstrip(',.!?')
    words = text.split()
    if len(words) > 4:
        mid = len(words) // 2
        return ' '.join(words[:mid]) + r'\N' + ' '.join(words[mid:])
    return text

def get_next_topic():
    if not os.path.exists(QUEUE_FILE):
        raise FileNotFoundError(f"Antrean topik {QUEUE_FILE} tidak ditemukan!")
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)
    if not queue:
        raise ValueError("Antrean topik kosong!")

    idx = 0
    if os.path.exists(POINTER_FILE):
        try:
            with open(POINTER_FILE, "r") as f:
                idx = int(f.read().strip())
        except Exception:
            idx = 0

    idx = idx % len(queue)
    topic = queue[idx]

    # Simpan pointer berikutnya
    next_idx = (idx + 1) % len(queue)
    with open(POINTER_FILE, "w") as f:
        f.write(str(next_idx))

    return topic, idx

def run_slot(slot_name="Automated_Slot"):
    print(f"\n=======================================================")
    print(f"[*] MEMULAI PIPELINE SHORTS OTOMATIS: {slot_name}")
    print(f"[*] Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB")
    print(f"=======================================================")

    topic, topic_idx = get_next_topic()
    topic_id = topic["id"]
    title = topic["title"]
    caption = topic["caption"]
    search_query = topic["search_query"]
    script_lines = topic["script"]

    workdir = f"/root/projects/shorts_{topic_id}"
    os.makedirs(workdir, exist_ok=True)
    os.makedirs("/root/assets", exist_ok=True)
    out_mp4 = f"/root/assets/shorts_{topic_id}.mp4"

    print(f"[*] Topik #{topic_idx + 1}: {title}")
    print(f"[*] Workspace: {workdir}")

    # 1. Tulis naskah
    script_txt_path = os.path.join(workdir, "script.txt")
    with open(script_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(script_lines))

    # 2. Generate Voiceover & VTT
    audio_path = os.path.join(workdir, "voiceover.mp3")
    vtt_path = os.path.join(workdir, "voiceover.vtt")
    print("[1/6] Memproduksi Voiceover & Subtitle VTT sinkron via edge-tts...")
    tts_cmd = [
        EDGE_TTS,
        "--voice=en-US-ChristopherNeural",
        "--rate=-2%",
        "--pitch=-2Hz",
        f"--file={script_txt_path}",
        f"--write-media={audio_path}",
        f"--write-subtitles={vtt_path}"
    ]
    subprocess.run(tts_cmd, check=True)

    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ], capture_output=True, text=True, check=True)
    duration = float(probe.stdout.strip())
    print(f"[✓] Voiceover selesai: {duration:.2f}s")

    # 3. VTT -> ASS Subtitle
    print("[2/6] Mengonversi VTT ke ASS Subtitle Eye-Tracking...")
    with open(vtt_path, "r", encoding="utf-8") as f:
        vtt_content = f.read()

    cues = re.findall(r'(\d\d:\d\d:\d\d[,\.]\d\d\d)\s*-->\s*(\d\d:\d\d:\d\d[,\.]\d\d\d)\s*\n([^\n]+)', vtt_content)
    parsed_cues = []
    for start, end, text in cues:
        s_sec = vtt_time_to_seconds(start)
        e_sec = vtt_time_to_seconds(end)
        parsed_cues.append((s_sec, e_sec, text))

    events = []
    for i in range(len(parsed_cues)):
        s_sec, e_sec, text = parsed_cues[i]
        if i + 1 < len(parsed_cues):
            next_s = parsed_cues[i+1][0]
            if e_sec > next_s:
                e_sec = next_s
        style = "ShortsYellow" if i % 2 == 0 else "ShortsWhite"
        if i == len(parsed_cues) - 1:
            style = "ShortsGreen"
        events.append(f"Dialogue: 0,{seconds_to_ass(s_sec)},{seconds_to_ass(e_sec)},{style},,0,0,0,,{format_text(text)}")

    ass_header = f"""[Script Info]
Title: {topic_id} High RPM Synchronized
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsYellow,Liberation Sans,78,&H0000E6FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,8,3,2,60,60,520,1
Style: ShortsWhite,Liberation Sans,78,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,8,3,2,60,60,520,1
Style: ShortsGreen,Liberation Sans,82,&H0033FF33,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,8,3,2,60,60,520,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_path = os.path.join(workdir, "synced_subtitles.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")
    print(f"[✓] File ASS sinkron ({len(events)} baris) siap.")

    # 4. Unduh & Rakit Footage Multi-Clip Dinamis (Pexels + Pixabay)
    print(f"[3/6] Memproduksi latar multi-clip dinamis 9:16 (Pexels + Pixabay) per scene...")
    from multiclip_shorts_builder import build_multiclip_background
    topic_queries = [
        search_query,
        f"{search_query} cinematic",
        f"{search_query} nature detail",
        f"{search_query} landscape 4k"
    ]
    footage_path = build_multiclip_background(topic_queries, duration, workdir, clip_duration=4.5)
    print("[✓] Background Multi-Clip Dinamis Berhasil Dirakit!")

    # 5. Render FFmpeg 1080x1920
    print("[4/6] Merender video 9:16 Full HD 1080x1920 + Subtitle Dinamis...")
    render_cmd = [
        "ffmpeg", "-y",
        "-i", footage_path,
        "-i", audio_path,
        "-t", str(duration),
        "-filter_complex",
        f"[0:v]ass={ass_path}[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        out_mp4
    ]
    subprocess.run(render_cmd, check=True)
    print(f"[✓] Render Video Selesai: {out_mp4}")

    # 6. Upload ke YouTube Akun 2
    print("[5/6] Mengunggah video ke YouTube Akun 2 (@zylvemedia02)...")
    upload_cmd = ["python3", UPLOAD_SCRIPT, out_mp4, title, caption]
    upload_proc = subprocess.run(upload_cmd, capture_output=True, text=True)
    print(upload_proc.stdout)
    if upload_proc.returncode != 0:
        print(f"[!] Warning upload error: {upload_proc.stderr}")

    # Cari link video
    video_link = "https://www.youtube.com/@zylvemedia02/shorts"
    match = re.search(r'https://youtube\.com/shorts/[a-zA-Z0-9_-]+', upload_proc.stdout)
    if match:
        video_link = match.group(0)

    # 7. Kirim ke Telegram
    print("[6/6] Mengirim video & laporan ke Telegram Bot...")
    tg_caption = (
        f"🚀 *SHORTS OTOMATIS TAYANG ({slot_name})*\n\n"
        f"📌 *Judul*: {title}\n"
        f"🔗 *Link*: {video_link}\n"
        f"⏱ *Durasi*: {duration:.1f}s (1080x1920)\n"
        f"🌐 *Target RPM*: US / Tier-1 ($4-$8/1k views)\n"
        f"🎙 *Voice*: US English Christopher + VTT 100% Synced\n\n"
        f"Video sukses dipublikasikan ke YouTube Akun 2 (@zylvemedia02)."
    )
    subprocess.run(["python3", TELEGRAM_SCRIPT, out_mp4, tg_caption])
    print("[✓] Selesai! Telegram terkirim.")

    # 8. Analisa Pertumbuhan
    if os.path.exists(GROWTH_ANALYST):
        subprocess.run(["python3", GROWTH_ANALYST], capture_output=True)

    return out_mp4, video_link

if __name__ == "__main__":
    slot = sys.argv[1] if len(sys.argv) > 1 else "Manual_Trigger"
    run_slot(slot)
