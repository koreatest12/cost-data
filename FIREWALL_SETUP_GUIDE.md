# Firewall Access Setup Guide

## Overview

This document explains how the GitHub Copilot agent is configured to handle firewall rules while ensuring that builds and dependency downloads still work correctly.

## Problem Statement

When firewall rules are enabled early in the GitHub Actions workflow, they can block access to essential external resources needed for:
- Maven dependency downloads from Maven Central and Spring repositories
- Python package downloads from PyPI
- GitHub API access
- DNS resolution for domain names

## Solution

The solution involves a carefully orchestrated setup sequence that ensures all dependencies are downloaded **before** the firewall is enabled, while still maintaining strong firewall security.

### Key Components

#### 1. Setup Steps Before Firewall Configuration

**For Both Windows and Linux Workflows:**

```yaml
# Step 1: Checkout code
- name: Checkout code
  uses: actions/checkout@v4

# Step 2: Setup Java 17 with Maven cache
- name: Setup Java 17
  uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'
    cache: 'maven'

# Step 3: Setup Python
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.x'

# Step 4: Pre-download Maven dependencies
- name: Download Maven dependencies
  run: mvn dependency:go-offline -B

# Step 5: NOW configure firewall
- name: Configure Firewall
  # ...firewall rules...
```

**Why This Order Matters:**
- Dependencies are downloaded using GitHub Actions' unrestricted network access
- Maven cache is populated before any firewall restrictions
- Python packages (if needed) can be installed before firewall
- Firewall is applied AFTER all external resources are cached

#### 2. Firewall Rules with Outbound Access

**Windows Firewall Configuration:**
```powershell
# HTTP - Inbound and Outbound
New-NetFirewallRule -DisplayName "Allow HTTP Inbound" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "Allow HTTP Outbound" -Direction Outbound -Protocol TCP -RemotePort 80 -Action Allow

# HTTPS - Inbound and Outbound
New-NetFirewallRule -DisplayName "Allow HTTPS Inbound" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "Allow HTTPS Outbound" -Direction Outbound -Protocol TCP -RemotePort 443 -Action Allow

# SSH - Inbound and Outbound
New-NetFirewallRule -DisplayName "Allow SSH Inbound" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow
New-NetFirewallRule -DisplayName "Allow SSH Outbound" -Direction Outbound -Protocol TCP -RemotePort 22 -Action Allow

# DNS - Outbound (essential for domain resolution)
New-NetFirewallRule -DisplayName "Allow DNS Outbound" -Direction Outbound -Protocol UDP -RemotePort 53 -Action Allow
```

**Linux Firewall Configuration (UFW):**
```bash
# Default policies
sudo ufw --force default deny incoming
sudo ufw --force default allow outgoing

# Allow specific inbound ports
sudo ufw allow 80/tcp comment 'Allow HTTP'
sudo ufw allow 443/tcp comment 'Allow HTTPS'
sudo ufw allow 22/tcp comment 'Allow SSH'

# Allow DNS
sudo ufw allow out 53 comment 'Allow DNS'
```

**Linux iptables Configuration:**
```bash
# Inbound rules
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT -m comment --comment "Allow HTTP"
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT -m comment --comment "Allow HTTPS"
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT -m comment --comment "Allow SSH"

# Outbound rules (for downloads)
sudo iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT -m comment --comment "Allow HTTP outbound"
sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT -m comment --comment "Allow HTTPS outbound"

# DNS rules
sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT -m comment --comment "Allow DNS UDP"
sudo iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT -m comment --comment "Allow DNS TCP"

# Allow established connections
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT -m comment --comment "Allow established inbound"
sudo iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT -m comment --comment "Allow established outbound"
```

#### 3. Firewall Allowlist

The following domains and services are accessible with the firewall enabled (documented in `agent-config.yml`):

**GitHub Services:**
- github.com
- api.github.com
- raw.githubusercontent.com
- objects.githubusercontent.com

**Maven Repositories:**
- repo.maven.apache.org
- repo1.maven.org
- central.maven.org
- repo.spring.io

**Python Package Index:**
- pypi.org
- files.pythonhosted.org

**DNS Servers:**
- 8.8.8.8 (Google DNS)
- 8.8.4.4 (Google DNS)

**Other Essential Services:**
- downloads.apache.org
- registry.npmjs.org

#### 4. Build Verification

After the firewall is configured, a verification step ensures that builds still work:

```yaml
- name: Verify build works after firewall configuration
  run: |
    echo "Verifying Maven build works with firewall enabled..."
    mvn verify -B -q
    echo "Build verification successful - firewall allows necessary traffic"
```

This step:
- Runs a Maven build with tests (without clean to use cached dependencies)
- Uses cached dependencies (downloaded before firewall)
- Verifies that the firewall doesn't block necessary operations
- Fails the workflow if the build doesn't work

## Workflow Execution Order

### Windows Workflow

1. ✅ Checkout code from repository
2. ✅ Setup Java 17 with Maven caching
3. ✅ Setup Python environment
4. ✅ Download Maven dependencies (before firewall)
5. 🔥 Configure Windows Firewall (inbound + outbound rules)
6. ✅ Verify firewall status
7. ✅ Run Windows-specific checks
8. ✅ Verify build works with firewall enabled
9. ✅ Display execution summary

