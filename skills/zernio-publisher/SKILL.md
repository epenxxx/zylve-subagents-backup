---
name: zernio-publisher
description: SOP Publikasi & Penjadwalan Konten Otomatis ke TikTok (@zylve70) dan 16 Platform Media Sosial via Zernio API resmi (Zero Captcha, Zero IP Block).
---

# Zernio Publisher SOP

## 1. Tujuan
Menjadwalkan dan menerbitkan video/foto/konten ke akun media sosial resmi ZYLVEmedia secara otomatis lewat Zernio API tanpa ketergantungan pada browser automation (Playwright) yang rentan terhadap captcha dan shadowban.

## 2. Kredensial & Konfigurasi
- **API Key**: `/root/.config/zernio/api_key` (`ZERNIO_API_KEY`)
- **Base URL**: `https://zernio.com/api/v1`
- **Profil Default**: `6aae7d456c7bf2f6c6904baa` (Default)
- **Akun TikTok ZYLVEmedia**:
  - `accountId`: `6aae7e918d284ffb211b417d`
  - `username`: `zylve70`
  - `displayName`: `ZYLVEmedia`
  - `status`: `active`

## 3. Modul Klien Python
File: `/root/tools/zernio_client.py`

### Cara Penggunaan:
```python
from zernio_client import ZernioClient

client = ZernioClient()

# 1. Posting Video ke TikTok Sekarang
result = client.post_tiktok_video(
    video_path="/root/projects/.../video.mp4",
    caption="Review Berita Terkini #beritaviral #zylvemedia",
    publish_now=True
)
print("Hasil post:", result)

# 2. Cek Status Post
post_id = result["post"]["_id"]
status = client.get_post(post_id)
print("Status post:", status)
```

# 3. Cek Analytics Akun (Zero Scraping)
analytics = client.get_analytics()
print("Overview:", analytics.get("overview"))

## 4. Penanganan Error & Idempotensi
- **Error 409 (Conflict)**: Muncul jika konten yang sama persis diposting dalam 24 jam terakhir. Ubah sedikit caption atau sertakan header `x-request-id`.
- **Media Format**: Hanya gunakan format yang didukung (`video/mp4`, `image/jpeg`, `image/png`, `image/webp`).
- **Live URL**: Setelah terbit, link tayang tersimpan di field `platforms[].platformPostUrl`.

## 5. Platform yang Didukung
- TikTok (`tiktok`) — Aktif: `@zylve70`
- YouTube (`youtube`)
- Facebook (`facebook`)
- Instagram (`instagram`)
- X / Twitter (`twitter`)
- LinkedIn (`linkedin`)
- Pinterest, Bluesky, Telegram, dll.
