import os
import json
import time
import urllib.request
import urllib.error
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime, timedelta

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 週次記事のテーマ候補（週によって自動ローテーション）
WEEKLY_THEMES = [
    {
        "theme": "ai_tool_experiment",
        "title_hint": "今週試したAIツール、ぶっちゃけどうやった？",
        "angle": "その週に話題になったAIツールや新機能を実際に触った（触ってみた想定の）体験談として書く。良かった点・微妙だった点・実務での使い所を正直に語る。",
    },
    {
        "theme": "engineer_lifestyle",
        "title_hint": "30代SEの週末の過ごし方と技術との距離感",
        "angle": "仕事と趣味（スプラトゥーン・バドミントン・投資）と技術のバランスについて、ぎんじが感じていることをエッセイ風に語る。",
    },
    {
        "theme": "tech_deep_dive",
        "title_hint": "今週一番気になった技術、ちゃんと調べてみた",
        "angle": "その週に気になったテクノロジートレンドを一つ深掘り。表面的な紹介ではなく、背景・仕組み・実務での影響を自分なりの言葉で解説する。",
    },
    {
        "theme": "investment_x_tech",
        "title_hint": "エンジニア目線で技術株・トレンドを読む",
        "angle": "技術トレンドと投資の視点を掛け合わせた考察。あくまで個人的な見方として、面白い気づきを語る（投資アドバイスではない）。",
    },
    {
        "theme": "weekly_reflection",
        "title_hint": "今週の振り返り：技術・仕事・生活",
        "angle": "週の総括。技術ニュースへの感想・仕事で感じたこと・日常の一コマを組み合わせて、等身大の30代SEとしての週を振り返る。",
    },
]


def get_this_week_theme() -> Dict:
    """週番号に基づいてテーマをローテーションする。"""
    week_number = datetime.now().isocalendar()[1]
    return WEEKLY_THEMES[week_number % len(WEEKLY_THEMES)]


def generate_weekly_article(news_list: Optional[List[Dict]] = None) -> Optional[Dict]:
    """
    週1回の「手書き風」深掘り記事を生成する。
    news_list: その週のニュースリスト（参考情報として渡す。なくてもOK）
    """
    if not GOOGLE_API_KEY:
        return {
            "title": "Error: API Key Missing",
            "body": "Google Gemini API Keyが設定されていません。.envファイルを確認してください。",
            "hashtags": [],
            "image_path": None,
            "is_paid": False,
        }

    theme = get_this_week_theme()
    today = datetime.now().strftime("%Y年%-m月%-d日")

    # 参考ニュースをテキスト化（あれば）
    news_context = ""
    if news_list:
        news_context = "## 今週の参考ニュース（記事の素材として使ってください）\n"
        for i, news in enumerate(news_list[:10], 1):
            news_context += f"{i}. {news['title']} — {news.get('source', '')}\n"
        news_context += "\n"

    prompt = f"""あなたは30代の現役SE「ぎんじ」として、週に1本だけ書く「ちゃんと書いた記事」を執筆してください。

## ぎんじのプロフィール
- 名前：ぎんじ
- 30代SE男性、既婚、京都出身。
- 趣味：スプラトゥーン、バドミントン、投資、ゴルフ（最近100切りを達成したばかり）。
- テクノロジー、AI、ガジェット、新しい開発ツールに強い関心がある。
- 専門用語は使いつつも、技術に詳しくない人にもなんとなく凄さが伝わるよう噛み砕いて解説する。
- 「〜だと思います」「〜かもしれません」など、断定を避けた謙虚な表現を好むが、技術への愛と好奇心は熱い。
- たまに京都弁が出る。

## この記事の性質
- 毎日の「ニュースまとめ」とは違い、週1本だけ書くちゃんとした読み物。
- 「ぎんじが自分の言葉で書いた」と感じられる、体験・感情・考察が込もった文章にする。
- 読者が「また来週も読みたい」と思えるような、人柄が伝わる文章。
- テンプレート感・まとめサイト感は一切排除。ぎんじ自身が主役。

## 今週のテーマ
テーマ方向性：{theme['angle']}
タイトルヒント（完全に同じでなくてOK、参考に）：{theme['title_hint']}

{news_context}

## 執筆の指針
- **書き出し**：「お疲れ様です」「忙しい皆さんのために」等の定型文は不要。ぎんじがその週に感じた・体験したことから自然に入る。
- **構成**：自由でOK。ただし「何かを発見・体験・考察した話」として読者を引き込む流れにする。
- **長さ**：毎日記事の2〜3倍（1500〜2500文字目安）。しっかり読み応えのある分量。
- **締め**：読者への問いかけや、ぎんじ自身の次のアクションで締める。説教臭くならず、等身大で。
- **ハッシュタグ**：最後に3〜5個。

## 出力フォーマット
Markdown形式で出力してください。タイトルは一番上に `# タイトル` で書いてください。
画像生成用プロンプトは不要です。
本文の最後にハッシュタグを3〜5個、`#`をつけて列挙してください。

今日の日付は {today} です。
"""

    model_id = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={GOOGLE_API_KEY}"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 1.0,      # 手書き感のために少し高め
            "maxOutputTokens": 4096,
        }
    })
    headers = {"Content-Type": "application/json"}

    print(f"Generating weekly article (theme: {theme['theme']})...")

    try:
        req = urllib.request.Request(url, data=payload.encode("utf-8"), headers=headers, method="POST")

        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=90) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 2:
                    wait = 20 * (attempt + 1)
                    print(f"Rate limit hit. Waiting {wait}s before retry...")
                    time.sleep(wait)
                else:
                    raise

        content = result["candidates"][0]["content"]["parts"][0]["text"]
        lines = content.strip().split("\n")
        title = lines[0].replace("# ", "").strip()
        body = "\n".join(lines[1:]).strip()

        return {
            "title": title,
            "body": body,
            "hashtags": [],       # 本文末に含まれる
            "image_path": None,
            "is_paid": True,      # 週次記事は有料記事として扱う
            "theme": theme["theme"],
        }

    except Exception as e:
        print(f"Error generating weekly article: {e}")
        return {
            "title": "エラー: 週次記事生成失敗",
            "body": f"記事の生成に失敗しました。\n詳細: {e}",
            "hashtags": [],
            "image_path": None,
            "is_paid": False,
            "theme": theme["theme"],
        }


if __name__ == "__main__":
    article = generate_weekly_article()
    if article:
        print(f"\n===== タイトル =====\n{article['title']}\n")
        print(f"===== 本文（冒頭300文字） =====\n{article['body'][:300]}...\n")
        print(f"テーマ: {article['theme']} / 有料: {article['is_paid']}")
