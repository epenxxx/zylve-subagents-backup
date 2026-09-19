---
name: generate-image
description: Prosedur standar (SOP) pembuatan dan penyajian gambar oleh Cimoy agar selalu lancar, sukses, dan langsung tampil di antarmuka chat, artifact, serta bot Telegram.
---

# SOP Generate Gambar (Cimoy)

## 1. Analisis & Formulasi Prompt
- **Rasio Aspek**: Sesuaikan permintaan pengguna (misal: 3:4 untuk storyboard/potret, 16:9 untuk wallpaper/sinematik, 1:1 untuk avatar).
- **Prompt Humanis & Detail**: Sertakan deskripsi ekspresi emosional manusiawi, tata cahaya volumetrik, tekstur bahan, dan sudut kamera sinematik.
- **Nama Berkas**: Maksimal 3 kata, huruf kecil dipisah garis bawah (contoh: `pixar_storyboard`).

## 2. Eksekusi Pembuatan Gambar & Teks
- **Engine Mutlak (Wajib 100%)**: HANYA menggunakan **Google Flow** (`flow.google.com`) atau **Gemini Web** (`gemini.google.com`).
- **Gambar Beserta Teks Natively AI**: Seluruh tipografi teks (judul, headline, badge, label fakta, watermark) WAJIB langsung ter-render di dalam gambar oleh AI Google Flow atau Gemini Web.
- **Dilarang Buat Teks di Luar Keduanya**: Dilarang keras menggunakan manipulasi teks eksternal (PIL/Pillow ImageDraw, HTML/CSS overlay screenshot, ImageMagick, dsb). Seluruh teks visual wajib menyatu dan dihasilkan murni dari prompt AI.

## 3. Sinkronisasi Berkas
- Segera salin berkas gambar ke direktori kerja utama pengguna:
  `cp <brain_image_path> /root/<nama_berkas>.jpg`
- Pastikan berkas memiliki izin baca normal (`chmod 644`).

## 4. Pembuatan Artifact Penampil
- Buat berkas artifact penampil di `<appDataDir>/brain/<conversation-id>/<nama_berkas>_preview.md`.
- Di dalam artifact, sematkan gambar dengan sintaks:
  `![Deskripsi](<brain_image_path>)`

## 5. Penyajian di Balasan Chat
- **Embed Gambar**: Wajib sertakan sintaks gambar dengan path brain yang valid agar dirender langsung oleh webview chat:
  `![Deskripsi](<brain_image_path>)`
- **Tautan Berkas**: Sertakan tautan berkas lokal yang bisa diklik:
  `[<nama_berkas>.jpg](file:///root/<nama_berkas>.jpg)`
- **Kirim Notifikasi**: Jalankan `notify-send "Cimoy" "Gambar <nama_berkas> berhasil dibuat"`.
- **Gaya Laporan**: Gunakan mode caveman Bahasa Indonesia yang ringkas dan langsung to the point.

## 6. Pengiriman Otomatis ke Telegram
- Wajib jalankan pengiriman foto via helper:
  `python3 /root/telegram_remote_bot/send_telegram.py /root/<nama_berkas>.jpg "<caption_menarik>"`
- Ini menjamin foto langsung masuk ke antarmuka chat Telegram pengguna.
