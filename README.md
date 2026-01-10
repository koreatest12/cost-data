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
