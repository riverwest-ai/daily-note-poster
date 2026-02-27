import os
import urllib.request
import json
from typing import Optional

# Unsplash API は無料で利用可能（API Key不要のデモモード or 登録して無料枠使用）
# デモモードでは制限がありますが、テストには十分です

def fetch_image_for_article(title: str, save_path: str = "temp_image.jpg") -> Optional[str]:
    """
    記事タイトルに基づいてUnsplashから関連画像を取得してダウンロードする。
    
    Args:
        title: 記事のタイトル
        save_path: 画像の保存先パス
        
    Returns:
        ダウンロードした画像のパス、失敗時はNone
    """
    try:
        # タイトルから検索キーワードを抽出（最初の数単語）
        # 日本語タイトルなのでシンプルに「news japan」で検索
        query = "japan,news,technology"
        
        # Unsplash Source API（簡易版、API Key不要）
        # 本番では https://api.unsplash.com/search/photos?query={query}&client_id={ACCESS_KEY}
        # を使用してください
        url = f"https://source.unsplash.com/800x600/?{query}"
        
        print(f"Fetching image for: {title}")
        print(f"Search query: {query}")
        
        # 画像をダウンロード
        urllib.request.urlretrieve(url, save_path)
        
        print(f"Image saved to: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"Failed to fetch image: {e}")
        return None

if __name__ == "__main__":
    # テスト
    result = fetch_image_for_article("テストニュース", "test_image.jpg")
    if result:
        print(f"✓ Image downloaded: {result}")
    else:
        print("✗ Failed to download image")
