import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import re
import concurrent.futures
from datetime import datetime
import time

# ---------------------------------------------------------
# 🚨 SSL 경고 메시지 무시 설정 (KISA 등 정부 사이트 접속용)
# ---------------------------------------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------
# 1. 초대량 보안 뉴스 채널 (URL 최신화 및 검증 완료)
# ---------------------------------------------------------
RSS_FEEDS = {
    "🇰🇷 국내 엔터프라이즈 및 공공": [
        {"title": "보안뉴스", "url": "https://www.boannews.com/media/news_rss.xml"},
        {"title": "데일리시큐", "url": "https://www.dailysecu.com/rss/allArticle.xml"},
        # ITWorld/CIO는 봇 차단이 심하므로 브라우저처럼 위장 필수
        {"title": "ITWorld Security", "url": "https://www.itworld.co.kr/rss/topics/security"}, 
        {"title": "CIO Korea Security", "url": "https://www.ciokorea.com/rss/topics/security"},
        # KISA는 SSL 인증서 문제로 verify=False 옵션 필수
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
        # CISA URL 업데이트
        {"title": "US-CERT (CISA Alerts)", "url": "https://www.cisa.gov/uscert/ncas/alerts.xml"},
    ]
}

# ---------------------------------------------------------
# 2. 강력한 네트워크 세션 생성 (재시도 로직 포함)
# ---------------------------------------------------------
def create_session():
    session = requests.Session()
    
    # 봇 차단 우회를 위한 리얼 브라우저 헤더
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
    })

    # 실패 시 3회 재시도 (Retry) 설정
    retry_strategy = Retry(
        total=3,
        backoff_factor=1, # 1초 대기 후 재시도
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()[:180] + "..."

def fetch_single_feed(feed):
    session = create_session()
    try:
        # verify=False: KISA 등 SSL 인증서 오류 무시
        # timeout=20: 응답 느린 사이트 대기
        response = session.get(feed['url'], timeout=20, verify=False)
        response.raise_for_status()
        
        # 바이너리 컨텐츠로 파싱 (인코딩 문제 해결)
        parsed = feedparser.parse(response.content)
        
        if not parsed.entries:
            # RSS 파싱 실패 시 텍스트로 재시도
            parsed = feedparser.parse(response.text)
        
        if not parsed.entries:
            return None, f"⚠️ 데이터 없음 (구조 변경됨): {feed['title']}"
            
        return parsed.entries[:5], feed['title']

    except requests.exceptions.SSLError:
        return None, f"❌ SSL 오류: {feed['title']}"
    except requests.exceptions.ConnectionError:
        return None, f"❌ 연결 거부: {feed['title']}"
    except requests.exceptions.Timeout:
        return None, f"⏰ 시간 초과: {feed['title']}"
    except Exception as e:
        return None, f"❌ 오류 발생 ({feed['title']}): {str(e)[:50]}"

# ---------------------------------------------------------
# 3. 메인 실행
# ---------------------------------------------------------
def main():
    start_time = time.time()
    today = datetime.now().strftime("%Y년 %m월 %d일")
    report = f"# 🛡️ {today} 엔터프라이즈 보안 브리핑\n\n"
    report += f"> 🔍 상태: 봇 탐지 우회 및 SSL 예외 처리 적용됨\n\n"
    
    total_count = 0
    
    for category, feeds in RSS_FEEDS.items():
        report += f"## {category}\n"
        print(f"📂 Category: {category}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed): feed for feed in feeds}
            
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, title_or_msg = future.result()
                if entries:
                    results.append((title_or_msg, entries))
                    print(f"  ✅ 성공: {title_or_msg}")
                else:
                    print(f"  {title_or_msg}")

            # 리포트 작성
            if not results:
                report += "> 수집된 뉴스가 없습니다.\n\n"
            
            # 결과 정렬 (제목 가나다순)
            results.sort(key=lambda x: x[0])
            
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
    print(f"\n✅ 최종 집계: {total_count}개 기사 수집 완료 ({elapsed:.2f}초)")
    
    with open("daily_security_report.md", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()
