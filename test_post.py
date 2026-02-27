"""
テスト用スクリプト: ダミー記事でnote投稿をテストする
API不要。Chrome終了後に実行してください。
"""
from note_poster import post_to_note

dummy_article = {
    "title": "【テスト】AI技術の最新動向と社会への影響",
    "body": """近年、AI技術は急速に進化を遂げています。

特に生成AIの台頭により、ビジネスの現場では大きな変革が起きています。

この記事はテスト投稿です。自動投稿システムの動作確認のために作成されました。

出典: https://example.com/test"""
}

print("=== ダミー記事でnote投稿テスト ===")
print(f"タイトル: {dummy_article['title']}")
print("Chromeを起動してnoteに下書き保存します...")

post_to_note(dummy_article, is_draft=True)
