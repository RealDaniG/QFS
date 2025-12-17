"""
manager.py - Guild Management Service
"""
<<<<<<< HEAD

import hashlib
from typing import Dict, Any, Optional, List, Union

=======
from typing import Dict, Any, Optional, List
from v13.libs.deterministic_hash import deterministic_uuid
from v13.libs.DeterministicTime import DeterministicTime
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)

class GuildManager:
    """
    Manages the lifecycle of Guilds (Communities) in ATLAS.
    """

    def __init__(self):
        self._guilds: Dict[str, Dict[str, Any]] = {}

<<<<<<< HEAD
    def create_guild(
        self,
        name: str,
        description: str,
        creator_id: str,
        coherence_threshold: int = 400,
        staking_amt: float = 100.0,
        timestamp: int = 1700000000,
    ) -> Dict[str, Any]:
        """
        Create a new Guild.
        """
        # Deterministic ID generation from creator + name
        seed_str = f"{creator_id}:{name}:{timestamp}"
        guild_hash = hashlib.sha256(seed_str.encode()).hexdigest()
        guild_id = f"did:atlas:guild:{guild_hash[:12]}"

        manifest = {
            "id": guild_id,
            "name": name,
            "description": description,
            "creator_id": creator_id,
            "coherence_threshold": coherence_threshold,
            "staking_requirement": {"token": "QFS", "amount": staking_amt},
            "treasury_address": f"0xTreasury_{guild_id.split(':')[-1]}",  # Mock derivation
            "created_at": timestamp,
            "members_count": 1,  # Founder
        }

=======
    def create_guild(self, name: str, description: str, creator_id: str, coherence_threshold: int=400, staking_amt: int=100) -> Dict[str, Any]:
        """
        Create a new Guild.
        """
        guild_id = f'did:atlas:guild:{deterministic_uuid(creator_id + name)[:12]}'
        dt = DeterministicTime()
        current_time = dt.get_timestamp()
        manifest = {'id': guild_id, 'name': name, 'description': description, 'creator_id': creator_id, 'coherence_threshold': coherence_threshold, 'staking_requirement': {'token': 'QFS', 'amount': staking_amt}, 'treasury_address': f"0xTreasury_{guild_id.split(':')[-1]}", 'created_at': current_time, 'members_count': 1}
>>>>>>> b27f784 (fix(ci/structure): structural cleanup and genesis_ledger AST fixes)
        self._guilds[guild_id] = manifest
        return manifest

    def get_guild(self, guild_id: str) -> Optional[Dict[str, Any]]:
        return self._guilds.get(guild_id)

    def update_guild(self, guild_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        guild = self._guilds.get(guild_id)
        if not guild:
            return None
        allowed = ['name', 'description', 'coherence_threshold']
        for k, v in updates.items():
            if k in allowed:
                guild[k] = v
        return guild