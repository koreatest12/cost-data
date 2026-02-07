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

# [✅ Massive Feeds: 40개 이상의 초대형 소스 정의]
FEEDS = {
    "PORTAL_KEYWORD": [
        # Google News RSS (네이버/다음 우회) - 검색어: 해킹, 보안, 취약점
        ("Naver/Portal Security", "https://news.google.com/rss/search?q=해킹+보안+취약점+site:naver.com&hl=ko&gl=KR&ceid=KR:ko"),
        ("Cyber Crime News", "https://news.google.com/rss/search?q=사이버범죄+피싱+스미싱&hl=ko&gl=KR&ceid=KR:ko"),
        ("Financial Security", "https://news.google.com/rss/search?q=금융보안+은행+해킹&hl=ko&gl=KR&ceid=KR:ko"),
    ],
    "GLOBAL_TIER_1": [
        ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("Dark Reading", "https://www.darkreading.com/rss.xml"),
        ("SecurityWeek", "https://feeds.feedburner.com/SecurityWeek"),
        ("TechCrunch Security", "https://techcrunch.com/category/security/feed/"),
        ("Wired Security", "https://www.wired.com/feed/category/security/latest/rss"),
    ],
    "CLOUD_&_VENDOR": [
        ("AWS Security Blog", "https://aws.amazon.com/blogs/security/feed/"),
        ("Microsoft Security", "https://api.msrc.microsoft.com/update-guide/rss"),
        ("Google Project Zero", "https://googleprojectzero.blogspot.com/feeds/posts/default"),
        ("Palo Alto Unit 42", "https://unit42.paloaltonetworks.com/feed/"),
        ("Cloudflare Blog", "https://blog.cloudflare.com/rss/"),
        ("Kaspersky Securelist", "https://securelist.com/feed/"),
        ("Trellix (McAfee)", "https://www.trellix.com/en-us/about/newsroom/stories.rss"),
        ("Cisco Talos", "https://blog.talosintelligence.com/rss/"),
    ],
    "KOREA_OFFICIAL": [
        ("BoanNews", "https://www.boannews.com/media/news_rss.xml"),
        ("AhnLab ASEC", "https://asec.ahnlab.com/ko/feed/"),
        ("DailySecu", "https://www.dailysecu.com/rss/all.xml"),
        ("KISA KrCERT", "https://www.krcert.or.kr/rss/rss.do"), 
        ("ETNews Security", "https://rss.etnews.com/Section902.xml"),
        ("Digital Daily", "https://www.ddaily.co.kr/rss/?sc=10300001"),
        ("Byline Network", "https://byline.network/category/security/feed/"),
        ("InforStock (Security)", "https://www.inforstock.co.kr/rss/S1N8.xml"),
    ]
}

# [✅ Advanced WAF Bypass: 헤더 시뮬레이션 강화]
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/122.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
]

def clean_xml_content(raw_str):
    if not raw_str: return ""
    # XML 선언 및 HTML 태그 제거
    cleaned = re.sub(r'<\?xml.*?\?>', '', raw_str)
    if "<!DOCTYPE html" in cleaned or "<html" in cleaned: return None
    # 특수 엔티티 처리
    cleaned = re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#x[0-9a-fA-F]+);)', '&amp;', cleaned)
    return cleaned.strip()

def fetch_feed_content(url, retries=3):
    for attempt in range(retries + 1):
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://www.google.com/'
        }
        
        try:
            # 랜덤 딜레이로 봇 탐지 회피
            time.sleep(random.uniform(0.5, 2.5))
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as response:
                raw_data = response.read()
                
                decoded_data = None
                for enc in ['utf-8', 'euc-kr', 'cp949', 'latin-1']:
                    try:
                        decoded_data = raw_data.decode(enc)
                        break
                    except: continue
                
                if not decoded_data: return None
                
                cleaned = clean_xml_content(decoded_data)
                if cleaned is None:
                    # HTML이 반환되면 WAF 차단으로 간주
                    if attempt < retries: continue
                    return None
                return cleaned

        except Exception as e:
            pass
    return None

def parse_feeds():
    collected_news = []
    stats = {"total": 0, "categories": {}}

    print(f"🔥 Starting Gemini Massive Collection from {sum(len(v) for v in FEEDS.values())} sources...")

    for category, feeds in FEEDS.items():
        stats["categories"][category] = 0
        print(f"\n📡 Scanning Category: [{category}]")
        
        for name, url in feeds:
            xml_str = fetch_feed_content(url)
            if not xml_str: 
                print(f"   ❌ {name}: Blocked/Failed")
                continue

            try:
                # 네임스페이스 제거
                xml_str = re.sub(r'\sxmlns="[^"]+"', '', xml_str, count=1)
                root = ET.fromstring(xml_str)
                items = root.findall('.//item') + root.findall('.//entry')
                count = 0
                
                # [✅ 초대량 수집: 소스당 20개까지 확장]
                for item in items[:20]:
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
                print(f"   ⚠️ {name}: XML Parse Error")

    return collected_news, stats

def save_data(news_data, stats):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Main JSON
    json_path = f"data/news/news_{today}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "meta": {"date": today, "timestamp": timestamp, "stats": stats},
            "articles": news_data
        }, f, ensure_ascii=False, indent=2)

    # Index JSON
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
