# ZYLVEmedia Subagents AI Ecosystem (Backup & Migrasi)

Repositori ini berisi cadangan lengkap seluruh arsitektur Subagent AI Cimoy / ZYLVEmedia, mencakup skill, alat orkestrasi, dan pedoman operasional otonom.

## 📁 Struktur Repositori
- `skills/`: Direktori skill subagen (`.agents/skills/`) lengkap (40+ persona & modul kerja).
- `tools/`: Kumpulan engine, router, uploader, dan orchestrator (`/root/tools/`).
- `master_docs/`: Dokumen aturan kerja dan ingatan (`AGENTS.md`, `memori.md`, `skill.md`, `GEMINI.md`, `CLAUDE.md`, `CIMOY_MASTER_SYSTEM.md`).
- `configs/`: Standar konfigurasi baku (`karaoke_golden_config.json`, `hooks.json`).
- `install.sh`: Script instalasi & migrasi 1-klik untuk server baru.

## 🚀 Cara Migrasi ke Server Baru
Di server target (Linux/Ubuntu/Debian), cukup jalankan:

```bash
# 1. Clone repositori ini
git clone https://github.com/epenxxx/zylve-subagents-backup.git /root/projects/zylve-subagents-backup

# 2. Masuk ke direktori dan jalankan installer 1-klik
cd /root/projects/zylve-subagents-backup
bash install.sh
```

Seluruh skill, tools, dan konfigurasi akan otomatis terpasang tepat pada jalurnya di `/root/`.
