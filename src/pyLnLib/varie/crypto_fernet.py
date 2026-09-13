#!/usr/bin/env python3
# by Loreto Notarantonio

import sys; sys.dont_write_bytecode=True
import os
import base64
import hashlib
from cryptography.fernet import Fernet


def _get_fernet(master_key: str) -> Fernet:
    # salt = os.urandom(16)
    _SALT = b"my-app-fixed-salt"
    key = hashlib.pbkdf2_hmac( "sha256",
                                master_key.encode("utf-8"),
                                _SALT,
                                600_000,
                                dklen=32,
                            )

    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)


def encrypt(value: str, master_key: str) -> str:
    return _get_fernet(master_key).encrypt( value.encode("utf-8") ).decode("utf-8")


def decrypt(value: str, master_key: str) -> str:
    return _get_fernet(master_key).decrypt( value.encode("utf-8") ).decode("utf-8")



if __name__ == "__main__":
    master_key=sys.argv[1]
    value=' '.join(sys.argv[2:])
    print(master_key)

    encrypted=encrypt(value, master_key)
    print(encrypted)

    original=decrypt(encrypted, master_key)
    print(original)
