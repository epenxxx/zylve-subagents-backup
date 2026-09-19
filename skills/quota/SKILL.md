---
name: quota
description: Cek sisa kuota, status rate limit, dan perkiraan waktu reset kuota model AI di Antigravity CLI layaknya perintah /quota di CLI.
---

# Skill: /quota (Antigravity Quota & Rate Limit Checker)

Skill ini menyinkronkan fungsionalitas perintah CLI `/quota` ke dalam antarmuka chat.

## Alur Kerja Saat Perintah `/quota` Dipanggil:

1. **Audit Riwayat & Log Limit**:
   - Periksa status kuota dari riwayat percakapan dan berkas `memori.md`.
   - Deteksi apakah ada model yang sedang terkena limit 429 atau kuota habis (misal kuota Gemini Pro / Flash High).

2. **Laporan Kuota**:
   - Tampilkan status ketersediaan model saat ini:
     - Model aktif (`settings.json`).
     - Alternatif bebas kuota (Gemini 3.8 Flash Medium/Low, Claude, GPT-OSS 120B, atau local proxy / 9router).
   - Berikan rekomendasi model terbaik jika model utama sedang exhausted/cooldown.
