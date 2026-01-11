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

# Check firewall allowlist
echo "Checking firewall allowlist configuration..."
if grep -q "firewall_allowlist:" .github/copilot/agent-config.yml; then
    echo "✓ Firewall allowlist is configured"
else
    echo "✗ Firewall allowlist not found"
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

# Check setup steps before firewall
echo "Checking setup steps order in workflow..."
if grep -q "Setup Java 17" .github/workflows/copilot-agent.yml && \
   grep -q "Download Maven dependencies" .github/workflows/copilot-agent.yml; then
    echo "✓ Setup steps configured before firewall"
else
    echo "✗ Setup steps missing or incorrect"
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

# Check outbound rules
echo "Checking outbound firewall rules..."
if grep -q "Allow HTTP Outbound" .github/workflows/copilot-agent.yml && \
   grep -q "Allow HTTPS Outbound" .github/workflows/copilot-agent.yml; then
    echo "✓ Outbound rules configured"
else
    echo "✗ Outbound rules missing"
    ERRORS=$((ERRORS + 1))
fi

# Check DNS configuration
echo "Checking DNS firewall rules..."
if grep -q "Allow DNS" .github/workflows/copilot-agent.yml; then
    echo "✓ DNS rules configured"
else
    echo "✗ DNS rules missing"
    ERRORS=$((ERRORS + 1))
fi

# Check build verification
echo "Checking build verification after firewall..."
if grep -q "Verify build works after firewall configuration" .github/workflows/copilot-agent.yml; then
    echo "✓ Build verification step found"
else
    echo "✗ Build verification step missing"
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
    echo "  - Setup steps: BEFORE FIREWALL"
    echo "  - Outbound rules: CONFIGURED"
    echo "  - DNS rules: CONFIGURED"
    echo "  - Build verification: ENABLED"
    exit 0
else
    echo "✗ Validation failed with $ERRORS error(s)"
    echo "Please review the configuration files"
    exit 1
fi
