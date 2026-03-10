"""
main_generate_only.py — 記事生成のみを行い、articles/に保存する（GitHub Actions用）

noteへの投稿は行わない。
生成された記事はgit commitでリポジトリに保存され、
Mac側のlaunchdがそれを読んで投稿する。
"""
import sys
from news_fetcher import fetch_latest_news
from article_generator import generate_article
from article_utils import save_daily_article


def main():
    print("=== Article Generator (GitHub Actions mode) ===")

    print("[1/2] Fetching news...")
    news_list = fetch_latest_news(limit=5)
    if not news_list:
        print("No news found. Exiting.")
        sys.exit(0)

    print("[2/2] Generating article...")
    article = generate_article(news_list)
    if not article or article.get("error"):
        print("Article generation failed.")
        sys.exit(1)

    saved_path = save_daily_article(article)
    print(f"✅ Article saved: {saved_path}")
    print(f"   Title: {article['title']}")


if __name__ == "__main__":
    main()
