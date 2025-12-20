from v15.auth.session_manager import SessionManager


def test_ascon_protected_session_lifecycle():
    sm = SessionManager()
    wallet = "0x1234567890123456789012345678901234567890"
    scopes = ["user:basic", "bounty:view"]

    # 1. Create Session
    token = sm.create_session(wallet, scopes)
    assert token.startswith("ascon1.")

    # 2. Validate Session
    session = sm.validate_session(token)
    assert session is not None
    assert session["user_id"] == wallet
    assert session["scopes"] == scopes

    # 3. Tamper with ciphertext
    parts = token.split(".")
    tampered_token = f"{parts[0]}.{parts[1]}.{'00' * len(parts[2])}.{parts[3]}"
    assert sm.validate_session(tampered_token) is None

    # 4. Tamper with tag
    tampered_tag = f"{parts[0]}.{parts[1]}.{parts[2]}.{'00' * 16}"
    assert sm.validate_session(tampered_tag) is None

    # 5. Revoke Session
    assert sm.revoke_session(token) is True
    assert sm.validate_session(token) is None


def test_session_manager_legacy_fallback():
    sm = SessionManager()
    # Manually insert a legacy session
    legacy_token = "legacy_sha256_token"
    sm._sessions[legacy_token] = {"user_id": "legacy_wallet", "scopes": []}

    assert sm.validate_session(legacy_token)["user_id"] == "legacy_wallet"
