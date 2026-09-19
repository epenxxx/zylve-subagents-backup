---
name: model
description: Lihat model AI yang aktif, daftar model yang tersedia di Antigravity CLI & custom models, atau ganti model aktif langsung dari chat layaknya perintah /model di CLI.
---

# Skill: /model (AI Model Selector & Switcher)

Skill ini menyinkronkan fungsionalitas perintah CLI `/model` ke dalam antarmuka chat.

## Alur Kerja Saat Perintah `/model` Dipanggil:

1. **Cek Model Aktif**:
   - Baca berkas `/root/.gemini/antigravity-cli/settings.json` pada properti `"model"`.
   - Identifikasi model yang sedang aktif saat ini.

2. **Daftar Model Resmi & Custom**:
   - **Model Resmi CLI (`agy models`)**:
     - `gemini-3.8-flash-high`: Gemini 3.8 Flash (High)
     - `gemini-3.8-flash-medium`: Gemini 3.8 Flash (Medium)
     - `gemini-3.8-flash-low`: Gemini 3.8 Flash (Low)
     - `gemini-3.7-flash-high`: Gemini 3.7 Flash (High)
     - `gemini-3.7-flash-medium`: Gemini 3.7 Flash (Medium)
     - `gemini-3.7-flash-low`: Gemini 3.7 Flash (Low)
     - `gemini-3.6-flash-high`: Gemini 3.6 Flash (High)
     - `gemini-3.6-flash-medium`: Gemini 3.6 Flash (Medium)
     - `gemini-3.6-flash-low`: Gemini 3.6 Flash (Low)
     - `gemini-3.1-pro-high`: Gemini 3.1 Pro (High)
     - `gemini-3.1-pro-low`: Gemini 3.1 Pro (Low)
     - `claude-sonnet-4-6`: Claude Sonnet 4.6 (Thinking)
     - `claude-opus-4-6-thinking`: Claude Opus 4.6 (Thinking)
     - `gpt-oss-120b-medium`: GPT-OSS 120B (Medium)
   - **Model Custom Proxy**:
     - `FREE` (Local Proxy Port 8128)
     - `Gemini` (9router/Gemini)

3. **Ganti Model (Bila Diberikan Argumen atau Diminta User)**:
   - Jika pengguna mengetik nama model (misal `/model gemini-3.8-flash-high` atau `/model claude-sonnet-4-6`), perbarui properti `"model"` di `/root/.gemini/antigravity-cli/settings.json`.
   - Kirim notifikasi sistem: `notify-send "Antigravity Model" "Model dialihkan ke <nama_model>"`.
   - Tampilkan konfirmasi sukses kepada pengguna.
   - Jika tanpa argumen, sajikan tombol interaktif (`ask_question`) agar pengguna bisa memilih model dengan sekali klik.
