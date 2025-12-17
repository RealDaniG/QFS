from v13.libs.crypto.derivation import derive_creator_keypair

priv, addr = derive_creator_keypair("DEV")
print(f"ADDRESS:{addr}")
