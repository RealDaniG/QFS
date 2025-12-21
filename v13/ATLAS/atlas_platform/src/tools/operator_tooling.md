# Operator Tooling for QFS V13.7

## Overview
This document describes the operator tooling available in QFS V13.7, including metrics, CIR-302 incident handling, and proof verification capabilities.

## Storage/Metrics Dashboard

### Available Endpoints
The following metrics endpoints are available through the ATLAS API:

1. **Basic Storage Metrics**
   - Endpoint: `GET /api/v1/metrics/storage`
   - Provides: Node counts, object counts, shard counts, ATR/NOD metrics

2. **Detailed Node Metrics**
   - Endpoint: `GET /api/v1/metrics/storage/nodes`
   - Provides: Per-node metrics including storage bytes, uptime, proofs verified

3. **Economics Summary**
   - Endpoint: `GET /api/v1/metrics/storage/economics`
   - Provides: ATR fees collected, NOD rewards distributed, conservation status

4. **Prometheus-Compatible Metrics**
   - Endpoint: `GET /api/v1/metrics/prometheus`
   - Provides: Metrics in Prometheus format for monitoring systems

### Schema Stability
All metrics endpoints return deterministic, structured data with stable schemas:
- JSON responses with consistent field names
- Deterministic ordering of collections
- Backward-compatible field additions
- No breaking changes without major version bump

### Degraded-Mode Handling
Metrics endpoints gracefully handle degraded modes:
- Return partial data when some nodes are unreachable
- Include error indicators in responses
- Maintain availability even during incidents
- Log appropriate warnings for troubleshooting

## CIR-302 Incident Handling

### Integration Status
The real CIR-302 handler is fully integrated with the simulation scripts:
- Located at: `scripts/simulate_storage_cir302_incident.py`
- Real handler integration documented in: `tools/cir302_playbook.md`

### Simulation Scripts
Operators can run incident simulations using:
```bash
cd v13/
python scripts/simulate_storage_cir302_incident.py --incident-type node_failure --severity 3
```

### Operator Playbook
See `tools/cir302_playbook.md` for detailed procedures on:
- Running simulations
- Interpreting results
- Responding to incidents
- Troubleshooting common issues

## Merkle/Proof Verification

### Available Endpoints
Minimal proof verification paths are exposed for ATLAS to verify high-stakes actions:

1. **Storage Proof Verification**
   - Endpoint: `POST /api/v1/proofs/verify-storage`
   - Verifies storage proofs for objects and shards
   - Deterministic and matches QFS outputs

2. **Transaction Proof Verification**
   - Endpoint: `POST /api/v1/proofs/verify-transaction`
   - Verifies transaction signatures and integrity

### Verification Characteristics
- **Deterministic**: Same inputs always produce same outputs
- **Stable**: API endpoints and response schemas are stable
- **Comprehensive**: Covers both storage and transaction proofs
- **Secure**: Uses cryptographic verification where applicable

### Test Verification
Proof verification is tested to ensure:
- Deterministic responses for fixed inputs
- Correct validation of proof chains
- Proper error handling for invalid proofs
- Schema stability across versions

## Best Practices for Operators

### Monitoring
1. Regularly check metrics endpoints for anomalies
2. Set up alerts for critical metric thresholds
3. Monitor CIR-302 logs for incident detection
4. Track proof verification success rates

### Maintenance
1. Run periodic CIR-302 simulations to verify system readiness
2. Update monitoring dashboards with new metrics
3. Review and update operator playbooks regularly
4. Test proof verification endpoints after system updates

### Incident Response
1. Follow the CIR-302 operator playbook for incident handling
2. Document all incidents and responses for future reference
3. Coordinate with development team for complex issues
4. Conduct post-incident reviews to improve procedures

### Upgrades
1. Verify metrics endpoint compatibility before upgrades
2. Test proof verification endpoints after upgrades
3. Update monitoring configurations as needed
4. Review new features in release notes

## Troubleshooting

### Common Issues

#### Metrics Endpoints Not Responding
1. Check if ATLAS API service is running
2. Verify network connectivity to API endpoints
3. Review service logs for error messages
4. Confirm metrics router is properly included

#### CIR-302 Simulations Failing
1. Check simulation script parameters
2. Verify incident types are supported
3. Review CIR-302 logs for error details
4. Ensure adequate system resources

#### Proof Verification Errors
1. Validate proof request format
2. Check cryptographic material validity
3. Verify node assignments are correct
4. Review proof chain integrity

### Diagnostic Commands
```bash
# Check API health
curl http://localhost:8000/health

# Check metrics endpoints
curl http://localhost:8000/api/v1/metrics/storage

# Check proof verification health
curl http://localhost:8000/api/v1/proofs/health

# Run basic CIR-302 simulation
python scripts/simulate_storage_cir302_incident.py --help
```

## Support Resources

### Documentation
- Main documentation: `/docs/qfs-v13.7-manual.pdf`
- API documentation: `/api/docs`
- Incident history: `/logs/incident-history/`

### Contact
- Security Team: security@qfs.example.com
- Operations Team: ops@qfs.example.com
- Development Team: dev@qfs.example.com

### Tools Directory
All operator tools are located in the `tools/` directory:
- `cir302_playbook.md`: CIR-302 procedures
- `operator_tooling.md`: This document
- Future tools will be added here