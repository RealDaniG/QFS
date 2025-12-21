from v17.agents.governance_advisory import process_governance_event


def test_governance_advisory_ascon_wrapping():
    # Mock governance event
    event = {
        "type": "GOV_PROPOSAL_CREATED",
        "payload": {
            "proposal": {
                "proposal_id": "prop_777",
                "requested_amount": 15000,
                "title": "Big Grant",
                "description": "This is a high value request that should trigger heuristics.",
            },
            "timestamp": 123456789,
        },
    }

    advisory = process_governance_event(event)

    assert advisory is not None
    payload = advisory["payload"]

    # Verify Ascon fields are present
    assert "ascon_integrity_digest" in payload
    assert "ascon_protected_reasons" in payload
    assert payload["v18_crypto_layer"] == "ascon-v18.5"

    # Verify the protected reasons are decryptable
    from v18.crypto.edge_crypto_adapter import edge_crypto
    from v18.crypto.ascon_adapter import AsconCiphertext
    import json

    envelope = AsconCiphertext(**payload["ascon_protected_reasons"])
    reasons_json = edge_crypto.ascon_adapter.ascon_aead_decrypt(
        envelope.context, envelope, b"prop_777", edge_crypto._get_edge_key("edge_v1")
    )
    reasons = json.loads(reasons_json)
    assert "Review: High-value request (>10k)" in reasons
