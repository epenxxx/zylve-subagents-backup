#!/usr/bin/env python3
"""
run_tim_bilibili_pipeline.py - Runner Otomatis Tim Bilibili
Memproduksi konten sains & teknologi High-RPM secara otomatis sesuai jadwal slot jam ramai China,
merender dengan akselerasi hardware VAAPI, dan mempublikasikannya ke Bilibili Studio Creator.
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

QUEUE_PATH = "/root/assets/bilibili_topic_queue.json"
WORKDIR = "/root/projects/bilibili_cuan"
EDGE_TTS = "/root/telegram_remote_bot/venv/bin/edge-tts"
PEXELS_KEY = "YOUR_PEXELS_API_KEY"
LOG_FILE = "/root/logs/tim_bilibili.log"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"
PROOF_SCREENSHOT = "/root/screenshots/bilibili_upload_proof.png"

os.makedirs("/root/logs", exist_ok=True)
os.makedirs(WORKDIR, exist_ok=True)
os.makedirs("/root/assets", exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S WIB]")
    text = f"{ts} [TIM-BILIBILI] {msg}"
    print(text, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(text + "\n")

def send_telegram_alert(message, image_path=None):
    if not os.path.exists(TELEGRAM_SCRIPT):
        return
    try:
        cmd = ['/usr/bin/python3', TELEGRAM_SCRIPT]
        if image_path and os.path.exists(image_path):
            cmd.extend([image_path, message])
        else:
            cmd.append(message)
        subprocess.run(cmd, timeout=30)
    except Exception as e:
        log(f"Gagal kirim Telegram: {e}")

def vtt_to_ass(vtt_file, ass_file):
    header = """[Script Info]
Title: Bilibili Subtitle
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
        style = "Highlight" if any(w in t_clean for w in ["一秒钟", "毁灭", "海啸", "瞬间", "大地震", "狂风", "一键三连", "黑洞", "火星", "量子"]) else "Default"
        dialogues.append(f"Dialogue: 0,{st},{et},{style},,0,0,0,,{t_clean}")

    with open(ass_file, 'w', encoding='utf-8') as f:
        f.write(header + "\n".join(dialogues) + "\n")
    log(f"Subtitle ASS siap: {len(dialogues)} baris dialog.")

def fetch_pexels_video(query, target_file):
    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation=landscape&per_page=5"
    req = urllib.request.Request(url, headers={
        "Authorization": PEXELS_KEY,
        "User-Agent": "Mozilla/5.0"
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    videos = data.get("videos", [])
    if not videos:
        raise RuntimeError(f"Video footage tidak ditemukan untuk: {query}")
    
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

    dl_req = urllib.request.Request(chosen_link, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(dl_req) as response, open(target_file, 'wb') as out_file:
        out_file.write(response.read())

def get_audio_duration(audio_file):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return float(res.stdout.strip())

def main():
    slot_name = sys.argv[1] if len(sys.argv) > 1 else "Auto"
    log(f"=== EKSEKUSI PIPELINE TIM BILIBILI: {slot_name.upper()} ===")

    if not os.path.exists(QUEUE_PATH):
        log(f"Error: Antrean {QUEUE_PATH} tidak ditemukan.")
        return

    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        queue = json.load(f)

    target_item = None
    target_idx = -1
    for idx, item in enumerate(queue):
        if item.get("status") == "ready":
            target_item = item
            target_idx = idx
            break

    if not target_item:
        log("Semua topik dalam antrean Tim Bilibili sudah diproduksi! Butuh generate stok baru.")
        send_telegram_alert("⚠️ *Peringatan Tim Bilibili*: Antrean topik High-RPM Bilibili sudah habis!")
        return

    item_id = target_item["id"]
    title = target_item["title"]
    script_text = target_item["script_text"]
    caption = target_item["caption"]
    tags = target_item.get("tags", "科普 科学 宇宙 天文 一键三连")
    query = target_item.get("query", "space planet universe")

    log(f"Memproses Topik #{item_id:02d}: '{title}'...")

    audio_path = os.path.join(WORKDIR, f"voice_{item_id}.mp3")
    vtt_path = os.path.join(WORKDIR, f"sub_{item_id}.vtt")
    ass_path = os.path.join(WORKDIR, f"sub_{item_id}.ass")
    footage_path = os.path.join(WORKDIR, f"footage_{item_id}.mp4")
    out_video = f"/root/assets/bilibili_slot_{item_id}.mp4"

    # 1. TTS Voiceover
    cmd_tts = [
        EDGE_TTS,
        "--voice", "zh-CN-YunyangNeural",
        "--text", script_text,
        "--write-media", audio_path,
        "--write-subtitles", vtt_path
    ]
    subprocess.run(cmd_tts, check=True)
    dur = get_audio_duration(audio_path)
    log(f"Audio narasi siap: {dur:.2f}s")

    # 2. Subtitle
    vtt_to_ass(vtt_path, ass_path)

    # 3. Footage Pexels
    fetch_pexels_video(query, footage_path)

    # 4. VAAPI Hardware Render
    log(f"Rendering dengan akselerasi hardware VAAPI...")
    escaped_ass = ass_path.replace(":", "\\:").replace("'", "\\'")
    vf = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,subtitles='{escaped_ass}',format=nv12,hwupload"
    cmd_render = [
        "ffmpeg", "-y",
        "-vaapi_device", "/dev/dri/renderD128",
        "-stream_loop", "-1",
        "-i", footage_path,
        "-i", audio_path,
        "-t", str(dur),
        "-vf", vf,
        "-c:v", "h264_vaapi",
        "-b:v", "5M",
        "-maxrate", "8M",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        out_video
    ]
    res_render = subprocess.run(cmd_render, capture_output=True, text=True)
    if res_render.returncode != 0:
        log(f"Error render: {res_render.stderr[-300:]}")
        return
    log(f"Render VAAPI sukses: {out_video}")

    # 5. Pre-upload Quality & Safety Check
    check_res = subprocess.run(
        ["/usr/bin/python3", "/root/tools/bilibili_video_analyzer.py", out_video, title, caption],
        capture_output=True, text=True
    )
    log(f"Hasil Analisis Kualitas: {check_res.stdout[:200]}")

    # 6. Upload Bilibili
    log("Mengunggah video ke Bilibili Studio...")
    up_cmd = [
        "/usr/bin/python3",
        "/root/zylve_automation/upload_to_bilibili.py",
        out_video,
        title,
        caption,
        tags
    ]
    up_res = subprocess.run(up_cmd, capture_output=True, text=True)
    if up_res.returncode == 0:
        queue[target_idx]["status"] = "uploaded"
        queue[target_idx]["uploaded_at"] = datetime.now().isoformat()
        queue[target_idx]["slot"] = slot_name
        with open(QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)

        remaining = sum(1 for x in queue if x.get("status") == "ready")
        log(f"🎉 Sukses tayang di Bilibili! Sisa stok: {remaining} topik.")

        tg_msg = (
            f"🚀 *Tim Bilibili: Konten Cuan Tayang!*\n"
            f"📺 *Platform*: Bilibili Studio Creator\n"
            f"⏰ *Slot*: {slot_name}\n"
            f"🎬 *Judul*: `{title}`\n"
            f"⚡ *Engine*: AMD VAAPI Hardware Render (1080p 16:9 + Hardsub)\n"
            f"📦 *Sisa Antrean*: {remaining} topik"
        )
        send_telegram_alert(tg_msg, PROOF_SCREENSHOT)
    else:
        log(f"Gagal upload: {up_res.stderr[-300:]}")

if __name__ == "__main__":
    main()
