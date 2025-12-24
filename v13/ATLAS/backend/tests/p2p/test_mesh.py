"""
Lightweight P2P Mesh Test Environment
Spins up multiple nodes in a single process for fast testing.
"""

import asyncio
import sys
import os
from typing import List

# Adjust path to backend root
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from lib.p2p.node import ATLASLibp2pNode
from lib.trust.envelope import TrustedEnvelope
from lib.intelligence.registry import get_agent_registry
from lib.ipfs.mock_service import get_test_ipfs_service


class P2PTestHarness:
    """Manages multiple P2P nodes for testing"""

    def __init__(self):
        self.nodes: List[ATLASLibp2pNode] = []
        self.received_messages = {}  # Track messages per node

    async def spawn_node(
        self, port: int, bootstrap_peers: List[str] = None
    ) -> ATLASLibp2pNode:
        """Spawn a new P2P node and wait for bootstrap connections"""
        # Inject Mock IPFS to avoid Docker dependency
        mock_ipfs = get_test_ipfs_service()

        node = ATLASLibp2pNode(
            port=port, bootstrap_peers=[]
        )  # Empty bootstrap, we connect manually

        # Inject Mock IPFS store
        from lib.ipfs.store import IPFSContentStore

        node.content_store = IPFSContentStore(ipfs_service=mock_ipfs)

        await node.start()
        await asyncio.sleep(0.2)  # Allow WS server to fully bind
        self.nodes.append(node)

        # Manually connect to bootstrap peers AFTER start completes
        if bootstrap_peers:
            for peer_url in bootstrap_peers:
                await node.connect_to_peer(peer_url)

        print(f"[Harness] [TRUE] Node spawned on port {port}")
        return node

    async def cleanup(self):
        """Stop all nodes"""
        print("\n[Harness] Cleaning up nodes...")
        for node in self.nodes:
            await node.shutdown()
        self.nodes = []
        self.received_messages = {}

    def get_message_count(self, node_port: int) -> int:
        """Get number of messages received by a node"""
        for node in self.nodes:
            if node.port == node_port:
                count = node.get_message_count()
                print(f"[DEBUG] Node {node_port} count: {count}")
                return count
        return 0


# ==================== Test Scenarios ====================


async def test_basic_connectivity():
    """Test: Two nodes connect and exchange messages"""
    print("\n[TEST] Basic Connectivity\n")

    harness = P2PTestHarness()

    try:
        # Spawn Node A (9000)
        node_a = await harness.spawn_node(9000)

        # Spawn Node B (9001) -> A
        node_b = await harness.spawn_node(
            9001, bootstrap_peers=["http://127.0.0.1:9000/ws"]
        )

        # Wait for connection
        await asyncio.sleep(2)

        # Check peer counts
        print(f"Node A peers: {node_a.get_peer_count()}")
        print(f"Node B peers: {node_b.get_peer_count()}")

        # Node A publishes a message
        test_envelope = TrustedEnvelope(
            payload_cid="bafyTest1",
            author_address="0x1234567890123456789012345678901234567890",
            signature="0xtest_sig",
            content_type="atlas.test.connectivity",
            tags=["test"],
        )

        print("\n[Node A] Publishing test envelope...")
        await node_a.publish("/atlas/feed", test_envelope)

        # Wait for propagation
        await asyncio.sleep(2)

        # Check if Node B received it
        b_messages = harness.get_message_count(9001)

        print(f"\n[PASS] Node B received {b_messages} message(s)")
        assert b_messages > 0, "Node B did not receive message!"

        print("[PASS] TEST PASSED: Basic Connectivity")

    finally:
        await harness.cleanup()


async def test_multi_hop_propagation():
    """Test: Message propagates A -> B -> C"""
    print("\n[TEST] Multi-Hop Propagation\n")

    harness = P2PTestHarness()

    try:
        # Create chain: A (9100) <- B (9101) <- C (9102)
        node_a = await harness.spawn_node(9100)
        await asyncio.sleep(0.5)  # Allow A to fully bind
        node_b = await harness.spawn_node(9101, ["http://127.0.0.1:9100/ws"])
        await asyncio.sleep(0.5)  # Allow B to connect to A
        node_c = await harness.spawn_node(9102, ["http://127.0.0.1:9101/ws"])

        await asyncio.sleep(3)  # Allow mesh to stabilize

        # Node C publishes
        test_envelope = TrustedEnvelope(
            payload_cid="bafyTestMultiHop",
            author_address="0x1234567890123456789012345678901234567890",
            signature="0xmultihop_sig",
            content_type="atlas.test.multihop",
            tags=["propagation"],
        )

        print("[Node C] Publishing...")
        await node_c.publish("/atlas/feed", test_envelope)

        await asyncio.sleep(3)

        # Check all nodes received it
        a_count = harness.get_message_count(9100)
        b_count = harness.get_message_count(9101)

        print(f"\nNode A: {a_count} messages")
        print(f"Node B: {b_count} messages")
        print(f"Node C: published (not counted)")

        assert a_count > 0, "Node A did not receive message!"
        assert b_count > 0, "Node B did not receive message!"

        print("[PASS] TEST PASSED: Multi-Hop Propagation")

    finally:
        await harness.cleanup()


