---
name: effort
description: Lihat atau atur tingkat pemikiran (reasoning effort: low, medium, high) untuk model AI layaknya perintah /effort di Antigravity CLI.
---

# Skill: /effort (Reasoning Effort Controller)

Skill ini menyinkronkan fungsionalitas perintah CLI `/effort` ke dalam antarmuka chat.

## Alur Kerja Saat Perintah `/effort` Dipanggil:

1. **Cek Effort Saat Ini**:
   - Cek konfigurasi effort aktif dari nama model (akhiran `-low`, `-medium`, `-high`) atau flag sesi.

2. **Atur Effort Baru**:
   - Pilihan effort:
     - `low`: Respons cepat, hemat token, penalaran ringkas.
     - `medium`: Keseimbangan optimal antara kecepatan dan kedalaman pemikiran.
     - `high`: Pemikiran mendalam multi-langkah (deep reasoning / chain of thought).
   - Jika pengguna menentukan tingkat effort (misal `/effort high` atau `/effort low`), sesuaikan model varian di `settings.json` yang sesuai.
