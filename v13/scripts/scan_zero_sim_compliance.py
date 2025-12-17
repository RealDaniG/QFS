<<<<<<< HEAD
# import sys removed (unused)
import os
=======
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
import re
import json
import ast
TIMESTAMP_REGEX = re.compile('(datetime\\.now|time\\.time|Date\\.now|new Date)', re.IGNORECASE)
RANDOM_REGEX = re.compile('(random\\.|uuid\\.uuid4|os\\.urandom|Math\\.random|crypto\\.random)', re.IGNORECASE)
FLOAT_REGEX = re.compile('(float\\(|/ \\d|\\d \\/|%)')
PRISMA_WRITE_REGEX = re.compile('prisma\\..*\\.(create|update|delete|upsert)')
IO_REGEX = re.compile('(requests\\.get|urllib|httpx|aiohttp|open\\()')
EXCLUDED_DIRS = ['__pycache__', 'node_modules', '.git', '.idea', '.vscode', 'dist', 'build', 'coverage', 'venv', 'env', '.gemini', 'artifacts', 'legacy_root', 'archive', 'ATLAS', 'docs']
NO_SCAN_FILES = ['scan_zero_sim_compliance.py', 'run_zero_sim_suite.py', 'simple_violations.py', 'golden_fail.py']
VIOLATIONS = []

def scan_python_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
    except Exception as e:
        print(f'Skipping {filepath}: {e}')
        return
    for i, line in enumerate(lines):
        ln = i + 1
<<<<<<< HEAD
        if "QODO:JUSTIFIED" in line:
            continue

        # Random
=======
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        if RANDOM_REGEX.search(line):
            if not line.strip().startswith('#'):
                add_violation(filepath, ln, 'RANDOM_USAGE', 'CRITICAL', line.strip())
        if TIMESTAMP_REGEX.search(line):
            if not line.strip().startswith('#'):
                add_violation(filepath, ln, 'WALL_CLOCK_TIME', 'HIGH', line.strip())
        if IO_REGEX.search(line):
<<<<<<< HEAD
            # Enforce on core, policy, guard, aegis, governance
            if any(
                x in filepath
                for x in [
                    "policy",
                    "core",
                    "guard",
                    "services/aegis",
                    "services/governance",
                ]
            ):
                if not line.strip().startswith("#"):
                    add_violation(filepath, ln, "EXTERNAL_IO", "CRITICAL", line.strip())

    # AST Checks for specific patterns (e.g. imports)
=======
            if 'policy' in filepath or 'core' in filepath or 'guard' in filepath:
                if not line.strip().startswith('#'):
                    add_violation(filepath, ln, 'EXTERNAL_IO', 'CRITICAL', line.strip())
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                module_name = getattr(node, 'module', '')
                names = [n.name for n in node.names]
                check_imports = ['random', 'time', 'secrets', 'uuid']
                for imp in check_imports:
                    if imp in names or (module_name and imp == module_name):
                        add_violation(filepath, node.lineno, f'FORBIDDEN_IMPORT_{imp.upper()}', 'CRITICAL', f'import {imp}')
    except SyntaxError:
        pass

def scan_ts_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return
    for i, line in enumerate(lines):
        ln = i + 1
        line_clean = line.strip()
        if line_clean.startswith('//') or line_clean.startswith('/*'):
            continue
<<<<<<< HEAD

        if "QODO:JUSTIFIED" in line:
            continue

        # Random
        if "Math.random" in line or "crypto.random" in line:
            add_violation(filepath, ln, "RANDOM_USAGE", "CRITICAL", line_clean)

        # Time
        if "Date.now" in line or "new Date" in line:
            # Heuristic: Critical if in hooks/lib, High/Low if in components (display)
            severity = "CRITICAL" if "src/lib" in filepath else "MEDIUM"
            add_violation(filepath, ln, "WALL_CLOCK_TIME", severity, line_clean)

        # Prisma Writes
=======
        if 'Math.random' in line or 'crypto.random' in line:
            add_violation(filepath, ln, 'RANDOM_USAGE', 'CRITICAL', line_clean)
        if 'Date.now' in line or 'new Date' in line:
            severity = 'CRITICAL' if 'src/lib' in filepath else 'MEDIUM'
            add_violation(filepath, ln, 'WALL_CLOCK_TIME', severity, line_clean)
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        if PRISMA_WRITE_REGEX.search(line):
            if 'balance' in line or 'amount' in line or 'reward' in line:
                add_violation(filepath, ln, 'PRISMA_ECONOMIC_WRITE', 'CRITICAL_AUTHORITY_VIOLATION', line_clean)
            else:
                add_violation(filepath, ln, 'PRISMA_WRITE_CHECK', 'MEDIUM', line_clean)

def scan_deps(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'numpy' in content or 'pandas' in content:
        pass
    if 'faker' in content:
        pass

def scan_test_file(filepath):
    scan_python_file(filepath)
    pass

def add_violation(filepath, line, v_type, severity, snippet):
    VIOLATIONS.append({'file': filepath.replace('\\', '/'), 'line': line, 'violation_type': v_type, 'severity': severity, 'code_snippet': snippet[0:100], 'suggested_fix': suggest_fix(v_type)})

def suggest_fix(v_type):
    if 'RANDOM' in v_type:
        return 'Use deterministic PRNG or hash-based ID.'
    if 'TIME' in v_type:
        return 'Use passed-in timestamp or ledger block time.'
    if 'IO' in v_type:
        return 'Remove I/O. Pass data as arguments.'
    if 'PRISMA' in v_type:
        return 'Remove DB write. Send intent to QFS.'
    return 'Check Zero-Sim contract.'

def walk_and_scan(root_dir):
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file in NO_SCAN_FILES:
                continue
            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext == '.py':
                if 'tests' in filepath or 'test_' in file:
                    scan_test_file(filepath)
                else:
                    scan_python_file(filepath)
            elif ext in ['.ts', '.tsx', '.js', '.jsx']:
                scan_ts_file(filepath)
            elif file in ['requirements.txt', 'package.json']:
                scan_deps(filepath)

def main():
    start_time = datetime.now()
    print('🚀 Starting V13.8 Zero-Sim Compliance Scan...')
    scan_root = '.'
    if os.path.exists('v13'):
        scan_root = 'v13'
    walk_and_scan(scan_root)
<<<<<<< HEAD

    end_time = datetime.now()
    print(f"Scan duration: {end_time - start_time}")

    # Generate Report
    report_path = os.path.join(
        scan_root, "evidence/zero_sim/compliance_scan_report.json"
    )
=======
    report_path = os.path.join(scan_root, 'evidence/zero_sim/compliance_scan_report.json')
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    summary = {'timestamp': datetime.utcnow().isoformat(), 'total_violations': len(VIOLATIONS), 'violations': VIOLATIONS}
    with open(report_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'✅ Scan Complete. Found {len(VIOLATIONS)} potential violations.')
    print(f'Report saved to: {report_path}')
    criticals = [v for v in VIOLATIONS if 'CRITICAL' in v['severity']]
    if criticals:
        print(f'⚠️  Found {len(criticals)} CRITICAL violations.')
if __name__ == '__main__':
    main()