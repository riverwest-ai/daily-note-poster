import os
import time
import shutil
from playwright.sync_api import sync_playwright
from typing import Dict

# Macの標準的なChromeプロファイルパス
CHROME_PROFILE_PATH = os.path.expanduser("~/Library/Application Support/Google/Chrome")

# セッション情報のコピー先
TEMP_PROFILE_DIR = os.path.join(os.getcwd(), "chrome_session")

def _prepare_session():
    """
    Chromeプロファイルから最低限のCookie/セッション情報だけをコピーする。
    """
    default_profile = os.path.join(CHROME_PROFILE_PATH, "Default")
    dest_default = os.path.join(TEMP_PROFILE_DIR, "Default")
    
    # 既にセッションコピーが存在していて比較的新しければスキップ
    cookie_dest = os.path.join(dest_default, "Cookies")
    if os.path.exists(cookie_dest):
        age = time.time() - os.path.getmtime(cookie_dest)
        if age < 3600:
            print("Cached session found (< 1 hour old). Reusing.")
            return
    
    print("Copying session data from Chrome profile...")
    os.makedirs(dest_default, exist_ok=True)
    
    files_to_copy = [
        "Cookies",
        "Cookies-journal",
        "Login Data",
        "Login Data-journal",
        "Web Data",
        "Web Data-journal",
        "Preferences",
        "Secure Preferences",
    ]
    
    for fname in files_to_copy:
        src = os.path.join(default_profile, fname)
        dst = os.path.join(dest_default, fname)
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
            except Exception as e:
                print(f"Warning: Could not copy {fname}: {e}")
    
    local_state_src = os.path.join(CHROME_PROFILE_PATH, "Local State")
    local_state_dst = os.path.join(TEMP_PROFILE_DIR, "Local State")
    if os.path.exists(local_state_src):
        try:
            shutil.copy2(local_state_src, local_state_dst)
        except Exception as e:
            print(f"Warning: Could not copy Local State: {e}")
    
    print("Session data copied.")

