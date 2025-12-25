"""
Test to verify deterministic behavior and QFS compliance of AtlasAPIGateway
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from libs.deterministic_helpers import (
    ZeroSimAbort,
    det_time_now,
    det_perf_counter,
    det_random,
    qnum,
)
import json
import hashlib
from atlas_api.gateway import AtlasAPIGateway
from atlas_api.models import FeedRequest, InteractionRequest


def create_test_drv_packet():
    """Create a deterministic DRV packet for testing"""

    class MockDRVPacket:
        def __init__(self):
            self.ttsTimestamp = 1234567890

    return MockDRVPacket()


def run_deterministic_test(test_name, run_number):
    """Run a deterministic test and return results"""
    print(f"Running {test_name} - Run #{run_number}...")
    gateway = AtlasAPIGateway()
    drv_packet = create_test_drv_packet()
    gateway.set_drv_packet(drv_packet)
    feed_request = FeedRequest(user_id="test_user_123", limit=5, mode="coherence")
    feed_response = gateway.get_feed(feed_request)
    interaction_request = InteractionRequest(
        user_id="test_user_123",
        target_id="test_post_456",
        content="This is a test comment",
    )
    interaction_response = gateway.post_interaction("comment", interaction_request)
    results = {
        "feed_response": {
            "posts_count": len(feed_response.posts),
            "policy_version": feed_response.policy_metadata.get("version"),
            "timestamp": feed_response.policy_metadata.get("applied_at"),
        },
        "interaction_response": {
            "success": interaction_response.success,
            "event_id": interaction_response.event_id,
            "safety_guard_passed": interaction_response.guard_results.safety_guard_passed
            if interaction_response.guard_results
            else False,
            "economics_guard_passed": interaction_response.guard_results.economics_guard_passed
            if interaction_response.guard_results
            else False,
        },
    }
    results_json = json.dumps(results, sort_keys=True, separators=(",", ":"))
    results_hash = hashlib.sha256(results_json.encode("utf-8")).hexdigest()
    print(f"{test_name} Run #{run_number} completed. Hash: {results_hash}")
    return (results_hash, results)


def main():
    """Main test function"""
    print("Starting deterministic behavior test...")
    hash1, results1 = run_deterministic_test("Deterministic Test", 1)
    hash2, results2 = run_deterministic_test("Deterministic Test", 2)
    if hash1 == hash2:
        print("✅ DETERMINISTIC BEHAVIOR TEST PASSED - Hashes match!")
        print(f"Hash: {hash1}")
        print("\nSample Results:")
        print(f"Feed posts count: {results1['feed_response']['posts_count']}")
        print(f"Interaction success: {results1['interaction_response']['success']}")
        print(
            f"Safety guard passed: {results1['interaction_response']['safety_guard_passed']}"
        )
        print(
            f"Economics guard passed: {results1['interaction_response']['economics_guard_passed']}"
        )
        return True
    else:
        print("❌ DETERMINISTIC BEHAVIOR TEST FAILED - Hashes do not match!")
        print(f"Hash 1: {hash1}")
        print(f"Hash 2: {hash2}")
        return False


if __name__ == "__main__":
    success = main()
    raise ZeroSimAbort(0 if success else 1)
