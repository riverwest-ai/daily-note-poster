import os
import time
from playwright.sync_api import sync_playwright

from note_poster import _prepare_session, TEMP_PROFILE_DIR

def test_authentication():
    """
    note_poster.pyの認証部分だけをテストするスクリプト。
    セッション（Chromeプロファイル）をコピーし、noteにアクセスしてログイン状態を確認します。
    """
    print("=== 認証テストを開始します ===")
    
    # セッション準備（note_poster.pyと同じ処理）
    _prepare_session()
    
    print("\nブラウザを起動して、note.comへアクセスします...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=TEMP_PROFILE_DIR,
                channel="chrome",
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                ignore_default_args=["--enable-automation"],
            )
            print("ブラウザの起動に成功しました。")
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # note.com にアクセス
            page.goto("https://note.com/", wait_until="networkidle", timeout=30000)
            
            if "login" in page.url:
                print("\n❌ ログインしていません（セッション切れ・未ログイン状態です）。")
                print("note_poster.py 実行時に認証エラーが発生する原因はこれです。")
                print("\n【解決方法】")
                print("1. このテストスクリプトを終了します。")
                print("2. 普段お使いの「Google Chrome」を開きます。")
                print("3. note.comにアクセスし、ログインを完了させます。")
                print("4. もう一度このテストを実行して、「✅ ログイン済み」になるか確認してください。")
            else:
                print("\n✅ ログイン済み（セッション有効）です！")
                print("note_poster.py の認証は正常に通過できるはずです。")
                
            print("\n動作確認のためブラウザをそのままにしています。")
            print("ターミナルで Enter キーを押すと終了します...")
            input()
            
        except Exception as e:
            print(f"\nエラーが発生しました: {e}")
        finally:
            if 'browser' in locals():
                browser.close()

if __name__ == "__main__":
    test_authentication()
