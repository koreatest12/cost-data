# 🌌 Omni-Intelligence Hub

![Data](https://img.shields.io/badge/PokemonGO-Data_Synced-blue) ![Status](https://img.shields.io/badge/System-Operational-green) ![Dependencies](https://img.shields.io/badge/Dependencies-Auto_Managed-success) ![Security](https://img.shields.io/badge/Security-Monitored-red)

## 🚀 System Status (2026-02-05 22:03)
- **Data Path:** `pokemon-go-data/` (JSON Aggregated)
- **Services:** 4 Microservices Built & Pushed
- **Dependabot:** ✅ Active (Python, Maven, Docker)
- **Security Monitoring:** ✅ Daily Scans
- **Homepage:** [View Live](https://koreatest12.github.io/cost-data/)

## 📦 자동 의존성 관리 (Dependabot)

이 프로젝트는 **Dependabot**을 통해 모든 의존성을 자동으로 관리합니다.

### 🔄 관리 대상
- **GitHub Actions**: 매일 오전 9시 (KST) 자동 업데이트
- **Python 패키지** (pip): 메인 프로젝트 및 KCA 모니터 스크립트
- **Maven 의존성**: 메인 프로젝트 + 4개 마이크로서비스
  - omni-algo-service
  - omni-cost-service
  - omni-job-service
  - omni-security-service
- **Docker 베이스 이미지**: 매주 월요일 업데이트

### ⚡ 자동화 기능
- ✅ 패치/마이너 버전 자동 승인 및 병합
- ✅ 보안 취약점 자동 스캔 (pip-audit, Safety, OWASP)
- ✅ 주간 의존성 상태 보고서 생성
- ✅ 메이저 버전 업데이트 시 수동 검토 알림
- ✅ 취약점 발견 시 자동 이슈 생성

## 🛠️ 기술 스택

### Backend
- **Spring Boot 3.2.1** (Java 17)
- **Spring Security** (인증/인가)
- **Maven** (빌드 도구)

### Data & Analytics
- **Python 3.11**
- **Pandas, NumPy** (데이터 처리)
- **Scikit-Learn** (머신러닝)
- **SHAP** (모델 해석)

### DevOps
- **Docker** (컨테이너화)
- **Kubernetes** (오케스트레이션)
- **GitHub Actions** (CI/CD)
- **Dependabot** (의존성 관리)

## 🏗️ 마이크로서비스 아키텍처

```
services/
├── omni-algo-service     # 알고리즘 처리 및 데이터 분석
├── omni-cost-service     # 비용 데이터 관리
├── omni-job-service      # 작업 스케줄링 및 배치 처리
└── omni-security-service # 인증 및 보안 관리
```

각 서비스는 독립적으로:
- Docker 컨테이너로 패키징
- Kubernetes로 배포
- Maven으로 빌드
- Dependabot으로 의존성 관리

## 🚀 시작하기

### 필수 요구사항
- Java 17+
- Python 3.11+
- Maven 3.8+
- Docker
- Kubernetes (선택사항)

### 로컬 개발

```bash
# 저장소 클론
git clone https://github.com/koreatest12/cost-data.git
cd cost-data

# Python 의존성 설치
pip install -r requirements.txt

# Maven 빌드
mvn clean install

# Spring Boot 실행
mvn spring-boot:run

# 또는 Docker로 실행
docker build -t cost-data .
docker run -p 8080:8080 cost-data
```

### 마이크로서비스 빌드

```bash
# 모든 서비스 빌드
cd services
for service in omni-*-service; do
  cd $service
  mvn clean package
  docker build -t $service:latest .
  cd ..
done
```

## 📊 주요 기능

### 1. 자동 의존성 관리
- Dependabot을 통한 24/7 의존성 모니터링
- 자동 PR 생성 및 병합
- 보안 취약점 실시간 알림

### 2. CI/CD 파이프라인
- GitHub Actions 기반 자동화
- 자동 빌드, 테스트, 배포
- PR 자동 검토 (Claude Code)

### 3. 보안 감사
- 일일 보안 스캔
- pip-audit, Safety, OWASP 도구 활용
- 취약점 발견 시 자동 이슈 생성

### 4. KCA 시험 모니터링
- 자동 공지사항 수집
- 데이터베이스 업데이트
- 이메일/슬랙 알림

### 5. 데이터 분석
- Pandas 기반 데이터 처리
- 머신러닝 파이프라인
- 시각화 및 보고서 생성

## 📚 문서

- [API 문서](./public/api/)
- [프로젝트 Wiki](./public/wiki/)
- [Agent 가이드](./AGENT_GUIDE.md)
- [KCA 모니터링 가이드](./KCA_EXAM_MONITORING_GUIDE.md)
- [Claude Code 매뉴얼](./CLAUDE_CODE_MANUAL_KR.md)

## 🔧 GitHub Actions 워크플로우

| 워크플로우 | 설명 | 실행 주기 |
|----------|------|---------|
| `dependabot-auto-merge.yml` | Dependabot PR 자동 병합 | PR 생성 시 |
| `dependency-report.yml` | 의존성 보고서 생성 | 매주 월요일 |
| `dependency-update-notification.yml` | 업데이트 알림 | PR 생성 시 |
| `ci-check.yml` | CI 테스트 및 빌드 | Push/PR 시 |
| `kca-exam-monitor.yml` | KCA 시험 모니터링 | 매시간 |
| `omni_pipeline.yml` | 통합 파이프라인 | Daily |

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Dependabot이 자동으로 의존성을 관리하므로, 보안 업데이트는 자동으로 처리됩니다.

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📧 연락처

- **Repository**: [koreatest12/cost-data](https://github.com/koreatest12/cost-data)
- **Issues**: [GitHub Issues](https://github.com/koreatest12/cost-data/issues)
- **Homepage**: [Project Website](https://koreatest12.github.io/cost-data/)

---

**🤖 Powered by Dependabot** | **🔒 Security First** | **⚡ Auto-Everything**
