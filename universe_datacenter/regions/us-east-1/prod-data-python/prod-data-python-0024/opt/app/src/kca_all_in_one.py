import os
import json
import datetime
import time
import pytz
from curl_cffi import requests
from bs4 import BeautifulSoup

# --- 설정 ---
DATA_DIR = "data"
SCHEDULE_FILE = os.path.join(DATA_DIR, "schedule_2026.json")
NOTICE_FILE = os.path.join(DATA_DIR, "kca_notices.json")
NEWS_FILE = os.path.join(DATA_DIR, "security_news.json")
BOARD_FILE = "KCA_NOTICE_BOARD.md"
KST = pytz.timezone('Asia/Seoul')

# --- [PART 1] 2026년 확정 일정 (Static Data) ---
STATIC_SCHEDULE = [
    {
        "round": "제1회", "type": "필기",
        "reg_period": "2026-01-26(월) ~ 01-29(목)",
        "exam_period": "2026-02-09(월) ~ 03-06(금)",
        "result_date": "2026-03-13(금)", "note": "CBT / 빈자리: 02.02~02.03"
    },
    {
        "round": "제1회", "type": "실기",
        "reg_period": "2026-03-16(월) ~ 03-19(목)",
        "exam_period": "2026-04-11(토) ~ 04-26(일)",
        "result_date": "2026-05-08(금)", "note": "정보보안 분야 전체"
    },
    {
        "round": "제2회", "type": "필기",
        "reg_period": "2026-05-11(월) ~ 05-14(목)",
        "exam_period": "2026-05-22(금) ~ 06-15(월)",
        "result_date": "2026-06-19(금)", "note": "CBT 방식"
    },
    {
        "round": "제2회", "type": "실기",
        "reg_period": "2026-06-22(월) ~ 06-25(목)",
        "exam_period": "2026-07-25(토) ~ 08-09(일)",
        "result_date": "2026-08-28(금)", "note": "기능사 제외"
    }
]

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- [PART 2] KCA 공지사항 크롤링 (403 우회) ---
def fetch_kca_notices():
    print("[*] KCA 공지사항 수집 시작...")
    url = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdList.do"
    try:
        session = requests.Session(impersonate="chrome120")
        session.get("https://www.cq.or.kr/", timeout=15) # 세션 획득
        time.sleep(1)
        
        payload = {'searchCondition': '', 'searchKeyword': '', 'pageIndex': '1'}
        res = session.post(url, data=payload, timeout=15)
        res.encoding = 'utf-8'
        
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table tbody tr')
        notices = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3: continue
            title = cols[1].get_text(strip=True)
            date = cols[3].get_text(strip=True) if len(cols) > 3 else ""
            if any(k in title for k in ["정보보안", "보안기사", "합격", "일정"]):
                notices.append({"date": date, "title": title, "link": url})
        return notices
    except Exception as e:
        print(f"[-] KCA 수집 오류: {e}")
        return []

# --- [PART 3] 보안뉴스 수집 ---
def fetch_security_news():
    print("[*] 보안뉴스 수집 시작...")
    try:
        session = requests.Session(impersonate="chrome120")
        res = session.get("https://www.boannews.com/media/t_list.asp", timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        news = []
        for art in soup.select('.news_list .news_txt')[:7]:
            t_tag = art.find('a')
            if t_tag:
                title = t_tag.get_text(strip=True)
                link = "https://www.boannews.com" + t_tag['href']
                news.append({"title": title, "link": link})
        return news
    except Exception as e:
        print(f"[-] 보안뉴스 수집 오류: {e}")
        return []

# --- [PART 4] 대시보드 생성 ---
def generate_dashboard(notices, news):
    now = datetime.datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    md = f"# 🛡️ KCA 정보보안기사 통합 상황판\n\n> **업데이트:** {now} (KST)\n\n"
    
    md += "## 📅 2026년 정보보안기사 시험 일정 (확정)\n"
    md += "| 회차 | 구분 | 원서접수 | 시험일 | 합격발표 | 비고 |\n|---|---|---|---|---|---|\n"
    for s in STATIC_SCHEDULE:
        md += f"| {s['round']} | **{s['type']}** | {s['reg_period']} | {s['exam_period']} | **{s['result_date']}** | {s['note']} |\n"
    
    md += "\n## 📢 최신 공지사항\n"
    if notices:
        for n in notices: md += f"- [{n['date']}] {n['title']}\n"
    else: md += "> 수집된 공지사항이 없습니다.\n"
    
    md += "\n## 📰 오늘의 보안뉴스\n"
    if news:
        for n in news: md += f"- [{n['title']}]({n['link']})\n"
    else: md += "> 뉴스를 불러오지 못했습니다.\n"
    
    md += "\n## 🔗 바로가기\n- [KCA 자격검정](https://www.cq.or.kr/)\n- [KISA 보호나라](https://www.boho.or.kr/)\n"
    
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(md)

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    save_json(SCHEDULE_FILE, STATIC_SCHEDULE)
    
    notices = fetch_kca_notices()
    news = fetch_security_news()
    
    if notices: save_json(NOTICE_FILE, notices)
    if news: save_json(NEWS_FILE, news)
    
    generate_dashboard(notices, news)
