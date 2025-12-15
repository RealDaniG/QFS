
import pytest
from unittest.mock import AsyncMock, MagicMock
from v13.ledger.referral_ledger import ReferralLedger
from v13.events.referral_events import ReferralCreated, ReferralAccepted, ReferralActivated, ReferralFraudBlocked

@pytest.mark.asyncio
class TestReferralSystem:
    async def test_deterministic_link_creation(self):
        """Test that referral links are created deterministically."""
        mock_ledger = AsyncMock()
        ref_ledger = ReferralLedger(mock_ledger)
        ref_ledger._count_referrals = AsyncMock(return_value=0)
        
        wallet = "0xRefWalletA"
        epoch = 100
        source = "profile"
        
        code1 = await ref_ledger.create_link(wallet, epoch, source)
        code2 = await ref_ledger.create_link(wallet, epoch, source)
        
        assert code1 == code2
        assert len(code1) == 22
        
        # Verify event appended
        assert mock_ledger.append_event.called
        event = mock_ledger.append_event.call_args[0][0]
        assert isinstance(event, ReferralCreated)
        assert event.referrer_wallet == wallet
        assert event.referral_code == code1

    async def test_referral_cap(self):
        """Test that referral cap is enforced."""
        mock_ledger = AsyncMock()
        ref_ledger = ReferralLedger(mock_ledger)
        ref_ledger._count_referrals = AsyncMock(return_value=100) # MAX
        
        with pytest.raises(ValueError, match="REFERRAL_CAP_EXCEEDED"):
            await ref_ledger.create_link("0xFullWallet", 100, "quest")

    async def test_referral_acceptance_success(self):
        """Test successful referral acceptance."""
        mock_ledger = AsyncMock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        referrer = "0xReferrer"
        referee = "0xReferee"
        code = "deterministic_code_123"
        epoch = 101
        device_hash = "hash_xyz"
        
        # Mocks
        ref_ledger._resolve_code = AsyncMock(return_value=referrer)
        ref_ledger._is_duplicate_device = AsyncMock(return_value=False)
        
        await ref_ledger.accept(code, referee, epoch, device_hash)
        
        # Verify
        assert mock_ledger.append_event.called
        event = mock_ledger.append_event.call_args[0][0]
        assert isinstance(event, ReferralAccepted)
        assert event.referrer_wallet == referrer
        assert event.referee_wallet == referee

    async def test_self_referral_fraud(self):
        """Test self-referral blocking."""
        mock_ledger = AsyncMock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        wallet = "0xSameWallet"
        code = "code_for_same"
        
        ref_ledger._resolve_code = AsyncMock(return_value=wallet)
        
        with pytest.raises(ValueError, match="SELF_REFERRAL_BLOCKED"):
            await ref_ledger.accept(code, wallet, 101, "hash_abc")
            
        # Verify fraud logged
        assert mock_ledger.append_event.called
        event = mock_ledger.append_event.call_args[0][0]
        assert isinstance(event, ReferralFraudBlocked)
        assert event.fraud_type == "SELF_REF"

    async def test_duplicate_device_fraud(self):
        """Test duplicate device blocking."""
        mock_ledger = AsyncMock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        ref_ledger._resolve_code = AsyncMock(return_value="0xReferrer")
        ref_ledger._is_duplicate_device = AsyncMock(return_value=True)
        
        with pytest.raises(ValueError, match="DUPLICATE_DEVICE_BLOCKED"):
            await ref_ledger.accept("code", "0xReferee", 101, "hash_known")
            
        # Verify fraud logged
        event = mock_ledger.append_event.call_args[0][0]
        assert isinstance(event, ReferralFraudBlocked)
        assert event.fraud_type == "DUP_DEVICE"

    async def test_referral_activation(self):
        """Test referral activation triggers reward logic."""
        mock_ledger = AsyncMock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        referee = "0xActiveReferee"
        referral_data = {"referrer": "0xReferrer", "code": "code123"}
        ref_ledger._get_pending_referral = AsyncMock(return_value=referral_data)
        # Mock count to trigger tier 1 reward (0 existing -> 1st referral)
        ref_ledger._count_referrals = AsyncMock(return_value=0)
        
        await ref_ledger.activate(referee, "FIRST_QUEST", 102)
        
        # Verify activation event
        assert mock_ledger.append_event.call_count >= 2 # Activation + Reward
        
        # Check Activation Event
        activation_arg = mock_ledger.append_event.call_args_list[0][0][0]
        assert isinstance(activation_arg, ReferralActivated)
        
        # Check Reward Event
        from v13.events.referral_events import ReferralRewarded
        reward_arg = mock_ledger.append_event.call_args_list[1][0][0]
        assert isinstance(reward_arg, ReferralRewarded)
        assert reward_arg.amount_scaled == 10_000_000_000 # 100 FLX (Tier 1)
        assert reward_arg.referrer_wallet == "0xReferrer"
