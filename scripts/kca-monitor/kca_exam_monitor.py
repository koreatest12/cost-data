import requests
from bs4 import BeautifulSoup
import json
import os
import datetime
import hashlib
import time

# --- 설정 ---
# KCA 자격검정 공지사항 URL (실제 구조에 맞춰 변경 가능)
BASE_URL = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdList.do" 
DETAIL_URL_PREFIX = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdView.do?noticeSeq="

# 데이터 저장 경로
DATA_DIR = "data/kca-notifications"
DB_FILE = os.path.join(DATA_DIR, "kca_history.json")
REPORT_FILE = os.path.join(DATA_DIR, "latest_report.md")
BOARD_FILE = "KCA_NOTICE_BOARD.md"

# 타겟 키워드 (이 키워드가 포함된 공지만 수집)
TARGET_KEYWORDS = ["정보보안", "보안기사", "시험일정", "합격자", "접수"]

# 대량 수집 설정 (몇 페이지까지 긁을 것인가)
MAX_PAGES = 10  # 1페이지당 10~15개 게시물이면 약 100~150개 수집

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_notices(page):
    """특정 페이지의 공지사항 목록을 스크래핑"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # KCA 게시판 구조에 따른 파라미터 (변경될 수 있음)
    params = {
        'searchCondition': '',
        'searchKeyword': '',
        'pageIndex': page
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, data=params, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        notices = []
        # 테이블 행(tr) 추출 - 사이트 구조에 따라 select 변경 필요할 수 있음
        rows = soup.select('table.tbl_board tbody tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 4: continue
            
            # 제목 추출
            title_tag = cols[1].find('a')
            if not title_tag: continue
            
            title = title_tag.get_text(strip=True)
            link_onclick = title_tag.get('onclick', '')
            
            # 게시물 ID 추출 (onclick="fn_view('12345');" 형태 파싱)
            post_id = ""
            if "fn_view" in link_onclick:
                post_id = link_onclick.split("'")[1]
            
            date = cols[3].get_text(strip=True)
            
            # 필터링: 정보보안 관련 키워드가 있는지 확인
            if any(keyword in title for keyword in TARGET_KEYWORDS):
                notices.append({
                    'id': post_id,
                    'title': title,
                    'date': date,
                    'link': f"{DETAIL_URL_PREFIX}{post_id}",
                    'fetched_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return notices

    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        return []

def update_markdown_board(all_data):
    """전체 현황판(KCA_NOTICE_BOARD.md) 생성"""
    sorted_data = sorted(all_data.values(), key=lambda x: x['date'], reverse=True)
    
    content = "# 🛡️ KCA 정보보안기사 공지사항 아카이브\n\n"
    content += f"> **마지막 업데이트:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (KST)\n"
    content += f"> **수집된 전체 공지 수:** {len(sorted_data)}건\n\n"
    
    content += "## 📌 최신 중요 공지 (Top 10)\n"
    content += "| 날짜 | 제목 | 바로가기 |\n"
    content += "|---|---|---|\n"
    
    for item in sorted_data[:10]:
        content += f"| {item['date']} | {item['title']} | [이동]({item['link']}) |\n"
    
    content += "\n## 🗂️ 전체 아카이빙 목록\n"
    content += "<details><summary>클릭하여 전체 목록 보기</summary>\n\n"
    content += "| 날짜 | 제목 |\n"
    content += "|---|---|\n"
    for item in sorted_data:
        content += f"| {item['date']} | [{item['title']}]({item['link']}) |\n"
    content += "\n</details>"
    
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    db = load_db()
    new_items_count = 0
    new_items_list = []
    
    print(f"[*] 대량 수집 시작 (최대 {MAX_PAGES} 페이지)...")
    
    for page in range(1, MAX_PAGES + 1):
        print(f"[*] {page} 페이지 스크래핑 중...")
        items = fetch_notices(page)
        
        if not items:
            print(f"[-] {page} 페이지에 데이터가 없거나 오류 발생. 중단합니다.")
            break
            
        for item in items:
            if item['id'] not in db:
                db[item['id']] = item
                new_items_list.append(item)
                new_items_count += 1
        
        # 서버 부하 방지를 위한 짧은 대기
        time.sleep(1)

    # DB 저장
    save_db(db)
    
    # Markdown 대시보드 업데이트
    update_markdown_board(db)
    
    # GitHub Actions Output 설정
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            fh.write(f'new_count={new_items_count}\n')
            fh.write(f'has_changes={"true" if new_items_count > 0 else "false"}\n')
    
    # Issue 생성을 위한 리포트 작성 (신규 건이 있을 때만)
    if new_items_count > 0:
        report_content = "### 🔔 새로 발견된 정보보안기사 공지사항\n\n"
        for item in new_items_list:
            report_content += f"- **[{item['date']}]** [{item['title']}]({item['link']})\n"
        
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
    print(f"[+] 완료. 신규 추가: {new_items_count}건, 전체 데이터: {len(db)}건")

if __name__ == "__main__":
    main()
