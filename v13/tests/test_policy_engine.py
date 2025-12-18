"""
Tests for the policy engine module
"""
import pytest
from v13.policy.policy_engine import PolicyEngine, PolicyConfiguration, PolicyHints, VisibilityLevel, WarningBannerType

class TestPolicyEngine:
    """Test suite for the policy engine"""

    def setup_method(self):
        """Setup test environment"""
        self.policy_engine = PolicyEngine()

    def test_info_advisory_no_block_suggested(self):
        """Test policy hints for info level advisory with no block suggested"""
        advisory = {'block_suggested': False, 'severity': 'info'}
        hints = self.policy_engine.generate_policy_hints(advisory)
        assert hints.visibility_level == VisibilityLevel.VISIBLE
        assert hints.warning_banner == WarningBannerType.NONE
        assert hints.warning_message is None
        assert hints.requires_click_through is False
        assert hints.client_tags == []

    def test_warning_advisory_block_suggested(self):
        """Test policy hints for warning level advisory with block suggested"""
        advisory = {'block_suggested': True, 'severity': 'warning'}
        hints = self.policy_engine.generate_policy_hints(advisory)
        assert hints.visibility_level == VisibilityLevel.WARNED
        assert hints.warning_banner == WarningBannerType.GENERAL
        assert hints.warning_message == 'This content may be inappropriate for some audiences'
        assert hints.requires_click_through is False
        assert 'aegis_severity_warning' in hints.client_tags
        assert 'aegis_block_suggested' in hints.client_tags

    def test_critical_advisory_block_suggested(self):
        """Test policy hints for critical level advisory with block suggested"""
        advisory = {'block_suggested': True, 'severity': 'critical'}
        hints = self.policy_engine.generate_policy_hints(advisory)
        assert hints.visibility_level == VisibilityLevel.HIDDEN
        assert hints.warning_banner == WarningBannerType.SAFETY
        assert hints.warning_message == 'This content has been flagged for safety concerns'
        assert hints.requires_click_through is True
        assert 'aegis_severity_critical' in hints.client_tags
        assert 'aegis_block_suggested' in hints.client_tags

    def test_custom_configuration_less_strict_warnings(self):
        """Test policy engine with custom configuration for less strict warnings"""
        custom_config = PolicyConfiguration(warning_visibility=VisibilityLevel.VISIBLE, require_click_through_for_warning=False, warning_banner=WarningBannerType.SAFETY)
        custom_engine = PolicyEngine(custom_config)
        advisory = {'block_suggested': True, 'severity': 'warning'}
        hints = custom_engine.generate_policy_hints(advisory)
        assert hints.visibility_level == VisibilityLevel.VISIBLE
        assert hints.warning_banner == WarningBannerType.SAFETY
        assert hints.requires_click_through is False
        assert 'aegis_severity_warning' in hints.client_tags
        assert 'aegis_block_suggested' in hints.client_tags

    def test_deterministic_behavior(self):
        """Test that policy engine produces deterministic results"""
        advisory = {'block_suggested': True, 'severity': 'critical'}
        hints1 = self.policy_engine.generate_policy_hints(advisory)
        hints2 = self.policy_engine.generate_policy_hints(advisory)
        assert hints1.visibility_level == hints2.visibility_level
        assert hints1.warning_banner == hints2.warning_banner
        assert hints1.warning_message == hints2.warning_message
        assert hints1.requires_click_through == hints2.requires_click_through
        assert hints1.client_tags == hints2.client_tags

    def test_missing_fields_defaults(self):
        """Test that policy engine handles missing advisory fields gracefully"""
        advisory = {}
        hints = self.policy_engine.generate_policy_hints(advisory)
        assert hints.visibility_level == VisibilityLevel.VISIBLE
        assert hints.warning_banner == WarningBannerType.NONE
        assert hints.warning_message is None
        assert hints.requires_click_through is False
        assert hints.client_tags == []

    def test_edge_case_severity_values(self):
        """Test policy engine with edge case severity values"""
        advisory = {'block_suggested': True, 'severity': 'unknown'}
        hints = self.policy_engine.generate_policy_hints(advisory)
        assert hints.visibility_level == VisibilityLevel.VISIBLE
        assert hints.warning_banner == WarningBannerType.NONE
        assert hints.requires_click_through is False
if __name__ == '__main__':
    pytest.main([__file__])
