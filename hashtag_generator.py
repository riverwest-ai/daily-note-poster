# ハッシュタグ生成用の関数
def generate_hashtags(title: str, summary: str) -> list:
    """
    記事のタイトルとサマリーからハッシュタグを生成する
    """
    # 基本ハッシュタグ
    base_tags = ["note", "時事ニュース"]
    
    # キーワードマッピング
    keyword_to_tag = {
        # テクノロジー
        "AI": "AI", "人工知能": "AI", "ロボット": "ロボット", "テクノロジー": "テクノロジー",
        "アプリ": "アプリ", "サービス": "新サービス", "ガジェット": "ガジェット",
        # スポーツ
        "オリンピック": "オリンピック", "金メダル": "金メダル", "五輪": "オリンピック",
        "フィギュア": "フィギュアスケート", "スノーボード": "スノーボード",
        "野球": "野球", "サッカー": "サッカー", "バドミントン": "バドミントン",
        # 社会
        "政治": "政治", "経済": "経済", "投資": "投資", "株": "投資",
        "働き方": "働き方改革", "労働": "働き方",
        # エンタメ
        "ゲーム": "ゲーム", "スプラトゥーン": "スプラトゥーン",
        "映画": "映画", "アニメ": "アニメ"
    }
    
    text = title + summary
    generated_tags = []
    
    for keyword, tag in keyword_to_tag.items():
        if keyword in text and tag not in generated_tags:
            generated_tags.append(tag)
            if len(generated_tags) >= 3:  # 最大3個の生成タグ
                break
    
    # 基本タグ + 生成タグ
    all_tags = base_tags + generated_tags
    return all_tags[:5]  # 最大5個
