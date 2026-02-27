from typing import Dict
import os

def generate_article_image(title: str, summary: str, output_path: str = "article_image.png") -> str:
    """
    記事のタイトルとサマリーから画像プロンプトを生成する
    
    Args:
        title: 記事のタイトル
        summary: 記事のサマリー
        output_path: 画像の保存先パス
    
    Returns:
        画像生成用のプロンプト
    """
    # 記事の内容を分析して画像のスタイルを決定
    text = title + summary
    
    # スタイルの決定
    style = "modern illustration"
    if any(word in text for word in ["スポーツ", "オリンピック", "選手", "試合"]):
        style = "dynamic sports illustration"
    elif any(word in text for word in ["AI", "テクノロジー", "技術", "アプリ", "ロボット"]):
        style = "futuristic tech illustration"
    elif any(word in text for word in ["自然", "環境", "花", "植物"]):
        style = "natural photography style"
    elif any(word in text for word in ["ビジネス", "経済", "投資", "働き方"]):
        style = "professional business illustration"
    
    # 簡潔なプロンプトを生成（日本語タイトルから英語に変換）
    prompt = f"""A {style} representing the concept of: {title[:50]}
    
Style: Clean, modern, suitable for a blog post header
Colors: Vibrant but professional
Mood: Positive and engaging
No text in the image
16:9 aspect ratio"""
    
    return prompt

if __name__ == "__main__":
    # テスト
    test_title = "AIが変える未来の働き方"
    test_summary = "人工知能技術の発展により、これからの働き方が大きく変わる可能性があります"
    prompt = generate_article_image(test_title, test_summary)
    print(f"Generated prompt:\n{prompt}")
