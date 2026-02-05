#!/usr/bin/env python3
"""
KCA 정보보안기사 시험 일정 및 공지사항 모니터링 스크립트
KCA 국가기술자격검정 (www.cq.or.kr) 사이트의 공지사항을 크롤링합니다.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import hashlib
from typing import List, Dict, Optional

class KCAExamMonitor:
    """KCA 정보보안기사 공지사항 모니터링 클래스"""

    def __init__(self):
        self.base_url = "https://www.cq.or.kr"
        self.notice_url = "https://www.cq.or.kr/qh_cusgm01_001.do"
        self.schedule_url = "https://www.cq.or.kr/qh_quagm03_001.do"
        self.data_dir = "data/kca-notifications"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """웹페이지를 가져와서 BeautifulSoup 객체로 반환"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"페이지 가져오기 실패: {url}")
            print(f"오류: {e}")
            return None

    def parse_notices(self, soup: BeautifulSoup) -> List[Dict]:
        """공지사항 목록 파싱"""
        notices = []

        try:
            # 여러 가능한 HTML 구조 시도
            # 방법 1: 테이블 구조
            table = soup.find('table', class_=['tbl_list', 'board_list', 'notice_list'])
            if table:
                rows = table.find_all('tr')
                for row in rows[1:]:  # 헤더 제외
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        notice = {
                            'number': cols[0].get_text(strip=True),
                            'title': cols[1].get_text(strip=True),
                            'date': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            'link': ''
                        }

                        # 링크 추출
                        link_tag = cols[1].find('a')
                        if link_tag and link_tag.get('href'):
                            notice['link'] = self.base_url + link_tag['href']

                        notices.append(notice)

            # 방법 2: 리스트 구조
            if not notices:
                notice_items = soup.find_all('li', class_=['notice_item', 'board_item'])
                for item in notice_items:
                    title_tag = item.find(['a', 'span'], class_=['title', 'subject'])
                    date_tag = item.find(['span', 'div'], class_=['date', 'reg_date'])

                    if title_tag:
                        notice = {
                            'number': '',
                            'title': title_tag.get_text(strip=True),
                            'date': date_tag.get_text(strip=True) if date_tag else '',
                            'link': ''
                        }

                        if title_tag.name == 'a' and title_tag.get('href'):
                            notice['link'] = self.base_url + title_tag['href']

                        notices.append(notice)

            # 방법 3: div 구조
            if not notices:
                notice_divs = soup.find_all('div', class_=['notice_list', 'board_list'])
                for div in notice_divs:
                    title = div.find(['a', 'span'], class_=['title', 'subject'])
                    date = div.find(['span', 'div'], class_=['date', 'reg_date'])

                    if title:
                        notice = {
                            'number': '',
                            'title': title.get_text(strip=True),
                            'date': date.get_text(strip=True) if date else '',
                            'link': ''
                        }

                        if title.name == 'a' and title.get('href'):
                            notice['link'] = self.base_url + title['href']

                        notices.append(notice)

            # 정보보안기사 관련 공지만 필터링
            filtered_notices = [
                n for n in notices
                if '정보보안' in n['title'] or '기사' in n['title'] or '산업기사' in n['title']
            ]

            return filtered_notices if filtered_notices else notices[:10]  # 최대 10개

        except Exception as e:
            print(f"공지사항 파싱 중 오류: {e}")
            return []

    def parse_schedule(self, soup: BeautifulSoup) -> List[Dict]:
        """시험 일정 파싱"""
        schedules = []

        try:
            # 테이블에서 시험 일정 추출
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # 헤더 제외
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        schedule = {
                            'round': cols[0].get_text(strip=True),
                            'type': cols[1].get_text(strip=True),
                            'application_period': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            'exam_date': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                            'result_date': cols[4].get_text(strip=True) if len(cols) > 4 else '',
                        }

                        # 정보보안기사 관련 일정만 필터링
                        if '정보보안' in schedule['type']:
                            schedules.append(schedule)

            return schedules

        except Exception as e:
            print(f"시험 일정 파싱 중 오류: {e}")
            return []

    def get_content_hash(self, content: List[Dict]) -> str:
        """컨텐츠의 해시값 계산"""
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def load_previous_data(self, filename: str) -> Optional[Dict]:
        """이전 데이터 로드"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"이전 데이터 로드 실패: {e}")
        return None

    def save_data(self, data: Dict, filename: str):
        """데이터 저장"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"데이터 저장 완료: {filepath}")
        except Exception as e:
            print(f"데이터 저장 실패: {e}")

    def check_changes(self, current_data: Dict, previous_data: Optional[Dict]) -> Dict:
        """변경사항 확인"""
        changes = {
            'has_changes': False,
            'new_notices': [],
            'updated_schedules': False,
            'timestamp': datetime.now().isoformat()
        }

        if not previous_data:
            changes['has_changes'] = True
            changes['new_notices'] = current_data.get('notices', [])
            changes['updated_schedules'] = len(current_data.get('schedules', [])) > 0
            return changes

        # 공지사항 변경 확인
        current_notices = current_data.get('notices', [])
        previous_notices = previous_data.get('notices', [])

        current_titles = {n['title'] for n in current_notices}
        previous_titles = {n['title'] for n in previous_notices}

        new_titles = current_titles - previous_titles
        if new_titles:
            changes['has_changes'] = True
            changes['new_notices'] = [n for n in current_notices if n['title'] in new_titles]

        # 시험 일정 변경 확인
        current_hash = self.get_content_hash(current_data.get('schedules', []))
        previous_hash = self.get_content_hash(previous_data.get('schedules', []))

        if current_hash != previous_hash:
            changes['has_changes'] = True
            changes['updated_schedules'] = True

        return changes

    def generate_report(self, data: Dict, changes: Dict) -> str:
        """리포트 생성"""
        report = []
        report.append("# KCA 정보보안기사 모니터링 리포트")
        report.append(f"\n**업데이트 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n## 변경사항")

        if changes['has_changes']:
            if changes['new_notices']:
                report.append(f"\n### 🆕 새로운 공지사항 ({len(changes['new_notices'])}개)")
                for notice in changes['new_notices']:
                    report.append(f"\n- **{notice['title']}**")
                    if notice['date']:
                        report.append(f"  - 날짜: {notice['date']}")
                    if notice['link']:
                        report.append(f"  - 링크: {notice['link']}")

            if changes['updated_schedules']:
                report.append(f"\n### 📅 시험 일정 업데이트")
                schedules = data.get('schedules', [])
                for schedule in schedules:
                    report.append(f"\n- **{schedule['round']} - {schedule['type']}**")
                    report.append(f"  - 접수기간: {schedule['application_period']}")
                    report.append(f"  - 시험일: {schedule['exam_date']}")
                    if schedule['result_date']:
                        report.append(f"  - 합격발표: {schedule['result_date']}")
        else:
            report.append("\n변경사항이 없습니다.")

        report.append(f"\n## 전체 공지사항 ({len(data.get('notices', []))}개)")
        for notice in data.get('notices', []):
            report.append(f"\n- {notice['title']} ({notice['date']})")

        return '\n'.join(report)

    def run(self) -> bool:
        """모니터링 실행"""
        print("KCA 정보보안기사 모니터링 시작...")
        print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 공지사항 크롤링
        print("\n공지사항 페이지 크롤링 중...")
        notice_soup = self.fetch_page(self.notice_url)
        notices = []
        if notice_soup:
            notices = self.parse_notices(notice_soup)
            print(f"공지사항 {len(notices)}개 발견")
        else:
            print("공지사항 페이지 접근 실패")

        # 시험 일정 크롤링
        print("\n시험 일정 페이지 크롤링 중...")
        schedule_soup = self.fetch_page(self.schedule_url)
        schedules = []
        if schedule_soup:
            schedules = self.parse_schedule(schedule_soup)
            print(f"시험 일정 {len(schedules)}개 발견")
        else:
            print("시험 일정 페이지 접근 실패")

        # 현재 데이터
        current_data = {
            'timestamp': datetime.now().isoformat(),
            'notices': notices,
            'schedules': schedules
        }

        # 이전 데이터 로드
        previous_data = self.load_previous_data('latest.json')

        # 변경사항 확인
        changes = self.check_changes(current_data, previous_data)

        # 데이터 저장
        self.save_data(current_data, 'latest.json')

        # 변경사항이 있으면 히스토리 저장
        if changes['has_changes']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.save_data(current_data, f'history_{timestamp}.json')
            self.save_data(changes, f'changes_{timestamp}.json')
            print("\n🔔 변경사항 감지!")

        # 리포트 생성
        report = self.generate_report(current_data, changes)

        # 리포트 저장
        report_path = os.path.join(self.data_dir, 'latest_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print("\n" + "="*50)
        print(report)
        print("="*50)

        # GitHub Actions 출력 설정
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"has_changes={str(changes['has_changes']).lower()}\n")
                f.write(f"new_notices_count={len(changes['new_notices'])}\n")

        return changes['has_changes']


def main():
    """메인 함수"""
    monitor = KCAExamMonitor()
    has_changes = monitor.run()

    # 변경사항이 있으면 exit code 1 (GitHub Actions에서 감지용)
    return 0 if not has_changes else 1


if __name__ == '__main__':
    exit(main())
