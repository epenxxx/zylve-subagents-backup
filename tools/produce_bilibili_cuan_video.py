#!/usr/bin/env python3
"""
produce_bilibili_cuan_video.py - Agent Bilibili
Memproduksi konten sains populer High-RPM 16:9 dengan voiceover Mandarin,
subtitle ASS, dan render hardware acceleration VAAPI, lalu upload ke Bilibili.
"""

import os
import sys
import json
import re
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

WORKDIR = "/root/projects/bilibili_cuan"
OUT_VIDEO = "/root/assets/bilibili_earth_stop_1s.mp4"
EDGE_TTS = "/root/telegram_remote_bot/venv/bin/edge-tts"
PEXELS_KEY = "YOUR_PEXELS_API_KEY"

TITLE = "如果地球突然停止自转1秒？全人类将面临毁灭性风暴！"
CAPTION = """如果地球突然停止自转，哪怕只有短短的1秒钟，世界会变成什么样？

很多人以为1秒钟眨眼就过，但真相足以毁灭全人类！在赤道，地球自转速度高达每小时1670公里。如果自转骤停，地表所有未固定的物体，将以超音速向东甩出！滔天海啸将瞬间吞没沿海大陆，地壳剧烈撕裂引发前所未有的全球大地震！

最可怕的是大气层仍在高速旋转，形成超越十级台风的毁灭性狂风！1秒之后自转恢复，留给地球的将是彻底被改写的地貌与废墟。

💬 面对这种毁灭性设想，你觉得人类科技未来能抵御吗？在评论区聊聊你的看法！

记得【一键三连 + 关注】，下期带你探索更惊人的宇宙未解之谜！

#科普 #科学 #宇宙 #地球 #物理 #天文 #一键三连 #未解之谜"""

TAGS = "科普 科学 宇宙 地球 物理 天文 一键三连 未解之谜"

SCRIPT_TEXT = (
    "如果地球突然停止自转，哪怕只有短短的一秒钟，世界会变成什么样？"
    "很多人以为一秒钟眨眼就过，但真相足以毁灭全人类。"
    "在赤道，地球自转速度高达每小时一千六百七十公里。"
    "如果自转骤停，地表所有未固定的物体，将以超音速向东猛烈甩出！"
    "滔天海啸将瞬间吞没沿海大陆，地壳剧烈撕裂，引发前所未有的全球超级大地震！"
    "最可怕的是，大气层仍在高速旋转，形成超越十级台风的毁灭性狂风！"
    "一秒之后自转恢复，留给地球的将是彻底被改写的地貌与废墟。"
    "你觉得人类科技未来能抵御这种灾难吗？记得一键三连并关注，下期更精彩！"
)

os.makedirs(WORKDIR, exist_ok=True)
os.makedirs("/root/assets", exist_ok=True)

def log(msg):
    print(f"[Agent Bilibili] {msg}", flush=True)

