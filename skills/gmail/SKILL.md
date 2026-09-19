---
name: gmail
description: Lihat daftar akun Google (Gmail) yang tersimpan di pool dan beralih instan antar akun tanpa perlu logout saat kuota habis, layaknya perintah /gmail di Telegram dan CLI.
---

# Skill: /gmail (Gmail Multi-Account Switcher)

Skill ini mengelola pool sesi akun Google OAuth (`antigravity-oauth-token`) dan memungkinkan beralih seketika saat kuota habis tanpa harus logout.

## Lokasi Berkas:
- Pool Akun: `/root/.gemini/antigravity-cli/accounts/<email>.json`
- Token Aktif: `/root/.gemini/antigravity-cli/antigravity-oauth-token`
- Tool CLI: `/root/tools/gmail_switcher.py` (tersedia di PATH sebagai `gmail`)

## Cara Penggunaan:
1. **Daftar Akun**:
   ```bash
   gmail list
   ```
2. **Beralih Akun**:
   ```bash
   gmail switch <email>
   # contoh: gmail switch epenxcc@gmail.com
   ```
3. **Tambah Akun Baru ke Pool**:
   ```bash
   gmail add <email>
   # contoh: gmail add masepenx@gmail.com
   # Buka tautan Google OAuth yang muncul di browser, lalu login/otorisasi.
   # Jika remote: jalankan `gmail add <email> --code <auth_code>`
   ```
4. **Putar Akun (Rolling Next)**:
   ```bash
   gmail next
   # Otomatis beralih ke akun berikutnya secara round-robin di pool
   ```
5. **Di Bot Telegram**:
   Ketik perintah `/gmail`:
   - Tap tombol akun spesifik untuk switch manual.
   - Tap tombol `🔄 Putar Akun Sekarang (Rolling)` untuk rolling instan.


