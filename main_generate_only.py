"""
main_generate_only.py — 記事生成のみを行い、articles/に保存する（GitHub Actions用）

noteへの投稿は行わない。
生成された記事はgit commitでリポジトリに保存され、
Mac側のlaunchdがそれを読んで投稿する。
"""
import os
import sys
from datetime import datetime
from news_fetcher import fetch_latest_news
from article_generator import generate_article

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "articles")

WEEKLY_CTA = """

---

毎週日曜日は、ぎんじが一つのテーマを深掘りした読み物記事を投稿しています。
ぜひフォローして、次の記事もチェックしてみてください！
"""


def save_article(article: dict) -> str:
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(ARTICLES_DIR, f"{timestamp}.md")

    hashtags = article.get("hashtags", [])
    hashtag_line = "  ".join(f"#{tag}" for tag in hashtags) if hashtags else ""

    content = f"# {article['title']}\n\n"
    if hashtag_line:
        content += f"{hashtag_line}\n\n"
    content += article["body"]
    content += WEEKLY_CTA

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def main():
    print("=== Article Generator (GitHub Actions mode) ===")

    print("[1/2] Fetching news...")
    news_list = fetch_latest_news(limit=5)
    if not news_list:
        print("No news found. Exiting.")
        sys.exit(0)

    print("[2/2] Generating article...")
    article = generate_article(news_list)
    if not article or "記事の生成に失敗しました" in article.get("body", ""):
        print("Article generation failed.")
        sys.exit(1)

    saved_path = save_article(article)
    print(f"✅ Article saved: {saved_path}")
    print(f"   Title: {article['title']}")


if __name__ == "__main__":
    main()
