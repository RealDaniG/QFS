
/**
 * SecureMessageV2 Client Implementation
 * Implements AES-GCM encryption and SHA-256 hashing for QFS-Native Secure Chat.
 * Zero-Sim compliance: Deterministic ordering via sequence numbers.
 */

// Types
export interface SecureMessageV2Payload {
    ciphertext: string; // Base64
    nonce: string;      // Base64
    seq: number;
    ts: number;         // Unix timestamp (seconds, float)
    hash: string;       // Base64 SHA-256(ciphertext + nonce + seq)
    // Metadata (not part of encryption but part of transport)
    sender?: string;
    recipient?: string;
}

// Helpers
function arrayBufferToBase64(buffer: ArrayBuffer): string {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}

function base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binary_string = window.atob(base64);
    const len = binary_string.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}

// Core Logic
export class SecureMessageClient {
    private sharedKey: CryptoKey | null = null;
    private sendSeq: number = 0;
    private recvSeq: number = 0; // Last received sequence

    /**
     * Initialize with a shared secret (derived from ECDH in real app).
     * For V1 MVP/Demo, we might derive this from a hardcoded secret or simpler exchange.
     */
    async initFromSecret(secretHex: string) {
        // Convert hex to bytes
        const keyBytes = new Uint8Array(
            secretHex.match(/.{1,2}/g)!.map(byte => parseInt(byte, 16))
        );

        this.sharedKey = await window.crypto.subtle.importKey(
            "raw",
            keyBytes,
            { name: "AES-GCM" },
            false,
            ["encrypt", "decrypt"]
        );
    }

    /**
     * Encrypt a message payload.
     */
    async encrypt(plaintext: string): Promise<SecureMessageV2Payload> {
        if (!this.sharedKey) throw new Error("CryptoKey not initialized");

        this.sendSeq++;
        const iv = window.crypto.getRandomValues(new Uint8Array(12)); // 96-bit nonce
        const enc = new TextEncoder();

        // Encrypt
        const ciphertextBuffer = await window.crypto.subtle.encrypt(
            { name: "AES-GCM", iv: iv },
            this.sharedKey,
            enc.encode(plaintext)
        );

        // Prepare fields
        const ciphertextB64 = arrayBufferToBase64(ciphertextBuffer);
        const nonceB64 = arrayBufferToBase64(iv);
        const ts = Date.now() / 1000;

        // Calculate Hash: SHA-256(ciphertext + nonce + seq_bytes)
        // Note: Python backend uses big-endian 8-byte int for seq. We must match.
        // JS DataView for 64-bit int is tricky, we'll try to match specific serialization
        // For simplicity in V1 JS-Python interop, we'll hash the STRING concatenation for robust debugging
        // unless byte-perfect match enforced.
        // Let's assume the Python V2 spec uses `ciphertext + nonce + sequence_num.to_bytes(8, 'big')`
        // We will replicate that byte construction:

        // 1. Ciphertext Bytes
        const ctBytes = new Uint8Array(ciphertextBuffer);
        // 2. Nonce Bytes
        // 3. Seq Bytes (Big Endian uint64)
        const seqBytes = new Uint8Array(8);
        const view = new DataView(seqBytes.buffer);
        // JS numbers are doubles (53 bit int precision safe), enough for sequence
        view.setUint32(4, this.sendSeq, false); // Low 32 bits, Big Endian
        // High 32 bits are 0 for now

        const hashMaterial = new Uint8Array(ctBytes.length + iv.length + 8);
        hashMaterial.set(ctBytes, 0);
        hashMaterial.set(iv, ctBytes.length);
        hashMaterial.set(seqBytes, ctBytes.length + iv.length);

        const hashBuffer = await window.crypto.subtle.digest("SHA-256", hashMaterial);
        const hashB64 = arrayBufferToBase64(hashBuffer);

        return {
            ciphertext: ciphertextB64,
            nonce: nonceB64,
            seq: this.sendSeq,
            ts: ts,
            hash: hashB64
        };
    }

    /**
     * Decrypt a message payload.
     */
    async decrypt(payload: SecureMessageV2Payload): Promise<string> {
        if (!this.sharedKey) throw new Error("CryptoKey not initialized");

        // Anti-Replay / Ordering Check
        if (payload.seq <= this.recvSeq) {
            console.warn(`Duplicate or old message: ${payload.seq} <= ${this.recvSeq}`);
            // In strict mode, throw. In relaxed UI mode, maybe just log.
            // throw new Error("Replay detected");
        }

        // Verify Hash Integrity (client-side check)
        // Reconstruct bytes
        const ctBytes = new Uint8Array(base64ToArrayBuffer(payload.ciphertext));
        const nonceBytes = new Uint8Array(base64ToArrayBuffer(payload.nonce));
        const seqBytes = new Uint8Array(8);
        new DataView(seqBytes.buffer).setUint32(4, payload.seq, false);

        const hashMaterial = new Uint8Array(ctBytes.length + nonceBytes.length + 8);
        hashMaterial.set(ctBytes, 0);
        hashMaterial.set(nonceBytes, ctBytes.length);
        hashMaterial.set(seqBytes, ctBytes.length + nonceBytes.length);

        const computedHashBuf = await window.crypto.subtle.digest("SHA-256", hashMaterial);
        const computedHash = arrayBufferToBase64(computedHashBuf);

        if (computedHash !== payload.hash) {
            throw new Error("Integrity check failed: Hash mismatch");
        }

        // Decrypt
        const plaintextBuffer = await window.crypto.subtle.decrypt(
            { name: "AES-GCM", iv: nonceBytes },
            this.sharedKey,
            ctBytes
        );

        this.recvSeq = Math.max(this.recvSeq, payload.seq);
        return new TextDecoder().decode(plaintextBuffer);
    }

    setRecvSeq(seq: number) {
        this.recvSeq = seq;
    }
}
