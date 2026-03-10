#!/bin/bash
# run_weekly.sh — 週次「手書き風」深掘り記事の生成・投稿スクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🗓️  Weekly Note Poster を起動します..."

# 仮想環境を有効化
source "$SCRIPT_DIR/.venv/bin/activate"

# 週次記事を生成・投稿
python "$SCRIPT_DIR/weekly_main.py"

exit 0
