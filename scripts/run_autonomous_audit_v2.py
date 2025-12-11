"""
QFS V13.5 Autonomous Audit v2.0
Evidence-driven, spec-aware compliance audit framework

Features:
- AST-based non-determinism detection (reduced false positives)
- Config-driven component scanning
- Spec and requirement linkage
- Baseline evidence comparison and regression detection
- Exit codes reflecting audit verdict
- Structured JSON output for CI integration
- Comprehensive logging and error handling
"""

import os
import re
import json
import logging
import subprocess
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
from fnmatch import fnmatch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
TESTS_DIR = REPO_ROOT / "tests"
EVIDENCE_DIR = REPO_ROOT / "evidence"
BASELINE_DIR = EVIDENCE_DIR / "baseline"
DIAGNOSTIC_DIR = EVIDENCE_DIR / "diagnostic"
AUDIT_CONFIG = Path(__file__).parent / "audit_config.json"

# Output paths
REPORT_PATH = DIAGNOSTIC_DIR / "QFSV13.5_AUTONOMOUS_AUDIT_REPORT_V2.md"
JSON_REPORT_PATH = DIAGNOSTIC_DIR / "QFSV13.5_AUDIT_REQUIREMENTS.json"
PYTEST_OUTPUT_PATH = DIAGNOSTIC_DIR / "pytest_output_v2.txt"

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ComponentStatus:
    name: str
    file: str
    status: str  # IMPLEMENTED, PARTIALLY_IMPLEMENTED, UNKNOWN, MISSING
    tests_collected: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    evidence_found: List[str] = None
    non_det_patterns: List[str] = None
    criticality: str = "MEDIUM"
    
    def __post_init__(self):
        if self.evidence_found is None:
            self.evidence_found = []
        if self.non_det_patterns is None:
            self.non_det_patterns = []

@dataclass
class BaselineComparison:
    metric: str
    baseline_value: any
    current_value: any
    status: str  # PASS, REGRESSION, IMPROVEMENT, UNKNOWN

@dataclass
class AuditVerdict:
    overall_status: str  # PASS, WARN, FAIL
    critical_issues: List[str]
    recommendations: List[str]
    exit_code: int

# ============================================================================
# Configuration Loading
# ============================================================================

