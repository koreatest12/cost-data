from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import os
import datetime
import time
import re

# --- 설정 ---
BASE_URL = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdList.do" 
DETAIL_URL_PREFIX = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdView.do?noticeSeq="
DATA_DIR = "data/kca-notifications"
DB_FILE = os.path.join(DATA_DIR, "kca_history.json")
REPORT_FILE = os.path.join(DATA_DIR, "latest_report.md")
BOARD_FILE = "KCA_NOTICE_BOARD.md"

# 타겟 키워드 (정보보안기사 집중)
TARGET_KEYWORDS = ["정보보안", "보안기사", "시험", "합격", "자격", "필기", "실기", "검정", "답안", "정답", "예정"]
MAX_PAGES = 15

# 학습 리소스
STUDY_RESOURCES = """
## 📚 정보보안기사 추천 학습 리소스 모음
| 구분 | 사이트명 | 설명 | 링크 |
|:---:|---|---|:---:|
| **공식** | KCA 자격검정 | 시험 접수 및 공식 공지 | [바로가기](https://www.cq.or.kr/) |
| **공식** | KISA 보호나라 | 최신 보안 동향 및 백서 (실기 필수) | [바로가기](https://www.boho.or.kr/) |
| **커뮤니티** | 알기사 (네이버카페) | 최대 수험생 커뮤니티, 기출 복원 | [바로가기](https://cafe.naver.com/algisa) |
| **기출** | CBT 기출문제 | 필기 과년도 기출문제 풀이 | [바로가기](https://www.comcbt.com/) |
"""

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def categorize_title(title):
    if any(k in title for k in ["정답", "답안", "기출", "문제", "자료"]): return "📄 **[학습자료]**"
    elif any(k in title for k in ["합격", "발표", "결과"]): return "🎉 **[합격발표]**"
    elif any(k in title for k in ["일정", "접수", "계획", "시행"]): return "📅 **[시험일정]**"
    elif "정보보안" in title: return "🔒 **[정보보안]**"
    else: return "📢 [일반공지]"

def fetch_notices(page):
    # curl_cffi용 세션 생성 (Chrome 120 버전으로 위장)
    session = requests.Session(impersonate="chrome120")
    
    headers = {
        'Referer': 'https://www.cq.or.kr/qs_qstd/retrieveQsQstdList.do',
        'Origin': 'https://www.cq.or.kr',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    
    params = {'searchCondition': '', 'searchKeyword': '', 'pageIndex': str(page)}
    
    try:
        # verify=False 옵션은 curl_cffi에서는 보통 필요 없으나, SSL 에러 방지를 위해 명시 가능
        # impersonate 옵션이 가장 중요합니다.
        response = session.post(BASE_URL, headers=headers, data=params, timeout=20)
        
        # 403 체크
        if response.status_code == 403:
            print(f"⚠️ Page {page}: 403 감지됨. 강력한 우회 시도 중...")
            time.sleep(5)
            # 세션을 재생성하여 재시도
            session = requests.Session(impersonate="chrome110") 
            response = session.post(BASE_URL, headers=headers, data=params, timeout=20)

        response.raise_for_status()
        
        # 인코딩 강제 설정 (한글 깨짐 방지)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        notices = []
        rows = soup.select('table tbody tr')
        
        # 데이터 없음 체크
        if not rows or (len(rows) == 1 and ("데이터가 없습니다" in rows[0].text or "No data" in rows[0].text)):
            return []

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3: continue
            
            title_cell = cols[1]
            title_tag = title_cell.find('a')
            
            if not title_tag: 
                title = title_cell.get_text(strip=True)
                post_id = f"unknown_{hash(title)}"
                link = BASE_URL
            else:
                title = title_tag.get_text(strip=True)
                onclick = title_tag.get('onclick', '')
                match = re.search(r"fn_view\('(\d+)'\)", onclick)
                if match:
                    post_id = match.group(1)
                    link = f"{DETAIL_URL_PREFIX}{post_id}"
                else:
                    post_id = f"unknown_{hash(title)}"
                    link = BASE_URL
            
            date = ""
            for col in cols:
                txt = col.get_text(strip=True)
                if re.match(r'\d{4}-\d{2}-\d{2}', txt):
                    date = txt
                    break
            if not date: date = datetime.datetime.now().strftime("%Y-%m-%d")

            # 키워드 필터링
            if any(keyword in title for keyword in TARGET_KEYWORDS):
                notices.append({
                    'id': post_id,
                    'title': title,
                    'date': date,
                    'link': link,
                    'category': categorize_title(title),
                    'scraped_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        return notices

    except Exception as e:
        print(f"❌ Error on page {page}: {e}")
        return []

def update_markdown_board(all_data):
    sorted_data = sorted(all_data.values(), key=lambda x: x['date'], reverse=True)
    
    content = "# 🛡️ KCA 정보보안기사 통합 대시보드\n\n"
    content += f"> **상태:** ✅ 정상 가동 (Bypass 403) | **업데이트:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    materials = [d for d in sorted_data if "학습자료" in d.get('category', '') or "정답" in d['title']]
    schedules = [d for d in sorted_data if "시험일정" in d.get('category', '')]
    
    content += "## 🚀 핵심 정보 (자료 & 일정)\n"
    content += "| 날짜 | 분류 | 제목 |\n"
    content += "|:---:|:---:|---|\n"
    for item in (materials[:5] + schedules[:5]):
        content += f"| {item['date']} | {item.get('category', '')} | [{item['title']}]({item['link']}) |\n"
        
    content += "\n" + STUDY_RESOURCES + "\n"
    
    content += "## 📋 전체 아카이브\n"
    content += "<details><summary>클릭하여 전체 보기</summary>\n\n"
    content += "| 날짜 | 분류 | 제목 |\n"
    content += "|---|---|---|\n"
    for item in sorted_data:
        content += f"| {item['date']} | {item.get('category','')} | [{item['title']}]({item['link']}) |\n"
    content += "\n</details>"
    
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print(f"[*] 정보보안기사 크롤러 가동 (curl_cffi 엔진)")
    db = load_db()
    new_items_list = []
    
    for page in range(1, MAX_PAGES + 1):
        print(f"  >> Page {page} Scanning...")
        items = fetch_notices(page)
        
        # 연속된 빈 페이지가 나오면 조기 종료 (옵션)
        if not items and page > 5:
             print("  [-] 데이터 없음. 조기 종료.")
             break

        for item in items:
            if item['id'] not in db:
                print(f"    [NEW] {item['title']}")
                db[item['id']] = item
                new_items_list.append(item)
        time.sleep(2) # 서버 부하 방지

    save_db(db)
    update_markdown_board(db)
    
    if new_items_list:
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            for item in new_items_list:
                f.write(f"- {item['category']} **[{item['date']}]** [{item['title']}]({item['link']})\n")

    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            fh.write(f'new_count={len(new_items_list)}\n')
            fh.write(f'has_changes={"true" if len(new_items_list) > 0 else "false"}\n')

if __name__ == "__main__":
    main()
