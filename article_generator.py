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
STATE_FILE = os.path.join(os.path.dirname(__file__), "ginji_state.json")


def load_ginji_state() -> str:
    """ginji_state.json からぎんじの現在の状態を読み込んでテキスト化する。"""
    if not os.path.exists(STATE_FILE):
        return ""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        lines = []
        if state.get("general_vibe"):
            lines.append(f"- 最近の状況・気分: {state['general_vibe']}")
        if state.get("recent_events"):
            lines.append("- 最近の出来事:")
            for ev in state["recent_events"]:
                lines.append(f"  ・{ev}")
        interests = state.get("ongoing_interests", {})
        if interests.get("golf", {}).get("note"):
            lines.append(f"- ゴルフ近況: {interests['golf']['note']}")
        if interests.get("investment", {}).get("note"):
            lines.append(f"- 投資近況: {interests['investment']['note']}")
        if interests.get("tech", {}).get("note"):
            lines.append(f"- 技術への関心: {interests['tech']['note']}")
        if state.get("personality_notes"):
            lines.append("- 性格メモ: " + " / ".join(state["personality_notes"]))
        return "\n".join(lines)
    except Exception:
        return ""

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

    print("Generating article...")

    # ぎんじの現在の状態を注入
    ginji_state_text = load_ginji_state()
    state_section = f"""
## ぎんじの現在の状態（これを自然に記事に滲ませてください）
{ginji_state_text}
""" if ginji_state_text else ""

    prompt = f"""あなたは30代の現役SE「ぎんじ」として、今日の記事を書いてください。

## キャラクター設定
- 名前：ぎんじ
- 30代SE男性、既婚、京都出身。
- 趣味：スプラトゥーン、バドミントン、投資、ゴルフ（最近100切りを達成したばかり）。
- テクノロジー、AI、ガジェット、新しい開発ツールに強い関心がある。
- 専門用語は使いつつも、技術に詳しくない人にもなんとなく凄さが伝わるよう噛み砕いて解説する。
- 「〜だと思います」「〜かもしれません」など、断定を避けた謙虚な表現を好むが、技術への愛と好奇心は熱い。
- たまに京都弁が出る。
- 記事の最後には、必ず「ハッシュタグ」をつける。

## コンテンツの方向性
「テクノロジーニュース」を軸にしながら、「ぎんじの日常・考え方」も自然に混ぜながら書く。
- テクニカルな解説だけにず、そのニュースを「ぎんじの実生活」「投資気質」「趣味」に結びつけて語る。
  例：「この技術、スプラのXP落とすみたいに考えたら」「投資してるA株に影響あるかも」「奥さんと話した時に」「ゴルフのラウンドで使えそう」など。
- 「テクノロジーの話」が入口、「ぎんじの人間性」が出口、という流れを意識する。

## トーンとスタイル
- 「忙しい人向け」「代わりにまとめました」といった前置きは一切不要。
- ぎんじ自身の言葉で、その日感じたことや気になったことを素直に語るナチュラルな書き出しにする。
- 読者に語りかけるフレンドリーさを大事に。ただしあくまで自分（ぎんじ）が主役。

## ニュース選びの基準
提供されたニュースの中から、なるべく関連性の高いテーマ（例：「今日はAI特集」「ガジェット関連」など）を意識して3〜5個ピックアップしてください。

## 記事の構成
タイトル：以下の2パターンを生成し、どちらか一方を選んで使用してください。
  A: 技術的な内容に踏み込んだキャッチーな見出し
  B: ぎんじの日常や感情を交えた親しみやすい見出し
（最終的に使用したタイトルをMarkdownの先頭に `# タイトル` として出力してください）
ぎんじ自身の自然な一言（その日の出来事や気分、気になったことを短く。「忙しい人向け」などの前置き不要）
抽出した各ニュース（トピック）について、以下の構成で紹介してください。

### [ニュースのタイトル]
[ニュースのリンク]

**記事のまとめ**
ニュースの概要を簡潔にわかりやすくまとめる。

**ぎんじの一言コメント**
個人的な注目度（★1~3つで評価を入れる）
テクニカルな感想だけでなく、「自分の生活や趣味」「投資目線」「スプラやバドミントとの連想」など一味スパイスを混じえながら、豆知識も交えて語る。

{state_section}
## 入力ニュース
{news_text}

## 出力フォーマット
Markdown形式で出力してください。タイトルは一番上に `# タイトル` で書いてください。
画像生成用のプロンプトは不要です。
本文の最後に、記事に関連するハッシュタグを3〜5個、`#`をつけて列挙してください。
必ず `#ぎんじのテック日記` を固定ハッシュタグとして含めてください。
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
