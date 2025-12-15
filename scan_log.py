
try:
    with open('job_58113044583.log', 'r', encoding='utf-16') as f:
        lines = f.readlines()
        
    print(f"Read {len(lines)} lines.")
    print("Errors Found:")
    print("="*40)
    for line in lines:
        if 'error' in line.lower() or 'fail' in line.lower() or 'exception' in line.lower():
             if 'downloading' not in line.lower():
                print(line.strip()[:200])
except Exception as e:
    print(f"utf-16 failed: {e}")
    try:
        with open('job_58113044583.log', 'r', encoding='utf-8', errors='ignore') as f:
             lines = f.readlines()
        print(f"Read {len(lines)} lines (utf-8 ignore).")
        for line in lines:
            if 'error' in line.lower() or 'fail' in line.lower() or 'exception' in line.lower():
                 if 'downloading' not in line.lower():
                    print(line.strip()[:200])
    except Exception as e2:
        print(f"utf-8 ignore failed: {e2}")
