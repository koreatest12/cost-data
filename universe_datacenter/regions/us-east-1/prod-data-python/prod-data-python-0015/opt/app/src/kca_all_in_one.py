import os
import json
import datetime
import time
import pytz
from curl_cffi import requests # 403 우회용 브라우저 엔진
from bs4 import BeautifulSoup

# --- [설정 및 경로] ---
DATA_DIR = "data"
SCHEDULE_FILE = os.path.join(DATA_DIR, "schedule_2026.json")
NOTICE_FILE = os.path.join(DATA_DIR, "kca_notices.json")
NEWS_FILE = os.path.join(DATA_DIR, "security_news.json")
BOARD_FILE = "KCA_NOTICE_BOARD.md"

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# --- [PART 1] 2026년 정보보안기사 확정 일정 (Static Data Injection) ---
# 제공해주신 PDF 정보를 기반으로 완벽하게 정리된 데이터
STATIC_SCHEDULE = [
    {
        "round": "제1회",
        "type": "필기",
        "reg_period": "2026-01-26(월) ~ 01-29(목)",
        "exam_period": "2026-02-09(월) ~ 03-06(금)",
        "result_date": "2026-03-13(금)",
        "note": "CBT 방식 / 빈자리접수: 02.02~02.03"
    },
    {
        "round": "제1회",
        "type": "실기",
        "reg_period": "2026-03-16(월) ~ 03-19(목)",
        "exam_period": "2026-04-11(토) ~ 04-26(일)",
        "result_date": "2026-05-08(금)",
        "note": "정보보안 분야 전체"
    },
    {
        "round": "제2회",
        "type": "필기",
        "reg_period": "2026-05-11(월) ~ 05-14(목)",
        "exam_period": "2026-05-22(금) ~ 06-15(월)",
        "result_date": "2026-06-19(금)",
        "note": "CBT 방식"
    },
    {
        "round": "제2회",
        "type": "실기",
        "reg_period": "2026-06-22(월) ~ 06-25(목)",
        "exam_period": "2026-07-25(토) ~ 08-09(일)",
        "result_date": "2026-08-28(금)",
        "note": "기능사 제외"
    }
]

def ensure_dir():
    """데이터 디렉토리 생성"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_json(path, data):
    """JSON 저장 유틸리티"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- [PART 2] KCA 공지사항 크롤링 (Advanced WAF Bypass) ---
def fetch_kca_notices():
    print("[*] KCA 공지사항 수집 시작 (Chrome 120 위장)...")
    base_url = "https://www.cq.or.kr"
    list_url = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdList.do"
    
    try:
        # curl_cffi 세션 생성 (브라우저 지문 위조)
        session = requests.Session(impersonate="chrome120")
        
        # 1. 메인 페이지 접속 (Session Cookie 획득)
        session.get(base_url, timeout=15)
        time.sleep(1)
        
        # 2. 공지사항 리스트 요청 (POST)
        payload = {'searchCondition': '', 'searchKeyword': '', 'pageIndex': '1'}
        response = session.post(list_url, data=payload, timeout=15)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select('table tbody tr')
        
        notices = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3: continue
            
            # 데이터 파싱
            title = cols[1].get_text(strip=True)
            date = cols[3].get_text(strip=True) if len(cols) > 3 else ""
            
            # 정보보안기사 관련 키워드 필터링
            keywords = ["정보보안", "보안기사", "필기", "실기", "합격", "자격"]
            if any(k in title for k in keywords):
                # 링크 파싱 (onclick 이벤트 등 처리 필요하나 단순화를 위해 리스트 URL 사용)
                notices.append({
                    "date": date,
                    "title": title,
                    "link": list_url
                })
                
        print(f"[+] KCA 공지 {len(notices)}건 수집 완료")
        return notices
        
    except Exception as e:
        print(f"[-] KCA 수집 중 오류 (서버 차단 등): {e}")
        # 실패하더라도 빈 리스트 반환하여 전체 프로세스는 계속 진행
        return []

