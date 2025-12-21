import { Ascon } from 'ascon-js'
import { hexToBytes, bytesToStr, strToBytes } from '../src/lib/p2p/crypto'

async function runTest() {
    console.log("Starting Parity Permutation Test...")

    // Test Vectors
    const key = hexToBytes("000102030405060708090a0b0c0d0e0f")
    const nonce = hexToBytes("000102030405060708090a0b0c0d0e0f")
    const ad = strToBytes("test_ad")

    // Python output (C || T) -> 25 bytes
    const pythonHash = "24c5901dda4455fbdfbd248a20fbd701ab7ede4d37c517d198"
    const pythonBytes = hexToBytes(pythonHash)

    console.log(`Original Python Bytes (25): ${pythonHash}`)

    // 1. Try Standard (C || T) - Expected to fail based on previous tests
    try {
        const d1 = Ascon.decrypt(key, nonce, pythonBytes, ad)
        console.log(`[Standard] Success: ${bytesToStr(d1)}`)
    } catch (e) {
        console.log(`[Standard] Failed: ${e.message}`)
    }

    // 2. Try Tag First (T || C)
    // C is 9 bytes. T is 16 bytes.
    // pythonBytes = C (9) || T (16)
    const C = pythonBytes.slice(0, 9)
    const T = pythonBytes.slice(9)

    const tagFirst = new Uint8Array(25)
    tagFirst.set(T, 0)
    tagFirst.set(C, 16)

    try {
        const d2 = Ascon.decrypt(key, nonce, tagFirst, ad)
        console.log(`[TagFirst] Success: ${bytesToStr(d2)}`)
    } catch (e) {
        console.log(`[TagFirst] Failed: ${e.message}`)
    }
}

runTest().catch(console.error)
