#!/usr/bin/env bash
# ==============================================================================
# Auto Backup Subagents AI ZYLVEmedia ke GitHub
# ==============================================================================

BACKUP_DIR="/root/projects/zylve-subagents-backup"
TARGET_REPO="https://github.com/epenxxx/zylve-subagents-backup.git"

echo "[1/4] Menyinkronkan file subagent & tools ke direktori backup..."
mkdir -p "$BACKUP_DIR/skills" "$BACKUP_DIR/tools" "$BACKUP_DIR/master_docs" "$BACKUP_DIR/configs"

# Sync skills
cp -rL /root/.agents/skills/* "$BACKUP_DIR/skills/" 2>/dev/null || true

# Sync tools
rsync -a --delete --exclude='__pycache__' --exclude='*.pyc' --exclude='*.log' /root/tools/ "$BACKUP_DIR/tools/"

# Sync master docs
cp /root/AGENTS.md /root/memori.md /root/skill.md /root/GEMINI.md /root/CLAUDE.md "$BACKUP_DIR/master_docs/" 2>/dev/null || true
cp /root/zylve_automation/CIMOY_MASTER_SYSTEM.md "$BACKUP_DIR/master_docs/" 2>/dev/null || true

# Sync configs
cp /root/assets/karaoke_golden_config.json "$BACKUP_DIR/configs/" 2>/dev/null || true
cp /root/.agents/hooks.json "$BACKUP_DIR/configs/" 2>/dev/null || true

echo "[2/4] Memeriksa status Git repositori..."
cd "$BACKUP_DIR"

if [ ! -d ".git" ]; then
    git init -b main
    git remote add origin "$TARGET_REPO" 2>/dev/null || git remote set-url origin "$TARGET_REPO"
fi

git config user.name "epenxxx"
git config user.email "epenxxx@users.noreply.github.com"

echo "[3/4] Melakukan staging dan commit perubahan..."
git add .

if git diff --staged --quiet; then
    echo "[✓] Tidak ada perubahan baru. Repositori backup sudah mutakhir."
else
    NOW=$(date "+%Y-%m-%d %H:%M:%S WIB")
    git commit -m "Auto backup subagents & tools: $NOW"
    echo "[✓] Commit berhasil dibuat: $NOW"
fi

echo "[4/4] Mengirim (push) ke GitHub..."
# Ambil token dari gh jika tersedia
if command -v gh >/dev/null 2>&1; then
    GH_TOKEN=$(gh auth token 2>/dev/null || true)
    if [ -n "$GH_TOKEN" ]; then
        PUSH_URL="https://epenxxx:${GH_TOKEN}@github.com/epenxxx/zylve-subagents-backup.git"
    else
        PUSH_URL="origin"
    fi
else
    PUSH_URL="origin"
fi

if git push -u "$PUSH_URL" main; then
    echo "=================================================================="
    echo "✅ SUKSES: Backup subagent berhasil dipush ke GitHub ($TARGET_REPO)!"
    echo "=================================================================="
else
    echo "=================================================================="
    echo "⚠️ PUSH DITUNDA: Remote repositori belum dibuat di GitHub atau perlu izin akses."
    echo "👉 Silakan buat repositori kosong 'zylve-subagents-backup' di akun GitHub @epenxxx."
    echo "=================================================================="
fi
