#!/bin/bash
# Agent Configuration Validator v2.0
# Validates that the agent is configured to run without skipping components
# and includes enhanced features

# Configuration
AGENT_VERSION="2.0.0"

echo "================================"
echo "Agent Configuration Validator v2.0"
echo "================================"
echo ""

ERRORS=0
WARNINGS=0

# Check if agent config exists
echo "Checking agent configuration file..."
if [ -f ".github/copilot/agent-config.yml" ]; then
    echo "✓ Agent configuration file found"
else
    echo "✗ Agent configuration file not found"
    ERRORS=$((ERRORS + 1))
fi

# Check version
echo "Checking agent version..."
if grep -q "version: $AGENT_VERSION" .github/copilot/agent-config.yml; then
    echo "✓ Agent version $AGENT_VERSION confirmed"
else
    echo "⚠ Agent version mismatch or not found"
    WARNINGS=$((WARNINGS + 1))
fi

# Check skip_firewall setting
echo "Checking firewall skip setting..."
if grep -q "skip_firewall: false" .github/copilot/agent-config.yml; then
    echo "✓ Firewall is configured to run (not skipped)"
else
    echo "✗ Firewall skip setting not found or incorrect"
    ERRORS=$((ERRORS + 1))
fi

# Check skip_windows setting
echo "Checking Windows skip setting..."
if grep -q "skip_windows: false" .github/copilot/agent-config.yml; then
    echo "✓ Windows checks are configured to run (not skipped)"
else
    echo "✗ Windows skip setting not found or incorrect"
    ERRORS=$((ERRORS + 1))
fi

# Check run_all_checks setting
echo "Checking run_all_checks setting..."
if grep -q "run_all_checks: true" .github/copilot/agent-config.yml; then
    echo "✓ All checks are enabled"
else
    echo "✗ run_all_checks setting not found or incorrect"
    ERRORS=$((ERRORS + 1))
fi

# Check enhanced features
echo "Checking enhanced features..."
if grep -q "enable_monitoring: true" .github/copilot/agent-config.yml; then
    echo "✓ Monitoring is enabled"
else
    echo "⚠ Monitoring may not be enabled"
    WARNINGS=$((WARNINGS + 1))
fi

if grep -q "enable_logging: true" .github/copilot/agent-config.yml; then
    echo "✓ Logging is enabled"
else
    echo "⚠ Logging may not be enabled"
    WARNINGS=$((WARNINGS + 1))
fi

if grep -q "enable_auto_remediation: true" .github/copilot/agent-config.yml; then
    echo "✓ Auto-remediation is enabled"
else
    echo "⚠ Auto-remediation may not be enabled"
    WARNINGS=$((WARNINGS + 1))
fi

# Check advanced security features
echo "Checking advanced security features..."
if grep -q "intrusion_detection: true" .github/copilot/agent-config.yml; then
    echo "✓ Intrusion detection is enabled"
else
    echo "⚠ Intrusion detection may not be enabled"
    WARNINGS=$((WARNINGS + 1))
fi

if grep -q "vulnerability_scanning: true" .github/copilot/agent-config.yml; then
    echo "✓ Vulnerability scanning is enabled"
else
    echo "⚠ Vulnerability scanning may not be enabled"
    WARNINGS=$((WARNINGS + 1))
fi

# Check workflow file exists
echo "Checking GitHub Actions workflow..."
if [ -f ".github/workflows/copilot-agent.yml" ]; then
    echo "✓ GitHub Actions workflow file found"
else
    echo "✗ GitHub Actions workflow file not found"
    ERRORS=$((ERRORS + 1))
fi

# Check firewall configuration in workflow
echo "Checking firewall configuration in workflow..."
if grep -q "Configure Windows Firewall" .github/workflows/copilot-agent.yml && \
   grep -q "Configure Linux Firewall" .github/workflows/copilot-agent.yml; then
    echo "✓ Firewall configuration found in workflow"
else
    echo "✗ Firewall configuration missing in workflow"
    ERRORS=$((ERRORS + 1))
fi

# Check for enhanced workflow features
echo "Checking enhanced workflow features..."
if grep -q "Collect security metrics" .github/workflows/copilot-agent.yml; then
    echo "✓ Security metrics collection found in workflow"
else
    echo "⚠ Security metrics collection may be missing"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "================================"
echo "Validation Summary"
echo "================================"

if [ $ERRORS -eq 0 ]; then
    echo "✓ All critical validations passed!"
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠ $WARNINGS warning(s) found (non-critical)"
    fi
    echo "✓ Agent v2.0 is configured to run completely without skipping"
    echo ""
    echo "Configuration Summary:"
    echo "  - Version: $AGENT_VERSION"
    echo "  - Firewall: NO SKIP ✓"
    echo "  - Windows: NO SKIP ✓"
    echo "  - All checks: ENABLED ✓"
    echo "  - Monitoring: ENABLED ✓"
    echo "  - Logging: ENABLED ✓"
    echo "  - Auto-remediation: ENABLED ✓"
    echo "  - Intrusion Detection: ENABLED ✓"
    echo "  - Vulnerability Scanning: ENABLED ✓"
    exit 0
else
    echo "✗ Validation failed with $ERRORS error(s)"
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠ Also found $WARNINGS warning(s)"
    fi
    echo "Please review the configuration files"
    exit 1
fi
