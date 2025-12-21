import { Ascon } from 'ascon-js'
import { hexToBytes, bytesToStr, strToBytes, bytesToHex } from '../src/lib/p2p/crypto'

async function runTest() {
    console.log("TS Generating Ciphertext for Empty AD...")

    // Test Vectors
    const key = hexToBytes("000102030405060708090a0b0c0d0e0f")
    const nonce = hexToBytes("000102030405060708090a0b0c0d0e0f")
    const ad = new Uint8Array(0) // Empty AD
    const plaintext = strToBytes("Hello P2P")

    try {
        // (key, nonce, plaintext, ad)
        const ciphertext = Ascon.encrypt(key, nonce, plaintext, ad)
        console.log(`Ciphertext (Hex): ${bytesToHex(ciphertext)}`)
    } catch (e) {
        console.error(`Error: ${e.message}`)
    }
}

runTest().catch(console.error)
