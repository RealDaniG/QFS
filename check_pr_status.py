import json
import subprocess

# Get PR status
result = subprocess.run(['gh', 'pr', 'view', '10', '--json', 'statusCheckRollup'], 
                       capture_output=True, text=True)
data = json.loads(result.stdout)

checks = data['statusCheckRollup']
print(f"Total checks: {len(checks)}")
print()

passing = [c for c in checks if c.get('conclusion') == 'SUCCESS']
failing = [c for c in checks if c.get('conclusion') == 'FAILURE']
skipped = [c for c in checks if c.get('conclusion') == 'SKIPPED']
cancelled = [c for c in checks if c.get('conclusion') == 'CANCELLED']
pending = [c for c in checks if c.get('status') != 'COMPLETED']

print(f"✅ Passing: {len(passing)}")
print(f"❌ Failing: {len(failing)}")
print(f"⏭️  Skipped: {len(skipped)}")
print(f"⚪ Cancelled: {len(cancelled)}")
print(f"⏳ Pending: {len(pending)}")
print()

if failing:
    print("FAILING CHECKS:")
    for check in failing:
        print(f"  - {check['name']}")
print()

if skipped:
    print("SKIPPED CHECKS:")
    for check in skipped[:5]:  # Show first 5
        print(f"  - {check['name']}")