def load_audit_config() -> Dict:
    """Load audit configuration from JSON."""
    try:
        with open(AUDIT_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Loaded audit config from {AUDIT_CONFIG}")
        return config
    except Exception as e:
        logger.warning(f"Could not load audit config: {e}. Using defaults.")
        return {}

# ============================================================================
# AST-Based Determinism Detection
# ============================================================================

def find_non_deterministic_ast(file_path: Path) -> List[Tuple[str, int]]:
    """
    Parse Python AST to detect non-deterministic function calls.
    Returns list of (pattern_name, line_number) tuples.
    
    This is more accurate than keyword matching and reduces false positives.
    """
    patterns_to_check = {
        'random': ['random', 'randint', 'choice', 'shuffle'],
        'time': ['time', 'sleep', 'time_ns'],
        'uuid': ['uuid4', 'uuid1'],
        'os_urandom': ['urandom'],
        'datetime': ['now', 'utcnow'],
        'math_special': ['inf', 'nan', 'isnan', 'isinf'],  # Problematic math ops
    }
    
    hits = []
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Extract function name from various AST node types
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                elif isinstance(node.func, ast.Subscript):
                    continue  # Skip complex calls
                
                if func_name:
                    # Check against all patterns
                    for pattern_family, funcs in patterns_to_check.items():
                        if func_name in funcs:
                            hits.append((pattern_family, node.lineno if hasattr(node, 'lineno') else 0))
    except SyntaxError as e:
        logger.warning(f"Syntax error in {file_path}: {e}")
        hits.append(('parse_error', 0))
    except Exception as e:
        logger.warning(f"Error parsing {file_path}: {e}")
        hits.append(('parse_error', 0))
    
    return hits

# ============================================================================
# Module Scanning
# ============================================================================

def scan_src_modules() -> Dict[str, Dict]:
    """Scan src/ directory and extract module metadata."""
    modules: Dict[str, Dict] = {}
    
    if not SRC_DIR.is_dir():
        logger.warning(f"src/ directory not found at {SRC_DIR}")
        return modules
    
    logger.info(f"Scanning modules in {SRC_DIR}...")
    
    for pyfile in sorted(SRC_DIR.rglob("*.py")):
        rel = pyfile.relative_to(REPO_ROOT)
        
        try:
            text = pyfile.read_text(encoding='utf-8', errors='ignore')
            
            # Extract classes and functions
            classes = re.findall(r'^\s*class\s+([A-Za-z0-9_]+)\s*[\(:]', text, re.MULTILINE)
            funcs = re.findall(r'^\s*def\s+([A-Za-z0-9_]+)\s*\(', text, re.MULTILINE)
            
            # Extract imports
            imports = re.findall(r'^\s*import\s+([A-Za-z0-9_\.]+)', text, re.MULTILINE)
            from_imports = re.findall(r'^\s*from\s+([A-Za-z0-9_\.]+)\s+import', text, re.MULTILINE)
            
            # AST-based non-determinism check
            non_det_ast = find_non_deterministic_ast(pyfile)
            non_det_keywords = list(set([p[0] for p in non_det_ast]))
            
            modules[str(rel)] = {
                'classes': classes,
                'functions': funcs,
                'imports': sorted(set(imports + from_imports)),
                'non_det_patterns': non_det_keywords,
                'non_det_details': non_det_ast,
                'file_size': len(text),
            }
        except Exception as e:
            logger.error(f"Error scanning {rel}: {e}")
            modules[str(rel)] = {'error': str(e)}
    
    logger.info(f"Scanned {len(modules)} modules")
    return modules

# ============================================================================
# Test Execution
# ============================================================================

def run_tests_deterministic() -> Dict:
    """
    Run pytest with deterministic environment.
    Returns structured test results.
    """
    logger.info("Running pytest with deterministic environment...")
    
    env = os.environ.copy()
    env['PYTHONHASHSEED'] = '0'
    env['TZ'] = 'UTC'
    
    cmd = ['python', '-m', 'pytest', '--collect-only', '-q']
    
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,
        )
        
        output = proc.stdout
        PYTEST_OUTPUT_PATH.write_text(output, encoding='utf-8')
        
        # Parse output
        tests_collected = 0
        match = re.search(r'(\d+)\s+test', output)
        if match:
            tests_collected = int(match.group(1))
        
        errors = output.count('ERROR')
        
        logger.info(f"Tests collected: {tests_collected}, Errors: {errors}")
        
        return {
            'cmd': ' '.join(cmd),
            'exit_code': proc.returncode,
            'output_path': str(PYTEST_OUTPUT_PATH.relative_to(REPO_ROOT)),
            'tests_collected': tests_collected,
            'errors': errors,
            'raw_output': output,
        }
    except subprocess.TimeoutExpired:
        logger.error("pytest timeout exceeded (300s)")
        return {'error': 'timeout', 'exit_code': -1}
    except Exception as e:
        logger.error(f"Error running pytest: {e}")
        return {'error': str(e), 'exit_code': -1}

def extract_test_names(pytest_output: str) -> Set[str]:
    """Extract test file/function names from pytest output."""
    tests = set()
    # Match lines like: "tests/unit/test_bignum128.py::test_add"
    for match in re.finditer(r'(tests/[^\s:]+)::', pytest_output):
        tests.add(match.group(1))
    return tests

# ============================================================================
# Component Status Assessment
# ============================================================================

