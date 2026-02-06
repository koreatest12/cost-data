import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import datetime
import json
import os
import re
import sys
import time

# 1. RSS 피드 목록 정의
FEEDS = {
    "global": [
        ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("SecurityWeek", "https://feeds.feedburner.com/SecurityWeek"),
        ("CISA Alerts", "https://www.cisa.gov/uscert/ncas/alerts.xml"),
        ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
        ("Dark Reading", "https://www.darkreading.com/rss.xml"),
    ],
    "korea": [
        ("DailySecu", "https://www.dailysecu.com/rss/all.xml"),
        ("BoanNews", "https://www.boannews.com/media/news_rss.xml"), 
        ("KISA KrCERT", "https://www.krcert.or.kr/rss/rss.do"),
    ]
}

# 2. 인코딩 처리 및 데이터 정제 함수
def fetch_feed_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read()
            
            # [핵심] 인코딩 자동 감지 및 디코딩
            decoded_data = None
            encodings = ['utf-8', 'euc-kr', 'cp949', 'latin-1']
            
            for enc in encodings:
                try:
                    decoded_data = raw_data.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            
            if not decoded_data:
                print(f"    ⚠️ Failed to decode content from {url}")
                return None

            # [핵심] XML 선언부의 인코딩 정보 제거 (파서 충돌 방지)
            # <?xml version="1.0" encoding="EUC-KR"?> 같은 부분을 제거하고 순수 문자열로 파싱
            decoded_data = re.sub(r'<\?xml.*encoding=[\'"].*[\'"].*\?>', '', decoded_data, count=1)
            return decoded_data.strip()
            
    except Exception as e:
        print(f"    ❌ Connection Error ({url}): {e}")
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
                continue

            try:
                # XML 파싱 (문자열로 직접 파싱)
                root = ET.fromstring(xml_str)
                items = root.findall('.//item')
                count = 0
                
                for item in items[:5]: # 피드당 최신 5개만 수집
                    title = item.find('title')
                    link = item.find('link')
                    pubDate = item.find('pubDate')
                    
                    if title is not None and link is not None:
                        news_item = {
                            "source": name,
                            "category": category,
                            "title": title.text.strip() if title.text else "No Title",
                            "link": link.text.strip() if link.text else "#",
                            "date": pubDate.text.strip() if pubDate is not None and pubDate.text else str(datetime.date.today())
                        }
                        collected_news.append(news_item)
                        count += 1
                
                print(f"    -> {count} articles collected")
                if category == 'global': global_cnt += count
                else: korea_cnt += count
                total += count

            except ET.ParseError as e:
                print(f"    ⚠️ XML Parse Error for {name}: {e}")
                continue
            except Exception as e:
                print(f"    ⚠️ Unknown Error for {name}: {e}")
                continue

    return collected_news, total, global_cnt, korea_cnt

def save_data(news_data, total, g_cnt, k_cnt):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. JSON 저장
    json_path = f"data/news/news_{today}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "date": today,
            "timestamp": timestamp,
            "stats": {"total": total, "global": g_cnt, "korea": k_cnt},
            "articles": news_data
        }, f, ensure_ascii=False, indent=2)

    # 2. Markdown DB 업데이트 (History)
    md_path = "DB/total_news_history.md"
    mode = 'a' if os.path.exists(md_path) else 'w'
    with open(md_path, mode, encoding='utf-8') as f:
        if mode == 'w':
            f.write("# 🛡️ Daily Security News History\n\n")
        
        f.write(f"## 📅 {today} ({total} Articles)\n")
        f.write(f"**Updated:** {timestamp} | **Global:** {g_cnt} | **Korea:** {k_cnt}\n\n")
        
        for news in news_data:
            flag = "🌍" if news['category'] == 'global' else "🇰🇷"
            f.write(f"- {flag} **[{news['source']}]** [{news['title']}]({news['link']})\n")
        f.write("\n---\n\n")

    # 3. Index JSON 업데이트 (Dashboard용)
    index_path = "data/news/news_index.json"
    index_data = {"last_updated": timestamp, "dates": []}
    
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except: pass

    # 오늘 날짜 중복 제거 후 추가
    index_data["dates"] = [d for d in index_data.get("dates", []) if d["date"] != today]
    index_data["dates"].insert(0, {
        "date": today,
        "total_articles": total,
        "global_count": g_cnt,
        "korea_count": k_cnt,
        "file": json_path
    })
    index_data["last_updated"] = timestamp
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    # 4. GitHub Actions Output 설정
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as fh:
            fh.write(f"date={today}\n")
            fh.write(f"total_articles={total}\n")
            fh.write(f"global_count={g_cnt}\n")
            fh.write(f"korea_count={k_cnt}\n")

def main():
    print("[Daily Security News Generator]")
    print(f"Timestamp: {datetime.datetime.now()}")
    
    news, total, g_cnt, k_cnt = parse_feeds()
    
    if total > 0:
        save_data(news, total, g_cnt, k_cnt)
        print(f"\n✅ Successfully saved {total} articles.")
    else:
        print("\n⚠️ No news collected. Check connections.")
    
if __name__ == "__main__":
    main()
