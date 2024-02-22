import bcrypt

from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def hash(string: str) -> str:
    """Hashes a string using bcrypt"""
    salt = bcrypt.gensalt()
    byte_string = string.encode()

    return bcrypt.hashpw(byte_string, salt).hex()


def verify_hash(hash: str, string: str) -> bool:
    """Returns true, if string matches the hash"""
    byte_string = string.encode()
    byte_hash = bytes.fromhex(hash)
    return bcrypt.checkpw(byte_string, byte_hash)


def generate_key(length: int = 30) -> str:
    """Generates a key that can be used in AES encryption"""
    return get_random_bytes(length).hex()


def generate_salt(length: int = 30) -> str:
    """Generates a salt that can be used with a key in encryption."""
    return get_random_bytes(length).hex()


def generate_iv(length: int = 16) -> str:
    """Generates a IV(initialization vector) for AES encryption, if length is 16(default)"""
    return get_random_bytes(length).hex()


def encrypt(plaintext: str, key: str, salt: str, iv: str) -> str:
    """Encryption based on AES.

    Args:
        plaintext (string): The plain text to use for encryption.
        key (string): The key to use in encryption.
        salt (string): The salt in hex format to protect the key in encryption.
        iv (string): The initialization vector in hex format to use in encryption.

    Returns:
        str: The cipher produced by AES.
    """
    byte_token = plaintext.encode("utf-8")
    byte_salt = bytes.fromhex(salt)
    byte_iv = bytes.fromhex(iv)

    protected_key = PBKDF2(key, byte_salt, dkLen=32)

    cipher_engine = AES.new(protected_key, AES.MODE_CBC, iv=byte_iv)
    cipher = cipher_engine.encrypt(pad(byte_token, AES.block_size))

    return cipher.hex()


def decrypt(cipher: str, key: str, salt: str, iv: str) -> str:
    """Decrypt cipher based on AES.

    Args:
        cipher (string): The cipher in hex format.
        key (string): The key used at encryption.
        salt (string): The salt in hex format that was used at encryption.
        iv (string): The initialization vector in hex format at encryption.

    Returns:
        str : The text used at encryption.
    """

    byte_token = bytes.fromhex(cipher)
    byte_salt = bytes.fromhex(salt)
    byte_iv = bytes.fromhex(iv)

    protected_key = PBKDF2(key, byte_salt, dkLen=32)

    cipher_engine = AES.new(protected_key, AES.MODE_CBC, iv=byte_iv)
    plaintext = unpad(cipher_engine.decrypt(byte_token), AES.block_size)

    return plaintext.decode()


if __name__ == "__main__":
    key = "password"
    salt = generate_salt()
    IV = generate_iv()

    cipher = encrypt("My very secret message", key, salt, IV)
    plain = decrypt(cipher, key, salt, IV)

    print(cipher, plain, sep="\n")
