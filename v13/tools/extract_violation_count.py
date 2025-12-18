"""
Extract violation count from AST checker output
"""
import re
import sys

def extract_violation_count(filepath):
    """Extract violation count from AST checker output file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search('\\[FAIL\\]\\s+(\\d+)\\s+violations found', content)
        if match:
            return int(match.group(1))
        if '[OK] Zero-Simulation compliance verified' in content:
            return 0
        return None
    except Exception as e:
        return None
if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'post_batch2_violations.txt'
    count = extract_violation_count(filepath)
    if count is not None:
        sys.exit(0)
    else:
        sys.exit(1)
