# Redis Streams Partitioning Strategy (F-005.X)

## Strategy: Single Stream with Sequence IDs

To ensure deterministic replay, we utilize a defined partitioning strategy for Redis Streams.

### Specification

- **Stream Name**: `qfs:genesis:events`
- **Method**: Single Global Stream
- **Ordering Guarantee**: First-In-First-Out (FIFO)
- **ID Format**: `monotonic_counter` (Redis auto-generated or timestamp-based)
- **Replay Strategy**: `XREAD` from `sequence_id=0`

### Event Payload Structure

```json
{
  "sequence_id": "1735000000000-0",
  "event_id": "uuid_v7",
  "wallet": "0x...",
  "event_type": "LOGIN|REFERRAL_USE|MESSAGE|REWARD_PAYOUT",
  "metadata": "json_string"
}
```

### Determinism

By forcing all social events through a single stream key `qfs:genesis:events` (partitioned by environment, e.g., `prod` vs `stage`), we guarantee a strict total ordering of events irrespective of worker concurrency. The `GenesisLedger` consumer reads from this stream sequentially to append to the immutable JSONL ledger.
