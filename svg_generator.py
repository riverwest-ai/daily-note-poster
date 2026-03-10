from gemini_client import call_gemini

def generate_svg_code(title: str, summary: str) -> str:
    """
    記事のタイトルとサマリーからSVGコードを生成する
    """
    prompt = f"""
    You are a talented graphic designer. Create a simple, modern, flat-design SVG illustration for a blog post.
    
    Blog Title: {title}
    Summary: {summary}
    
    Requirements:
    - Output ONLY valid SVG code. No markdown, no explanations.
    - Aspect ratio: 16:9 (e.g., width="1200" height="675")
    - Style: Flat design, minimal, corporate tech blog style, vibrant but professional colors.
    - Use meaningful shapes and icons related to the topic.
    - Background: Use a soft, solid color or subtle gradient background (do not leave transparent).
    - Ensure all text (if any) is large and legible, but prefer visual metaphors over text.
    - The SVG must be self-contained (no external references).
    
    SVG Code:
    """

    try:
        content = call_gemini(prompt)

        # Markdownのコードブロック記号を削除
        content = content.replace("```svg", "").replace("```xml", "").replace("```", "").strip()

        # SVGタグが含まれているか確認
        if "<svg" not in content:
            return generate_placeholder_svg(title)

        return content

    except Exception as e:
        print(f"Error generating SVG: {e}")
        return generate_placeholder_svg(title)

def generate_placeholder_svg(title: str) -> str:
    """
    生成に失敗した場合のプレースホルダーSVG
    """
    return f'''
    <svg width="1200" height="675" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#f0f0f0"/>
        <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="48" fill="#333" text-anchor="middle" dominant-baseline="middle">
            {title[:20]}...
        </text>
    </svg>
    '''

if __name__ == "__main__":
    test_title = "AIの進化と未来"
    test_summary = "AI技術は日々進化しており、私たちの生活を変えようとしています。"
    svg = generate_svg_code(test_title, test_summary)
    print("Generated SVG code length:", len(svg))
    with open("test_image.svg", "w") as f:
        f.write(svg)
    print("Test SVG saved to test_image.svg")
