"""
Zero-Mock Compliance Scanner for QFS V13
Verifies that no mock usage, fixtures, or fake data exist in production paths.
Enforces the mandatory Zero-Simulation invariant for live feeds.
"""
import re
import json
import ast
from pathlib import Path
from typing import List, Dict, Any, Set
if os.path.exists('core') and os.path.isdir('core'):
    PREFIX = ''
else:
    PREFIX = 'v13/'
SCAN_ROOTS = [f'{PREFIX}ATLAS', f'{PREFIX}core', f'{PREFIX}policy']
EXCLUDE_DIRS = [f'{PREFIX}ATLAS/node_modules', f'{PREFIX}ATLAS/.next', f'{PREFIX}ATLAS/dist', f'{PREFIX}ATLAS/coverage', '__pycache__', '.git', f'{PREFIX}tests', f'{PREFIX}legacy_root']
FORBIDDEN_KEYWORDS = ['mock', 'fixture', 'fake', 'test_array', 'deterministic_mock', 'simulated_event', 'sample_events']
EXPLAIN_THIS_ROUTES = [f'{PREFIX}ATLAS/src/api/routes/explain.py']
ALLOWED_EXPLAIN_SOURCES = ['QFSReplaySource', 'ValueNodeReplayEngine.replay_events', 'ValueNodeReplayEngine.explain_content_ranking']
OUTPUT_FILE = 'v13/evidence/zero_mock_scan_status.json'

class ZeroMockScanner:

    def __init__(self):
        self.violations: List[Dict[str, Any]] = []
        self.files_scanned = 0
        self.stats = {'slices': {'Humor': {'mock_found': False, 'files': []}, 'ValueNode': {'mock_found': False, 'files': []}, 'Storage': {'mock_found': False, 'files': []}, 'Artistic': {'mock_found': False, 'files': []}, 'General': {'mock_found': False, 'files': []}}}

    def _get_slice_name(self, file_path: str) -> str:
        lower_path = file_path.lower()
        if 'humor' in lower_path:
            return 'Humor'
        if 'value_node' in lower_path or 'valuenode' in lower_path or 'explain' in lower_path:
            return 'ValueNode'
        if 'storage' in lower_path or 'ipfs' in lower_path:
            return 'Storage'
        if 'artistic' in lower_path or 'aes' in lower_path:
            return 'Artistic'
        return 'General'

    def scan_file_contents(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                line_num = i + 1
                for keyword in sorted(FORBIDDEN_KEYWORDS):
                    if re.search(f'\\b{keyword}\\b', line, re.IGNORECASE):
                        violation = {'file': file_path, 'line': line_num, 'keyword': keyword, 'content': line.strip()}
                        self.violations.append(violation)
                        slice_name = self._get_slice_name(file_path)
                        self.stats['slices'][slice_name]['mock_found'] = True
                        self.stats['slices'][slice_name]['files'].append(f'{file_path}:{line_num}')
        except Exception as e:
            print(f'Error checking file {file_path}: {e}')

    def scan_directories(self):
        root_dir = os.getcwd()
        for scan_path in sorted(SCAN_ROOTS):
            abs_scan_path = Path(root_dir) / scan_path
            if not abs_scan_path.exists():
                print(f'Warning: Path not found {scan_path}')
                continue
            for root, dirs, files in os.walk(abs_scan_path):
                dirs[:] = [d for d in dirs if not any((x in os.path.join(root, d).replace('\\', '/') for x in EXCLUDE_DIRS))]
                files = [f for f in files if f.endswith(('.py', '.ts', '.tsx', '.js'))]
                for file in sorted(files):
                    file_path = os.path.join(root, file).replace('\\', '/')
                    if any((x in file_path for x in EXCLUDE_DIRS)):
                        continue
                    if '/__tests__/' in file_path or '/tests/' in file_path:
                        continue
                    if file.endswith(('.test.ts', '.spec.ts', '.test.py', '.test.js', '.spec.js', '.test.tsx')):
                        continue
                    self.files_scanned += 1
                    self.scan_file_contents(file_path)

    def verify_explain_this_sources(self):
        """
        Special check for explain.py to ensure it sources from ReplayEngine.
        This is a heuristic check looking for hardcoded lists vs Allowed calls.
        """
        for route_file in sorted(EXPLAIN_THIS_ROUTES):
            if not os.path.exists(route_file):
                continue
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if route_file.endswith('.py'):
                try:
                    tree = ast.parse(content)
                    if re.search('events\\s*=\\s*\\[.*\\{.*\\}.*\\]', content, re.DOTALL):
                        self.violations.append({'file': route_file, 'line': 0, 'keyword': 'INLINE_MOCK_ARRAY', 'content': 'Found inline array assignment potentially containing mock events.'})
                    found_valid_source = False
                    for valid in sorted(ALLOWED_EXPLAIN_SOURCES):
                        if valid in content:
                            found_valid_source = True
                    slice_name = self._get_slice_name(route_file)
                    self.stats['slices'][slice_name]['live_source_verified'] = found_valid_source
                except Exception as e:
                    print(f'Error parsing {route_file}: {e}')

    def generate_report(self):
        success = len(self.violations) == 0
        slice_reports = []
        for name, data in self.stats['slices'].items():
            is_compliant = not data['mock_found']
            mock_usage = data['mock_found']
            report_item = {'name': name, 'mock_usage_found': mock_usage, 'files': data['files'], 'live_source_verified': data.get('live_source_verified', None), 'zero_sim_compliant': is_compliant}
            slice_reports.append(report_item)
        report = {'timestamp': datetime.utcnow().isoformat(), 'scan_result': 'PASS' if success else 'FAIL', 'files_scanned': self.files_scanned, 'violations': self.violations, 'slices': slice_reports, 'notes': 'Automated Zero-Mock Verification Scan.'}
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(report, f, indent=2)
        return (success, report)
if __name__ == '__main__':
    print('>> Starting Zero-Mock Verification Scan...')
    scanner = ZeroMockScanner()
    scanner.scan_directories()
    scanner.verify_explain_this_sources()
    success, report = scanner.generate_report()
    if success:
        print('[OK] ZERO-MOCK COMPLIANCE VERIFIED.')
        print(f'Scanned {scanner.files_scanned} files across production paths.')
        raise ZeroSimAbort(0)
    else:
        print(f'[FAIL] MOCK USAGE DETECTED: {len(scanner.violations)} violations.')
        for v in scanner.violations[:5]:
            print(f"  - {v['file']}:{v['line']} -> found '{v['keyword']}'")
        print(f'See full report at {OUTPUT_FILE}')
        raise ZeroSimAbort(1)
