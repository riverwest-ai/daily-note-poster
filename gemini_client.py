"""
gemini_client.py — Gemini API の共通クライアント

全ジェネレーター（article, weekly, state_updater, svg）から使う共通の呼び出し口。
リトライ（最大3回）・タイムアウト・エラーハンドリングをここで一元管理する。
"""
import json
import time
import urllib.request
import urllib.error
import os
from dotenv import load_dotenv
from config import GEMINI_MODEL

load_dotenv()
_API_KEY = os.getenv("GOOGLE_API_KEY")


def call_gemini(
    prompt: str,
    model: str = GEMINI_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """
    Gemini API を呼び出してテキストを返す。

    Args:
        prompt: 送信するプロンプト文字列。
        model: 使用するモデルID（デフォルトは config.GEMINI_MODEL）。
        temperature: 生成温度（0.0〜1.0）。
        max_tokens: 最大出力トークン数。

    Returns:
        生成されたテキスト文字列。

    Raises:
        ValueError: GOOGLE_API_KEY が未設定の場合。
        urllib.error.HTTPError: APIがエラーレスポンスを返した場合（リトライ上限後）。
        RuntimeError: 3回リトライしても成功しなかった場合。
    """
    if not _API_KEY:
        raise ValueError("GOOGLE_API_KEY が設定されていません。.env ファイルを確認してください。")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={_API_KEY}"
    )
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    for attempt in range(3):
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                wait = 20 * (attempt + 1)
                print(f"Rate limit hit. Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError("Gemini API: 3回リトライしても応答を得られませんでした。")
