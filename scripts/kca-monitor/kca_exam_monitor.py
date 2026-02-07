import requests
from bs4 import BeautifulSoup
import json
import os
import datetime
import time
import urllib3

# SSL 경고 메시지 숨기기 (공공기관 사이트 접속 시 필수)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 설정 ---
BASE_URL = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdList.do" 
DETAIL_URL_PREFIX = "https://www.cq.or.kr/qs_qstd/retrieveQsQstdView.do?noticeSeq="

# 데이터 저장 경로
DATA_DIR = "data/kca-notifications"
DB_FILE = os.path.join(DATA_DIR, "kca_history.json")
REPORT_FILE = os.path.join(DATA_DIR, "latest_report.md")
BOARD_FILE = "KCA_NOTICE_BOARD.md"

# 타겟 키워드 (정보보안기사 관련 광범위 키워드)
TARGET_KEYWORDS = ["정보보안", "보안기사", "시험", "합격", "자격", "필기", "실기", "검정"]

# 대량 수집 설정 (최근 20페이지까지 깊게 탐색)
MAX_PAGES = 20 

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_db(data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_notices(page):
    """
    403 우회를 위해 헤더를 브라우저처럼 위장하여 요청
    """
    # 중요: Referer와 Origin이 있어야 서버가 정상적인 접근으로 인식함
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.cq.or.kr/qs_qstd/retrieveQsQstdList.do',
        'Origin': 'https://www.cq.or.kr',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    params = {
        'searchCondition': '',
        'searchKeyword': '',
        'pageIndex': page
    }
    
    try:
        # verify=False로 SSL 인증서 검증 무시 (공공기관 사이트 접속 문제 해결)
        response = requests.post(BASE_URL, headers=headers, data=params, timeout=15, verify=False)
        
        # 403이 뜨더라도 내용을 확인해볼 필요가 있음 (가끔 200 OK인데 내용이 에러인 경우도 있음)
        if response.status_code == 403:
            print(f"⚠️ 403 Forbidden 발생 (Page {page}). 잠시 대기 후 재시도합니다.")
            time.sleep(5)
            # 재시도 로직 (헤더를 조금 단순화해서 재시도)
            response = requests.post(BASE_URL, headers=headers, data=params, timeout=15, verify=False)
            
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        notices = []
        
        # 테이블 파싱 로직 강화
        rows = soup.select('table tbody tr')
        
        # 데이터가 없는 경우 (페이지 끝)
        if not rows or (len(rows) == 1 and "데이터가 없습니다" in rows[0].text):
            return []

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3: continue
            
            # 제목 추출
            title_cell = cols[1] # 보통 두 번째 칸이 제목
            title_tag = title_cell.find('a')
            
            if not title_tag: 
                # a 태그가 없으면 텍스트만이라도 가져옴
                title = title_cell.get_text(strip=True)
                post_id = f"unknown_{hash(title)}"
                link = BASE_URL
            else:
                title = title_tag.get_text(strip=True)
                onclick_text = title_tag.get('onclick', '')
                
                # fn_view('1234') 형태에서 숫자 추출
                import re
                match = re.search(r"fn_view\('(\d+)'\)", onclick_text)
                if match:
                    post_id = match.group(1)
                    link = f"{DETAIL_URL_PREFIX}{post_id}"
                else:
                    post_id = f"unknown_{hash(title)}"
                    link = BASE_URL
            
            # 날짜 추출 (보통 마지막이나 뒤에서 두번째)
            date = ""
            for col in cols:
                txt = col.get_text(strip=True)
                # 202X-XX-XX 형식 찾기
                if re.match(r'\d{4}-\d{2}-\d{2}', txt):
                    date = txt
                    break
            
            if not date:
                date = datetime.datetime.now().strftime("%Y-%m-%d")

            # 키워드 필터링
            if any(keyword in title for keyword in TARGET_KEYWORDS):
                notices.append({
                    'id': post_id,
                    'title': title,
                    'date': date,
                    'link': link,
                    'scraped_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return notices

    except Exception as e:
        print(f"❌ Error fetching page {page}: {e}")
        return []

def update_markdown_board(all_data):
    """전체 현황판 업데이트"""
    sorted_data = sorted(all_data.values(), key=lambda x: x['date'], reverse=True)
    
    content = "# 🛡️ KCA 정보보안기사 및 자격검정 통합 아카이브\n\n"
    content += f"> **최종 업데이트:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (KST)\n"
    content += f"> **총 아카이빙된 공지:** {len(sorted_data)}건\n\n"
    
    content += "## 🚨 긴급/최신 공지 (Top 5)\n"
    content += "| 날짜 | 제목 | 링크 |\n"
    content += "|:---:|---|:---:|\n"
    
    for item in sorted_data[:5]:
        content += f"| {item['date']} | **{item['title']}** | [바로가기]({item['link']}) |\n"
    
    content += "\n## 📂 전체 공지사항 히스토리\n"
    content += "<details><summary>🔽 클릭하여 전체 목록 펼치기</summary>\n\n"
    content += "| 날짜 | 제목 |\n"
    content += "|---|---|\n"
    for item in sorted_data:
        content += f"| {item['date']} | [{item['title']}]({item['link']}) |\n"
    content += "\n</details>"
    
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print(f"[*] KCA 정보보안기사 공지사항 대량 수집 시작 (타겟: {MAX_PAGES} pages)")
    
    db = load_db()
    new_items_list = []
    
    for page in range(1, MAX_PAGES + 1):
        print(f"  >> {page} 페이지 요청 중...")
        items = fetch_notices(page)
        
        # 빈 리스트 반환 시 (데이터 없음 혹은 에러) -> 연속 3번 비었을 때 멈추는 로직이 좋으나, 간단히 멈춤
        if not items and page > 1: # 1페이지가 비었으면 에러일 확률 높음, 그 뒤페이지면 끝난 것
            pass
            
        for item in items:
            if item['id'] not in db:
                print(f"    [NEW] {item['title']}")
                db[item['id']] = item
                new_items_list.append(item)
        
        # 서버 부하 방지 및 차단 회피를 위한 대기
        time.sleep(2)

    # 결과 저장
    if new_items_list:
        print(f"[+] 총 {len(new_items_list)}건의 신규 데이터 발견 및 저장")
        save_db(db)
        
        # 이슈 생성을 위한 리포트 파일 작성
        report_content = "### 📢 KCA 자격검정 신규 공지사항 알림\n\n"
        for item in new_items_list:
            report_content += f"- [{item['date']}] **{item['title']}** [바로가기]({item['link']})\n"
        
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report_content)
    else:
        print("[-] 신규 업데이트된 공지사항이 없습니다.")

    # 항상 보드는 최신 상태로 갱신 (삭제된 글 반영 등은 아니지만 정렬 등을 위해)
    update_markdown_board(db)

    # GitHub Actions Output
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            fh.write(f'new_count={len(new_items_list)}\n')
            fh.write(f'has_changes={"true" if len(new_items_list) > 0 else "false"}\n')

if __name__ == "__main__":
    main()
