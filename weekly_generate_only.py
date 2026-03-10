"""
weekly_generate_only.py — 週次記事生成のみを行う（GitHub Actions用）

noteへの投稿は行わない。生成された記事はweekly_articles/に保存される。
"""
import sys
from news_fetcher import fetch_latest_news
from weekly_article_generator import generate_weekly_article
from article_utils import save_weekly_article


def main():
    print("=== Weekly Article Generator (GitHub Actions mode) ===")

    print("[1/2] Fetching news for context...")
    try:
        news_list = fetch_latest_news(limit=10)
    except Exception:
        news_list = []

    print("[2/2] Generating weekly article...")
    article = generate_weekly_article(news_list)
    if not article or article.get("error"):
        print("Weekly article generation failed.")
        sys.exit(1)

    saved_path = save_weekly_article(article)
    print(f"✅ Weekly article saved: {saved_path}")
    print(f"   Title: {article['title']}")
    print(f"   Theme: {article.get('theme', 'N/A')}")


if __name__ == "__main__":
    main()
