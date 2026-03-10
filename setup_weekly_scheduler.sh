#!/bin/bash
# setup_weekly_scheduler.sh — 週次記事の自動投稿スケジューラをセットアップする

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.tomac.weekly-note-poster"
PLIST_SRC="$SCRIPT_DIR/$PLIST_NAME.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"

echo "🗓️  週次記事スケジューラをセットアップします..."

# 既存のジョブをアンロード（存在する場合）
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "  既存のスケジューラを停止中..."
    launchctl unload "$PLIST_DEST" 2>/dev/null
fi

# plistをLaunchAgentsにコピー
cp "$PLIST_SRC" "$PLIST_DEST"

# スケジューラを登録
launchctl load "$PLIST_DEST"

echo "✅ セットアップ完了！"
echo "   毎週日曜日 20:00 に自動実行されます。"
echo ""
echo "停止する場合:"
echo "  launchctl unload ~/Library/LaunchAgents/$PLIST_NAME.plist"
echo ""
echo "手動で今すぐ実行する場合:"
echo "  ./run_weekly.sh"
