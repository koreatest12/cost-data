# 배포 가이드 (Deployment Guide)

Cost Data 애플리케이션 배포 가이드 - 포트 9999

## 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [배포 방법](#배포-방법)
3. [디렉토리 구조](#디렉토리-구조)
4. [각 컴포넌트 기능](#각-컴포넌트-기능)
5. [서비스 관리](#서비스-관리)
6. [문제 해결](#문제-해결)

---

## 시스템 요구사항

### 필수 소프트웨어
- **Java**: JDK 17 이상
- **Maven**: 3.6 이상
- **Python**: 3.6 이상
- **운영체제**: Ubuntu 20.04+, CentOS 7+, 또는 다른 리눅스 배포판

### 하드웨어 권장사항
- **CPU**: 2코어 이상
- **메모리**: 2GB 이상
- **디스크**: 10GB 이상 여유 공간

---

## 배포 방법

### 방법 1: 자동 배포 스크립트 (권장)

```bash
# 저장소 클론
git clone https://github.com/koreatest12/cost-data.git
cd cost-data

# 배포 스크립트 실행
sudo ./deploy/deploy.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
- 필수 소프트웨어 확인
- 애플리케이션 빌드
- 시스템 서비스 설치
- 방화벽 구성
- 필요한 디렉토리 생성

### 방법 2: Docker 배포

```bash
# Docker 이미지 빌드 및 실행
docker-compose up -d

# 또는 Docker만 사용
docker build -t cost-data .
docker run -d -p 9999:9999 --name cost-data-app cost-data
```

### 방법 3: Ansible 대량 배포

여러 서버에 동시 배포:

```bash
# Ansible 설치 (필요한 경우)
sudo apt-get install ansible

# inventory.ini 파일 수정 (서버 IP 설정)
vi inventory.ini

# 배포 실행
ansible-playbook -i inventory.ini deploy/playbook.yml
```

### 방법 4: 수동 배포

```bash
# 1. 애플리케이션 빌드
mvn clean package -DskipTests

# 2. 설치 디렉토리 생성
sudo mkdir -p /opt/cost-data
sudo chown $USER:$USER /opt/cost-data

# 3. JAR 파일 복사
cp target/*.jar /opt/cost-data/cost-data.jar

# 4. Python 스크립트 복사
cp server_manager.py demo.py security_news.py /opt/cost-data/

# 5. 필요한 디렉토리 생성
mkdir -p /opt/cost-data/uploads /opt/cost-data/data

# 6. systemd 서비스 설치
sudo cp deploy/cost-data.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cost-data
sudo systemctl start cost-data

# 7. 방화벽 설정
sudo ufw allow 9999/tcp
```

---

## 디렉토리 구조

배포 후 디렉토리 구조:

```
/opt/cost-data/                    # 메인 설치 디렉토리
├── cost-data.jar                  # Spring Boot 애플리케이션
├── server_manager.py              # 서버 관리 시스템
├── demo.py                        # 데모 스크립트
├── security_news.py               # 보안 뉴스 시스템
├── uploads/                       # 파일 업로드 디렉토리
│   └── (사용자 업로드 파일)
├── data/                          # 데이터 저장 디렉토리
│   └── server_config.json         # 서버 구성 파일
├── DB/                            # 데이터베이스 파일
│   ├── knowledge_base.md
│   ├── neural_memory.json.gz
│   └── total_news_history.md
└── deployment-info.txt            # 배포 정보

/etc/systemd/system/
└── cost-data.service              # Systemd 서비스 파일
```

---

## 각 컴포넌트 기능

### 1. Spring Boot 파일 관리 시스템 (포트 9999)

**기능:**
- 파일 생성, 읽기, 삭제
- 디렉토리 관리
- 사용자 인증 및 권한 관리

**엔드포인트:**
- `POST /api/files/create` - 파일 생성
- `POST /api/files/directory/create` - 디렉토리 생성
- `GET /api/files/list` - 파일 목록 조회
- `GET /api/files/read` - 파일 읽기
- `GET /api/files/info` - 파일 정보
- `DELETE /api/files/delete` - 파일 삭제 (관리자만)

**디렉토리:** `/opt/cost-data/`

**사용 예시:**
```bash
# 파일 생성
curl -u user:password -X POST http://localhost:9999/api/files/create \
  -H "Content-Type: application/json" \
  -d '{"path":"test.txt","content":"Hello World"}'

# 파일 목록 조회
curl -u user:password http://localhost:9999/api/files/list
```

### 2. Python 서버 관리 시스템

**기능:**
- 서버 업그레이드 (CPU, 메모리)
- 용량 체크 및 증설
- 디스크 설치 및 관리

**디렉토리:** `/opt/cost-data/`

**사용 예시:**
```bash
cd /opt/cost-data

# 서버 추가
python3 server_manager.py add --server-id web-1 --cpu 4 --memory 8

# 용량 체크
python3 server_manager.py check-capacity --server-id web-1

# 디스크 설치
python3 server_manager.py install-disk --server-id web-1 --disk-size 500 --disk-type SSD
```

### 3. 데모 스크립트

**기능:** 시스템 기능 시연

**디렉토리:** `/opt/cost-data/demo.py`

**사용 예시:**
```bash
cd /opt/cost-data
python3 demo.py
```

### 4. 보안 뉴스 시스템

**기능:** 보안 관련 뉴스 및 정보 수집

**디렉토리:** `/opt/cost-data/security_news.py`

**데이터 위치:** `/opt/cost-data/DB/`

---

## 서비스 관리

### Systemd 서비스 명령어

```bash
# 서비스 시작
sudo systemctl start cost-data

# 서비스 중지
sudo systemctl stop cost-data

# 서비스 재시작
sudo systemctl restart cost-data

# 서비스 상태 확인
sudo systemctl status cost-data

# 부팅 시 자동 시작 활성화
sudo systemctl enable cost-data

# 부팅 시 자동 시작 비활성화
sudo systemctl disable cost-data

# 로그 보기
sudo journalctl -u cost-data -f
```

### 서비스 상태 확인

```bash
# 애플리케이션 헬스 체크
curl http://localhost:9999/actuator/health

# 포트 확인
sudo netstat -tulpn | grep 9999
# 또는
sudo ss -tulpn | grep 9999

# 프로세스 확인
ps aux | grep cost-data
```

### Docker 서비스 관리

```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down

# 로그 보기
docker-compose logs -f

# 컨테이너 상태 확인
docker ps
```

---

## 접근 정보

### API 엔드포인트
- **Base URL**: `http://localhost:9999/api`
- **Health Check**: `http://localhost:9999/actuator/health`

### 기본 사용자 계정

**일반 사용자:**
- Username: `user`
- Password: `password`
- 권한: 파일 생성, 조회, 읽기

**관리자:**
- Username: `admin`
- Password: `admin`
- 권한: 모든 기능 (삭제 포함)

---

## 문제 해결

### 1. 포트가 이미 사용 중

```bash
# 포트 9999를 사용하는 프로세스 확인
sudo lsof -i :9999

# 프로세스 종료 (필요한 경우)
sudo kill -9 <PID>
```

### 2. 서비스 시작 실패

```bash
# 로그 확인
sudo journalctl -u cost-data -n 50

# Java 설치 확인
java -version

# JAR 파일 존재 확인
ls -l /opt/cost-data/cost-data.jar

# 권한 확인
ls -la /opt/cost-data/
```

### 3. 방화벽 문제

```bash
# UFW 방화벽 상태 확인
sudo ufw status

# 포트 9999 허용
sudo ufw allow 9999/tcp

# firewalld 확인 (CentOS/RHEL)
sudo firewall-cmd --list-ports
sudo firewall-cmd --permanent --add-port=9999/tcp
sudo firewall-cmd --reload
```

### 4. 권한 문제

```bash
# 디렉토리 권한 수정
sudo chown -R costdata:costdata /opt/cost-data
sudo chmod -R 755 /opt/cost-data

# uploads 디렉토리 쓰기 권한
sudo chmod 777 /opt/cost-data/uploads
```

### 5. 빌드 실패

```bash
# Maven 캐시 정리
mvn clean

# 의존성 재다운로드
mvn dependency:purge-local-repository

# 테스트 없이 빌드
mvn clean package -DskipTests
```

---

## 업그레이드 및 재배포

### 애플리케이션 업데이트

```bash
# 1. 최신 코드 가져오기
git pull origin main

# 2. 서비스 중지
sudo systemctl stop cost-data

# 3. 재빌드
mvn clean package -DskipTests

# 4. JAR 파일 교체
sudo cp target/*.jar /opt/cost-data/cost-data.jar

# 5. 서비스 시작
sudo systemctl start cost-data

# 6. 상태 확인
sudo systemctl status cost-data
```

### Docker 업데이트

```bash
# 1. 최신 코드 가져오기
git pull origin main

# 2. 컨테이너 중지 및 제거
docker-compose down

# 3. 이미지 재빌드
docker-compose build

# 4. 컨테이너 시작
docker-compose up -d
```

---

## 백업 및 복구

### 데이터 백업

```bash
# 데이터 디렉토리 백업
sudo tar -czf cost-data-backup-$(date +%Y%m%d).tar.gz \
  /opt/cost-data/uploads \
  /opt/cost-data/data \
  /opt/cost-data/DB

# 백업 파일 확인
ls -lh cost-data-backup-*.tar.gz
```

### 데이터 복구

```bash
# 백업에서 복구
sudo tar -xzf cost-data-backup-YYYYMMDD.tar.gz -C /

# 권한 재설정
sudo chown -R costdata:costdata /opt/cost-data

# 서비스 재시작
sudo systemctl restart cost-data
```

---

## 모니터링

### 로그 모니터링

```bash
# 실시간 로그 보기
sudo journalctl -u cost-data -f

# 최근 100줄 로그
sudo journalctl -u cost-data -n 100

# 특정 날짜 로그
sudo journalctl -u cost-data --since "2024-01-01" --until "2024-01-02"
```

### 리소스 모니터링

```bash
# CPU 및 메모리 사용량
top -p $(pgrep -f cost-data.jar)

# 또는 htop 사용
htop -p $(pgrep -f cost-data.jar)

# 디스크 사용량
df -h /opt/cost-data
du -sh /opt/cost-data/*
```

---

## 보안 고려사항

1. **기본 비밀번호 변경**: 프로덕션 환경에서는 반드시 기본 사용자 비밀번호를 변경하세요.
2. **HTTPS 사용**: 프로덕션에서는 HTTPS를 사용하도록 설정하세요.
3. **방화벽 설정**: 필요한 포트만 열어두세요.
4. **정기 업데이트**: 보안 패치를 정기적으로 적용하세요.
5. **로그 모니터링**: 비정상적인 접근을 주시하세요.

---

## 추가 정보

- **프로젝트 저장소**: https://github.com/koreatest12/cost-data
- **이슈 보고**: GitHub Issues 사용
- **문서**: README.md 및 DOCUMENTATION.md 참조

---

배포에 문제가 있거나 질문이 있으시면 GitHub Issues에 문의해 주세요.
