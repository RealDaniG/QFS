"""
Script to fix all invalid libs.economics imports
"""

import os
import re

files_to_fix = [
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\signals\humor_v2.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\signals\humor_zerosim.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\signals\humor.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\signals\base.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\signals\artistic.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\p2p\secure_message_v2.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\models\wallet.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\p2p\connection_manager.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\models\quantum.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\p2p\bandwidth_economics.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\models\transaction.py",
    r"d:\AI AGENT CODERV1\QUANTUM CURRENCY\QFS\V13\v13\atlas\src\core\economic_views.py",
]

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"SKIP: {filepath} (not found)")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace the import
    new_content = content.replace("from libs.economics", "from v13.libs.economics")

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"FIXED: {filepath}")
    else:
        print(f"NO CHANGE: {filepath}")

print("\n✅ All imports fixed!")
