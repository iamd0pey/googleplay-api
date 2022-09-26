from cryptography.fernet import Fernet

import os
import base64

ENCRYPTION_KEY_FILE = os.environ["ENCRYPTION_KEY_FILE"]

def generate_encryption_key():
    key = Fernet.generate_key()

    if os.path.exists(ENCRYPTION_KEY_FILE):
        return None

    with open(ENCRYPTION_KEY_FILE, "wb") as file:
        file.write(key)
        return True

    return False

def load_encryption_key():
    if not os.path.exists(ENCRYPTION_KEY_FILE):
        return None

    with open(ENCRYPTION_KEY_FILE, "rb") as file:
        return file.read()

def encrypt_string(text):
    fernet = Fernet(load_encryption_key())
    encrypted_text = fernet.encrypt(text.encode())
    # print('type: ', type(encrypted_text))
    return encrypted_text

def base64_encrypt_string(text):
    encrypted_text = encrypt_string(text)
    encoded = base64.b64encode(encrypted_text).decode('utf-8')
    # print('encoded: ', encoded)
    # print('type: ', type(encoded))
    return encoded

def decrypt_string(encrypted_text):
    fernet = Fernet(load_encryption_key())
    return fernet.decrypt(encrypted_text)

def base64_decrypt_string(base64_encrypted_text):
    encrypted_text = base64.b64decode(base64_encrypted_text)
    decrypted_text = decrypt_string(encrypted_text).decode('utf-8')
    return decrypted_text
