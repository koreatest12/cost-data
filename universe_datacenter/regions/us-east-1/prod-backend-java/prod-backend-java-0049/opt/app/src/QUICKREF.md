# Quick Reference Guide (빠른 참조 가이드)

## 명령어 치트시트 (Command Cheat Sheet)

### 서버 관리 (Server Management)

```bash
# 서버 추가 (Add Server)
python3 server_manager.py add --server-id SERVER_ID --cpu N --memory N

# 서버 정보 (Server Info)
python3 server_manager.py info --server-id SERVER_ID

# 서버 목록 (List Servers)
python3 server_manager.py list
```

### 업그레이드 (Upgrades)

```bash
# CPU 업그레이드 (Upgrade CPU)
python3 server_manager.py upgrade --server-id SERVER_ID --cpu N

# 메모리 업그레이드 (Upgrade Memory)
python3 server_manager.py upgrade --server-id SERVER_ID --memory N

# CPU + 메모리 동시 업그레이드 (Upgrade Both)
python3 server_manager.py upgrade --server-id SERVER_ID --cpu N --memory N
```

### 용량 관리 (Capacity Management)

```bash
# 용량 체크 (Check Capacity)
python3 server_manager.py check-capacity --server-id SERVER_ID

# CPU 증설 (Expand CPU)
python3 server_manager.py expand-capacity --server-id SERVER_ID --expansion-type cpu --amount N

# 메모리 증설 (Expand Memory)
python3 server_manager.py expand-capacity --server-id SERVER_ID --expansion-type memory --amount N

# 디스크 증설 (Expand Disk)
python3 server_manager.py expand-capacity --server-id SERVER_ID --expansion-type disk --amount N
```

### 디스크 관리 (Disk Management)

```bash
# 디스크 설치 (Install Disk)
python3 server_manager.py install-disk --server-id SERVER_ID --disk-size N --disk-type TYPE

# 디스크 추가 (Add Disk with Reflection)
python3 server_manager.py add-disk --server-id SERVER_ID --disk-size N --disk-type TYPE
```

디스크 타입 (Disk Types): `SSD` 또는 `HDD`

## Python API 빠른 참조 (Python API Quick Reference)

```python
from server_manager import ServerManager

# 초기화 (Initialize)
manager = ServerManager()

# 서버 추가 (Add Server)
manager.add_server("server-id", {
    "cpu": 4,
    "memory_gb": 8,
    "os": "Ubuntu 22.04"
})

# 서버 업그레이드 (Upgrade Server)
manager.upgrade_server("server-id", {
    "cpu": 8,
    "memory_gb": 16
})

# 용량 체크 (Check Capacity)
capacity = manager.check_capacity("server-id")

# 용량 증설 (Expand Capacity)
manager.expand_capacity("server-id", "cpu", 2)
manager.expand_capacity("server-id", "memory", 8)
manager.expand_capacity("server-id", "disk", 100)

# 디스크 설치 (Install Disk)
manager.install_disk("server-id", {
    "size_gb": 500,
    "type": "SSD"
})

# 디스크 추가 (Add Disk)
manager.add_disk("server-id", {
    "size_gb": 1000,
    "type": "HDD"
})

# 서버 정보 (Get Server Info)
info = manager.get_server_info("server-id")

# 서버 목록 (List Servers)
servers = manager.list_servers()
```

## 일반적인 시나리오 (Common Scenarios)

### 시나리오 1: 신규 웹 서버 설정
```bash
# 1. 서버 생성
python3 server_manager.py add --server-id web-1 --cpu 2 --memory 4

# 2. 시스템 디스크 추가
python3 server_manager.py install-disk --server-id web-1 --disk-size 100 --disk-type SSD

# 3. 용량 확인
python3 server_manager.py check-capacity --server-id web-1
```

### 시나리오 2: 트래픽 증가로 인한 스케일업
```bash
# 1. 현재 상태 확인
python3 server_manager.py info --server-id web-1

# 2. CPU 및 메모리 업그레이드
python3 server_manager.py upgrade --server-id web-1 --cpu 4 --memory 16

# 3. 추가 디스크 설치
python3 server_manager.py add-disk --server-id web-1 --disk-size 500 --disk-type SSD
```

### 시나리오 3: 점진적 용량 증설
```bash
# 1. CPU 2코어 추가
python3 server_manager.py expand-capacity --server-id web-1 --expansion-type cpu --amount 2

# 2. 메모리 8GB 추가
python3 server_manager.py expand-capacity --server-id web-1 --expansion-type memory --amount 8

# 3. 디스크 200GB 추가
python3 server_manager.py expand-capacity --server-id web-1 --expansion-type disk --amount 200
```

## 테스트 실행 (Running Tests)

```bash
# 전체 테스트 실행 (Run all tests)
python3 test_server_manager.py

# 상세 출력으로 테스트 실행 (Run with verbose output)
python3 test_server_manager.py -v

# 특정 테스트 실행 (Run specific test)
python3 test_server_manager.py TestServerManager.test_upgrade_server_cpu
```

## 데모 실행 (Running Demo)

```bash
# 전체 기능 데모 (Full feature demo)
python3 demo.py
```

## 설정 파일 위치 (Configuration File Location)

기본 설정 파일: `server_config.json`

다른 파일 사용:
```python
manager = ServerManager(config_file="custom_config.json")
```

## 문제 해결 (Troubleshooting)

### 서버를 찾을 수 없음
```
Error: Server XXX not found
```
→ `python3 server_manager.py list`로 서버 ID 확인

### 서버가 이미 존재함
```
Error: Server XXX already exists
```
→ 다른 서버 ID 사용 또는 기존 서버 업그레이드

### JSON 디코딩 오류
```
JSONDecodeError: Expecting value
```
→ 설정 파일 삭제 후 재시작: `rm server_config.json`

## 추가 도움말 (Additional Help)

- 전체 문서: `DOCUMENTATION.md`
- 구현 요약: `SUMMARY.md`
- 프로젝트 개요: `README.md`
