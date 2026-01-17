
# Cost Data - File Management System

Spring Boot 애플리케이션으로 파일 및 디렉토리 관리 기능과 권한 인증, 그리고 **고급 방화벽 보안 기능**을 제공합니다.

## 🔥 새로운 방화벽 기능

이 시스템은 이제 **완전한 방화벽 및 보안 기능**을 포함합니다:

### Java Spring Boot 방화벽 기능
- ✅ **IP 기반 접근 제어**: 화이트리스트/블랙리스트 관리
- ✅ **속도 제한 (Rate Limiting)**: DDoS 공격 방지
- ✅ **실시간 방화벽 관리 API**: 관리자 전용 엔드포인트
- ✅ **보안 헤더**: CSP, Frame Options, Content Type Protection
- ✅ **요청 필터링 및 검증**

### Python 서버 관리 방화벽 기능
- ✅ **방화벽 설치 및 구성**: UFW, Windows Firewall, iptables 지원
- ✅ **방화벽 규칙 관리**: 포트, 프로토콜, 방향 제어
- ✅ **고급 보안 업그레이드**: DDoS 보호, 침입 탐지, 속도 제한
- ✅ **지리적 차단 (Geo-blocking)** 지원

## 기능

- 파일 생성 및 관리
- 디렉토리 생성 및 관리
- 파일 목록 조회
- 파일 읽기
- 파일/디렉토리 삭제 (관리자 권한 필요)
- Spring Security를 통한 권한 관리
- **🔥 IP 기반 방화벽 보호**
- **🔥 요청 속도 제한**
- **🔥 실시간 방화벽 규칙 관리**

## 기술 스택

- Java 17
- Spring Boot 3.2.1
- Spring Security
- Maven
- Lombok

## 빌드 및 실행

### 필수 요구사항
- JDK 17 이상
- Maven 3.6 이상

### 빌드
```bash
mvn clean install
```

### 실행
```bash
mvn spring-boot:run
```

애플리케이션은 기본적으로 `http://localhost:8080`에서 실행됩니다.

## 사용자 인증

애플리케이션은 두 가지 사용자 계정을 제공합니다:

### 일반 사용자
- Username: `user`
- Password: `password`
- 권한: 파일/디렉토리 생성, 조회, 읽기

### 관리자
- Username: `admin`
- Password: `admin`
- 권한: 모든 기능 + 삭제

## API 엔드포인트

### 파일 관리 API

### 1. 파일 생성
```
POST /api/files/create
Authorization: Basic Auth (user/admin)

Request Body:
{
  "path": "test.txt",
  "content": "파일 내용"
}
```

### 2. 디렉토리 생성
```
POST /api/files/directory/create
Authorization: Basic Auth (user/admin)

Request Body:
{
  "path": "test-directory"
}
```

### 3. 파일 목록 조회
```
GET /api/files/list?path=directory-path
Authorization: Basic Auth (user/admin)
```

### 4. 파일 정보 조회
```
GET /api/files/info?path=file-path
Authorization: Basic Auth (user/admin)
```

### 5. 파일 읽기
```
GET /api/files/read?path=file-path
Authorization: Basic Auth (user/admin)
```

### 6. 파일/디렉토리 삭제
```
DELETE /api/files/delete?path=file-or-directory-path
Authorization: Basic Auth (admin only)
```

### 방화벽 관리 API (관리자 전용)

### 7. 방화벽 상태 조회
```
GET /api/firewall/status
Authorization: Basic Auth (admin only)

Response:
{
  "success": true,
  "message": "Firewall status retrieved",
  "data": {
    "enabled": true,
    "whitelist_count": 2,
    "blacklist_count": 1,
    "allow_localhost": true,
    "max_requests_per_minute": 100
  }
}
```

