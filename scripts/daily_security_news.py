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

# [✅ 공식 주소 최신화 & 대량 추가]
FEEDS = {
    "global": [
        ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("CISA Alerts", "https://www.cisa.gov/uscert/ncas/alerts.xml"),
        # MS: 블로그 대신 보안 응답 센터(MSRC) 공식 피드로 교체 (차단 우회)
        ("Microsoft Security Response", "https://api.msrc.microsoft.com/update-guide/rss"),
        ("Google Project Zero", "https://googleprojectzero.blogspot.com/feeds/posts/default"),
        ("Dark Reading", "https://www.darkreading.com/rss.xml"),
        ("NIST NVD", "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml"),
        ("Threatpost", "https://threatpost.com/feed/"),
        ("Trend Micro", "https://www.trendmicro.com/rss/index.xml"),
        ("Symantec", "https://www.broadcom.com/rss/security-response/threats.xml"),
    ],
    "korea": [
        ("BoanNews", "https://www.boannews.com/media/news_rss.xml"),
        ("AhnLab ASEC", "https://asec.ahnlab.com/ko/feed/"),
        # ZDNet: 죽은 링크(404) -> 보안 섹션 메인 RSS로 교체
        ("ZDNet Korea", "https://zdnet.co.kr/rss/sec"),
        ("ETNews", "https://rss.etnews.com/Section902.xml"),
        ("KISA KrCERT", "https://www.krcert.or.kr/rss/rss.do"),
    ]
}

# [✅ 방화벽 우회용 헤더 로테이션]
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.19582'
]

def clean_xml_content(raw_str):
    if not raw_str: return ""
    # 1. XML 선언 제거
    cleaned = re.sub(r'<\?xml.*?\?>', '', raw_str)
    # 2. HTML Doctype 감지 (WAF 차단 페이지 필터링)
    if "<!DOCTYPE" in cleaned or "<html" in cleaned:
        return None
    # 3. 특수문자 및 엔티티 처리
    cleaned = re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#x[0-9a-fA-F]+);)', '&amp;', cleaned)
    return cleaned.strip()

def fetch_feed_content(url, retries=3):
    for attempt in range(retries + 1):
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Referer': 'https://www.google.com/',
            'Cache-Control': 'no-cache'
        }
        try:
            # [✅ 서버 부하 방지용 지연]
            time.sleep(random.uniform(1.0, 3.0))
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as response:
                raw_data = response.read()
                
                # 인코딩 자동 감지 (EUC-KR 대응)
                decoded_data = None
                encodings = ['utf-8', 'euc-kr', 'cp949', 'latin-1']
                for enc in encodings:
                    try:
                        decoded_data = raw_data.decode(enc)
                        break
                    except: continue
                
                if not decoded_data: return None
                
                cleaned = clean_xml_content(decoded_data)
                if cleaned is None:
                    print(f"    ⚠️ Blocked by WAF (HTML Response)")
                    continue # 재시도
                return cleaned

        except Exception as e:
            print(f"    ⚠️ Retry {attempt+1}/{retries}: {e}")
            
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
            
            if not xml_str: 
                print("    ❌ Failed to fetch.")
                continue

            try:
                # XML 네임스페이스 제거 (파싱 오류 방지)
                xml_str = re.sub(r'\sxmlns="[^"]+"', '', xml_str, count=1)
                root = ET.fromstring(xml_str)
                items = root.findall('.//item') + root.findall('.//entry')
                count = 0
                
                for item in items[:5]: # 최신 5건
                    title = item.find('title')
                    link = item.find('link')
                    pubDate = item.find('pubDate') or item.find('updated') or item.find('dc:date', {'dc': 'http://purl.org/dc/elements/1.1/'})
                    
                    # 링크 추출 로직 강화
                    link_url = ""
                    if link is not None:
                        link_url = link.attrib.get('href') if 'href' in link.attrib else link.text

                    if title is not None:
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
    
    # JSON 저장
    json_path = f"data/news/news_{today}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "date": today,
            "timestamp": timestamp,
            "stats": {"total": total, "global": g_cnt, "korea": k_cnt},
            "articles": news_data
        }, f, ensure_ascii=False, indent=2)

    # Index JSON 업데이트
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
        
    print(f"\n✅ Data Saved: {json_path}")

def main():
    print("[Omni-Intelligence SOC Engine]")
    news, total, g_cnt, k_cnt = parse_feeds()
    if total > 0:
        save_data(news, total, g_cnt, k_cnt)
    else:
        print("⚠️ No data collected (Network or WAF issues).")

if __name__ == "__main__":
    main()
