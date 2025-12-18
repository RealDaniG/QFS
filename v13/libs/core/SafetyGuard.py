"""
SafetyGuard.py - Content safety checks for ATLAS x QFS

Implements the SafetyGuard class for validating content against safety policies
using deterministic models and maintaining full auditability.
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
try:
    from ...libs.CertifiedMath import CertifiedMath, BigNum128
    from ...core.TokenStateBundle import TokenStateBundle
except ImportError:
    try:
        from v13.libs.CertifiedMath import CertifiedMath, BigNum128
        from v13.core.TokenStateBundle import TokenStateBundle
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        try:
            from v13.libs.CertifiedMath import CertifiedMath, BigNum128
            from v13.core.TokenStateBundle import TokenStateBundle
        except ImportError:
            from v13.libs.CertifiedMath import CertifiedMath, BigNum128
            from core.TokenStateBundle import TokenStateBundle

@dataclass
class SafetyValidationResult:
    """Result of safety validation."""
    passed: bool
    risk_score: BigNum128
    explanation: str
    details: Optional[Dict[str, Any]] = None
    policy_version: str = 'SAFETY_GUARD_V1'

class SafetyGuard:
    """
    Content safety guard for ATLAS x QFS.
    
    Validates content against safety policies using deterministic models.
    All operations are fully auditable and deterministic.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the Safety Guard.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance
        self.quantum_metadata = {'component': 'SafetyGuard', 'version': 'QFS-V13-P1-2', 'pqc_scheme': 'Dilithium-5'}

    def validate_content(self, content_text: str, content_metadata: Dict[str, Any], token_bundle: TokenStateBundle, log_list: Optional[List[Dict[str, Any]]]=None, pqc_cid: Optional[str]=None, deterministic_timestamp: int=0) -> SafetyValidationResult:
        """
        Validate content against safety policies.
        
        Args:
            content_text: Text content to validate (can be None or empty)
            content_metadata: Metadata about the content (author, community, etc.)
            token_bundle: Current token state bundle
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            SafetyValidationResult: Validation result with risk assessment
        """
        if log_list is None:
            log_list = []
        if content_text is None:
            content_text = ''
        risk_score = BigNum128(0)
        explicit_keywords = ['explicit', 'nsfw', 'adult']
        found_explicit = any((keyword in content_text.lower() for keyword in explicit_keywords))
        if found_explicit:
            risk_score = self.cm.add(risk_score, BigNum128.from_string('0.8'), log_list, pqc_cid, self.quantum_metadata)
        spam_indicators = ['buy now', 'click here', 'free money', 'urgent', 'limited time', 'act now']
        spam_count = sum((1 for indicator in spam_indicators if indicator in content_text.lower()))
        if spam_count > 0:
            spam_risk = self.cm.mul(BigNum128.from_int(spam_count), BigNum128.from_string('0.1'), log_list, pqc_cid, self.quantum_metadata)
            risk_score = self.cm.add(risk_score, spam_risk, log_list, pqc_cid, self.quantum_metadata)
        if len(content_text.strip()) < 5:
            risk_score = self.cm.add(risk_score, BigNum128.from_string('0.3'), log_list, pqc_cid, self.quantum_metadata)
        one = BigNum128.from_int(1)
        if self.cm.gt(risk_score, one, log_list, pqc_cid, self.quantum_metadata):
            risk_score = one
        threshold = BigNum128.from_string('0.5')
        passed = not self.cm.gt(risk_score, threshold, log_list, pqc_cid, self.quantum_metadata)
        if passed:
            explanation = f'Content safety check passed with risk score {risk_score.to_decimal_string()}'
        else:
            explanation = f'Content safety check failed with risk score {risk_score.to_decimal_string()} (threshold: {threshold.to_decimal_string()})'
        log_entry = {'operation': 'safety_guard_validation', 'content_length': len(content_text), 'explicit_found': found_explicit, 'spam_indicators_found': spam_count, 'risk_score': risk_score.to_decimal_string(), 'passed': passed, 'timestamp': deterministic_timestamp, 'pqc_cid': pqc_cid}
        log_list.append(log_entry)
        return SafetyValidationResult(passed=passed, risk_score=risk_score, explanation=explanation, details={'content_length': len(content_text), 'explicit_found': found_explicit, 'spam_indicators_found': spam_count}, policy_version='SAFETY_GUARD_V1')

    def validate_media(self, media_metadata: Dict[str, Any], token_bundle: TokenStateBundle, log_list: Optional[List[Dict[str, Any]]]=None, pqc_cid: Optional[str]=None, deterministic_timestamp: int=0) -> SafetyValidationResult:
        """
        Validate media content against safety policies.
        
        Args:
            media_metadata: Metadata about the media (type, size, hash, etc.)
            token_bundle: Current token state bundle
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            SafetyValidationResult: Validation result with risk assessment
        """
        if log_list is None:
            log_list = []
        risk_score = BigNum128(0)
        if 'size' in media_metadata:
            size_mb = media_metadata['size'] // (1024 * 1024)
            if size_mb > 100:
                excess_size = size_mb - 100
                size_risk = self.cm.mul(BigNum128.from_int(int(excess_size)), BigNum128.from_string('0.01'), log_list, pqc_cid, self.quantum_metadata)
                risk_score = self.cm.add(risk_score, size_risk, log_list, pqc_cid, self.quantum_metadata)
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4']
        if 'mime_type' in media_metadata and media_metadata['mime_type'] not in allowed_types:
            risk_score = self.cm.add(risk_score, BigNum128.from_string('0.7'), log_list, pqc_cid, self.quantum_metadata)
        one = BigNum128.from_int(1)
        if self.cm.gt(risk_score, one, log_list, pqc_cid, self.quantum_metadata):
            risk_score = one
        threshold = BigNum128.from_string('0.5')
        passed = not self.cm.gt(risk_score, threshold, log_list, pqc_cid, self.quantum_metadata)
        if passed:
            explanation = f'Media safety check passed with risk score {risk_score.to_decimal_string()}'
        else:
            explanation = f'Media safety check failed with risk score {risk_score.to_decimal_string()} (threshold: {threshold.to_decimal_string()})'
        log_entry = {'operation': 'safety_guard_media_validation', 'media_metadata': media_metadata, 'risk_score': risk_score.to_decimal_string(), 'passed': passed, 'timestamp': deterministic_timestamp, 'pqc_cid': pqc_cid}
        log_list.append(log_entry)
        return SafetyValidationResult(passed=passed, risk_score=risk_score, explanation=explanation, details=media_metadata, policy_version='SAFETY_GUARD_V1')