### 8. 화이트리스트 관리
```
# 화이트리스트 조회
GET /api/firewall/whitelist
Authorization: Basic Auth (admin only)

# IP 추가
POST /api/firewall/whitelist?ip=192.168.1.100
Authorization: Basic Auth (admin only)

# IP 제거
DELETE /api/firewall/whitelist?ip=192.168.1.100
Authorization: Basic Auth (admin only)
```

### 9. 블랙리스트 관리
```
# 블랙리스트 조회
GET /api/firewall/blacklist
Authorization: Basic Auth (admin only)

# IP 추가
POST /api/firewall/blacklist?ip=10.0.0.50
Authorization: Basic Auth (admin only)

# IP 제거
DELETE /api/firewall/blacklist?ip=10.0.0.50
Authorization: Basic Auth (admin only)
```

### 10. 방화벽 활성화/비활성화
```
POST /api/firewall/toggle?enabled=true
Authorization: Basic Auth (admin only)
```

### 11. 속도 제한 설정
```
POST /api/firewall/rate-limit?maxRequestsPerMinute=150
Authorization: Basic Auth (admin only)
```

## 사용 예시 (curl)

### 파일 생성
```bash
curl -u user:password -X POST http://localhost:8080/api/files/create \
  -H "Content-Type: application/json" \
  -d '{"path":"example.txt","content":"Hello World"}'
```

### 디렉토리 생성
```bash
curl -u user:password -X POST http://localhost:8080/api/files/directory/create \
  -H "Content-Type: application/json" \
  -d '{"path":"my-directory"}'
```

### 파일 목록 조회
```bash
curl -u user:password http://localhost:8080/api/files/list
```

### 파일 읽기
```bash
curl -u user:password http://localhost:8080/api/files/read?path=example.txt
```

### 파일 삭제 (관리자만 가능)
```bash
curl -u admin:admin -X DELETE http://localhost:8080/api/files/delete?path=example.txt
```

## 파일 저장 위치

파일은 기본적으로 `uploads/` 디렉토리에 저장됩니다. 이는 `application.properties`에서 변경할 수 있습니다:

```properties
file.storage.location=uploads
```

## 방화벽 설정

방화벽 기능은 `application.properties`에서 구성할 수 있습니다:

```properties
# 방화벽 활성화/비활성화
firewall.enabled=true

# 로컬호스트 접근 허용
firewall.allow-localhost=true

# 분당 최대 요청 수 (속도 제한)
firewall.max-requests-per-minute=100

# 화이트리스트 IP 추가 (예시)
# firewall.whitelist[0]=192.168.1.0/24
# firewall.whitelist[1]=10.0.0.100

# 블랙리스트 IP 추가 (예시)
# firewall.blacklist[0]=203.0.113.0
```

## 테스트

```bash
mvn test
```

## 라이센스

이 프로젝트는 LICENSE 파일에 명시된 라이센스를 따릅니다.
=======

# cost-data

## GitHub Copilot Agent with Complete Firewall and Windows Support

This repository contains a fully configured GitHub Copilot agent that runs **without skipping any components**, including firewall and Windows-specific configurations.

### ✨ Key Features

- ✅ **No-Skip Configuration**: All components run without being skipped
- 🔥 **Complete Firewall Support**: Configures both Windows Firewall and Linux UFW/iptables
- 🪟 **Full Windows Support**: Windows-specific checks and configurations
- 🐧 **Linux Support**: Complete Linux environment support
- 🔒 **Security Focused**: All security checks enabled

### 📁 Repository Structure

```
.github/
├── copilot/
│   └── agent-config.yml          # Main agent configuration (skip_firewall: false, skip_windows: false)
└── workflows/
    └── copilot-agent.yml         # GitHub Actions workflow for agent execution
AGENT_GUIDE.md                    # Detailed guide for the agent
validate-agent.sh                 # Linux/Mac validation script
validate-agent.ps1                # Windows PowerShell validation script
```

### 🚀 Quick Start

#### Validate Configuration

**On Linux/Mac:**
```bash
./validate-agent.sh
```

