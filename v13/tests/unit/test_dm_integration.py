"""
test_dm_integration.py - Integration tests for the Direct Messaging System
"""
import pytest
from v13.services.dm.identity import IdentityManager
from v13.services.dm.crypto import DMCryptoEngine
from v13.services.dm.messenger import DirectMessagingService

def test_identity_flow():
    mgr = IdentityManager()
    uid = "0xUserA"
    pub = "pubkeyA"
    
    # 1. Publish
    mgr.publish_identity(uid, pub, "sig_proof")
    
    # 2. Retrieve
    bundle = mgr.get_identity(uid)
    assert bundle is not None
    assert bundle["user_id"] == uid
    assert bundle["public_key"] == pub
    assert bundle["encryption_algo"] == "Dilithium+Kyber"

def test_crypto_wrapper():
    engine = DMCryptoEngine()
    pub, priv = engine.generate_keypair()
    
    msg = "Hello World"
    # Encrypt
    enc = engine.encrypt_message(pub, msg)
    assert enc != msg
    assert "ENC" in enc
    
    # Decrypt
    dec = engine.decrypt_message(priv, enc)
    assert dec == msg

def test_messaging_flow():
    service = DirectMessagingService()
    
    sender = "0xSender"
    recipient = "0xRecipient"
    
    # Setup identities
    service.identity_mgr.publish_identity(sender, "pubS", "proofS")
    service.identity_mgr.publish_identity(recipient, "pubR", "proofR")
    
    # Send
    uri = "ipfs://QmHash"
    c_hash = "sha256_of_content"
    
    success = service.send_message_signal(sender, recipient, uri, c_hash)
    assert success is True
    
    # Receive
    inbox = service.get_inbox(recipient)
    assert len(inbox) == 1
    assert inbox[0].sender == sender
    assert inbox[0].storage_uri == uri

def test_send_to_unknown_recipient():
    service = DirectMessagingService()
    # No identity published for recipient
    with pytest.raises(ValueError, match="Recipient.*not found"):
        service.send_message_signal("0xSender", "0xGhost", "uri", "hash")
