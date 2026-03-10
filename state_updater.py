"""
state_updater.py — ぎんじの状態を週次でAIが少しずつ更新するスクリプト

設計方針：
- 変化は「ほんの少し」だけ。大きな変化は起こさない。
- AIが自然な人生の流れで、リアルな小さな出来事を積み重ねていく。
- 週次記事の生成後に呼ばれる想定。
"""
import os
import json
import time
import urllib.request
import urllib.error
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
STATE_FILE = os.path.join(os.path.dirname(__file__), "ginji_state.json")


def load_state() -> dict:
    """現在のぎんじの状態を読み込む。"""
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    """状態をファイルに保存する。"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def update_state_with_ai(current_state: dict) -> dict:
    """
    AIを使ってぎんじの状態をほんの少しだけ更新する。
    変化は微細で、人間的なリアリティを持たせる。
    """
    if not GOOGLE_API_KEY:
        print("GOOGLE_API_KEY がないため状態更新をスキップします。")
        return current_state

    today = datetime.now().strftime("%Y年%-m月%-d日")
    current_json = json.dumps(current_state, ensure_ascii=False, indent=2)

    prompt = f"""あなたは「ぎんじ」というキャラクターの人生を少しずつ育てるAIです。

## ぎんじについて
- 30代SE男性、既婚（奥さんあり）、京都出身。
- 趣味：スプラトゥーン、バドミントン、投資、ゴルフ（最近100切り達成）。
- テクノロジーと日常を愛する、謙虚だが好奇心旺盛な人物。

## 現在の状態（JSON）
{current_json}

## あなたのタスク
上記の状態から「1週間が経過した」として、ぎんじの状態を**ほんのわずかだけ**更新してください。

### 更新のルール（厳守）
- 変化は**リアルで小さいもの**のみ。劇的な変化は絶対にしない。
- 例：「ゴルフの練習に1回行った」「投資の本を読み始めた」「奥さんと映画を見た」「仕事で小さな成功があった」など。
- `recent_events` は最新3件に絞る（古いものは消す）。
- `growth_log` に今週の変化を1行だけ追記する。
- `last_updated` を今日の日付 {today} に更新する。
- `version` に1を足す。
- フィールドの追加・削除はしない。既存の構造を守る。
- **変化しすぎてはいけない**。読者が「あ、少し変わってきたな」と気づく程度が理想。

## 出力フォーマット
更新後のJSONのみを出力してください。説明文や```は不要です。
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
    })
    headers = {"Content-Type": "application/json"}

    try:
        req = urllib.request.Request(url, data=payload.encode("utf-8"), headers=headers, method="POST")
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 2:
                    time.sleep(20 * (attempt + 1))
                else:
                    raise

        content = result["candidates"][0]["content"]["parts"][0]["text"].strip()

        # ```json ``` ブロックがある場合は除去
        content = content.replace("```json", "").replace("```", "").strip()

        new_state = json.loads(content)
        print(f"状態を更新しました（version: {new_state.get('version', '?')}）")
        return new_state

    except Exception as e:
        print(f"状態更新に失敗しました（既存の状態を保持）: {e}")
        return current_state


def run_update():
    """状態を読み込み → AI更新 → 保存。"""
    print("=== ぎんじの状態を更新中... ===")
    current = load_state()
    if not current:
        print("ginji_state.json が見つかりません。スキップします。")
        return

    updated = update_state_with_ai(current)
    save_state(updated)
    print(f"更新完了: {STATE_FILE}")


if __name__ == "__main__":
    run_update()
