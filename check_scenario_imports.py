import sys
import os

sys.path.append(os.getcwd())

print("Checking scenario imports...")

try:
    from v13.libs.CertifiedMath import CertifiedMath

    print("CertifiedMath: OK")
except ImportError as e:
    print(f"CertifiedMath: FAIL {e}")

try:
    from v13.atlas.spaces.spaces_manager import SpacesManager

    print("SpacesManager: OK")
except ImportError as e:
    print(f"SpacesManager: FAIL {e}")

try:
    from v13.atlas.spaces.wall_posts import WallPostManager

    print("WallPostManager: OK")
except ImportError as e:
    print(f"WallPostManager: FAIL {e}")

try:
    from v13.atlas.chat.chat_session import ChatSessionManager

    print("ChatSessionManager: OK")
except ImportError as e:
    print(f"ChatSessionManager: FAIL {e}")

try:
    from v13.atlas.social.feed_generator import FeedGenerator

    print("FeedGenerator: OK")
except ImportError as e:
    print(f"FeedGenerator: FAIL {e}")
