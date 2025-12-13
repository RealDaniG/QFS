# QFS V13.6 Release - Git Commit and Push Script

Write-Output "================================"
Write-Output "QFS V13.6 Release - Git Operations"
Write-Output "================================"
Write-Output ""

# Check current branch
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Output "Current branch: $currentBranch"
Write-Output ""

# Stage all V13.6 files
Write-Output "Staging V13.6 files..."
git add tests/v13_6/*.py
git add evidence/v13_6/*.json
git add V13.6_RELEASE_SUMMARY.md
git add run_v13_6_tests.ps1
git add docs/qfs-v13.5-dashboard.html
git add CHANGELOG_V13.6.md
git add README.md
git add src/handlers/CIR302_Handler.py
git add docs/qfs_v13_plans/NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md
git add AUTONOMOUS_AUDIT_V2_IMPLEMENTATION.md

# Show status
Write-Output ""
Write-Output "Staged files:"
git status --short

# Commit
Write-Output ""
Write-Output "Creating commit..."
git commit -m "release: QFS V13.6 Constitutional Integration Complete

- 3 constitutional guards deployed (2,352 lines)
- 7 modules guarded (TreasuryEngine, RewardAllocator, NODAllocator, etc.)
- 4 test suites implemented (1,766 lines)
- CIR-302 enhanced with 27+ guard error codes
- Dashboard updated with V13.6 release tab
- Documentation aligned (README, specs, audit prompts)

Guards:
- EconomicsGuard.py (937 lines, 8 methods, 27+ error codes)
- NODInvariantChecker.py (682 lines, NOD-I1..I4)
- AEGIS_Node_Verification.py (733 lines, 5 checks)

Test Suites:
- DeterministicReplayTest.py (373 lines)
- BoundaryConditionTests.py (393 lines)
- FailureModeTests.py (602 lines)
- PerformanceBenchmark.py (398 lines)

Evidence Artifacts:
- nod_replay_determinism.json
- economic_bounds_verification.json
- failure_mode_verification.json
- performance_benchmark.json

Status: Phase 2 Integration 100% COMPLETE
"

if ($LASTEXITCODE -eq 0) {
    Write-Output "✅ Commit created successfully"
    
    # Show last commit
    Write-Output ""
    Write-Output "Last commit:"
    git log -1 --oneline
    
    # Push to remote
    Write-Output ""
    Write-Output "Pushing to origin/$currentBranch..."
    git push origin $currentBranch
    
    if ($LASTEXITCODE -eq 0) {
        Write-Output "✅ Pushed to origin/$currentBranch"
        
        # If on v13-hardening, ask about merging to master
        if ($currentBranch -eq "v13-hardening") {
            Write-Output ""
            Write-Output "To merge to master:"
            Write-Output "  git checkout master"
            Write-Output "  git merge v13-hardening"
            Write-Output "  git push origin master"
            Write-Output "  git tag v13.6.0-constitutional-integration"
            Write-Output "  git push origin v13.6.0-constitutional-integration"
        }
    } else {
        Write-Output "❌ Push failed (exit code: $LASTEXITCODE)"
    }
} else {
    Write-Output "❌ Commit failed (exit code: $LASTEXITCODE)"
}

Write-Output ""
Write-Output "================================"
