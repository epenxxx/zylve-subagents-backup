#!/usr/bin/env python3
"""
Eksekutor Pemisahan Audio Karaoke Hugging Face (Agent 2)
Memanggil Hugging Face Space: https://huggingface.co/spaces/abidlabs/music-separation
menggunakan Gradio Client resmi dengan autentikasi Hugging Face Token (hf_...)
untuk pemisahan vokal & instrumen 100% murni ZeroGPU AI.
"""

import os
import sys
import time
import argparse
import subprocess
from gradio_client import Client, handle_file

TOKEN_FILE = "/root/zylve_automation/huggingface_token.txt"
BACKUP_TOKEN_FILE = "/root/.cache/huggingface/token"
DEFAULT_TOKEN = "hf_YOUR_HUGGINGFACE_TOKEN"


def get_hf_token():
    for fpath in [TOKEN_FILE, BACKUP_TOKEN_FILE]:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                tok = f.read().strip()
                if tok.startswith("hf_"):
                    return tok
    return DEFAULT_TOKEN


def separate_karaoke_hf(input_audio, output_karaoke, output_vocals=None, retries=3):
    input_audio = os.path.abspath(input_audio)
    output_karaoke = os.path.abspath(output_karaoke)
    if output_vocals:
        output_vocals = os.path.abspath(output_vocals)

    if not os.path.exists(input_audio):
        print(f"[!] Berkas audio tidak ditemukan: {input_audio}")
        return False

    token = get_hf_token()
    print("[*] [Agent 2 - Hugging Face Music Separation]")
    print(f"    - Input: {input_audio}")
    print(f"    - Output Karaoke: {output_karaoke}")
    print(f"    - Endpoint: https://huggingface.co/spaces/abidlabs/music-separation")
    print(f"    - Auth Token: {token[:8]}...{token[-4:]}")

    for attempt in range(1, retries + 1):
        try:
            print(f"[*] Menghubungkan ke Gradio Space abidlabs/music-separation (Percobaan {attempt}/{retries})...")
            client = Client("abidlabs/music-separation", token=token)
            
            t0 = time.time()
            print("[*] Mengunggah audio dan memproses pemisahan AI di ZeroGPU...")
            res = client.predict(
                audio=handle_file(input_audio),
                api_name="/inference"
            )
            elapsed = time.time() - t0
            print(f"[✓] Pemisahan AI Sukses dalam {elapsed:.1f} detik!")

            vocals_wav, inst_wav = res
            os.makedirs(os.path.dirname(output_karaoke), exist_ok=True)

            # Master Studio Super Smooth, Denoise FFT, Audio Gate & Pure Acoustic
            print("[*] Menerapkan Studio Super Smooth (Audio Gate, FFT Denoise, Pure Acoustic Restoration)...")
            af_chain = (
                "highpass=f=35,"
                "lowpass=f=15000,"
                "afftdn=nr=14:nf=-42:tn=1:gs=4,"
                "agate=threshold=0.012:ratio=2.5:attack=25:release=250,"
                "equalizer=f=3100:t=q:w=1.5:g=-3.0,"
                "equalizer=f=85:t=q:w=1.2:g=1.8,"
                "equalizer=f=250:t=q:w=1.0:g=1.2,"
                "adynamicsmooth=sensitivity=2:basefreq=12000,"
                "loudnorm=I=-14.0:TP=-1.0:LRA=11"
            )
            cmd_inst = f'ffmpeg -y -i "{inst_wav}" -af "{af_chain}" -c:a libmp3lame -b:a 320k "{output_karaoke}" >/dev/null 2>&1'
            subprocess.run(cmd_inst, shell=True, check=True)
            print(f"[✓] Berkas Karaoke HD Master Anti-Copyright Tersimpan: {output_karaoke} ({os.path.getsize(output_karaoke)} bytes)")

            if output_vocals:
                os.makedirs(os.path.dirname(output_vocals), exist_ok=True)
                cmd_voc = f'ffmpeg -y -i "{vocals_wav}" -c:a libmp3lame -b:a 192k "{output_vocals}" >/dev/null 2>&1'
                subprocess.run(cmd_voc, shell=True, check=True)
                print(f"[✓] Berkas Vokal Tersimpan: {output_vocals} ({os.path.getsize(output_vocals)} bytes)")

            return True

        except Exception as e:
            print(f"[!] Error pada percobaan {attempt}: {e}")
            if attempt < retries:
                print("[*] Menunggu 5 detik sebelum mencoba kembali...")
                time.sleep(5)

    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pemisah Audio Karaoke Hugging Face abidlabs/music-separation")
    parser.add_argument("input", help="Path berkas audio input")
    parser.add_argument("-o", "--output", default=None, help="Path berkas karaoke output")
    parser.add_argument("--vocals", default=None, help="Path berkas vokal output (opsional)")

    args, unknown = parser.parse_known_args()
    input_file = args.input
    output_file = args.output
    vocals_file = args.vocals

    if not output_file and unknown:
        output_file = unknown[0]
        if len(unknown) > 1:
            vocals_file = unknown[1]

    if not output_file:
        output_file = "karaoke_output.mp3"

    success = separate_karaoke_hf(input_file, output_file, vocals_file)
    sys.exit(0 if success else 1)
