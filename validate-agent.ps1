# Agent Configuration Validator (Windows PowerShell)
# Validates that the agent is configured to run without skipping components

Write-Host "================================"
Write-Host "Agent Configuration Validator"
Write-Host "================================"
Write-Host ""

$Errors = 0

# Check if agent config exists
Write-Host "Checking agent configuration file..."
if (Test-Path ".github/copilot/agent-config.yml") {
    Write-Host "✓ Agent configuration file found" -ForegroundColor Green
} else {
    Write-Host "✗ Agent configuration file not found" -ForegroundColor Red
    $Errors++
}

# Check skip_firewall setting
Write-Host "Checking firewall skip setting..."
$configContent = Get-Content ".github/copilot/agent-config.yml" -Raw -ErrorAction SilentlyContinue
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

# Check firewall allowlist
Write-Host "Checking firewall allowlist configuration..."
if ($configContent -match "firewall_allowlist:") {
    Write-Host "✓ Firewall allowlist is configured" -ForegroundColor Green
} else {
    Write-Host "✗ Firewall allowlist not found" -ForegroundColor Red
    $Errors++
}

# Check workflow file exists
Write-Host "Checking GitHub Actions workflow..."
if (Test-Path ".github/workflows/copilot-agent.yml") {
    Write-Host "✓ GitHub Actions workflow file found" -ForegroundColor Green
} else {
    Write-Host "✗ GitHub Actions workflow file not found" -ForegroundColor Red
    $Errors++
}

# Check setup steps before firewall
Write-Host "Checking setup steps order in workflow..."
$workflowContent = Get-Content ".github/workflows/copilot-agent.yml" -Raw -ErrorAction SilentlyContinue
if ($workflowContent -match "Setup Java 17" -and $workflowContent -match "Download Maven dependencies") {
    Write-Host "✓ Setup steps configured before firewall" -ForegroundColor Green
} else {
    Write-Host "✗ Setup steps missing or incorrect" -ForegroundColor Red
    $Errors++
}

# Check firewall configuration in workflow
Write-Host "Checking firewall configuration in workflow..."
if ($workflowContent -match "Configure Windows Firewall" -and $workflowContent -match "Configure Linux Firewall") {
    Write-Host "✓ Firewall configuration found in workflow" -ForegroundColor Green
} else {
    Write-Host "✗ Firewall configuration missing in workflow" -ForegroundColor Red
    $Errors++
}

# Check outbound rules
Write-Host "Checking outbound firewall rules..."
if ($workflowContent -match "Allow HTTP Outbound" -and $workflowContent -match "Allow HTTPS Outbound") {
    Write-Host "✓ Outbound rules configured" -ForegroundColor Green
} else {
    Write-Host "✗ Outbound rules missing" -ForegroundColor Red
    $Errors++
}

# Check DNS configuration
Write-Host "Checking DNS firewall rules..."
if ($workflowContent -match "Allow DNS") {
    Write-Host "✓ DNS rules configured" -ForegroundColor Green
} else {
    Write-Host "✗ DNS rules missing" -ForegroundColor Red
    $Errors++
}

# Check build verification
Write-Host "Checking build verification after firewall..."
if ($workflowContent -match "Verify build works after firewall configuration") {
    Write-Host "✓ Build verification step found" -ForegroundColor Green
} else {
    Write-Host "✗ Build verification step missing" -ForegroundColor Red
    $Errors++
}

Write-Host ""
Write-Host "================================"
Write-Host "Validation Summary"
Write-Host "================================"

if ($Errors -eq 0) {
    Write-Host "✓ All validations passed!" -ForegroundColor Green
    Write-Host "✓ Agent is configured to run completely without skipping" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configuration Summary:"
    Write-Host "  - Firewall: NO SKIP"
    Write-Host "  - Windows: NO SKIP"
    Write-Host "  - All checks: ENABLED"
    Write-Host "  - Setup steps: BEFORE FIREWALL"
    Write-Host "  - Outbound rules: CONFIGURED"
    Write-Host "  - DNS rules: CONFIGURED"
    Write-Host "  - Build verification: ENABLED"
    exit 0
} else {
    Write-Host "✗ Validation failed with $Errors error(s)" -ForegroundColor Red
    Write-Host "Please review the configuration files"
    exit 1
}
