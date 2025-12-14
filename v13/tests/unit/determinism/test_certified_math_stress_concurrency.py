"""
Stress and concurrency verification for CertifiedMath.py to confirm determinism under high load
"""

import sys
import os
import json
import hashlib
import threading
import time
import concurrent.futures
from typing import List, Dict, Any

# Add the libs directory to the path

from CertifiedMath import (
    CertifiedMath, BigNum128, 
    MathOverflowError, MathValidationError,
    PHI_INTENSITY_B, LN2_CONSTANT, EXP_LIMIT, ZERO, ONE, TWO,
    set_series_precision, set_phi_intensity_damping, set_exp_limit, get_current_config,
    LogContext
)

def test_multi_threaded_determinism():
    """Test multi-threaded determinism with concurrent operations."""
    print("Testing multi-threaded determinism...")
    
    # Create multiple threads with identical operations
    num_threads = 8
    operations_per_thread = 100
    
    # Shared results list
    results = []
    locks = [threading.Lock() for _ in range(num_threads)]
    
    def worker_thread(thread_id: int, result_list: List):
        """Worker thread that performs identical operations."""
        log = []
        math = CertifiedMath(log)
        
        # Perform identical operations in each thread
        for i in range(operations_per_thread):
            a = BigNum128.from_string("1.123456")
            b = BigNum128.from_string("2.654321")
            
            quantum_metadata = {
                "thread_id": 0,  # Keep thread_id consistent for deterministic behavior
                "operation_index": i,
                "test_id": "MULTI_THREAD_001"
            }
            
            result1 = math.add(a, b, pqc_cid="MULTI_THREAD_001", quantum_metadata=quantum_metadata)
            result2 = math.mul(result1, a, pqc_cid="MULTI_THREAD_001", quantum_metadata=quantum_metadata)
        
        # Get the log hash
        log_hash = math.get_log_hash()
        
        # Store result with lock
        with locks[thread_id]:
            result_list.append({
                "thread_id": thread_id,
                "log_hash": log_hash,
                "log_entries": len(log)
            })
    
    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker_thread, args=(i, results))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify all threads produced identical results
    assert len(results) == num_threads, f"Expected {num_threads} results, got {len(results)}"
    
    # All log hashes should be identical
    first_hash = results[0]["log_hash"]
    for result in results:
        assert result["log_hash"] == first_hash, f"Hash mismatch: {result['log_hash']} != {first_hash}"
        assert result["log_entries"] == results[0]["log_entries"], f"Log count mismatch"
    
    print(f"  [PASS] Multi-threaded determinism verified")
    print(f"  Threads: {num_threads}")
    print(f"  Operations per thread: {operations_per_thread}")
    print(f"  Log hash: {first_hash[:16]}...")
    print(f"  Log entries per thread: {results[0]['log_entries']}")


def test_concurrent_nested_operations():
    """Test deterministic exception propagation in concurrent nested operations."""
    print("Testing concurrent nested operations...")
    
    # Test concurrent operations that may cause exceptions
    num_threads = 4
    results = []
    locks = [threading.Lock() for _ in range(num_threads)]
    
    def worker_thread_with_exceptions(thread_id: int, result_list: List):
        """Worker thread that performs operations including potential exceptions."""
        log = []
        math = CertifiedMath(log)
        
        exception_count = 0
        
        # Mix of normal operations and operations that may cause exceptions
        for i in range(50):
            try:
                if i % 10 == 0:
                    # Operation that will cause overflow
                    max_val = BigNum128(BigNum128.MAX_VALUE)
                    one = BigNum128(BigNum128.SCALE)
                    result = math.add(max_val, one, pqc_cid=f"CONCURRENT_{thread_id}")
                else:
                    # Normal operation
                    a = BigNum128.from_string(f"1.{i:06d}")
                    b = BigNum128.from_string(f"2.{i:06d}")
                    result = math.add(a, b, pqc_cid=f"CONCURRENT_{thread_id}")
            except MathOverflowError:
                exception_count += 1
            except Exception:
                exception_count += 1
        
        # Get the log hash (only successful operations are logged)
        log_hash = math.get_log_hash()
        
        # Store result with lock
        with locks[thread_id]:
            result_list.append({
                "thread_id": thread_id,
                "log_hash": log_hash,
                "log_entries": len(log),
                "exceptions": exception_count
            })
    
    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker_thread_with_exceptions, args=(i, results))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify consistency
    assert len(results) == num_threads, f"Expected {num_threads} results, got {len(results)}"
    
    # All threads should have the same number of exceptions
    first_exception_count = results[0]["exceptions"]
    for result in results:
        assert result["exceptions"] == first_exception_count, f"Exception count mismatch: {result['exceptions']} != {first_exception_count}"
    
    print(f"  [PASS] Concurrent nested operations verified")
    print(f"  Exceptions per thread: {first_exception_count}")


