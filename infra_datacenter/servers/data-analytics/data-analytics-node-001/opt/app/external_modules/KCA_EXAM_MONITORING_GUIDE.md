# 🎓 KCA 정보보안기사 시험 자동 알림 시스템

## 📌 시스템 개요

이 시스템은 **KCA(한국방송통신전파진흥원) 정보보안기사 시험 공지사항**을 매시간 자동으로 확인하고, 새로운 공지사항이나 시험 일정 변경이 있을 때 자동으로 알림을 보내는 시스템입니다.

### ✨ 주요 기능

1. **자동 모니터링**: 매시간 정각에 KCA 웹사이트 자동 크롤링
2. **즉각 알림**: 새 공지사항 발견 시 GitHub Issue로 자동 알림
3. **히스토리 보관**: 모든 공지사항과 변경사항을 자동으로 저장
4. **시험 일정 추적**: 2026년도 정보보안기사 시험 일정 변경 감지

## 🚀 시작하기

### 1. 워크플로우 활성화 확인

시스템이 설치되면 자동으로 다음과 같이 작동합니다:

```
✅ 매시간 00분에 자동 실행
✅ 새 공지사항 발견 시 Issue 생성
✅ 변경사항 자동 커밋 및 저장
```

### 2. 수동 실행 방법

즉시 확인하고 싶다면 GitHub에서 수동으로 실행할 수 있습니다:

1. GitHub 저장소의 **Actions** 탭으로 이동
2. 왼쪽 메뉴에서 **"KCA 정보보안기사 시험 모니터링"** 워크플로우 선택
3. 오른쪽 상단의 **"Run workflow"** 버튼 클릭
4. 브랜치 선택 후 **"Run workflow"** 실행

### 3. 알림 받기

새로운 공지사항이 발견되면:

1. **Issues** 탭에 새 Issue가 자동 생성됩니다
2. Issue 제목: `🔔 KCA 정보보안기사 새 공지사항 - [날짜]`
3. 라벨: `notification`, `kca-exam`, `auto-generated`
4. 내용에 공지사항 상세 정보 포함

### 4. 알림 받는 방법 설정

#### GitHub 알림 받기
1. GitHub 저장소 우측 상단의 **Watch** 버튼 클릭
2. **Custom** 선택
3. **Issues** 체크박스 활성화
4. 이메일로 새 Issue 알림 수신

#### 모바일 앱으로 받기
1. GitHub 모바일 앱 설치 (iOS/Android)
2. 저장소를 Watch 설정
3. 앱 알림 허용
4. 실시간 푸시 알림 수신

## 📊 모니터링 대상

### KCA 국가기술자격검정 사이트
- **공지사항**: https://www.cq.or.kr/qh_cusgm01_001.do
- **시험 일정**: https://www.cq.or.kr/qh_quagm03_001.do

### 감지하는 정보
- ✅ 2026년도 시험 일정 공고
- ✅ 접수 기간 변경
- ✅ 시험 방법 변경 (CBT 관련)
- ✅ 합격 기준 변경
- ✅ 응시 자격 변경
- ✅ 기타 중요 공지사항

## 📂 저장되는 데이터

### 디렉토리 구조
```
data/kca-notifications/
├── latest.json              # 최신 크롤링 데이터
├── latest_report.md         # 최신 리포트 (마크다운)
├── history_YYYYMMDD_HHMMSS.json  # 변경 히스토리
└── changes_YYYYMMDD_HHMMSS.json  # 변경사항 상세
```

### 데이터 확인 방법
1. GitHub 저장소의 `data/kca-notifications/` 디렉토리 확인
2. `latest_report.md` 파일에서 최신 요약 확인
3. `latest.json` 파일에서 전체 데이터 확인

## ⚙️ 설정 변경

### 크롤링 주기 변경

`.github/workflows/kca-exam-monitor.yml` 파일 수정:

