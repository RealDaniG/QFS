import ascon
import sys


def main():
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    nonce = bytes.fromhex("00000000000000000000000000000000")
    ad = b""
    plaintext = b"hello"

    # Variant Ascon-128
    c1 = ascon.encrypt(key, nonce, ad, plaintext, variant="Ascon-128")
    print(f"Python (Ascon-128) Ciphertext: {c1.hex()}")

    # Variant Ascon-128a
    c2 = ascon.encrypt(key, nonce, ad, plaintext, variant="Ascon-128a")
    print(f"Python (Ascon-128a) Ciphertext: {c2.hex()}")


if __name__ == "__main__":
    main()
