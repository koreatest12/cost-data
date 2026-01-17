# Firewall Security Features Guide

## 개요 (Overview)

이 시스템은 포괄적인 방화벽 및 보안 기능을 제공하여 애플리케이션과 서버를 보호합니다.

This system provides comprehensive firewall and security features to protect applications and servers.

---

## Java Spring Boot Firewall Features

### 1. IP-Based Access Control (IP 기반 접근 제어)

방화벽은 IP 주소 기반으로 요청을 필터링합니다.

**Features:**
- ✅ Whitelist: 특정 IP만 허용
- ✅ Blacklist: 특정 IP 차단
- ✅ Localhost 자동 허용 옵션

**Configuration (application.properties):**
```properties
firewall.enabled=true
firewall.allow-localhost=true
firewall.whitelist[0]=192.168.1.0/24
firewall.whitelist[1]=10.0.0.100
firewall.blacklist[0]=203.0.113.0
```

### 2. Rate Limiting (속도 제한)

DDoS 공격을 방지하기 위해 IP당 분당 요청 수를 제한합니다.

**Configuration:**
```properties
firewall.max-requests-per-minute=100
```

**API Endpoint:**
```bash
# 속도 제한 업데이트
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/rate-limit?maxRequestsPerMinute=150"
```

### 3. Security Headers (보안 헤더)

자동으로 추가되는 보안 헤더:
- ✅ Content Security Policy (CSP)
- ✅ X-Frame-Options (Clickjacking 방지)
- ✅ X-Content-Type-Options

### 4. Firewall Management API

#### 방화벽 상태 확인
```bash
curl -u admin:admin http://localhost:8080/api/firewall/status
```

**Response:**
```json
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

#### 화이트리스트 관리
```bash
# IP 추가
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/whitelist?ip=192.168.1.100"

# IP 목록 조회
curl -u admin:admin http://localhost:8080/api/firewall/whitelist

# IP 제거
curl -u admin:admin -X DELETE \
  "http://localhost:8080/api/firewall/whitelist?ip=192.168.1.100"
```

#### 블랙리스트 관리
```bash
# IP 추가
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/blacklist?ip=10.0.0.50"

# IP 목록 조회
curl -u admin:admin http://localhost:8080/api/firewall/blacklist

# IP 제거
curl -u admin:admin -X DELETE \
  "http://localhost:8080/api/firewall/blacklist?ip=10.0.0.50"
```

#### 방화벽 활성화/비활성화
```bash
# 활성화
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/toggle?enabled=true"

# 비활성화
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/toggle?enabled=false"
```

---

## Python Server Manager Firewall Features

### 1. Firewall Installation (방화벽 설치)

서버에 방화벽을 설치하고 기본 규칙을 구성합니다.

**Supported Firewall Types:**
- `ufw` - Ubuntu/Debian Linux (기본)
- `windows` - Windows Firewall
- `iptables` - Advanced Linux

**Usage:**
```bash
# UFW 방화벽 설치
python3 server_manager.py install-firewall \
  --server-id server-1 \
  --firewall-type ufw

# Windows 방화벽 설치
python3 server_manager.py install-firewall \
  --server-id server-2 \
  --firewall-type windows
```

**기본 규칙 (Default Rules):**

**Linux (UFW):**
- SSH (Port 22)
- HTTP (Port 80)
- HTTPS (Port 443)

**Windows:**
- RDP (Port 3389)
- HTTP (Port 80)
- HTTPS (Port 443)

### 2. Firewall Rule Management (방화벽 규칙 관리)

#### 규칙 추가
```bash
python3 server_manager.py add-firewall-rule \
  --server-id server-1 \
  --rule-name "Custom SSH" \
  --protocol TCP \
  --port 2222 \
  --direction inbound \
  --action allow
```

**Parameters:**
- `--rule-name`: 규칙 이름
- `--protocol`: TCP 또는 UDP
- `--port`: 포트 번호
- `--direction`: inbound 또는 outbound
- `--action`: allow 또는 deny

#### 규칙 목록 조회
```bash
python3 server_manager.py list-firewall-rules --server-id server-1
```

**Example Output:**
```json
[
  {
    "id": "rule-1",
    "name": "SSH",
    "protocol": "TCP",
    "port": 22,
    "direction": "inbound",
    "action": "allow",
    "source": "any",
    "destination": "any",
    "created_at": "2026-01-17T14:00:00"
  },
  {
    "id": "rule-2",
    "name": "HTTP",
    "protocol": "TCP",
    "port": 80,
    "direction": "inbound",
    "action": "allow",
    "source": "any",
    "destination": "any",
    "created_at": "2026-01-17T14:00:00"
  }
]
```

#### 규칙 제거
```bash
python3 server_manager.py remove-firewall-rule \
  --server-id server-1 \
  --rule-id rule-1
```

### 3. Firewall Upgrade (방화벽 업그레이드)

고급 보안 기능을 활성화합니다.

```bash
python3 server_manager.py upgrade-firewall \
  --server-id server-1 \
  --enable-ddos \
  --enable-ids \
  --enable-rate-limit
```

**Advanced Features:**

#### DDoS Protection (DDoS 보호)
- 분산 서비스 거부 공격 방지
- 비정상적인 트래픽 패턴 탐지

#### Intrusion Detection System (침입 탐지 시스템)
- 의심스러운 활동 모니터링
- 실시간 위협 탐지

#### Rate Limiting (속도 제한)
- 연결당 최대 요청 수 제한
- 기본값: 100 connections

#### Geo-blocking (지리적 차단)
- 특정 국가의 IP 차단
- 화이트리스트 국가 설정

**Example:**
```bash
python3 server_manager.py upgrade-firewall \
  --server-id server-1 \
  --enable-ddos \
  --enable-ids
