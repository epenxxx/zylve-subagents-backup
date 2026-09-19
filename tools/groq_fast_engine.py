#!/usr/bin/env python3
"""
groq_fast_engine.py
Engine Khusus Kecepatan Tinggi Berbasis Groq LPU untuk Subagen ZYLVEmedia:
1. SEO & Metadata Kilat (Agent 5 Karaoke & Berita)
2. Filter & Skoring Berita Viral (Agent 0 & Radar Berita)
3. Transkripsi Audio Kilat via Whisper Large V3 (Agent 1 Karaoke)
"""

import sys
import os
import json
import urllib.request
import urllib.error

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

def fast_chat(prompt: str, system_prompt: str = "Jawab ringkas, padat, to the point dalam Bahasa Indonesia.", model: str = "qwen/qwen3.8-27b", max_tokens: int = 512) -> str:
    """Kirim chat completions cepat ke Groq."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.6
    }
    req = urllib.request.Request(
        CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "CimoyGroqEngine/1.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[GROQ ERROR] {e}"

def generate_karaoke_seo(artist: str, song_title: str, genre: str = "Pop/Slow Rock") -> dict:
    """Agent 5: Bikin paket judul, hashtag, dan tags YouTube CTR tinggi dalam sekejap."""
    system_prompt = (
        "Kamu adalah Spesialis SEO YouTube Musik & Karaoke profesional ZYLVEmedia. "
        "Buat paket SEO ramah penonton, anti-AI-slop, mengundang klik penonton karaoke. "
        "Output WAJIB format JSON valid dengan keys: 'titles' (array 3 judul), 'tags' (string koma), 'hashtags' (string spasi)."
    )
    prompt = (
        f"Lagu: {song_title}\n"
        f"Penyanyi: {artist}\n"
        f"Genre: {genre}\n"
        "Format judul harus memuat kata KARAOKE, LIRIK, NADA PAS, dan brand ZYLVEmedia."
    )
    raw = fast_chat(prompt, system_prompt=system_prompt, max_tokens=400)
    # Ekstrak JSON
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except Exception:
        pass
    return {"raw_output": raw}

def score_viral_news(headline: str, snippet: str = "") -> dict:
    """Agent 0: Skoring berita viral kilat (1-100)."""
    system_prompt = (
        "Kamu adalah Kurator Intelijen Berita Viral ZYLVEmedia. "
        "Nilai potensi viralitas, emosi publik, dan kelayakan berita jadi poster 1 slide. "
        "Output WAJIB JSON valid: {'score': int 1-100, 'verdict': 'LAYAK'/'TOLAK', 'core_hook': '1 kalimat emosional', 'suggested_category': 'Hukum/Politik/Hiburan/Sosial'}."
    )
    prompt = f"Judul Berita: {headline}\nKonteks: {snippet}"
    raw = fast_chat(prompt, system_prompt=system_prompt, max_tokens=250)
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except Exception:
        pass
    return {"raw_output": raw}

def transcribe_audio_whisper(audio_path: str) -> str:
    """Agent 1: Transkripsi file audio kilat menggunakan Whisper Large v3."""
    if not os.path.exists(audio_path):
        return f"[ERROR] File {audio_path} tidak ditemukan."
        
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    data = []
    
    # Model param
    data.append(f"--{boundary}".encode("utf-8"))
    data.append(b'Content-Disposition: form-data; name="model"\r\n')
    data.append(b"whisper-large-v3\r\n")
    
    # File param
    filename = os.path.basename(audio_path)
    data.append(f"--{boundary}".encode("utf-8"))
    data.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    data.append(b"Content-Type: audio/mpeg\r\n\r\n")
    with open(audio_path, "rb") as f:
        data.append(f.read())
    data.append(b"\r\n")
    
    # End
    data.append(f"--{boundary}--\r\n".encode("utf-8"))
    payload = b"".join(data)
    
    req = urllib.request.Request(
        AUDIO_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "CimoyGroqEngine/1.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res.get("text", "")
    except Exception as e:
        return f"[WHISPER ERROR] {e}"

if __name__ == "__main__":
    print("=== TEST GROQ FAST ENGINE ===")
    print("\n1. Test Fast SEO (Karaoke):")
    seo = generate_karaoke_seo("Exists", "Mencari Alasan", "Slow Rock 90s")
    print(json.dumps(seo, indent=2, ensure_ascii=False))
    
    print("\n2. Test Skoring Berita Viral:")
    score = score_viral_news("KPK Dalami 2 Mobil Mewah Pemberian Pengusaha ke Adik Pejabat", "Penyidik KPK memeriksa saksi terkait dugaan gratifikasi.")
    print(json.dumps(score, indent=2, ensure_ascii=False))
