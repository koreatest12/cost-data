# Server Management System

서버 관리 시스템 - 서버 업그레이드, 용량 관리, 디스크 관리를 위한 종합 솔루션

## 기능 (Features)

이 시스템은 다음과 같은 기능을 제공합니다:

### 1. 서버 업그레이드 구성 (Server Upgrade Configuration)
- CPU 업그레이드
- 메모리 업그레이드
- 업그레이드 이력 추적

### 2. 용량 체크 (Capacity Check)
- 현재 서버 용량 확인
- CPU, 메모리, 디스크 용량 조회
- 디스크 개수 및 상세 정보 확인

### 3. 용량 증설 (Capacity Expansion)
- CPU 용량 증설
- 메모리 용량 증설
- 디스크 용량 증설

### 4. 디스크 설치 (Disk Installation)
- 새로운 디스크 설치
- 디스크 타입 지정 (SSD/HDD)
- 디스크 크기 설정

### 5. 디스크 추가 반영 (Disk Addition Reflection)
- 디스크 추가 및 구성 반영
- 디스크 상태 검증
- 반영 시간 기록

## 설치 (Installation)

```bash
# 저장소 클론
git clone https://github.com/koreatest12/cost-data.git
cd cost-data

# Python 3.6 이상 필요
python3 --version
```

## 사용법 (Usage)

### CLI 사용

#### 서버 추가
```bash
python3 server_manager.py add --server-id server-1 --cpu 4 --memory 8
```

#### 서버 업그레이드
```bash
# CPU 업그레이드
python3 server_manager.py upgrade --server-id server-1 --cpu 8

# 메모리 업그레이드
python3 server_manager.py upgrade --server-id server-1 --memory 16

# CPU와 메모리 동시 업그레이드
python3 server_manager.py upgrade --server-id server-1 --cpu 8 --memory 16
```

#### 용량 체크
```bash
python3 server_manager.py check-capacity --server-id server-1
```

#### 용량 증설
```bash
# CPU 2코어 증설
python3 server_manager.py expand-capacity --server-id server-1 --expansion-type cpu --amount 2

# 메모리 8GB 증설
python3 server_manager.py expand-capacity --server-id server-1 --expansion-type memory --amount 8

# 디스크 100GB 증설
python3 server_manager.py expand-capacity --server-id server-1 --expansion-type disk --amount 100
```

#### 디스크 설치
```bash
# SSD 디스크 500GB 설치
python3 server_manager.py install-disk --server-id server-1 --disk-size 500 --disk-type SSD

# HDD 디스크 1000GB 설치
python3 server_manager.py install-disk --server-id server-1 --disk-size 1000 --disk-type HDD
```

#### 디스크 추가 반영
```bash
python3 server_manager.py add-disk --server-id server-1 --disk-size 1000 --disk-type SSD
```

#### 서버 정보 조회
```bash
python3 server_manager.py info --server-id server-1
```

#### 모든 서버 목록 조회
```bash
python3 server_manager.py list
```

### Python 코드에서 사용

```python
from server_manager import ServerManager

# ServerManager 인스턴스 생성
manager = ServerManager()

# 서버 추가
manager.add_server("web-server-1", {
    "cpu": 4,
    "memory_gb": 16,
    "os": "Ubuntu 22.04"
})

# 서버 업그레이드
result = manager.upgrade_server("web-server-1", {
    "cpu": 8,
    "memory_gb": 32
})
print(f"Upgrade result: {result}")

# 용량 체크
capacity = manager.check_capacity("web-server-1")
print(f"Current capacity: {capacity}")

# 용량 증설
expansion = manager.expand_capacity("web-server-1", "memory", 16)
print(f"Expansion result: {expansion}")

# 디스크 설치
disk_result = manager.install_disk("web-server-1", {
    "size_gb": 500,
    "type": "SSD"
})
print(f"Disk installed: {disk_result}")

# 디스크 추가 및 반영
disk_add = manager.add_disk("web-server-1", {
    "size_gb": 1000,
    "type": "SSD"
})
print(f"Disk added and reflected: {disk_add}")

# 서버 정보 조회
info = manager.get_server_info("web-server-1")
print(f"Server info: {info}")

# 모든 서버 목록
servers = manager.list_servers()
print(f"All servers: {servers}")
```

## 테스트 (Testing)

```bash
# 모든 테스트 실행
python3 test_server_manager.py

# 특정 테스트 실행
python3 test_server_manager.py TestServerManager.test_upgrade_server_cpu
```

