
try:
    with open('job_58113044583.log', 'r', encoding='utf-16') as f:
        content = f.read()
except:
    with open('job_58113044583.log', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

print("Searching for AST/Zero-Sim failures...")
if "Zero-Sim" in content:
    idx = content.find("Zero-Sim")
    print(content[idx:idx+500])
elif "AST" in content:
    idx = content.find("AST")
    print(content[idx:idx+500])
else:
    print("No specific AST/Zero-Sim markers found.")

print("\nLast 20 lines of log:")
print('\n'.join(content.splitlines()[-20:]))
