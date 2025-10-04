"""
Message Encryption Module for Crypt-Talk
Handles end-to-end encryption and decryption of messages using Fernet (AES 128)
"""

from cryptography.fernet import Fernet
import base64
import hashlib

def generate_key_from_users(user1_id, user2_id):
    """Generate a consistent encryption key for two users"""
    users = sorted([str(user1_id), str(user2_id)])
    key_string = f"{users[0]}:{users[1]}"
    # Generate a key using SHA-256 and encode it for Fernet
    key_hash = hashlib.sha256(key_string.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)

def encrypt_message(message, user1_id, user2_id):
    """Encrypt a message between two users"""
    key = generate_key_from_users(user1_id, user2_id)
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())
    encrypted_b64 = base64.urlsafe_b64encode(encrypted_message).decode()
    
    # Store encryption info for debugging
    key_display = key.decode()[:16] + "..."  # Show first 16 chars of key
    message_hash = hashlib.sha256(message.encode()).hexdigest()[:12]  # First 12 chars of message hash
    
    return {
        'encrypted_message': encrypted_b64,
        'encryption_key': key_display,
        'message_hash': message_hash,
        'original_length': len(message)
    }

def decrypt_message(encrypted_data, user1_id, user2_id):
    """Decrypt a message between two users"""
    try:
        # Handle both old format (string) and new format (dict)
        if isinstance(encrypted_data, dict):
            encrypted_message = encrypted_data['encrypted_message']
        else:
            encrypted_message = encrypted_data
            
        key = generate_key_from_users(user1_id, user2_id)
        fernet = Fernet(key)
        decoded_message = base64.urlsafe_b64decode(encrypted_message.encode())
        decrypted_message = fernet.decrypt(decoded_message)
        return decrypted_message.decode()
    except Exception as e:
        print(f"🔐 Decryption error: {e}")
        return encrypted_data if isinstance(encrypted_data, str) else encrypted_data.get('encrypted_message', '')  # Return original if decryption fails