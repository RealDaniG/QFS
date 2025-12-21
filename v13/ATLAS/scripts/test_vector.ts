import { Ascon } from 'ascon-js';

function bytesToHex(bytes: Uint8Array): string {
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function main() {
    const key = new Uint8Array(16);
    const nonce = new Uint8Array(16);
    const ad = new Uint8Array(0);
    const plaintext = new Uint8Array(0);

    const c = await Ascon.encrypt(key, nonce, plaintext, ad);
    console.log(`TS_Zero: ${bytesToHex(c)}`);
}

main();
