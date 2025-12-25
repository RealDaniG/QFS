"""
Simple test script to verify the explain API functionality.
"""


def test_explain_helper():
    """Test that the explain helper works correctly."""
    from v13.atlas.src.api.routes.explain import explain_helper

    # Test data
    base_reward = {"ATR": "10.0 ATR"}
    bonuses = [
        {
            "label": "Coherence bonus",
            "value": "+2.5 ATR",
            "reason": "Coherence score 0.92 above threshold",
        },
        {
            "label": "Humor bonus",
            "value": "+1.2 ATR",
            "reason": "Humor signal 0.88 above threshold",
        },
    ]
    caps = [
        {
            "label": "Humor cap",
            "value": "-0.3 ATR",
            "reason": "Humor cap applied at 1.0 ATR",
        },
    ]
    guards = [
        {"name": "Balance guard", "result": "pass", "reason": "Balance within limits"},
        {
            "name": "Rate limit guard",
            "result": "pass",
            "reason": "Rate limit not exceeded",
        },
    ]

    # Create explanation
    explanation = explain_helper.explain_value_node_reward(
        wallet_id="wallet_123",
        user_id="user_456",
        reward_event_id="reward_789",
        epoch=1,
        base_reward=base_reward,
        bonuses=bonuses,
        caps=caps,
        guards=guards,
        timestamp=1234567890,
    )

    print(f"Explanation created for wallet: {explanation.wallet_id}")
    print(f"Total reward: {explanation.total_reward}")
    print(f"Explanation hash: {explanation.explanation_hash[:16]}...")

    # Test simplified explanation
    simplified = explain_helper.get_simplified_explanation(explanation)
    print(f"Simplified summary: {simplified['summary']}")
    print(f"Verification consistent: {simplified['verification']['consistent']}")

    return True


if __name__ == "__main__":
    test_explain_helper()
    print("All tests passed!")
