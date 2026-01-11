import feedparser
from datetime import datetime

# 수집할 보안 뉴스 RSS 피드 목록 (필요에 따라 추가/변경 가능)
RSS_FEEDS = [
    {
        "title": "KISA 보호나라 (보안공지)",
        "url": "https://www.krcert.or.kr/rss/feed.do?feedType=1" # 예시 URL
    },
    {
        "title": "The Hacker News (Global)",
        "url": "https://feeds.feedburner.com/TheHackersNews"
    },
    {
        "title": "Daily Secu (국내)",
        "url": "https://www.dailysecu.com/rss/allArticle.xml"
    }
]

def fetch_news():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    report = f"# 🛡️ {today} 일일 보안 뉴스 브리핑\n\n"
    
    for feed in RSS_FEEDS:
        print(f"Fetching: {feed['title']}...")
        parsed_feed = feedparser.parse(feed['url'])
        
        report += f"## 📰 {feed['title']}\n"
        
        # 각 피드에서 최신 글 5개만 가져오기
        for entry in parsed_feed.entries[:5]:
            title = entry.title
            link = entry.link
            # 요약이 있다면 가져오기 (없으면 제목만)
            summary = getattr(entry, 'summary', '요약 내용 없음')[:100] + "..." 
            
            report += f"- **[{title}]({link})**\n"
            report += f"  - {summary}\n\n"
        
        report += "---\n\n"
    
    return report

if __name__ == "__main__":
    news_report = fetch_news()
    
    # 결과를 파일로 저장 (GitHub Actions에서 이슈 본문으로 사용)
    with open("daily_security_report.md", "w", encoding="utf-8") as f:
        f.write(news_report)
    
    print("✅ 보안 뉴스 리포트 생성 완료")
