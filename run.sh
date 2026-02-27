#!/bin/bash
# daily-note-poster 自動実行用ラッパースクリプト
# launchd から呼び出される

# スクリプトのディレクトリに移動
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ログディレクトリ作成
mkdir -p logs

# ログファイル名（日付ごと）
LOG_FILE="logs/daily_note_$(date +%Y%m%d).log"

echo "=== Daily Note Poster ===" >> "$LOG_FILE" 2>&1
echo "Start: $(date)" >> "$LOG_FILE" 2>&1

# 人間的なランダム遅延（0〜30分）を追加
DELAY=$((RANDOM % 1800))  # 0-1800秒（0-30分）
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Waiting ${DELAY} seconds before posting..." >> "$LOG_FILE" 2>&1
sleep $DELAY

# 仮想環境を有効化して実行
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting daily note poster..." >> "$LOG_FILE" 2>&1
source .venv/bin/activate >> "$LOG_FILE" 2>&1
python3 main.py >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Completed." >> "$LOG_FILE" 2>&1

echo "Exit Code: $EXIT_CODE" >> "$LOG_FILE" 2>&1
echo "End: $(date)" >> "$LOG_FILE" 2>&1

# 古いログを削除（30日以上前）
find "$SCRIPT_DIR/logs" -name "run_*.log" -mtime +30 -delete 2>/dev/null

exit $EXIT_CODE
