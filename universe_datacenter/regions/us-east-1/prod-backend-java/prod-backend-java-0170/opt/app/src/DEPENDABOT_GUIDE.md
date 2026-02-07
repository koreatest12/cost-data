# 📦 Dependabot 설정 가이드

## 개요

이 프로젝트는 GitHub Dependabot을 통해 모든 의존성을 자동으로 관리합니다. 이 문서는 Dependabot 설정 및 운영 방법을 설명합니다.

## 🎯 관리 대상

### 1. GitHub Actions
- **경로**: `/`
- **업데이트 주기**: 매일 오전 9시 (KST)
- **PR 제한**: 최대 10개
- **라벨**: `dependencies`, `github-actions`

### 2. Python 패키지

#### 메인 프로젝트
- **경로**: `/`
- **파일**: `requirements.txt`
- **업데이트 주기**: 매일 오전 9시 (KST)
- **PR 제한**: 최대 10개
- **라벨**: `dependencies`, `python`

#### KCA Monitor
- **경로**: `/scripts/kca-monitor`
- **파일**: `requirements.txt`
- **업데이트 주기**: 매일 오전 9시 (KST)
- **PR 제한**: 최대 5개
- **라벨**: `dependencies`, `python`, `kca-monitor`

### 3. Maven 의존성

#### 메인 프로젝트
- **경로**: `/`
- **파일**: `pom.xml`
- **업데이트 주기**: 매일 오전 9시 (KST)
- **PR 제한**: 최대 10개
- **라벨**: `dependencies`, `java`, `maven`

#### Microservices
각 마이크로서비스는 개별적으로 관리됩니다:

1. **Omni Algo Service**
   - 경로: `/services/omni-algo-service`
   - 라벨: `dependencies`, `java`, `algo-service`
   - 커밋 prefix: `chore(deps-algo)`

2. **Omni Cost Service**
   - 경로: `/services/omni-cost-service`
   - 라벨: `dependencies`, `java`, `cost-service`
   - 커밋 prefix: `chore(deps-cost)`

3. **Omni Job Service**
   - 경로: `/services/omni-job-service`
   - 라벨: `dependencies`, `java`, `job-service`
   - 커밋 prefix: `chore(deps-job)`

4. **Omni Security Service**
   - 경로: `/services/omni-security-service`
   - 라벨: `dependencies`, `java`, `security-service`
   - 커밋 prefix: `chore(deps-security)`

### 4. Docker 베이스 이미지

각 마이크로서비스의 Dockerfile을 주간 단위로 업데이트합니다.

- **업데이트 주기**: 매주 월요일 오전 9시 (KST)
- **PR 제한**: 서비스당 최대 3개
- **라벨**: `dependencies`, `docker`, `[service-name]`

## 🤖 자동화 워크플로우

### 1. Dependabot Auto-Merge
**파일**: `.github/workflows/dependabot-auto-merge.yml`

**기능**:
- 패치/마이너 버전 업데이트 자동 승인
- 자동 병합 (squash merge)
- 메이저 버전 업데이트 시 수동 검토 요청 코멘트

**트리거**: Dependabot PR 생성 시

**동작 방식**:
```yaml
패치/마이너 업데이트:
  1. PR 자동 승인
  2. Auto-merge 활성화
  3. CI 통과 후 자동 병합

메이저 업데이트:
  1. PR에 경고 코멘트 작성
  2. 수동 검토 대기
  3. 승인 후 수동 병합
```

### 2. Dependency Report Generator
**파일**: `.github/workflows/dependency-report.yml`

**기능**:
- Python 의존성 트리 생성
- Maven 의존성 트리 생성
- 보안 감사 (pip-audit, Safety, OWASP)
- 오래된 패키지 확인
- JSON 형식 보고서 생성

**트리거**:
- 매주 월요일 오전 10시 (KST)
- 수동 실행 (workflow_dispatch)
- requirements.txt, pom.xml 변경 시

**생성 파일**:
- `dependency_report.md`: 종합 보고서
- `dependabot_report.json`: JSON 형식 데이터
- `safety_report.json`: 보안 감사 결과
- `maven_deps.txt`: Maven 의존성 트리

**보안 취약점 발견 시**:
- 자동으로 GitHub Issue 생성
- 라벨: `security`, `dependencies`, `automated`

### 3. Dependency Update Notifications
**파일**: `.github/workflows/dependency-update-notification.yml`

