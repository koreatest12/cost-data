import feedparser
from datetime import datetime
import re
import ssl

# SSL 인증서 문제 방지 (오래된 서버 대응)
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# ---------------------------------------------------------
# 1. 대량 보안 뉴스 채널 리스트 (카테고리별 분류)
# ---------------------------------------------------------
RSS_FEEDS = {
    "🇰🇷 국내 주요 보안 뉴스": [
        {"title": "보안뉴스 (BoanNews)", "url": "https://www.boannews.com/media/news_rss.xml"},
        {"title": "데일리시큐 (DailySecu)", "url": "https://www.dailysecu.com/rss/allArticle.xml"},
        {"title": "KISA 보호나라 (보안공지)", "url": "https://www.krcert.or.kr/rss/feed.do?feedType=1"},
        {"title": "ITWorld (Security)", "url": "https://www.itworld.co.kr/rss/topics/security"},
        {"title": "CIO Korea", "url": "https://www.ciokorea.com/rss/topics/security"},
    ],
    "🌍 글로벌 위협 인텔리전스": [
        {"title": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
        {"title": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
        {"title": "Dark Reading", "url": "https://www.darkreading.com/rss.xml"},
        {"title": "Threatpost", "url": "https://threatpost.com/feed/"},
        {"title": "Krebs on Security", "url": "https://krebsonsecurity.com/feed/"},
    ],
    "🐛 취약점 및 기술 분석 (CVE/Exploit)": [
        {"title": "CISA Alerts (US Govt)", "url": "https://www.cisa.gov/uscert/ncas/alerts.xml"},
        {"title": "Google Project Zero", "url": "https://googleprojectzero.blogspot.com/feeds/posts/default"},
        {"title": "Exploit-DB", "url": "https://www.exploit-db.com/rss.xml"},
    ]
}

# ---------------------------------------------------------
# 2. 유틸리티 함수: HTML 태그 제거 및 텍스트 정리
# ---------------------------------------------------------
def clean_html(raw_html):
    if not raw_html:
        return "요약 없음"
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()[:200] + "..." # 너무 길면 200자에서 자름

# ---------------------------------------------------------
# 3. 뉴스 수집 메인 로직
# ---------------------------------------------------------
def fetch_news():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    report = f"# 🛡️ {today} 종합 보안 브리핑\n"
    report += f"> 🕒 업데이트 시간: {datetime.now().strftime('%H:%M:%S')}\n\n"
    
    total_articles = 0

    for category, feeds in RSS_FEEDS.items():
        report += f"## {category}\n"
        
        for feed in feeds:
            print(f"📡 Fetching: {feed['title']}...")
            try:
                parsed_feed = feedparser.parse(feed['url'])
                
                # 피드가 비어있거나 에러가 있는 경우 패스
                if not parsed_feed.entries:
                    print(f"  └─ ⚠️ 데이터 없음: {feed['url']}")
                    continue

                # UI 깔끔하게 하기 위해 접기 기능 사용 (<details>)
                report += f"<details>\n<summary><b>{feed['title']}</b> (최신 {len(parsed_feed.entries[:5])}건)</summary>\n\n"
                
                # 각 피드에서 최신 글 5개만 가져오기 (너무 많으면 이슈 생성 실패함)
                for entry in parsed_feed.entries[:5]:
                    title = entry.title
                    link = entry.link
                    summary_raw = getattr(entry, 'summary', getattr(entry, 'description', ''))
                    summary = clean_html(summary_raw)
                    published = getattr(entry, 'published', '날짜 정보 없음')[:16] # 날짜 포맷 단순화

                    report += f"- **[{title}]({link})** <br> <sub>📅 {published} | {summary}</sub>\n\n"
                    total_articles += 1
                
                report += "</details>\n\n"
            
            except Exception as e:
                print(f"  └─ ❌ Error: {e}")
                report += f"- ⚠️ *{feed['title']} 수집 실패*\n\n"

        report += "---\n"
    
    print(f"\n✅ 총 {total_articles}개의 기사가 수집되었습니다.")
    return report

# ---------------------------------------------------------
# 4. 실행 및 저장
# ---------------------------------------------------------
if __name__ == "__main__":
    news_report = fetch_news()
    
    with open("daily_security_report.md", "w", encoding="utf-8") as f:
        f.write(news_report)
    
    print("📂 daily_security_report.md 파일 생성 완료")