## 데이터 저장

모든 서버 구성은 `server_config.json` 파일에 자동으로 저장됩니다. 이 파일은 다음과 같은 정보를 포함합니다:

- 서버 ID 및 기본 사양
- CPU 및 메모리 구성
- 디스크 목록 및 상세 정보
- 업그레이드 이력
- 디스크 설치 이력

## 예제 시나리오

### 시나리오 1: 신규 웹 서버 설정 및 확장
```bash
# 1. 서버 추가
python3 server_manager.py add --server-id web-server-1 --cpu 2 --memory 4

# 2. 디스크 설치
python3 server_manager.py install-disk --server-id web-server-1 --disk-size 100 --disk-type SSD

# 3. 용량 확인
python3 server_manager.py check-capacity --server-id web-server-1

# 4. 트래픽 증가로 인한 업그레이드
python3 server_manager.py upgrade --server-id web-server-1 --cpu 4 --memory 16

# 5. 추가 디스크 필요
python3 server_manager.py add-disk --server-id web-server-1 --disk-size 500 --disk-type SSD

# 6. 디스크 용량 증설
python3 server_manager.py expand-capacity --server-id web-server-1 --expansion-type disk --amount 200

# 7. 최종 상태 확인
python3 server_manager.py info --server-id web-server-1
```

### 시나리오 2: 데이터베이스 서버 구성
```python
from server_manager import ServerManager

manager = ServerManager()

# 데이터베이스 서버 추가 (고성능 구성)
manager.add_server("db-server-1", {
    "cpu": 8,
    "memory_gb": 64,
    "os": "Ubuntu 22.04"
})

# 대용량 SSD 디스크 설치
manager.install_disk("db-server-1", {
    "size_gb": 2000,
    "type": "SSD",
    "mount_point": "/var/lib/postgresql"
})

# 백업용 HDD 디스크 설치
manager.install_disk("db-server-1", {
    "size_gb": 5000,
    "type": "HDD",
    "mount_point": "/backup"
})

# 용량 확인
capacity = manager.check_capacity("db-server-1")
print(f"Database server capacity: {capacity}")
```

## API 참조

### ServerManager 클래스

#### `__init__(config_file: str = "server_config.json")`
ServerManager 인스턴스를 초기화합니다.

#### `add_server(server_id: str, specs: Dict) -> Dict`
새로운 서버를 추가합니다.

**Parameters:**
- `server_id`: 서버 고유 ID
- `specs`: 서버 사양 (cpu, memory_gb, os 등)

**Returns:** 추가된 서버 정보

#### `upgrade_server(server_id: str, upgrade_specs: Dict) -> Dict`
서버를 업그레이드합니다.

**Parameters:**
- `server_id`: 서버 ID
- `upgrade_specs`: 업그레이드할 사양 (cpu, memory_gb)

**Returns:** 업그레이드 결과 및 현재 사양

#### `check_capacity(server_id: str) -> Dict`
서버 용량을 확인합니다.

**Parameters:**
- `server_id`: 서버 ID

**Returns:** 용량 정보 (CPU, 메모리, 디스크)

#### `expand_capacity(server_id: str, expansion_type: str, amount: int) -> Dict`
서버 용량을 증설합니다.

**Parameters:**
- `server_id`: 서버 ID
- `expansion_type`: 증설 타입 ("cpu", "memory", "disk")
- `amount`: 증설량

**Returns:** 증설 결과

#### `install_disk(server_id: str, disk_specs: Dict) -> Dict`
새로운 디스크를 설치합니다.

**Parameters:**
- `server_id`: 서버 ID
- `disk_specs`: 디스크 사양 (size_gb, type)

**Returns:** 설치된 디스크 정보

#### `add_disk(server_id: str, disk_specs: Dict) -> Dict`
디스크를 추가하고 반영합니다.

**Parameters:**
- `server_id`: 서버 ID
- `disk_specs`: 디스크 사양

**Returns:** 추가 및 반영 결과

#### `get_server_info(server_id: str) -> Dict`
서버 상세 정보를 조회합니다.

#### `list_servers() -> List[Dict]`
모든 서버 목록을 조회합니다.

## 라이센스 (License)

이 프로젝트는 Apache License 2.0 하에 배포됩니다.

## 기여 (Contributing)

기여를 환영합니다! 이슈를 생성하거나 풀 리퀘스트를 제출해 주세요.
