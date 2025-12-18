"""
Stress and concurrency verification for CertifiedMath.py to confirm determinism under high load
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import json
import hashlib
import concurrent.futures
from typing import List, Dict, Any
from CertifiedMath import CertifiedMath, BigNum128, MathOverflowError, MathValidationError, PHI_INTENSITY_B, LN2_CONSTANT, EXP_LIMIT, ZERO, ONE, TWO, set_series_precision, set_phi_intensity_damping, set_exp_limit, get_current_config, LogContext

def test_multi_threaded_determinism():
    """Test multi-threaded determinism with concurrent operations."""
    print('Testing multi-threaded determinism...')
    num_threads = 8
    operations_per_thread = 100
    results = []
    locks = [threading.Lock() for _ in range(num_threads)]

    def worker_thread(thread_id: int, result_list: List):
        """Worker thread that performs identical operations."""
        log = []
        math = CertifiedMath(log)
        for i in range(operations_per_thread):
            a = BigNum128.from_string('1.123456')
            b = BigNum128.from_string('2.654321')
            quantum_metadata = {'thread_id': 0, 'operation_index': i, 'test_id': 'MULTI_THREAD_001'}
            result1 = math.add(a, b, pqc_cid='MULTI_THREAD_001', quantum_metadata=quantum_metadata)
            result2 = math.mul(result1, a, pqc_cid='MULTI_THREAD_001', quantum_metadata=quantum_metadata)
        log_hash = math.get_log_hash()
        with locks[thread_id]:
            result_list.append({'thread_id': thread_id, 'log_hash': log_hash, 'log_entries': len(log)})
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker_thread, args=(i, results))
        threads.append(thread)
        thread.start()
    for thread in sorted(threads):
        thread.join()
    assert len(results) == num_threads, f'Expected {num_threads} results, got {len(results)}'
    first_hash = results[0]['log_hash']
    for result in sorted(results):
        assert result['log_hash'] == first_hash, f"Hash mismatch: {result['log_hash']} != {first_hash}"
        assert result['log_entries'] == results[0]['log_entries'], f'Log count mismatch'
    print(f'  [PASS] Multi-threaded determinism verified')
    print(f'  Threads: {num_threads}')
    print(f'  Operations per thread: {operations_per_thread}')
    print(f'  Log hash: {first_hash[:16]}...')
    print(f"  Log entries per thread: {results[0]['log_entries']}")

def test_concurrent_nested_operations():
    """Test deterministic exception propagation in concurrent nested operations."""
    print('Testing concurrent nested operations...')
    num_threads = 4
    results = []
    locks = [threading.Lock() for _ in range(num_threads)]

    def worker_thread_with_exceptions(thread_id: int, result_list: List):
        """Worker thread that performs operations including potential exceptions."""
        log = []
        math = CertifiedMath(log)
        exception_count = 0
        for i in range(50):
            try:
                if i % 10 == 0:
                    max_val = BigNum128(BigNum128.MAX_VALUE)
                    one = BigNum128(BigNum128.SCALE)
                    result = math.add(max_val, one, pqc_cid=f'CONCURRENT_{thread_id}')
                else:
                    a = BigNum128.from_string(f'1.{i:06d}')
                    b = BigNum128.from_string(f'2.{i:06d}')
                    result = math.add(a, b, pqc_cid=f'CONCURRENT_{thread_id}')
            except MathOverflowError:
                exception_count += 1
            except Exception:
                exception_count += 1
        log_hash = math.get_log_hash()
        with locks[thread_id]:
            result_list.append({'thread_id': thread_id, 'log_hash': log_hash, 'log_entries': len(log), 'exceptions': exception_count})
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker_thread_with_exceptions, args=(i, results))
        threads.append(thread)
        thread.start()
    for thread in sorted(threads):
        thread.join()
    assert len(results) == num_threads, f'Expected {num_threads} results, got {len(results)}'
    first_exception_count = results[0]['exceptions']
    for result in sorted(results):
        assert result['exceptions'] == first_exception_count, f"Exception count mismatch: {result['exceptions']} != {first_exception_count}"
    print(f'  [PASS] Concurrent nested operations verified')
    print(f'  Exceptions per thread: {first_exception_count}')

def test_high_load_performance():
    """Test performance under high load while maintaining determinism."""
    print('Testing high load performance...')
    log = []
    math = CertifiedMath(log)
    start_time = det_time_now()
    operation_count = 10000
    for i in range(operation_count):
        a = BigNum128.from_string(f'1.{i:06d}')
        b = BigNum128.from_string(f'2.{i:06d}')
        quantum_metadata = {'batch_id': 'HIGH_LOAD_001', 'operation_index': i}
        result1 = math.add(a, b, pqc_cid='HIGH_LOAD_001', quantum_metadata=quantum_metadata)
        result2 = math.mul(result1, a, pqc_cid='HIGH_LOAD_001', quantum_metadata=quantum_metadata)
    end_time = det_time_now()
    duration = end_time - start_time
    tps = operation_count * 2 / duration
    log_hash = math.get_log_hash()
    print(f'  [PASS] High load performance test completed')
    print(f'  Operations: {operation_count * 2}')
    print(f'  Duration: {duration:.4f}s')
    print(f'  TPS: {tps:.2f}')
    print(f'  Log hash: {log_hash[:16]}...')
    print(f'  Log entries: {len(log)}')

def test_thread_pool_executor():
    """Test with ThreadPoolExecutor for additional concurrency verification."""
    print('Testing ThreadPoolExecutor...')

    def execute_batch(batch_id: int):
        """Execute a batch of operations and return the log hash."""
        log = []
        math = CertifiedMath(log)
        for i in range(10):
            a = BigNum128.from_string(f'1.{batch_id:03d}{i:03d}')
            b = BigNum128.from_string(f'2.{batch_id:03d}{i:03d}')
            quantum_metadata = {'batch_id': batch_id, 'operation_index': i}
            result1 = math.add(a, b, pqc_cid=f'THREAD_POOL_{batch_id}', quantum_metadata=quantum_metadata)
            result2 = math.mul(result1, a, pqc_cid=f'THREAD_POOL_{batch_id}', quantum_metadata=quantum_metadata)
        return math.get_log_hash()
    num_batches = 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_batch = {executor.submit(execute_batch, i): i for i in range(num_batches)}
        results = []
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_id = future_to_batch[future]
            try:
                log_hash = future.result()
                results.append(log_hash)
            except Exception as exc:
                print(f'Batch {batch_id} generated an exception: {exc}')
    assert len(results) == num_batches, f'Expected {num_batches} results, got {len(results)}'
    unique_hashes = set(results)
    assert len(unique_hashes) == num_batches, f'Expected {num_batches} unique hashes, got {len(unique_hashes)}'
    print(f'  [PASS] ThreadPoolExecutor test completed')
    print(f'  Batches: {num_batches}')
    print(f'  Unique hashes: {len(unique_hashes)}')

def run_stress_concurrency_tests():
    """Run all stress and concurrency tests."""
    print('Running CertifiedMath Stress & Concurrency Tests...')
    print('=' * 60)
    test_multi_threaded_determinism()
    test_concurrent_nested_operations()
    test_high_load_performance()
    test_thread_pool_executor()
    print('=' * 60)
    print('[SUCCESS] All CertifiedMath Stress & Concurrency tests passed!')
if __name__ == '__main__':
    run_stress_concurrency_tests()
