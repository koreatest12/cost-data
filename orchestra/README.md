# Ansible AWX (Orchestra Server) 설치 가이드

Ansible AWX는 Ansible의 오픈소스 웹 기반 UI 및 오케스트레이션 도구입니다. 이 가이드는 Docker Compose를 사용하여 AWX를 설치하고 구성하는 방법을 안내합니다.

## 목차

- [개요](#개요)
- [시스템 요구사항](#시스템-요구사항)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [설정](#설정)
- [문제 해결](#문제-해결)

## 개요

Ansible AWX는 다음과 같은 기능을 제공합니다:

- **웹 기반 UI**: 브라우저를 통한 Ansible 작업 관리
- **역할 기반 접근 제어 (RBAC)**: 사용자 및 팀 권한 관리
- **작업 스케줄링**: 정기적인 작업 실행
- **인벤토리 관리**: 호스트 및 그룹 관리
- **플레이북 실행**: Ansible 플레이북의 중앙 집중식 실행
- **API 지원**: RESTful API를 통한 자동화

## 시스템 요구사항

### 최소 요구사항

- **OS**: Ubuntu 20.04+, CentOS 8+, RHEL 8+, 또는 기타 Linux 배포판
- **CPU**: 2 코어 이상
- **메모리**: 4GB RAM 이상 (권장: 8GB)
- **디스크**: 20GB 이상의 여유 공간
- **Docker**: 20.10 이상
- **Docker Compose**: 1.29 이상 또는 Docker Compose Plugin

### 네트워크 요구사항

- **포트 8080**: AWX 웹 UI 접속 (변경 가능)

## 설치 방법

### 방법 1: 자동 설치 스크립트 사용 (권장)

가장 쉬운 설치 방법은 제공된 설치 스크립트를 사용하는 것입니다:

```bash
# 저장소 루트 디렉토리에서 실행
cd orchestra
chmod +x install-awx.sh
./install-awx.sh
```

설치 스크립트는 다음 작업을 자동으로 수행합니다:

1. Docker 및 Docker Compose 설치 확인 (없으면 설치)
2. AWX 컨테이너 시작
3. 초기화 대기 및 상태 확인

### 방법 2: 수동 설치

Docker와 Docker Compose가 이미 설치되어 있다면 수동으로 설치할 수 있습니다:

```bash
# orchestra 디렉토리로 이동
cd orchestra

# AWX 컨테이너 시작
docker-compose up -d

# 로그 확인 (선택사항)
docker logs -f awx_web
```

### 설치 확인

설치가 완료되면 웹 브라우저에서 다음 URL로 접속합니다:

```
http://localhost:8080
```

기본 로그인 정보:
- **사용자명**: `admin`
- **비밀번호**: `admin`

## 사용 방법

### 1. 초기 로그인

1. 웹 브라우저에서 `http://localhost:8080` 접속
2. 사용자명 `admin`, 비밀번호 `admin`으로 로그인
3. 로그인 후 비밀번호 변경 권장

### 2. 인벤토리 추가

AWX에서 관리할 서버 인벤토리를 추가합니다:

1. 좌측 메뉴에서 **Inventories** 클릭
2. **Add** → **Add inventory** 클릭
3. 인벤토리 이름 입력 (예: "Web Servers")
4. **Save** 클릭

### 3. 호스트 추가

인벤토리에 서버 호스트를 추가합니다:

1. 생성한 인벤토리 클릭
2. **Hosts** 탭 선택
3. **Add** 클릭
4. 호스트 정보 입력:
   - Name: 서버 이름 또는 IP (예: `192.168.1.101`)
   - Variables: (선택사항) YAML 형식으로 변수 입력
   ```yaml
   ansible_user: ubuntu
   ansible_ssh_private_key_file: /path/to/key
   ```
5. **Save** 클릭

### 4. 프로젝트 추가

Ansible 플레이북이 포함된 Git 저장소를 프로젝트로 추가합니다:

1. 좌측 메뉴에서 **Projects** 클릭
2. **Add** 클릭
3. 프로젝트 정보 입력:
   - Name: 프로젝트 이름
   - SCM Type: Git
   - SCM URL: Git 저장소 URL
4. **Save** 클릭

### 5. Job Template 생성

플레이북을 실행할 Job Template을 생성합니다:

1. 좌측 메뉴에서 **Templates** 클릭
2. **Add** → **Add job template** 클릭
3. 템플릿 정보 입력:
   - Name: 템플릿 이름
   - Job Type: Run
   - Inventory: 이전에 생성한 인벤토리 선택
   - Project: 이전에 생성한 프로젝트 선택
   - Playbook: 실행할 플레이북 선택
4. **Save** 클릭

### 6. Job 실행

1. 생성한 Job Template 선택
2. **Launch** 버튼 클릭
3. 실행 로그를 실시간으로 확인

## 설정

### 보안 설정

프로덕션 환경에서는 다음 보안 설정을 권장합니다:

#### 1. 비밀번호 변경

`docker-compose.yml` 파일에서 다음 항목들을 변경하세요:

```yaml
environment:
  POSTGRES_PASSWORD: <강력한-비밀번호>
  DATABASE_PASSWORD: <강력한-비밀번호>
  SECRET_KEY: <임의의-긴-문자열>
  AWX_ADMIN_PASSWORD: <관리자-비밀번호>
```

#### 2. HTTPS 설정

프로덕션 환경에서는 HTTPS를 사용하는 것이 좋습니다. Nginx 리버스 프록시를 사용하여 SSL/TLS를 구성할 수 있습니다.

### 포트 변경

기본 포트(8080)를 변경하려면 `docker-compose.yml`에서 다음을 수정하세요:

```yaml
ports:
  - "9000:8052"  # 9000으로 변경
```

### 데이터 백업

AWX 데이터를 백업하려면:

```bash
# PostgreSQL 데이터베이스 백업
docker exec awx_postgres pg_dump -U awx awx > awx_backup_$(date +%Y%m%d).sql

# 볼륨 백업
docker run --rm -v orchestra_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/awx_data_backup_$(date +%Y%m%d).tar.gz /data
```

### 데이터 복구

백업에서 데이터를 복구하려면:

```bash
# PostgreSQL 데이터베이스 복구
cat awx_backup_20240117.sql | docker exec -i awx_postgres psql -U awx awx
```

## 운영 명령어

### 컨테이너 상태 확인

```bash
cd orchestra
docker-compose ps
```

### 로그 확인

```bash
# AWX 웹 로그
docker logs -f awx_web

# AWX Task 로그
docker logs -f awx_task

# PostgreSQL 로그
docker logs -f awx_postgres

# Redis 로그
docker logs -f awx_redis
```

### AWX 중지

```bash
cd orchestra
docker-compose stop
```

### AWX 재시작

```bash
cd orchestra
docker-compose restart
```

### AWX 완전 제거 (데이터 포함)

```bash
cd orchestra
docker-compose down -v
```

## 기존 inventory.ini 통합

이 저장소의 루트에 있는 `inventory.ini` 파일을 AWX에서 사용하려면:

### 방법 1: 파일 기반 인벤토리 (간단)

1. AWX에서 새 인벤토리 생성
2. 인벤토리 소스로 "Sourced from a Project" 선택
3. 프로젝트에 `inventory.ini` 파일 포함
4. AWX가 자동으로 인벤토리 동기화

### 방법 2: 수동 입력 (권장)

현재 `inventory.ini`의 내용:

```ini
[web_servers]
192.168.1.101 ansible_user=ubuntu
192.168.1.102 ansible_user=ubuntu
192.168.1.103 ansible_user=ubuntu

[deploy_server]
192.168.1.200 ansible_user=admin
```

AWX UI에서 다음과 같이 설정:

1. **Inventories** → **Add** → 인벤토리 생성 (예: "Production Servers")

2. **Groups** 추가:
   - Group 1: `web_servers`
   - Group 2: `deploy_server`

3. **Hosts** 추가:
   - Group: `web_servers`
     - Host: `192.168.1.101` (Variables: `ansible_user: ubuntu`)
     - Host: `192.168.1.102` (Variables: `ansible_user: ubuntu`)
     - Host: `192.168.1.103` (Variables: `ansible_user: ubuntu`)
   
   - Group: `deploy_server`
     - Host: `192.168.1.200` (Variables: `ansible_user: admin`)

## 문제 해결

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose logs

# 특정 컨테이너 로그
docker logs awx_web
docker logs awx_postgres
```

### 웹 UI에 접속할 수 없음

1. 컨테이너 상태 확인:
   ```bash
   docker-compose ps
   ```

2. 포트가 사용 중인지 확인:
   ```bash
   sudo netstat -tulpn | grep 8080
   ```

3. 방화벽 설정 확인:
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 8080
   
   # CentOS/RHEL
   sudo firewall-cmd --add-port=8080/tcp --permanent
   sudo firewall-cmd --reload
   ```

### PostgreSQL 연결 오류

PostgreSQL 컨테이너가 완전히 시작되기 전에 AWX가 연결을 시도할 수 있습니다:

```bash
# 컨테이너 재시작
docker-compose restart awx_web awx_task
```

### 메모리 부족

AWX는 최소 4GB RAM이 필요합니다. 시스템 메모리를 확인하세요:

```bash
free -h
```

메모리가 부족하면 swap 공간을 추가하거나 시스템 메모리를 증설하세요.

## 참고 자료

- [Ansible AWX 공식 문서](https://github.com/ansible/awx)
- [Ansible 문서](https://docs.ansible.com/)
- [Docker 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)

## 라이센스

이 프로젝트는 Apache License 2.0 하에 배포됩니다.

## 지원

문제가 발생하면 GitHub 이슈를 생성하거나 프로젝트 관리자에게 문의하세요.
