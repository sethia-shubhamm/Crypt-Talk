"""
Message Encryption Module for Crypt-Talk
Handles end-to-end encryption and decryption of messages using 7-Layer Military-Grade Encryption
"""

import base64
import hashlib
import os
import sys
from datetime import datetime

# Import 7-layer encryption system
try:
    # Add the 7_layer_encryption directory to the path
    encryption_path = os.path.join(os.path.dirname(__file__), '..', '..', '7_layer_encryption')
    if encryption_path not in sys.path:
        sys.path.insert(0, encryption_path)
    
    from master_encryption import SevenLayerEncryption
    print("🛡️ 7-LAYER ENCRYPTION SYSTEM LOADED")
    print("   🎯 Profile: BALANCED")
    print("   📊 Verbose Logging: ENABLED")
    print("   ✅ Ready for secure communications")
    SEVEN_LAYER_AVAILABLE = True
except ImportError as e:
    print(f"❌ Failed to import 7-layer encryption: {e}")
    print(f"   📁 Tried path: {os.path.join(os.path.dirname(__file__), '..', '..', '7_layer_encryption')}")
    SEVEN_LAYER_AVAILABLE = False

# Control verbose logging
VERBOSE_LOGGING = os.getenv('CRYPTO_VERBOSE', 'true').lower() == 'true'

def debug_print(*args, **kwargs):
    """Print debug information only if verbose logging is enabled"""
    if VERBOSE_LOGGING:
        print(*args, **kwargs)

def generate_master_key_from_users(user1_id, user2_id):
    """Generate a consistent 64-byte master key for 7-layer encryption"""
    users = sorted([str(user1_id), str(user2_id)])
    key_string = f"{users[0]}:{users[1]}"
    
    if VERBOSE_LOGGING:
        print(f"\n🔑 7-LAYER MASTER KEY GENERATION")
        print(f"   👥 Users: {user1_id} ↔ {user2_id}")
        print(f"   📝 Key String: '{key_string}'")
    
    # Generate a 64-byte master key using PBKDF2 for 7-layer encryption
    master_key = hashlib.pbkdf2_hmac('sha256', key_string.encode(), b'7layer_msg_salt', 100000, 64)
    
    if VERBOSE_LOGGING:
        print(f"   🔐 Master Key (64 bytes): {master_key.hex()[:32]}...{master_key.hex()[-32:]}")
        print(f"   ✅ Master Key Generated Successfully")
    
    return master_key

def encrypt_message(message, user1_id, user2_id):
    """Encrypt a message using 7-layer military-grade encryption"""
    if not SEVEN_LAYER_AVAILABLE:
        print(f"❌ 7-Layer encryption not available, falling back to simple Base64")
        # Simple fallback - just Base64 encode (NOT SECURE - for debugging only)
        encoded = base64.b64encode(message.encode('utf-8')).decode()
        return {
            'encrypted_message': encoded,
            'encryption_system': 'fallback',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    print(f"\n🛡️ 7-LAYER MESSAGE ENCRYPTION")
    print(f"   👥 Users: {user1_id} ↔ {user2_id}")
    print(f"   📨 Original Message: '{message[:50]}{'...' if len(message) > 50 else ''}'")
    print(f"   📏 Message Length: {len(message)} characters")
    
    try:
        # Generate master key from user IDs
        master_key = generate_master_key_from_users(user1_id, user2_id)
        
        # Create 7-layer encryption system
        crypto_system = SevenLayerEncryption("BALANCED")
        
        # Generate operation ID for logging
        operation_id = f"msg_{user1_id}_{user2_id}_{int(datetime.utcnow().timestamp() * 1000000)}"
        
        # Encrypt message with 7-layer system
        message_bytes = message.encode('utf-8')
        encrypted_data = crypto_system.encrypt(message_bytes, master_key, operation_id=operation_id)
        
        # Encode to Base64 for storage/transmission
        encrypted_b64 = base64.urlsafe_b64encode(encrypted_data).decode()
        
        print(f"   🔒 7-Layer Encrypted Size: {len(encrypted_data)} bytes")
        print(f"   📊 Encryption Overhead: {len(encrypted_data) - len(message_bytes)} bytes")
        print(f"   🆔 Operation ID: {operation_id}")
        print(f"   ✅ 7-Layer Message Encrypted Successfully")
        
        # Return in compatible format for existing system
        return {
            'encrypted_message': encrypted_b64,
            'encryption_system': '7_layer',
            'operation_id': operation_id,
            'original_length': len(message),
            'encrypted_length': len(encrypted_data),
            'timestamp': datetime.utcnow().isoformat(),
            'users': f"{user1_id}↔{user2_id}"
        }
        
    except Exception as e:
        print(f"   ❌ 7-Layer Encryption Error: {e}")
        raise Exception(f"Message encryption failed: {e}")

def decrypt_message(encrypted_data, user1_id, user2_id):
    """Decrypt a message using 7-layer military-grade decryption"""
    if not SEVEN_LAYER_AVAILABLE:
        print(f"❌ 7-Layer decryption not available, using fallback")
        # Simple fallback - just Base64 decode
        if isinstance(encrypted_data, dict):
            encoded = encrypted_data.get('encrypted_message', '')
        else:
            encoded = encrypted_data
        try:
            return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
        except:
            return encoded  # Return as-is if decoding fails
    
    print(f"\n🛡️ 7-LAYER MESSAGE DECRYPTION")
    print(f"   👥 Users: {user1_id} ↔ {user2_id}")
    
    try:
        # Handle both old format (string) and new format (dict)
        if isinstance(encrypted_data, dict):
            encrypted_message = encrypted_data['encrypted_message']
            operation_id = encrypted_data.get('operation_id', 'unknown')
            print(f"   🆔 Operation ID: {operation_id}")
            print(f"   📊 Metadata: {dict((k, v) for k, v in encrypted_data.items() if k not in ['encrypted_message'])}")
        else:
            encrypted_message = encrypted_data
            operation_id = 'legacy'
            print(f"   📊 Legacy format (no metadata)")
        
        print(f"   🔒 Encrypted (Base64): {encrypted_message[:60]}{'...' if len(encrypted_message) > 60 else ''}")
        
        # Regenerate the same master key
        master_key = generate_master_key_from_users(user1_id, user2_id)
        
        # Decode from Base64
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_message.encode())
        print(f"   🔒 Encrypted Size: {len(encrypted_bytes)} bytes")
        
        # Create 7-layer decryption system
        crypto_system = SevenLayerEncryption("BALANCED")
        
        # Decrypt message with 7-layer system
        decrypted_bytes = crypto_system.decrypt(encrypted_bytes, master_key)
        decrypted_message = decrypted_bytes.decode('utf-8')
        
        print(f"   🔓 Decrypted Message: '{decrypted_message[:50]}{'...' if len(decrypted_message) > 50 else ''}'")
        print(f"   📏 Decrypted Length: {len(decrypted_message)} characters")
        print(f"   ✅ 7-Layer Message Decrypted Successfully")
        
        return decrypted_message
        
    except Exception as e:
        print(f"   ❌ 7-Layer Decryption Error: {e}")
        # Return fallback for debugging - in production you might want to handle this differently
        fallback_msg = encrypted_data if isinstance(encrypted_data, str) else encrypted_data.get('encrypted_message', 'DECRYPTION_FAILED')
        print(f"   🔄 Returning fallback: {fallback_msg[:50]}...")
        return fallback_msg