**On Windows (PowerShell):**
```powershell
.\validate-agent.ps1
```

#### View Agent Configuration

The agent configuration ensures nothing is skipped:
```yaml
settings:
  skip_firewall: false    # Firewall always runs
  skip_windows: false     # Windows checks always run
  run_all_checks: true    # All checks enabled
```

### 📖 Documentation

See [AGENT_GUIDE.md](AGENT_GUIDE.md) for detailed information about:
- Agent configuration
- Firewall rules
- Platform support
- Troubleshooting

### 🔍 What Gets Executed

#### Windows Environment
1. Windows Firewall configuration (HTTP, HTTPS, SSH ports)
2. Windows Firewall status verification
3. Windows Defender status checks
4. System information validation

#### Linux Environment
1. UFW firewall configuration (HTTP, HTTPS, SSH ports)
2. iptables rules setup
3. Firewall status verification
4. System and network configuration checks

### ✅ Verification

The agent includes automatic validation to ensure:
- ✅ All firewall configurations are applied
- ✅ No components are skipped
- ✅ Security checks are performed
- ✅ Both Windows and Linux environments are supported

### 🎯 Usage

The agent automatically runs on:
- Push to main/master/develop branches
- Pull requests to main/master/develop branches
- Manual workflow dispatch

### 📊 Status

All configurations are set to run completely without skipping:
- **Firewall**: NO SKIP ✅
- **Windows**: NO SKIP ✅
- **All Checks**: ENABLED ✅
=======
# Server Management System (서버 관리 시스템)

A comprehensive server management system for server upgrades, capacity management, and disk operations.

종합 서버 관리 시스템 - 서버 업그레이드, 용량 관리, 디스크 운영을 위한 솔루션

## Features (기능)

- ✅ **Server Upgrade Configuration (서버 업그레이드 구성)** - Upgrade CPU and memory
- ✅ **Capacity Check (용량 체크)** - Check current server capacity
- ✅ **Capacity Expansion (용량 증설)** - Expand CPU, memory, or disk capacity
- ✅ **Disk Installation (디스크 설치)** - Install new disks
- ✅ **Disk Addition Reflection (디스크 추가 반영)** - Add and reflect disk changes
- 🔥 **Firewall Installation (방화벽 설치)** - Install and configure firewalls (UFW, Windows, iptables)
- 🔥 **Firewall Rule Management (방화벽 규칙 관리)** - Add, remove, and list firewall rules
- 🔥 **Firewall Upgrade (방화벽 업그레이드)** - Enable advanced security features (DDoS protection, IDS, rate limiting)

## Quick Start

### Installation
```bash
git clone https://github.com/koreatest12/cost-data.git
cd cost-data
```

### Basic Usage
```bash
# Add a server
python3 server_manager.py add --server-id server-1 --cpu 4 --memory 8

# Upgrade server
python3 server_manager.py upgrade --server-id server-1 --cpu 8 --memory 16

# Check capacity
python3 server_manager.py check-capacity --server-id server-1

# Install disk
python3 server_manager.py install-disk --server-id server-1 --disk-size 500 --disk-type SSD

# List all servers
python3 server_manager.py list

# 🔥 FIREWALL MANAGEMENT

# Install firewall
python3 server_manager.py install-firewall --server-id server-1 --firewall-type ufw

# Upgrade firewall with advanced features
python3 server_manager.py upgrade-firewall --server-id server-1 --enable-ddos --enable-ids --enable-rate-limit

# Add firewall rule
python3 server_manager.py add-firewall-rule --server-id server-1 --rule-name "Custom SSH" --protocol TCP --port 2222 --direction inbound --action allow

# List firewall rules
python3 server_manager.py list-firewall-rules --server-id server-1

# Remove firewall rule
python3 server_manager.py remove-firewall-rule --server-id server-1 --rule-id rule-1
```

## Documentation

For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)

## Testing

```bash
python3 test_server_manager.py
```

## License

Apache License 2.0


