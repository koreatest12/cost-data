import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

class KCABulkMonitor:
    def __init__(self):
        self.base_url = "https://www.cq.or.kr/qh_cusgm01_001.do"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://www.cq.or.kr/"
        }
        self.data_dir = "data/kca-notifications"
        self.json_path = os.path.join(self.data_dir, "database.json")
        self.all_md_path = "KCA_NOTICE_BOARD.md" # 전체 공지사항 아카이브 파일
        self.report_path = os.path.join(self.data_dir, "latest_report.md")
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_pages(self, max_pages=10):
        """대량의 페이지를 훑어 전체 목록을 가져옵니다."""
        all_data = []
        for p in range(1, max_pages + 1):
            print(f"🔄 {p}페이지 수집 중...")
            try:
                res = requests.get(self.base_url, params={"pageIndex": p}, headers=self.headers, timeout=15)
                soup = BeautifulSoup(res.text, "html.parser")
                rows = soup.select("table.board_list tbody tr")
                
                for row in rows:
                    cells = row.select("td")
                    if len(cells) < 3: continue
                    
                    num = cells[0].get_text(strip=True)
                    title_elem = cells[1].select_one("a")
                    title = title_elem.get_text(strip=True)
                    date = cells[3].get_text(strip=True)
                    link = title_elem.get("href", "")
                    full_link = f"https://www.cq.or.kr{link}" if link.startswith("/") else link
                    
                    all_data.append({"id": num, "title": title, "date": date, "link": full_link})
                time.sleep(0.5)
            except Exception as e:
                print(f"Error on page {p}: {e}")
        return all_data

    def update_archive(self, current_data):
        """기존 데이터와 병합하고 전체 대시보드 파일을 생성합니다."""
        # 1. 기존 데이터 로드 (중복 제거용)
        existing_data = []
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        
        # 2. 신규 데이터 판별
        existing_titles = {n['title'] for n in existing_data}
        new_items = [n for n in current_data if n['title'] not in existing_titles]
        
        # 3. 전체 데이터 병합 (최신순 정렬)
        # 셋(Set)을 이용해 제목 기준 중복 제거 후 날짜 내림차순 정렬
        combined = {item['title']: item for item in (current_data + existing_data)}.values()
        final_list = sorted(combined, key=lambda x: x['date'], reverse=True)

        # 4. JSON 데이터베이스 저장
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=2)

        # 5. 전체 공지사항 마크다운 대시보드 생성 (사용자 조회용)
        with open(self.all_md_path, "w", encoding="utf-8") as f:
            f.write(f"# 📚 KCA 정보보안기사 공지사항 아카이브\n\n")
            f.write(f"> 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}\n\n")
            f.write(f"| 번호 | 날짜 | 제목 | 링크 |\n")
            f.write(f"| :--- | :--- | :--- | :--- |\n")
            for item in final_list:
                f.write(f"| {item['id']} | {item['date']} | {item['title']} | [🔗 바로가기]({item['link']}) |\n")

        # 6. 신규 알림 리포트 생성 (Action 출력용)
        if new_items:
            with open(self.report_path, "w", encoding="utf-8") as f:
                f.write(f"## 🔔 신규 공지 발견 ({len(new_items)}건)\n")
                for n in new_items:
                    f.write(f"- **[{n['date']}]** {n['title']} ([링크]({n['link']}))\n")
            return len(new_items)
        return 0

if __name__ == "__main__":
    monitor = KCABulkMonitor()
    data = monitor.fetch_pages(max_pages=10) # 10페이지 대량 수집
    new_count = monitor.update_archive(data)
    
    with open(os.environ.get('GITHUB_OUTPUT', 'output.txt'), 'a') as f:
        f.write(f"new_count={new_count}\n")
        f.write(f"has_changes={'true' if new_count > 0 else 'false'}\n")
