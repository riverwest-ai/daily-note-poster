from news_fetcher import fetch_latest_news, save_posted_urls_bulk
from article_generator import generate_article
from note_poster import post_to_note
from svg_generator import generate_svg_code
from image_renderer import render_svg_to_png
import random
import time
import os
from datetime import datetime

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "articles")

# 週次記事への誘導文（無料記事末尾に自動挿入）
WEEKLY_CTA = """

---

毎週日曜日は、ぎんじが一つのテーマを深掘りした読み物記事を投稿しています。
ぜひフォローして、次の記事もチェックしてみてください！
"""

def save_article_to_file(article: dict, news_list: list = None) -> str:
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
    content += WEEKLY_CTA  # 週次記事への誘導文を末尾に追加

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
    saved_path = save_article_to_file(article, news_list)
    print(f"記事をファイルに保存しました: {saved_path}")

    # 3.6. サムネイル画像を生成 (SVG → PNG)
    print("Generating thumbnail image...")
    try:
        svg_code = generate_svg_code(article['title'], article['body'][:200])
        # thumbnailsディレクトリに保存
        thumb_dir = os.path.join(os.path.dirname(__file__), "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(thumb_dir, f"{timestamp}.png")
        render_svg_to_png(svg_code, image_path)
        article['image_path'] = image_path
        print(f"サムネイルを保存しました: {image_path}")
    except Exception as e:
        print(f"サムネイル生成に失敗しました（記事投稿は続行）: {e}")
        article['image_path'] = None

    # 4. Post to Note
    print("Posting to Note (Draft)...")
    print("※ Google Chromeが終了していることを確認してください。")
    try:
        post_to_note(article, is_draft=True)
        print("Done!")
        # 5. 投稿済みURLを記録（次回以降の重複防止）
        posted_links = [n['link'] for n in news_list if 'link' in n]
        if posted_links:
            save_posted_urls_bulk(posted_links)
            print(f"投稿済みURL {len(posted_links)} 件を記録しました。")
    except Exception as e:
        print(f"Failed to post to note: {e}")

if __name__ == "__main__":
    main()
