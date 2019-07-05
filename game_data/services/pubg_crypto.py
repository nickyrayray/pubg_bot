import os
from cryptography.fernet import Fernet


def encrypt(s):
    if isinstance(s, str):
        s = s.encode()
    enc_bytes = _get_cipher().encrypt(s)
    return enc_bytes.decode()


def decrypt(s):
    if isinstance(s, str):
        s = s.encode()
    dec_bytes = _get_cipher().decrypt(s)
    return dec_bytes.decode()


def _get_cipher():
    key = os.environ.get('PUBG_SECRET_KEY')
    return Fernet(key)
