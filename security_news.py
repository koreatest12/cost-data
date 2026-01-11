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
from duckduckgo_search import DDGS

# 🚨 SSL 경고 제거
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------
# 1. RSS 채널 리스트 (검증된 소스)
# ---------------------------------------------------------
RSS_FEEDS = {
    "🚨 Critical Threats (긴급)": [
        {"title": "CISA Alerts", "url": "https://www.cisa.gov/uscert/ncas/alerts.xml"},
        {"title": "Microsoft Security", "url": "https://www.microsoft.com/security/blog/feed/"},
        {"title": "Palo Alto Unit 42", "url": "https://unit42.paloaltonetworks.com/feed/"},
    ],
    "🇰🇷 국내 보안 뉴스": [
        {"title": "보안뉴스", "url": "https://www.boannews.com/media/news_rss.xml"},
        {"title": "데일리시큐", "url": "https://www.dailysecu.com/rss/allArticle.xml"},
        {"title": "바이라인네트워크", "url": "https://byline.network/feed/"},
    ],
    "🌍 글로벌 인텔리전스": [
        {"title": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
        {"title": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
        {"title": "SecurityWeek", "url": "https://feeds.feedburner.com/SecurityWeek"},
    ]
}

# ---------------------------------------------------------
# 2. AI 에이전트 유틸리티 (검색 및 분석)
# ---------------------------------------------------------
def create_session():
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    retry = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

def clean_html(raw_html):
    if not raw_html: return ""
    text = re.sub(r'<[^>]+>', '', raw_html).strip()
    return text[:120] + "..." if len(text) > 120 else text

# 🔥 AI 기능 1: 키워드 기반 중요도 분석
def analyze_importance(title, summary):
    critical_keywords = ['RCE', 'Zero-day', 'Vulnerability', 'Exploit', 'Critical', 'Patch', '취약점', '긴급', '해킹', '유출']
    score = 0
    detected_keywords = []
    
    content = (title + " " + summary).lower()
    for kw in critical_keywords:
        if kw.lower() in content:
            score += 1
            detected_keywords.append(kw)
    
    return score, list(set(detected_keywords))

# 🔥 AI 기능 2: 딥러닝(심층) 검색 (Self-Learning)
def deep_search_context(keyword):
    try:
        with DDGS() as ddgs:
            # 뉴스 검색 결과 2개만 요약해서 가져옴
            results = list(ddgs.news(keyword, max_results=2))
            if results:
                return [f"👉 관련 추가 뉴스: {r['title']} ({r['source']})" for r in results]
    except Exception:
        return []
    return []

def fetch_single_feed(feed):
    session = create_session()
    try:
        resp = session.get(feed['url'], timeout=10, verify=False)
        if resp.status_code == 404: return [], f"⚠️ 404 Error: {feed['title']}"
        
        parsed = feedparser.parse(resp.content)
        if not parsed.entries: parsed = feedparser.parse(resp.text)
        
        if not parsed.entries: return [], f"⚠️ No Data: {feed['title']}"
        
        # 최신 3개만, 분석 로직 적용
        processed_entries = []
        for entry in parsed.entries[:3]:
            title = entry.title
            link = entry.link
            summary = clean_html(getattr(entry, 'summary', getattr(entry, 'description', '')))
            published = getattr(entry, 'published', '')[:16]
            
            # 중요도 분석 실행
            score, keywords = analyze_importance(title, summary)
            
            # 중요도가 높으면(키워드 1개 이상) 추가 검색 수행 (AI Agent 행동)
            extra_info = []
            if score >= 1:
                # 너무 많은 요청 방지를 위해 가장 중요한 키워드로만 검색
                search_query = f"{keywords[0]} security news"
                extra_info = deep_search_context(title[:30]) 
            
            processed_entries.append({
                "title": title,
                "link": link,
                "summary": summary,
                "date": published,
                "score": score,
                "keywords": keywords,
                "extra_info": extra_info
            })
            
        return processed_entries, feed['title']

    except Exception as e:
        return [], f"❌ Fail: {feed['title']}"

# ---------------------------------------------------------
# 3. 메인 실행
# ---------------------------------------------------------
def main():
    start = time.time()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # GitHub Summary용 출력 (화면에 바로 보임)
    summary_output = f"# 🤖 AI Security Briefing ({today})\n"
    summary_output += f"> Analysis Engine: Active | Auto-Search: Enabled\n\n"
    
    total_articles = 0
    
    for category, feeds in RSS_FEEDS.items():
        summary_output += f"## {category}\n"
        print(f"📂 Processing: {category}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_feed = {executor.submit(fetch_single_feed, feed): feed for feed in feeds}
            
            results = []
            for future in concurrent.futures.as_completed(future_to_feed):
                entries, title = future.result()
                if entries:
                    results.append((title, entries))
            
            if not results:
                summary_output += "> *No significant updates.*\n\n"
                continue
            
            results.sort(key=lambda x: x[0])
            
            for title, entries in results:
                summary_output += f"### {title}\n"
                for item in entries:
                    # 중요 아이콘 표시
                    icon = "🔥" if item['score'] >= 1 else "🔹"
                    
                    summary_output += f"- {icon} **[{item['title']}]({item['link']})**\n"
                    if item['summary']:
                        summary_output += f"  - {item['summary']}\n"
                    
                    # AI 분석 결과 표시 (키워드 & 추가 검색 정보)
                    if item['keywords']:
                        tags = ", ".join([f"`{k}`" for k in item['keywords']])
                        summary_output += f"  - 🧠 **AI Focus:** {tags}\n"
                    
                    # 추가 검색된 정보가 있으면 표시
                    if item['extra_info']:
                        for info in item['extra_info']:
                            summary_output += f"  - *{info}*\n"
                    
                    summary_output += "\n"
                    total_articles += 1

    # GitHub Actions 화면(Summary)에 출력하기 위해 환경변수에 쓰기
    if "GITHUB_STEP_SUMMARY" in os.environ:
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(summary_output)
            
    # 이슈 생성용 파일 저장
    with open("daily_security_report.md", "w", encoding="utf-8") as f:
        f.write(summary_output)

    print(f"\n✨ Processed {total_articles} articles in {time.time()-start:.2f}s")

if __name__ == "__main__":
    main()
