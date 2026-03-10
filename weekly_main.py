"""
weekly_main.py — 週次「手書き風」深掘り記事の生成・投稿エントリポイント

実行方法:
  ./run_weekly.sh
  または
  source .venv/bin/activate && python weekly_main.py
"""
from news_fetcher import fetch_latest_news
from weekly_article_generator import generate_weekly_article
from note_poster import post_to_note
from state_updater import run_update as update_ginji_state
from article_utils import save_weekly_article
from config import ARTICLES_DIR


def main():
    print("=" * 50)
    print("Weekly Note Poster — 手書き風深掘り記事")
    print("=" * 50)

    # 1. 今週のニュースを参考情報として取得（多めに取る）
    print("\n[1/3] 今週のニュースを取得中...")
    try:
        news_list = fetch_latest_news(limit=10)
        print(f"  {len(news_list)} 件のニュースを取得しました（参考素材として使用）")
    except Exception as e:
        print(f"  ニュース取得に失敗しましたが、続行します: {e}")
        news_list = []

    # 2. 手書き風記事を生成
    print("\n[2/3] 週次記事を生成中（少し時間がかかります）...")
    article = generate_weekly_article(news_list)

    if not article or article.get("error"):
        print("記事の生成に失敗しました。終了します。")
        return

    print(f"\n  タイトル: {article['title']}")
    print(f"  テーマ  : {article.get('theme', 'N/A')}")
    print(f"  有料設定: {'✓ 有料記事' if article.get('is_paid') else '無料記事'}")

    # 3. ファイルに保存（weekly_main では articles/ に保存）
    saved_path = save_weekly_article(article, directory=ARTICLES_DIR)
    print(f"\n  保存先: {saved_path}")

    # 4. Note へ投稿（下書き保存）
    print("\n[3/3] Noteに下書き投稿中...")
    print("※ Google Chromeが終了していることを確認してください。")
    try:
        post_to_note(article, is_draft=True)
        print("\n✅ 完了！下書きとして保存されました。")
        print("   noteの管理画面から内容を確認し、有料設定の上で公開してください。")
    except Exception as e:
        print(f"\n❌ 投稿に失敗しました: {e}")
        print(f"   記事はファイルに保存済みです: {saved_path}")

    # 5. ぎんじの状態を小さく進化させる
    print("\n[ボーナス] ぎんじの状態を少し変化させます...")
    try:
        update_ginji_state()
    except Exception as e:
        print(f"   状態アップデートに失敗（記事投稿には影響なし）: {e}")


if __name__ == "__main__":
    main()
