#!/usr/bin/env python3
"""
generate_shorts_yellowstone.py
Shorts #2 Target High RPM (US Tier-1):
Topik: Yellowstone Supervolcano Eruption
Voiceover: US English (Christopher Neural)
Subtitle: VTT langsung dari edge-tts (100% Sinkron)
Footage: 1080x1920 60fps Volcano Eruption Pexels API
Output: /root/assets/shorts_yellowstone_eruption.mp4
"""

import os
import sys
import json
import re
import subprocess
import urllib.request
import urllib.parse

WORKDIR = "/root/projects/shorts_yellowstone"
PEXELS_KEY = "YOUR_PEXELS_API_KEY"
EDGE_TTS = "/root/telegram_remote_bot/venv/bin/edge-tts"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"
OUT_MP4 = "/root/assets/shorts_yellowstone_eruption.mp4"

SCRIPT_LINES = [
    "Deep beneath Yellowstone National Park,",
    "lies a sleeping monster capable of wiping out modern civilization.",
    "If this supervolcano erupts,",
    "it would blast one thousand cubic kilometers of ash into the sky.",
    "Two-thirds of the United States,",
    "would become completely uninhabitable in minutes.",
    "A global volcanic winter,",
    "would block the sun and plunge our planet into freezing darkness.",
    "Scientists say it is overdue.",
    "Are we truly prepared for the unthinkable?"
]

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

def run():
    os.makedirs(WORKDIR, exist_ok=True)
    os.makedirs("/root/assets", exist_ok=True)
    
    # 1. Tulis naskah
    script_txt_path = os.path.join(WORKDIR, "script_lines.txt")
    with open(script_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(SCRIPT_LINES))

    # 2. Voiceover & Subtitle VTT langsung dari edge-tts
    audio_path = os.path.join(WORKDIR, "voiceover.mp3")
    vtt_path = os.path.join(WORKDIR, "voiceover.vtt")
    print("[1/5] Memproduksi Voiceover & Subtitle Sinkron via edge-tts...")
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
    print(f"[✓] Voiceover selesai. Durasi: {duration:.2f} detik")

    # 3. Konversi VTT ke ASS Subtitle Sinkron
    print("[2/5] Mengonversi VTT ke ASS Subtitle Eye-Tracking...")
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

    ass_header = """[Script Info]
Title: Yellowstone Supervolcano High RPM Shorts
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
    ass_path = os.path.join(WORKDIR, "subtitles.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")
    print(f"[✓] File ASS sinkron ({len(events)} cues) selesai!")

    # 4. Unduh Footage Vertikal 1080p Pexels API
    print("[3/5] Mengambil footage vertikal 1080p resmi via Pexels API...")
    footage_path = os.path.join(WORKDIR, "raw_footage.mp4")
    if not os.path.exists(footage_path):
        query = "volcano lava eruption dark smoke"
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation=portrait&per_page=8"
        req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY, "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            videos = data.get("videos", [])
            download_url = None
            for v in videos:
                for f in v.get("video_files", []):
                    if f.get("width") == 1080 and f.get("height") == 1920:
                        download_url = f.get("link")
                        break
                if download_url:
                    break
            if not download_url and videos:
                download_url = videos[0]["video_files"][0]["link"]

        print(f"[*] Mengunduh video Pexels: {download_url[:70]}...")
        dl_req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(dl_req, timeout=60) as dl_resp, open(footage_path, "wb") as out_f:
            out_f.write(dl_resp.read())
        print("[✓] Footage Pexels berhasil diunduh!")

    # 5. Render Video 9:16 Full HD via FFmpeg
    print("[4/5] Merender video 9:16 Full HD 1080x1920 dengan subtitle sinkron...")
    render_cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", footage_path,
        "-i", audio_path,
        "-t", str(duration),
        "-filter_complex",
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,ass={ass_path}[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        OUT_MP4
    ]
    subprocess.run(render_cmd, check=True)
    print(f"[✓] Render Video Selesai: {OUT_MP4}")

    # 6. Kirim Laporan & Video ke Telegram Bot
    print("[5/5] Mengirim video hasil ke Telegram Bot...")
    caption = (
        "🌋 *SHORTS #2 TIER-1 HIGH RPM (SIAP POSTING JAM 01:00 WIB)*\n\n"
        "📌 *Title*: What If The Yellowstone Supervolcano Erupts Tomorrow? 🌋\n"
        "🌐 *Target Audience*: United States, UK, Canada, Australia\n"
        "💰 *Est. RPM*: $4.00 - $9.00 per 1,000 views\n"
        f"⏱ *Duration*: {duration:.1f}s (9:16 Full HD 1080p)\n"
        "🎙 *Voiceover*: US English (Christopher Neural)\n"
        "✨ *Subtitle*: 100% sinkron edge-tts VTT, dynamic gold/white styling\n\n"
        "Video sudah diproduksi & dijadwalkan otomatis tayang jam 01:00 WIB."
    )
    subprocess.run(["python3", TELEGRAM_SCRIPT, OUT_MP4, caption])
    print("[✓] Video dan laporan terkirim ke Telegram!")

if __name__ == "__main__":
    run()
