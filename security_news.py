import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import re
import concurrent.futures
from datetime import datetime
import time
from fake_useragent import UserAgent
from deep_translator import GoogleTranslator

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# RSS 채널 리스트
RSS_FEEDS = {
    "🚨 Critical Threats": [
        {"title": "CISA Alerts", "url": "https://www.cisa.gov/uscert/ncas/alerts.xml", "lang": "en"},
        {"title": "MS Security", "url": "https://www.microsoft.com/security/blog/feed/", "lang": "en"},
    ],
    "🌍 Global Intelligence": [
        {"title": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews", "lang": "en"},
        {"title": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/", "lang": "en"},
    ],
    "🇰🇷 Korea Security": [
        {"title": "보안뉴스", "url": "https://www.boannews.com/media/news_rss.xml", "lang": "ko"},
        {"title": "데일리시큐", "url": "https://www.dailysecu.com/rss/allArticle.xml", "lang": "ko"},
    ]
}

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

def fetch_single_feed(feed):
    session = create_session()
    try:
        resp = session.get(feed['url'], timeout=15, verify=False)
        parsed = feedparser.parse(resp.content)
        if not parsed.entries: parsed = feedparser.parse(resp.text)
        if not parsed.entries: return [], f"⚠️ 빈 피드: {feed['title']}"
        
        processed = []
        for entry in parsed.entries[:2]:
            title = entry.title; link = entry.link
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
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = f"# 🛡️ Security Briefing Release ({now_str})\n\n"
    
    for category, feeds in RSS_FEEDS.items():
        md += f"## {category}\n"
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed): feed for feed in feeds}
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, name = future.result()
                if entries: results.append((name, entries))
            
            results.sort(key=lambda x: x[0])
            for name, entries in results:
                md += f"### {name}\n"
                for item in entries:
                    tag_str = " ".join([f"`{t}`" for t in item['tags']])
                    md += f"- **[{item['title']}]({item['link']})**\n"
                    if tag_str: md += f"  - {tag_str}\n"
                    if item['summary']: md += f"  - {item['summary']}\n"
                    md += "\n"
        md += "---\n"
    
    with open("hourly_security_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✨ Released in {time.time()-start:.2f}s")

if __name__ == "__main__":
    main()
