import feedparser
import random
from typing import List, Dict

# Tech RSS Feeds
RSS_FEEDS = [
    "https://www.publickey1.jp/atom.xml",          # Publickey (クラウド、DevOps)
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml", # ITmedia (総合IT)
    "https://cn.engadget.com/rss.xml",             # Engadget (ガジェット) -> 閉鎖されている可能性あるので注意、代替: Gizmodo
    "https://www.gizmodo.jp/index.xml",            # Gizmodo Japan
    "https://qiita.com/popular-items/feed",        # Qiita Popular
    "https://zenn.dev/feed",                       # Zenn Trending
    "https://japan.cnet.com/rss/index.rdf",        # CNET Japan
    "https://japanese.engadget.com/rss.xml"        # Engadget Japan (念のため)
]

# RSSフィードの信頼性を考慮して選定
TECH_RSS_URLS = [
    "https://www.publickey1.jp/atom.xml",
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
    "https://www.gizmodo.jp/index.xml",
    "https://japan.cnet.com/rss/index.rdf",
]

# ネガティブなキーワード（除外対象）
NEGATIVE_KEYWORDS = [
    '死亡', '死去', '事故', '爆発', '火災', '逮捕', '容疑', '殺人', 
    '遺体', '負傷', '重体', '被害', '崩壊', '墜落', '衝突', '戦争',
    '地震', '津波', '台風', '災害', '被災', '犠牲', '訃報', '急死',
    'はねられ', '意識不明', '救急搬送', '重傷', '軽傷', '不明',
    '炎上', '謝罪', '不正', '流出' # テック系でのネガティブワード追加
]

def is_negative_news(title: str, summary: str) -> bool:
    """ニュースがネガティブかどうかを判定"""
    text = title + summary
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text:
            return True
    return False

def fetch_latest_news(limit: int = 5) -> List[Dict[str, str]]:
    """
    複数のテック系RSSからニュースを取得し、まとめて返す。
    
    Args:
        limit (int): 取得する記事の最大数
        
    Returns:
        List[Dict]: ニュース情報のリスト
    """
    all_news = []
    
    # ランダムにRSSを選んで負荷分散しつつ、多様なソースを混ぜる
    # 毎回すべてのRSSを見るのは時間がかかるので、ランダムに3つ選ぶ
    selected_feeds = random.sample(TECH_RSS_URLS, min(3, len(TECH_RSS_URLS)))
    
    for url in selected_feeds:
        try:
            print(f"Fetching RSS: {url}")
            feed = feedparser.parse(url)
            
            # 各フィードから最新3件を取得
            for entry in feed.entries[:3]:
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                # HTMLタグ除去などのクリーニングが必要な場合があるが、簡易的に取得
                summary = entry.get('summary', '') or entry.get('description', '')
                
                # ネガティブフィルタ
                if is_negative_news(title, summary):
                    continue
                
                news_item = {
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'source': feed.feed.get('title', 'Unknown Source')
                }
                all_news.append(news_item)
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

    if not all_news:
        print("No news found from any source.")
        return []

    # 重複排除（リンクで判定）
    unique_news = {v['link']: v for v in all_news}.values()
    all_news = list(unique_news)

    # ランダムにシャッフルして、指定件数を返す
    # ※最新順にしたい場合はシャッフルしない
    random.shuffle(all_news)
    
    # 最大件数
    result = all_news[:limit]
    
    print(f"Collected {len(result)} news items.")
    for n in result:
        print(f"- {n['title']} ({n['source']})")
        
    return result

if __name__ == "__main__":
    news = fetch_latest_news()
    for n in news:
        print(f"Title: {n['title']}")
        print(f"Link: {n['link']}")
        print(f"Source: {n.get('source', 'Unknown')}")
        print("-" * 20)
