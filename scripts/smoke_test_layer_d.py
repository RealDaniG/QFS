import os
import tempfile
import json
from v15.evidence.bus import EvidenceBus
from v17.agents import process_governance_event
from v17.ui.governance_projection import GovernanceProjection


def run_smoke_test():
    print("Running Layer D Smoke Test...")

    # 1. Setup Env
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        EvidenceBus._log_file = f.name

    try:
        # 2. Emit Proposal Event
        prop_payload = {
            "timestamp": 1234567890,
            "proposal": {
                "proposal_id": "p_smoke",
                "title": "Smoke Test",
                "requested_amount": 20000,  # Should trigger High Amount advisory
                "description": "Short",  # Should trigger Short Desc
                "creator_wallet": "0xSmoke",
                "created_at": 1234567890,
                "voting_ends_at": 1234569999,
            },
        }
        # Emit raw envelope? No, EvidenceBus.emit wraps it.
        # But we need to construct the event dict for process_governance_event manually to simulate consumption
        # Or read it back.

        EvidenceBus.emit("GOV_PROPOSAL_CREATED", prop_payload)

        # Read back to get the envelope structure
        events = EvidenceBus.get_events()
        prop_envelope = events[0]  # Should be the one

        # 3. Trigger Agent (Simulate Listener)
        # extract event from envelope
        event_data = prop_envelope.get("event")

        adv = process_governance_event(event_data)
        if adv:
            EvidenceBus.emit(adv["type"], adv["payload"])
            print(f"Agent emitted advisory: {adv['payload']['signal']['reasons']}")
        else:
            print("Agent emitted nothing (UNEXPECTED)")
            exit(1)

        # 4. View in Projection
        proj = GovernanceProjection()
        props = proj.list_proposals(limit=10)

        found = False
        for p in props:
            if p["id"] == "p_smoke":
                if "advisory" in p and len(p["advisory"]) > 0:
                    print(f"UI Projection visible: {p['advisory'][0]['reasons']}")
                    found = True

        if found:
            print("SUCCESS: Layer D functional.")
        else:
            print("FAILURE: Advisory not seen in UI.")
            exit(1)

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            try:
                os.unlink(f.name)
            except:
                pass


if __name__ == "__main__":
    run_smoke_test()
