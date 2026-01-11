import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import re
import concurrent.futures
from datetime import datetime
import time

# 🚨 SSL 경고 무시 (일부 구형 서버 대응)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------
# 1. 검증된 초대량 보안 뉴스 채널 리스트 (2026년 최신)
# ---------------------------------------------------------
RSS_FEEDS = {
    "🇰🇷 국내 핵심 보안 뉴스 (Verified)": [
        {"title": "보안뉴스 (BoanNews)", "url": "https://www.boannews.com/media/news_rss.xml"},
        {"title": "데일리시큐 (DailySecu)", "url": "https://www.dailysecu.com/rss/allArticle.xml"},
        {"title": "ZDNet Korea (Security)", "url": "https://zdnet.co.kr/rss/sec"},
        {"title": "전자신문 (Security)", "url": "https://rss.etnews.com/04045.xml"},
        {"title": "디지털데일리 (Security)", "url": "https://www.ddaily.co.kr/rss/?section_id=10"},
    ],
    "🛡️ 국내 위협 인텔리전스 & 분석": [
        {"title": "AhnLab ASEC (대응팀)", "url": "https://asec.ahnlab.com/feed/"},
        {"title": "ESTsecurity (Alyac)", "url": "https://blog.alyac.co.kr/rss"},
        {"title": "Toss Tech (Security)", "url": "https://toss.tech/rss.xml"}, 
    ],
    "🌍 글로벌 Must Read (Top Tier)": [
        {"title": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
        {"title": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
        {"title": "Dark Reading", "url": "https://www.darkreading.com/rss.xml"},
        {"title": "The Register (Security)", "url": "https://www.theregister.com/security/headlines.atom"},
        {"title": "TechCrunch (Security)", "url": "https://techcrunch.com/category/security/feed/"},
    ],
    "🧠 전문가 칼럼 & 심층 분석": [
        {"title": "Schneier on Security", "url": "https://www.schneier.com/feed/atom/"},
        {"title": "SANS Internet Storm Center", "url": "https://isc.sans.edu/rssfeed.xml"},
        {"title": "Krebs on Security", "url": "https://krebsonsecurity.com/feed/"},
        {"title": "Naked Security (Sophos)", "url": "https://news.sophos.com/en-us/category/security-operations/feed/"},
    ],
    "🏢 빅테크 & 벤더 블로그": [
        {"title": "Microsoft Security", "url": "https://www.microsoft.com/security/blog/feed/"},
        {"title": "Google Online Security", "url": "https://security.googleblog.com/feeds/posts/default"},
        {"title": "AWS Security", "url": "https://aws.amazon.com/blogs/security/feed/"},
        {"title": "Cloudflare Blog", "url": "https://blog.cloudflare.com/rss/"},
    ],
    "🐛 취약점 & 익스플로잇 (DB)": [
        {"title": "Exploit-DB", "url": "https://www.exploit-db.com/rss.xml"},
        {"title": "Packet Storm Security", "url": "https://rss.packetstormsecurity.com/news/"},
        {"title": "CISA Alerts (US-CERT)", "url": "https://www.cisa.gov/uscert/ncas/alerts.xml"},
    ]
}

# ---------------------------------------------------------
# 2. 강력한 네트워크 세션 (봇 우회 & 재시도)
# ---------------------------------------------------------
def create_session():
    session = requests.Session()
    # 리얼 브라우저 헤더 (User-Agent 교체)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.google.com/'
    })
    # 재시도 전략 (최대 3회, 403/500 에러 대응)
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[403, 429, 500, 502, 503])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def clean_html(raw_html):
    if not raw_html: return ""
    # HTML 태그 제거 및 길이 제한
    text = re.sub(r'<[^>]+>', '', raw_html).strip()
    return text[:200] + "..." if len(text) > 200 else text

def fetch_single_feed(feed):
    session = create_session()
    try:
        # verify=False로 SSL 인증서 에러 무시
        resp = session.get(feed['url'], timeout=15, verify=False)
        
        # 404 등 클라이언트 에러 발생 시 명시적으로 예외 처리
        if resp.status_code == 404:
            return None, f"⚠️ 주소 변경됨 (404): {feed['title']}"
            
        resp.raise_for_status()
        
        # 인코딩 강제 설정 (한글 깨짐 방지 시도)
        resp.encoding = resp.apparent_encoding
        
        # 파싱
        parsed = feedparser.parse(resp.content)
        
        if not parsed.entries:
            return None, f"⚠️ 빈 데이터: {feed['title']}"
            
        return parsed.entries[:5], feed['title']

    except Exception as e:
        return None, f"❌ 접속 실패 ({feed['title']}): {str(e)[:30]}"

# ---------------------------------------------------------
# 3. 메인 실행 (병렬 처리)
# ---------------------------------------------------------
def main():
    start = time.time()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 리포트 헤더
    md_output = f"# 🛡️ Security Briefing ({today})\n"
    md_output += f"> 🕒 Generated at: {datetime.now().strftime('%H:%M:%S')}\n\n"
    
    total_count = 0
    
    # 카테고리별 순회
    for category, feeds in RSS_FEEDS.items():
        md_output += f"## {category}\n"
        print(f"\n📂 {category}")
        
        # 병렬 처리 (스레드 20개)
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed): feed for feed in feeds}
            
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, msg = future.result()
                if entries:
                    results.append((msg, entries))
                    print(f"  ✅ Fetched: {msg}")
                else:
                    print(f"  {msg}") # 실패 로그 출력

            # 결과가 없으면 스킵
            if not results:
                md_output += "> *No updates in this category.*\n\n"
                continue
                
            # 이름순 정렬 후 마크다운 작성
            results.sort(key=lambda x: x[0])
            for title, entries in results:
                md_output += f"<details><summary><b>{title}</b> ({len(entries)})</summary>\n\n"
                for entry in entries:
                    link = entry.link
                    summary = clean_html(getattr(entry, 'summary', getattr(entry, 'description', '')))
                    # 게시일 (없으면 생략)
                    published = getattr(entry, 'published', '')[:16]
                    
                    md_output += f"- **[{entry.title}]({link})**\n"
                    if published:
                        md_output += f"  - <small>📅 {published}</small>\n"
                    md_output += f"  - {summary}\n\n"
                md_output += "</details>\n"
        
        md_output += "---\n"

    elapsed = time.time() - start
    print(f"\n✨ Completed! Total {total_count} articles in {elapsed:.2f}s")
    
    # 파일 저장
    with open("daily_security_report.md", "w", encoding="utf-8") as f:
        f.write(md_output)

if __name__ == "__main__":
    main()
