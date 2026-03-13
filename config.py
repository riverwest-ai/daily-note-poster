"""
config.py — プロジェクト全体の定数管理
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Gemini API ---
GEMINI_MODEL = "gemini-2.5-flash"

# --- ファイルパス ---
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
WEEKLY_ARTICLES_DIR = os.path.join(BASE_DIR, "weekly_articles")
STATE_FILE = os.path.join(BASE_DIR, "ginji_state.json")
POSTED_URLS_FILE = os.path.join(BASE_DIR, "posted_urls.json")
