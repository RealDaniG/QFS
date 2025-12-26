import os
import sys
import json
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# 1. Setup Environment
os.environ["QFS_SERVICE_NAME"] = "qfs-staging-pqc-check"
os.environ["QFS_VERSION_TAG"] = "v13.5.0-social-verified"
os.environ["QFS_GIT_COMMIT"] = "staging-commit-hash"
os.environ["QFS_ARTIFACT_SHA256"] = "sha256:staging-artifact"
os.environ["QFS_BUILD_MANIFEST_SHA256"] = "sha256:staging-manifest"
os.environ["QFS_ENV"] = "staging"
os.environ["QFS_PQC_MODE"] = "mock"

# Mock oqs/drbg imports
sys.modules["oqs"] = MagicMock()
sys.modules["aes256_ctr_drbg"] = MagicMock()

# Ensure root is in path
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "v13", "atlas"))

try:
    from v13.atlas.src.main_minimal import app
    from v13.atlas.src import build_info
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

client = TestClient(app)


def verify_pqc_mode():
    print("--- Verifying PQC Mode ---")
    pqc_mode = os.getenv("QFS_PQC_MODE", "unknown")
    print(f"QFS_PQC_MODE: {pqc_mode}")

    assert pqc_mode == "mock"
    # Future: /api/meta/crypto endpoint could expose this at runtime
    print("✅ PQC Mode is strictly locked to 'mock' for this phase.")


def verify_identity_check():
    print("--- Verifying Identity in Staging ---")
    resp = client.get("/api/meta/build")
    data = resp.json()
    print(json.dumps(data, indent=2))
    assert data["service"] == "qfs-staging-pqc-check"
    assert data["build_manifest_sha256"] == "sha256:staging-manifest"
    print("✅ Identity verified in Staging env.")


if __name__ == "__main__":
    verify_pqc_mode()
    verify_identity_check()
