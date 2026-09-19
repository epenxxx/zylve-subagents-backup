#!/usr/bin/env python3
"""
ElevenLabs Engine ZYLVEmedia
Otomasi Text-to-Speech Ultra-Realistis dengan Auto-Fallback ke Edge-TTS.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import subprocess

KEY_FILE = "/root/.config/elevenlabs/api_key"

def get_api_key():
    key = os.getenv("ELEVENLABS_API_KEY")
    if key and key.strip():
        return key.strip()
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    return None

# Voice ID Populer:
# - George (British, Storyteller): JBFqnCBsd6RMkjVDRZzb
# - Charlie (Australian, Deep & Energetic): IKne3meq5aSn9XLyUdCD
# - Roger (American, Casual Resonant): CwhRBWXzGAHq8TQ4Fs17
# - Sarah (American, Reassuring News): EXAVITQu4vr4xnSDxMaL
DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"

def generate_speech_elevenlabs(text, output_path, voice_id=DEFAULT_VOICE, model_id="eleven_multilingual_v2"):
    api_key = get_api_key()
    if not api_key:
        raise ValueError("API Key ElevenLabs tidak ditemukan.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.2,
            "use_speaker_boost": True
        }
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            audio_bytes = resp.read()
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            return output_path
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"ElevenLabs HTTP Error {e.code}: {err_msg}")

def fallback_edge_tts(text, output_path, voice="en-US-ChristopherNeural"):
    """Fallback otomatis ke Edge-TTS jika kuota ElevenLabs habis atau offline"""
    edge_bin = "/root/telegram_remote_bot/venv/bin/edge-tts"
    if not os.path.exists(edge_bin):
        edge_bin = "edge-tts"
    cmd = [edge_bin, f"--voice={voice}", f"--text={text}", f"--write-media={output_path}"]
    subprocess.run(cmd, check=True)
    return output_path

def synthesize(text, output_path, voice_id=DEFAULT_VOICE, fallback=True):
    try:
        print(f"[*] Mencoba generate TTS via ElevenLabs (Voice ID: {voice_id})...")
        return generate_speech_elevenlabs(text, output_path, voice_id=voice_id)
    except Exception as e:
        print(f"[!] ElevenLabs terkendala: {e}")
        if fallback:
            print("[*] Mengaktifkan Fallback otomatis ke Edge-TTS Neural...")
            return fallback_edge_tts(text, output_path)
        raise e

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan: python3 elevenlabs_engine.py \"Teks narasi\" [output.mp3] [voice_id]")
        sys.exit(1)

    text_input = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else "/root/assets/test_elevenlabs.mp3"
    v_id = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_VOICE

    res = synthesize(text_input, out_file, voice_id=v_id)
    print(f"[✓] Audio berhasil disimpan: {res} ({os.path.getsize(res)} bytes)")
