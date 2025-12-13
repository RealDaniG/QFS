#!/usr/bin/env python3
"""
Scan ALL Python files in src/ for Zero-Sim violations.
"""

import subprocess
from pathlib import Path

def get_all_python_files():
    """Get all Python files in src/ excluding tests."""
    src_path = Path("src")
    python_files = []
    
    for py_file in src_path.rglob("*.py"):
        # Skip test files, cache, venv
        if any(part in str(py_file) for part in ["test", "__pycache__", "venv", ".venv", "migration", "deprecated"]):
            continue
        python_files.append(str(py_file))
    
    return sorted(python_files)

def analyze_file(file_path):
    """Run AST checker on single file and parse output."""
    try:
        result = subprocess.run(
            ["python", "src/libs/AST_ZeroSimChecker.py", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout + result.stderr
        
        # Extract violation count
        violation_count = 0
        violation_types = set()
        
        for line in output.split('\n'):
            if 'violations found' in line:
                parts = line.split()
                if parts and parts[0].isdigit():
                    violation_count = int(parts[0])
            if '[' in line and ']' in line:
                start = line.find('[')
                end = line.find(']')
                if start != -1 and end != -1:
                    violation_types.add(line[start+1:end])
        
        return {
            "file": file_path,
            "violations": violation_count,
            "types": sorted(list(violation_types))
        }
    except Exception as e:
        return {
            "file": file_path,
            "violations": -1,
            "types": [],
            "error": str(e)
        }

def main():
    files = get_all_python_files()
    print(f"Scanning {len(files)} Python files in src/...\n")
    
    results = []
    for file_path in files:
        result = analyze_file(file_path)
        results.append(result)
        
        if result["violations"] > 0:
            print(f"❌ {file_path:60} | {result['violations']:4} violations")
            if result["types"]:
                print(f"   → {', '.join(result['types'][:5])}")
    
    # Summary
    clean = sum(1 for r in results if r["violations"] == 0)
    violated = sum(1 for r in results if r["violations"] > 0)
    
    print(f"\n{'='*80}")
    print(f"SUMMARY: {clean}/{len(files)} files clean, {violated} files with violations")
    print(f"{'='*80}\n")
    
    # List all violated files
    if violated > 0:
        print("[FILES WITH VIOLATIONS]\n")
        for result in sorted(results, key=lambda r: -r["violations"]):
            if result["violations"] > 0:
                print(f"{result['file']:65} | {result['violations']:4} violations")
    else:
        print("🎉 ALL FILES ARE ZERO-SIM CLEAN!")

if __name__ == "__main__":
    main()
