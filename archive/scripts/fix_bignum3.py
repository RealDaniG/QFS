import re

# Read the file
with open('v13/libs/BigNum128.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all lines with "cm = CertifiedMath()" and add the import before them
# But only if the import is not already present in the previous few lines
lines = content.split('\n')
new_lines = []

for i, line in enumerate(lines):
    # Check if this line contains the CertifiedMath() call
    if 'cm = CertifiedMath()' in line:
        # Check if the import is already present in the previous 3 lines
        import_already_present = False
        for j in range(max(0, i-3), i):
            if 'from .CertifiedMath import CertifiedMath' in lines[j]:
                import_already_present = True
                break
        
        # If import is not already present, add it
        if not import_already_present:
            # Add the import with the same indentation as the current line
            indent = len(line) - len(line.lstrip())
            import_line = ' ' * indent + 'from .CertifiedMath import CertifiedMath'
            new_lines.append(import_line)
    
    new_lines.append(line)

# Join the lines back together
fixed_content = '\n'.join(new_lines)

# Write the fixed content back
with open('v13/libs/BigNum128.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed file successfully!")