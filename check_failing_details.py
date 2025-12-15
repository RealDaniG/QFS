import json
import subprocess

# Get PR status
result = subprocess.run(['gh', 'pr', 'view', '10', '--json', 'statusCheckRollup'], 
                       capture_output=True, text=True)
data = json.loads(result.stdout)

checks = data['statusCheckRollup']

failing = [c for c in checks if c.get('conclusion') == 'FAILURE']

print("=" * 80)
print("FAILING CHECKS DETAILS:")
print("=" * 80)
for i, check in enumerate(failing, 1):
    print(f"\n{i}. {check['name']}")
    print(f"   Workflow: {check.get('workflowName', 'N/A')}")
    print(f"   Status: {check.get('status')}")
    print(f"   Conclusion: {check.get('conclusion')}")
    if 'detailsUrl' in check:
        print(f"   Details: {check['detailsUrl']}")
