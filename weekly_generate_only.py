"""
weekly_generate_only.py — 週次記事生成のみを行う（GitHub Actions用）

noteへの投稿は行わない。生成された記事はweekly_articles/に保存される。
"""
import os
import sys
from datetime import datetime
from news_fetcher import fetch_latest_news
from weekly_article_generator import generate_weekly_article

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "weekly_articles")


def save_weekly_article(article: dict) -> str:
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(ARTICLES_DIR, f"weekly_{timestamp}.md")

    content = f"# {article['title']}\n\n"
    content += article["body"]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def main():
    print("=== Weekly Article Generator (GitHub Actions mode) ===")

    print("[1/2] Fetching news for context...")
    try:
        news_list = fetch_latest_news(limit=10)
    except Exception:
        news_list = []

    print("[2/2] Generating weekly article...")
    article = generate_weekly_article(news_list)
    if not article or "記事の生成に失敗しました" in article.get("body", ""):
        print("Weekly article generation failed.")
        sys.exit(1)

    saved_path = save_weekly_article(article)
    print(f"✅ Weekly article saved: {saved_path}")
    print(f"   Title: {article['title']}")
    print(f"   Theme: {article.get('theme', 'N/A')}")


if __name__ == "__main__":
    main()
