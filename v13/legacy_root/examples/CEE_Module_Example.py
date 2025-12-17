"""
CEE_Module_Example.py - Example CEE Module Implementation
Demonstrates integration with PQC adapters and SignedMessage protocol
"""
import hashlib
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from src.libs.cee.interfaces.module_interface import ModuleInput, ModuleOutput, CEEModule
from src.libs.cee.interfaces.message_protocol import SignedMessage
from src.libs.cee.adapters.pqc_adapter_factory import PQCAdapterFactory
from src.libs.pqc.CanonicalSerializer import CanonicalSerializer

class ExampleModuleInput(ModuleInput):
    """Example input schema for the demonstration module."""
    action: str
    amount: str
    recipient: str

class ExampleModuleOutput(ModuleOutput):
    """Example output schema for the demonstration module."""
    transaction_id: str

class ExampleCEEModule(CEEModule):
    """
    Example CEE module demonstrating PQC adapter integration.
    """

    def __init__(self):
        """Initialize the module with a PQC adapter."""
        self.pqc_adapter, self.backend_name = PQCAdapterFactory.create_adapter()
        self.transaction_counter = 0

    def process(self, input_data: ExampleModuleInput) -> ExampleModuleOutput:
        """
        Process input and return deterministic output.
        
        Args:
            input_data: Validated module input
            
        Returns:
            Module output with state delta and audit log
        """
        audit_log = []
        audit_entry = {'operation': 'process_request', 'action': input_data.action, 'amount': input_data.amount, 'recipient': input_data.recipient, 'tick': input_data.tick, 'timestamp': input_data.timestamp}
        audit_log.append(audit_entry)
        if input_data.action == 'transfer':
            state_delta = {'transfer': {'from': 'module_account', 'to': input_data.recipient, 'amount': input_data.amount}}
            self.transaction_counter += 1
            transaction_id = f'tx_{self.transaction_counter}_{input_data.tick}'
        else:
            state_delta = {'action': input_data.action}
            transaction_id = f'op_{hashlib.sha256(input_data.action.encode()).hexdigest()[:8]}'
        output = ExampleModuleOutput(tick=input_data.tick, state_delta=state_delta, audit_log=audit_log, next_hash='', transaction_id=transaction_id)
        output_dict = output.dict()
        serialized_output = CanonicalSerializer.serialize_data(output_dict)
        next_hash = hashlib.sha3_512(serialized_output).hexdigest()
        output.next_hash = next_hash
        return output

    def validate_input(self, input_data: ExampleModuleInput) -> bool:
        """
        Validate input contract before processing.
        
        Args:
            input_data: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not input_data.action:
            return False
        if input_data.action == 'transfer':
            if not input_data.amount or not input_data.recipient:
                return False
        try:
            return True
        except Exception:
            return False

    def get_audit_schema(self) -> dict:
        """
        Return JSON schema for this module's audit logs.
        
        Returns:
            JSON schema dict
        """
        return {'type': 'object', 'properties': {'operation': {'type': 'string'}, 'action': {'type': 'string'}, 'amount': {'type': 'string'}, 'recipient': {'type': 'string'}, 'tick': {'type': 'integer'}, 'timestamp': {'type': 'integer'}}, 'required': ['operation', 'action', 'tick', 'timestamp']}

def demo_pqc_integration():
    """Demonstrate PQC adapter integration with CEE module."""
    print('=' * 80)
    print('CEE Module PQC Integration Demo')
    print('=' * 80)
    module = ExampleCEEModule()
    print(f'Module initialized with PQC backend: {module.backend_name}')
    seed = b'demo_seed_1234567890123456789012'
    private_key, public_key = module.pqc_adapter.keygen(seed)
    print(f'Generated keypair - Private key length: {len(private_key)}, Public key length: {len(public_key)}')
    test_input = ExampleModuleInput(tick=100, timestamp=1000, signature=b'', prev_hash='0' * 64, action='transfer', amount='100.0', recipient='node_abc123')
    print(f'\nProcessing input: {test_input.action} {test_input.amount} to {test_input.recipient}')
    output = module.process(test_input)
    print(f'Output generated:')
    print(f'  Transaction ID: {output.transaction_id}')
    print(f'  State delta: {output.state_delta}')
    print(f'  Audit log entries: {len(output.audit_log)}')
    print(f'  Next hash: {output.next_hash[:16]}...')
    print(f'\nCreating signed message...')
    payload = {'module': 'ExampleCEEModule', 'action': 'transfer', 'amount': '100.0', 'recipient': 'node_abc123'}
    message = SignedMessage.create(sender_qid='test_node_001', recipient_module='ExampleCEEModule', payload=payload, tick=100, timestamp=1000, private_key=private_key, public_key=public_key, pqc=module.pqc_adapter)
    print(f'Signed message created:')
    print(f'  Sender: {message.sender_qid}')
    print(f'  Recipient: {message.recipient_module}')
    print(f'  Signature length: {len(message.signature)}')
    is_valid = message.verify(module.pqc_adapter)
    print(f"Message verification: {('✅ PASS' if is_valid else '❌ FAIL')}")
    print(f'\nTesting tamper detection...')
    tampered_payload = payload.copy()
    tampered_payload['amount'] = '999999.0'
    tampered_message = SignedMessage(sender_qid=message.sender_qid, recipient_module=message.recipient_module, payload=tampered_payload, tick=message.tick, timestamp=message.timestamp, signature=message.signature, public_key=message.public_key)
    is_valid_tampered = tampered_message.verify(module.pqc_adapter)
    print(f"Tampered message verification: {('✅ PASS' if is_valid_tampered else '❌ FAIL')}")
    if not is_valid_tampered:
        print('✅ Tamper detection working - invalid signature correctly rejected')
    else:
        print('❌ Tamper detection failed - signature accepted for tampered data')
    print('\n' + '=' * 80)
    print('Demo complete!')
    print('=' * 80)
if __name__ == '__main__':
    demo_pqc_integration()