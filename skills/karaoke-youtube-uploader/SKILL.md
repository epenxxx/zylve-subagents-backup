---
name: karaoke-youtube-uploader
description: Subagen Eksekutor Upload & Publikasi YouTube Karaoke (Agent 6). Bertugas mengunggah video karaoke 16:9 Full HD, memasang thumbnail kustom Google Flow 16:9, menyematkan metadata SEO (Judul, Deskripsi, Kategori Musik 10, Tags), dan memverifikasi status tayang publik via YouTube Data API v3 resmi.
---

# SOP Subagen 6: YouTube Karaoke Uploader & Publisher (`karaoke_youtube_uploader`)

Subagen ini merupakan pilar ke-6 (eksekutor final) dalam pipeline karaoke otomatis. Bertugas mengunggah dan mempublikasikan karya video karaoke secara resmi ke kanal YouTube target.

---

## 1. Spesifikasi Teknis Upload
- **Engine**: YouTube Data API v3 resmi (`/root/zylve_automation/youtube_token.json`).
- **Python Environment**: `/opt/mikrotik-tools/venv/bin/python3` (library `google-api-python-client` & `google-auth`).
- **Parameter Video**:
  - File: MP4 16:9 Full HD 1080p (`video_karaoke_<judul>_16x9.mp4`).
  - Kategori: `10` (Music).
  - Status Privasi: `public`.
  - Custom Thumbnail: Format 16:9 PNG (`thumbnail_youtube_karaoke_<judul>_16x9.png`) via endpoint `thumbnails().set()`.
- **Integrasi Notifikasi**: Mengirim tautan video YouTube resmi yang berhasil tayang ke bot Telegram dan notifikasi sistem (`notify-send`).
