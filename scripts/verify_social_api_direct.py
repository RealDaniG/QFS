import asyncio
import sys
import os

# Add root to path
sys.path.insert(0, os.getcwd())

from v13.atlas.src.api.routes.social import list_epochs, get_epoch_rewards


async def main():
    print("Verifying list_epochs...")
    epochs = await list_epochs()
    print(f"Epochs: {epochs}")
    assert len(epochs) > 0, "No epochs returned"
    assert epochs[0]["id"] == 1, "Epoch ID mismatch"

    print("Verifying get_epoch_rewards...")
    rewards = await get_epoch_rewards(1)
    print(f"Rewards: {rewards}")
    assert len(rewards) > 0, "No rewards returned"
    assert "build_manifest_sha256" in rewards[0], "Missing build identity"
    assert rewards[0]["build_manifest_sha256"] == "sha256:real-manifest-123", (
        "Mismatch in build identity"
    )

    print("API Logic Verified.")


if __name__ == "__main__":
    asyncio.run(main())
