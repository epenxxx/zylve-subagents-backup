---
name: status
description: Tampilkan status kesehatan sistem lengkap (resource CPU, RAM, Disk, background services bot Telegram, scheduled runner, dan pipeline) layaknya perintah /status atau /statusline di CLI.
---

# Skill: /status (System & Service Health Monitor)

Skill ini menyinkronkan fungsionalitas pemantauan status sistem dan layanan ke dalam chat.

## Alur Kerja Saat Perintah `/status` Dipanggil:

1. **Cek Resource Sistem**:
   - Penggunaan CPU, RAM (`free -h`), Disk (`df -h /`).
   - Suhu atau beban prosesor.

2. **Cek Layanan Aktif (Systemd & Cron)**:
   - `cimoy-bot.service` (Bot Telegram 1 @agyzyl_bot)
   - `cimoy-bot2.service` (Bot Telegram 2 @Laptopzyl_bot)
   - `scheduled_runner` / cron job ZYLVEmedia
   - Web server portal `zylvemedia.web.id`

3. **Tampilkan Ringkasan Singkat & Rapi**:
   - Berikan status hijau/merah indikator kesehatan sistem dalam format ringkas.
