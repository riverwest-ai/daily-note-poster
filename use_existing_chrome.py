from playwright.sync_api import sync_playwright
import os
import shutil
import sys

# データ保存用ディレクトリ
USER_DATA_DIR = os.path.join(os.getcwd(), "browser_data")

# Macの標準的なChromeプロファイルパス
# 注意: ユーザー環境によって異なる場合があります
CHROME_PROFILE_PATH = os.path.expanduser("~/Library/Application Support/Google/Chrome")

def setup_login_with_existing_profile():
    """
    既存のChromeプロファイルの一部をコピーして利用することで、
    Googleログイン済みの状態（または信頼された端末情報）を引き継ぐ試み。
    """
    
    print("既存のChromeプロファイルを利用して起動を試みます。")
    print(f"Chrome Profile Path: {CHROME_PROFILE_PATH}")
    
    # コピーには時間がかかる＆リスクがあるため、今回は「Default」プロファイルのみをターゲットにする
    # または、ユーザーに「Chromeをすべて終了してください」と案内して直接指定する方法もあるが、
    # ロックファイルの競合でエラーになるため、推奨手順は「一度Chromeを終了してから実行」
    
    with sync_playwright() as p:
        print("Chromeを起動します...")
        print("もし『ユーザーデータディレクトリが使用中です』というエラーが出た場合は、")
        print("一度開いているGoogle Chromeをすべて終了（Command+Q）してから再実行してください。")
        
        try:
            # 既存のユーザーデータディレクトリを直接指定して起動
            # これにより、普段使っているChromeのログイン状態をそのまま利用できる可能性が高い
            browser = p.chromium.launch_persistent_context(
                user_data_dir=CHROME_PROFILE_PATH,
                channel="chrome",
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                ignore_default_args=["--enable-automation"],
            )
            
            page = browser.new_page()
            page.goto("https://note.com/")
            
            print("===")
            print("普段お使いのChrome設定で起動しました。")
            print("すでにログイン済みであれば、そのまま利用可能です。")
            print("もしログインしていない場合は、この画面でログインを行ってください。")
            print("確認が終わったら、ブラウザを閉じてスクリプトを終了してください。")
            print("===")
            
            input("確認完了したらEnterを押してください（スクリプトを終了します） >> ")
            browser.close()
            
        except Exception as e:
            print(f"\nエラーが発生しました: {e}")
            print("\n【対処法】")
            print("Google Chromeがバックグラウンドで起動している可能性があります。")
            print("DockのChromeアイコンを右クリック -> 「終了」をしてから、もう一度実行してください。")

if __name__ == "__main__":
    setup_login_with_existing_profile()
