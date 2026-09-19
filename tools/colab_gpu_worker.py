#!/usr/bin/env python3
"""
colab_gpu_worker.py - CLI Utilitas Pemanggil Eksekusi GPU Colab dari Server Lokal
Dikelola oleh Cimoy (agent_orchestrator).
Mendukung:
1. Pemisahan Audio Karaoke (Demucs v4)
2. Transkripsi Lirik & Subtitle (Whisper Large-v3)
3. Render Video FFmpeg NVENC
"""

import os
import sys
import argparse
import requests

TUNNEL_FILE = "/root/.config/colab/tunnel_url.txt"

def get_tunnel_url():
    if not os.path.exists(TUNNEL_FILE):
        return None
    with open(TUNNEL_FILE, "r") as f:
        url = f.read().strip()
    return url if url else None

def check_health(url):
    try:
        r = requests.get(f"{url}/health", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def separate_audio(url, audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Error: File audio {audio_path} tidak ditemukan.")
        return False
    print(f"Mengirim {audio_path} ke Demucs v4 di Colab GPU...")
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
        r = requests.post(f"{url}/separate", files=files, timeout=300)
    if r.status_code == 200:
        with open(output_path, "wb") as out:
            out.write(r.content)
        print(f"Sukses! Instrumen karaoke tersimpan di: {output_path}")
        return True
    else:
        print(f"Gagal memisahkan audio: {r.status_code} - {r.text}")
        return False

def transcribe_audio(url, audio_path):
    if not os.path.exists(audio_path):
        print(f"Error: File audio {audio_path} tidak ditemukan.")
        return None
    print(f"Mentranskripsi {audio_path} via Whisper Large-v3 di Colab GPU...")
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
        r = requests.post(f"{url}/transcribe", files=files, timeout=300)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Gagal transkripsi: {r.status_code} - {r.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="ZYLVE Colab GPU CLI Client")
    parser.add_argument("action", choices=["status", "separate", "transcribe"], help="Aksi yang dijalankan")
    parser.add_argument("--input", "-i", help="Path file audio/video input")
    parser.add_argument("--output", "-o", help="Path file output")
    args = parser.parse_args()

    url = get_tunnel_url()
    if not url:
        print("URL tunnel Colab belum tersimpan di /root/.config/colab/tunnel_url.txt")
        print("Pastikan worker di Colab sudah aktif.")
        sys.exit(1)

    if args.action == "status":
        health = check_health(url)
        print("Status Colab GPU:", health)
    elif args.action == "separate":
        if not args.input or not args.output:
            print("Wajib sertakan --input dan --output")
            sys.exit(1)
        separate_audio(url, args.input, args.output)
    elif args.action == "transcribe":
        if not args.input:
            print("Wajib sertakan --input")
            sys.exit(1)
        res = transcribe_audio(url, args.input)
        if res:
            print("Hasil Transkripsi:", res.get("language"), f"{res.get('duration')}s")
            for s in res.get("segments", [])[:10]:
                print(f"[{s['start']}s -> {s['end']}s] {s['text']}")

if __name__ == "__main__":
    main()
