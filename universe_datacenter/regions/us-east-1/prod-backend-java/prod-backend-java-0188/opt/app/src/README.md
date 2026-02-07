# KCA 정보보안기사 시험 모니터링 시스템

KCA(한국방송통신전파진흥원) 국가기술자격검정의 정보보안기사 시험 일정 및 공지사항을 자동으로 모니터링하는 시스템입니다.

## 📋 개요

이 시스템은 다음을 자동으로 수행합니다:
- **매시간** KCA 웹사이트의 공지사항 페이지 크롤링
- 정보보안기사 관련 새로운 공지사항 감지
- 시험 일정 변경사항 추적
- 변경사항 발견 시 자동으로 GitHub Issue 생성
- 모든 데이터의 히스토리 보관

## 🎯 주요 기능

### 1. 자동 크롤링
- **공지사항 페이지**: https://www.cq.or.kr/qh_cusgm01_001.do
- **시험 일정 페이지**: https://www.cq.or.kr/qh_quagm03_001.do
- 매시간 정각에 자동 실행 (GitHub Actions 스케줄러)

### 2. 변경사항 감지
- 새로운 공지사항 자동 감지
- 시험 일정 변경 추적
- 중복 알림 방지 (해시 기반 비교)

### 3. 알림 시스템
- 새 공지사항 발견 시 GitHub Issue 자동 생성
- 라벨링: `notification`, `kca-exam`, `auto-generated`
- 상세한 리포트 자동 생성

### 4. 데이터 보관
- `data/kca-notifications/latest.json` - 최신 데이터
- `data/kca-notifications/latest_report.md` - 최신 리포트
- `data/kca-notifications/history_*.json` - 변경 히스토리
- `data/kca-notifications/changes_*.json` - 변경사항 상세

## 🚀 사용 방법

### 자동 실행 (GitHub Actions)
워크플로우는 자동으로 실행됩니다:
- **스케줄**: 매시간 정각 (00분)
- **수동 실행**: GitHub Actions 탭에서 "Run workflow" 버튼 클릭

### 로컬 실행
```bash
# 의존성 설치
pip install -r scripts/kca-monitor/requirements.txt

# 스크립트 실행
python scripts/kca-monitor/kca_exam_monitor.py
```

## 📊 출력 형식

### JSON 데이터 구조
```json
{
  "timestamp": "2026-02-05T12:00:00",
  "notices": [
    {
      "number": "123",
      "title": "2026년도 정보보안기사 제1회 시험 일정 공고",
      "date": "2026-02-01",
      "link": "https://www.cq.or.kr/..."
    }
  ],
  "schedules": [
    {
      "round": "제1회",
      "type": "정보보안기사",
      "application_period": "2026-03-01 ~ 2026-03-07",
      "exam_date": "2026-04-15",
      "result_date": "2026-05-10"
    }
  ]
}
```

### 마크다운 리포트
- 새로운 공지사항 목록
- 시험 일정 변경사항
- 전체 공지사항 요약

## ⚙️ 설정

### 크롤링 주기 변경
`.github/workflows/kca-exam-monitor.yml` 파일의 `cron` 설정을 수정:
```yaml
schedule:
  - cron: '0 * * * *'  # 매시간
  # - cron: '0 */2 * * *'  # 2시간마다
  # - cron: '0 9,18 * * *'  # 매일 9시, 18시
```

### 알림 설정
워크플로우 파일에서 다음을 수정:
- Issue 생성 조건
- 라벨 설정
- 알림 메시지 형식

## 🔧 트러블슈팅

### 403 Forbidden 오류
KCA 웹사이트가 봇 접근을 차단하는 경우:
1. User-Agent 헤더 확인
2. 요청 간격 조정
3. 필요시 프록시 사용

### 파싱 오류
웹사이트 구조가 변경된 경우:
1. `kca_exam_monitor.py`의 `parse_notices()` 함수 확인
2. HTML 구조에 맞게 셀렉터 수정

### 데이터가 저장되지 않음
1. `data/kca-notifications/` 디렉토리 존재 확인
2. 파일 권한 확인
3. GitHub Actions의 커밋 권한 확인

## 📝 모니터링 대상

### 정보보안기사
- 시험 일정 (접수, 시험일, 합격발표)
- 응시 자격 변경사항
- 시험 방법 변경 (필기/실기)
- 합격 기준 변경
- 기타 중요 공지사항

### 정보보안산업기사
- 동일한 모니터링 적용
- 필터링을 통해 함께 추적

## 🔗 관련 링크

- [KCA 국가기술자격검정 홈페이지](https://www.cq.or.kr/)
- [정보보안기사 공지사항](https://www.cq.or.kr/qh_cusgm01_001.do)
- [시험 일정](https://www.cq.or.kr/qh_quagm03_001.do)
- [Q-net (기사/산업기사)](https://www.q-net.or.kr/)

## 📄 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.

## 🤝 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

---

**마지막 업데이트**: 2026-02-05
