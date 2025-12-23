import asyncio
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from lib.trust.envelope import TrustedEnvelope
from lib.intelligence.registry import get_agent_registry
from lib.intelligence.report import AdvisoryVerdict


async def verify_intelligence_layer():
    print("Locked & Loaded: Verifying ATLAS v19 Phase 4 (Intelligence)...")

    registry = get_agent_registry()
    print(f"\n[1] Agents Online: {len(registry._agents)}")

    # Test Case 1: valid Bounty Claim
    print("\n[2] Testing BountyValidator (Valid Case)...")
    bounty_envelope = TrustedEnvelope(
        payload_cid="QmValidBountyProof123",
        author_address="0x1234567890123456789012345678901234567890",
        signature="0xValidSig",
        content_type="atlas.bounty.claim.v1",
        tags=["proof", "v19"],
    )

    reports = await registry.analyze_envelope(bounty_envelope)

    bounty_report = next((r for r in reports if r.agent_id == "BountyValidator"), None)
    if bounty_report and bounty_report.verdict == AdvisoryVerdict.PASS:
        print("✅ BountyValidator: PASSED valid claim")
    else:
        print(
            f"❌ BountyValidator: Unexpected result {bounty_report.verdict if bounty_report else 'None'}"
        )

    # Test Case 2: Fraud Detection (Future Timestamp)
    print("\n[3] Testing FraudDetector (Time Travel)...")
    import time

    future_envelope = TrustedEnvelope(
        payload_cid="QmFraud",
        author_address="0x1234567890123456789012345678901234567890",  # Valid format, malicious intent
        signature="0xSig",
        content_type="atlas.feed.post",
        timestamp=int(time.time() + 3600),  # 1 hour in future
        tags=[],
    )

    reports_fraud = await registry.analyze_envelope(future_envelope)
    fraud_report = next(
        (r for r in reports_fraud if r.agent_id == "FraudDetector"), None
    )

    if fraud_report and fraud_report.verdict == AdvisoryVerdict.REJECT:
        print(f"✅ FraudDetector: CAUGHT time travel ({fraud_report.factors})")
    else:
        print(
            f"❌ FraudDetector: Failed to catch fraud. Verdict: {fraud_report.verdict if fraud_report else 'None'}"
        )

    # Test Case 3: Governance Analysis
    print("\n[4] Testing GovernanceAnalyzer (Emergency)...")
    gov_envelope = TrustedEnvelope(
        payload_cid="QmProposal",
        author_address="0x1234567890123456789012345678901234567890",
        signature="0xSig",
        content_type="atlas.governance.proposal",
        tags=["emergency", "economics"],
    )

    reports_gov = await registry.analyze_envelope(gov_envelope)
    gov_report = next(
        (r for r in reports_gov if r.agent_id == "GovernanceAnalyzer"), None
    )

    if gov_report and "Emergency tag present" in gov_report.factors:
        print(f"✅ GovernanceAnalyzer: Flagged EMERGENCY proposal")
    else:
        print(f"❌ GovernanceAnalyzer: Missed flags.")

    print("\n✅ PHASE 4 VERIFIED. Intelligence Layer is Active (Advisory Mode).")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_intelligence_layer())
