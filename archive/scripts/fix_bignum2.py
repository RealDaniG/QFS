# Read the file
with open('v13/libs/BigNum128.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the CertifiedMath imports
content = content.replace(
    '            cm = CertifiedMath()', 
    '            from .CertifiedMath import CertifiedMath\n            cm = CertifiedMath()'
)

content = content.replace(
    '        cm = CertifiedMath()', 
    '        from .CertifiedMath import CertifiedMath\n        cm = CertifiedMath()'
)

# Write the fixed content back
with open('v13/libs/BigNum128.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed file successfully!")