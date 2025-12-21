import { Ascon } from 'ascon-js';

function hexToBytes(hex: string): Uint8Array {
    if (hex.length % 2 !== 0) throw new Error("Invalid hex string");
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
        bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
    }
    return bytes;
}

function bytesToHex(bytes: Uint8Array): string {
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function main() {
    const key = hexToBytes("000102030405060708090a0b0c0d0e0f");
    const nonce = hexToBytes("00000000000000000000000000000000");
    const plaintext = new TextEncoder().encode("hello");

    // Try Undefined AD
    try {
        const c1 = await Ascon.encrypt(key, nonce, plaintext, undefined);
        console.log(`TS_UndefinedAD: ${bytesToHex(c1)}`);
    } catch (e) {
        console.log("TS_UndefinedAD Failed", e);
    }

    // Try null AD
    try {
        const c2 = await Ascon.encrypt(key, nonce, plaintext, null);
        console.log(`TS_NullAD: ${bytesToHex(c2)}`);
    } catch (e) {
        console.log("TS_NullAD Failed", e);
    }
}

main();