```yaml
# 현재: 매시간 실행
schedule:
  - cron: '0 * * * *'

# 2시간마다 실행하려면:
schedule:
  - cron: '0 */2 * * *'

# 매일 오전 9시, 오후 6시 실행하려면:
schedule:
  - cron: '0 0,9 * * *'  # UTC 시간 (KST -9시간)
```

### 알림 조건 변경

워크플로우 파일의 다음 섹션 수정:
```yaml
- name: 새 공지사항 Issue 생성
  if: steps.monitor.outputs.has_changes == 'true'
```

## 🔍 모니터링 결과 확인

### 1. GitHub Actions 로그
- **Actions** 탭에서 워크플로우 실행 기록 확인
- 각 실행의 상세 로그 확인 가능
- 크롤링 성공/실패 여부 확인

### 2. Summary 확인
- 각 워크플로우 실행의 Summary 섹션
- 최신 리포트 자동 표시
- 변경사항 요약 확인

### 3. Issues 확인
- 새 공지사항은 자동으로 Issue 생성
- `kca-exam` 라벨로 필터링 가능
- 히스토리 추적 용이

## 🛠️ 문제 해결

### 크롤링 실패 (403 Forbidden)
**원인**: KCA 웹사이트의 봇 접근 차단

**해결방법**:
1. GitHub Actions 환경에서는 일반적으로 정상 작동
2. 로컬 테스트 시 발생하는 것은 정상
3. 지속적인 차단 시 User-Agent 변경 필요

### 데이터가 업데이트되지 않음
**확인사항**:
1. 워크플로우가 정상 실행되는지 확인
2. GitHub Actions 권한 확인 (Issues 생성 권한)
3. 브랜치 푸시 권한 확인

### 알림을 받지 못함
**확인사항**:
1. 저장소 Watch 설정 확인
2. GitHub 알림 설정 확인
3. 이메일 알림 필터 확인

### 워크플로우 실행 실패
**확인사항**:
1. Actions 로그에서 에러 메시지 확인
2. 의존성 설치 실패 여부 확인
3. Python 스크립트 오류 확인

## 📱 알림 활용 팁

### 1. 라벨 기반 필터링
- `kca-exam` 라벨로 시험 관련 Issue만 보기
- `notification` 라벨로 자동 알림만 보기

### 2. 이메일 필터 설정
Gmail 필터 예시:
```
from:notifications@github.com
subject:"KCA 정보보안기사"
label:중요
```

### 3. 슬랙/디스코드 연동
GitHub Actions에 웹훅 추가:
```yaml
- name: 슬랙 알림
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: '새로운 정보보안기사 공지사항이 있습니다!'
  if: steps.monitor.outputs.has_changes == 'true'
```

## 📈 활용 사례

### 수험생
- 시험 일정 변경 즉시 확인
- 접수 기간 놓치지 않기
- 중요 공지사항 실시간 수신

### 학원/교육기관
- 수강생 안내 자료 업데이트
- 커리큘럼 일정 조정
- 공지사항 자동 전달

### 기업 인사팀
- 직원 자격증 취득 지원
- 사내 공지사항 전달
- 교육 일정 관리

## 🔗 관련 링크

- [KCA 국가기술자격검정](https://www.cq.or.kr/)
- [Q-net 홈페이지](https://www.q-net.or.kr/)
- [정보보안기사 정보 (나무위키)](https://namu.wiki/w/정보보안기사)

## 💡 추가 기능 제안

다음과 같은 기능을 추가하고 싶다면 Issue를 생성해주세요:

- ⬜ 카카오톡 알림 연동
- ⬜ SMS 알림 기능
- ⬜ 정보보안산업기사 별도 트래킹
- ⬜ 타 자격증 모니터링 확장
- ⬜ 웹 대시보드 구축

## 📞 문의 및 지원

- **버그 리포트**: GitHub Issues
- **기능 제안**: GitHub Discussions
- **긴급 문의**: Repository Maintainer에게 연락

---

**마지막 업데이트**: 2026-02-05
**버전**: 1.0.0
**상태**: ✅ 활성화됨