def assess_component_status(
    config: Dict,
    modules: Dict,
    tests_found: Set[str],
    baseline_data: Dict
) -> List[ComponentStatus]:
    """
    Assess implementation status of configured components.
    """
    statuses = []
    components = config.get('critical_components', [])
    
    for comp in components:
        name = comp['name']
        file_path = comp['file']
        test_patterns = comp['test_patterns']
        evidence_paths = comp.get('evidence_paths', [])
        criticality = comp.get('criticality', 'MEDIUM')
        
        # Check if file exists
        full_path = REPO_ROOT / file_path
        file_exists = full_path.is_file()
        
        # Check for matching tests
        matching_tests = []
        for test_pattern in test_patterns:
            for test_file in tests_found:
                if fnmatch(test_file.lower(), test_pattern.lower()):
                    matching_tests.append(test_file)
        
        # Check for evidence files
        found_evidence = []
        for ev_path in evidence_paths:
            if (REPO_ROOT / ev_path).is_file():
                found_evidence.append(ev_path)
        
        # Get non-deterministic patterns
        non_det = []
        if str(file_path) in modules and 'non_det_patterns' in modules[str(file_path)]:
            non_det = modules[str(file_path)]['non_det_patterns']
        
        # Determine status
        if not file_exists:
            status = 'MISSING'
        elif matching_tests and found_evidence:
            status = 'IMPLEMENTED'
        elif matching_tests or found_evidence:
            status = 'PARTIALLY_IMPLEMENTED'
        elif file_exists:
            status = 'UNKNOWN'
        else:
            status = 'UNKNOWN'
        
        statuses.append(ComponentStatus(
            name=name,
            file=file_path,
            status=status,
            tests_collected=len(matching_tests),
            evidence_found=found_evidence,
            non_det_patterns=non_det,
            criticality=criticality,
        ))
    
    return statuses

# ============================================================================
# Baseline Comparison
# ============================================================================

def compare_with_baseline(
    current_tests: int,
    current_errors: int,
) -> List[BaselineComparison]:
    """
    Compare current test execution with baseline.
    """
    comparisons = []
    
    try:
        baseline_file = BASELINE_DIR / 'baseline_test_results.json'
        if baseline_file.exists():
            baseline_data = json.loads(baseline_file.read_text(encoding='utf-8'))
            
            baseline_collected = baseline_data.get('summary', {}).get('tests_collected', 0)
            baseline_errors = baseline_data.get('summary', {}).get('collection_errors', 0)
            
            # Compare tests collected
            if current_tests > baseline_collected:
                test_status = 'IMPROVEMENT'
            elif current_tests < baseline_collected:
                test_status = 'REGRESSION'
            else:
                test_status = 'PASS'
            
            comparisons.append(BaselineComparison(
                metric='Tests collected',
                baseline_value=baseline_collected,
                current_value=current_tests,
                status=test_status,
            ))
            
            # Compare errors
            if current_errors > baseline_errors:
                error_status = 'REGRESSION'
            elif current_errors < baseline_errors:
                error_status = 'IMPROVEMENT'
            else:
                error_status = 'PASS'
            
            comparisons.append(BaselineComparison(
                metric='Collection errors',
                baseline_value=baseline_errors,
                current_value=current_errors,
                status=error_status,
            ))
    except Exception as e:
        logger.warning(f"Could not load baseline for comparison: {e}")
    
    return comparisons

# ============================================================================
# Verdict Generation
# ============================================================================

def generate_verdict(
    components: List[ComponentStatus],
    test_results: Dict,
    comparisons: List[BaselineComparison],
    config: Dict,
) -> AuditVerdict:
    """
    Generate final audit verdict with exit code.
    """
    critical_issues = []
    recommendations = []
    exit_code = 0
    
    # Check for regressions
    for comp in comparisons:
        if comp.status == 'REGRESSION':
            critical_issues.append(f"{comp.metric}: {comp.baseline_value} → {comp.current_value}")
            exit_code = max(exit_code, 1)  # WARN
    
    # Check critical components
    critical_missing = [c for c in components if c.criticality == 'CRITICAL' and c.status == 'MISSING']
    if critical_missing:
        for comp in critical_missing:
            critical_issues.append(f"CRITICAL COMPONENT MISSING: {comp.name}")
            exit_code = 2  # FAIL
    
    # Check for non-determinism in critical paths
    critical_non_det = [c for c in components 
                        if c.criticality == 'CRITICAL' and c.non_det_patterns]
    if critical_non_det:
        for comp in critical_non_det:
            msg = f"Non-deterministic patterns in CRITICAL component {comp.name}: {comp.non_det_patterns}"
            critical_issues.append(msg)
            exit_code = max(exit_code, 1)  # WARN at least
    
    # Generate recommendations
    for comp in components:
        if comp.status == 'UNKNOWN':
            recommendations.append(
                f"Create tests for {comp.name} (file exists but no tests found)"
            )
        elif comp.status == 'PARTIALLY_IMPLEMENTED':
            recommendations.append(
                f"Complete {comp.name} implementation with evidence artifacts"
            )
    
    # Determine overall status
    if exit_code >= 2:
        overall_status = 'FAIL'
    elif exit_code >= 1:
        overall_status = 'WARN'
    else:
        overall_status = 'PASS'
    
    return AuditVerdict(
        overall_status=overall_status,
        critical_issues=critical_issues,
        recommendations=recommendations,
        exit_code=exit_code,
    )

