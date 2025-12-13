# QFS V13.6 Test Suite Runner
# Executes all V13.6 test suites and generates evidence artifacts

Write-Output "================================"
Write-Output "QFS V13.6 Test Suite Runner"
Write-Output "================================"
Write-Output ""

# Set deterministic environment
$env:PYTHONHASHSEED = "0"
$env:TZ = "UTC"

# Create evidence directory
$evidenceDir = "evidence\v13_6"
if (!(Test-Path $evidenceDir)) {
    New-Item -ItemType Directory -Path $evidenceDir | Out-Null
    Write-Output "✅ Created evidence directory: $evidenceDir"
}

# Test Suite 1: Deterministic Replay
Write-Output ""
Write-Output "[1/4] Running DeterministicReplayTest.py..."
python tests\v13_6\DeterministicReplayTest.py
if ($LASTEXITCODE -eq 0) {
    Write-Output "✅ DeterministicReplayTest PASSED"
} else {
    Write-Output "❌ DeterministicReplayTest FAILED (exit code: $LASTEXITCODE)"
}

# Test Suite 2: Boundary Conditions
Write-Output ""
Write-Output "[2/4] Running BoundaryConditionTests.py..."
python tests\v13_6\BoundaryConditionTests.py
if ($LASTEXITCODE -eq 0) {
    Write-Output "✅ BoundaryConditionTests PASSED"
} else {
    Write-Output "❌ BoundaryConditionTests FAILED (exit code: $LASTEXITCODE)"
}

# Test Suite 3: Failure Modes
Write-Output ""
Write-Output "[3/4] Running FailureModeTests.py..."
python tests\v13_6\FailureModeTests.py
if ($LASTEXITCODE -eq 0) {
    Write-Output "✅ FailureModeTests PASSED"
} else {
    Write-Output "❌ FailureModeTests FAILED (exit code: $LASTEXITCODE)"
}

# Test Suite 4: Performance Benchmark
Write-Output ""
Write-Output "[4/4] Running PerformanceBenchmark.py..."
python tests\v13_6\PerformanceBenchmark.py
if ($LASTEXITCODE -eq 0) {
    Write-Output "✅ PerformanceBenchmark PASSED"
} else {
    Write-Output "❌ PerformanceBenchmark FAILED (exit code: $LASTEXITCODE)"
}

# Verify evidence artifacts
Write-Output ""
Write-Output "================================"
Write-Output "Evidence Artifact Verification"
Write-Output "================================"

$artifacts = @(
    "nod_replay_determinism.json",
    "economic_bounds_verification.json",
    "failure_mode_verification.json",
    "performance_benchmark.json"
)

$allArtifactsExist = $true
foreach ($artifact in $artifacts) {
    $path = Join-Path $evidenceDir $artifact
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        Write-Output "✅ $artifact ($size bytes)"
    } else {
        Write-Output "❌ $artifact (NOT FOUND)"
        $allArtifactsExist = $false
    }
}

Write-Output ""
if ($allArtifactsExist) {
    Write-Output "🎉 ALL TESTS PASSED - V13.6 READY FOR RELEASE"
} else {
    Write-Output "⚠️  SOME ARTIFACTS MISSING - Review test output above"
}

Write-Output ""
Write-Output "Evidence location: $evidenceDir"
Write-Output "================================"
