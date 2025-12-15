
import pytest
from unittest.mock import Mock, MagicMock
from v13.ledger.referral_ledger import ReferralLedger
from v13.events.referral_events import ReferralCreated, ReferralAccepted, ReferralActivated, ReferralFraudBlocked

class TestReferralSystem:
    def test_deterministic_link_creation(self):
        """Test that referral links are created deterministically."""
        mock_ledger = Mock()
        ref_ledger = ReferralLedger(mock_ledger)
        ref_ledger._count_referrals = Mock(return_value=0)
        
        wallet = "0xRefWalletA"
        epoch = 100
        source = "profile"
        
        code1 = ref_ledger.create_link(wallet, epoch, source)
        code2 = ref_ledger.create_link(wallet, epoch, source)
        
        assert code1 == code2
        assert len(code1) == 22
        
        # Verify event appended
        assert mock_ledger.append_event.called
        event = mock_ledger.append_event.call_args[0][0]
        assert isinstance(event, ReferralCreated)
        assert event.referrer_wallet == wallet
        assert event.referral_code == code1

    def test_referral_cap(self):
        """Test that referral cap is enforced."""
        mock_ledger = Mock()
        ref_ledger = ReferralLedger(mock_ledger)
        ref_ledger._count_referrals = Mock(return_value=100) # MAX
        
        with pytest.raises(ValueError, match="REFERRAL_CAP_EXCEEDED"):
            ref_ledger.create_link("0xFullWallet", 100, "quest")

    def test_referral_acceptance_success(self):
        """Test successful referral acceptance."""
        mock_ledger = Mock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        referrer = "0xReferrer"
        referee = "0xReferee"
        code = "deterministic_code_123"
        epoch = 101
        device_hash = "hash_xyz"
        
        # Mocks
        ref_ledger._resolve_code = Mock(return_value=referrer)
        ref_ledger._is_duplicate_device = Mock(return_value=False)
        
        ref_ledger.accept(code, referee, epoch, device_hash)
        
        # Verify
        assert mock_ledger.append_event.called
        event = mock_ledger.append_event.call_args[0][0]
        assert isinstance(event, ReferralAccepted)
        assert event.referrer_wallet == referrer
        assert event.referee_wallet == referee

    def test_self_referral_fraud(self):
        """Test self-referral blocking."""
        mock_ledger = Mock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        wallet = "0xSameWallet"
        code = "code_for_same"
        
        ref_ledger._resolve_code = Mock(return_value=wallet)
        
        with pytest.raises(ValueError, match="SELF_REFERRAL_BLOCKED"):
            ref_ledger.accept(code, wallet, 101, "hash_abc")
            
        # Verify fraud logged
        assert mock_ledger.append_event.called
        event = mock_ledger.append_event.call_args[0][0]
        assert isinstance(event, ReferralFraudBlocked)
        assert event.fraud_type == "SELF_REF"

    def test_duplicate_device_fraud(self):
        """Test duplicate device blocking."""
        mock_ledger = Mock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        ref_ledger._resolve_code = Mock(return_value="0xReferrer")
        ref_ledger._is_duplicate_device = Mock(return_value=True)
        
        with pytest.raises(ValueError, match="DUPLICATE_DEVICE_BLOCKED"):
            ref_ledger.accept("code", "0xReferee", 101, "hash_known")
            
        # Verify fraud logged
        event = mock_ledger.append_event.call_args[0][0]
        assert isinstance(event, ReferralFraudBlocked)
        assert event.fraud_type == "DUP_DEVICE"

    def test_referral_activation(self):
        """Test referral activation triggers reward logic."""
        mock_ledger = Mock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        referee = "0xActiveReferee"
        referral_data = {"referrer": "0xReferrer", "code": "code123"}
        ref_ledger._get_pending_referral = Mock(return_value=referral_data)
        # Mock count to trigger tier 1 reward (0 existing -> 1st referral)
        ref_ledger._count_referrals = Mock(return_value=0)
        
        ref_ledger.activate(referee, "FIRST_QUEST", 102)
        
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

    def test_referral_acceptance_invalid_code(self):
        """Test acceptance with an invalid/non-existent code."""
        mock_ledger = Mock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        ref_ledger._resolve_code = Mock(return_value=None)
        
        with pytest.raises(ValueError, match="INVALID_REFERRAL_CODE"):
            ref_ledger.accept("invalid_code", "0xReferee", 101, "hash_xyz")
            
    def test_referral_tiers(self):
        """Test reward tiers are correctly applied."""
        mock_ledger = Mock()
        ref_ledger = ReferralLedger(mock_ledger)
        
        # Helper to test a tier
        def check_tier(referral_count, expected_reward):
            ref_ledger._count_referrals = Mock(return_value=referral_count)
            ref_ledger._get_pending_referral = Mock(return_value={"referrer": "0xRef", "code": "c"})
            
            # Reset mocks
            mock_ledger.reset_mock()
            
            ref_ledger.activate("0xUser", "QUEST", 100)
            
            # Find Reward Event
            # Activated is first, Rewarded is second
            assert mock_ledger.append_event.call_count >= 2
            reward_arg = mock_ledger.append_event.call_args_list[1][0][0]
            assert isinstance(reward_arg, ReferralRewarded)
            assert reward_arg.amount_scaled == expected_reward
            
        # Tier 1: < 5 refs -> 100 FLX
        check_tier(0, 10_000_000_000)
        
        # Tier 2: 5 <= refs < 20 -> 50 FLX
        check_tier(5, 5_000_000_000)
        
        # Tier 3: >= 20 refs -> 10 FLX
        check_tier(20, 1_000_000_000)
        
    def test_referral_link_creation_below_cap(self):
        """Explicit test for success path below cap."""
        mock_ledger = Mock()
        ref_ledger = ReferralLedger(mock_ledger)
        ref_ledger._count_referrals = Mock(return_value=99) # Below max 100
        
        code = ref_ledger.create_link("0xWallet", 100, "source")
        assert code is not None
        assert mock_ledger.append_event.called
