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

# [✅ Massive Feeds: 죽은 링크 제거 및 고품질 피드 20종 대량 추가]
FEEDS = {
    "global": [
        ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("Palo Alto Unit 42", "https://unit42.paloaltonetworks.com/feed/"), # Symantec 대체
        ("CISA Alerts", "https://www.cisa.gov/uscert/ncas/alerts.xml"),
        ("Microsoft MSRC", "https://api.msrc.microsoft.com/update-guide/rss"),
        ("Google Project Zero", "https://googleprojectzero.blogspot.com/feeds/posts/default"),
        ("Dark Reading", "https://www.darkreading.com/rss.xml"),
        ("NIST NVD", "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml"),
        ("Schneier on Security", "https://www.schneier.com/feed/atom/"),
        ("Sophos Naked Security", "https://nakedsecurity.sophos.com/feed/"),
        ("Threatpost", "https://threatpost.com/feed/"),
        ("FBI Cyber", "https://www.fbi.gov/feeds/fbi-in-the-news/atom"),
        ("SANS ISC", "https://isc.sans.edu/rssfeed.xml"),
    ],
    "korea": [
        ("BoanNews", "https://www.boannews.com/media/news_rss.xml"),
        ("AhnLab ASEC", "https://asec.ahnlab.com/ko/feed/"),
        ("Datanet", "http://www.datanet.co.kr/rss/S1N8.xml"), # ZDNet 대체
        ("ITWorld Security", "https://www.itworld.co.kr/rss/topic/t/54"), # 추가
        ("DailySecu", "https://www.dailysecu.com/rss/all.xml"), # 404 해결 시도
        ("CIO Korea", "https://www.ciokorea.com/rss/topic/t/29"),
        ("Digital Daily", "https://www.ddaily.co.kr/rss/?sc=10300001"),
    ]
}

# [✅ WAF 우회: 최신 브라우저 헤더 로테이션]
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/122.0',
]

def clean_xml_content(raw_str):
    if not raw_str: return ""
    # XML 선언 제거 & HTML 필터링
    cleaned = re.sub(r'<\?xml.*?\?>', '', raw_str)
    if "<!DOCTYPE html" in cleaned or "<html" in cleaned: return None
    # 엔티티 정제
    cleaned = re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#x[0-9a-fA-F]+);)', '&amp;', cleaned)
    return cleaned.strip()

def fetch_feed_content(url, retries=2):
    for attempt in range(retries + 1):
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Cache-Control': 'no-cache',
            'Referer': 'https://www.google.com'
        }
        try:
            time.sleep(random.uniform(0.5, 2.0)) # 차단 방지 딜레이
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
                if cleaned is None:
                    print(f"    ⚠️ Blocked by WAF (HTML)")
                    continue 
                return cleaned

        except urllib.error.HTTPError as e:
            if e.code == 404: 
                print(f"    ❌ 404 Not Found (Skipping)")
                return None # 404는 재시도 안함
            print(f"    ⚠️ HTTP {e.code} (Retry {attempt+1})")
        except Exception as e:
            print(f"    ⚠️ Error: {e}")
    return None

def parse_feeds():
    collected_news = []
    total = 0
    global_cnt = 0
    korea_cnt = 0

    for category, feeds in FEEDS.items():
        for name, url in feeds:
            print(f"  Fetching [{category}] {name}...")
            xml_str = fetch_feed_content(url)
            if not xml_str: continue

            try:
                xml_str = re.sub(r'\sxmlns="[^"]+"', '', xml_str, count=1)
                root = ET.fromstring(xml_str)
                items = root.findall('.//item') + root.findall('.//entry')
                count = 0
                
                # [✅ 대량 수집: 피드당 최대 10개까지 수집]
                for item in items[:10]:
                    title = item.find('title')
                    link = item.find('link')
                    pubDate = item.find('pubDate') or item.find('updated') or item.find('dc:date', {'dc': 'http://purl.org/dc/elements/1.1/'})
                    
                    link_url = ""
                    if link is not None:
                        link_url = link.attrib.get('href') if 'href' in link.attrib else link.text

                    if title is not None and title.text:
                        news_item = {
                            "source": name,
                            "category": category,
                            "title": html.unescape(title.text.strip()),
                            "link": link_url.strip() if link_url else "#",
                            "date": pubDate.text.strip() if pubDate is not None and pubDate.text else str(datetime.date.today())
                        }
                        collected_news.append(news_item)
                        count += 1
                
                print(f"    -> {count} collected")
                if category == 'global': global_cnt += count
                else: korea_cnt += count
                total += count

            except Exception as e:
                print(f"    ❌ Parse Error: {e}")

    return collected_news, total, global_cnt, korea_cnt

def save_data(news_data, total, g_cnt, k_cnt):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    json_path = f"data/news/news_{today}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "date": today,
            "timestamp": timestamp,
            "stats": {"total": total, "global": g_cnt, "korea": k_cnt},
            "articles": news_data
        }, f, ensure_ascii=False, indent=2)

    index_path = "data/news/news_index.json"
    index_data = {"last_updated": timestamp, "dates": []}
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f: index_data = json.load(f)
        except: pass
    
    index_data["dates"] = [d for d in index_data.get("dates", []) if d["date"] != today]
    index_data["dates"].insert(0, {"date": today, "total": total, "global": g_cnt, "korea": k_cnt})
    index_data["last_updated"] = timestamp
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("[Omni-SOC Massive Collector]")
    news, total, g_cnt, k_cnt = parse_feeds()
    if total > 0:
        save_data(news, total, g_cnt, k_cnt)
        print(f"\n✅ Total {total} Intelligence Collected.")
    else:
        print("⚠️ No data collected.")