def post_to_note(article: Dict[str, str], is_draft: bool = True):
    """
    Posts an article to note.com using a lightweight copy of Chrome session.
    """
    _prepare_session()
    print("Launching browser...")

    # ハッシュタグを取得（存在する場合）
    hashtags = article.get('hashtags', [])
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=TEMP_PROFILE_DIR,
                channel="chrome",
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                ignore_default_args=["--enable-automation"],
            )
            print("Browser launched successfully.")
        except Exception as e:
            print(f"Chromeの起動に失敗しました: {e}")
            return

        try:
            if browser.pages:
                page = browser.pages[0]
            else:
                page = browser.new_page()

            # 1. note.com のトップにアクセスしてログイン状態を確認
            print("Checking login status...")
            page.goto("https://note.com/", wait_until="networkidle", timeout=30000)
            
            if "login" in page.url:
                print("Error: ログインしていません。")
                raise Exception("Login required.")

            print("Session looks valid.")

            # 2. エディタページに遷移
            # note.com/notes/new → editor.note.com/new にリダイレクトされる
            print("Navigating to editor...")
            page.goto("https://note.com/notes/new", timeout=60000, wait_until="networkidle")
            
            # OAuth リダイレクトが発生する場合があるため、
            # 最終的に editor.note.com に到達するまで待機
            print(f"Current URL: {page.url}")
            max_wait = 90
            waited = 0
            while waited < max_wait:
                url = page.url
                if "editor.note.com" in url:
                    print(f"Editor URL detected: {url}")
                    break
                elif "note.com/notes/new" in url:
                    print(f"Redirecting... ({waited}s)")
                elif "accounts.google" in url:
                    print(f"Google OAuth in progress... ({waited}s)")
                else:
                    print(f"Waiting... ({waited}s) URL: {url[:80]}")
                time.sleep(3)
                waited += 3
            
            # エディタはSPA（Next.js）なので、JS読み込み完了を待つ
            print("Waiting for editor to fully load...")
            time.sleep(5)  # SPAの初期レンダリング待ち
            
            # エディタのタイトル入力欄を探す
            # note.comのエディタは動的にレンダリングされるため、複数のセレクタを試す
            title_selectors = [
                'textarea[placeholder*="タイトル"]',
                'textarea[placeholder*="title"]',
                'input[placeholder*="タイトル"]',
                '.note-editor__title',
                '[data-testid="title"]',
                'textarea',
                'div[contenteditable="true"]:first-of-type',
            ]
            
            title_element = None
            for selector in title_selectors:
                try:
                    title_element = page.wait_for_selector(selector, timeout=5000)
                    if title_element:
                        print(f"Title element found with selector: {selector}")
                        break
                except:
                    continue
            
            if not title_element:
                # セレクタが見つからない場合、現在のHTMLの構造をデバッグ出力
                print("Warning: Could not find title element. Dumping page structure...")
                html_snippet = page.evaluate("() => document.querySelector('#__next')?.innerHTML?.substring(0, 2000) || 'N/A'")
                print(f"HTML snippet: {html_snippet}")
                raise Exception("Could not find title input element in the editor.")
            
            # タイトル入力
            print("Inputting title...")
            title_element.click()
            title_element.fill(article['title'])

            # 画像をアップロード（存在する場合）
            image_path = article.get('image_path')
            if image_path and os.path.exists(image_path):
                print(f"Uploading image: {image_path}")
                try:
                    # 方法1: 強力なJSインジェクションでinput[type=file]を探して操作
                    # noteのエディタには通常、隠れたfile inputがある
                    print("Attempting to upload via JS injection...")
                    
                    # ページ内のすべてのinput[type=file]を可視化・操作可能にする
                    page.evaluate("""
                        () => {
                            const inputs = document.querySelectorAll('input[type="file"]');
                            inputs.forEach(input => {
                                input.style.display = 'block';
                                input.style.visibility = 'visible';
                                input.style.position = 'fixed';
                                input.style.top = '0';
                                input.style.left = '0';
                                input.style.zIndex = '9999';
                                input.style.width = '100px';
                                input.style.height = '100px';
                                input.style.opacity = '1';
                            });
                        }
                    """)
                    
                    file_input = page.locator('input[type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(image_path)
                        print("Image uploaded via forced input[type='file']")
                        time.sleep(5)
                    else:
                        print("No input[type='file'] found even after JS injection.")
                        # 方法2: ドラッグ＆ドロップ（ProseMirrorエディタに対して）
                        print("Attempting to upload via Drag & Drop simulation...")
                        
                        # 画像ファイルをバイナリとして読み込む
                        with open(image_path, 'rb') as f:
                            # Playwrightのevaluateで渡すためにリスト化（大きなファイルだと重いが、今回は数KBなのでOK）
                            # バイナリデータを直接渡すとエラーになることがあるので、Base64かUint8Arrayの配列にする
                            # ここでは簡便のため、Python側で読んでJS側でFileオブジェクトを再構築する手法をとる
                            # ただしバイナリをそのまま渡せないので、Base64エンコードする
                            import base64
                            encoded_image = base64.b64encode(f.read()).decode('utf-8')
                            
                        page.evaluate("""
                            ([encodedImage, fileName, mimeType]) => {
                                // Base64からBlob/Fileを作成
                                const byteCharacters = atob(encodedImage);
                                const byteNumbers = new Array(byteCharacters.length);
                                for (let i = 0; i < byteCharacters.length; i++) {
                                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                                }
                                const byteArray = new Uint8Array(byteNumbers);
                                const file = new File([byteArray], fileName, { type: mimeType });
                                
                                // DataTransferを作成
                                const dt = new DataTransfer();
                                dt.items.add(file);
                                
                                // dropイベントを作成
                                const dropEvent = new DragEvent('drop', {
                                    bubbles: true,
                                    cancelable: true,
                                    dataTransfer: dt
                                });
                                
                                // エディタに対してイベント発火
                                const editor = document.querySelector('.ProseMirror') || document.querySelector('[contenteditable="true"]');
                                if (editor) {
                                    editor.dispatchEvent(dropEvent);
                                    console.log("Drop event dispatched to editor");
                                } else {
                                    console.error("Editor not found for drop event");
                                }
                            }
                        """, [encoded_image, os.path.basename(image_path), "image/png"])
                        
                        print("Drag & Drop event dispatched.")
                        time.sleep(5)
                        
                except Exception as e:
                    print(f"Failed to upload image: {e}")
            
            # 画像をアップロード（存在する場合）
            image_path = article.get('image_path')
            if image_path and os.path.exists(image_path):
                print(f"Uploading image: {image_path}")
                try:
                    # まずはinput[type="file"]があるか確認し、あればアップロード
                    # noteのエディタでは隠しinput要素があることが多い
                    file_input = page.locator('input[type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(image_path)
                        print("Image uploaded via input[type='file']")
                        # アップロード完了を少し待つ
                        time.sleep(5)
                    else:
                        print("File input not found, skipping image upload.")
                except Exception as e:
                    print(f"Failed to upload image: {e}")
            
            # 本文入力
            # ProseMirrorエディタを探す
            print("Looking for body editor...")
            body_selectors = [
                '.ProseMirror',
                'div[contenteditable="true"]',
                '[role="textbox"]',
            ]
            
            body_element = None
            for selector in body_selectors:
                try:
                    body_element = page.wait_for_selector(selector, timeout=5000)
                    if body_element:
                        print(f"Body element found with selector: {selector}")
                        break
                except:
                    continue
            
            if not body_element:
                print("Warning: Could not find body editor element.")
                raise Exception("Could not find body editor element.")
            
            # 本文を入力
            print("Inputting body...")
            body_element.click()
            # keyboard.type で1文字ずつ入力（ProseMirrorはfillが使えない場合がある）
            page.keyboard.type(article['body'])
            
            # 下書き保存
            if is_draft:
                print("Saving as draft...")
                time.sleep(2)
                
                # 下書き保存ボタンを探す
                draft_selectors = [
                    'button:has-text("下書き保存")',
                    'button:has-text("保存")',
                    '[data-testid="save-draft"]',
                ]
                
                saved = False
                for selector in draft_selectors:
                    try:
                        page.click(selector, timeout=5000)
                        saved = True
                        print(f"Clicked save button: {selector}")
                        break
                    except:
                        continue
                
                if not saved:
                    print("Could not find save button. Article may auto-save.")
                
                time.sleep(3)
                print("Draft saved.")

            print("Article processed successfully!")

        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
            
        finally:
            browser.close()

if __name__ == "__main__":
    print("This module is for posting logic. Run test_post.py or main.py.")
