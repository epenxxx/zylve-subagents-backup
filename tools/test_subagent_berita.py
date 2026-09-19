#!/usr/bin/env python3
"""
test_subagent_berita.py
Uji coba kolaborasi Tim Subagen Berita ZYLVEmedia:
1. Radar Berita (Fetch RSS media kredibel)
2. Fast Classifier Groq (Skoring viralitas & filter instan <0.5s)
3. Gemini CoT Subagent Engine (Analisis mendalam, hook 1 slide, 3 poin faktual)
"""

import os
import sys
import json
import urllib.request
import xml.etree.ElementTree as ET
import re

# Import engine lokal kita
from groq_fast_engine import score_viral_news
from gemini_subagent_engine import generate_subagent_response

def run_test():
    print("=== [1. RADAR BERITA: PENCARIAN BERITA TERKINI] ===")
    feeds = [
        ('CNN Indonesia', 'https://www.cnnindonesia.com/nasional/rss'),
        ('Detikcom', 'https://news.detik.com/rss'),
        ('Tempo', 'https://rss.tempo.co/nasional'),
        ('CNBC Indonesia', 'https://www.cnbcindonesia.com/news/rss')
    ]
    
    top_news = []
    for source, url in feeds:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                root = ET.fromstring(resp.read())
                for item in root.findall('.//item')[:2]:
                    title = item.find('title').text.strip() if item.find('title') is not None else ''
                    desc = item.find('description').text if item.find('description') is not None else ''
                    clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
                    if title:
                        top_news.append({'source': source, 'title': title, 'desc': clean_desc})
        except Exception as e:
            print(f"[-] RSS {source} timeout: {e}")

    if not top_news:
        print("[!] Gagal mengambil berita.")
        return

    print(f"[✓] Berhasil menjaring {len(top_news)} berita hangat.")
    
    print("\n=== [2. GROQ FAST ENGINE: SKORING & FILTER VIRAL (<0.5 DETIK)] ===")
    scored_news = []
    for n in top_news[:4]:
        res = score_viral_news(n['title'], n['desc'])
        score = res.get('score', 50)
        verdict = res.get('verdict', 'REVIEW')
        hook = res.get('core_hook', '')
        scored_news.append({**n, 'score': score, 'verdict': verdict, 'hook': hook})
        print(f"- [{verdict} | Skor: {score}] {n['title']} ({n['source']})")

    # Ambil skor tertinggi
    scored_news.sort(key=lambda x: x['score'], reverse=True)
    best_news = scored_news[0]
    print(f"\n[★] Topik Terpilih: '{best_news['title']}' (Skor: {best_news['score']})")

    print("\n=== [3. GEMINI REASONING SUBAGENT: ANALISIS STORYBOARD 1 SLIDE] ===")
    system_prompt = (
        "Kamu adalah Subagen Analis Berita & Copywriter Senior ZYLVEmedia. "
        "Gunakan penalaran mendalam (Chain-of-Thought). Rancang paket berita 1 Slide Poster Fotorealistis rasio 3:4. "
        "Format Output:\n"
        "1. HEADLINE HOOK (Semua Huruf Kapital, Emosional, Menohok)\n"
        "2. CALLOUT BALON KATA (1 Kalimat respon publik/pertanyaan menohok)\n"
        "3. 3 POIN KUNCI FAKTUAL (Singkat, padat, berbobot data angka/pernyataan resmi)\n"
        "4. REKOMENDASI VISUAL FOTOREALISTIS (Kamera Hasselblad, pencahayaan dramatis, tokoh/objek riil)"
    )
    prompt = (
        f"Judul Berita: {best_news['title']}\n"
        f"Sumber: {best_news['source']}\n"
        f"Konteks: {best_news['desc']}"
    )
    
    analysis = generate_subagent_response(prompt, system_prompt=system_prompt, thinking_budget=2048)
    if analysis['success']:
        print(f"[Engine: {analysis['model_used']}]")
        print(analysis['text'])
    else:
        print(f"[!] Gemini Subagent Gagal: {analysis.get('error')}")

if __name__ == '__main__':
    run_test()
