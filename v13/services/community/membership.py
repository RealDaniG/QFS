"""
membership.py - Guild Membership & Staking Service
"""

from typing import Dict, List, Any
from v13.services.community.manager import GuildManager


class MembershipService:
    def __init__(self, guild_manager: GuildManager):
        self.guild_mgr = guild_manager
        # Mapping: guild_id -> list of member_records
        self._memberships: Dict[str, List[Dict[str, Any]]] = {}

    def join_guild(
        self, user_id: str, guild_id: str, user_coherence: float, user_balance: float
    ) -> bool:
        """
        Process a user joining a guild.
        checks coherence > threshold and balance > stake.
        """
        guild = self.guild_mgr.get_guild(guild_id)
        if not guild:
            raise ValueError("Guild not found")

        # 1. Coherence Check
        if user_coherence < guild["coherence_threshold"]:
            raise ValueError(
                f"Coherence score {user_coherence} below threshold {guild['coherence_threshold']}"
            )

        # 2. Staking Check (Mock)
        required_stake = guild["staking_requirement"]["amount"]
        if user_balance < required_stake:
            raise ValueError(
                f"Insufficient balance for stake. Need {required_stake}, have {user_balance}"
            )

        # 3. Add Member
        if guild_id not in self._memberships:
            self._memberships[guild_id] = []

        # Check if already member
        for m in self._memberships[guild_id]:
            if m["user_id"] == user_id:
                return True  # Already joined

        member_record = {
            "user_id": user_id,
            "guild_id": guild_id,
            "role": "MEMBER",
            "stake_locked": required_stake,
            "joined_at": 1234567890,  # Mock time
        }
        self._memberships[guild_id].append(member_record)

        # Update guild stats
        guild["members_count"] += 1

        return True

    def get_members(self, guild_id: str) -> List[Dict[str, Any]]:
        return self._memberships.get(guild_id, [])
