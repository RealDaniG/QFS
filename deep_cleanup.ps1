# Deep Repository Cleanup Script
# Removes legacy folders, consolidates root folders, and organizes files

Write-Host "=== QFS Deep Repository Cleanup ===" -ForegroundColor Cyan
Write-Host "Starting at: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

$removedCount = 0
$movedCount = 0
$errors = @()

# Phase 1: Remove legacy_root
Write-Host "[1/6] Removing legacy_root..." -ForegroundColor Yellow
if (Test-Path "v13\legacy_root") {
    try {
        Remove-Item -Path "v13\legacy_root" -Recurse -Force
        Write-Host "  [OK] legacy_root removed" -ForegroundColor Green
        $removedCount++
    }
    catch {
        Write-Host "  [ERROR] Failed to remove legacy_root" -ForegroundColor Red
        $errors += "legacy_root: $_"
    }
}
else {
    Write-Host "  [SKIP] legacy_root not found" -ForegroundColor Gray
}

# Phase 2: Remove root folders
Write-Host ""
Write-Host "[2/6] Removing _root folders..." -ForegroundColor Yellow

# libs_root
if (Test-Path "v13\libs_root") {
    try {
        # Move checks_tests if exists
        if (Test-Path "v13\libs_root\checks_tests") {
            if (-not (Test-Path "v13\tests\libs_checks")) {
                New-Item -Path "v13\tests\libs_checks" -ItemType Directory -Force | Out-Null
            }
            Copy-Item -Path "v13\libs_root\checks_tests\*" -Destination "v13\tests\libs_checks\" -Recurse -Force -ErrorAction SilentlyContinue
            $movedCount++
        }
        Remove-Item -Path "v13\libs_root" -Recurse -Force
        Write-Host "  [OK] libs_root removed" -ForegroundColor Green
        $removedCount++
    }
    catch {
        Write-Host "  [ERROR] Failed to remove libs_root" -ForegroundColor Red
        $errors += "libs_root: $_"
    }
}

# services_root
if (Test-Path "v13\services_root") {
    try {
        Remove-Item -Path "v13\services_root" -Recurse -Force
        Write-Host "  [OK] services_root removed" -ForegroundColor Green
        $removedCount++
    }
    catch {
        Write-Host "  [ERROR] Failed to remove services_root" -ForegroundColor Red
        $errors += "services_root: $_"
    }
}

# tools_root
if (Test-Path "v13\tools_root") {
    try {
        # Move audit folder if exists
        if (Test-Path "v13\tools_root\audit") {
            if (-not (Test-Path "v13\tools\audit")) {
                Copy-Item -Path "v13\tools_root\audit" -Destination "v13\tools\" -Recurse -Force
                $movedCount++
            }
        }
        Remove-Item -Path "v13\tools_root" -Recurse -Force
        Write-Host "  [OK] tools_root removed" -ForegroundColor Green
        $removedCount++
    }
    catch {
        Write-Host "  [ERROR] Failed to remove tools_root" -ForegroundColor Red
        $errors += "tools_root: $_"
    }
}

# Phase 3: Clean up root-level test files
Write-Host ""
Write-Host "[3/6] Cleaning root-level test files..." -ForegroundColor Yellow

$rootTestFiles = @(
    "debug_test.py",
    "debug_imports.py",
    "test_wallet.py",
    "test_launcher_autonomous.py",
    "parse_report.py",
    "v13\test_violations.py"
)

foreach ($file in $rootTestFiles) {
    if (Test-Path $file) {
        try {
            Remove-Item -Path $file -Force
            Write-Host "  [OK] Removed $(Split-Path -Leaf $file)" -ForegroundColor Green
            $removedCount++
        }
        catch {
            $errors += "$file : $_"
        }
    }
}

# Phase 4: Organize error log files
Write-Host ""
Write-Host "[4/6] Organizing error log files..." -ForegroundColor Yellow

$errorFiles = @(
    "ast_errors.txt",
    "cm_errors.txt",
    "econ_errors.txt",
    "econ_errors_final.txt",
    "econ_errors_final_2.txt",
    "econ_errors_final_3.txt",
    "econ_errors_final_4.txt",
    "econ_errors_final_5.txt",
    "final_test_results.txt",
    "test_results.txt",
    "test.log",
    "type_check_report.txt",
    "type_safety_report.txt"
)

if (-not (Test-Path "logs\error_reports")) {
    New-Item -Path "logs\error_reports" -ItemType Directory -Force | Out-Null
}

foreach ($file in $errorFiles) {
    if (Test-Path $file) {
        try {
            Move-Item -Path $file -Destination "logs\error_reports\" -Force
            Write-Host "  [OK] Moved $(Split-Path -Leaf $file)" -ForegroundColor Green
            $movedCount++
        }
        catch {
            $errors += "$file : $_"
        }
    }
}

# Phase 5: Remove outdated folders
Write-Host ""
Write-Host "[5/6] Removing outdated root folders..." -ForegroundColor Yellow

$outdatedFolders = @(
    "AGENT",
    "CODERV1",
    "CURRENCY",
    "src",
    "tests",
    "zero_sim",
    "test_logs",
    "structure_analysis",
    "wiki_migration",
    "artifacts"
)

foreach ($folder in $outdatedFolders) {
    if (Test-Path $folder) {
        try {
            Remove-Item -Path $folder -Recurse -Force
            Write-Host "  [OK] Removed $folder" -ForegroundColor Green
            $removedCount++
        }
        catch {
            Write-Host "  [ERROR] Failed to remove $folder" -ForegroundColor Red
            $errors += "$folder : $_"
        }
    }
}

# Phase 6: Copy documentation
Write-Host ""
Write-Host "[6/6] Organizing documentation..." -ForegroundColor Yellow

$docFiles = @(
    "BOUNTIES.md",
    "CI_IMPROVEMENTS.md",
    "REGRESSION.md",
    "REPO_STRUCTURE.md",
    "ROOT_CLEANUP_SUMMARY.md",
    "SECURITY_NOTES.md"
)

if (-not (Test-Path "docs\root_docs")) {
    New-Item -Path "docs\root_docs" -ItemType Directory -Force | Out-Null
}

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        try {
            Copy-Item -Path $file -Destination "docs\root_docs\" -Force
            Write-Host "  [OK] Copied $(Split-Path -Leaf $file)" -ForegroundColor Green
        }
        catch {
            $errors += "$file : $_"
        }
    }
}

# Summary
Write-Host ""
Write-Host "=== Cleanup Summary ===" -ForegroundColor Cyan
Write-Host "[OK] Removed $removedCount items" -ForegroundColor Green
Write-Host "[OK] Moved/Copied $movedCount items" -ForegroundColor Green

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "[ERRORS] $($errors.Count) errors occurred:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Completed at: $(Get-Date)" -ForegroundColor Gray
Write-Host "=== Deep Cleanup Complete ===" -ForegroundColor Cyan
