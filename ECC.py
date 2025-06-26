# type: ignore[reportMissingImports]
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

def generate_key_pair():
    """Generate a new X25519 key pair"""
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return public_key, private_key

def serialize_public_key(public_key):
    """Convert public key to bytes for transmission"""
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

def deserialize_public_key(public_bytes):
    """Convert received bytes back to public key"""
    return x25519.X25519PublicKey.from_public_bytes(public_bytes)

def derive_shared_key(private_key, peer_public_key):
    """Derive a shared key using X25519"""
    shared_key = private_key.exchange(peer_public_key)
    
    # Use HKDF to derive a proper encryption key
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data'
    ).derive(shared_key)
    
    return derived_key

def encrypt_message(message, shared_key):
    """Encrypt a message using AES-GCM"""
    if not isinstance(message, str):
        raise TypeError("Input must be a string")
    
    # Convert message to bytes
    message_bytes = message.encode('utf-8')
    
    # Generate a random IV
    iv = os.urandom(12)
    
    # Create an encryptor
    encryptor = Cipher(
        algorithms.AES(shared_key),
        modes.GCM(iv)
    ).encryptor()
    
    # Encrypt the message
    ciphertext = encryptor.update(message_bytes) + encryptor.finalize()
    
    # Combine IV, ciphertext, and tag
    return iv + encryptor.tag + ciphertext

def decrypt_message(encrypted_data, shared_key):
    """Decrypt a message using AES-GCM"""
    if not isinstance(encrypted_data, bytes):
        raise TypeError("Input must be bytes")
    
    # Split the encrypted data into IV, tag, and ciphertext
    iv = encrypted_data[:12]
    tag = encrypted_data[12:28]
    ciphertext = encrypted_data[28:]
    
    # Create a decryptor
    decryptor = Cipher(
        algorithms.AES(shared_key),
        modes.GCM(iv, tag)
    ).decryptor()
    
    # Decrypt the message
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Convert back to string
    return plaintext.decode('utf-8')