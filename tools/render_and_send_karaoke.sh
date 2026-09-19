#!/bin/bash
set -e

BG_VIDEO="/root/.gemini/antigravity-cli/scratch/karaoke/bg_video.mp4"
AUDIO="/root/.gemini/antigravity-cli/scratch/karaoke/karaoke_MUTIARA_-_LAILA_AYU_FT_IRWAN_KRISDIYANTO_-_SIMPATIK_MUSIC.mp3"
ASS_SUB="/root/.gemini/antigravity-cli/scratch/karaoke/karaoke.ass"
OUT_VIDEO="/root/video_karaoke_mutiara_16x9.mp4"
ARTIFACT_DIR="/root/.gemini/antigravity-cli/brain/1e762963-a2a4-4982-b3f1-9626ac5bbc2c"

echo "[1/5] Rendering video with FFmpeg (explicit -map 0:v:0 -map 1:a:0)..."
ffmpeg -y -stream_loop -1 -i "$BG_VIDEO" \
  -i "$AUDIO" \
  -vf "subtitles=$ASS_SUB" \
  -map 0:v:0 -map 1:a:0 \
  -t 407.15 \
  -c:v libx264 -preset ultrafast -b:v 750k -maxrate 850k -bufsize 1500k \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  "$OUT_VIDEO"

echo "[2/5] Verifying output volume..."
ffmpeg -i "$OUT_VIDEO" -af "volumedetect" -vn -sn -dn -f null /dev/null 2>&1 | grep -E "mean_volume|max_volume"

echo "[3/5] Verifying output file size..."
ls -lh "$OUT_VIDEO"

echo "[4/5] Copying to artifact directory..."
cp "$OUT_VIDEO" "$ARTIFACT_DIR/video_karaoke_mutiara_16x9.mp4"

echo "[5/5] Sending to Telegram..."
python3 /root/telegram_remote_bot/send_telegram.py "$OUT_VIDEO" "🎤 Video Karaoke 16:9 (Audio Bersih + Latar Alam Pexels + Subtitle Tengah Layar): MUTIARA - LAILA AYU FT IRWAN KRISDIYANTO"

notify-send "Cimoy" "Video Karaoke Audio Bersih Terkirim ke Telegram" 2>/dev/null || true
echo "ALL DONE!"
