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
import json
from fake_useragent import UserAgent
from deep_translator import GoogleTranslator

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------
# 1. 설정 및 저장소 경로
# ---------------------------------------------------------
DB_DIR = "DB"
HISTORY_FILE = os.path.join(DB_DIR, "seen_urls.json")
TOTAL_LOG_FILE = os.path.join(DB_DIR, "total_news_history.md")
HOURLY_REPORT_FILE = "hourly_security_report.md"

# RSS 채널 리스트
RSS_FEEDS = {
    "🚨 Critical Threats": [
        {"title": "CISA Alerts", "url": "https://www.cisa.gov/uscert/ncas/alerts.xml", "lang": "en"},
        {"title": "MS Security", "url": "https://www.microsoft.com/security/blog/feed/", "lang": "en"},
    ],
    "🌍 Global Intelligence": [
        {"title": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews", "lang": "en"},
        {"title": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/", "lang": "en"},
        {"title": "SecurityWeek", "url": "https://feeds.feedburner.com/SecurityWeek", "lang": "en"},
    ],
    "🇰🇷 Korea Security": [
        {"title": "보안뉴스", "url": "https://www.boannews.com/media/news_rss.xml", "lang": "ko"},
        {"title": "데일리시큐", "url": "https://www.dailysecu.com/rss/allArticle.xml", "lang": "ko"},
        {"title": "전자신문 보안", "url": "https://rss.etnews.com/04045.xml", "lang": "ko"},
    ]
}

# ---------------------------------------------------------
# 2. 데이터베이스(DB) 관리 함수
# ---------------------------------------------------------
def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        print(f"📂 Created DB Directory: {DB_DIR}")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_history(urls):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(urls), f, indent=4)

def append_to_total_log(content):
    # 파일이 없으면 헤더 생성
    if not os.path.exists(TOTAL_LOG_FILE):
        with open(TOTAL_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("# 📚 Total Security News History\n\n")
    
    # 내용 이어쓰기 (Append)
    with open(TOTAL_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(content)

# ---------------------------------------------------------
# 3. 유틸리티 함수
# ---------------------------------------------------------
def create_session():
    session = requests.Session()
    try: ua = UserAgent(); header = ua.random
    except: header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    session.headers.update({'User-Agent': header})
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

def clean_html(raw_html):
    if not raw_html: return ""
    text = re.sub(r'<[^>]+>', '', raw_html).strip()
    return text[:200] + "..." if len(text) > 200 else text

def translate_text(text):
    try: return GoogleTranslator(source='auto', target='ko').translate(text)
    except: return text

def get_tags(text):
    text = text.lower()
    tags = []
    if 'ransomware' in text or '랜섬웨어' in text: tags.append("💰랜섬웨어")
    if 'vulnerability' in text or '취약점' in text or 'cve' in text: tags.append("🐛취약점")
    if 'zero-day' in text or '제로데이' in text: tags.append("🚨제로데이")
    if 'exploit' in text or '익스플로잇' in text: tags.append("🔥익스플로잇")
    return tags

# ---------------------------------------------------------
# 4. 뉴스 수집 (중복 필터링 적용)
# ---------------------------------------------------------
def fetch_single_feed(feed, seen_urls):
    session = create_session()
    try:
        resp = session.get(feed['url'], timeout=15, verify=False)
        parsed = feedparser.parse(resp.content)
        if not parsed.entries: parsed = feedparser.parse(resp.text)
        if not parsed.entries: return [], f"⚠️ 빈 피드: {feed['title']}"
        
        processed = []
        # 최신 5개 확인 (중복이 아니면 수집)
        for entry in parsed.entries[:5]:
            link = entry.link
            
            # [중요] 이미 수집한 링크면 건너뜀
            if link in seen_urls:
                continue
                
            title = entry.title
            summary = clean_html(getattr(entry, 'summary', ''))
            tags = get_tags(title + " " + summary)
            
            if feed.get('lang') == 'en':
                title = f"[번역] {translate_text(title)}"
                if summary: summary = translate_text(summary[:150]) + "..."
            
            processed.append({"title": title, "link": link, "summary": summary, "tags": tags})
            
        return processed, feed['title']
    except Exception as e: return [], f"❌ 오류: {feed['title']}"

# ---------------------------------------------------------
# 5. 메인 실행
# ---------------------------------------------------------
def main():
    start = time.time()
    init_db()
    seen_urls = load_history()
    initial_seen_count = len(seen_urls)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 리포트 버퍼 (이번 시간용)
    new_report_md = f"# 🛡️ Security Briefing Release ({now_str})\n\n"
    # 로그 버퍼 (누적용 - 날짜 헤더 포함)
    log_buffer = f"\n## 📅 {now_str} Updates\n"
    
    total_new_count = 0
    
    for category, feeds in RSS_FEEDS.items():
        category_has_news = False
        cat_buffer = f"### {category}\n"
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed, seen_urls): feed for feed in feeds}
            
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, name = future.result()
                if entries:
                    results.append((name, entries))
            
            results.sort(key=lambda x: x[0])
            
            for name, entries in results:
                category_has_news = True
                cat_buffer += f"#### {name}\n"
                for item in entries:
                    seen_urls.add(item['link']) # URL 기록
                    total_new_count += 1
                    
                    tag_str = " ".join([f"`{t}`" for t in item['tags']])
                    item_md = f"- **[{item['title']}]({item['link']})**\n"
                    if tag_str: item_md += f"  - {tag_str}\n"
                    if item['summary']: item_md += f"  - {item['summary']}\n"
                    item_md += "\n"
                    
                    cat_buffer += item_md
        
        if category_has_news:
            new_report_md += f"## {category}\n" + cat_buffer.replace(f"### {category}\n", "") + "---\n"
            log_buffer += cat_buffer + "---\n"

    # 1. 변경사항이 있을 때만 파일 저장
    if total_new_count > 0:
        # DB 저장 (URL 목록)
        save_history(seen_urls)
        
        # 누적 로그 저장 (Total Log)
        append_to_total_log(log_buffer)
        
        # 이번 시간 리포트 저장 (Issue/Release용)
        with open(HOURLY_REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(new_report_md)
            
        print(f"✨ New articles: {total_new_count} (Total DB: {len(seen_urls)})")
    else:
        # 뉴스가 없어도 파일은 만들어야 에러가 안 남 (빈 내용)
        with open(HOURLY_REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# 🛡️ Security Briefing ({now_str})\n\n> ✅ 새로운 보안 뉴스가 없습니다.")
        print("💤 No new articles found.")

    print(f"⏱️ Processed in {time.time()-start:.2f}s")

if __name__ == "__main__":
    main()
