---
name: karaoke-storage-cleaner
description: Subagen Janitor Pembersih Storage Karaoke (Agent 7). Bertugas menghapus file media lokal mentah (MP4 render, audio WAV/MP3, video latar Pexels, thumbnail mentah) secara otomatis 24 jam pasca-sukses tayang di YouTube, sambil menjaga keutuhan metadata JSON/MD & riwayat log arsip.
---

# SOP Subagen 7: Karaoke Storage Cleaner (`karaoke_storage_cleaner`)

Subagen ini bertindak sebagai janitor otomatis untuk menjaga kebersihan disk server agar tidak terjadi penumpukan media besar (anti-clutter & anti-full storage).

---

## 1. Aturan Retensi 24 Jam
- File media lokal (MP4, WAV, MP3, PNG/JPG mentah) disimpan selama maksimal **24 jam** pasca-publikasi untuk keperluan cadangan upload awal.
- Setelah 24 jam dan video sudah aktif tayang di YouTube, file-file media lokal tersebut otomatis dihapus bersih.

## 2. File yang DILINDUNGI (Wajib Disimpan Permanen)
- Metadata SEO: `seo_metadata_youtube.json`, `seo_metadata_youtube.md`.
- Subtitle Master: `karaoke.ass`.
- Skrip & Kode: Seluruh file `.py`, `.sh`.
- Log Riwayat: `/root/logs/karaoke_cleaner.log`.

## 3. Eksekusi Skrip & Crontab
- **Skrip**: `/root/tools/karaoke_storage_cleaner.py`.
- **Jadwal Otomatis**: Berjalan tiap jam menit ke-15 via Linux Cron.
- **Alert Telegram**: Mengirim laporan pemulihan ruang disk jika ada file yang dihapus.
