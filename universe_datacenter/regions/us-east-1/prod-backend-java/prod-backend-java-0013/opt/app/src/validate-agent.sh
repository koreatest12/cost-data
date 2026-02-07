#!/bin/bash
# Agent Configuration Validator
# Validates that the agent is configured to run without skipping components

echo "================================"
echo "Agent Configuration Validator"
echo "================================"
echo ""

ERRORS=0

# Check if agent config exists
echo "Checking agent configuration file..."
if [ -f ".github/copilot/agent-config.yml" ]; then
    echo "✓ Agent configuration file found"
else
    echo "✗ Agent configuration file not found"
    ERRORS=$((ERRORS + 1))
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

echo ""
echo "================================"
echo "Validation Summary"
echo "================================"

if [ $ERRORS -eq 0 ]; then
    echo "✓ All validations passed!"
    echo "✓ Agent is configured to run completely without skipping"
    echo ""
    echo "Configuration Summary:"
    echo "  - Firewall: NO SKIP"
    echo "  - Windows: NO SKIP"
    echo "  - All checks: ENABLED"
    exit 0
else
    echo "✗ Validation failed with $ERRORS error(s)"
    echo "Please review the configuration files"
    exit 1
fi