**기능**:
- Dependabot PR에 상세 정보 코멘트
- 변경된 파일 목록 표시
- 자동 검토 체크리스트 제공
- 에코시스템별 라벨 자동 추가

**트리거**: Dependabot PR 생성/재오픈 시

## 📋 운영 가이드

### PR 검토 프로세스

#### 1. 패치/마이너 업데이트
이러한 업데이트는 자동으로 처리됩니다:
- ✅ 자동 승인
- ✅ 자동 병합 (CI 통과 시)
- ✅ 추가 조치 불필요

#### 2. 메이저 업데이트
수동 검토가 필요합니다:
1. PR 내용 확인
2. 변경 로그 검토
3. 호환성 문제 확인
4. 테스트 결과 확인
5. 승인 및 병합

### 수동 실행

의존성 보고서를 수동으로 생성하려면:

1. GitHub Actions 페이지 이동
2. "Dependency Report Generator" 워크플로우 선택
3. "Run workflow" 클릭
4. 결과는 Artifacts 및 저장소에 커밋됨

### 보안 알림 처리

보안 취약점 발견 시:

1. 자동 생성된 Issue 확인
2. 의존성 보고서 검토
3. 업데이트 또는 대안 검토
4. 신속하게 조치

## 🔧 설정 커스터마이징

### 업데이트 주기 변경

`.github/dependabot.yml` 파일에서 `schedule` 섹션 수정:

```yaml
schedule:
  interval: "daily"    # daily, weekly, monthly
  time: "09:00"        # HH:MM 형식
  timezone: "Asia/Seoul"
  day: "monday"        # weekly인 경우
```

### PR 제한 조정

```yaml
open-pull-requests-limit: 10  # 0-10 사이 값
```

### 라벨 변경

```yaml
labels:
  - "dependencies"
  - "custom-label"
```

### 커밋 메시지 형식

```yaml
commit-message:
  prefix: "chore(deps)"
  include: "scope"  # scope 포함 여부
```

## 📊 모니터링

### Dependabot 대시보드

GitHub 저장소에서:
1. Insights 탭
2. Dependency graph
3. Dependabot 섹션

### 보고서 확인

주간 보고서는 다음 위치에 저장됩니다:
- `dependency_report.md`: 종합 보고서
- `dependabot_report.json`: JSON 데이터

### Artifacts

각 워크플로우 실행 시:
- GitHub Actions > 워크플로우 실행 > Artifacts
- `dependency-report` 아카이브 다운로드

## 🚨 문제 해결

### Dependabot이 PR을 생성하지 않음

1. `.github/dependabot.yml` 파일 문법 확인
2. Dependabot 로그 확인 (Settings > Security > Dependabot)
3. 디렉토리 경로 확인
4. 패키지 파일 존재 확인

### 자동 병합이 작동하지 않음

1. Branch protection rules 확인
2. CI 워크플로우 상태 확인
3. GitHub Actions 권한 확인
4. `GITHUB_TOKEN` 권한 확인

### 보안 취약점 알림이 너무 많음

1. `.github/dependabot.yml`에서 특정 패키지 무시:
```yaml
ignore:
  - dependency-name: "package-name"
    versions: ["1.x", "2.x"]
```

2. 보안 수준 조정:
```yaml
security-advisories:
  - severity: "critical"  # critical, high, medium, low
```

## 🎓 모범 사례

### 1. 정기적인 검토
- 주간 보고서 확인
- 오래된 의존성 업데이트
- 보안 취약점 신속 대응

### 2. 테스트 커버리지
- 업데이트 전 충분한 테스트
- CI/CD 파이프라인 유지
- 회귀 테스트 수행

### 3. 문서화
- 주요 업데이트 변경사항 기록
- 호환성 이슈 문서화
- 팀 공유

### 4. 커뮤니케이션
- 메이저 업데이트 사전 공지
- 팀원과 영향 논의
- 롤백 계획 수립

## 📚 참고 자료

- [Dependabot 공식 문서](https://docs.github.com/en/code-security/dependabot)
- [Dependabot Configuration Reference](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [GitHub Actions 문서](https://docs.github.com/en/actions)

## 🆘 지원

문제가 발생하면:
1. [GitHub Issues](https://github.com/koreatest12/cost-data/issues)에 이슈 생성
2. 의존성 보고서 첨부
3. 에러 로그 포함

---

**마지막 업데이트**: 2026-02-05
**버전**: 1.0.0