async def test_fraud_detection_integration():
    """Test: FraudDetector agent catches bad envelope"""
    print("\n[TEST] Fraud Detection Integration\n")

    harness = P2PTestHarness()

    try:
        # Use 9020
        node_a = await harness.spawn_node(9020)

        # Deterministic timestamp for Zero-Sim compliance
        # Base represents "now", future is 2 hours ahead for fraud detection
        BASE_TIMESTAMP = 1735689600  # 2025-01-01 00:00:00 UTC
        FUTURE_TIMESTAMP = BASE_TIMESTAMP + 7200  # 2 hours in future

        # Create malicious envelope (time-travel)
        fraud_envelope = TrustedEnvelope(
            payload_cid="bafyFraud",
            author_address="0x1234567890123456789012345678901234567890",
            signature="0xfraud_sig",
            content_type="atlas.test.fraud",
            timestamp=FUTURE_TIMESTAMP,  # Future timestamp triggers fraud detection
            tags=["malicious"],
        )

        # Run through agent registry
        registry = get_agent_registry()
        reports = await registry.analyze_envelope(fraud_envelope)

        # Check if FraudDetector flagged it
        fraud_report = next((r for r in reports if r.agent_id == "FraudDetector"), None)

        assert fraud_report is not None, "FraudDetector did not analyze envelope"
        # Since v19.1 maps verdicts to PASS/NEEDS_REVIEW/REJECT in code
        # FraudDetector code returns AdvisoryVerdict.REJECT ('REJECT')
        assert fraud_report.verdict == "REJECT", (
            f"Expected REJECT, got {fraud_report.verdict}"
        )

        print(f"[PASS] FraudDetector verdict: {fraud_report.verdict}")
        print(f"   Reasoning: {fraud_report.reasoning}")
        print("[PASS] TEST PASSED: Fraud Detection")

    finally:
        await harness.cleanup()


async def test_deduplication():
    """Test: Duplicate messages are filtered"""
    print("\n[TEST] Message Deduplication\n")

    harness = P2PTestHarness()

    try:
        # Use 9030, 9031
        node_a = await harness.spawn_node(9030)
        node_b = await harness.spawn_node(9031, ["http://127.0.0.1:9030/ws"])

        await asyncio.sleep(2)

        test_envelope = TrustedEnvelope(
            payload_cid="bafyDedup",
            author_address="0x1234567890123456789012345678901234567890",
            signature="0xdedup_sig_same",  # Same signature = same message ID
            content_type="atlas.test.dedup",
            tags=["duplicate"],
        )

        # Publish same envelope 3 times
        print("Publishing exact same envelope 3 times...")
        for i in range(3):
            await node_a.publish("/atlas/feed", test_envelope)
            await asyncio.sleep(0.5)

        await asyncio.sleep(2)

        # Node B should receive only 1 (deduplicated)
        b_count = harness.get_message_count(9031)

        print(f"Node B received {b_count} message(s) (expected: 1)")
        assert b_count == 1, f"Deduplication failed: received {b_count} instead of 1"

        print("[PASS] TEST PASSED: Deduplication")

    finally:
        await harness.cleanup()


# ==================== Main Test Runner ====================


async def run_all_tests():
    """Run complete P2P test suite"""
    print("=" * 60)
    print("ATLAS v20 P2P Network Test Suite (Lightweight)")
    print("=" * 60)

    tests = [
        test_basic_connectivity,
        test_multi_hop_propagation,
        test_fraud_detection_integration,
        test_deduplication,
    ]

    passed = 0
    failed = 0

    for test in tests:
        await asyncio.sleep(1)  # Cleanup gap
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"[FAIL] TEST ERROR: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(1)
