# Cost Data - 배포 현황 (Deployment Status)

## 배포 완료 일시 (Deployment Date)
2026-01-17

## 포트 번호 (Port Number)
**9999** - 모든 서비스가 포트 9999에서 실행됩니다.

## 배포된 컴포넌트 (Deployed Components)

### 1. Spring Boot 파일 관리 시스템
- **포트**: 9999
- **기능**: 파일 및 디렉토리 관리 REST API
- **JAR 파일**: `target/file-management-1.0.0.jar` (24MB)
- **설정 파일**: `src/main/resources/application.properties`

### 2. Python 서버 관리 시스템
- **스크립트**: `server_manager.py`
- **기능**: 서버 업그레이드, 용량 관리, 디스크 관리
- **데이터 저장**: `data/server_config.json`

### 3. 보안 뉴스 시스템
- **스크립트**: `security_news.py`
- **데이터**: `DB/` 디렉토리

### 4. 데모 시스템
- **스크립트**: `demo.py`
- **기능**: 시스템 기능 시연

## 배포 방법 (Deployment Methods)

### 방법 1: 빠른 시작 (개발/테스트용)
```bash
./quick-start.sh
```
- 로컬에서 즉시 실행
- 포트 9999에서 애플리케이션 시작
- 개발 및 테스트에 적합

### 방법 2: 전체 시스템 배포 (프로덕션용)
```bash
sudo ./deploy/deploy.sh
```
- `/opt/cost-data`에 설치
- systemd 서비스 등록
- 방화벽 자동 구성
- 자동 시작 설정 가능

### 방법 3: Docker 배포
```bash
# 단일 컨테이너
docker build -t cost-data .
docker run -d -p 9999:9999 --name cost-data-app cost-data

# Docker Compose
docker-compose up -d
```

### 방법 4: Ansible 대량 배포
```bash
ansible-playbook -i inventory.ini deploy/playbook.yml
```
- 여러 서버에 동시 배포
- `inventory.ini`에서 서버 목록 관리
- 일관된 배포 보장

## 배포 디렉토리 구조 (Deployment Directory Structure)

```
/opt/cost-data/              # 프로덕션 설치 디렉토리
├── cost-data.jar            # Spring Boot 애플리케이션 (24MB)
├── server_manager.py        # 서버 관리 시스템
├── demo.py                  # 데모 스크립트
├── security_news.py         # 보안 뉴스 시스템
├── uploads/                 # 업로드 파일 저장소
├── data/                    # 애플리케이션 데이터
│   └── server_config.json   # 서버 구성 파일
├── DB/                      # 데이터베이스 파일
│   ├── knowledge_base.md
│   ├── neural_memory.json.gz
│   └── total_news_history.md
└── deployment-info.txt      # 배포 정보
```

## 각 디렉토리별 기능 (Directory-Specific Functions)

모든 디렉토리 기능 설명은 `DIRECTORY_FEATURES.md` 파일 참조

### 주요 디렉토리:
- `/src/main/java/` - Spring Boot 애플리케이션 소스
- `/deploy/` - 배포 스크립트 및 설정
- `/uploads/` - 사용자 업로드 파일
- `/data/` - 애플리케이션 데이터
- `/DB/` - 데이터베이스 및 지식베이스

## 서비스 관리 (Service Management)

### Systemd 서비스 (프로덕션)
```bash
# 시작
sudo systemctl start cost-data

# 중지
sudo systemctl stop cost-data

# 재시작
sudo systemctl restart cost-data

# 상태 확인
sudo systemctl status cost-data

# 부팅 시 자동 시작
sudo systemctl enable cost-data

# 로그 보기
sudo journalctl -u cost-data -f
```

### Docker 서비스
```bash
# 시작
docker-compose up -d

# 중지
docker-compose down

# 로그
docker-compose logs -f

# 상태
docker ps
```

## API 엔드포인트 (API Endpoints)

### Base URL
```
http://localhost:9999/api
```

### 주요 엔드포인트
- `POST /api/files/create` - 파일 생성
- `POST /api/files/directory/create` - 디렉토리 생성
- `GET /api/files/list` - 파일 목록
- `GET /api/files/read?path=<path>` - 파일 읽기
- `GET /api/files/info?path=<path>` - 파일 정보
- `DELETE /api/files/delete?path=<path>` - 파일 삭제 (관리자)

### 헬스 체크
```
GET http://localhost:9999/actuator/health
```

## 사용자 계정 (User Accounts)

