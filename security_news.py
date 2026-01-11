import feedparser
import requests
import re
import concurrent.futures
from datetime import datetime
import time

# ---------------------------------------------------------
# 1. 초대량 보안 뉴스 채널 리스트 (30개 이상 확장)
# ---------------------------------------------------------
RSS_FEEDS = {
    "🇰🇷 국내 엔터프라이즈 및 공공": [
        {"title": "보안뉴스 (BoanNews)", "url": "https://www.boannews.com/media/news_rss.xml"},
        {"title": "데일리시큐 (DailySecu)", "url": "https://www.dailysecu.com/rss/allArticle.xml"},
        {"title": "ITWorld Korea", "url": "https://www.itworld.co.kr/rss/topics/security"}, 
        {"title": "CIO Korea", "url": "https://www.ciokorea.com/rss/topics/security"},
        {"title": "KISA 보호나라 (공지사항)", "url": "https://www.krcert.or.kr/rss/feed.do?feedType=1"}, 
    ],
    "🌍 글로벌 탑 티어 (Must Read)": [
        {"title": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
        {"title": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
        {"title": "Dark Reading", "url": "https://www.darkreading.com/rss.xml"},
        {"title": "TechCrunch Security", "url": "https://techcrunch.com/category/security/feed/"},
        {"title": "Wired Security", "url": "https://www.wired.com/feed/category/security/latest/rss"},
    ],
    "🏢 빅테크 & 벤더 블로그": [
        {"title": "Microsoft Security", "url": "https://www.microsoft.com/security/blog/feed/"},
        {"title": "Google Online Security", "url": "https://security.googleblog.com/feeds/posts/default"},
        {"title": "AWS Security Blog", "url": "https://aws.amazon.com/blogs/security/feed/"},
        {"title": "Cloudflare Blog", "url": "https://blog.cloudflare.com/rss/"},
        {"title": "CrowdStrike Blog", "url": "https://www.crowdstrike.com/blog/feed/"},
    ],
    "🐛 취약점 & 악성코드 분석 (Deep Dive)": [
        {"title": "Trend Micro Research", "url": "https://feeds.feedburner.com/TrendMicroResearch"},
        {"title": "Malwarebytes Labs", "url": "https://blog.malwarebytes.com/feed/"},
        {"title": "Securelist (Kaspersky)", "url": "https://securelist.com/feed/"},
        {"title": "Exploit-DB", "url": "https://www.exploit-db.com/rss.xml"},
        {"title": "US-CERT (CISA)", "url": "https://www.cisa.gov/uscert/ncas/current-activity.xml"},
    ]
}

# ---------------------------------------------------------
# 2. 고급 설정: 봇 차단 우회 및 병렬 처리기
# ---------------------------------------------------------
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()[:150] + "..."

def fetch_single_feed(feed):
    """
    개별 피드를 수집하는 함수 (타임아웃 및 예외처리 강화)
    """
    try:
        # requests로 먼저 원본 데이터를 가져옴 (헤더 포함)
        response = requests.get(feed['url'], headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # feedparser에 텍스트 데이터 전달
        parsed = feedparser.parse(response.content)
        
        if not parsed.entries:
            return None, f"⚠️ 데이터 없음: {feed['title']}"
            
        return parsed.entries[:5], feed['title'] # 최신 5개만 반환
        
    except Exception as e:
        return None, f"❌ 접속 실패 ({feed['title']}): {str(e)[:50]}"

# ---------------------------------------------------------
# 3. 메인 실행 로직 (멀티 스레드 적용)
# ---------------------------------------------------------
def main():
    start_time = time.time()
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    final_report = f"# 🛡️ {today} 대용량 보안 인텔리전스 리포트\n"
    final_report += f"> 🚀 시스템: 고성능 병렬 수집 엔진 가동\n\n"
    
    total_count = 0
    
    # 카테고리별 루프
    for category, feeds in RSS_FEEDS.items():
        final_report += f"## {category}\n"
        print(f"\n📂 Processing Category: {category}")
        
        # 병렬 처리 (ThreadPoolExecutor) - 동시에 여러 사이트 접속
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed): feed for feed in feeds}
            
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, msg_or_title = future.result()
                if entries:
                    results.append((msg_or_title, entries)) # 성공
                    print(f"  ✅ Fetched: {msg_or_title}")
                else:
                    print(f"  {msg_or_title}") # 실패 메시지 출력

            # 결과 정렬 및 리포트 작성
            if not results:
                final_report += "> *이 카테고리에서 수집된 뉴스가 없습니다.*\n\n"
            
            for title, entries in results:
                final_report += f"<details><summary><b>{title}</b> ({len(entries)})</summary>\n\n"
                for entry in entries:
                    summary = clean_html(getattr(entry, 'summary', getattr(entry, 'description', '')))
                    pub_date = getattr(entry, 'published', '')[:16]
                    final_report += f"- **[{entry.title}]({entry.link})** <br> <sub>⏱️ {pub_date} | {summary}</sub>\n\n"
                    total_count += 1
                final_report += "</details>\n"
        
        final_report += "\n---\n"

    elapsed_time = time.time() - start_time
    footer = f"\n✅ **총 {total_count}개 기사 수집 완료** (소요 시간: {elapsed_time:.2f}초)"
    print(footer)
    final_report += footer
    
    # 파일 저장
    with open("daily_security_report.md", "w", encoding="utf-8") as f:
        f.write(final_report)

if __name__ == "__main__":
    main()
