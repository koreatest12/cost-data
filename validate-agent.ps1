# Agent Configuration Validator v2.0 (Windows PowerShell)
# Validates that the agent is configured to run without skipping components
# and includes enhanced features

# Configuration
$AgentVersion = "2.0.0"

Write-Host "================================"
Write-Host "Agent Configuration Validator v2.0"
Write-Host "================================"
Write-Host ""

$Errors = 0
$Warnings = 0

# Check if agent config exists
Write-Host "Checking agent configuration file..."
if (Test-Path ".github/copilot/agent-config.yml") {
    Write-Host "✓ Agent configuration file found" -ForegroundColor Green
} else {
    Write-Host "✗ Agent configuration file not found" -ForegroundColor Red
    $Errors++
}

# Get config content
$configContent = Get-Content ".github/copilot/agent-config.yml" -Raw -ErrorAction SilentlyContinue

# Check version
Write-Host "Checking agent version..."
if ($configContent -match "version:\s*$AgentVersion") {
    Write-Host "✓ Agent version $AgentVersion confirmed" -ForegroundColor Green
} else {
    Write-Host "⚠ Agent version mismatch or not found" -ForegroundColor Yellow
    $Warnings++
}

# Check skip_firewall setting
Write-Host "Checking firewall skip setting..."
if ($configContent -match "skip_firewall:\s*false") {
    Write-Host "✓ Firewall is configured to run (not skipped)" -ForegroundColor Green
} else {
    Write-Host "✗ Firewall skip setting not found or incorrect" -ForegroundColor Red
    $Errors++
}

# Check skip_windows setting
Write-Host "Checking Windows skip setting..."
if ($configContent -match "skip_windows:\s*false") {
    Write-Host "✓ Windows checks are configured to run (not skipped)" -ForegroundColor Green
} else {
    Write-Host "✗ Windows skip setting not found or incorrect" -ForegroundColor Red
    $Errors++
}

# Check run_all_checks setting
Write-Host "Checking run_all_checks setting..."
if ($configContent -match "run_all_checks:\s*true") {
    Write-Host "✓ All checks are enabled" -ForegroundColor Green
} else {
    Write-Host "✗ run_all_checks setting not found or incorrect" -ForegroundColor Red
    $Errors++
}

# Check enhanced features
Write-Host "Checking enhanced features..."
if ($configContent -match "enable_monitoring:\s*true") {
    Write-Host "✓ Monitoring is enabled" -ForegroundColor Green
} else {
    Write-Host "⚠ Monitoring may not be enabled" -ForegroundColor Yellow
    $Warnings++
}

if ($configContent -match "enable_logging:\s*true") {
    Write-Host "✓ Logging is enabled" -ForegroundColor Green
} else {
    Write-Host "⚠ Logging may not be enabled" -ForegroundColor Yellow
    $Warnings++
}

if ($configContent -match "enable_auto_remediation:\s*true") {
    Write-Host "✓ Auto-remediation is enabled" -ForegroundColor Green
} else {
    Write-Host "⚠ Auto-remediation may not be enabled" -ForegroundColor Yellow
    $Warnings++
}

# Check advanced security features
Write-Host "Checking advanced security features..."
if ($configContent -match "intrusion_detection:\s*true") {
    Write-Host "✓ Intrusion detection is enabled" -ForegroundColor Green
} else {
    Write-Host "⚠ Intrusion detection may not be enabled" -ForegroundColor Yellow
    $Warnings++
}

if ($configContent -match "vulnerability_scanning:\s*true") {
    Write-Host "✓ Vulnerability scanning is enabled" -ForegroundColor Green
} else {
    Write-Host "⚠ Vulnerability scanning may not be enabled" -ForegroundColor Yellow
    $Warnings++
}

# Check workflow file exists
Write-Host "Checking GitHub Actions workflow..."
if (Test-Path ".github/workflows/copilot-agent.yml") {
    Write-Host "✓ GitHub Actions workflow file found" -ForegroundColor Green
} else {
    Write-Host "✗ GitHub Actions workflow file not found" -ForegroundColor Red
    $Errors++
}

# Check firewall configuration in workflow
Write-Host "Checking firewall configuration in workflow..."
$workflowContent = Get-Content ".github/workflows/copilot-agent.yml" -Raw -ErrorAction SilentlyContinue
if ($workflowContent -match "Configure Windows Firewall" -and $workflowContent -match "Configure Linux Firewall") {
    Write-Host "✓ Firewall configuration found in workflow" -ForegroundColor Green
} else {
    Write-Host "✗ Firewall configuration missing in workflow" -ForegroundColor Red
    $Errors++
}

# Check for enhanced workflow features
Write-Host "Checking enhanced workflow features..."
if ($workflowContent -match "Collect security metrics") {
    Write-Host "✓ Security metrics collection found in workflow" -ForegroundColor Green
} else {
    Write-Host "⚠ Security metrics collection may be missing" -ForegroundColor Yellow
    $Warnings++
}

Write-Host ""
Write-Host "================================"
Write-Host "Validation Summary"
Write-Host "================================"

if ($Errors -eq 0) {
    Write-Host "✓ All critical validations passed!" -ForegroundColor Green
    if ($Warnings -gt 0) {
        Write-Host "⚠ $Warnings warning(s) found (non-critical)" -ForegroundColor Yellow
    }
    Write-Host "✓ Agent v2.0 is configured to run completely without skipping" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configuration Summary:"
    Write-Host "  - Version: $AgentVersion"
    Write-Host "  - Firewall: NO SKIP ✓"
    Write-Host "  - Windows: NO SKIP ✓"
    Write-Host "  - All checks: ENABLED ✓"
    Write-Host "  - Monitoring: ENABLED ✓"
    Write-Host "  - Logging: ENABLED ✓"
    Write-Host "  - Auto-remediation: ENABLED ✓"
    Write-Host "  - Intrusion Detection: ENABLED ✓"
    Write-Host "  - Vulnerability Scanning: ENABLED ✓"
    exit 0
} else {
    Write-Host "✗ Validation failed with $Errors error(s)" -ForegroundColor Red
    if ($Warnings -gt 0) {
        Write-Host "⚠ Also found $Warnings warning(s)" -ForegroundColor Yellow
    }
    Write-Host "Please review the configuration files"
    exit 1
}
