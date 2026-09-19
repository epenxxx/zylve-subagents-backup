#!/bin/bash
# Guardian Watchdog untuk konfigurasi AGY & Bot Telegram
SETTINGS="/root/.gemini/antigravity-cli/settings.json"
BACKUP="/root/.gemini/antigravity-cli/settings.json.locked_master"

if [ -f "$BACKUP" ]; then
    chattr -i "$SETTINGS" 2>/dev/null
    if ! grep -q '"modelProvider": "gemini"' "$SETTINGS" 2>/dev/null; then
        cp -f "$BACKUP" "$SETTINGS"
        chmod 644 "$SETTINGS" 2>/dev/null
    fi
fi
