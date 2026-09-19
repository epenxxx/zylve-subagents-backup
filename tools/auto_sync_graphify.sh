#!/bin/bash
# auto_sync_graphify.sh - Auto-sync graphify AST tanpa blocking & anti-tabrakan
LOCKFILE="/tmp/graphify_sync.lock"

# Cek lock aktif
if [ -f "$LOCKFILE" ]; then
    PID=$(cat "$LOCKFILE" 2>/dev/null)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        exit 0
    else
        rm -f "$LOCKFILE"
    fi
fi

(
    trap 'rm -f "$LOCKFILE"' EXIT INT TERM
    echo $BASHPID > "$LOCKFILE"
    sleep 2
    cd /root
    /root/telegram_remote_bot/venv/bin/python3 -m graphify update . >/dev/null 2>&1 || graphify update . >/dev/null 2>&1
) >/dev/null 2>&1 &

exit 0