def generate_voiceover_and_vtt(audio_out, vtt_out):
    log("1. Menghasilkan voiceover Mandarin & VTT via edge-tts...")
    cmd = [
        EDGE_TTS,
        "--voice", "zh-CN-YunyangNeural",
        "--text", SCRIPT_TEXT,
        "--write-media", audio_out,
        "--write-subtitles", vtt_out
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Gagal generate TTS: {res.stderr}")
    log("Voiceover & VTT sukses dibuat.")

def vtt_to_ass(vtt_file, ass_file):
    log("2. Mengonversi VTT ke ASS subtitle berformat Bilibili...")
    header = """[Script Info]
Title: Bilibili Cuan Subtitle
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans CJK SC,62,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,4.5,2,2,40,40,75,1
Style: Highlight,Noto Sans CJK SC,66,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,3,2,40,40,75,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def convert_time(t_str):
        t_str = t_str.strip().replace(",", ".")
        parts = t_str.split(":")
        if len(parts) == 2:
            m = int(parts[0])
            s, ms = parts[1].split(".")
            return f"0:{m:02d}:{int(s):02d}.{int(ms[:2]):02d}"
        elif len(parts) == 3:
            h = int(parts[0])
            m = int(parts[1])
            s, ms = parts[2].split(".")
            return f"{h}:{m:02d}:{int(s):02d}.{int(ms[:2]):02d}"
        return "0:00:00.00"

    dialogues = []
    with open(vtt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.findall(r"(\d{2}:[0-9:.,]+)\s*-->\s*([0-9:.,]+)\s*\n(.*?)(?=\n\s*\d+\s*\n|\n\n|\Z)", content, re.DOTALL)
    for start, end, text in blocks:
        t_clean = text.strip().replace("\n", " ")
        if not t_clean:
            continue
        st = convert_time(start)
        et = convert_time(end)
        style = "Highlight" if any(w in t_clean for w in ["一秒钟", "毁灭", "海啸", "大地震", "狂风", "一键三连"]) else "Default"
        dialogues.append(f"Dialogue: 0,{st},{et},{style},,0,0,0,,{t_clean}")

    with open(ass_file, 'w', encoding='utf-8') as f:
        f.write(header + "\n".join(dialogues) + "\n")
    log(f"Subtitle ASS selesai: {len(dialogues)} baris dialog.")

def fetch_pexels_video(query, target_file):
    log(f"3. Mencari footage 16:9 di Pexels untuk query '{query}'...")
    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation=landscape&per_page=5"
    req = urllib.request.Request(url, headers={
        "Authorization": PEXELS_KEY,
        "User-Agent": "Mozilla/5.0"
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    videos = data.get("videos", [])
    if not videos:
        raise RuntimeError(f"Tidak ada video ditemukan untuk query '{query}'")
    
    # Pilih video resolusi 1080p atau 720p
    chosen_link = None
    for v in videos:
        for vf in v.get("video_files", []):
            if vf.get("width", 0) >= 1280 and vf.get("height", 0) >= 720:
                chosen_link = vf.get("link")
                break
        if chosen_link:
            break
    
    if not chosen_link:
        chosen_link = videos[0]["video_files"][0]["link"]

    log(f"Mengunduh footage dari Pexels...")
    dl_req = urllib.request.Request(chosen_link, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(dl_req) as response, open(target_file, 'wb') as out_file:
        out_file.write(response.read())
    log(f"Footage tersimpan: {target_file}")

def get_audio_duration(audio_file):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return float(res.stdout.strip())

def render_video_with_vaapi(video_in, audio_in, ass_in, video_out, duration):
    log("4. Rendering video 16:9 Full HD dengan akselerasi hardware VAAPI...")
    # Escape path untuk filter subtitles ffmpeg
    escaped_ass = ass_in.replace(":", "\\:").replace("'", "\\'")
    
    # Filter: loop video to match duration, scale to 1920x1080, burn subtitle ASS, format nv12, upload ke VAAPI
    vf = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,subtitles='{escaped_ass}',format=nv12,hwupload"
    
    cmd = [
        "ffmpeg", "-y",
        "-vaapi_device", "/dev/dri/renderD128",
        "-stream_loop", "-1",
        "-i", video_in,
        "-i", audio_in,
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "h264_vaapi",
        "-b:v", "5M",
        "-maxrate", "8M",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        video_out
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        log(f"FFmpeg error: {res.stderr[-400:]}")
        raise RuntimeError("Gagal render dengan VAAPI.")
    log(f"[✓] Render VAAPI sukses: {video_out}")

def main():
    audio_path = os.path.join(WORKDIR, "voice.mp3")
    vtt_path = os.path.join(WORKDIR, "sub.vtt")
    ass_path = os.path.join(WORKDIR, "sub.ass")
    bg_video_path = os.path.join(WORKDIR, "bg_space_earth.mp4")

    # 1. Voiceover
    generate_voiceover_and_vtt(audio_path, vtt_path)
    dur = get_audio_duration(audio_path)
    log(f"Durasi audio narasi: {dur:.2f} detik")

    # 2. Subtitle ASS
    vtt_to_ass(vtt_path, ass_path)

    # 3. Footage 16:9 Pexels
    fetch_pexels_video("planet earth space rotation", bg_video_path)

    # 4. Render VAAPI
    render_video_with_vaapi(bg_video_path, audio_path, ass_path, OUT_VIDEO, dur)

    # 5. Analisis Pre-Upload via bilibili_video_analyzer.py
    log("5. Menjalankan analisis kualitas pre-upload Agent Bilibili...")
    res_probe = subprocess.run(
        ["/usr/bin/python3", "/root/tools/bilibili_video_analyzer.py", OUT_VIDEO, TITLE, CAPTION],
        capture_output=True, text=True
    )
    print(res_probe.stdout)

    # 6. Upload Otomatis ke Bilibili
    log("6. Mengunggah video ke Bilibili via Playwright...")
    up_cmd = [
        "/usr/bin/python3",
        "/root/zylve_automation/upload_to_bilibili.py",
        OUT_VIDEO,
        TITLE,
        CAPTION,
        TAGS
    ]
    up_res = subprocess.run(up_cmd, capture_output=True, text=True)
    print(up_res.stdout)
    if up_res.returncode == 0:
        log("🎉 KONTEN BERHASIL TERBIT DI BILIBILI DENGAN SUKSES!")
    else:
        log(f"Upload Bilibili gagal: {up_res.stderr}")

if __name__ == "__main__":
    main()
