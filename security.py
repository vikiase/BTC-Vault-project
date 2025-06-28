import json
import base64
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken

def generate_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_json_to_file(data: dict, file_path: str, password: str):
    magic_key = 'asf52ccc87sf56+'
    salt = os.urandom(16)
    key = generate_key_from_password(password, salt)
    fernet = Fernet(key)

    data_with_magic_key = data.copy()
    data_with_magic_key['magic_key'] = magic_key

    json_data = json.dumps(data_with_magic_key).encode()
    encrypted_data = fernet.encrypt(json_data)

    with open(file_path, 'wb') as file:
        file.write(salt + encrypted_data)

def decrypt_json_from_file(file_path: str, password: str):
    magic_key = 'asf52ccc87sf56+'
    with open(file_path, 'rb') as file:
        file_content = file.read()

    salt = file_content[:16]
    encrypted_data = file_content[16:]

    key = generate_key_from_password(password, salt)
    fernet = Fernet(key)

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
        data = json.loads(decrypted_data.decode())

        if data.get('magic_key') != magic_key:
            raise ValueError("Invalid magic key in decrypted data.")
        del data['magic_key']
        return data
    except InvalidToken:
        print("Decryption failed. Invalid password or corrupted data.")