# GitHub Copilot Agent Configuration Guide

## Overview
This repository contains a complete GitHub Copilot agent configuration that runs without skipping any components, including firewall and Windows-specific configurations.

## Agent Features

### ✅ No-Skip Configuration
- **Firewall Configuration**: Always runs, never skipped
- **Windows Settings**: Always runs, never skipped
- **All Security Checks**: Always enabled

### 🔥 Firewall Support
The agent configures firewall rules on both Windows and Linux:

#### Windows Firewall
- Automatically enables Windows Firewall for all profiles
- Configures inbound rules for HTTP (80), HTTPS (443), and SSH (22)
- Verifies firewall status after configuration

#### Linux Firewall (UFW & iptables)
- Configures UFW (Uncomplicated Firewall)
- Sets up iptables rules
- Configures inbound rules for HTTP (80), HTTPS (443), and SSH (22)

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

### `.github/workflows/copilot-agent.yml`
GitHub Actions workflow that:
- Runs on both Windows and Linux
- Executes firewall configuration
- Performs platform-specific checks
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
- **Port 80 (HTTP)**: Inbound allowed
- **Port 443 (HTTPS)**: Inbound allowed
- **Port 22 (SSH)**: Inbound allowed

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

### If components are being skipped:
1. Check `skip_firewall` and `skip_windows` in agent-config.yml
2. Ensure both are set to `false`
3. Verify `run_all_checks` is set to `true`

## Support
For issues or questions, please open an issue in the repository.
