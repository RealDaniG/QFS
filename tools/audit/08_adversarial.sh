#!/bin/bash

# QFS V13.5 - Adversarial Simulator Runner
# Runs the AdversarialSimulator with specified parameters

set -e

# Default values
MODE="dev"
SCENARIO="all"
OUT="evidence/phase2/adversary_results.json"
TEST_MODE="false"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --scenario)
            SCENARIO="$2"
            shift 2
            ;;
        --out)
            OUT="$2"
            shift 2
            ;;
        --test_mode)
            TEST_MODE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Running Adversarial Simulator - Mode: $MODE, Scenario: $SCENARIO"

# Create evidence directory
mkdir -p "$(dirname "$OUT")"

# Run the adversarial simulator
cd src/tools
if [[ "$TEST_MODE" == "true" ]]; then
    python -c "
import sys
sys.path.insert(0, '../..')
from adversarial_simulator import AdversarialSimulator, CIR302_Handler
from test_cir302_handler import TestCIR302Handler
from libs.CertifiedMath import CertifiedMath
import json

# Create test-mode CIR302 handler
test_cir302 = TestCIR302Handler()

# Create simulator in test mode
simulator = AdversarialSimulator(CertifiedMath(), test_cir302, test_mode=True)

# Run all attacks
results = simulator.run_all_attacks()

# Save results
result_data = {
    'mode': '$MODE',
    'scenario': '$SCENARIO',
    'attacks': [
        {
            'attack_name': r.attack_name,
            'triggered_cir302': r.triggered_cir302,
            'error_message': r.error_message,
            'recovery_state': r.recovery_state
        }
        for r in results
    ]
}

with open('../../$OUT', 'w') as f:
    json.dump(result_data, f, indent=2)

print('Adversarial simulator completed. Results saved.')
"
else
    # Run in live mode (would trigger actual CIR-302)
    python -c "
import sys
sys.path.insert(0, '../..')
from adversarial_simulator import AdversarialSimulator, CIR302_Handler
from libs.CertifiedMath import CertifiedMath
import json

# Create CIR302 handler
cm = CertifiedMath
cir302 = CIR302_Handler(cm)

# Create simulator
simulator = AdversarialSimulator(CertifiedMath(), cir302)

# Run all attacks (these will trigger SystemExit in real implementation)
try:
    results = simulator.run_all_attacks()
    
    # Save results
    result_data = {
        'mode': '$MODE',
        'scenario': '$SCENARIO',
        'attacks': [
            {
                'attack_name': r.attack_name,
                'triggered_cir302': r.triggered_cir302,
                'error_message': r.error_message,
                'recovery_state': r.recovery_state
            }
            for r in results
        ]
    }
    
    with open('../../$OUT', 'w') as f:
        json.dump(result_data, f, indent=2)
        
    print('Adversarial simulator completed. Results saved.')
except SystemExit as e:
    print(f'SystemExit caught with code {e.code} - this is expected in adversarial testing')
"
fi
cd ../..

echo "Adversarial Simulator completed."