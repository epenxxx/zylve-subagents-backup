#!/usr/bin/env bash
# ==============================================================================
# Script Migrasi & Restore Ekosistem Subagent AI Cimoy / ZYLVEmedia
# Jalankan script ini di server baru untuk instalasi 1-klik instan!
# ==============================================================================

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_ROOT="/root"

echo "=================================================================="
echo "🚀 MEMULAI MIGRASI SUBAGENT AI ZYLVEmedia KE SERVER BARU..."
echo "=================================================================="

# 1. Pastikan direktori target ada
echo "[1/6] Menyiapkan struktur direktori..."
mkdir -p "$TARGET_ROOT/.agents/skills"
mkdir -p "$TARGET_ROOT/tools"
mkdir -p "$TARGET_ROOT/assets"
mkdir -p "$TARGET_ROOT/zylve_automation"
mkdir -p "$TARGET_ROOT/screenshots"
mkdir -p "$TARGET_ROOT/projects"

# 2. Restore Subagent Skills
echo "[2/6] Memulihkan seluruh Skill Subagent ke $TARGET_ROOT/.agents/skills/..."
cp -rL "$BASE_DIR/skills/"* "$TARGET_ROOT/.agents/skills/"

# Sinkronkan juga ke ~/.gemini/config/skills jika ada
if [ -d "$TARGET_ROOT/.gemini/config/skills" ]; then
    cp -rL "$BASE_DIR/skills/"* "$TARGET_ROOT/.gemini/config/skills/" 2>/dev/null || true
fi

# 3. Restore Tools & Orchestrators
echo "[3/6] Memulihkan Tools & Orchestrator ke $TARGET_ROOT/tools/..."
cp -r "$BASE_DIR/tools/"* "$TARGET_ROOT/tools/"
chmod +x "$TARGET_ROOT/tools/"*.sh 2>/dev/null || true
chmod +x "$TARGET_ROOT/tools/"*.py 2>/dev/null || true
chmod +x "$TARGET_ROOT/tools/agy-m" "$TARGET_ROOT/tools/agyx" 2>/dev/null || true

# 4. Restore Master Docs & Panduan
echo "[4/6] Memulihkan Master Docs (AGENTS.md, memori.md, skill.md)..."
cp "$BASE_DIR/master_docs/AGENTS.md" "$TARGET_ROOT/AGENTS.md" 2>/dev/null || true
cp "$BASE_DIR/master_docs/memori.md" "$TARGET_ROOT/memori.md" 2>/dev/null || true
cp "$BASE_DIR/master_docs/skill.md" "$TARGET_ROOT/skill.md" 2>/dev/null || true
cp "$BASE_DIR/master_docs/GEMINI.md" "$TARGET_ROOT/GEMINI.md" 2>/dev/null || true
cp "$BASE_DIR/master_docs/CLAUDE.md" "$TARGET_ROOT/CLAUDE.md" 2>/dev/null || true
if [ -f "$BASE_DIR/master_docs/CIMOY_MASTER_SYSTEM.md" ]; then
    cp "$BASE_DIR/master_docs/CIMOY_MASTER_SYSTEM.md" "$TARGET_ROOT/zylve_automation/CIMOY_MASTER_SYSTEM.md" 2>/dev/null || true
fi

# 5. Restore Configs & Hooks
echo "[5/6] Memulihkan Konfigurasi Emas & Hooks..."
if [ -f "$BASE_DIR/configs/karaoke_golden_config.json" ]; then
    cp "$BASE_DIR/configs/karaoke_golden_config.json" "$TARGET_ROOT/assets/karaoke_golden_config.json"
fi
if [ -f "$BASE_DIR/configs/hooks.json" ]; then
    cp "$BASE_DIR/configs/hooks.json" "$TARGET_ROOT/.agents/hooks.json"
fi

# 6. Uji Coba Status Subagent Manager
echo "[6/6] Memverifikasi Super Manager Subagent..."
if [ -f "$TARGET_ROOT/tools/agent_manager_orchestrator.py" ]; then
    python3 "$TARGET_ROOT/tools/agent_manager_orchestrator.py" status || true
fi

echo "=================================================================="
echo "✅ MIGRASI SELESAI! Seluruh subagent & tools siap beroperasi penuh."
echo "=================================================================="
EOF
chmod +x /root/projects/zylve-subagents-backup/install.sh
