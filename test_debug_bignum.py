import sys

sys.path.append(".")
try:
    from v13.libs.BigNum128 import BigNum128

    print("Imported BigNum128")
    print(f"BigNum128.SCALE type: {type(BigNum128.SCALE)}")

    val = BigNum128.from_string(".0")
    print(f"Result .0: {val}")

    val2 = BigNum128(100)
    print(f"Result 100: {val2}")

except Exception as e:
    import traceback

    traceback.print_exc()
