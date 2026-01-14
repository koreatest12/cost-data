# 배포 서버 네트워크 설치 워크플로우 가이드
# Deployment Server Network Installation Workflow Guide

## 개요 (Overview)

이 워크플로우는 배포 서버에 네트워크 관련 도구를 자동으로 설치하고, 실패 시 최대 99,999번까지 재시도하는 강력한 자동화 시스템입니다.

This workflow automatically installs network tools on deployment servers and retries up to 99,999 times on failure.

## 주요 기능 (Key Features)

### 1. 자동 재시도 메커니즘 (Automatic Retry Mechanism)
- ✅ 최대 99,999번까지 자동 재시도
- ✅ 지수 백오프(Exponential Backoff) 대기 시간
- ✅ 성공할 때까지 계속 실행

### 2. 네트워크 도구 설치 (Network Tools Installation)
설치되는 도구들:
- `net-tools` - ifconfig, netstat 등
- `curl` - HTTP 클라이언트
- `wget` - 파일 다운로더
- `iputils-ping` - ping 명령어
- `dnsutils` - DNS 조회 도구
- `netcat` - 네트워크 유틸리티
- `traceroute` - 네트워크 경로 추적
- `nmap` - 네트워크 스캐너
- `tcpdump` - 패킷 분석
- `iptables` - 방화벽 관리
- `ufw` - 방화벽 프론트엔드

### 3. 방화벽 자동 구성 (Automatic Firewall Configuration)
자동으로 개방되는 포트:
- `22/tcp` - SSH
- `80/tcp` - HTTP
- `443/tcp` - HTTPS
- `8080/tcp` - 애플리케이션 서버

### 4. 설치 검증 (Installation Verification)
- 네트워크 명령어 가용성 확인
- 인터넷 연결 테스트 (Google DNS 8.8.8.8)
- 설치 로그 자동 저장

## 사용 방법 (Usage)

### 방법 1: 자동 실행 (Automatic Execution)

워크플로우는 `main` 브랜치에 코드가 push될 때 자동으로 실행됩니다.

```bash
git push origin main
```

### 방법 2: 수동 실행 (Manual Execution)

1. GitHub 저장소로 이동
2. **Actions** 탭 클릭
3. **Deploy Server Network Installation with Retry** 워크플로우 선택
4. **Run workflow** 버튼 클릭
5. 다음 정보 입력:
   - **서버 호스트 주소**: 배포할 서버의 IP 주소 (예: `123.123.123.123`)
   - **서버 포트**: SSH 포트 (기본값: `22`)
   - **서버 사용자명**: SSH 사용자 (기본값: `root`)
   - **최대 재시도 횟수**: 재시도 횟수 (기본값: `99999`)
6. **Run workflow** 버튼 클릭하여 실행

### 방법 3: GitHub CLI 사용 (Using GitHub CLI)

```bash
gh workflow run "Deploy Server Network Installation with Retry" \
  -f server_host="123.123.123.123" \
  -f server_port="22" \
  -f server_user="root" \
  -f max_retries="99999"
```

## 워크플로우 구조 (Workflow Structure)

### Job 1: deploy-with-retry
로컬 환경에서 네트워크 도구 설치 및 테스트

**단계:**
1. 소스 코드 체크아웃
2. Python 환경 설정
3. 필수 패키지 설치
4. 설치 스크립트 생성
5. 네트워크 설치 실행 (재시도 로직 포함)
6. 설치 로그 업로드
7. 결과 요약

### Job 2: deploy-to-remote-server (선택사항)
원격 서버에 SSH로 접속하여 설치

**필요 조건:**
- `SERVER_PASSWORD` 또는 `SSH_PRIVATE_KEY` Secret 설정
- 서버 정보 입력 (수동 실행 시)

**단계:**
1. 원격 설치 스크립트 생성
2. SSH로 원격 서버 접속
3. 네트워크 도구 설치 (최대 99,999번 재시도)

## 재시도 로직 상세 (Retry Logic Details)

### 대기 시간 계산
```python
wait_time = min(10 * attempt, 300)  # 최대 5분
```

예시:
- 1차 시도 실패 → 10초 대기
- 2차 시도 실패 → 20초 대기
- 3차 시도 실패 → 30초 대기
- ...
- 30차 이후 → 300초(5분) 대기 고정

### 종료 조건
1. **성공**: 모든 설치가 완료되고 검증이 통과되면 즉시 종료
2. **최대 재시도**: 99,999번 시도 후에도 실패하면 종료
3. **타임아웃**: 8시간(480분) 초과 시 자동 종료

