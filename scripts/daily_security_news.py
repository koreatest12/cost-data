import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import datetime
import json
import os
import re
import time
import html
import random
import sys

# [✅ Massive Feeds: 35개 이상의 초대형 소스 정의]
FEEDS = {
    "PORTAL_KEYWORD": [
        # 네이버/다음 등 포털 뉴스 (Google News RSS를 통해 '보안/해킹' 키워드 우회 수집)
        ("Naver/Portal (Security)", "https://news.google.com/rss/search?q=해킹+보안+취약점+site:naver.com&hl=ko&gl=KR&ceid=KR:ko"),
        ("Portal (Cyber Crime)", "https://news.google.com/rss/search?q=사이버범죄+피싱+랜섬웨어&hl=ko&gl=KR&ceid=KR:ko"),
    ],
    "GLOBAL_TIER_1": [
        ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("Dark Reading", "https://www.darkreading.com/rss.xml"),
        ("SecurityWeek", "https://feeds.feedburner.com/SecurityWeek"),
        ("TechCrunch Security", "https://techcrunch.com/category/security/feed/"),
    ],
    "CLOUD_&_VENDOR": [
        ("AWS Security Blog", "https://aws.amazon.com/blogs/security/feed/"),
        ("Microsoft Security", "https://api.msrc.microsoft.com/update-guide/rss"),
        ("Google Project Zero", "https://googleprojectzero.blogspot.com/feeds/posts/default"),
        ("Palo Alto Unit 42", "https://unit42.paloaltonetworks.com/feed/"),
        ("Cloudflare Blog", "https://blog.cloudflare.com/rss/"),
        ("Kaspersky Securelist", "https://securelist.com/feed/"),
        ("Trellix (McAfee)", "https://www.trellix.com/en-us/about/newsroom/stories.rss"),
    ],
    "KOREA_OFFICIAL": [
        ("BoanNews", "https://www.boannews.com/media/news_rss.xml"),
        ("AhnLab ASEC", "https://asec.ahnlab.com/ko/feed/"),
        ("DailySecu", "https://www.dailysecu.com/rss/all.xml"),
        ("KISA KrCERT", "https://www.krcert.or.kr/rss/rss.do"), # WAF 주의
        ("ETNews Security", "https://rss.etnews.com/Section902.xml"),
        ("Digital Daily", "https://www.ddaily.co.kr/rss/?sc=10300001"),
        ("Byline Network", "https://byline.network/category/security/feed/"),
    ]
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def clean_xml_content(raw_str):
    if not raw_str: return ""
    cleaned = re.sub(r'<\?xml.*?\?>', '', raw_str)
    if "<!DOCTYPE html" in cleaned or "<html" in cleaned: return None
    cleaned = re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#x[0-9a-fA-F]+);)', '&amp;', cleaned)
    return cleaned.strip()

def fetch_feed_content(url, retries=2):
    for attempt in range(retries + 1):
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Cache-Control': 'no-cache'
        }
        try:
            time.sleep(random.uniform(0.5, 1.5))
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                raw_data = response.read()
                
                decoded_data = None
                for enc in ['utf-8', 'euc-kr', 'cp949', 'latin-1']:
                    try:
                        decoded_data = raw_data.decode(enc)
                        break
                    except: continue
                
                if not decoded_data: return None
                cleaned = clean_xml_content(decoded_data)
                return cleaned

        except Exception as e:
            pass
    return None

def parse_feeds():
    collected_news = []
    stats = {"total": 0, "categories": {}}

    print(f"🔥 Starting Massive Collection from {sum(len(v) for v in FEEDS.values())} sources...")

    for category, feeds in FEEDS.items():
        stats["categories"][category] = 0
        print(f"\n📡 Scanning Category: [{category}]")
        
        for name, url in feeds:
            xml_str = fetch_feed_content(url)
            if not xml_str: 
                print(f"   ❌ {name}: Connection Failed")
                continue

            try:
                xml_str = re.sub(r'\sxmlns="[^"]+"', '', xml_str, count=1)
                root = ET.fromstring(xml_str)
                items = root.findall('.//item') + root.findall('.//entry')
                count = 0
                
                # [✅ 대량 수집: 소스당 15개까지]
                for item in items[:15]:
                    title = item.find('title')
                    link = item.find('link')
                    pubDate = item.find('pubDate') or item.find('updated') or item.find('dc:date', {'dc': 'http://purl.org/dc/elements/1.1/'})
                    
                    link_url = ""
                    if link is not None:
                        link_url = link.attrib.get('href') if 'href' in link.attrib else link.text

                    if title is not None and title.text:
                        collected_news.append({
                            "source": name,
                            "category": category,
                            "title": html.unescape(title.text.strip()),
                            "link": link_url.strip() if link_url else "#",
                            "date": pubDate.text.strip() if pubDate is not None and pubDate.text else str(datetime.date.today())
                        })
                        count += 1
                
                print(f"   ✅ {name}: {count} articles")
                stats["categories"][category] += count
                stats["total"] += count

            except Exception as e:
                print(f"   ⚠️ {name}: Parse Error")

    return collected_news, stats

def save_data(news_data, stats):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # JSON 저장
    json_path = f"data/news/news_{today}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "meta": {"date": today, "timestamp": timestamp, "stats": stats},
            "articles": news_data
        }, f, ensure_ascii=False, indent=2)

    # Index 업데이트
    index_path = "data/news/news_index.json"
    index_data = {"last_updated": timestamp, "dates": []}
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f: index_data = json.load(f)
        except: pass
    
    index_data["dates"] = [d for d in index_data.get("dates", []) if d["date"] != today]
    index_data["dates"].insert(0, {"date": today, "total": stats["total"], "details": stats["categories"]})
    index_data["last_updated"] = timestamp
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n💾 Data Saved: {json_path} ({stats['total']} articles)")

if __name__ == "__main__":
    news, stats = parse_feeds()
    if stats["total"] > 0:
        save_data(news, stats)
    else:
        print("⚠️ No data collected.")
