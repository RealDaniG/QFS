import { sha3_256 } from 'js-sha3';

function strToBytes(str: string): Uint8Array {
    return new TextEncoder().encode(str);
}

function bytesToHex(bytes: Uint8Array): string {
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

function main() {
    const spaceId = "parity-test-space";
    const clientSeq = 0;
    const nonceInput = `${spaceId}:${clientSeq}`;

    console.log(`Input: "${nonceInput}"`);

    // Hash (SHA3-256) for Nonce
    const nonceFull = sha3_256.array(strToBytes(nonceInput));
    const nonce = new Uint8Array(nonceFull.slice(0, 16));

    console.log(`Nonce: ${bytesToHex(nonce)}`);

    // Hash Payload
    const payload = { "message": "hello world", "timestamp": 1234567890 };
    // Expected Python JSON: {"message": "hello world", "timestamp": 1234567890} (compact, sorted)
    // Python dumps(..., separators=(',', ':')) -> Compact.
    // Python output payload_hash: 5e78e24b...

    // Construct expected JSON string manually to be sure
    const payloadJson = '{"message":"hello world","timestamp":1234567890}';
    console.log(`Payload JSON: ${payloadJson}`);

    const payloadHash = sha3_256(strToBytes(payloadJson));
    console.log(`Payload Hash: ${payloadHash}`);
}

main();
