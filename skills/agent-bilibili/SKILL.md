---
name: agent-bilibili
description: SOP Tim Agent Bilibili - Pengelolaan Akun Full-Stack, Akselerasi Syarat Monetisasi, Optimasi High-RPM Niche, Distribusi Cuan (Incentive Program & Afiliasi), dan Eksekusi VAAPI
---

# Tim Agent Bilibili (Pengelolaan Akun & Akselerasi Monetisasi)

Subagen & tim khusus yang mengelola akun Bilibili dari hulu ke hilir untuk menghasilkan cuan (revenue) nyata melalui Creator Incentive Program, Xuanshang Daihuo (afiliasi), Charging Program, dan ekspansi audiens loyal.

## 1. Roadmap Menuju Cuan Bilibili
1. **Fase 1: Tembus Syarat Monetisasi (Creation Incentive / 创作激励计划)**:
   - Target: Akun Level 4, 1.000 Followers, atau 100.000 akumulasi tayang.
   - Strategi: Push video retensi tinggi pada partisi Sains/Teknologi/Edukasi (科技/知识).
2. **Fase 2: Optimasi Revenue Per View (Nilai Koin & Sanlian)**:
   - Algoritma pembayaran Bilibili didasarkan pada bobot koin (投币) dan tonton penuh (*completion rate*), bukan sekadar klik mentah.
   - Formula: Hook 10s + Pemicu Danmaku di menit 2 + CTA Sanlian emosional di penutup.
3. **Fase 3: Multi-Stream Monetization**:
   - **Bilibili Charging (充电计划)**: Langganan konten eksklusif / donasi penggemar loyal.
   - **Afiliasi Produk (悬赏带货)**: Sisipkan link barang di komentar tersemat (*pinned comment*).
   - **Traffic Diversion**: Alirkan audiens ke ekosistem portal media & aset digital.

## 2. Standar Produksi Video Bernilai Cuan Tinggi
- **Niche Rekomendasi**: Fakta Dunia Tersembunyi, AI & Masa Depan, Analisis Teknologi, Musik/Budaya.
- **Rasio & Mutu**: 16:9 Full HD 1080p, render kilat hardware acceleration VAAPI (`/dev/dri/renderD128`).
- **Durasi Sweet Spot**: 3–8 menit (retensi koin tertinggi).
- **Bahasa & Voiceover**: Mandarin natural + Subtitle dinamis eye-tracking.
- **Packaging CTR**: Thumbnail 16:9 kontras tinggi (maksimal 6 karakter teks mencolok) + Judul psikologis rasa penasaran.

## 3. Jadwal Unggah Jam Emas (Peak Traffic China Standard Time - UTC+8 / WIB+1)
- **Slot Siang**: 11:30 - 12:30 WIB (Makan siang pekerja/mahasiswa).
- **Slot Malam (Prime Time Emas)**: 17:00 - 20:00 WIB (Puncak aktif Bilibili santai malam).

## 4. Eksekusi Otomasi
- **Analyzer Pra-Unggah**: `/root/tools/bilibili_video_analyzer.py`
- **Uploader Script**: `/root/zylve_automation/upload_to_bilibili.py`
- **Slot Runner**: `/root/zylve_automation/run_bilibili_slot.py`
- **Laporan & Bukti**: Notifikasi otomatis via `/root/telegram_remote_bot/send_telegram.py`.
