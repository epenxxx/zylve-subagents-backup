---
name: settings
description: Lihat dan konfigurasi parameter sistem Antigravity CLI (~/.gemini/antigravity-cli/settings.json) layaknya perintah /settings atau /config di CLI.
---

# Skill: /settings (Antigravity System Settings)

Skill ini menyinkronkan akses konfigurasi preferensi sistem Antigravity dari CLI ke antarmuka chat.

## Alur Kerja Saat Perintah `/settings` Dipanggil:

1. **Baca settings.json**:
   - Tampilkan parameter penting: model default, artifactReviewPolicy, allowNonWorkspaceAccess, dan daftar customModels.

2. **Ubah Pengaturan Bila Diminta**:
   - Perbarui nilai konfigurasi sesuai permintaan pengguna secara aman.
