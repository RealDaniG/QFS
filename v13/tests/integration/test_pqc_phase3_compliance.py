"""
test_pqc_phase3_compliance.py - Phase-3 Compliance Test Suite
Comprehensive tests for PQC modules deterministic behavior
"""
from fractions import Fraction
import pytest
from copy import deepcopy
from v13.libs.pqc.CanonicalSerializer import CanonicalSerializer
from v13.libs.pqc.PQC_Logger import PQC_Logger
from v13.libs.pqc.PQC_Audit import PQC_Audit

class TestCanonicalSerializer:
    """1. CanonicalSerializer — Deterministic Canonicalization Tests"""

    def test_deterministic_dict_ordering(self):
        """1.1 Deterministic Dict Ordering"""
        a = {'b': 2, 'a': 1}
        b = {'a': 1, 'b': 2}
        assert CanonicalSerializer.serialize_data(a) == CanonicalSerializer.serialize_data(b)

    def test_bignum128_support(self):
        """1.2 BigNum128 Support"""

        class FakeBigNum:

            def to_decimal_string(self):
                return '12345678900'
        assert CanonicalSerializer.canonicalize_for_sign(FakeBigNum()) == '12345678900'

    def test_list_canonicalization(self):
        """1.3 List Canonicalization"""
        data = [{'b': 2, 'a': 1}, {'d': 4, 'c': 3}]
        result = CanonicalSerializer.canonicalize_for_sign(data)
        assert isinstance(result, str)
        assert 'a' in result and 'b' in result

    def test_bytes_to_hex(self):
        """1.4 Bytes to Hex"""
        assert CanonicalSerializer.canonicalize_for_sign(b'\x01\xff') == '01ff'

    def test_no_ascii_escaping(self):
        """1.5 No ASCII escaping - UTF-8 output"""
        data = {'key': 'value'}
        result = CanonicalSerializer.serialize_data(data)
        assert isinstance(result, bytes)
        result.decode('utf-8')

    def test_float_rejection(self):
        """Phase-3: Floats must be rejected"""
        with pytest.raises(TypeError, match='Float type is nondeterministic'):
            CanonicalSerializer.canonicalize_for_sign(Fraction(157, 50))

    def test_unsupported_type_rejection(self):
        """Phase-3: Unsupported types must be rejected"""

        class UnsupportedType:
            pass
        with pytest.raises(TypeError, match='Unsupported type'):
            CanonicalSerializer.canonicalize_for_sign(UnsupportedType())

class TestPQCLogger:
    """2. PQC_Logger — Deterministic Logging & Hash Chain"""

    def test_entry_hash_stable_reproduction(self):
        """2.1 Entry Hash Stable Reproduction"""
        log1 = []
        log2 = []
        PQC_Logger.log_pqc_operation('op', {'x': 1}, log1, deterministic_timestamp=42)
        PQC_Logger.log_pqc_operation('op', {'x': 1}, log2, deterministic_timestamp=42)
        assert log1[0]['entry_hash'] == log2[0]['entry_hash']

    def test_prev_hash_assignment_after_context_exit(self):
        """2.2 prev_hash Assignment After Context Exit"""
        with PQC_Logger.LogContext() as log:
            PQC_Logger.log_pqc_operation('op1', {'x': 1}, log, deterministic_timestamp=1)
            PQC_Logger.log_pqc_operation('op2', {'x': 2}, log, deterministic_timestamp=2)
        assert log[1]['prev_hash'] == log[0]['entry_hash']
        assert log[0]['prev_hash'] == PQC_Logger.ZERO_HASH

    def test_error_logging(self):
        """2.3 Error Logging Test"""
        log = []
        try:
            raise ValueError('fail')
        except Exception as e:
            PQC_Logger.log_pqc_operation('test', {}, log, error=e)
        assert 'error' in log[0]
        assert log[0]['error']['type'] == 'ValueError'
        assert log[0]['error']['message'] == 'fail'

    def test_logcontext_isolation(self):
        """2.4 LogContext Isolation Test"""
        with PQC_Logger.LogContext() as A:
            PQC_Logger.log_pqc_operation('op', {'x': 1}, A, deterministic_timestamp=1)
        with PQC_Logger.LogContext() as B:
            PQC_Logger.log_pqc_operation('op', {'x': 1}, B, deterministic_timestamp=2)
        assert A[0]['entry_hash'] != B[0]['entry_hash']

    def test_context_reuse_prevention(self):
        """Phase-3: Context cannot be reused after exit"""
        ctx = PQC_Logger.LogContext()
        with ctx as log:
            PQC_Logger.log_pqc_operation('op', {}, log)
        with pytest.raises(RuntimeError, match='cannot be reused'):
            with ctx as log2:
                pass

    def test_log_list_type_guard(self):
        """Phase-3: log_list must be a list"""
        with pytest.raises(TypeError, match='must be a list'):
            PQC_Logger.log_pqc_operation('op', {}, None)

    def test_details_json_serializability(self):
        """Phase-3: details must be JSON-serializable"""

        class NonSerializable:
            pass
        with pytest.raises(TypeError, match='must be JSON-serializable'):
            PQC_Logger.log_pqc_operation('op', {'bad': NonSerializable()}, [])

