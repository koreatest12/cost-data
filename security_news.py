import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import re
import concurrent.futures
from datetime import datetime
import time
import random
from fake_useragent import UserAgent
from duckduckgo_search import DDGS
from deep_translator import GoogleTranslator # 🔥 번역 기능 추가

# 🚨 SSL 경고 제거
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------
# 1. 감시 채널 리스트 (글로벌/국내 통합)
# ---------------------------------------------------------
RSS_FEEDS = {
    "🚨 긴급 위협 (Critical)": [
        {"title": "CISA Alerts", "url": "https://www.cisa.gov/uscert/ncas/alerts.xml", "lang": "en"},
        {"title": "MS Security", "url": "https://www.microsoft.com/security/blog/feed/", "lang": "en"},
        {"title": "Palo Alto Unit 42", "url": "https://unit42.paloaltonetworks.com/feed/", "lang": "en"},
    ],
    "🌍 글로벌 인텔리전스 (자동 번역)": [
        {"title": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews", "lang": "en"},
        {"title": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/", "lang": "en"},
        {"title": "SecurityWeek", "url": "https://feeds.feedburner.com/SecurityWeek", "lang": "en"},
    ],
    "🇰🇷 국내 보안 뉴스": [
        {"title": "보안뉴스", "url": "https://www.boannews.com/media/news_rss.xml", "lang": "ko"},
        {"title": "데일리시큐", "url": "https://www.dailysecu.com/rss/allArticle.xml", "lang": "ko"},
        {"title": "바이라인네트워크", "url": "https://byline.network/feed/", "lang": "ko"},
    ]
}

# ---------------------------------------------------------
# 2. 유틸리티: 세션, 번역, 태깅
# ---------------------------------------------------------
def create_session():
    session = requests.Session()
    try:
        ua = UserAgent()
        header = ua.random
    except:
        header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
        
    session.headers.update({'User-Agent': header, 'Referer': 'https://www.google.com/'})
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

def clean_html(raw_html):
    if not raw_html: return ""
    text = re.sub(r'<[^>]+>', '', raw_html).strip()
    return text[:200] + "..." if len(text) > 200 else text

# 🔥 [New] 영어 -> 한국어 자동 번역
def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text)
    except:
        return text # 실패 시 원문 반환

# 🔥 [New] 스마트 태깅 (공격 유형 분류)
def get_tags(text):
    text = text.lower()
    tags = []
    if 'ransomware' in text or '랜섬웨어' in text: tags.append("💰랜섬웨어")
    if 'vulnerability' in text or '취약점' in text or 'cve' in text: tags.append("🐛취약점")
    if 'phishing' in text or '피싱' in text: tags.append("🎣피싱")
    if 'breach' in text or 'leak' in text or '유출' in text: tags.append("💧데이터유출")
    if 'zero-day' in text or '제로데이' in text: tags.append("🚨제로데이")
    if 'north korea' in text or '북한' in text: tags.append("🇰🇵북한위협")
    
    return tags

# ---------------------------------------------------------
# 3. 뉴스 수집 및 처리 (병렬)
# ---------------------------------------------------------
def fetch_single_feed(feed):
    session = create_session()
    try:
        resp = session.get(feed['url'], timeout=15, verify=False)
        parsed = feedparser.parse(resp.content)
        if not parsed.entries: parsed = feedparser.parse(resp.text)
        if not parsed.entries: return [], f"⚠️ 빈 피드: {feed['title']}"
        
        processed = []
        # 최신 2개만 수집 (매 시간 실행이므로 최신 정보만 필요)
        for entry in parsed.entries[:2]:
            title = entry.title
            link = entry.link
            summary = clean_html(getattr(entry, 'summary', ''))
            
            # 1. 스마트 태깅
            tags = get_tags(title + " " + summary)
            
            # 2. 글로벌 뉴스는 한국어로 번역 (AI Translation)
            if feed.get('lang') == 'en':
                title = f"[번역] {translate_text(title)}"
                # 요약문 번역은 시간이 걸리므로 짧게 처리
                if summary: summary = translate_text(summary[:150]) + "..."
            
            processed.append({
                "title": title,
                "link": link,
                "summary": summary,
                "tags": tags
            })
            
        return processed, feed['title']

    except Exception as e:
        return [], f"❌ 오류: {feed['title']}"

# ---------------------------------------------------------
# 4. 메인 실행
# ---------------------------------------------------------
def main():
    start = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    md = f"# 🛡️ 실시간 AI 보안 브리핑 ({now_str})\n"
    md += f"> 🔄 상태: 매 시간 감시 중 | 🇰🇷 자동 번역: 활성화됨\n\n"
    
    total_count = 0
    
    for category, feeds in RSS_FEEDS.items():
        md += f"## {category}\n"
        print(f"📂 Scanning: {category}...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed): feed for feed in feeds}
            
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, name = future.result()
                if entries: results.append((name, entries))
            
            if not results:
                md += "> *최근 1시간 내 업데이트 없음*\n\n"
                continue
                
            results.sort(key=lambda x: x[0])
            
            for name, entries in results:
                md += f"### {name}\n"
                for item in entries:
                    # 태그 출력
                    tag_str = " ".join([f"`{t}`" for t in item['tags']])
                    
                    md += f"- **[{item['title']}]({item['link']})**\n"
                    if tag_str:
                        md += f"  - {tag_str}\n"
                    if item['summary']:
                        md += f"  - {item['summary']}\n"
                    md += "\n"
                    total_count += 1
        md += "---\n"

    print(f"✨ Total {total_count} articles in {time.time()-start:.2f}s")
    
    with open("hourly_security_report.md", "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    main()
