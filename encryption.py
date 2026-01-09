from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64
import os
import hashlib

def generate_key(key_size=32):
    """Generate random AES key"""
    return get_random_bytes(key_size)

def save_key(file_id, key, folder='keys'):
    """Save key to file"""
    os.makedirs(folder, exist_ok=True)
    key_path = os.path.join(folder, f"{file_id}.key")
    
    # Encode key in base64 for safe storage
    encoded_key = base64.b64encode(key).decode('utf-8')
    
    with open(key_path, 'w') as f:
        f.write(encoded_key)
    
    return key_path

def load_key(file_id, folder='keys'):
    """Load key from file"""
    key_path = os.path.join(folder, f"{file_id}.key")
    
    if not os.path.exists(key_path):
        return None
    
    with open(key_path, 'r') as f:
        encoded_key = f.read().strip()
    
    try:
        return base64.b64decode(encoded_key)
    except:
        return None

def encrypt_file(file_path, key):
    """
    Encrypt file with AES-256-GCM
    Returns: nonce(16) + tag(16) + ciphertext
    """
    # Read file
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    
    # Create cipher with GCM mode
    cipher = AES.new(key, AES.MODE_GCM)
    
    # Encrypt
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    
    # Combine nonce + tag + ciphertext
    encrypted_data = cipher.nonce + tag + ciphertext
    
    return encrypted_data

def decrypt_file_with_key(encrypted_path, key):
    """
    Decrypt file with provided key
    """
    # Read encrypted file
    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()
    
    # Extract components (first 16 bytes: nonce, next 16 bytes: tag, rest: ciphertext)
    if len(encrypted_data) < 32:
        raise ValueError("File too small to be encrypted with AES-GCM")
    
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    
    # Create cipher and decrypt
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext
    except (ValueError, KeyError) as e:
        print(f"Decryption failed: {e}")
        return None

def decrypt_file_direct(encrypted_data, key):
    """
    Decrypt data directly (for testing)
    """
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext
    except (ValueError, KeyError):
        return None

def derive_key_from_password(password, salt=None):
    """Derive AES key from password (optional)"""
    if salt is None:
        salt = get_random_bytes(16)
    
    key = PBKDF2(password, salt, dkLen=32, count=1000000)
    return key, salt

def get_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()

def verify_encryption(original_path, encrypted_path, key):
    """
    Verify that encryption/decryption works correctly
    """
    # Read original
    with open(original_path, 'rb') as f:
        original_data = f.read()
    
    # Decrypt
    decrypted_data = decrypt_file_with_key(encrypted_path, key)
    
    if decrypted_data is None:
        return False
    
    return original_data == decrypted_data