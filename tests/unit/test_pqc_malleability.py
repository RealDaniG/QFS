from libs.PQC import PQC
from core.DRV_Packet import DRV_Packet

# Create a log list for the operations
log_list = []

# Create a simple packet
packet = DRV_Packet(
    ttsTimestamp=1700000000,
    sequence=1,
    seed="test_seed_12345",
    log_list=log_list
)

# Generate a keypair
keypair = PQC.generate_keypair(log_list, packet.seed_bytes, PQC.DILITHIUM5)

# Sign the packet
packet.sign(bytes(keypair.private_key), log_list)

# Get the original signature
original_sig = packet.pqc_signature

# Check if signature exists
if original_sig is None:
    print("✗ No signature generated")
    exit(1)

# Modify the signature slightly (malleability test)
sig_modified = bytearray(original_sig)
sig_modified[-1] ^= 1  # Flip the last bit
sig_modified = bytes(sig_modified)

# Verify the original signature
is_valid_original = packet.verify_signature(keypair.public_key, log_list)

# Verify the modified signature
packet.pqc_signature = sig_modified
is_valid_modified = packet.verify_signature(keypair.public_key, log_list)

if is_valid_original and not is_valid_modified:
    print("✓ PQC correctly protects against signature malleability")
else:
    print(f"✗ PQC malleability test failed: original={is_valid_original}, modified={is_valid_modified}")