from CertifiedMath import CertifiedMath, BigNum128

def debug_transcendental():
    """Debug transcendental function logging."""
    log_list = []
    cm = CertifiedMath(log_list)
    x = BigNum128.from_string('0.5')
    print('Testing sqrt...')
    result_sqrt = cm.sqrt(x, 'sqrt_test', {'func': 'sqrt'})
    print(f'Result: {result_sqrt.to_decimal_string()}')
    print('Testing ln...')
    result_ln = cm.ln(x, 'ln_test', {'func': 'ln'})
    print(f'Result: {result_ln.to_decimal_string()}')
    print('Testing phi_series...')
    result_phi = cm.phi_series(x, 'phi_test', {'func': 'phi_series'})
    print(f'Result: {result_phi.to_decimal_string()}')
    print(f'\nLog entries: {len(log_list)}')
    for i, entry in enumerate(log_list):
        print(f"  {i}: op_name={entry.get('op_name')}, log_index={entry.get('log_index')}")
if __name__ == '__main__':
    debug_transcendental()
