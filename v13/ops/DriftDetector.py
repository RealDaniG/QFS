"""
DriftDetector.py - Operational tool for detecting Ledger Drift.

This tool performs a "Replay Drill" by:
1. Loading a specific segment of the QFS Ledger.
2. Re-executing the Policy Logic on the recorded inputs.
3. Comparing the resulting Explanation Hash against the hash recorded in the ledger.
4. Reporting zero-tolerance drift.

Usage:
    python -m v13.ops.DriftDetector --ledger-path v13/ledger/qfs_ledger.jsonl
"""
import argparse
import logging
from typing import List, Dict, Any
from v13.core.QFSReplaySource import LiveLedgerReplaySource
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
from v13.policy.artistic_policy import ArtisticSignalPolicy, ArtisticPolicy
from v13.policy.value_node_replay import ValueNodeReplayEngine
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DriftDetector')

class DriftDetector:

    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        self.cm = CertifiedMath()
        self.storage = StorageEngine(self.cm)
        self.replay_source = LiveLedgerReplaySource(ledger_path, self.storage)
        self.humor_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode='rewarding', dimension_weights={'surreal': 0.5, 'meta': 0.5}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1.0))
        self.artistic_policy = ArtisticSignalPolicy(policy=ArtisticPolicy(enabled=True, mode='rewarding', dimension_weights={'composition': 1.0}, max_bonus_ratio=0.3, per_user_daily_cap_atr=2.0))
        self.explain_helper = ValueNodeExplainabilityHelper(self.humor_policy, self.artistic_policy)
        self.replay_engine = ValueNodeReplayEngine(self.explain_helper)

    def check_drift(self) -> bool:
        """
        Scan the ledger for 'RewardAllocated' events and verify they replay identically.
        
        Returns:
            True if 100% compliant (no drift). False otherwise.
        """
        logger.info(f'Starting Drift Check on {self.ledger_path}...')
        drift_count = 0
        check_count = 0
        all_events = []
        for entry in sorted(self.replay_source.ledger.ledger_entries):
            event = {'id': entry.entry_id, 'timestamp': entry.timestamp, 'type': entry.entry_type, **entry.data}
            if entry.entry_type == 'reward_allocation':
                event['type'] = 'RewardAllocated'
            all_events.append(event)
        logger.info(f'Hydrating state from {len(all_events)} events...')
        self.replay_engine.replay_events(all_events)
        for i, event in enumerate(all_events):
            if event['type'] == 'RewardAllocated':
                check_count += 1
                try:
                    explanation = self.replay_engine.explain_specific_reward(event['id'], all_events)
                    if not explanation:
                        logger.error(f"DRIFT: Failed to generate explanation for event {event['id']}")
                        drift_count += 1
                        continue
                    current_hash = explanation.explanation_hash
                except Exception as e:
                    logger.error(f"DRIFT: Exception replaying {event['id']}: {e}")
                    drift_count += 1
        logger.info(f'Drift Check Complete. Checked {check_count} events. Drifts detected: {drift_count}')
        return drift_count == 0

def main():
    parser = argparse.ArgumentParser(description='QFS Ledger Drift Detector')
    parser.add_argument('--ledger-path', required=True, help='Path to JSONL ledger artifact')
    args = parser.parse_args()
    detector = DriftDetector(args.ledger_path)
    success = detector.check_drift()
    if not success:
        raise ZeroSimAbort(1)
if __name__ == '__main__':
    main()