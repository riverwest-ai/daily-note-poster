from playwright.sync_api import sync_playwright
import os
import time

# データ保存用ディレクトリ (note_poster.py と統一)
USER_DATA_DIR = os.path.join(os.getcwd(), "chrome_session")

def setup_login():
    """
    ユーザーが手動でログインし、そのセッション情報を保存するためのスクリプト。
    """
    print(f"Browser data will be saved to: {USER_DATA_DIR}")
    
    with sync_playwright() as p:
        # Googleログインのセキュリティブロックを回避するため、
        # 同梱のChromiumではなく、システムにインストールされている正規のGoogle Chromeを使用します。
        # 注意: Google Chromeがインストールされている必要があります。
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                channel="chrome",  # 正規のChromeを使用
                # 検出回避のための追加引数
                args=[
                    "--disable-blink-features=AutomationControlled",
                ]
            )
        except Exception as e:
            print(f"Chromeの起動に失敗しました: {e}")
            print("Chromiumで再試行します...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
            )
        
        page = browser.new_page()
        page.goto("https://note.com/login")
        
        print("===")
        print("【重要】ブラウザが開きました。")
        print("手動でGoogleログイン（または他のSSO）を行ってください。")
        print("ログインが完了し、noteのトップページが表示されたら、このターミナルで Enter キーを押してください。")
        print("===")
        
        input("ログイン完了後に Enter を押してください >> ")
        
        # 念のためトップページへ
        page.goto("https://note.com/")
        print("セッション情報を保存しました。ブラウザを閉じます...")
        
        browser.close()
        print("設定完了です！ main.py を実行するとログイン状態が維持されます。")

if __name__ == "__main__":
    setup_login()