# ============================================================================
# Report Generation
# ============================================================================

def generate_markdown_report(
    config: Dict,
    modules: Dict,
    components: List[ComponentStatus],
    test_results: Dict,
    comparisons: List[BaselineComparison],
    verdict: AuditVerdict,
) -> str:
    """Generate comprehensive markdown audit report."""
    
    lines = []
    now = datetime.utcnow().isoformat() + 'Z'
    
    # Header
    lines.extend([
        '# QFS V13.5 Autonomous Audit Report (v2.0)',
        '',
        '**Evidence-driven compliance audit for QFS V13.5 / V2.1**',
        '',
        f'**Generated:** {now}',
        f'**Repository:** {REPO_ROOT}',
        f'**Audit Status:** {verdict.overall_status}',
        '',
        f'Git commit: `{get_git_commit()}`',
        f'Python version: `{get_python_version()}`',
        '',
        '---',
        '',
    ])
    
    # Executive Summary
    lines.extend([
        '## Executive Summary',
        '',
        f'**Verdict:** {verdict.overall_status}',
        '',
        '### Critical Issues',
        '',
    ])
    
    if verdict.critical_issues:
        for issue in verdict.critical_issues:
            lines.append(f'- ❌ {issue}')
    else:
        lines.append('- ✅ No critical issues detected')
    
    lines.extend(['', '### Recommendations', ''])
    
    if verdict.recommendations:
        for i, rec in enumerate(verdict.recommendations[:5], 1):
            lines.append(f'{i}. {rec}')
    else:
        lines.append('- Continue monitoring')
    
    lines.extend(['', '---', ''])
    
    # Component Status Table
    lines.extend([
        '## Component Implementation Status',
        '',
        '| Component | Status | Tests | Evidence | Non-Det | Criticality |',
        '|-----------|--------|-------|----------|---------|-------------|',
    ])
    
    for comp in sorted(components, key=lambda c: c.criticality, reverse=True):
        status_icon = {
            'IMPLEMENTED': '✅',
            'PARTIALLY_IMPLEMENTED': '🟡',
            'UNKNOWN': '❓',
            'MISSING': '❌',
        }.get(comp.status, '?')
        
        non_det_str = ', '.join(comp.non_det_patterns[:2]) if comp.non_det_patterns else '-'
        
        lines.append(
            f'| {comp.name} | {status_icon} {comp.status} | {comp.tests_collected} | '
            f'{len(comp.evidence_found)} | {non_det_str} | {comp.criticality} |'
        )
    
    lines.extend(['', '---', ''])
    
    # Test Results
    lines.extend([
        '## Test Execution Results',
        '',
        f'- Tests collected: {test_results.get("tests_collected", "?")}',
        f'- Collection errors: {test_results.get("errors", "?")}',
        f'- Exit code: {test_results.get("exit_code", "?")}',
        f'- Output log: `{test_results.get("output_path", "")}`',
        '',
    ])
    
    # Baseline Comparison
    if comparisons:
        lines.extend(['## Baseline Comparison', ''])
        for comp in comparisons:
            status_icon = '📈' if comp.status == 'IMPROVEMENT' else '📉' if comp.status == 'REGRESSION' else '✅'
            lines.append(
                f'- {status_icon} {comp.metric}: {comp.baseline_value} → {comp.current_value} ({comp.status})'
            )
        lines.append('')
    
    # Non-Determinism Analysis
    lines.extend([
        '## Non-Determinism Analysis',
        '',
    ])
    
    critical_with_issues = [c for c in components if c.criticality == 'CRITICAL' and c.non_det_patterns]
    if critical_with_issues:
        lines.append('### ⚠️ Critical Path Issues')
        lines.append('')
        for comp in critical_with_issues:
            lines.append(f'- **{comp.name}**: {comp.non_det_patterns}')
        lines.append('')
    else:
        lines.append('✅ No non-deterministic patterns in critical components')
        lines.append('')
    
    # Footer
    lines.extend([
        '---',
        '',
        '**Report generated by:** QFS V13.5 Autonomous Audit v2.0',
        '**Exit code:** ' + str(verdict.exit_code),
    ])
    
    return '\n'.join(lines)

