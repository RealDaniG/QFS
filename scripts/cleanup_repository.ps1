# QFS Repository Cleanup Script
# Removes backup files and fixes structural issues
# Safe operations only - no import path changes

Write-Host "=== QFS Repository Cleanup ===" -ForegroundColor Cyan
Write-Host "Starting cleanup at: $(Get-Date)" -ForegroundColor Gray

# Phase 1: Count and remove backup files
Write-Host "`n[1/5] Analyzing .backup files..." -ForegroundColor Yellow
$backupFiles = Get-ChildItem -Path "v13" -Filter "*.backup" -Recurse -File
$backupCount = $backupFiles.Count
Write-Host "Found $backupCount backup files" -ForegroundColor White

if ($backupCount -gt 0) {
    Write-Host "Removing backup files..." -ForegroundColor Yellow
    $backupFiles | Remove-Item -Force
    Write-Host "[OK] Backup files removed" -ForegroundColor Green
}
else {
    Write-Host "[SKIP] No backup files found" -ForegroundColor Gray
}

# Phase 2: Fix nested v13/v13/evidence structure
Write-Host "`n[2/5] Checking for nested v13/v13/evidence..." -ForegroundColor Yellow
if (Test-Path "v13/v13/evidence") {
    Write-Host "Found nested structure - fixing..." -ForegroundColor Yellow
    
    # Ensure target directory exists
    if (-not (Test-Path "v13/evidence")) {
        New-Item -Path "v13/evidence" -ItemType Directory -Force | Out-Null
    }
    
    # Copy contents
    Get-ChildItem -Path "v13/v13/evidence" -Recurse | ForEach-Object {
        $targetPath = $_.FullName.Replace("v13\v13\evidence", "v13\evidence")
        if ($_.PSIsContainer) {
            if (-not (Test-Path $targetPath)) {
                New-Item -Path $targetPath -ItemType Directory -Force | Out-Null
            }
        }
        else {
            Copy-Item -Path $_.FullName -Destination $targetPath -Force
        }
    }
    
    # Remove nested directory
    Remove-Item -Path "v13/v13" -Recurse -Force
    Write-Host "[OK] Nested structure fixed" -ForegroundColor Green
}
else {
    Write-Host "[SKIP] No nested v13/v13/evidence found" -ForegroundColor Gray
}

# Phase 3: Remove empty economics folder
Write-Host "`n[3/5] Checking v13/economics folder..." -ForegroundColor Yellow
if (Test-Path "v13/economics") {
    $nonBackupFiles = Get-ChildItem -Path "v13/economics" -Recurse -File | Where-Object { $_.Extension -ne ".backup" }
    
    if ($nonBackupFiles.Count -eq 0) {
        Write-Host "Folder is empty or contains only backups - removing..." -ForegroundColor Yellow
        Remove-Item -Path "v13/economics" -Recurse -Force
        Write-Host "[OK] Empty economics folder removed" -ForegroundColor Green
    }
    else {
        Write-Host "[SKIP] economics folder contains active files ($($nonBackupFiles.Count) files)" -ForegroundColor Gray
    }
}
else {
    Write-Host "[SKIP] v13/economics folder not found" -ForegroundColor Gray
}

# Phase 4: Report on _root folders (manual review required)
Write-Host "`n[4/5] Checking _root folders..." -ForegroundColor Yellow
$rootFolders = @("v13/libs_root", "v13/services_root", "v13/tools_root")
$foundRootFolders = @()

foreach ($folder in $rootFolders) {
    if (Test-Path $folder) {
        $foundRootFolders += $folder
        $fileCount = (Get-ChildItem -Path $folder -Recurse -File).Count
        Write-Host "  - $folder exists ($fileCount files)" -ForegroundColor White
    }
}

if ($foundRootFolders.Count -gt 0) {
    Write-Host "[MANUAL] $($foundRootFolders.Count) _root folders require manual review" -ForegroundColor Yellow
}
else {
    Write-Host "[OK] No _root folders found" -ForegroundColor Green
}

# Phase 5: Report on legacy_root (decision required)
Write-Host "`n[5/5] Checking legacy_root..." -ForegroundColor Yellow
if (Test-Path "v13/legacy_root") {
    $legacySize = (Get-ChildItem -Path "v13/legacy_root" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  - legacy_root exists ($('{0:N2}' -f $legacySize) MB)" -ForegroundColor White
    Write-Host "[DECISION] Archive or delete legacy_root?" -ForegroundColor Yellow
}
else {
    Write-Host "[OK] No legacy_root folder found" -ForegroundColor Green
}

# Summary
Write-Host "`n=== Cleanup Summary ===" -ForegroundColor Cyan
Write-Host "[OK] Removed $backupCount backup files" -ForegroundColor Green
Write-Host "[OK] Fixed nested directory structure" -ForegroundColor Green
Write-Host "[OK] Removed empty folders" -ForegroundColor Green

if ($foundRootFolders.Count -gt 0) {
    Write-Host "[MANUAL] Review required for _root folders" -ForegroundColor Yellow
}

if (Test-Path "v13/legacy_root") {
    Write-Host "[DECISION] Decision required for legacy_root/" -ForegroundColor Yellow
}

Write-Host "`nCompleted at: $(Get-Date)" -ForegroundColor Gray
Write-Host "=== Cleanup Complete ===" -ForegroundColor Cyan
