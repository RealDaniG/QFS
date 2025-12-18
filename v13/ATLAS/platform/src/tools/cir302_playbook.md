# CIR-302 Operator Playbook

## Overview
This document describes how to run CIR-302 simulations and interpret results for the QFS V13.7 system.

## Running CIR-302 Simulations

### Prerequisites
- Python 3.8+
- QFS V13.7 installed
- Access to ATLAS API endpoints

### Simulation Script
The CIR-302 simulation script is located at `scripts/simulate_storage_cir302_incident.py`. To run it:

```bash
cd v13/
python scripts/simulate_storage_cir302_incident.py
```

### Simulation Parameters
The script accepts the following parameters:
- `--incident-type`: Type of incident to simulate (default: "node_failure")
- `--severity`: Severity level (1-5, default: 3)
- `--duration`: Duration of simulation in seconds (default: 60)
- `--nodes`: Number of nodes to affect (default: 1)

## Interpreting Results

### Success Indicators
- CIR-302 handler triggers correctly
- Incident is logged to the ledger
- Affected nodes are quarantined
- System continues operating with remaining nodes
- Recovery procedures execute successfully

### Failure Indicators
- CIR-302 handler does not trigger
- Incident is not logged
- System becomes unstable
- Data loss occurs
- Recovery fails

### Log Analysis
Check the following logs for CIR-302 events:
- `/var/log/qfs/cir302.log`
- ATLAS API logs
- StorageEngine event logs
- Node telemetry data

## Common Incident Types

### 1. Node Failure
- **Symptoms**: Node stops responding, heartbeats fail
- **Impact**: Reduced redundancy, potential data unavailability
- **Resolution**: Quarantine node, redistribute shards

### 2. Network Partition
- **Symptoms**: Nodes cannot communicate, consensus failure
- **Impact**: System fragmentation, inconsistent state
- **Resolution**: Isolate affected partitions, restore connectivity

### 3. Data Corruption
- **Symptoms**: Hash mismatches, proof verification failures
- **Impact**: Data integrity compromised
- **Resolution**: Quarantine corrupted shards, reconstruct from replicas

### 4. AEGIS Verification Failure
- **Symptoms**: Node fails AEGIS checks, security breach suspected
- **Impact**: Compromised node security
- **Resolution**: Immediate node revocation, security audit

## Response Procedures

### Immediate Actions (0-5 minutes)
1. Confirm CIR-302 trigger
2. Isolate affected components
3. Begin forensic analysis
4. Notify stakeholders

### Short-term Actions (5-30 minutes)
1. Execute containment procedures
2. Initiate recovery processes
3. Monitor system stability
4. Document findings

### Long-term Actions (30+ minutes)
1. Conduct root cause analysis
2. Implement preventive measures
3. Update security protocols
4. Review and update procedures

## Metrics to Monitor

### System Health
- Node uptime percentage
- StorageEngine shard availability
- Transaction processing latency
- Error rates

### Security Metrics
- AEGIS verification success rate
- Unauthorized access attempts
- Cryptographic operation success rate
- Node revocation events

### Performance Metrics
- StorageEngine throughput
- Network latency
- Resource utilization
- Recovery time objectives

## Troubleshooting

### CIR-302 Not Triggering
1. Check incident detection thresholds
2. Verify monitoring configuration
3. Review log collection settings
4. Test incident simulation manually

### False Positives
1. Adjust detection sensitivity
2. Review incident criteria
3. Update baseline metrics
4. Calibrate alert thresholds

### Recovery Failures
1. Check backup systems
2. Verify recovery procedures
3. Test restoration processes
4. Validate system integrity

## Best Practices

### Prevention
- Regular system maintenance
- Security audits and penetration testing
- Performance optimization
- Capacity planning

### Detection
- Comprehensive monitoring
- Real-time alerting
- Automated anomaly detection
- Regular log analysis

### Response
- Well-defined procedures
- Trained personnel
- Adequate tools and resources
- Regular drills and simulations

### Recovery
- Reliable backups
- Tested restoration procedures
- Clear rollback plans
- Post-incident reviews

## Contact Information

### Emergency Contacts
- Security Team: security@qfs.example.com
- Operations Team: ops@qfs.example.com
- Development Team: dev@qfs.example.com

### Support Resources
- Internal Wiki: https://wiki.qfs.example.com
- Documentation: /docs/qfs-v13.7-manual.pdf
- Incident History: /logs/incident-history/