"""
Message Encryption Module for Crypt-Talk
Handles end-to-end encryption and decryption of messages using Fernet (AES 128)
"""

from cryptography.fernet import Fernet
import base64
import hashlib
import binascii
import os
from datetime import datetime

# Control verbose logging
VERBOSE_LOGGING = os.getenv('CRYPTO_VERBOSE', 'false').lower() == 'true'

def debug_print(*args, **kwargs):
    """Print debug information only if verbose logging is enabled"""
    if VERBOSE_LOGGING:
        print(*args, **kwargs)

def generate_key_from_users(user1_id, user2_id):
    """Generate a consistent encryption key for two users"""
    users = sorted([str(user1_id), str(user2_id)])
    key_string = f"{users[0]}:{users[1]}"
    
    if VERBOSE_LOGGING:
        print(f"\n🔑 MESSAGE KEY GENERATION")
        print(f"   👥 Users: {user1_id} ↔ {user2_id}")
        print(f"   📝 Key String: '{key_string}'")
        print(f"   🔢 Key String (hex): {key_string.encode().hex()}")
    
    # Generate a key using SHA-256 and encode it for Fernet
    key_hash = hashlib.sha256(key_string.encode()).digest()
    key_b64 = base64.urlsafe_b64encode(key_hash)
    
    if VERBOSE_LOGGING:
        print(f"   #️⃣ SHA-256 Hash (raw): {key_hash.hex()}")
        print(f"   🔐 Fernet Key (B64): {key_b64.decode()}")
        print(f"   ✅ Key Generated Successfully")
    
    return key_b64

def encrypt_message(message, user1_id, user2_id):
    """Encrypt a message between two users"""
    if VERBOSE_LOGGING:
        print(f"\n🔐 MESSAGE ENCRYPTION PROCESS")
    print(f"   📨 Original Message: '{message[:50]}{'...' if len(message) > 50 else ''}'")
    print(f"   📏 Message Length: {len(message)} characters")
    print(f"   🔢 Message (UTF-8 bytes): {message.encode()[:30].hex()}{'...' if len(message.encode()) > 30 else ''}")
    
    # Generate message hash for integrity
    message_bytes = message.encode()
    message_hash_full = hashlib.sha256(message_bytes).hexdigest()
    message_hash_short = message_hash_full[:12]
    
    print(f"   #️⃣ Message SHA-256 Hash: {message_hash_full}")
    print(f"   #️⃣ Hash (short): {message_hash_short}")
    
    key = generate_key_from_users(user1_id, user2_id)
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message_bytes)
    encrypted_b64 = base64.urlsafe_b64encode(encrypted_message).decode()
    
    print(f"   🔒 Encrypted (raw bytes): {encrypted_message[:40].hex()}{'...' if len(encrypted_message) > 40 else ''}")
    print(f"   🔒 Encrypted (Base64): {encrypted_b64[:60]}{'...' if len(encrypted_b64) > 60 else ''}")
    print(f"   📊 Encryption Overhead: {len(encrypted_message) - len(message_bytes)} bytes")
    print(f"   ✅ Message Encrypted Successfully")
    
    # Store encryption info for debugging
    key_display = key.decode()[:16] + "..."  # Show first 16 chars of key
    
    return {
        'encrypted_message': encrypted_b64,
        'encryption_key': key_display,
        'message_hash': message_hash_short,
        'original_length': len(message),
        'encrypted_length': len(encrypted_message),
        'timestamp': datetime.utcnow().isoformat()
    }

def decrypt_message(encrypted_data, user1_id, user2_id):
    """Decrypt a message between two users"""
    try:
        print(f"\n🔓 MESSAGE DECRYPTION PROCESS")
        print(f"   👥 Users: {user1_id} ↔ {user2_id}")
        
        # Handle both old format (string) and new format (dict)
        if isinstance(encrypted_data, dict):
            encrypted_message = encrypted_data['encrypted_message']
            print(f"   📊 Metadata: {dict((k, v) for k, v in encrypted_data.items() if k != 'encrypted_message')}")
        else:
            encrypted_message = encrypted_data
            print(f"   📊 Legacy format (no metadata)")
            
        print(f"   🔒 Encrypted (Base64): {encrypted_message[:60]}{'...' if len(encrypted_message) > 60 else ''}")
        
        # Decode Base64 to get raw encrypted bytes
        decoded_message = base64.urlsafe_b64decode(encrypted_message.encode())
        print(f"   🔒 Encrypted (raw bytes): {decoded_message[:40].hex()}{'...' if len(decoded_message) > 40 else ''}")
        
        key = generate_key_from_users(user1_id, user2_id)
        fernet = Fernet(key)
        decrypted_bytes = fernet.decrypt(decoded_message)
        decrypted_message = decrypted_bytes.decode()
        
        print(f"   🔓 Decrypted (UTF-8 bytes): {decrypted_bytes[:30].hex()}{'...' if len(decrypted_bytes) > 30 else ''}")
        print(f"   📨 Decrypted Message: '{decrypted_message[:50]}{'...' if len(decrypted_message) > 50 else ''}'")
        print(f"   📏 Decrypted Length: {len(decrypted_message)} characters")
        
        # Verify integrity if hash is available
        if isinstance(encrypted_data, dict) and 'message_hash' in encrypted_data:
            current_hash = hashlib.sha256(decrypted_bytes).hexdigest()[:12]
            original_hash = encrypted_data['message_hash']
            if current_hash == original_hash:
                print(f"   ✅ Integrity Verified: Hash matches ({original_hash})")
            else:
                print(f"   ⚠️ Integrity Warning: Hash mismatch (got {current_hash}, expected {original_hash})")
        
        print(f"   ✅ Message Decrypted Successfully")
        return decrypted_message
        
    except Exception as e:
        print(f"   ❌ Decryption Error: {e}")
        print(f"   🔄 Returning original data as fallback")
        return encrypted_data if isinstance(encrypted_data, str) else encrypted_data.get('encrypted_message', '')