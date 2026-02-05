import requests
from bs4 import BeautifulSoup
import json
import os
import sys
from datetime import datetime

class KCABulkMonitor:
    def __init__(self):
        # 자격검정 공지사항 상세 URL
        self.base_url = "https://www.cq.or.kr/qh_cusgm01_001.do"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://www.cq.or.kr/"
        }
        self.data_path = "data/kca-notifications/latest.json"
        self.report_path = "data/kca-notifications/latest_report.md"
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

    def get_page_notices(self, page_index):
        """특정 페이지의 공지사항을 수집합니다."""
        params = {"pageIndex": page_index}
        try:
            res = requests.get(self.base_url, params=params, headers=self.headers, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            
            # KCA 게시판 테이블 구조 파싱 (tr.ntc 클래스나 일반 tr 확인)
            rows = soup.select("table.board_list tbody tr")
            page_data = []
            
            for row in rows:
                cells = row.select("td")
                if len(cells) < 3: continue
                
                # 번호, 제목, 작성일 추출
                num = cells[0].text.strip()
                title_elem = cells[1].select_one("a")
                title = title_elem.text.strip()
                date = cells[3].text.strip()
                
                # 상세 페이지 링크 생성
                link = title_elem.get("href", "")
                full_link = f"https://www.cq.or.kr{link}" if link.startswith("/") else link
                
                page_data.append({
                    "id": num,
                    "title": title,
                    "date": date,
                    "link": full_link
                })
            return page_data
        except Exception as e:
            print(f"Error fetching page {page_index}: {e}")
            return []

    def run(self, max_pages=5):
        """설정된 페이지 수만큼 대량으로 데이터를 수집하고 비교합니다."""
        print(f"🚀 KCA 모니터링 시작 (최대 {max_pages}페이지)")
        
        # 1. 신규 데이터 수집
        current_notices = []
        for p in range(1, max_pages + 1):
            current_notices.extend(self.get_page_notices(p))
            
        # 2. 기존 데이터 로드
        old_notices = []
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                old_notices = json.load(f)
        
        # 3. 변경 사항 확인 (제목 기준 신규 확인)
        old_titles = {n['title'] for n in old_notices}
        new_items = [n for n in current_notices if n['title'] not in old_titles]
        
        # 4. 결과 저장 및 리포트 생성
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(current_notices, f, ensure_ascii=False, indent=2)
            
        if new_items:
            with open(self.report_path, "w", encoding="utf-8") as f:
                f.write(f"## 🔔 KCA 정보보안기사 신규 공지 ({len(new_items)}건)\n\n")
                for item in new_items:
                    f.write(f"- **[{item['date']}]** {item['title']}\n")
                    f.write(f"  - [바로가기]({item['link']})\n")
            
            # GitHub Actions용 환경 변수 출력
            with open(os.environ.get('GITHUB_OUTPUT', 'output.txt'), 'a') as f:
                f.write(f"has_changes=true\n")
                f.write(f"new_count={len(new_items)}\n")
        else:
            if os.path.exists(self.report_path):
                os.remove(self.report_path)
            with open(os.environ.get('GITHUB_OUTPUT', 'output.txt'), 'a') as f:
                f.write(f"has_changes=false\n")

if __name__ == "__main__":
    monitor = KCABulkMonitor()
    monitor.run(max_pages=5) # 5페이지 분량 대량 수집
