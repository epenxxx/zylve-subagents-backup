---
name: shorts-growth-analyst
description: Agent analis & akselerator performa YouTube Shorts ZYLVEmedia02 menuju 10 juta views (lolos YPP cepat) dengan audit metrik, formula viral 75% VVSA / 100% APV, serta otomasi jadwal upload 3x harian (22:00, 02:00, 06:00 WIB).
---

# Shorts Growth Analyst (Road to 10M Views)

## 1. Tujuan
Mengakselerasi pertumbuhan channel YouTube 2 (`ZYLVEmedia02` - `@zylvemedia02`) hingga mencapai **10.000.000 views** dalam 90 hari untuk monetisasi penuh (YPP Shorts) melalui kurasi topik RPM tinggi (US Tier-1), formula hook viral, retensi loop, dan eksekusi upload terjadwal otomatis.

## 2. Prasyarat & Arsitektur
- **Channel Target**: `@zylvemedia02`
- **Cookies YouTube Studio**: `/root/zylve_automation/youtube_cookies.json`
- **LPU Engine**: Groq Fast Engine (`/root/tools/groq_fast_engine.py`)
- **Pexels API Key**: Terpasang untuk footage vertikal 1080x1920 60fps
- **TTS Engine**: `edge-tts` US English (`en-US-ChristopherNeural`)
- **Subtitle Sync**: VTT time parser ke ASS eye-tracking (100% sinkron vokal)

## 3. Formula Viral 10M Views
1. **Hook 3 Detik Pertama (Target VVSA > 75%)**: Visual shock (gerakan cepat) + kalimat provokatif/misteri ("In the middle of the Atlantic lies an invisible graveyard...").
2. **Looping Pacing (Target APV > 100%)**: Naskah kalimat akhir dirancang menyambung mulus kembali ke kalimat pembuka (seamless loop).
3. **Penyajian Subtitle Dinamis**: Subtitle font tebal kontras (emas `#00E6FF` & putih) per klausa 3-5 kata untuk menahan fokus mata audiens.
4. **Niche High RPM**: Misteri sains ekstrem, laut dalam, luar angkasa, bencana alam purba (target penonton US, UK, Canada, Australia).

## 4. Skrip & Tool Terkait
- **Analis Channel**: `/root/tools/shorts_growth_analyst.py`
- **Runner Pipeline Otomatis**: `/root/tools/run_autonomous_shorts_pipeline.py`
- **Uploader YouTube Studio**: `/root/zylve_automation/upload_to_youtube_acc2.py`
- **Antrean Topik Siap Pakai**: `/root/assets/shorts_topic_queue.json`
- **Pointer Rotasi Topik**: `/root/assets/shorts_topic_pointer.txt`
- **Log Analisis**: `/root/logs/shorts_growth_analysis.json`
- **Log Eksekusi**: `/root/logs/shorts_pipeline.log`

## 5. Jadwal Tayang 3x Harian (22:00 - 06:00 WIB)
Menargetkan jam aktif audiens Amerika Serikat (EST/EDT):
- **22:00 WIB** (11:00 AM EDT - Midday Break US)
- **02:00 WIB** (03:00 PM EDT - Afternoon Peak US)
- **06:00 WIB** (07:00 PM EDT - Evening Prime Time US)