# --- [PART 3] 보안뉴스(Boannews) 수집 ---
def fetch_security_news():
    print("[*] 보안뉴스(Boannews) 헤드라인 수집 시작...")
    url = "https://www.boannews.com/media/t_list.asp"
    
    try:
        session = requests.Session(impersonate="chrome120")
        response = session.get(url, timeout=15)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        # 뉴스 리스트 아이템 추출
        articles = soup.select('.news_list .news_txt')
        
        for article in articles[:7]: # 최신 7개만
            title_tag = article.find('a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = "https://www.boannews.com" + title_tag['href']
                desc_tag = article.find('p') # 요약글
                desc = desc_tag.get_text(strip=True) if desc_tag else ""
                
                news_list.append({
                    "title": title,
                    "link": link,
                    "desc": desc
                })
                
        print(f"[+] 보안뉴스 {len(news_list)}건 수집 완료")
        return news_list
        
    except Exception as e:
        print(f"[-] 보안뉴스 수집 실패: {e}")
        return []

# --- [PART 4] 통합 대시보드(Markdown) 생성 ---
def generate_dashboard(notices, news):
    print("[*] 통합 대시보드(Markdown) 생성 중...")
    now_str = datetime.datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    
    md = f"# 🛡️ KCA 정보보안기사 & 보안뉴스 통합 상황판\n\n"
    md += f"> **최종 업데이트:** {now_str} (KST)\n"
    md += f"> **시스템 상태:** 🟢 정상 가동 중\n\n"
    
    # 1. 2026년 시험 일정 (확정된 정적 데이터) - 가장 중요하므로 상단 배치
    md += "## 📅 2026년 정보보안기사 시험 일정 (확정)\n"
    md += "| 회차 | 구분 | 원서접수 | 시험일 | 합격발표 | 비고 |\n"
    md += "|:---:|:---:|:---:|:---:|:---:|:---:|\n"
    
    for s in STATIC_SCHEDULE:
        md += f"| {s['round']} | **{s['type']}** | {s['reg_period']} | {s['exam_period']} | **{s['result_date']}** | {s['note']} |\n"
    
    # 2. 최신 공지사항 (크롤링 데이터)
    md += "\n## 📢 KCA 최신 공지사항\n"
    if notices:
        md += "| 날짜 | 제목 |\n"
        md += "|:---:|---|\n"
        for n in notices:
            md += f"| {n['date']} | [{n['title']}]({n['link']}) |\n"
    else:
        md += "> ⚠️ 현재 수집된 신규 공지사항이 없거나, KCA 서버 연결이 지연되고 있습니다.\n"
        
    # 3. 오늘의 보안뉴스
    md += "\n## 📰 오늘의 보안뉴스 (Boannews)\n"
    if news:
        for n in news:
            md += f"- **[{n['title']}]({n['link']})**\n"
            if n['desc']:
                md += f"  - _{n['desc'][:60]}..._\n"
    else:
        md += "> ⚠️ 보안뉴스를 불러오지 못했습니다.\n"
        
    # 4. 학습 및 환불/문의 안내
    md += "\n## 🔗 필수 정보 및 바로가기\n"
    md += "- **[KCA 자격검정 홈페이지](https://www.cq.or.kr/)** (원서접수/합격확인)\n"
    md += "- **[KISA 보호나라](https://www.boho.or.kr/)** (최신 보안 가이드)\n"
    md += "- **[CBT 기출문제](https://www.comcbt.com/)** (필기 학습)\n\n"
    
    md += "### 💰 환불 규정\n"
    md += "- **100% 환불:** 원서접수 기간 내 (마감일 18:00까지)\n"
    md += "- **50% 환불:** 접수마감 다음날 ~ 시험 5일 전 (18:00까지)\n"
    
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"[+] {BOARD_FILE} 생성 완료!")

# --- 메인 실행 함수 ---
def main():
    ensure_dir()
    
    # [Step 1] 정적 일정 데이터 저장 (파일로 백업)
    save_json(SCHEDULE_FILE, STATIC_SCHEDULE)
    
    # [Step 2] 데이터 수집 (크롤링)
    kca_notices = fetch_kca_notices()
    security_news = fetch_security_news()
    
    # [Step 3] 수집 데이터 저장
    if kca_notices: save_json(NOTICE_FILE, kca_notices)
    if security_news: save_json(NEWS_FILE, security_news)
    
    # [Step 4] 통합 대시보드 생성
    generate_dashboard(kca_notices, security_news)
    
    print("[+] 모든 작업이 성공적으로 완료되었습니다.")

if __name__ == "__main__":
    main()
