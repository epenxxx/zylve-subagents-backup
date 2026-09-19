---
name: stop
description: Hentikan seketika proses latar belakang (background tasks), subagen berjalan, atau proses komputasi aktif di sistem layaknya perintah /stop di CLI.
---

# Skill: /stop (Process & Task Termination)

Skill ini menangani penghentian proses, eksekusi latar belakang, atau subagen yang sedang berjalan secara seketika dan aman ketika pengguna memberikan instruksi `/stop`, "stop", "hentikan", "batal", atau "kill process".

## Prosedur Operasional Standar (SOP) Eksekusi /stop:

1. **Audit & Hentikan Background Tasks (CLI / Agent Tasks)**:
   - Jalankan pengecekan task yang sedang berjalan via tool `manage_task` dengan action `'list'`.
   - Untuk setiap task ID yang berstatus `running` atau `waiting`, eksekusi `manage_task` dengan action `'kill'`.

2. **Audit & Hentikan Subagent Aktif**:
   - Periksa subagent aktif via tool `manage_subagents` dengan action `'list'`.
   - Hentikan seluruh subagent yang masih berjalan dengan action `'kill_all'`.

3. **Audit & Bersihkan Proses Orphan / Hung di Sistem (Jika Diminta)**:
   - Jika pengguna secara spesifik meminta penghentian proses rendering video (`ffmpeg`), crawling browser (`playwright`/`chrome`), ekstraksi audio, atau skrip yang menggantung, identifikasi PID secara spesifik lalu kirimkan sinyal terminasi (`kill` / `pkill -f`) secara presisi tanpa mematikan core daemon sistem.

4. **Konfirmasi & Status**:
   - Laporkan hasil tindakan penghentian kepada pengguna secara singkat, padat, dan jelas (mode caveman).
   - Pastikan lingkungan kerja kembali dalam kondisi stabil dan siap menerima instruksi selanjutnya.
