
import subprocess
import sys
import os
import json
import pytest
from unittest.mock import MagicMock
from v13.core.CoherenceLedger import CoherenceLedger

def test_verify_reward_proof_cli():
    # 1. Generate valid proof data
    # We use CoherenceLedger's own hash function to ensure consistency
    cl = CoherenceLedger(MagicMock())
    
    timestamp = 12345
    previous_hash = "abc12345" * 4 # 32 chars
    entry_data = {"test": "data", "rewards": {"amount": 10}}
    
    # Generate canonical hash
    expected_hash = cl._generate_entry_hash(entry_data, previous_hash, timestamp)
    
    proof_json = {
        "explanation": {
            "zero_sim_proof": {
                "input_state_hash": previous_hash,
                "output_state_hash": expected_hash,
                "timestamp": timestamp,
                "entry_data_snapshot": entry_data,
                "logic_version": "test",
                "pqc_cid": "cid"
            }
        }
    }
    
    # 2. Write to file
    filename = "temp_test_proof.json"
    try:
        with open(filename, "w") as f:
            json.dump(proof_json, f)
            
        # 3. Run script
        cmd = [sys.executable, "v13/scripts/verify_reward_proof.py", filename]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 4. Assert
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        assert result.returncode == 0
        assert "[SUCCESS]" in result.stdout
        
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def test_verify_reward_proof_cli_failure():
    # Tampered data
    proof_json = {
        "explanation": {
            "zero_sim_proof": {
                "input_state_hash": "abc",
                "output_state_hash": "def", # Mismatch
                "timestamp": 123,
                "entry_data_snapshot": {},
            }
        }
    }
    
    filename = "temp_test_fail.json"
    try:
        with open(filename, "w") as f:
            json.dump(proof_json, f)
        
        cmd = [sys.executable, "v13/scripts/verify_reward_proof.py", filename]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("STDOUT:", result.stdout)
        assert result.returncode == 1
        assert "[FAILURE]" in result.stdout
        
    finally:
        if os.path.exists(filename):
            os.remove(filename)
