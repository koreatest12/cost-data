import os
import json
import datetime
import time
import random
from curl_cffi import requests # 403 우회 핵심 라이브러리
from bs4 import BeautifulSoup

# --- 설정 ---
DATA_DIR = "data"
SCHEDULE_FILE = os.path.join(DATA_DIR, "schedule_2026.json")
NOTICE_FILE = os.path.join(DATA_DIR, "kca_notices.json")
NEWS_FILE = os.path.join(DATA_DIR, "security_news.json")
BOARD_FILE = "KCA_NOTICE_BOARD.md"

# --- [PART 1] 2026년 정보보안기사 확정 일정 (정적 데이터 주입) ---
STATIC_SCHEDULE = [
    {
        "round": "제1회 (상반기)",
        "type": "필기",
        "reg_start": "2026-01-26", "reg_end": "2026-01-29",
        "exam_start": "2026-02-09", "exam_end": "2026-03-06",
        "result": "2026-03-13",
        "status": "진행중"
    },
    {
        "round": "제1회 (상반기)",
        "type": "실기",
        "reg_start": "2026-03-16", "reg_end": "2026-03-19",
        "exam_start": "2026-04-11", "exam_end": "2026-04-26",
        "result": "2026-05-08",
        "status": "예정"
    },
    {
        "round": "제2회 (하반기)",
        "type": "필기",
        "reg_start": "2026-05-11", "reg_end": "2026-05-14",
        "exam_start": "2026-05-22", "exam_end": "2026-06-15",
        "result": "2026-06-19",
        "status": "예정"
    },
    {
        "round": "제2회 (하반기)",
        "type": "실기",
        "reg_start": "2026-06-22", "reg_end": "2026-06-25",
        "exam_start": "2026-07-25", "exam_end": "2026-08-09",
        "result": "2026-08-28",
        "status": "예정"
    }
]

def ensure_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- [PART 2] KCA 공지사항 크롤링 (403 우회) ---
def fetch_kca_notices():
    print("[*] KCA 공지사항 수집 시작 (Chrome 위장)...")
    url = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdList.do"
    view_url = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdView.do?noticeSeq="
    
    try:
        # curl_cffi를 사용하여 브라우저 지문(Fingerprint) 위장
        session = requests.Session(impersonate="chrome120")
        
        # 1. 세션 획득 (GET)
        session.get("https://www.cq.or.kr/", timeout=10)
        time.sleep(1)
        
        # 2. 데이터 요청 (POST)
        data = {'searchCondition': '', 'searchKeyword': '', 'pageIndex': '1'}
        response = session.post(url, data=data, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select('table tbody tr')
        
        notices = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3: continue
            
            title = cols[1].get_text(strip=True)
            date = cols[3].get_text(strip=True) if len(cols) > 3 else datetime.datetime.now().strftime("%Y-%m-%d")
            
            # 정보보안 관련 키워드만 필터링
            if any(k in title for k in ["정보보안", "보안기사", "합격", "일정", "자격"]):
                notices.append({"date": date, "title": title, "link": url}) # 링크는 상세페이지 ID 파싱 필요하나 생략
                
        print(f"[+] KCA 공지 {len(notices)}건 수집 완료")
        return notices
    except Exception as e:
        print(f"[-] KCA 수집 실패 (서버 차단 가능성): {e}")
        return []

# --- [PART 3] 보안뉴스(Boannews) 수집 ---
def fetch_security_news():
    print("[*] 보안뉴스 수집 시작...")
    url = "https://www.boannews.com/media/t_list.asp"
    try:
        session = requests.Session(impersonate="chrome120")
        response = session.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        # 보안뉴스 구조에 맞춰 파싱
        articles = soup.select('.news_list .news_txt')
        for article in articles[:7]: # 최신 7개
            title_tag = article.find('a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = "https://www.boannews.com" + title_tag['href']
                news_list.append({"title": title, "link": link})
                
        print(f"[+] 보안뉴스 {len(news_list)}건 수집 완료")
        return news_list
    except Exception as e:
        print(f"[-] 보안뉴스 수집 실패: {e}")
        return []

# --- [PART 4] 대시보드(Markdown) 생성 ---
def generate_dashboard(notices, news):
    print("[*] 대시보드 생성 중...")
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    md = f"# 🛡️ KCA 정보보안기사 & 보안뉴스 통합 상황판\n\n"
    md += f"> **최종 업데이트:** {now} (KST)\n\n"
    
    # 1. 2026년 시험 일정 (확정된 정적 데이터)
    md += "## 📅 2026년 정보보안기사 시험 일정 (확정)\n"
    md += "| 회차 | 구분 | 원서접수 | 시험일 | 합격발표 |\n"
    md += "|:---:|:---:|:---:|:---:|:---:|\n"
    for s in STATIC_SCHEDULE:
        md += f"| {s['round']} | **{s['type']}** | {s['reg_start']} ~ {s['reg_end']} | {s['exam_start']} ~ {s['exam_end']} | **{s['result']}** |\n"
    
    # 2. 최신 공지사항
    md += "\n## 📢 KCA 최신 공지사항\n"
    if notices:
        for n in notices:
            md += f"- [{n['date']}] {n['title']}\n"
    else:
        md += "> ⚠️ 현재 수집된 공지사항이 없거나 서버 응답이 없습니다.\n"
        
    # 3. 보안뉴스
    md += "\n## 📰 오늘의 보안뉴스 (Boannews)\n"
    if news:
        for n in news:
            md += f"- [{n['title']}]({n['link']})\n"
    else:
        md += "> ⚠️ 뉴스를 불러오지 못했습니다.\n"
        
    # 4. 학습 리소스
    md += "\n## 📚 추천 학습 자료\n"
    md += "- [KISA 보호나라 (보안백서)](https://www.boho.or.kr/)\n"
    md += "- [CBT 기출문제](https://www.comcbt.com/)\n"
    
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"[+] {BOARD_FILE} 생성 완료!")

# --- 메인 실행 함수 ---
def main():
    ensure_dir()
    
    # 1. 일정 저장 (Inject)
    save_json(SCHEDULE_FILE, STATIC_SCHEDULE)
    
    # 2. 데이터 수집
    kca_data = fetch_kca_notices()
    news_data = fetch_security_news()
    
    # 3. 결과 저장
    if kca_data: save_json(NOTICE_FILE, kca_data)
    if news_data: save_json(NEWS_FILE, news_data)
    
    # 4. 보드 생성
    generate_dashboard(kca_data, news_data)

if __name__ == "__main__":
    main()
