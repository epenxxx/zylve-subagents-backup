---
name: switch
description: Ganti konteks fokus kerja proyek, alihkan workspace, atau alihkan sesi conversation layaknya perintah /switch di Antigravity CLI.
---

# Skill: /switch (Workspace & Project Switcher)

Skill ini menyinkronkan fungsionalitas pergantian konteks proyek dari CLI `/switch`.

## Alur Kerja Saat Perintah `/switch` Dipanggil:

1. **Daftar Proyek Aktif**:
   - Tampilkan proyek yang ada di `/root/projects/` (Karaoke, Masalembo, Affiliate, IKN, dll).

2. **Alihkan Fokus**:
   - Jika pengguna menentukan proyek (misal `/switch karaoke` atau `/switch affiliate`), baca konteks folder tersebut dan fokuskan eksekusi pada proyek yang dipilih.
