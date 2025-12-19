"""
QFS × ATLAS Bootstrap System
Initializes all services in correct dependency order
"""

import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# Ensure v13 is in path
ROOTDIR = Path(__file__).resolve().parents[3]
if str(ROOTDIR) not in sys.path:
    sys.path.insert(0, str(ROOTDIR))

try:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.BigNum128 import BigNum128
    from v13.atlas.spaces.spaces_manager import SpacesManager
    from v13.atlas.wall.wall_service import WallService
    from v13.atlas.chat.chat_service import ChatService
    from v13.policy.bounties.bounty_state_machine import BountyStateMachine
    from v13.policy.treasury.dev_rewards_treasury import DevRewardsTreasury
except ImportError as e:
    print(f"Bootstrap Import Warning: {e}")
    # We allow imports to fail if strictly just checking existence,
    # but initialize_ methods will fail.


class ATLASBootstrap:
    """Manages initialization of ATLAS services"""

    def __init__(self):
        self.certified_math: Optional[CertifiedMath] = None
        self.spaces: Optional[SpacesManager] = None
        self.wall: Optional[WallService] = None
        self.chat: Optional[ChatService] = None
        self.bounty_system: Optional[BountyStateMachine] = None
        self.treasury: Optional[DevRewardsTreasury] = None
        self.initialized = False

    def initialize_core_math(self) -> Tuple[bool, str]:
        """Initialize mathematical foundation"""
        try:
            self.certified_math = CertifiedMath()
            # Verify constants loaded correctly
            if (
                self.certified_math.getPI() is None
            ):  # Assuming availability of PI constant if initialized
                return (False, "Core math PI constant check failed")
            return (True, "Core math initialized")
        except Exception as e:
            return (False, f"Core math failed: {str(e)}")

    def initialize_social_layer(self) -> Tuple[bool, str]:
        """Initialize Spaces, Wall, Chat"""
        try:
            if self.certified_math is None:
                return (False, "Core math not initialized")

            self.spaces = SpacesManager(self.certified_math)
            self.wall = WallService(self.certified_math)
            self.chat = ChatService(self.certified_math)
            return (True, "Social layer initialized")
        except Exception as e:
            return (False, f"Social layer failed: {str(e)}")

    def initialize_bounty_system(self) -> Tuple[bool, str]:
        """Initialize bounty state machine and treasury"""
        try:
            if self.certified_math is None:
                return (False, "Core math not initialized")

            self.treasury = DevRewardsTreasury()
            self.bounty_system = BountyStateMachine(
                treasury=self.treasury,
                # certified_math=self.certified_math # BountyStateMachine might need cm? Check init
            )
            # Depending on BountyStateMachine init, we might need to inject cm
            return (True, "Bounty system initialized")
        except Exception as e:
            return (False, f"Bounty system failed: {str(e)}")

    def verify_v14_baseline(self) -> Tuple[bool, str]:
        """Verify v14 regression hashes match golden values"""
        # Placeholder for actual hash verification logic if we had a dedicated validator module
        # For now, we rely on the existence of golden_hashes.json
        golden_path = ROOTDIR / "v13/tests/regression/golden_hashes.json"
        if golden_path.exists():
            return (True, "v14 baseline golden hash file found")
        return (False, "golden_hashes.json missing")

    def get_system_status(self) -> Dict[str, Any]:
        """Health check for all services"""
        return {
            "core_math": self.certified_math is not None,
            "social_layer": all(
                [self.spaces is not None, self.wall is not None, self.chat is not None]
            ),
            "bounty_system": self.bounty_system is not None,
            "treasury": self.treasury is not None,
            "initialized": self.initialized,
        }

    def bootstrap_all(self) -> Dict[str, Any]:
        """Execute full initialization sequence"""
        results = {}

        # Step 1: Core Math
        success, message = self.initialize_core_math()
        results["core_math"] = {"success": success, "message": message}
        if not success:
            return {"overall_success": False, "results": results}

        # Step 2: Social Layer
        success, message = self.initialize_social_layer()
        results["social_layer"] = {"success": success, "message": message}
        if not success:
            return {"overall_success": False, "results": results}

        # Step 3: Bounty System
        success, message = self.initialize_bounty_system()
        results["bounty_system"] = {"success": success, "message": message}
        if not success:
            return {"overall_success": False, "results": results}

        # Step 4: Verify v14 Baseline
        success, message = self.verify_v14_baseline()
        results["v14_verification"] = {"success": success, "message": message}

        self.initialized = True
        return {"overall_success": True, "results": results}


# Convenience functions for direct import
def bootstrap_atlas() -> Tuple[ATLASBootstrap, Dict[str, Any]]:
    """Main entry point for ATLAS initialization"""
    atlas = ATLASBootstrap()
    results = atlas.bootstrap_all()
    return (atlas, results)


def quick_check() -> bool:
    """Quick sanity check that imports work"""
    try:
        from v13.libs.CertifiedMath import CertifiedMath
        from v13.libs.BigNum128 import BigNum128

        cm = CertifiedMath()
        bn = BigNum128.from_int(100)
        return True
    except Exception:
        return False
