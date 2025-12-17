with open('v13/libs/BigNum128.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    
    # Check if this line contains the CertifiedMath() call
    if 'cm = CertifiedMath()' in line and not 'from .CertifiedMath import CertifiedMath' in ''.join(lines[max(0, i-5):i]):
        # Insert the import statement before the CertifiedMath() call
        new_lines.insert(-1, '            from .CertifiedMath import CertifiedMath\n')
    
    i += 1

with open('v13/libs/BigNum128_fixed.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed file created as v13/libs/BigNum128_fixed.py")