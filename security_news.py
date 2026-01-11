import feedparser
import requests
import re
import concurrent.futures
from datetime import datetime
import time

# ---------------------------------------------------------
# 1. 초대량 보안 뉴스 채널 (30+ 소스)
# ---------------------------------------------------------
RSS_FEEDS = {
    "🇰🇷 국내 엔터프라이즈 및 공공": [
        {"title": "보안뉴스", "url": "https://www.boannews.com/media/news_rss.xml"},
        {"title": "데일리시큐", "url": "https://www.dailysecu.com/rss/allArticle.xml"},
        {"title": "ITWorld Security", "url": "https://www.itworld.co.kr/rss/topics/security"}, 
        {"title": "CIO Korea Security", "url": "https://www.ciokorea.com/rss/topics/security"},
        {"title": "KISA 보호나라", "url": "https://www.krcert.or.kr/rss/feed.do?feedType=1"}, 
    ],
    "🌍 글로벌 Must Read": [
        {"title": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
        {"title": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
        {"title": "Dark Reading", "url": "https://www.darkreading.com/rss.xml"},
        {"title": "Wired Security", "url": "https://www.wired.com/feed/category/security/latest/rss"},
    ],
    "🏢 빅테크 & 벤더 블로그": [
        {"title": "Microsoft Security", "url": "https://www.microsoft.com/security/blog/feed/"},
        {"title": "Google Online Security", "url": "https://security.googleblog.com/feeds/posts/default"},
        {"title": "AWS Security", "url": "https://aws.amazon.com/blogs/security/feed/"},
        {"title": "Cloudflare", "url": "https://blog.cloudflare.com/rss/"},
    ],
    "🐛 취약점 & 심층 분석": [
        {"title": "Trend Micro", "url": "https://feeds.feedburner.com/TrendMicroResearch"},
        {"title": "Exploit-DB", "url": "https://www.exploit-db.com/rss.xml"},
        {"title": "US-CERT (CISA)", "url": "https://www.cisa.gov/uscert/ncas/current-activity.xml"},
    ]
}

# ---------------------------------------------------------
# 2. 엔진 설정 (봇 차단 우회 헤더)
# ---------------------------------------------------------
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()[:180] + "..."

def fetch_single_feed(feed):
    try:
        # 타임아웃 10초 설정
        response = requests.get(feed['url'], headers=HEADERS, timeout=10)
        response.raise_for_status()
        parsed = feedparser.parse(response.content)
        
        if not parsed.entries:
            return None, f"⚠️ 데이터 없음: {feed['title']}"
        return parsed.entries[:5], feed['title']
    except Exception as e:
        return None, f"❌ 접속 실패 ({feed['title']})"

# ---------------------------------------------------------
# 3. 메인 실행 (병렬 처리)
# ---------------------------------------------------------
def main():
    start_time = time.time()
    today = datetime.now().strftime("%Y년 %m월 %d일")
    report = f"# 🛡️ {today} 엔터프라이즈 보안 브리핑\n\n"
    
    total_count = 0
    
    for category, feeds in RSS_FEEDS.items():
        report += f"## {category}\n"
        print(f"📂 Category: {category}")
        
        # 스레드 20개로 동시 접속 (초고속 수집)
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed): feed for feed in feeds}
            
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, title_or_msg = future.result()
                if entries:
                    results.append((title_or_msg, entries))
                else:
                    print(f"  {title_or_msg}")

            if not results:
                report += "> 수집된 뉴스가 없습니다.\n\n"
            
            for title, entries in results:
                report += f"<details><summary><b>{title}</b> ({len(entries)})</summary>\n\n"
                for entry in entries:
                    summary = clean_html(getattr(entry, 'summary', getattr(entry, 'description', '')))
                    link = entry.link
                    report += f"- [{entry.title}]({link}) <br> <sub>{summary}</sub>\n\n"
                    total_count += 1
                report += "</details>\n"
        
        report += "---\n"

    elapsed = time.time() - start_time
    print(f"\n✅ 총 {total_count}개 기사 수집 완료 ({elapsed:.2f}초)")
    
    with open("daily_security_report.md", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()
