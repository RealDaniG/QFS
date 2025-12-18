"""
Quantum API endpoints for the ATLAS system.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Optional
import logging
import hashlib
from ...core.quantum_engine import QuantumEngine
from ...models.quantum import QuantumKeyPair, QuantumSignature, QuantumSignatureVerify, EntangledPair, QuantumState
logger = logging.getLogger(__name__)
router = APIRouter()
quantum_engine = QuantumEngine(qubits=256)
key_store: Dict[str, Dict] = {}

@router.post('/keys/generate', response_model=QuantumKeyPair)
async def generate_quantum_key_pair(key_name: Optional[str]=None, user_id: str='default_user') -> QuantumKeyPair:
    """
    Generate a new quantum-resistant key pair.
    
    Args:
        key_name: Optional name for the key pair
        user_id: User ID for key ownership
        
    Returns:
        QuantumKeyPair: The generated key pair
    """
    try:
        private_key = quantum_engine.generate_quantum_key()
        public_key = hashlib.sha256(private_key).digest()
        key_id = f'key_{len(key_store) + 1}'
        key_data = {'key_id': key_id, 'name': key_name or f'Quantum Key {len(key_store) + 1}', 'user_id': user_id, 'private_key': private_key.hex(), 'public_key': public_key.hex(), 'algorithm': 'QFS-QUANTUM-256', 'created_at': '2023-01-01T00:00:00Z'}
        key_store[key_id] = key_data
        logger.info(f'Generated quantum key pair {key_id} for user {user_id}')
        return QuantumKeyPair(key_id=key_id, name=key_data['name'], public_key=key_data['public_key'], algorithm=key_data['algorithm'])
    except Exception as e:
        logger.error(f'Error generating quantum key pair: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to generate quantum key pair')

@router.post('/sign', response_model=QuantumSignature)
async def create_quantum_signature(data: str, key_id: str, user_id: str='default_user') -> QuantumSignature:
    """
    Create a quantum-resistant signature for the given data.
    
    Args:
        data: The data to sign
        key_id: ID of the key to use for signing
        user_id: User ID for authorization
        
    Returns:
        QuantumSignature: The generated signature
    """
    try:
        key_data = key_store.get(key_id)
        if not key_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Key not found')
        if key_data['user_id'] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to use this key')
        private_key = bytes.fromhex(key_data['private_key'])
        signature = quantum_engine._generate_signature(data.encode(), private_key)
        logger.info(f'Created quantum signature with key {key_id}')
        return QuantumSignature(key_id=key_id, public_key=key_data['public_key'], signature=signature.hex(), algorithm=key_data['algorithm'])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error creating quantum signature: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to create quantum signature')

@router.post('/verify', response_model=Dict[str, bool])
async def verify_quantum_signature(verify_data: QuantumSignatureVerify) -> Dict[str, bool]:
    """
    Verify a quantum-resistant signature.
    
    Args:
        verify_data: Signature verification data
        
    Returns:
        Dict with 'is_valid' indicating if the signature is valid
    """
    try:
        signature = bytes.fromhex(verify_data.signature)
        public_key = bytes.fromhex(verify_data.public_key)
        is_valid = quantum_engine.verify_quantum_signature(verify_data.data.encode(), signature, public_key)
        return {'is_valid': is_valid}
    except Exception as e:
        logger.error(f'Error verifying quantum signature: {str(e)}')
        return {'is_valid': False}

@router.post('/entangle', response_model=EntangledPair)
async def create_entangled_pair() -> EntangledPair:
    """
    Create a pair of entangled quantum states.
    
    Returns:
        EntangledPair: The entangled quantum states
    """
    try:
        state1, state2 = quantum_engine.create_entangled_pair()
        logger.info('Created entangled quantum pair')
        return EntangledPair(state1=state1.hex(), state2=state2.hex())
    except Exception as e:
        logger.error(f'Error creating entangled pair: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to create entangled quantum pair')

@router.post('/measure', response_model=QuantumState)
async def measure_quantum_state(state: str, basis: int=0) -> QuantumState:
    """
    Measure a quantum state in the specified basis.
    
    Args:
        state: The quantum state to measure (hex string)
        basis: Measurement basis (0 or 1)
        
    Returns:
        QuantumState: The measurement result
    """
    try:
        state_bytes = bytes.fromhex(state)
        if basis not in (0, 1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Basis must be 0 or 1')
        collapsed_state, result = quantum_engine.measure_entangled_state(state_bytes, basis)
        return QuantumState(original_state=state, collapsed_state=collapsed_state.hex(), measurement_result=bool(result), basis_used=basis)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error measuring quantum state: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to measure quantum state')