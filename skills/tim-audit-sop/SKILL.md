---
name: tim-audit-sop
description: SOP Tim Audit, Kepatuhan & Quality Control (Di Bawah Manager agent_orchestrator) - Mengawasi Kepatuhan Protokol AGENTS.md, Verifikasi Zero Cimoy Token, Audit Mutu Konten Pra-Rilis, dan Penegakan Single-Gate Reporting
---

# Tim Audit SOP & Kepatuhan (`tim_audit_sop`)

Divisi pengawas mutu dan kepatuhan sistem yang berada langsung di bawah komando **`agent_orchestrator`** (Manager). Bertugas menjamin seluruh subagen bekerja sesuai SOP resmi, tidak melanggar batasan sumber daya, dan bebas dari penyimpangan operasional.

## 1. Subagen dalam Tim Audit SOP
1. **`sop_compliance_auditor`** (Ketua Tim):
   - Memastikan aturan protokol AGENTS.md, memori.md, dan skill.md dipatuhi 100%.
   - Menegakkan *Zero Cimoy Token Policy* (hanya Groq LPU API dan Gemini API eksternal yang diizinkan untuk otomasi internal).
2. **`quality_gate_inspector`** (Inspektur Mutu):
   - Audit teknis pra-rilis (*Pre-Flight QC*): rasio video (16:9 / 9:16), keselarasan subtitle hardsub, normalisasi audio EBU R128 (-14 LUFS), dan cover infografis 3:4 bebas distorsi.
3. **`workflow_drift_detector`** (Pendeteksi Deviasi Alur Kerja):
   - Memastikan *Single-Gate Reporting* tetap terkunci (tidak ada subagen yang membocorkan chat langsung ke Telegram).
   - Memantau hardware lock VAAPI (`/tmp/vaapi.lock`) agar tidak terjadi tabrakan render antar subagen.

## 2. Parameter Inspeksi Baku
- **Token Rule**: 0% konsumsi token antarmuka Cimoy.
- **Reporting Gate**: Seluruh notifikasi wajib disaring via `send_telegram.py` buffer ke Manager.
- **Hardware Acceleration**: Encoding video wajib memanfaatkan AMD VAAPI (`h264_vaapi`).
- **Integritas Master Dokumen**: AGENTS.md, memori.md, dan skill.md wajib sinkron.

## 3. Eksekusi Perintah Audit
Jalankan inspeksi audit otomatis:
```bash
python3 /root/tools/sop_audit_inspector.py
```
Output berupa status `PASS`, `WARN`, atau `FAIL` yang langsung dilaporkan ke Manajer.
