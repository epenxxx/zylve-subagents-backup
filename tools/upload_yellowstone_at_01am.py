#!/usr/bin/env python3
"""
upload_yellowstone_at_01am.py
Eksekutor Otomatis Upload Shorts Yellowstone ke YouTube Akun 2 pada Jam 01:00 WIB
"""

import os
import sys
import subprocess

VIDEO_FILE = "/root/assets/shorts_yellowstone_eruption.mp4"
TITLE = "What If The Yellowstone Supervolcano Erupts Tomorrow? 🌋 #Shorts #Facts #Science"
CAPTION = "What happens if Yellowstone supervolcano erupts? A look into nature's deadliest disaster. #Shorts #Yellowstone #Science #Facts #Volcano #DidYouKnow #Earth"
UPLOADER = "/root/zylve_automation/upload_to_youtube_acc2.py"
TELEGRAM_SCRIPT = "/root/telegram_remote_bot/send_telegram.py"

def main():
    print(f"[*] Menjalankan Upload Terjadwal Jam 01:00 WIB...")
    if not os.path.exists(VIDEO_FILE):
        print(f"[!] File {VIDEO_FILE} tidak ditemukan, membuat video terlebih dahulu...")
        subprocess.run(["python3", "/root/tools/generate_shorts_yellowstone.py"], check=True)

    # Eksekusi upload ke YouTube Akun 2
    cmd = ["python3", UPLOADER, VIDEO_FILE, TITLE, CAPTION]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Output upload:")
    print(res.stdout)
    if res.returncode != 0:
        print("Error upload:", res.stderr)
        msg = f"❌ *UPLOAD SHORTS 01:00 GAGAL*\n\nError: `{res.stderr[-300:]}`"
        subprocess.run(["python3", TELEGRAM_SCRIPT, msg])
        sys.exit(1)

    # Kirim konfirmasi sukses ke Telegram
    msg = (
        "🚀 *JADWAL 01:00 WIB: SHORTS #2 SUKSES TAYANG!*\n\n"
        f"📌 *Judul*: {TITLE}\n"
        "🌐 *Target*: US / UK High RPM\n"
        "📺 *Channel*: YouTube Akun 2 (ZYLVEmedia02)\n\n"
        "Status: Publik 100%!"
    )
    subprocess.run(["python3", TELEGRAM_SCRIPT, msg])
    print("[✓] Jadwal 01:00 WIB selesai sukses!")

if __name__ == "__main__":
    main()
