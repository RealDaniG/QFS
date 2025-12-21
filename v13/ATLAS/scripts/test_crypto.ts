import { asconEncrypt, asconDecrypt, hexToBytes, strToBytes, bytesToHex, bytesToStr } from '../src/lib/p2p/crypto'

async function runTest() {
    console.log("Starting TS Crypto Test...")

    // Test Vectors (Must match Python)
    const key = hexToBytes("000102030405060708090a0b0c0d0e0f")
    const nonce = hexToBytes("000102030405060708090a0b0c0d0e0f")
    const ad = strToBytes("test_ad")
    const plaintext = strToBytes("Hello P2P")

    // Encrypt
    const ciphertext = await asconEncrypt(key, nonce, ad, plaintext)
    console.log(`Ciphertext (Hex): ${bytesToHex(ciphertext)}`)

    // Decrypt
    const decrypted = await asconDecrypt(key, nonce, ad, ciphertext)
    if (decrypted) {
        console.log(`TS Decrypted (Self): ${bytesToStr(decrypted)}`)
    } else {
        console.error("TS Decryption (Self) failed")
    }

    // CROSS-LANGUAGE VERIFICATION
    // Python Output from Step 809: 24c5901dda4455fbdfbd248a20fbd701ab7ede4d37c517d198
    const pythonCiphertextHex = "24c5901dda4455fbdfbd248a20fbd701ab7ede4d37c517d198"
    const pythonCiphertext = hexToBytes(pythonCiphertextHex)

    console.log(`Attempting to decrypt Python ciphertext: ${pythonCiphertextHex}`)
    const decryptedPython = await asconDecrypt(key, nonce, ad, pythonCiphertext)

    if (decryptedPython) {
        console.log(`TS Decrypted (Python): ${bytesToStr(decryptedPython)}`)
        if (bytesToStr(decryptedPython) === "Hello P2P") {
            console.log("SUCCESS: Cross-Language Parity Verified!")
        } else {
            console.error("FAILURE: Decrypted content mismatch.")
        }
    } else {
        console.error("FAILURE: TS could not decrypt Python ciphertext. Variant mismatch likely.")
    }
}

runTest().catch(console.error)
