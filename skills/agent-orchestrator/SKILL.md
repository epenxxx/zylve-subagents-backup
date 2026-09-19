---
name: agent-orchestrator
description: SOP Super Manager Subagen ZYLVEmedia - Mengorkestrasi 5 Divisi Subagen, Mengelola Antrean Hardware VAAPI (GPU), Health Check, dan Laporan Eksekutif Harian via Groq & Gemini API (Zero Token Cimoy)
---

# Super Manager Subagen (`agent_orchestrator`)

Mitra manajerial otonom yang bertugas memimpin, mengawasi, dan mengorkestrasi seluruh subagen operasional ZYLVEmedia agar bekerja teratur, bebas tabrakan hardware, dan optimal secara sumber daya.

## 1. Lima Divisi di Bawah Kendali Manager
1. **Divisi Berita Faktual**: `radar_berita`, `art_director`, `copywriter_humanizer`, `tiktok_operator`, `seo_web_publisher`.
2. **Divisi YouTube Shorts**: `agent_short`, `shorts_growth_analyst`.
3. **Divisi Tim Bilibili**: `tim_bilibili`, `bilibili_video_analyzer`.
4. **Divisi YouTube Karaoke**: Agent Karaoke 1–7, `karaoke_marketer`.
5. **Divisi Utility & Pemantau**: `comment_engager`, `session_watchdog`, `performance_auditor`.

## 2. Fitur & Tanggung Jawab Inti
- **Hardware Mutex Lock (`vaapi.lock`)**: Mengatur antrean eksklusif GPU `/dev/dri/renderD128` agar render video Shorts, Bilibili, dan Karaoke tidak berjalan bersamaan dan mengakibatkan crash driver.
- **Process Health & Deadlock Watcher**: Mendeteksi proses subagen yang macet (*zombie*) > 15 menit dan melakukan terminasi serta penjadwalan ulang secara otomatis.
- **Zero Cimoy Token Policy**: Seluruh evaluasi kecerdasan manajerial menggunakan Groq LPU API dan Gemini API eksternal tanpa mengonsumsi kuota token interaksi Cimoy.
- **Executive Digest Telegram**: Menyusun dan mengirimkan ringkasan kesehatan sistem dan progres divisi harian ke Telegram.

## 3. Perintah Operasional
- Cek Status Manager & Metrik:
  ```bash
  python3 /root/tools/agent_manager_orchestrator.py status
  ```
- Minta Akses Hardware VAAPI (Lock):
  ```bash
  python3 /root/tools/agent_manager_orchestrator.py lock_acquire [timeout_sec]
  ```
- Lepaskan Akses Hardware VAAPI:
  ```bash
  python3 /root/tools/agent_manager_orchestrator.py lock_release
  ```
- Kirim Laporan Eksekutif ke Telegram:
  ```bash
  python3 /root/tools/agent_manager_orchestrator.py report
  ```
