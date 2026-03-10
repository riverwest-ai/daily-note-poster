import feedparser
import random
import json
import os
from typing import List, Dict
from config import POSTED_URLS_FILE

# RSSフィードソース（信頼性と多様性を考慮して選定）
TECH_RSS_URLS = [
    "https://www.publickey1.jp/atom.xml",               # Publickey (クラウド、DevOps)
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",# ITmedia (総合IT)
    "https://www.gizmodo.jp/index.xml",                  # Gizmodo Japan (ガジェット)
    "https://japan.cnet.com/rss/index.rdf",              # CNET Japan
    "https://zenn.dev/feed",                             # Zenn Trending (エンジニア向け)
    "https://qiita.com/popular-items/feed",              # Qiita Popular (エンジニア向け)
]

# ネガティブなキーワード（除外対象）
NEGATIVE_KEYWORDS = [
    '死亡', '死去', '事故', '爆発', '火災', '逮捕', '容疑', '殺人',
    '遺体', '負傷', '重体', '被害', '崩壊', '墜落', '衝突', '戦争',
    '地震', '津波', '台風', '災害', '被災', '犠牲', '訃報', '急死',
    'はねられ', '意識不明', '救急搬送', '重傷', '軽傷', '不明',
    '炎上', '謝罪', '不正', '流出',
]


def load_posted_urls() -> set:
    """投稿済みURLのセットを読み込む。"""
    if not os.path.exists(POSTED_URLS_FILE):
        return set()
    try:
        with open(POSTED_URLS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("urls", []))
    except Exception:
        return set()


def save_posted_url(url: str) -> None:
    """投稿済みURLをファイルに追記する。"""
    posted = load_posted_urls()
    posted.add(url)
    try:
        with open(POSTED_URLS_FILE, "w", encoding="utf-8") as f:
            json.dump({"urls": list(posted)}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: posted_urls.json の保存に失敗しました: {e}")


def save_posted_urls_bulk(urls: List[str]) -> None:
    """複数の投稿済みURLをまとめて保存する（1回のread/writeで効率的に処理）。"""
    if not urls:
        return
    posted = load_posted_urls()
    posted.update(urls)
    try:
        with open(POSTED_URLS_FILE, "w", encoding="utf-8") as f:
            json.dump({"urls": list(posted)}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: posted_urls.json の保存に失敗しました: {e}")



def is_negative_news(title: str, summary: str) -> bool:
    """ニュースがネガティブかどうかを判定"""
    text = title + summary
    return any(kw in text for kw in NEGATIVE_KEYWORDS)


def fetch_latest_news(limit: int = 5) -> List[Dict[str, str]]:
    """
    複数のテック系RSSからニュースを取得し、重複チェック済みのリストを返す。

    Args:
        limit (int): 取得する記事の最大数

    Returns:
        List[Dict]: ニュース情報のリスト
    """
    posted_urls = load_posted_urls()
    all_news = []

    # ランダムに4つ選んで多様なソースを確保
    selected_feeds = random.sample(TECH_RSS_URLS, min(4, len(TECH_RSS_URLS)))

    for url in selected_feeds:
        try:
            print(f"Fetching RSS: {url}")
            feed = feedparser.parse(url)

            for entry in feed.entries[:4]:
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                summary = entry.get('summary', '') or entry.get('description', '')

                # ネガティブフィルタ
                if is_negative_news(title, summary):
                    continue

                # 投稿済みURLはスキップ
                if link in posted_urls:
                    print(f"  [SKIP - 既出] {title}")
                    continue

                all_news.append({
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'source': feed.feed.get('title', 'Unknown Source'),
                })

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

    if not all_news:
        print("No new news found from any source.")
        return []

    # リンクで重複排除
    unique_news = list({v['link']: v for v in all_news}.values())
    random.shuffle(unique_news)
    result = unique_news[:limit]

    print(f"Collected {len(result)} news items.")
    for n in result:
        print(f"  - {n['title']} ({n['source']})")

    return result


if __name__ == "__main__":
    news = fetch_latest_news()
    for n in news:
        print(f"Title: {n['title']}")
        print(f"Link:  {n['link']}")
        print(f"Source:{n.get('source', 'Unknown')}")
        print("-" * 20)
