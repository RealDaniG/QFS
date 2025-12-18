import sys
import unittest
import os

# Add root to sys.path to allow imports if run directly
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from v13.tests.integration.harness import SimulationHarness


class TestQFSLifecycle(unittest.TestCase):
    def setUp(self):
        self.harness = SimulationHarness()
        self.user = self.harness.register_user("u_test", "0x123")

    def test_full_flow(self):
        """
        Verify: User Post -> Reward (BigNum128) -> OpenAGI Signal
        """
        print("\n--- Starting Lifecycle Simulation ---")

        # 1. User posts content
        content_id = "post_001"
        print(f"[1] User {self.user.user_id} posting content {content_id}...")
        event = self.harness.simulate_content_lifecycle(
            self.user, content_id, {"text": "Hello QFS"}
        )

        self.assertIsNotNone(event)
        self.assertEqual(event.target_id, self.user.user_id)
        # CRITICAL INVARIANT: BigNum128 precision (18 decimals) must be preserved as string.
        # Do NOT convert to float or int before this boundary.
        self.assertEqual(event.amount, "10000000000000000000")
        print(f"[2] Reward Event Logged: {event.amount} {event.token_type}")

        # 2. Agent observes
        print(f"[3] OpenAGI Agent observing {content_id}...")
        signal = self.harness.simulate_agent_observation(content_id)

        self.assertIsNotNone(signal)
        self.assertEqual(signal.payload["target_content"], content_id)
        print(f"[4] Advisory Signal Issued: {signal.signature}")

        # 3. Final Ledger Check
        self.assertEqual(len(self.harness.ledger), 1)
        self.assertEqual(len(self.harness.signals), 1)
        print("--- Simulation Complete: SUCCESS ---")


if __name__ == "__main__":
    unittest.main()
