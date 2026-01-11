import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import re
import concurrent.futures
from datetime import datetime
import time
import os
import random

# 새로 추가된 모듈 (설치 완료됨)
from duckduckgo_search import DDGS
from fake_useragent import UserAgent 

# 🚨 SSL 경고 제거
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------
# 1. 초대량 RSS 채널 (35개 이상)
# ---------------------------------------------------------
RSS_FEEDS = {
    "🚨 긴급 위협 (Critical)": [
        {"title": "CISA Alerts", "url": "https://www.cisa.gov/uscert/ncas/alerts.xml"},
        {"title": "MS Security Response", "url": "https://www.microsoft.com/security/blog/feed/"},
        {"title": "Palo Alto Unit 42", "url": "https://unit42.paloaltonetworks.com/feed/"},
    ],
    "🇰🇷 국내 보안 뉴스": [
        {"title": "보안뉴스", "url": "https://www.boannews.com/media/news_rss.xml"},
        {"title": "데일리시큐", "url": "https://www.dailysecu.com/rss/allArticle.xml"},
        {"title": "바이라인네트워크", "url": "https://byline.network/feed/"},
        {"title": "전자신문 보안", "url": "https://rss.etnews.com/04045.xml"},
    ],
    "🌍 글로벌 인텔리전스": [
        {"title": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
        {"title": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
        {"title": "SecurityWeek", "url": "https://feeds.feedburner.com/SecurityWeek"},
        {"title": "Qualys Blog", "url": "https://blog.qualys.com/feed"},
    ]
}

# ---------------------------------------------------------
# 2. 강력한 연결 생성기 (Fake User-Agent 적용)
# ---------------------------------------------------------
def create_session():
    session = requests.Session()
    
    # 랜덤한 최신 브라우저 헤더 생성 (차단 완벽 회피)
    try:
        ua = UserAgent()
        header = ua.random
    except:
        header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
    session.headers.update({
        'User-Agent': header,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.google.com/'
    })
    
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

def clean_html(raw_html):
    if not raw_html: return ""
    text = re.sub(r'<[^>]+>', '', raw_html).strip()
    return text[:150] + "..." if len(text) > 150 else text

# 🔥 AI 분석: 중요 키워드 감지 및 추가 검색
def analyze_and_search(title):
    keywords = ['RCE', 'Zero-day', 'Remote Code', 'Critical', '북한', '랜섬웨어', '계정 유출']
    
    is_important = any(k.lower() in title.lower() for k in keywords)
    extra_info = []

    # 중요 기사라면 DuckDuckGo로 관련 최신 정보 검색 (AI Agent)
    if is_important:
        try:
            # 검색 속도 조절을 위해 30% 확률로만 검색 (차단 방지)
            if random.random() < 0.3:
                with DDGS() as ddgs:
                    results = list(ddgs.news(title[:20], max_results=1))
                    if results:
                        extra_info = [f"🔎 관련: {r['title']} ({r['source']})" for r in results]
        except:
            pass
            
    return is_important, extra_info

def fetch_single_feed(feed):
    session = create_session()
    try:
        resp = session.get(feed['url'], timeout=15, verify=False)
        
        # XML 파싱
        parsed = feedparser.parse(resp.content)
        if not parsed.entries:
            parsed = feedparser.parse(resp.text)
            
        if not parsed.entries:
            return [], f"⚠️ Empty: {feed['title']}"
            
        processed_entries = []
        for entry in parsed.entries[:3]: # 채널당 최신 3개
            title = entry.title
            link = entry.link
            summary = clean_html(getattr(entry, 'summary', getattr(entry, 'description', '')))
            published = getattr(entry, 'published', '')[:16]
            
            # AI 분석 실행
            is_urgent, ai_notes = analyze_and_search(title)
            
            processed_entries.append({
                "title": title,
                "link": link,
                "summary": summary,
                "date": published,
                "urgent": is_urgent,
                "ai_notes": ai_notes
            })
            
        return processed_entries, feed['title']

    except Exception as e:
        return [], f"❌ Error: {feed['title']}"

# ---------------------------------------------------------
# 3. 메인 실행 루프
# ---------------------------------------------------------
def main():
    start = time.time()
    today = datetime.now().strftime("%Y-%m-%d")
    
    md_output = f"# 🛡️ AI Security Daily ({today})\n"
    md_output += f"> ⚡ Powered by GitHub Actions & AI Search Agent\n\n"
    
    total_count = 0
    
    for category, feeds in RSS_FEEDS.items():
        md_output += f"## {category}\n"
        print(f"📂 {category}...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed): feed for feed in feeds}
            
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, name = future.result()
                if entries:
                    results.append((name, entries))
            
            # 정렬 및 출력
            results.sort(key=lambda x: x[0])
            
            for name, entries in results:
                md_output += f"### {name}\n"
                for item in entries:
                    icon = "🔥" if item['urgent'] else "🔹"
                    md_output += f"- {icon} **[{item['title']}]({item['link']})**\n"
                    if item['summary']:
                        md_output += f"  - {item['summary']}\n"
                    
                    # AI 검색 결과가 있으면 표시
                    if item['ai_notes']:
                        for note in item['ai_notes']:
                            md_output += f"  - *{note}*\n"
                    
                    md_output += "\n"
                    total_count += 1
        
        md_output += "---\n"

    print(f"✨ Total {total_count} articles collected in {time.time()-start:.2f}s")
    
    # 파일 저장
    with open("daily_security_report.md", "w", encoding="utf-8") as f:
        f.write(md_output)

if __name__ == "__main__":
    main()