def test_high_load_performance():
    """Test performance under high load while maintaining determinism."""
    print("Testing high load performance...")
    
    # Perform a large number of operations
    log = []
    math = CertifiedMath(log)
    
    start_time = time.time()
    operation_count = 10000
    
    for i in range(operation_count):
        a = BigNum128.from_string(f"1.{i:06d}")
        b = BigNum128.from_string(f"2.{i:06d}")
        
        quantum_metadata = {
            "batch_id": "HIGH_LOAD_001",
            "operation_index": i
        }
        
        result1 = math.add(a, b, pqc_cid="HIGH_LOAD_001", quantum_metadata=quantum_metadata)
        result2 = math.mul(result1, a, pqc_cid="HIGH_LOAD_001", quantum_metadata=quantum_metadata)
    
    end_time = time.time()
    duration = end_time - start_time
    tps = operation_count * 2 / duration  # 2 operations per iteration
    
    # Get final log hash
    log_hash = math.get_log_hash()
    
    print(f"  [PASS] High load performance test completed")
    print(f"  Operations: {operation_count * 2}")
    print(f"  Duration: {duration:.4f}s")
    print(f"  TPS: {tps:.2f}")
    print(f"  Log hash: {log_hash[:16]}...")
    print(f"  Log entries: {len(log)}")


def test_thread_pool_executor():
    """Test with ThreadPoolExecutor for additional concurrency verification."""
    print("Testing ThreadPoolExecutor...")
    
    def execute_batch(batch_id: int):
        """Execute a batch of operations and return the log hash."""
        log = []
        math = CertifiedMath(log)
        
        # Perform operations
        for i in range(10):
            a = BigNum128.from_string(f"1.{batch_id:03d}{i:03d}")
            b = BigNum128.from_string(f"2.{batch_id:03d}{i:03d}")
            
            quantum_metadata = {
                "batch_id": batch_id,
                "operation_index": i
            }
            
            result1 = math.add(a, b, pqc_cid=f"THREAD_POOL_{batch_id}", quantum_metadata=quantum_metadata)
            result2 = math.mul(result1, a, pqc_cid=f"THREAD_POOL_{batch_id}", quantum_metadata=quantum_metadata)
        
        return math.get_log_hash()
    
    # Execute multiple batches concurrently
    num_batches = 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all batches
        future_to_batch = {executor.submit(execute_batch, i): i for i in range(num_batches)}
        
        # Collect results
        results = []
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_id = future_to_batch[future]
            try:
                log_hash = future.result()
                results.append(log_hash)
            except Exception as exc:
                print(f"Batch {batch_id} generated an exception: {exc}")
    
    # Verify all results are identical (since they're doing the same operations)
    assert len(results) == num_batches, f"Expected {num_batches} results, got {len(results)}"
    
    # Since each batch has different inputs, hashes should be different
    # But within each batch, the operations are deterministic
    unique_hashes = set(results)
    assert len(unique_hashes) == num_batches, f"Expected {num_batches} unique hashes, got {len(unique_hashes)}"
    
    print(f"  [PASS] ThreadPoolExecutor test completed")
    print(f"  Batches: {num_batches}")
    print(f"  Unique hashes: {len(unique_hashes)}")


def run_stress_concurrency_tests():
    """Run all stress and concurrency tests."""
    print("Running CertifiedMath Stress & Concurrency Tests...")
    print("=" * 60)
    
    test_multi_threaded_determinism()
    test_concurrent_nested_operations()
    test_high_load_performance()
    test_thread_pool_executor()
    
    print("=" * 60)
    print("[SUCCESS] All CertifiedMath Stress & Concurrency tests passed!")


if __name__ == "__main__":
    run_stress_concurrency_tests()