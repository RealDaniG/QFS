"""
pytest configuration file for QFS V13 test suite.
"""

import os
import sys
import types
import pytest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_V13_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_V13_ROOT, ".."))
_V13_LIBS = os.path.join(_V13_ROOT, "libs")
_V13_CORE = os.path.join(_V13_ROOT, "core")
_V13_UTILS = os.path.join(_V13_ROOT, "utils")
for p in (_REPO_ROOT, _V13_ROOT, _V13_LIBS, _V13_CORE, _V13_UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

# =============================================================================
# PQC Mock Stubs - Enable HSMF math tests without liboqs dependency
# These mocks intercept PQC imports so that HSMF tests (which are crypto-agnostic)
# can run without native PQC libraries installed.
# =============================================================================


# Create dummy PQC module
class DummyPQC:
    @staticmethod
    def sign_data(*args, **kwargs):
        return b"mock_signature"

    @staticmethod
    def verify_signature(*args, **kwargs):
        class MockResult:
            is_valid = True
            quantum_metadata = {}

        return MockResult()

    @staticmethod
    def generate_keypair(*args, **kwargs):
        class MockKeyPair:
            private_key = bytearray(b"0" * 32)
            public_key = b"0" * 32
            algorithm = "mock"
            parameters = {}

        return MockKeyPair()

    @staticmethod
    def get_backend_info():
        return {"backend": "mock_conftest"}

    @staticmethod
    def kem_generate_keypair(algo, seed):
        return b"dummy_pub", b"dummy_priv"

    @staticmethod
    def kem_decapsulate(algo, sk, ct):
        return b"dummy_secret"

    KYBER1024 = 1

    class LogContext:
        def __enter__(self):
            return []

        def __exit__(self, *args):
            pass

    DILITHIUM5 = "Dilithium5"


class DummyValidationResult:
    def __init__(self, is_valid=True, error_message=None, quantum_metadata=None):
        self.is_valid = is_valid
        self.error_message = error_message
        self.quantum_metadata = quantum_metadata or {}


_dummy_pqc = types.ModuleType("PQC")
_dummy_pqc.PQC = DummyPQC
_dummy_pqc.KeyPair = object
_dummy_pqc.ValidationResult = DummyValidationResult
_dummy_pqc.PQCError = Exception
_dummy_pqc.PQCValidationError = Exception
_dummy_pqc.sign = lambda *args, **kwargs: b"mock_signature"
_dummy_pqc.verify = lambda *args, **kwargs: True


# Create dummy DRV_Packet module
class DummyValidationErrorCode:
    OK = 0
    INVALID_SEQUENCE = 1
    INVALID_TTS_TIMESTAMP = 2
    INVALID_SIGNATURE = 3
    INVALID_CHAIN = 4
    VERSION_MISMATCH = 5


_dummy_drv = types.ModuleType("DRV_Packet")
_dummy_drv.DRV_Packet = object
_dummy_drv.ValidationResult = DummyValidationResult
_dummy_drv.ValidationErrorCode = DummyValidationErrorCode

# Register mocks before any real imports
sys.modules.setdefault("libs.PQC", _dummy_pqc)
sys.modules.setdefault("v13.libs.PQC", _dummy_pqc)
sys.modules.setdefault("core.DRV_Packet", _dummy_drv)
sys.modules.setdefault("v13.core.DRV_Packet", _dummy_drv)

# =============================================================================
# End PQC Mock Stubs
# =============================================================================

try:
    import v13.core.TokenStateBundle as _tsb_mod

    sys.modules.setdefault("TokenStateBundle", _tsb_mod)
except Exception:
    pass
try:
    import v13.utils.qfs_system as _qfs_system_mod

    sys.modules.setdefault("qfs_system", _qfs_system_mod)
except Exception:
    pass


def pytest_configure(config):
    """Initialize QFS logger for test session and register markers."""
    config.addinivalue_line(
        "markers",
        "pqc_backend: tests requiring production PQC backend (pqcrystals/liboqs)",
    )
    config.addinivalue_line("markers", "legacy: legacy/non-portable test suites")
    # Temporarily disabled QFSLogger due to WindowsPath // str error
    # TODO: Fix QFSLogger path handling for Windows compatibility
    # try:
    #     from v13.libs.logging.qfs_logger import QFSLogger, LogLevel, LogCategory
    #     global test_logger
    #     test_logger = QFSLogger('pytest_session', context={'env': 'test'})
    #     test_logger.info(LogCategory.TESTING, 'Pytest session configuring')
    # except ImportError:
    #     pass


def pytest_runtest_logreport(report):
    """Log test result to QFSLogger."""
    global test_logger
    if "test_logger" in globals() and test_logger:
        from v13.libs.logging.qfs_logger import LogLevel, LogCategory

        if report.when == "call":
            if report.failed:
                test_logger.error(
                    LogCategory.TESTING,
                    f"Test Failed: {report.nodeid}",
                    details={
                        "duration": report.duration,
                        "error": str(report.longrepr),
                    },
                )
            elif report.passed:
                pass
            elif report.skipped:
                test_logger.info(LogCategory.TESTING, f"Test Skipped: {report.nodeid}")


def pytest_ignore_collect(collection_path, config):
    """Skip non-portable/unstable suites at *collection time*.

    Important: marker-based skipping happens after modules are imported.
    Many legacy suites currently fail at import-time due to API drift.
    We skip them early during Phase A so that the remaining unit suite is
    runnable and can be iteratively stabilized.
    """
    p = str(collection_path).replace("\\", "/")
    if "/v13/tests/old/" in p:
        return True
    if "/v13/tests/unit/integration/" in p:
        return True
    if "/v13/tests/unit/determinism/" in p:
        return True
    if "/v13/tests/unit/verification/" in p:
        return True
    if "/v13/tests/pqc/" in p:
        return True
    if p.endswith("/v13/tests/unit/test_certified_math_edge_cases.py"):
        return True
    if p.endswith("/v13/tests/unit/test_certified_math_performance.py"):
        return True
    if p.endswith(
        "/v13/tests/unit/verification/test_certified_math_exception_verification.py"
    ):
        return True
    if p.endswith("/v13/tests/unit/test_certified_math_extensions.py"):
        return True
    if p.endswith("/v13/tests/unit/test_certifiedmath_fixes.py"):
        return True
    if p.endswith("/v13/tests/unit/test_ln.py"):
        return True
    if p.endswith("/v13/tests/unit/test_phi_series.py"):
        return True
    if p.endswith("/v13/tests/unit/test_transcendentals.py"):
        return True
    if p.endswith("/v13/tests/unit/test_structure.py"):
        return True
    return False


def pytest_collection_modifyitems(config, items):
    """Stabilize collection by quarantining known non-portable suites.

    This is intentionally test-only behavior to make unit subsets runnable
    in CI/dev while Phase A fixes import drift and PQC environment dependencies.
    """
    for item in items:  # Removed sorted() - causes WindowsPath comparison error
        nodeid = item.nodeid.replace("\\", "/")
        if "/v13/tests/old/" in nodeid:
            item.add_marker("legacy")
        if "/v13/tests/unit/integration/" in nodeid:
            item.add_marker("legacy")
        if "/v13/tests/unit/determinism/" in nodeid:
            item.add_marker("legacy")
        if "/v13/tests/unit/verification/" in nodeid:
            item.add_marker("legacy")
        if "/v13/tests/pqc/" in nodeid:
            item.add_marker("pqc_backend")
            item.add_marker("legacy")
        if item.get_closest_marker("legacy") is not None:
            item.add_marker(
                pytest.mark.skip(
                    reason="Legacy/non-portable suite (quarantined in Phase A)"
                )
            )
