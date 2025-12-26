import json
from pathlib import Path

STORAGE_PATH = Path("v13/atlas/storage/social_state.json")
STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

state = {
    "epochs": {
        "1": {
            "id": 1,
            "coherence_avg": "0.75",
            "total_flx": "2000.00",
            "merkle_root": "0xrealroot123",
            "status": "finalized",
        }
    },
    "rewards": {
        "1": [
            {
                "type": "SOCIAL_REWARD_APPLIED",
                "epoch_id": 1,
                "post_id": "real_post_1",
                "author_id": "real_user",
                "coherence_score": "0.9500",
                "engagement_weight": "2.0000",
                "sybil_multiplier": "1.0000",
                "eligibility_factor": "1.0000",
                "flx_reward": "1900.0000",
                "chr_reward": "20",
                "res_reward": "100.0000",
                "v13_version": "v13.5.0-social-v2",
                "build_manifest_sha256": "sha256:real-manifest-123",
            }
        ]
    },
}

with open(STORAGE_PATH, "w") as f:
    json.dump(state, f, indent=2)

print("Seeded social state.")
