from news_fetcher import fetch_latest_news
from article_generator import generate_article
from note_poster import post_to_note
# from svg_generator import generate_svg_code
# from image_renderer import render_svg_to_png
import random
import time
import os
from datetime import datetime

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "articles")

def save_article_to_file(article: dict) -> str:
    """生成した記事をMarkdownファイルとして保存する。保存先パスを返す。"""
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.md"
    filepath = os.path.join(ARTICLES_DIR, filename)

    hashtags = article.get("hashtags", [])
    hashtag_line = "  ".join(f"#{tag}" for tag in hashtags) if hashtags else ""

    content = f"# {article['title']}\n\n"
    if hashtag_line:
        content += f"{hashtag_line}\n\n"
    content += article["body"]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath

def main():
    print("Starting Daily Note Poster...")

    # 1. Fetch News
    print("Fetching news...")
    news_list = fetch_latest_news(limit=5)
    
    if not news_list:
        print("No news found. Exiting.")
        return

    # 2. Generate Article
    print("Generating article...")
    article = generate_article(news_list)
    
    if not article:
        print("Failed to generate article. Exiting.")
        return
        
    print(f"Generated Title: {article['title']}")

    # 3. Check if article generation succeeded
    if "記事の生成に失敗しました" in article['body'] or "API Key Missing" in article['title']:
        print("記事の生成に失敗したため、投稿をスキップします。")
        print("しばらく待ってから再実行してください（APIレートリミットの可能性があります）。")
        return

    # 3.5. ファイルに書き出す
    saved_path = save_article_to_file(article)
    print(f"記事をファイルに保存しました: {saved_path}")

    # 3.6. Generate image for the article (SVG based)
    # ユーザー要望により画像生成はスキップ
    print("Skipping image generation as per user request.")
    article['image_path'] = None

    # 4. Post to Note
    print("Posting to Note (Draft)...")
    print("※ Google Chromeが終了していることを確認してください。")
    try:
        post_to_note(article, is_draft=True)
        print("Done!")
    except Exception as e:
        print(f"Failed to post to note: {e}")

if __name__ == "__main__":
    main()
