### Operational Runbook: Social Layer & Code Identity

#### 1. Verifying Service Identity

All production services expose their build identity at `/api/meta/build`.
**Command:**

```bash
curl -s http://localhost:8001/api/meta/build | jq .
```

**Expected Output:**

```json
{
  "service": "qfs-backend-v18-modular",
  "version_tag": "v18.0.0-rc1",
  "build_manifest_sha256": "sha256:..."
}
```

#### 2. Verifying Social Rewards

Social rewards must carry the `build_manifest_sha256` of the distributor node.
**Command:**

```bash
curl -s http://localhost:8001/api/v13/social/epochs/1/rewards | jq '.[0]'
```

**Verification:**

- Check `type` is `SOCIAL_REWARD_APPLIED`
- Check `build_manifest_sha256` matches the `/api/meta/build` output.

#### 3. Analyzing EvidenceBus

Check the local SQLite evidence log for reward events.
**Command:**

```bash
sqlite3 ~/.atlas_v18/evidence.db "SELECT payload FROM evidence WHERE event_type='SOCIAL_REWARD_APPLIED' LIMIT 1;"
```

**Verification:**

- Ensure payload contains `build_manifest_sha256`.

#### 4. Automated Verification Script

Use the provided script to verify the entire end-to-end flow in a simulated production environment.

**Command:**

```bash
python scripts/verify_social_identity_full.py
```

**Scope:**

1. Verifies `/api/meta/build` against env vars.
2. Verifies `/api/v13/social/epochs/{id}/rewards` structure.
3. Emits a test reward event and verifies persistence in `evidence.db`.
