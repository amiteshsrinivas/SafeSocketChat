import datetime
import os
from cryptography.hazmat.primitives import serialization

class MessageLogger:
    def __init__(self, client_name):
        self.client_name = client_name
        self.log_dir = "message_logs"
        self.ensure_log_directory()
        self.log_file = os.path.join(self.log_dir, f"{client_name}_messages.log")
        self.initialize_log_file()

    def ensure_log_directory(self):
        """Create logs directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def initialize_log_file(self):
        """Initialize the log file with headers"""
        with open(self.log_file, 'w') as f:
            f.write("=== Message Exchange Log ===\n")
            f.write(f"Client: {self.client_name}\n")
            f.write(f"Started at: {datetime.datetime.now()}\n")
            f.write("=" * 50 + "\n\n")

    def log_public_key(self, key, is_sent=True):
        """Log public key exchange"""
        timestamp = datetime.datetime.now()
        key_bytes = key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(self.log_file, 'a') as f:
            f.write(f"\n[{timestamp}] {'Sent' if is_sent else 'Received'} Public Key:\n")
            f.write(f"{key_bytes.decode()}\n")
            f.write("-" * 50 + "\n")

    def log_message(self, plain_text, cipher_text, shared_key, is_sent=True):
        """Log message exchange with encryption details"""
        timestamp = datetime.datetime.now()
        with open(self.log_file, 'a') as f:
            f.write(f"\n[{timestamp}] {'Sent' if is_sent else 'Received'} Message:\n")
            f.write(f"Plain Text: {plain_text}\n")
            f.write(f"Cipher Text (hex): {cipher_text.hex()}\n")
            f.write(f"Shared Key (hex): {shared_key.hex()}\n")
            f.write("-" * 50 + "\n")

    def log_error(self, error_message):
        """Log any errors that occur"""
        timestamp = datetime.datetime.now()
        with open(self.log_file, 'a') as f:
            f.write(f"\n[{timestamp}] ERROR:\n")
            f.write(f"{error_message}\n")
            f.write("-" * 50 + "\n") 