def test_safety_guard():
    """Test the SafetyGuard implementation."""
    cm = CertifiedMath()
    safety_guard = SafetyGuard(cm)
    try:
        from ...core.TokenStateBundle import create_token_state_bundle
    except ImportError:
        try:
            from v13.core.TokenStateBundle import create_token_state_bundle
        except ImportError:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
            from v13.core.TokenStateBundle import create_token_state_bundle
    token_bundle = create_token_state_bundle(chr_state={'balance': '100.0'}, flx_state={'balance': '50.0'}, psi_sync_state={'balance': '25.0'}, atr_state={'balance': '30.0'}, res_state={'balance': '40.0'}, nod_state={'balance': '20.0'}, lambda1=BigNum128.from_int(1), lambda2=BigNum128.from_int(1), c_crit=BigNum128.from_int(1), pqc_cid='test_safety_001', timestamp=1234567890)
    log_list = []
    safe_content = 'This is a safe, family-friendly post about quantum computing.'
    safe_metadata = {'author': 'user_123', 'community': 'technology', 'timestamp': 1234567890}
    result1 = safety_guard.validate_content(content_text=safe_content, content_metadata=safe_metadata, token_bundle=token_bundle, log_list=log_list, pqc_cid='test_safety_001', deterministic_timestamp=1234567890)
    unsafe_content = 'This is explicit adult content that should be flagged.'
    unsafe_metadata = {'author': 'user_456', 'community': 'general', 'timestamp': 1234567891}
    result2 = safety_guard.validate_content(content_text=unsafe_content, content_metadata=unsafe_metadata, token_bundle=token_bundle, log_list=log_list, pqc_cid='test_safety_002', deterministic_timestamp=1234567891)
    media_metadata = {'mime_type': 'image/jpeg', 'size': 5 * 1024 * 1024, 'hash': 'QmHash1234567890'}
    result3 = safety_guard.validate_media(media_metadata=media_metadata, token_bundle=token_bundle, log_list=log_list, pqc_cid='test_safety_003', deterministic_timestamp=1234567892)
if __name__ == '__main__':
    test_safety_guard()
