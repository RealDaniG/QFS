import unittest
import sys
import os

# Add root to sys.path
sys.path.append(".")

from pydantic import ValidationError
from v13.libs.canonical.models import (
    UserIdentity,
    ContentMetadata,
    EconomicEvent,
    AdvisorySignal,
    ContentType,
)


class TestAPIContracts(unittest.TestCase):
    """
    Validate that canonical models enforce type constraints strictly.
    """

    def test_user_identity_valid(self):
        uid = UserIdentity(
            user_id="user_123", wallet_address="0xABC...", public_key="pqc_pub_key_xyz"
        )
        self.assertEqual(uid.user_id, "user_123")

    def test_user_identity_invalid_missing_fields(self):
        with self.assertRaises(ValidationError):
            UserIdentity(user_id="user_123")  # Missing wallet and pubkey

    def test_content_metadata_enum(self):
        # Valid enum
        cm = ContentMetadata(
            content_id="c1", author_id="u1", timestamp=100, type=ContentType.POST
        )
        self.assertEqual(cm.type, ContentType.POST)

        # Invalid enum value
        with self.assertRaises(ValidationError):
            ContentMetadata(
                content_id="c1", author_id="u1", timestamp=100, type="INVALID_TYPE"
            )

    def test_economic_event_amount_string(self):
        """
        Ensure amount is stored as string/bignum safe.
        """
        ev = EconomicEvent(
            event_id="e1",
            source_id="s1",
            target_id="t1",
            amount="1000000000000000000",  # Big int as string
            token_type="QFS",
            reason="test",
            timestamp=100,
        )
        self.assertIsInstance(ev.amount, str)

    def test_advisory_signal_signature(self):
        sig = AdvisorySignal(
            signal_id="s1",
            issuer_id="i1",
            payload={"recommendation": "BUY"},
            signature="sig_123",
            timestamp=100,
        )
        self.assertEqual(sig.signature, "sig_123")

    # --- Golden Path Tests (Contract Freezing) ---
    def test_golden_path_user_identity(self):
        """Golden path: Standard UserIdentity structure."""
        gold = UserIdentity(
            user_id="u_gold_001",
            wallet_address="0xGoldAddr",
            public_key="pub_gold",
            profile={"tier": "GOLD"},
        )
        # Using model_dump() for Pydantic v2 or dict() for v1
        # Assuming v1 compat based on previous requirements.txt, but v2 is standard now.
        # using dict() for safety or checking attributes directly.
        self.assertEqual(gold.user_id, "u_gold_001")
        self.assertEqual(gold.wallet_address, "0xGoldAddr")
        self.assertEqual(gold.profile, {"tier": "GOLD"})

    def test_golden_path_economic_event(self):
        """Golden path: EconomicEvent precision."""
        gold_evt = EconomicEvent(
            event_id="evt_gold_001",
            source_id="sys",
            target_id="usr",
            amount="1000000000000000000",
            token_type="QFS",
            reason="MINT",
            timestamp=1234567890,
        )
        # MUST remain a string, never float
        self.assertIsInstance(gold_evt.amount, str)
        self.assertEqual(gold_evt.amount, "1000000000000000000")


if __name__ == "__main__":
    unittest.main()
