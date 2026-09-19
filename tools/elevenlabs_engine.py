#!/usr/bin/env python3
"""
ElevenLabs Universal Engine ZYLVEmedia
Otomasi Text-to-Speech Utama dengan Dukungan Subtitle WebVTT Sinkron & Auto-Fallback.
"""

import os
import sys
import json
import base64
import re
import urllib.request
import urllib.error
import subprocess

KEY_FILE = "/root/.config/elevenlabs/api_key"

# Voice ID Resmi ElevenLabs ZYLVEmedia (Premade Tier - Free/All Tier Compatible):
VOICE_NEWS_ID_MALE = "onwK4e9ZLuTAKqWW03F9"      # Daniel - Steady Broadcaster (Multilingual)
VOICE_NEWS_ID_FEMALE = "EXAVITQu4vr4xnSDxMaL"    # Sarah - Mature Reassuring News (Multilingual)
VOICE_SHORTS_EN = "JBFqnCBsd6RMkjVDRZzb"         # George - Warm Captivating Storyteller (US/UK Shorts)
VOICE_CREATOR_EN = "TX3LPaxmHKxFdv7VOQHJ"        # Liam - Energetic Social Media Creator
VOICE_ROGER_EN = "CwhRBWXzGAHq8TQ4Fs17"          # Roger - American Laid-Back Resonant

DEFAULT_VOICE = VOICE_SHORTS_EN

def get_api_key():
    key = os.getenv("ELEVENLABS_API_KEY")
    if key and key.strip():
        return key.strip()
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    return None

def alignment_to_vtt(alignment, words_per_cue=4):
    """Konversi karakter timestamp ElevenLabs menjadi WebVTT sinkron kata"""
    chars = alignment.get('characters', [])
    starts = alignment.get('character_start_times_seconds', [])
    ends = alignment.get('character_end_times_seconds', [])

    words = []
    curr_word = ''
    w_start = None
    w_end = None

    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if curr_word:
                words.append({'word': curr_word, 'start': w_start, 'end': w_end})
                curr_word = ''
                w_start = None
                w_end = None
        else:
            if w_start is None:
                w_start = s
            curr_word += c
            w_end = e
    if curr_word:
        words.append({'word': curr_word, 'start': w_start, 'end': w_end})

    def fmt_time(sec):
        m = int(sec // 60)
        s = int(sec % 60)
        ms = int(round((sec - int(sec)) * 1000))
        return f"00:{m:02d}:{s:02d}.{ms:03d}"

    vtt = ["WEBVTT\n"]
    for i in range(0, len(words), words_per_cue):
        chunk = words[i:i+words_per_cue]
        start_str = fmt_time(chunk[0]['start'])
        end_str = fmt_time(chunk[-1]['end'])
        text_str = ' '.join(w['word'] for w in chunk)
        vtt.append(f"{start_str} --> {end_str}\n{text_str}\n")

    return '\n'.join(vtt)

def fallback_edge_tts(text, output_audio_path, output_vtt_path=None, voice="en-US-ChristopherNeural"):
    """Fallback ke Edge-TTS jika kuota ElevenLabs limit atau error"""
    edge_bin = "/root/telegram_remote_bot/venv/bin/edge-tts"
    if not os.path.exists(edge_bin):
        edge_bin = "edge-tts"

    cmd = [edge_bin, f"--voice={voice}"]
    if output_vtt_path:
        cmd.append(f"--write-subtitles={output_vtt_path}")
    
    if os.path.isfile(text):
        cmd.append(f"--file={text}")
    else:
        cmd.append(f"--text={text}")
    cmd.append(f"--write-media={output_audio_path}")

    subprocess.run(cmd, check=True)
    return output_audio_path

def generate_speech_with_vtt(text, output_audio_path, output_vtt_path, voice_id=DEFAULT_VOICE, fallback=True):
    """Generate audio MP3 dan file WebVTT (.vtt) via ElevenLabs with-timestamps API"""
    api_key = get_api_key()
    if not api_key:
        if fallback:
            print("[!] API Key ElevenLabs tidak ada, fallback ke Edge-TTS...")
            return fallback_edge_tts(text, output_audio_path, output_vtt_path)
        raise ValueError("API Key ElevenLabs tidak ditemukan.")

    raw_text = text
    if os.path.isfile(text):
        with open(text, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": raw_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.2,
            "use_speaker_boost": True
        }
    }

    try:
        print(f"[*] [ElevenLabs] Generating audio & timestamps (Voice: {voice_id})...")
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        audio_bytes = base64.b64decode(data.get("audio_base64", ""))
        with open(output_audio_path, "wb") as f:
            f.write(audio_bytes)

        if "alignment" in data and output_vtt_path:
            vtt_content = alignment_to_vtt(data["alignment"], words_per_cue=4)
            with open(output_vtt_path, "w", encoding="utf-8") as f:
                f.write(vtt_content)

        print(f"[✓] [ElevenLabs] Berhasil generate: {output_audio_path}")
        return output_audio_path
    except Exception as e:
        print(f"[!] [ElevenLabs] Gagal generate: {e}")
        if fallback:
            print("[*] Mengalihkan otomatis ke Fallback Edge-TTS...")
            return fallback_edge_tts(text, output_audio_path, output_vtt_path)
        raise e

def generate_speech(text, output_audio_path, voice_id=DEFAULT_VOICE, fallback=True):
    """Generate audio MP3 standar (tanpa subtitle VTT terpisah)"""
    api_key = get_api_key()
    if not api_key:
        if fallback:
            return fallback_edge_tts(text, output_audio_path)
        raise ValueError("API Key ElevenLabs tidak ditemukan.")

    raw_text = text
    if os.path.isfile(text):
        with open(text, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": raw_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.2,
            "use_speaker_boost": True
        }
    }

    try:
        print(f"[*] [ElevenLabs] Generating audio (Voice: {voice_id})...")
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            audio_bytes = resp.read()
        with open(output_audio_path, "wb") as f:
            f.write(audio_bytes)
        print(f"[✓] [ElevenLabs] Audio tersimpan: {output_audio_path}")
        return output_audio_path
    except Exception as e:
        print(f"[!] [ElevenLabs] Gagal: {e}")
        if fallback:
            print("[*] Fallback ke Edge-TTS...")
            return fallback_edge_tts(text, output_audio_path)
        raise e

# Alias backward compatibility
synthesize = generate_speech

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan: python3 elevenlabs_engine.py \"Teks narasi\" [output.mp3] [voice_id]")
        sys.exit(1)

    text_input = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else "/root/assets/test_elevenlabs.mp3"
    v_id = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_VOICE

    res = generate_speech(text_input, out_file, voice_id=v_id)
    print(f"[✓] Audio berhasil disimpan: {res} ({os.path.getsize(res)} bytes)")
