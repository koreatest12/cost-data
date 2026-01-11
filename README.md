
# Cost Data - File Management System

Spring Boot 애플리케이션으로 파일 및 디렉토리 관리 기능과 권한 인증을 제공합니다.

## 기능

- 파일 생성 및 관리
- 디렉토리 생성 및 관리
- 파일 목록 조회
- 파일 읽기
- 파일/디렉토리 삭제 (관리자 권한 필요)
- Spring Security를 통한 권한 관리

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
- 🚀 **Actions Setup Steps**: Dependencies downloaded before firewall is enabled
- 🌐 **Firewall Allowlist**: Essential URLs for Maven, PyPI, and GitHub allowed

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

The agent configuration ensures nothing is skipped and includes a firewall allowlist:
```yaml
settings:
  skip_firewall: false    # Firewall always runs
  skip_windows: false     # Windows checks always run
  run_all_checks: true    # All checks enabled

firewall_allowlist:
  # Essential URLs for builds
  - github.com
  - repo.maven.apache.org
  - pypi.org
  # ...and more
```

### 📖 Documentation

See [AGENT_GUIDE.md](AGENT_GUIDE.md) for detailed information about:
- Agent configuration
- Firewall rules
- Platform support
- Troubleshooting

### 🔍 What Gets Executed

#### Windows Environment
1. Setup Java 17 and Python (before firewall)
2. Pre-download Maven dependencies (before firewall)
3. Windows Firewall configuration (HTTP, HTTPS, SSH, DNS ports - inbound and outbound)
4. Windows Firewall status verification
5. Windows Defender status checks
6. System information validation
7. Build verification after firewall enabled

#### Linux Environment
1. Setup Java 17 and Python (before firewall)
2. Pre-download Maven dependencies (before firewall)
3. UFW firewall configuration (HTTP, HTTPS, SSH, DNS ports)
4. iptables rules setup (inbound and outbound)
5. Firewall status verification
6. System and network configuration checks
7. Build verification after firewall enabled

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
```

## Documentation

For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)

## Testing

```bash
python3 test_server_manager.py
```

## License

Apache License 2.0


