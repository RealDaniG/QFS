import os
from v18.pqc.anchors import PQCBatchAnchorService


def test_anchor_generation_and_verification():
    """Verify that a batch of hashes can be anchored and verified deterministically."""
    os.environ["MOCKQPC_ENABLED"] = "true"
    service = PQCBatchAnchorService()

    hashes = ["hash1", "hash2", "hash3"]
    anchor = service.create_batch_signature(hashes)

    assert "pqc_signature" in anchor
    assert anchor["event_count"] == 3
    assert anchor["algorithm"] == "v18-Dilithium-Anchor"

    # Verify valid signature
    is_valid = service.verify_batch_signature(hashes, anchor["pqc_signature"])
    assert is_valid is True

    # Verify invalid signature (tampered hashes)
    is_valid_bad = service.verify_batch_signature(
        ["hash1", "tampered", "hash3"], anchor["pqc_signature"]
    )
    assert is_valid_bad is False


def test_anchor_determinism():
    """Verify that the same batch always produces the same anchor signature in MOCKQPC mode."""
    os.environ["MOCKQPC_ENABLED"] = "true"
    service = PQCBatchAnchorService()
    hashes = ["a", "b", "c"]

    anchor1 = service.create_batch_signature(hashes)
    anchor2 = service.create_batch_signature(hashes)

    assert anchor1["pqc_signature"] == anchor2["pqc_signature"]
    assert anchor1["batch_root"] == anchor2["batch_root"]
