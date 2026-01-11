# GitHub Copilot Agent Configuration Guide

## Overview
This repository contains a complete GitHub Copilot agent configuration that runs without skipping any components, including firewall and Windows-specific configurations.

## Agent Features

### ✅ No-Skip Configuration
- **Firewall Configuration**: Always runs, never skipped
- **Windows Settings**: Always runs, never skipped
- **All Security Checks**: Always enabled

### 🚀 Actions Setup Steps
The agent is configured to set up the build environment **before** enabling the firewall:

1. **Java 17 Setup**: Installed using `actions/setup-java@v4`
2. **Python Setup**: Installed using `actions/setup-python@v5`
3. **Maven Dependencies**: Pre-downloaded using `mvn dependency:go-offline`
4. **Firewall Configuration**: Applied after dependencies are cached

This prevents firewall rules from blocking access to essential package repositories.

### 🔥 Firewall Support
The agent configures firewall rules on both Windows and Linux:

#### Windows Firewall
- Automatically enables Windows Firewall for all profiles
- Configures inbound and outbound rules for HTTP (80), HTTPS (443), and SSH (22)
- Allows DNS traffic (UDP/TCP port 53)
- Verifies firewall status after configuration

#### Linux Firewall (UFW & iptables)
- Configures UFW (Uncomplicated Firewall) with default deny incoming, allow outgoing
- Sets up iptables rules for both inbound and outbound traffic
- Configures rules for HTTP (80), HTTPS (443), SSH (22), and DNS (53)
- Allows established connections to continue

### 🔓 Firewall Allowlist
Essential domains and services that are accessible even with firewall enabled:
- **GitHub**: github.com, api.github.com, raw.githubusercontent.com
- **Maven Central**: repo.maven.apache.org, repo1.maven.org, central.maven.org
- **Python PyPI**: pypi.org, files.pythonhosted.org
- **Spring Repositories**: repo.spring.io
- **DNS**: Port 53 (UDP/TCP) for domain resolution
- **HTTP/HTTPS**: Ports 80 and 443 for outbound connections

### 🪟 Windows Support
- Full Windows environment support
- Windows Defender status checks
- System information verification
- PowerShell-based automation

## Configuration Files

### `.github/copilot/agent-config.yml`
Main agent configuration file with:
- `skip_firewall: false` - Ensures firewall setup always runs
- `skip_windows: false` - Ensures Windows checks always run
- `run_all_checks: true` - All checks are executed
- `firewall_allowlist` - Documents essential URLs/hosts for builds

### `.github/workflows/copilot-agent.yml`
GitHub Actions workflow that:
- Sets up Java and Python **before** firewall configuration
- Pre-downloads Maven dependencies before firewall is enabled
- Configures firewall with both inbound and outbound rules
- Executes platform-specific checks
- Verifies builds still work after firewall configuration
- Validates all configurations

## Usage

### Automatic Execution
The agent automatically runs on:
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main`, `master`, or `develop` branches
- Manual workflow dispatch

### Manual Execution
To manually trigger the agent:
1. Go to Actions tab in GitHub
2. Select "Copilot Agent - Complete Run"
3. Click "Run workflow"

## Verification

The agent includes validation steps to ensure:
1. ✅ Windows firewall is configured and enabled
2. ✅ Linux firewall (UFW/iptables) is configured and enabled
3. ✅ All security checks are performed
4. ✅ No components are skipped

## Configuration Details

### Firewall Rules
The following ports are configured:
- **Port 80 (HTTP)**: Inbound and outbound allowed
- **Port 443 (HTTPS)**: Inbound and outbound allowed
- **Port 22 (SSH)**: Inbound and outbound allowed
- **Port 53 (DNS)**: UDP and TCP outbound allowed

### Setup Order
1. **Checkout code** from repository
2. **Setup Java 17** with Maven cache
3. **Setup Python** environment
4. **Download Maven dependencies** (before firewall)
5. **Configure firewall** rules
6. **Run platform checks**
7. **Verify builds** work after firewall

### Platform Support
- ✅ Windows (latest)
- ✅ Linux (Ubuntu latest)

### Security Features
- Windows Defender status monitoring
- Firewall profile verification
- Network configuration validation
- System information checks

## Troubleshooting

### If firewall configuration fails:
1. Check that the workflow has necessary permissions
2. Verify the platform supports the firewall commands
3. Review the workflow logs for specific errors

### If builds fail after firewall is enabled:
1. Verify that setup steps ran before firewall configuration
2. Check that Maven dependencies were cached successfully
3. Ensure outbound HTTPS/HTTP traffic is allowed
4. Verify DNS resolution is working (port 53)
5. Check the firewall allowlist in agent-config.yml

### If components are being skipped:
1. Check `skip_firewall` and `skip_windows` in agent-config.yml
2. Ensure both are set to `false`
3. Verify `run_all_checks` is set to `true`

## Support
For issues or questions, please open an issue in the repository.
