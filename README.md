
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

