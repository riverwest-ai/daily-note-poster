import os
import json
import time
import urllib.request
import urllib.error
from dotenv import load_dotenv
from typing import Dict, List
from hashtag_generator import generate_hashtags

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def generate_article(news_list: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Generates a tech trend summary article based on a list of news items.
    """
    if not GOOGLE_API_KEY:
        return {
            "title": "Error: API Key Missing",
            "body": "Google Gemini API Keyが設定されていません。.envファイルを確認してください。"
        }

    if not news_list:
        return None

    # ニュースリストをテキスト形式に整形
    news_text = ""
    for i, news in enumerate(news_list, 1):
        news_text += f"News {i}:\nTitle: {news['title']}\nSummary: {news['summary']}\nSource: {news.get('source', '')}\nLink: {news['link']}\n\n"

    print("Generating tech trend summary article...")

    prompt = f"""あなたは30代の現役SE（システムエンジニア）で、テックブログの運営者です。
「自分で調べるのは面倒だけど、最新の技術トレンド情報は欲しい」という忙しい人向けに、今日の技術ニュースのまとめ記事を書いてください。

## キャラクター設定
- 30代SE男性、既婚、京都出身。
- 趣味：スプラトゥーン、バドミントン、投資。
- テクノロジー、AI、ガジェット、新しい開発ツールに強い関心がある。
- 専門用語は使いつつも、非エンジニアでもなんとなく凄さがわかるように噛み砕いて解説する。
- 「〜だと思います」「〜かもしれません」など、断定を避けた謙虚な表現を好むが、技術への愛は熱い。
- たまに京都弁が出る。
- 記事の最後には、必ず「ハッシュタグ」をつける。

## ニュース選びの基準
提供されたニュースの中から、なるべく関連性の高いテーマ（例：「今日はAI特集」「ガジェット関連」など）を意識して3〜5個ピックアップしてください。

## 記事の構成
タイトル：【日付入り】[キャッチーな見出し]
簡単なひとこと（アイスブレイク的な）
抽出した各ニュース（トピック）について、以下の簡単な構成で紹介してください。（導入や全体のまとめなどは不要です。シンプルにトピックを羅列してください）

### [ニュースのタイトル]
[ニュースのリンク]

**記事のまとめ**
ニュースの概要を簡潔にわかりやすくまとめる。

**ぎんじの一言コメント**
個人的な注目度（★1~3つで評価を入れる）
関連するちょっとした雑学（豆知識）を交えながら、現場のエンジニア目線での感想やコメントを語る。

## 入力ニュース
{news_text}

## 出力フォーマット
Markdown形式で出力してください。タイトルは一番上に `# タイトル` で書いてください。
画像生成用のプロンプトは不要です。
本文の最後（まとめの後）に、記事に関連するハッシュタグを3〜5個、`#`をつけて列挙してください。
"""

    # Gemini REST API endpoint
    model_id = "gemini-flash-latest"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={GOOGLE_API_KEY}"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    })

    headers = {"Content-Type": "application/json"}

    try:
        req = urllib.request.Request(url, data=payload.encode("utf-8"), headers=headers, method="POST")
        
        # Retry logic for rate limits
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 2:
                    wait = 15 * (attempt + 1)
                    print(f"Rate limit hit. Waiting {wait}s before retry...")
                    time.sleep(wait)
                else:
                    raise

        # If loop completes without breaking, it means all retries failed or no result was obtained
        if 'result' not in locals():
            raise Exception("Failed to get a response after multiple retries.")

        # Extract generated text
        content = result["candidates"][0]["content"]["parts"][0]["text"]
        
        # タイトル抽出（1行目にあると仮定）
        lines = content.strip().split('\n')
        title = lines[0].replace('# ', '').strip()
        body = '\n'.join(lines[1:]).strip()
        
        # 本文からハッシュタグを抽出（簡易的）
        # プロンプトでハッシュタグ生成を指示しているので、本文に含まれているはずだが、
        # note_poster側でもハッシュタグを求めている場合があるので、念のため別途生成するか、
        # outputから抽出するロジックを入れる。
        # ここではgenerate_hashtagsは使わず、本文に含まれることを期待するが、
        # 互換性のため空リストを返して、note_poster側で本文内のハッシュタグをそのまま使うようにする。
        # あるいは、generate_hashtags関数を使ってダミー生成する（タイトルから）。
        
        # 今回は、プロンプトでハッシュタグを出力させているので、それをそのままbodyとして扱う。
        # note_poster.pyは article['hashtags'] を使う場合と使わない場合があるか確認要。
        # -> note_poster.py は article['hashtags'] を見ている。
        
        # 簡易的にタイトルから生成しておく（冗長だが安全）
        hashtags = generate_hashtags(title, "Tech Trend Summary")

        return {
            "title": title,
            "body": body,
            "hashtags": hashtags,
            "image_path": None # 画像はなし
        }

    except Exception as e:
        print(f"Error generating article: {e}")
        return {
            "title": "エラー: 記事生成失敗",
            "body": f"記事の生成に失敗しました。\n詳細: {e}",
            "hashtags": [],
            "image_path": None
        }

if __name__ == "__main__":
    sample_list = [
        {"title": "AIが進化", "summary": "すごい", "link": "http://example.com", "source": "Sample"},
        {"title": "新型スマホ発売", "summary": "早い", "link": "http://example.co.jp", "source": "Demo"}
    ]
    article = generate_article(sample_list)
    if article:
        print(f"Title: {article['title']}")
        print(article['body'][:100] + "...")