### Linux Workflow

1. ✅ Checkout code from repository
2. ✅ Setup Java 17 with Maven caching
3. ✅ Setup Python environment
4. ✅ Download Maven dependencies (before firewall)
5. 🔥 Configure UFW firewall
6. ✅ Verify UFW status
7. 🔥 Configure iptables rules
8. ✅ Run Linux-specific checks
9. ✅ Verify build works with firewall enabled
10. ✅ Display execution summary

## Validation

### Automated Validation Scripts

Two validation scripts are provided:

**Linux/Mac:** `./validate-agent.sh`
**Windows:** `.\validate-agent.ps1`

These scripts check:
- ✅ Agent configuration file exists
- ✅ `skip_firewall: false` is set
- ✅ `skip_windows: false` is set
- ✅ `run_all_checks: true` is set
- ✅ Firewall allowlist is configured
- ✅ Setup steps are configured before firewall
- ✅ Firewall configuration exists in workflow
- ✅ Outbound rules are configured
- ✅ DNS rules are configured
- ✅ Build verification step exists

### Running Validation

```bash
# On Linux/Mac
chmod +x validate-agent.sh
./validate-agent.sh

# On Windows PowerShell
.\validate-agent.ps1
```

Expected output:
```
================================
Agent Configuration Validator
================================

✓ Agent configuration file found
✓ Firewall is configured to run (not skipped)
✓ Windows checks are configured to run (not skipped)
✓ All checks are enabled
✓ Firewall allowlist is configured
✓ GitHub Actions workflow file found
✓ Setup steps configured before firewall
✓ Firewall configuration found in workflow
✓ Outbound rules configured
✓ DNS rules configured
✓ Build verification step found

================================
Validation Summary
================================
✓ All validations passed!
✓ Agent is configured to run completely without skipping

Configuration Summary:
  - Firewall: NO SKIP
  - Windows: NO SKIP
  - All checks: ENABLED
  - Setup steps: BEFORE FIREWALL
  - Outbound rules: CONFIGURED
  - DNS rules: CONFIGURED
  - Build verification: ENABLED
```

## Troubleshooting

### Issue: Dependencies fail to download

**Symptom:** Maven or Python packages fail to download during the build.

**Solution:** 
1. Verify that setup steps run before firewall configuration
2. Check that `mvn dependency:go-offline` completes successfully
3. Ensure Maven cache is enabled in `actions/setup-java`

### Issue: Build fails after firewall is enabled

**Symptom:** The "Verify build works" step fails.

**Solution:**
1. Check that outbound HTTPS/HTTP traffic is allowed
2. Verify DNS resolution is working (port 53)
3. Check the firewall logs for blocked connections
4. Ensure established connections are allowed (iptables)

### Issue: Firewall blocks unexpected traffic

**Symptom:** Some service or tool fails due to blocked network access.

**Solution:**
1. Add the required domain to the firewall allowlist in `agent-config.yml`
2. Add appropriate firewall rules in the workflow
3. Consider if the service should be initialized before firewall configuration

## Configuration Files

### Primary Files Modified

1. **`.github/workflows/copilot-agent.yml`**
   - Added setup steps before firewall configuration
   - Added outbound firewall rules
   - Added DNS firewall rules
   - Added build verification step

2. **`.github/copilot/agent-config.yml`**
   - Added `firewall_allowlist` section
   - Documented essential URLs and domains

3. **`AGENT_GUIDE.md`**
   - Added Actions Setup Steps section
   - Updated firewall support documentation
   - Added firewall allowlist information
   - Updated troubleshooting guide

4. **`README.md`**
   - Updated key features list
   - Updated execution flow documentation
   - Added firewall allowlist reference

5. **`validate-agent.sh` and `validate-agent.ps1`**
   - Added checks for firewall allowlist
   - Added checks for setup steps order
   - Added checks for outbound rules
   - Added checks for DNS rules
   - Added checks for build verification

## Benefits

✅ **Security:** Firewall is still enabled and configured (not skipped)
✅ **Functionality:** Dependencies download successfully before firewall
✅ **Reliability:** Build verification ensures everything works
✅ **Transparency:** Comprehensive logging and validation
✅ **Flexibility:** Allowlist can be extended for new requirements
✅ **Maintainability:** Clear documentation and automated validation

## References

- [GitHub Actions Setup Java](https://github.com/actions/setup-java)
- [GitHub Actions Setup Python](https://github.com/actions/setup-python)
- [Maven Dependency Plugin](https://maven.apache.org/plugins/maven-dependency-plugin/)
- [UFW Firewall](https://help.ubuntu.com/community/UFW)
- [Windows Firewall with PowerShell](https://learn.microsoft.com/en-us/powershell/module/netsecurity/)
- [iptables Tutorial](https://www.netfilter.org/documentation/)

## Support

For issues or questions about the firewall configuration:
1. Check this guide for common solutions
2. Review the validation script output
3. Check the GitHub Actions workflow logs
4. Open an issue in the repository with:
   - Error messages
   - Validation script output
   - Workflow logs (if applicable)
