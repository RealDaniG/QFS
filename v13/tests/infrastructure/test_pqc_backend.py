
"""
Infrastructure tests for PQC backend configuration.
Ensures CI/CD environment expectations are met and creating documentation exists.
"""

import pytest
import os
from pathlib import Path

# Try to import PQC to check backend status
# Note: PQC import might initialize the backend immediately
try:
    from v13.libs.PQC import PQC
except ImportError:
    PQC = None

def test_ci_pqc_backend_is_development():
    """
    CI/CD environments use development PQC backend.
    
    Production liboqs backend is NOT expected in CI.
    This is intentional and correct.
    """
    if PQC is None:
        pytest.skip("PQC module could not be imported")

    # Access backend info
    info = PQC.get_backend_info()
    backend = info.get("backend")
    
    # CI should use either:
    # 1. pqcrystals/dilithium (pure Python or C-ext if wheels avail)
    # 2. MockPQC (fallback or integration testing)
    # 3. liboqs (only if explicitly set up in a specific Linux CI job)
    
    # In our current Phase 1 setup (Windows/Ubuntu CI), we generally expect 'pqcrystals' (via dilithium pkg) or 'mock'
    # We DO NOT expect 'liboqs' unless we added that specific job.
    
    accepted_backends = ["pqcrystals", "mock", "liboqs-python"] # 'pqcrystals' is what our PQC.py reports for dilithium pkg
    
    assert backend in accepted_backends, (
        f"CI detected unexpected backend: {backend}. "
        f"See docs/architecture/PQC_BACKENDS.md"
    )

def test_production_pqc_requirements_documented():
    """
    Ensure production PQC requirements are explicitly documented.
    """
    # Locate repo root relative to this test file
    # v13/tests/infrastructure/test_pqc_backend.py -> ../../../
    repo_root = Path(__file__).parent.parent.parent.parent
    
    docs_path = repo_root / "v13/docs/compliance/PQC_PRODUCTION.md"
    
    assert docs_path.exists(), (
        "Production PQC documentation missing. "
        f"Expected path: {docs_path.absolute()}. "
        "See docs/architecture/PQC_BACKENDS.md for creation template."
    )
    
    content = docs_path.read_text(encoding='utf-8')
    assert "liboqs" in content
    assert "Linux" in content
    assert "Ubuntu 22.04" in content

def test_invalid_dependency_rejected():
    """
    Regression test: Ensure dilithium-py is never reintroduced.
    """
    repo_root = Path(__file__).parent.parent.parent.parent
    req_file = repo_root / "requirements.txt"
    
    if not req_file.exists():
        pytest.skip("requirements.txt not found at repo root")
        
    content = req_file.read_text(encoding='utf-8')
    
    # This dependency does not exist on PyPI and will break CI
    assert "dilithium-py" not in content, (
        "CRITICAL: dilithium-py does not exist on PyPI. "
        "Use 'dilithium>=1.0.0,<2.0.0' instead. "
        "See CI failure logs from 2025-12-15."
    )
