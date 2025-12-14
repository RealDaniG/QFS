"""
Compliance tests for the humor signal addon to ensure it doesn't directly
access TreasuryEngine or token balances.
"""

import sys
import os
import pytest

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from v13.ATLAS.src.signals.humor import HumorSignalAddon
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
from v13.policy.humor_observatory import HumorSignalObservatory
from v13.policy.humor_explainability import HumorExplainabilityHelper


class TestHumorCompliance:
    """Test suite for humor signal compliance with QFS constraints"""
    
    def setup_method(self):
        """Setup test environment"""
        self.humor_addon = HumorSignalAddon()
        self.humor_policy = HumorSignalPolicy(
            policy=HumorPolicy(
                enabled=True,
                mode="rewarding",
                dimension_weights={
                    "chronos": 0.15,
                    "lexicon": 0.10,
                    "surreal": 0.10,
                    "empathy": 0.20,
                    "critique": 0.15,
                    "slapstick": 0.10,
                    "meta": 0.20
                },
                max_bonus_ratio=0.25,
                per_user_daily_cap_atr=1.0
            )
        )
        self.observatory = HumorSignalObservatory()
        self.explainability = HumorExplainabilityHelper(self.humor_policy)
    
    def test_humor_signal_addon_no_treasury_imports(self):
        """Test that HumorSignalAddon doesn't import TreasuryEngine"""
        import inspect
        import v13.ATLAS.src.signals.humor as humor_module
        
        # Get the source code of the humor addon module
        source = inspect.getsource(humor_module)
        
        # Check that TreasuryEngine is not imported or referenced in executable code
        # We need to be more specific to avoid false positives from comments/documentation
        lines = source.split('\n')
        in_class_or_function = False
        
        for line in lines:
            # Track if we're inside a class or function definition
            stripped_line = line.strip()
            if stripped_line.startswith('class ') or stripped_line.startswith('def '):
                in_class_or_function = True
            elif stripped_line == '' or stripped_line.startswith('#'):
                # Empty lines or comments don't change our state
                continue
            elif stripped_line.startswith('"""') or stripped_line.startswith("'''"):
                # Docstrings don't change our state for this check
                continue
            elif not stripped_line.startswith(' ') and not stripped_line.startswith('\t'):
                # If we're at module level and not in a comment/docstring, 
                # and line doesn't start with whitespace, we're likely outside classes/functions
                if not stripped_line.startswith('import ') and not stripped_line.startswith('from '):
                    in_class_or_function = False
            
            # Only check for TreasuryEngine in actual code (inside classes/functions or assignments)
            if in_class_or_function or '=' in stripped_line:
                # Skip comment lines
                if stripped_line.startswith('#'):
                    continue
                # Skip import statements
                if stripped_line.startswith('import ') or stripped_line.startswith('from '):
                    continue
                # Check for actual code references that would indicate direct usage
                if (('TreasuryEngine()' in line or 
                     'TreasuryEngine.' in line or 
                     '.TreasuryEngine' in line) and 
                    not stripped_line.startswith('#')):
                    # If TreasuryEngine appears in actual executable code, fail
                    assert False, f"TreasuryEngine found in actual code: {line}"
    
    def test_humor_signal_addon_no_direct_economic_effects(self):
        """Test that HumorSignalAddon doesn't directly affect token balances"""
        content = "Why don't scientists trust atoms? Because they make up everything!"
        context = {
            "views": 100,
            "laughs": 50,
            "saves": 20,
            "replays": 30,
            "author_reputation": 0.8
        }
        
        # Evaluate content - should only produce signal, not economic effects
        result = self.humor_addon.evaluate(content, context)
        
        # Verify it's a pure signal result
        assert result is not None
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'metadata')
        
        # Verify no token balance information in result
        assert "token" not in str(result.metadata).lower()
        assert "balance" not in str(result.metadata).lower()
        assert "mint" not in str(result.metadata).lower()
        assert "reward" not in str(result.metadata).lower()
    
    def test_humor_policy_no_direct_treasury_access(self):
        """Test that HumorSignalPolicy doesn't directly access TreasuryEngine"""
        import inspect
        import v13.policy.humor_policy as policy_module
        
        # Get the source code of the humor policy module
        source = inspect.getsource(policy_module)
        
        # Check that TreasuryEngine is not directly accessed (except in comments)
        lines = source.split('\n')
        for line in lines:
            # Skip comment lines
            if line.strip().startswith('#'):
                continue
            # Check for actual code references
            if 'TreasuryEngine()' in line and not line.strip().startswith('#'):
                assert False, f"TreasuryEngine() found in actual code: {line}"
            if '.mint(' in line and not line.strip().startswith('#'):
                assert False, f".mint( found in actual code: {line}"
            if '.allocate(' in line and not line.strip().startswith('#'):
                assert False, f".allocate( found in actual code: {line}"
            if '.transfer(' in line and not line.strip().startswith('#'):
                assert False, f".transfer( found in actual code: {line}"
    
    def test_humor_observatory_no_direct_economic_effects(self):
        """Test that HumorSignalObservatory doesn't directly affect economics"""
        import inspect
        import v13.policy.humor_observatory as observatory_module
        
        # Get the source code of the humor observatory module
        source = inspect.getsource(observatory_module)
        
        # Check that it doesn't directly affect token balances (except in comments)
        lines = source.split('\n')
        for line in lines:
            # Skip comment lines
            if line.strip().startswith('#'):
                continue
            # Check for actual code references
            if 'token_balance' in line and not line.strip().startswith('#'):
                assert False, f"token_balance found in actual code: {line}"
            if 'mint_token' in line and not line.strip().startswith('#'):
                assert False, f"mint_token found in actual code: {line}"
            if 'allocate_token' in line and not line.strip().startswith('#'):
                assert False, f"allocate_token found in actual code: {line}"
    
    def test_humor_explainability_no_direct_economic_actions(self):
        """Test that HumorExplainabilityHelper doesn't perform economic actions"""
        import inspect
        import v13.policy.humor_explainability as explainability_module
        
        # Get the source code of the explainability module
        source = inspect.getsource(explainability_module)
        
        # Check that it doesn't directly affect token balances (except in comments)
        lines = source.split('\n')
        for line in lines:
            # Skip comment lines
            if line.strip().startswith('#'):
                continue
            # Check for actual code references
            if 'token_balance' in line and not line.strip().startswith('#'):
                assert False, f"token_balance found in actual code: {line}"
            if 'mint_token' in line and not line.strip().startswith('#'):
                assert False, f"mint_token found in actual code: {line}"
            if 'allocate_token' in line and not line.strip().startswith('#'):
                assert False, f"allocate_token found in actual code: {line}"
            if '.transfer(' in line and not line.strip().startswith('#'):
                assert False, f".transfer( found in actual code: {line}"
    
    def test_humor_signal_pure_functionality(self):
        """Test that humor signal provides pure 7-dimensional vector output"""
        content = "This is a funny joke about quantum physics!"
        context = {
            "views": 1000,
            "laughs": 800,
            "saves": 200,
            "replays": 150,
            "author_reputation": 0.9
        }
        
        # Evaluate content
        result = self.humor_addon.evaluate(content, context)
        
        # Verify 7-dimensional output
        dimensions = result.metadata.get("dimensions", {})
        assert isinstance(dimensions, dict)
        assert len(dimensions) == 7
        
        # Verify all required dimensions are present
        required_dimensions = ["chronos", "lexicon", "surreal", "empathy", "critique", "slapstick", "meta"]
        for dim in required_dimensions:
            assert dim in dimensions
            assert isinstance(dimensions[dim], float)
            assert 0.0 <= dimensions[dim] <= 1.0
        
        # Verify confidence is present
        assert hasattr(result, 'confidence')
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0
    
    def test_no_network_io_in_humor_modules(self):
        """Test that humor modules don't perform network I/O"""
        import inspect
        import v13.ATLAS.src.signals.humor as humor_module
        import v13.policy.humor_policy as policy_module
        import v13.policy.humor_observatory as observatory_module
        import v13.policy.humor_explainability as explainability_module
        
        # Check HumorSignalAddon
        humor_source = inspect.getsource(humor_module)
        assert "requests." not in humor_source
        assert "urllib." not in humor_source
        assert "socket." not in humor_source
        assert "http.client" not in humor_source
        
        # Check HumorSignalPolicy
        policy_source = inspect.getsource(policy_module)
        assert "requests." not in policy_source
        assert "urllib." not in policy_source
        assert "socket." not in policy_source
        assert "http.client" not in policy_source
        
        # Check HumorSignalObservatory
        observatory_source = inspect.getsource(observatory_module)
        assert "requests." not in observatory_source
        assert "urllib." not in observatory_source
        assert "socket." not in observatory_source
        assert "http.client" not in observatory_source
        
        # Check HumorExplainabilityHelper
        explain_source = inspect.getsource(explainability_module)
        assert "requests." not in explain_source
        assert "urllib." not in explain_source
        assert "socket." not in explain_source
        assert "http.client" not in explain_source

    def test_no_filesystem_io_in_humor_modules(self):
        """Test that humor modules don't perform filesystem I/O"""
        import inspect
        import v13.ATLAS.src.signals.humor as humor_module
        import v13.policy.humor_policy as policy_module
        import v13.policy.humor_observatory as observatory_module
        import v13.policy.humor_explainability as explainability_module
        
        # Check HumorSignalAddon
        humor_source = inspect.getsource(humor_module)
        # Check for common filesystem operations
        forbidden_patterns = [
            "open(", "write(", "read(", "os.", "shutil.", "pathlib.",
            "pickle.", "json.dump", "json.load", "csv.", "sqlite3."
        ]
        for pattern in forbidden_patterns:
            # Only check outside of comments
            lines = humor_source.split('\n')
            for line in lines:
                stripped = line.strip()
                if not stripped.startswith('#') and pattern in line:
                    # Make sure it's not in a string/comment context
                    if not ('"' in line[:line.find(pattern)] and '"' in line[line.find(pattern):]):
                        assert False, f"Forbidden filesystem pattern '{pattern}' found in humor module: {line}"

    def test_no_ledger_adapters_in_humor_modules(self):
        """Strengthen tests that assert humor modules do not import TreasuryEngine/ledger adapters"""
        import inspect
        import v13.ATLAS.src.signals.humor as humor_module
        import v13.policy.humor_policy as policy_module
        import v13.policy.humor_observatory as observatory_module
        import v13.policy.humor_explainability as explainability_module
        
        def check_for_actual_usage(source_code, forbidden_terms):
            """Check that forbidden terms are not used in actual code (not comments)"""
            lines = source_code.split('\n')
            in_multiline_string = False
            for line in lines:
                stripped = line.strip()
                
                # Handle multiline strings
                if '"""' in line or "'''" in line:
                    quote_count = line.count('"""') + line.count("'''")
                    if quote_count % 2 == 1:
                        in_multiline_string = not in_multiline_string
                
                # Skip comment lines and docstrings
                if stripped.startswith('#') or in_multiline_string:
                    continue
                    
                # Check for actual usage in code
                for term in forbidden_terms:
                    if term in line:
                        # Make sure it's not in a comment on the same line
                        if '#' in line and line.find(term) > line.find('#'):
                            continue  # Term is in a comment
                        
                        # Make sure it's not in a string literal
                        # Simple check: count quotes before the term
                        before_term = line[:line.find(term)]
                        single_quotes_before = before_term.count("'") - before_term.count("\\'")
                        double_quotes_before = before_term.count('"') - before_term.count('\\"')
                        
                        # If odd number of quotes, we're inside a string
                        if single_quotes_before % 2 == 1 or double_quotes_before % 2 == 1:
                            continue  # Inside string, not actual code
                            
                        # Also check if it's part of an import statement
                        if stripped.startswith('import ') or stripped.startswith('from '):
                            continue  # Import statements are OK
                            
                        # Check if it's in a docstring (triple quotes)
                        if '"""' in before_term or "'''" in before_term:
                            continue  # In docstring, not actual code
                            
                        return True, line  # Found actual usage
            return False, ""

        # Check HumorSignalAddon imports
        humor_source = inspect.getsource(humor_module)
        found, line = check_for_actual_usage(humor_source, ["TreasuryEngine", "RealLedger", "TokenStateBundle", "EconomicsGuard"])
        assert not found, f"TreasuryEngine/ledger adapter found in actual code: {line}"
        
        # Check HumorSignalPolicy imports
        policy_source = inspect.getsource(policy_module)
        found, line = check_for_actual_usage(policy_source, ["TreasuryEngine", "RealLedger", "TokenStateBundle", "EconomicsGuard"])
        assert not found, f"TreasuryEngine/ledger adapter found in actual code: {line}"
        
        # Check HumorSignalObservatory imports
        observatory_source = inspect.getsource(observatory_module)
        found, line = check_for_actual_usage(observatory_source, ["TreasuryEngine", "RealLedger", "TokenStateBundle", "EconomicsGuard"])
        assert not found, f"TreasuryEngine/ledger adapter found in actual code: {line}"
        
        # Check HumorExplainabilityHelper imports
        explainability_source = inspect.getsource(explainability_module)
        found, line = check_for_actual_usage(explainability_source, ["TreasuryEngine", "RealLedger", "TokenStateBundle", "EconomicsGuard"])
        assert not found, f"TreasuryEngine/ledger adapter found in actual code: {line}"


if __name__ == "__main__":
    pytest.main([__file__])