## 로그 및 아티팩트 (Logs and Artifacts)

### 설치 로그
- 파일명: `installation_log.txt`
- 위치: 워크플로우 아티팩트
- 보존 기간: 30일

### 로그 내용
- 각 시도마다 타임스탬프 기록
- 설치 진행 상황
- 성공/실패 메시지
- 네트워크 상태 정보

### 로그 다운로드 방법
1. GitHub Actions 실행 결과 페이지 접속
2. **Artifacts** 섹션에서 `installation-log-{run_number}` 다운로드

## Secrets 설정 (Secret Configuration)

원격 서버 배포를 위해 다음 Secret을 설정하세요:

### 방법 1: 비밀번호 사용
```
이름: SERVER_PASSWORD
값: 서버 SSH 비밀번호
```

### 방법 2: SSH 키 사용 (권장)
```
이름: SSH_PRIVATE_KEY
값: SSH 개인 키 내용
```

**Secret 설정 방법:**
1. GitHub 저장소 → **Settings**
2. **Secrets and variables** → **Actions**
3. **New repository secret** 클릭
4. Secret 이름과 값 입력
5. **Add secret** 클릭

## 문제 해결 (Troubleshooting)

### 문제 1: 설치가 계속 실패함
**원인**: 네트워크 연결 불안정, 패키지 저장소 문제

**해결 방법**:
1. 로그 파일 확인
2. 서버 네트워크 연결 확인
3. 패키지 저장소 URL 확인

### 문제 2: SSH 연결 실패
**원인**: 잘못된 서버 정보 또는 방화벽 차단

**해결 방법**:
1. 서버 호스트, 포트, 사용자명 확인
2. SSH Secret 설정 확인
3. 서버 방화벽에서 GitHub Actions IP 허용

### 문제 3: 타임아웃 발생
**원인**: 8시간 실행 제한 초과

**해결 방법**:
1. 재시도 횟수 줄이기
2. 대기 시간 조정
3. 별도의 서버에서 직접 실행

## 모니터링 (Monitoring)

### GitHub Actions UI
- 실행 상태 실시간 확인
- 각 단계별 로그 확인
- 전체 실행 시간 확인

### Job Summary
워크플로우 실행 완료 후 요약 정보 제공:
- 실행 시간
- 워크플로우 ID
- 최대 재시도 횟수
- 마지막 50줄 로그

## 보안 고려사항 (Security Considerations)

1. **Secret 관리**: SSH 키와 비밀번호를 GitHub Secrets에 안전하게 저장
2. **방화벽 설정**: 필요한 포트만 개방
3. **로그 보안**: 민감한 정보가 로그에 포함되지 않도록 주의
4. **권한 관리**: 최소 권한 원칙 적용

## 성능 최적화 (Performance Optimization)

1. **병렬 설치**: 가능한 도구들을 병렬로 설치
2. **캐싱**: Python 패키지 캐싱 활용
3. **타임아웃**: 각 설치 작업에 적절한 타임아웃 설정

## 확장 가능성 (Extensibility)

### 추가 네트워크 도구 설치
`deploy_network_installer.py`의 `tools` 리스트에 추가:

```python
tools = [
    'net-tools',
    'curl',
    # 여기에 새로운 도구 추가
    'your-tool-name',
]
```

### 추가 포트 개방
방화벽 설정 섹션에 포트 추가:

```python
ports = ['22', '80', '443', '8080', '3000']  # 3000 포트 추가
```

### 커스텀 검증 로직
`verify_installation()` 함수에 추가 검증 코드 작성

## 예제 시나리오 (Example Scenarios)

### 시나리오 1: 개발 서버 설정
```bash
gh workflow run "Deploy Server Network Installation with Retry" \
  -f server_host="dev.example.com" \
  -f server_user="developer" \
  -f max_retries="100"
```

### 시나리오 2: 프로덕션 서버 설정
```bash
gh workflow run "Deploy Server Network Installation with Retry" \
  -f server_host="prod.example.com" \
  -f server_user="admin" \
  -f max_retries="99999"
```

### 시나리오 3: 로컬 테스트
main 브랜치에 push하면 GitHub Actions 러너에서 자동 실행

## 참고 자료 (References)

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [SSH Action 문서](https://github.com/appleboy/ssh-action)
- [UFW 방화벽 가이드](https://help.ubuntu.com/community/UFW)

## 라이센스 (License)

이 워크플로우는 저장소의 라이센스를 따릅니다.

## 지원 (Support)

문제가 발생하면 GitHub Issues에 보고해 주세요.

---

**버전**: 1.0.0  
**최종 업데이트**: 2026-01-14