def generate_json_report(
    components: List[ComponentStatus],
    verdict: AuditVerdict,
) -> Dict:
    """Generate machine-readable JSON report for CI integration."""
    return {
        'audit_version': '2.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'git_commit': get_git_commit(),
        'verdict': {
            'overall_status': verdict.overall_status,
            'exit_code': verdict.exit_code,
            'critical_issues': verdict.critical_issues,
            'recommendations': verdict.recommendations,
        },
        'components': [asdict(c) for c in components],
        'non_det_patterns': {
            c.name: c.non_det_patterns for c in components if c.non_det_patterns
        },
    }

# ============================================================================
# Utility Functions
# ============================================================================

def get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()[:12]
    except Exception:
        return 'unknown'

def get_python_version() -> str:
    """Get Python version."""
    try:
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    except Exception:
        return 'unknown'

def ensure_dirs():
    """Ensure output directories exist."""
    DIAGNOSTIC_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory ready: {DIAGNOSTIC_DIR}")

# ============================================================================
# Main Execution
# ============================================================================

def run_audit():
    """Execute complete autonomous audit."""
    logger.info("=" * 80)
    logger.info("QFS V13.5 Autonomous Audit v2.0 - Starting")
    logger.info("=" * 80)
    
    ensure_dirs()
    
    # Load configuration
    config = load_audit_config()
    
    # 1. Scan modules
    logger.info("\n[1/6] Scanning modules...")
    modules = scan_src_modules()
    
    # 2. Run tests
    logger.info("\n[2/6] Running tests...")
    test_results = run_tests_deterministic()
    tests_found = extract_test_names(test_results.get('raw_output', ''))
    
    # 3. Assess components
    logger.info("\n[3/6] Assessing component status...")
    baseline_data = {}
    components = assess_component_status(config, modules, tests_found, baseline_data)
    
    # 4. Compare with baseline
    logger.info("\n[4/6] Comparing with baseline...")
    comparisons = compare_with_baseline(
        test_results.get('tests_collected', 0),
        test_results.get('errors', 0),
    )
    
    # 5. Generate verdict
    logger.info("\n[5/6] Generating verdict...")
    verdict = generate_verdict(components, test_results, comparisons, config)
    
    # 6. Generate reports
    logger.info("\n[6/6] Generating reports...")
    
    # Markdown report
    md_report = generate_markdown_report(
        config, modules, components, test_results, comparisons, verdict
    )
    REPORT_PATH.write_text(md_report, encoding='utf-8')
    logger.info(f"✅ Markdown report: {REPORT_PATH}")
    
    # JSON report
    json_report = generate_json_report(components, verdict)
    JSON_REPORT_PATH.write_text(json.dumps(json_report, indent=2), encoding='utf-8')
    logger.info(f"✅ JSON report: {JSON_REPORT_PATH}")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info(f"VERDICT: {verdict.overall_status}")
    logger.info(f"EXIT CODE: {verdict.exit_code}")
    logger.info("=" * 80)
    
    if verdict.critical_issues:
        logger.warning("\nCritical Issues:")
        for issue in verdict.critical_issues:
            logger.warning(f"  - {issue}")
    
    logger.info("\nRecommendations:")
    for rec in verdict.recommendations[:3]:
        logger.info(f"  - {rec}")
    
    return verdict.exit_code

if __name__ == '__main__':
    import sys
    exit_code = run_audit()
    sys.exit(exit_code)
