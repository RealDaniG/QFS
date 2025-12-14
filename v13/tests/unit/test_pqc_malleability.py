import pytest

from v13.libs.PQC import PQC
from v13.core.DRV_Packet import DRV_Packet


def _has_production_pqc_backend() -> bool:
    # PQC.py defines Dilithium5Impl at module scope, but it can end up as:
    # - pqcrystals implementation
    # - liboqs adapter
    # - MockPQC fallback
    # Some parts of PQC.py also reassign Dilithium5Impl later.
    impl = getattr(PQC, "Dilithium5Impl", None)
    if impl is None:
        return False

    # Heuristic: MockPQC is a local class with name `_MockPQC` in PQC.py.
    # We treat that as non-production and skip this test.
    return impl.__class__.__name__ not in {"_MockPQC"}


@pytest.mark.integration
def test_pqc_signature_malleability_production_backend() -> None:
    """Malleability check for PQC signatures.

    This test is only meaningful when a production-grade PQC backend
    is installed (pqcrystals or liboqs). When running with MockPQC, we
    skip to avoid false failures.
    """

    if not _has_production_pqc_backend():
        pytest.skip("Production PQC backend not available (running with MockPQC)")

    log_list = []
    packet = DRV_Packet(
        ttsTimestamp=1700000000,
        sequence=1,
        seed="test_seed_12345",
        log_list=log_list,
    )

    keypair = PQC.generate_keypair(log_list, packet.seed_bytes, PQC.DILITHIUM5)
    packet.sign(bytes(keypair.private_key), log_list)

    original_sig = packet.pqc_signature
    assert original_sig is not None

    # Modify the signature slightly (malleability test)
    sig_modified = bytearray(original_sig)
    sig_modified[-1] ^= 1
    sig_modified = bytes(sig_modified)

    is_valid_original = packet.verify_signature(keypair.public_key, log_list)

    packet.pqc_signature = sig_modified
    is_valid_modified = packet.verify_signature(keypair.public_key, log_list)

    assert is_valid_original is True
    assert is_valid_modified is False