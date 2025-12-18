# ATLAS Secure Chat Protocol Specification
# Version: 0.2.0

## 1. Overview

ATLAS Secure Chat provides end-to-end encrypted messaging capabilities integrated with the QFS economic system. The system ensures privacy while maintaining deterministic behavior for economic calculations.

## 2. Message Format

### 2.1 Message Headers
```json
{
  "version": "0.2.0",
  "timestamp": "ISO-8601 UTC timestamp",
  "message_id": "deterministic_hash(message, thread_id, sender_id, content_hash, timestamp)",
  "thread_id": "deterministic_hash(thread, creator_id, timestamp, sorted_participants)",
  "sender_id": "user_id",
  "content_hash": "sha256(ciphertext)",
  "content_size": 1234,
  "content_type": "text/plain",
  "message_type": "text|image|file|governance",
  "metadata": {
    "mime_type": "text/plain",
    "compression": "none",
    "encryption": "x25519-xsalsa20-poly1305"
  }
}
```

### 2.2 Deterministic ID Generation

All IDs are generated using HMAC-SHA256 with a fixed secret:
- Thread ID: `HMAC("ATLAS_SECURE_CHAT", "thread:" + creator_id + ":" + timestamp + ":" + sorted_participants)`
- Message ID: `HMAC("ATLAS_SECURE_CHAT", "message:" + thread_id + ":" + sender_id + ":" + content_hash + ":" + timestamp)`

## 3. Thread Lifecycle

### 3.1 Thread States
- **DRAFT**: Initial state, only visible to creator
- **ACTIVE**: Thread is active and messages can be sent
- **ARCHIVED**: Thread is read-only (no new messages)
- **DELETED**: Thread is hidden from normal API responses

### 3.2 State Transitions
- DRAFT → ACTIVE: When thread is created (immediate)
- ACTIVE → ARCHIVED: By thread creator only
- ARCHIVED → ACTIVE: By thread creator only
- * → DELETED: By thread creator only (soft delete)

### 3.3 Permissions
- **Creator**: Full control (create, archive, delete, add/remove participants)
- **Participant**: Can read/write messages in ACTIVE threads
- **Non-participant**: No access to thread or messages

## 4. Storage Layer

### 4.1 Storage Interface
```python
class SecureChatStorage:
    async def store(self, content: bytes) -> str:  # Returns content_hash
        """Store content and return its hash"""
        
    async def retrieve(self, content_hash: str) -> bytes:
        """Retrieve content by hash"""
        
    async def exists(self, content_hash: str) -> bool:
        """Check if content exists"""
```

### 4.2 Content Addressing
- **Hash Function**: SHA-256
- **Storage Backends**:
  - MemoryStorage: For testing only
  - IPFSStorage: For production (PLANNED - NOT IMPLEMENTED YET)

## 5. Security Considerations

### 5.1 Input Validation
- Maximum message size: 1MB
- Maximum participants per thread: 100
- Required fields for all operations
- Type and format validation

### 5.2 Deterministic Behavior
- All IDs are deterministically generated
- Timestamps are injected for testability
- No random number generation in business logic

### 5.3 Encryption (PLANNED - NOT IMPLEMENTED YET)
- End-to-end encryption using libsodium
- Per-thread keys with key rotation
- Perfect forward secrecy

## 6. API Endpoints

### 6.1 Thread Management
- `POST /secure-chat/threads` - Create new thread
- `GET /secure-chat/threads` - List user's threads
- `GET /secure-chat/threads/{id}` - Get thread metadata
- `PUT /secure-chat/threads/{id}/status` - Update thread status

### 6.2 Message Operations
- `POST /secure-chat/messages` - Send message
- `GET /secure-chat/threads/{id}/messages` - Get thread messages

## 7. Economic Integration

### 7.1 ATR Fees
- Fee charged per message: 1 ATR (base rate)
- Fee calculation: `fee = base_fee * (content_size / 1024)` (PLANNED)

### 7.2 Event Types
- `THREAD_CREATED`
- `MESSAGE_POSTED`
- `THREAD_UPDATED`

## 8. Open Questions

### 8.1 To Be Decided
- [ ] Finalize key rotation policy
- [ ] Define message retention period
- [ ] Determine backup/restore strategy
- [ ] Finalize rate limiting approach
- [ ] Define thread expiration policy

### 8.2 Implementation Status
- [x] Thread management
- [x] Message posting
- [x] Deterministic IDs
- [x] Basic validation
- [ ] IPFS storage adapter
- [ ] Client-side encryption
- [ ] Rate limiting
- [ ] Message expiration
- [ ] File attachments
- [ ] Message reactions
- [ ] Read receipts

## 9. Testing

### 9.1 Test Coverage
- Unit tests for engine operations
- Integration tests for storage adapters
- Security tests for validation
- Performance tests for scalability

### 9.2 Test Data
All tests use deterministic timestamps and fixed data to ensure reproducible results.

## 10. References

- Signal Protocol for encryption design
- libsodium for cryptographic primitives
- IPFS for content-addressable storage
- QFS economic model for fee structure
