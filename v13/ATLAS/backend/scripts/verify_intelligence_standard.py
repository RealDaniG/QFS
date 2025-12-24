import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lib.trust.envelope import TrustedEnvelope
from lib.intelligence.agents.governance import GovernanceAnalyzer
from lib.intelligence.adapters.mock_adapter import MockModelAdapter

# Deterministic test timestamp for Zero-Sim compliance
TEST_TIMESTAMP = 1735689600  # 2025-01-01 00:00:00 UTC


async def verify_standardization():
    print("=" * 60)
    print("ATLAS v20 Intelligence API Standardization Check")
    print("=" * 60)

    # 1. Setup Mock Adapter with specific response
    mock_response = "RISK_LEVEL: HIGH. Reason: Detected keyword 'emergency'."
    adapter = MockModelAdapter(fixed_response=mock_response)
    print(f"✅ Adapter initialized: {adapter.__class__.__name__}")

    # 2. Instantiate Agent with Adapter
    agent = GovernanceAnalyzer(model_adapter=adapter)
    print(f"✅ Agent initialized: {agent.agent_id} v{agent.version}")

    # 3. Create Test Envelope with deterministic timestamp
    envelope = TrustedEnvelope(
        payload_cid="bafyTest",
        author_address="0x1234567890123456789012345678901234567890",  # Valid length
        signature="0xsig",
        content_type="governance.proposal",
        tags=["economics"],  # Should trigger heuristic OR AI
        timestamp=TEST_TIMESTAMP,
    )

    # 4. Run Analysis
    print("\n[Analysis] Running agent analysis...")
    report = await agent.analyze(envelope)

    print(f"\n[Result] Verdict: {report.verdict}")
    print(f"[Result] Factors: {report.factors}")

    # 5. Verify AI path was used
    # Mock adapter returns "RISK_LEVEL: HIGH..."
    # Logic looks for "HIGH" in content.
    # Factors should contain "AI Analysis (mock-v1): ..."

    ai_factor_present = any("AI Analysis (mock-v1)" in f for f in report.factors)

    if ai_factor_present:
        print("✅ SUCCESS: Agent used ModelAdapter for analysis.")
    else:
        print("❌ FAILURE: Agent fell back to heuristic or ignored adapter.")
        print(f"Factors found: {report.factors}")
        return False

    return True


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    success = asyncio.run(verify_standardization())
    sys.exit(0 if success else 1)
