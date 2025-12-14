#!/usr/bin/env python3
"""
Simple test to verify EconomicsGuard functionality
"""

import sys
import os


from v13.libs.economics.EconomicsGuard import EconomicsGuard
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

def test_economics_guard():
    """Test the EconomicsGuard implementation."""
    print("Testing EconomicsGuard...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create EconomicsGuard
    economics_guard = EconomicsGuard(cm)
    
    log_list = []
    
    # Test CHR reward validation - valid reward
    reward_amount = BigNum128.from_int(100)  # Valid reward amount
    current_daily_total = BigNum128.from_int(1000)  # Current daily total
    current_total_supply = BigNum128.from_int(100000)  # Current total supply
    
    result1 = economics_guard.validate_chr_reward(
        reward_amount=reward_amount,
        current_daily_total=current_daily_total,
        current_total_supply=current_total_supply,
        log_list=log_list
    )
    
    print(f"Valid CHR reward validation: {result1.passed}")
    if not result1.passed:
        print(f"Error code: {result1.error_code}")
        print(f"Error message: {result1.error_message}")
    
    # Test CHR reward validation - reward too high
    high_reward_amount = BigNum128.from_int(100000)  # Too high reward amount
    
    result2 = economics_guard.validate_chr_reward(
        reward_amount=high_reward_amount,
        current_daily_total=current_daily_total,
        current_total_supply=current_total_supply,
        log_list=log_list
    )
    
    print(f"High CHR reward validation: {result2.passed}")
    if not result2.passed:
        print(f"Error code: {result2.error_code}")
        print(f"Error message: {result2.error_message}")
    
    # Verify results
    if result1.passed and not result2.passed:
        print("✅ ECONOMICS GUARD TEST PASSED!")
        return True
    else:
        print("❌ ECONOMICS GUARD TEST FAILED!")
        return False

if __name__ == "__main__":
    success = test_economics_guard()
    sys.exit(0 if success else 1)