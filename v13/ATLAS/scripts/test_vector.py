import ascon
import sys


def main():
    key = bytes([0] * 16)
    nonce = bytes([0] * 16)
    ad = b""
    plaintext = b""

    # Ascon-128
    c = ascon.encrypt(key, nonce, ad, plaintext, variant="Ascon-128")
    print(f"Py_128_Zero: {c.hex()}")

    # Ascon-128a
    c_a = ascon.encrypt(key, nonce, ad, plaintext, variant="Ascon-128a")
    print(f"Py_128a_Zero: {c_a.hex()}")


if __name__ == "__main__":
    main()
