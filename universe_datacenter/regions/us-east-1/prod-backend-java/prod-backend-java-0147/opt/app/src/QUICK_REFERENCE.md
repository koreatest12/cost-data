# Agent Quick Reference

## 🎯 Core Configuration

### No-Skip Settings
```yaml
skip_firewall: false     # ✅ Firewall ALWAYS runs
skip_windows: false      # ✅ Windows checks ALWAYS run
run_all_checks: true     # ✅ ALL checks enabled
```

## 🔥 Firewall Configuration

### Configured Ports
- **Port 80** (HTTP) - Inbound allowed
- **Port 443** (HTTPS) - Inbound allowed  
- **Port 22** (SSH) - Inbound allowed

### Platforms
- ✅ Windows Firewall
- ✅ Linux UFW
- ✅ Linux iptables

## 🪟 Windows Features

### Enabled Checks
- ✅ Windows Firewall configuration
- ✅ Windows Firewall verification
- ✅ Windows Defender status
- ✅ System information

## 🐧 Linux Features

### Enabled Checks
- ✅ UFW firewall configuration
- ✅ iptables rules setup
- ✅ Firewall status verification
- ✅ Network configuration

## 🚀 Validation Commands

### Linux/Mac
```bash
./validate-agent.sh
```

### Windows PowerShell
```powershell
.\validate-agent.ps1
```

## 📋 Files Overview

| File | Purpose |
|------|---------|
| `.github/copilot/agent-config.yml` | Main agent configuration |
| `.github/workflows/copilot-agent.yml` | GitHub Actions workflow |
| `AGENT_GUIDE.md` | Detailed documentation |
| `validate-agent.sh` | Linux/Mac validator |
| `validate-agent.ps1` | Windows validator |
| `README.md` | Project overview |

## ✅ Expected Behavior

When the agent runs:
1. ✅ Windows firewall is configured
2. ✅ Linux firewall is configured
3. ✅ All security checks run
4. ✅ NO components are skipped
5. ✅ Full validation is performed

## 🔍 Verification

All settings ensure complete execution:
- `skip_firewall: false` → Firewall setup RUNS
- `skip_windows: false` → Windows checks RUN
- `run_all_checks: true` → Everything RUNS

## 🎓 Key Principle

**NOTHING IS SKIPPED** - The agent is configured to execute all components completely.
