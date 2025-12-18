import sys
import os

sys.path.append(os.getcwd())

print("Checking imports...")
try:
    from v13.atlas.chat.chat_models import ChatSessionState

    print("chat_models: OK")
except ImportError as e:
    print(f"chat_models: FAIL {e}")

try:
    from v13.atlas.chat.chat_session import ChatSessionManager

    print("chat_session: OK")
except ImportError as e:
    print(f"chat_session: FAIL {e}")

try:
    from v13.tests.test_secure_chat import test_chat_creation_determinism

    print("test_secure_chat: OK")
except ImportError as e:
    print(f"test_secure_chat: FAIL {e}")
except Exception as e:
    print(f"test_secure_chat: FAIL {e}")
