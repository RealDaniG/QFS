import json
import subprocess
from datetime import datetime

# Get PR status
result = subprocess.run(['gh', 'pr', 'view', '10', '--json', 'statusCheckRollup,commits'], 
                       capture_output=True, text=True)
data = json.loads(result.stdout)

checks = data['statusCheckRollup']
commits = data['commits']

print("=" * 80)
print("LATEST COMMIT INFO:")
print("=" * 80)
latest_commit = commits[-1] if commits else {}
print(f"SHA: {latest_commit.get('oid', 'N/A')[:8]}")
print(f"Message: {latest_commit.get('messageHeadline', 'N/A')}")
print(f"Author: {latest_commit.get('authors', [{}])[0].get('name', 'N/A')}")
print()

failing = [c for c in checks if c.get('conclusion') == 'FAILURE']

print("=" * 80)
print(f"FAILING CHECKS ({len(failing)}):")
print("=" * 80)
for i, check in enumerate(failing, 1):
    print(f"\n{i}. {check['name']}")
    print(f"   Commit: {check.get('checkSuite', {}).get('headSha', 'N/A')[:8]}")
    print(f"   Started: {check.get('startedAt', 'N/A')}")
    print(f"   Completed: {check.get('completedAt', 'N/A')}")
    
print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)
latest_sha = latest_commit.get('oid', '')[:8]
for check in failing:
    check_sha = check.get('checkSuite', {}).get('headSha', '')[:8]
    if check_sha != latest_sha:
        print(f"⚠️  '{check['name']}' is from OLD commit {check_sha}, not latest {latest_sha}")
        print(f"   → This check needs to be re-run!")
