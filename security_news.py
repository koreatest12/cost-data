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

# 설정
DB_DIR = "DB"
HISTORY_FILE = os.path.join(DB_DIR, "seen_urls.json")
TOTAL_LOG_FILE = os.path.join(DB_DIR, "total_news_history.md")
HOURLY_REPORT_FILE = "hourly_security_report.md"

# RSS 채널
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

def init_db():
    if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f: return set(json.load(f))
    return set()

def save_history(urls):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f: json.dump(list(urls), f, indent=4)

def append_to_total_log(content):
    if not os.path.exists(TOTAL_LOG_FILE):
        with open(TOTAL_LOG_FILE, 'w', encoding='utf-8') as f: f.write("# 📚 Total Security News History\n\n")
    with open(TOTAL_LOG_FILE, 'a', encoding='utf-8') as f: f.write(content)

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
    return tags

def fetch_single_feed(feed, seen_urls):
    session = create_session()
    try:
        resp = session.get(feed['url'], timeout=15, verify=False)
        parsed = feedparser.parse(resp.content)
        if not parsed.entries: parsed = feedparser.parse(resp.text)
        if not parsed.entries: return [], f"⚠️ 빈 피드: {feed['title']}"
        
        processed = []
        for entry in parsed.entries[:5]:
            link = entry.link
            if link in seen_urls: continue
            
            title = entry.title
            summary = clean_html(getattr(entry, 'summary', ''))
            tags = get_tags(title + " " + summary)
            
            if feed.get('lang') == 'en':
                title = f"[번역] {translate_text(title)}"
                if summary: summary = translate_text(summary[:150]) + "..."
            
            processed.append({"title": title, "link": link, "summary": summary, "tags": tags})
        return processed, feed['title']
    except Exception as e: return [], f"❌ 오류: {feed['title']}"

def main():
    start = time.time()
    init_db()
    seen_urls = load_history()
    before_count = len(seen_urls)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 임시 저장소
    news_content = ""
    log_buffer = f"\n## 📅 {now_str} Updates\n"
    total_new_count = 0
    
    for category, feeds in RSS_FEEDS.items():
        cat_buffer = ""
        has_cat_news = False
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed, seen_urls): feed for feed in feeds}
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, name = future.result()
                if entries: results.append((name, entries))
            
            results.sort(key=lambda x: x[0])
            for name, entries in results:
                has_cat_news = True
                cat_buffer += f"#### {name}\n"
                for item in entries:
                    seen_urls.add(item['link'])
                    total_new_count += 1
                    
                    tag_str = " ".join([f"`{t}`" for t in item['tags']])
                    item_md = f"- **[{item['title']}]({item['link']})**\n"
                    if tag_str: item_md += f"  - {tag_str}\n"
                    if item['summary']: item_md += f"  - {item['summary']}\n"
                    item_md += "\n"
                    cat_buffer += item_md
        
        if has_cat_news:
            news_content += f"## {category}\n" + cat_buffer + "---\n"
            log_buffer += f"### {category}\n" + cat_buffer + "---\n"

    elapsed = time.time() - start
    
    # 📊 [핵심] 화면 출력을 위한 대시보드(Summary) 생성
    dashboard = f"""
# 🛡️ Security Briefing Dashboard ({now_str})

| ⏱️ 실행 시간 | 🆕 신규 뉴스 | 📚 총 누적 데이터 |
| :---: | :---: | :---: |
| `{elapsed:.2f}s` | **`{total_new_count}건`** | `{len(seen_urls)}건` |

---
"""
    
    final_report = dashboard + (news_content if total_new_count > 0 else "\n> ✅ **현재 새로운 보안 뉴스가 없습니다.** (모니터링 중)")
    
    # 파일 저장
    if total_new_count > 0:
        save_history(seen_urls)
        append_to_total_log(log_buffer)
    
    with open(HOURLY_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_report)
        
    print(f"✨ Processed: {total_new_count} new articles.")

if __name__ == "__main__":
    main()
