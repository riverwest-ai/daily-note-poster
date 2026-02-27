import os
from playwright.sync_api import sync_playwright

def render_svg_to_png(svg_code: str, output_path: str = "article_image.png"):
    """
    SVGコードをPNG画像に変換して保存する
    """
    # SVGを一時的なHTMLファイルとして保存（またはData URIとして扱う）
    # ここではHTMLコンテンツとして直接Playwrightに読み込ませる方法をとる
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>body {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background: #fff; }}</style>
    </head>
    <body>
        {svg_code}
    </body>
    </html>
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # ビューポートサイズをSVGのアスペクト比に合わせる
        page = browser.new_page(viewport={"width": 1200, "height": 675})
        
        # HTMLコンテンツを設定
        page.set_content(html_content)
        
        # SVG要素が表示されるのを待つ
        try:
            svg_locator = page.locator("svg").first
            svg_locator.wait_for(timeout=5000)
            
            # スクリーンショットを撮る
            svg_locator.screenshot(path=output_path)
            print(f"Image saved to {output_path}")
        except Exception as e:
            # SVGが見つからない場合やタイムアウト時は画面全体を撮る
            print(f"Warning: SVG capture failed ({e}), taking full page screenshot")
            page.screenshot(path=output_path)
            
        browser.close()
        
    return output_path

if __name__ == "__main__":
    # テスト
    with open("test_image.svg", "r") as f:
        svg_code = f.read()
    render_svg_to_png(svg_code, "test_output.png")