### 일반 사용자
- **Username**: `user`
- **Password**: `password`
- **권한**: 파일 생성, 조회, 읽기

### 관리자
- **Username**: `admin`
- **Password**: `admin`
- **권한**: 모든 기능 (삭제 포함)

## 방화벽 설정 (Firewall Configuration)

### UFW (Ubuntu/Debian)
```bash
sudo ufw allow 9999/tcp
sudo ufw status
```

### firewalld (CentOS/RHEL)
```bash
sudo firewall-cmd --permanent --add-port=9999/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

## 테스트 명령 (Test Commands)

### Spring Boot API 테스트
```bash
# 헬스 체크
curl http://localhost:9999/actuator/health

# 파일 생성 (인증 필요)
curl -u user:password -X POST http://localhost:9999/api/files/create \
  -H "Content-Type: application/json" \
  -d '{"path":"test.txt","content":"Hello Port 9999"}'

# 파일 목록
curl -u user:password http://localhost:9999/api/files/list
```

### Python 서버 관리 테스트
```bash
cd /opt/cost-data

# 서버 추가
python3 server_manager.py add --server-id test-server --cpu 4 --memory 8

# 서버 목록
python3 server_manager.py list

# 용량 체크
python3 server_manager.py check-capacity --server-id test-server
```

## 문제 해결 (Troubleshooting)

### 포트 확인
```bash
# 포트 9999가 열려있는지 확인
sudo netstat -tulpn | grep 9999
# 또는
sudo ss -tulpn | grep 9999
```

### 애플리케이션 로그
```bash
# Systemd 로그
sudo journalctl -u cost-data -n 100

# Docker 로그
docker-compose logs -f cost-data
```

### 프로세스 확인
```bash
ps aux | grep cost-data
ps aux | grep java
```

## 보안 고려사항 (Security Considerations)

1. **기본 비밀번호 변경** - 프로덕션에서는 반드시 변경
2. **HTTPS 설정** - 프로덕션 환경에서는 SSL/TLS 사용
3. **방화벽 규칙** - 필요한 IP만 허용
4. **정기 업데이트** - 보안 패치 적용
5. **로그 모니터링** - 비정상 접근 감시

## 백업 (Backup)

```bash
# 데이터 백업
sudo tar -czf cost-data-backup-$(date +%Y%m%d).tar.gz \
  /opt/cost-data/uploads \
  /opt/cost-data/data \
  /opt/cost-data/DB

# 백업 확인
ls -lh cost-data-backup-*.tar.gz
```

## 모니터링 (Monitoring)

```bash
# CPU 및 메모리
top -p $(pgrep -f cost-data.jar)

# 디스크 사용량
df -h /opt/cost-data
du -sh /opt/cost-data/*

# 네트워크 연결
sudo netstat -an | grep 9999
```

## 참고 문서 (Documentation)

- **메인 README**: `README.md`
- **배포 가이드**: `DEPLOYMENT.md`
- **디렉토리 기능**: `DIRECTORY_FEATURES.md`
- **기술 문서**: `DOCUMENTATION.md`

## 배포 체크리스트 (Deployment Checklist)

- [x] 포트를 8080에서 9999로 변경
- [x] Spring Boot 애플리케이션 빌드 성공 (24MB JAR)
- [x] 배포 스크립트 생성 (`deploy.sh`)
- [x] Systemd 서비스 파일 생성
- [x] Docker 배포 지원 (Dockerfile, docker-compose.yml)
- [x] Ansible 플레이북 생성
- [x] 디렉토리별 기능 문서화
- [x] 배포 가이드 문서 작성
- [x] Quick start 스크립트 생성
- [x] 모든 디렉토리 기능 매핑 완료

## 성공 기준 (Success Criteria)

✅ 애플리케이션이 포트 9999에서 실행
✅ 모든 API 엔드포인트가 정상 작동
✅ 파일 업로드/다운로드 기능 작동
✅ Python 서버 관리 시스템 작동
✅ 배포 스크립트 실행 가능
✅ Docker 컨테이너 실행 가능
✅ 문서화 완료

## 다음 단계 (Next Steps)

1. 프로덕션 서버에 배포 실행
2. SSL/TLS 인증서 설정
3. 모니터링 시스템 구축
4. 백업 자동화 설정
5. CI/CD 파이프라인 구축

---

**배포 준비 완료! (Ready for Deployment!)**

모든 컴포넌트가 포트 9999에서 작동하도록 설정되었습니다.
