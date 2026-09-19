#!/usr/bin/env python3
"""
broadcast_telegram_channel.py
Otomasi Publikasi Berita ke Saluran Resmi Telegram: @zylvemedia_news (ZYLVEmedia News).
Menggunakan jalur cepat Cloudflare WARP 1.1.1.1 (1 detik upload, zero timeout).
"""

import os
import sys
import json
import subprocess

BOT_TOKEN = "8788641167:AAFykL_fSuyHag_C7igtIACoe13-164-L3I"
CHANNEL_ID = "-1004342580936" # @zylvemedia_news
PROXY = "http://127.0.0.1:8118" if os.path.exists("/usr/local/bin/with_warp") else None

def broadcast_photo(image_path, caption=""):
    if not os.path.exists(image_path):
        print(f"[!] File poster tidak ditemukan: {image_path}")
        return False

    for mode in ["HTML", "Markdown", None]:
        cmd = [
            "curl", "-s",
            "-F", f"chat_id={CHANNEL_ID}",
            "-F", f"caption={caption}",
            "-F", f"photo=@{image_path}"
        ]
        if mode:
            cmd.extend(["-F", f"parse_mode={mode}"])
        if PROXY:
            cmd.extend(["-x", PROXY])
        cmd.append(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto")

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            data = json.loads(res.stdout)
            if data.get("ok"):
                msg_id = data.get("result", {}).get("message_id")
                print(f"[✓] SUKSES! Poster tayang di @zylvemedia_news (Message ID: {msg_id})")
                return True
        except Exception:
            pass

    print("[!] Gagal broadcast foto setelah mencoba semua parse_mode.")
    return False

def broadcast_message(text):
    for mode in ["HTML", "Markdown", None]:
        cmd = [
            "curl", "-s",
            "-F", f"chat_id={CHANNEL_ID}",
            "-F", f"text={text}"
        ]
        if mode:
            cmd.extend(["-F", f"parse_mode={mode}"])
        if PROXY:
            cmd.extend(["-x", PROXY])
        cmd.append(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage")

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            data = json.loads(res.stdout)
            if data.get("ok"):
                msg_id = data.get("result", {}).get("message_id")
                print(f"[✓] SUKSES! Pesan tayang di @zylvemedia_news (Message ID: {msg_id})")
                return True
        except Exception:
            pass

    print("[!] Gagal broadcast pesan setelah mencoba semua parse_mode.")
    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Penggunaan: python3 broadcast_telegram_channel.py photo <path_gambar> [caption]")
        print("            python3 broadcast_telegram_channel.py text <pesan>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "photo":
        img = sys.argv[2]
        cap = sys.argv[3] if len(sys.argv) > 3 else "ZYLVEmedia News Update"
        ok = broadcast_photo(img, cap)
        sys.exit(0 if ok else 1)
    elif cmd == "text":
        txt = " ".join(sys.argv[2:])
        ok = broadcast_message(txt)
        sys.exit(0 if ok else 1)
    else:
        if os.path.exists(sys.argv[1]):
            cap = sys.argv[2] if len(sys.argv) > 2 else "ZYLVEmedia News Update"
            ok = broadcast_photo(sys.argv[1], cap)
            sys.exit(0 if ok else 1)
        else:
            ok = broadcast_message(" ".join(sys.argv[1:]))
            sys.exit(0 if ok else 1)
