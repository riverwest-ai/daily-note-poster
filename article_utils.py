"""
article_utils.py — 記事の保存に関する共通ユーティリティ

main.py / main_generate_only.py / weekly_main.py / weekly_generate_only.py で
重複していた save 関数と WEEKLY_CTA 定数をここに集約する。
"""
import os
from datetime import datetime
from config import ARTICLES_DIR, WEEKLY_ARTICLES_DIR

# 日次記事末尾に挿入する週次記事への誘導文
WEEKLY_CTA = """
---

毎週日曜日は、ぎんじが一つのテーマを深掘りした読み物記事を投稿しています。
ぜひフォローして、次の記事もチェックしてみてください！
"""


def _build_article_content(article: dict, include_cta: bool = False) -> str:
    """記事 dict から Markdown 文字列を組み立てる（内部ヘルパー）。"""
    hashtags = article.get("hashtags", [])
    hashtag_line = "  ".join(f"#{tag}" for tag in hashtags) if hashtags else ""

    content = f"# {article['title']}\n\n"
    if hashtag_line:
        content += f"{hashtag_line}\n\n"
    content += article["body"]
    if include_cta:
        content += WEEKLY_CTA
    return content


def save_daily_article(article: dict, directory: str = ARTICLES_DIR) -> str:
    """日次記事を Markdown ファイルとして保存する。保存先パスを返す。"""
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(directory, f"{timestamp}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(_build_article_content(article, include_cta=True))
    return filepath


def save_weekly_article(article: dict, directory: str = WEEKLY_ARTICLES_DIR) -> str:
    """週次記事を Markdown ファイルとして保存する。保存先パスを返す。"""
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(directory, f"weekly_{timestamp}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(_build_article_content(article, include_cta=False))
    return filepath
