#!/bin/bash
# スケジューラーのセットアップスクリプト
# このスクリプトを一度実行すると、毎日19:30に自動投稿が設定されます。

PLIST_NAME="com.tomac.daily-note-poster"
PLIST_SRC="$(cd "$(dirname "$0")" && pwd)/${PLIST_NAME}.plist"
PLIST_DST="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo "=== Daily Note Poster スケジューラー設定 ==="
echo ""

# logsディレクトリを作成
mkdir -p "$(cd "$(dirname "$0")" && pwd)/logs"

# 既存のジョブがあれば停止
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "既存のスケジュールを停止中..."
    launchctl unload "$PLIST_DST" 2>/dev/null
fi

# plistファイルをコピー
echo "スケジュール設定ファイルをインストール中..."
cp "$PLIST_SRC" "$PLIST_DST"

# ジョブをロード
echo "スケジュールを登録中..."
launchctl load "$PLIST_DST"

echo ""
echo "✅ 設定完了!"
echo ""
echo "スケジュール:"
echo "  - 毎日 19:30 に実行"
echo ""
echo "ログは以下に保存されます:"
echo "  $(cd "$(dirname "$0")" && pwd)/logs/"
echo ""
echo "--- コマンド一覧 ---"
echo "スケジュール停止: launchctl unload ~/Library/LaunchAgents/${PLIST_NAME}.plist"
echo "スケジュール再開: launchctl load ~/Library/LaunchAgents/${PLIST_NAME}.plist"
echo "状態確認:         launchctl list | grep ${PLIST_NAME}"
echo "手動テスト実行:   ./run.sh"