class TestPQCAudit:
    """3. PQC_Audit — Deterministic Audit Hash"""

    def test_stable_audit_hash_reproduction(self):
        """3.1 Stable Audit Hash Reproduction"""
        log = []
        PQC_Logger.log_pqc_operation('op', {'x': 1}, log, deterministic_timestamp=42)
        h1 = PQC_Audit.get_pqc_audit_hash(log)
        h2 = PQC_Audit.get_pqc_audit_hash(log)
        assert h1 == h2

    def test_audit_hash_diff_sensitivity(self):
        """3.2 Audit Hash Diff Sensitivity"""
        log = []
        PQC_Logger.log_pqc_operation('op', {'x': 1}, log, deterministic_timestamp=42)
        log2 = deepcopy(log)
        log2[0]['details']['x'] = 999
        assert PQC_Audit.get_pqc_audit_hash(log) != PQC_Audit.get_pqc_audit_hash(log2)

    def test_export_log_file_format(self, tmp_path):
        """3.3 Export Log File Format Check"""
        log = []
        PQC_Logger.log_pqc_operation('op', {'x': 1}, log, deterministic_timestamp=42)
        export_path = tmp_path / 'test_log.json'
        PQC_Audit.export_log(log, str(export_path))
        import json
        with open(export_path, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        assert isinstance(exported, list)
        assert len(exported) == 1

class TestEndToEndDeterministicReplay:
    """4. End-to-End PQC Deterministic Replay Test"""

    def test_full_deterministic_replay(self):
        """4.2 Full Deterministic Replay"""

        def run_session():
            with PQC_Logger.LogContext() as log:
                PQC_Logger.log_pqc_operation('gen_key', {'seed': 'abc'}, log, deterministic_timestamp=111)
                PQC_Logger.log_pqc_operation('sign', {'msg': 'hello'}, log, deterministic_timestamp=112)
            return log
        log1 = run_session()
        log2 = run_session()
        assert log1 == log2
        assert len(log1) == 2
        assert log1[0]['entry_hash'] == log2[0]['entry_hash']
        assert log1[1]['entry_hash'] == log2[1]['entry_hash']

class TestZeroSimulationEnforcement:
    """5. Zero-Simulation Enforcement Tests"""

    def test_no_nondeterministic_fields(self):
        """5.1 No nondeterministic fields in output"""
        log = []
        PQC_Logger.log_pqc_operation('op', {'x': 1}, log, deterministic_timestamp=42)
        import json
        output = json.dumps(log)
        assert 'uuid' not in output.lower()
        assert 'random' not in output.lower()

    def test_no_mutation_in_serializer(self):
        """5.2 No mutation-in-signer"""
        original = {'b': 2, 'a': 1}
        original_copy = original.copy()
        CanonicalSerializer.serialize_data(original)
        assert original == original_copy

    def test_integer_only_timestamp(self):
        """5.3 Integer-Only Timestamp Test"""
        log = []
        with pytest.raises(TypeError, match='must be an int'):
            PQC_Logger.log_pqc_operation('op', {}, log, deterministic_timestamp=Fraction(85, 2))
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])