```

**Result:**
```json
{
  "server_id": "server-1",
  "upgrade_info": {
    "timestamp": "2026-01-17T14:00:00",
    "upgrades": [
      "DDoS protection enabled",
      "Intrusion detection enabled"
    ]
  },
  "firewall_config": {
    "type": "ufw",
    "installed": true,
    "enabled": true,
    "ddos_protection": true,
    "intrusion_detection": true
  }
}
```

---

## Common Use Cases (일반적인 사용 사례)

### Use Case 1: 웹 서버 보호

**Scenario:** 웹 서버를 설정하고 HTTP/HTTPS만 허용

```bash
# 1. 서버 추가
python3 server_manager.py add --server-id web-1 --cpu 4 --memory 16

# 2. 방화벽 설치
python3 server_manager.py install-firewall --server-id web-1 --firewall-type ufw

# 3. SSH 포트 변경 (보안 강화)
python3 server_manager.py add-firewall-rule \
  --server-id web-1 \
  --rule-name "Custom SSH" \
  --protocol TCP \
  --port 2222 \
  --direction inbound \
  --action allow

# 4. 고급 보안 활성화
python3 server_manager.py upgrade-firewall \
  --server-id web-1 \
  --enable-ddos \
  --enable-rate-limit
```

### Use Case 2: 데이터베이스 서버 보안

**Scenario:** 데이터베이스 서버를 특정 IP에서만 접근 가능하도록 설정

```bash
# 1. 서버 추가
python3 server_manager.py add --server-id db-1 --cpu 8 --memory 32

# 2. 방화벽 설치
python3 server_manager.py install-firewall --server-id db-1 --firewall-type ufw

# 3. MySQL 포트 추가
python3 server_manager.py add-firewall-rule \
  --server-id db-1 \
  --rule-name "MySQL" \
  --protocol TCP \
  --port 3306 \
  --direction inbound \
  --action allow

# Java 애플리케이션에서 특정 IP만 허용
# application.properties에 추가:
# firewall.whitelist[0]=192.168.1.10
# firewall.whitelist[1]=192.168.1.11
```

### Use Case 3: API 서버 DDoS 방지

**Scenario:** REST API 서버에 속도 제한 적용

```bash
# 1. Spring Boot 설정
# application.properties:
firewall.enabled=true
firewall.max-requests-per-minute=100

# 2. 런타임에 속도 제한 조정
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/rate-limit?maxRequestsPerMinute=50"

# 3. 악의적인 IP 차단
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/blacklist?ip=203.0.113.100"
```

---

## Testing (테스트)

### Python Firewall Tests
```bash
# 모든 방화벽 테스트 실행
python3 test_firewall.py -v
```

### Manual Testing

#### 1. 방화벽 상태 확인
```bash
curl -u admin:admin http://localhost:8080/api/firewall/status
```

#### 2. 속도 제한 테스트
```bash
# 빠르게 100+ 요청 전송
for i in {1..150}; do
  curl -u user:password http://localhost:8080/api/files/list
done
# 429 Too Many Requests 응답 확인
```

#### 3. IP 차단 테스트
```bash
# 1. 자신의 IP를 블랙리스트에 추가
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/blacklist?ip=YOUR_IP"

# 2. 요청 시도
curl -u user:password http://localhost:8080/api/files/list
# 403 Forbidden 응답 확인

# 3. 블랙리스트에서 제거
curl -u admin:admin -X DELETE \
  "http://localhost:8080/api/firewall/blacklist?ip=YOUR_IP"
```

---

## Troubleshooting (문제 해결)

### 문제: 접근이 차단됨

**해결:**
```bash
# 1. 방화벽 상태 확인
curl -u admin:admin http://localhost:8080/api/firewall/status

# 2. 자신의 IP를 화이트리스트에 추가
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/whitelist?ip=YOUR_IP"

# 또는 방화벽 비활성화
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/toggle?enabled=false"
```

### 문제: 속도 제한으로 인한 차단

**해결:**
```bash
# 속도 제한 증가
curl -u admin:admin -X POST \
  "http://localhost:8080/api/firewall/rate-limit?maxRequestsPerMinute=500"
```

### 문제: 블랙리스트에 실수로 IP 추가

**해결:**
```bash
# 블랙리스트에서 제거
curl -u admin:admin -X DELETE \
  "http://localhost:8080/api/firewall/blacklist?ip=WRONG_IP"
```

---

## Best Practices (모범 사례)

1. **화이트리스트 우선 사용**: 중요한 서버는 화이트리스트 방식 사용
2. **로그 모니터링**: 차단된 요청을 정기적으로 검토
3. **속도 제한 조정**: 실제 트래픽 패턴에 맞게 조정
4. **정기적 업데이트**: 방화벽 규칙을 정기적으로 검토 및 업데이트
5. **백업 접근**: 관리자 접근을 위한 백업 IP 유지
6. **테스트 환경**: 프로덕션 적용 전 테스트 환경에서 검증

---

## Security Considerations (보안 고려사항)

- ⚠️ 관리자 비밀번호를 강력하게 설정하세요
- ⚠️ HTTPS를 사용하여 API 통신을 암호화하세요
- ⚠️ 정기적으로 로그를 검토하세요
- ⚠️ 불필요한 포트는 모두 차단하세요
- ⚠️ 방화벽 규칙을 문서화하세요

---

## License

Apache License 2.0
