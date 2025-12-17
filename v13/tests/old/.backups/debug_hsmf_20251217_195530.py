from CertifiedMath import CertifiedMath, BigNum128
from HSMF import HSMF
from TokenStateBundle import create_token_state_bundle
timestamp = 1700000000
pqc_cid = 'QFSV13-HSMF-TEST-001'
quantum_metadata = {'test': 'debug'}
bundle_id = 'test-bundle-001'
chr_state = {'coherence_metric': BigNum128.from_string('1.500000000000000000')}
flx_state = {}
psi_sync_state = {}
atr_state = {'directional_metric': BigNum128.from_string('0.001000000000000000'), 'atr_magnitude': BigNum128.from_string('1.000000000000000000')}
res_state = {}
lambda1 = BigNum128.from_string('0.500000000000000000')
lambda2 = BigNum128.from_string('0.300000000000000000')
c_crit = BigNum128.from_string('1.000000000000000000')
f_atr = BigNum128.from_string('0.000010000000000000')
token_bundle = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, lambda1, lambda2, c_crit, pqc_cid, timestamp, quantum_metadata, bundle_id)
print(f'Token bundle created successfully')
print(f'Coherence metric: {token_bundle.get_coherence_metric().to_decimal_string()}')
print(f'C_CRIT: {token_bundle.c_crit.to_decimal_string()}')
print(f"ATR magnitude: {token_bundle.atr_state.get('atr_magnitude').to_decimal_string()}")
print(f'f_atr: {f_atr.to_decimal_string()}')
log_list = []
cm = CertifiedMath(log_list)
hsmf = HSMF(cm)
dez_ok = hsmf._check_directional_encoding(f_atr, pqc_cid)
print(f'DEZ check passed: {dez_ok}')
survival_ok = cm._safe_gte(token_bundle.get_coherence_metric(), token_bundle.c_crit)
print(f'Survival imperative passed: {survival_ok}')
atr_coherent = hsmf._check_atr_coherence(token_bundle.atr_state, f_atr, quantum_metadata, pqc_cid)
print(f'ATR coherence check passed: {atr_coherent}')
if not atr_coherent:
    atr_magnitude = token_bundle.atr_state.get('atr_magnitude', BigNum128.from_int(0))
    one_percent = BigNum128.from_string('0.010000000000000000')
    threshold = cm._safe_mul(atr_magnitude, one_percent)
    print(f'ATR magnitude: {atr_magnitude.to_decimal_string()}')
    print(f'One percent: {one_percent.to_decimal_string()}')
    print(f'Threshold (magnitude * 0.01): {threshold.to_decimal_string()}')
    print(f'f_atr: {f_atr.to_decimal_string()}')
    print(f'Is f_atr <= threshold? {cm._safe_lte(f_atr, threshold)}')