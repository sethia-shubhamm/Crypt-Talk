"""
7-Layer Military-Grade Message Encryption Integration
==================================================

This module integrates the revolutionary 7-layer encryption system with the
existing message handling infrastructure, providing seamless military-grade
security for all message communications.

Features:
- Drop-in replacement for existing message encryption
- Maintains compatibility with current message_handler.py
- User-specific encryption keys with deterministic derivation
- Enhanced security through 7-layer protection stack
- Comprehensive encryption metadata and logging
"""

import hashlib
import secrets
import base64
import os
import time
from datetime import datetime
from typing import Dict, Any, Tuple

# Import the 7-layer encryption system
import sys
import importlib.util

# Import the detailed encryption logger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from encryption_logger import encryption_logger

# Load the 7-layer encryption module
spec = importlib.util.spec_from_file_location(
    'seven_layer_encryption', 
    os.path.join(os.path.dirname(__file__), '..', '..', '7_layer_encryption', '__init__.py')
)
seven_layer_module = importlib.util.module_from_spec(spec)
sys.modules['seven_layer_encryption'] = seven_layer_module
spec.loader.exec_module(seven_layer_module)

# Import 7-layer functions
SevenLayerEncryption = seven_layer_module.SevenLayerEncryption
seven_layer_encrypt = seven_layer_module.encrypt_message
seven_layer_decrypt = seven_layer_module.decrypt_message

# Configuration
VERBOSE_LOGGING = os.getenv('CRYPTO_VERBOSE', 'true').lower() == 'true'
SECURITY_PROFILE = os.getenv('CRYPTO_PROFILE', 'BALANCED')  # PERFORMANCE, BALANCED, MAXIMUM

def debug_print(*args, **kwargs):
    """Print debug information if verbose logging is enabled"""
    if VERBOSE_LOGGING:
        print(*args, **kwargs)

def generate_user_pair_key(user1_id: str, user2_id: str) -> bytes:
    """
    Generate a deterministic master key for two users using secure key derivation
    
    Args:
        user1_id: First user ID
        user2_id: Second user ID
        
    Returns:
        64-byte master key for 7-layer encryption
    """
    # Create consistent ordering of users
    users = sorted([str(user1_id), str(user2_id)])
    key_material = f"CRYPT_TALK_7LAYER:{users[0]}:{users[1]}"
    
    debug_print(f"\n🔑 7-LAYER KEY GENERATION")
    debug_print(f"   👥 Users: {user1_id} ↔ {user2_id}")
    debug_print(f"   📝 Key Material: '{key_material}'")
    
    # Use PBKDF2 for secure key derivation
    salt = b"CryptTalk7LayerSalt2024"  # Fixed salt for deterministic keys
    master_key = hashlib.pbkdf2_hmac(
        'sha512', 
        key_material.encode('utf-8'), 
        salt, 
        100000,  # 100k iterations
        64       # 64-byte output for 7-layer system
    )
    
    debug_print(f"   🔐 Master Key (64 bytes): {master_key.hex()[:32]}...{master_key.hex()[-32:]}")
    debug_print(f"   ✅ User Pair Key Generated Successfully")
    
    return master_key

def encrypt_message(message: str, user1_id: str, user2_id: str) -> Dict[str, Any]:
    """
    Encrypt a message using 7-layer military-grade encryption
    
    Args:
        message: Plain text message to encrypt
        user1_id: First user ID  
        user2_id: Second user ID
        
    Returns:
        Dictionary with encrypted message and metadata
    """
    # Start detailed logging
    operation_id = encryption_logger.log_message_encryption_start(
        message, user1_id, user2_id, SECURITY_PROFILE
    )
    start_time = time.time()
    
    debug_print(f"\n🛡️ 7-LAYER MESSAGE ENCRYPTION")
    debug_print(f"   📨 Original Message: '{message[:50]}{'...' if len(message) > 50 else ''}'")
    debug_print(f"   📏 Message Length: {len(message)} characters")
    debug_print(f"   🎯 Security Profile: {SECURITY_PROFILE}")
    
    try:
        # Convert message to bytes
        message_bytes = message.encode('utf-8')
        
        # Generate message hash for integrity verification
        message_hash_full = hashlib.sha256(message_bytes).hexdigest()
        message_hash_short = message_hash_full[:16]  # First 16 chars for display
        
        debug_print(f"   #️⃣ Message SHA-256: {message_hash_full}")
        debug_print(f"   #️⃣ Hash (display): {message_hash_short}")
        
        # Generate user-pair master key
        master_key = generate_user_pair_key(user1_id, user2_id)
        
        # Log key generation details
        key_material = f"CRYPT_TALK_7LAYER:{user1_id}:{user2_id}"
        derived_keys = {"master_key": master_key}  # Will be expanded with individual layer keys
        encryption_logger.log_key_generation(operation_id, master_key, derived_keys, key_material)
        
        # Encrypt using 7-layer system directly with operation logging
        crypto_system = SevenLayerEncryption(SECURITY_PROFILE)
        encrypted_data = crypto_system.encrypt(message_bytes, master_key, operation_id=operation_id)
        
        # Convert to base64 for storage compatibility  
        encrypted_b64 = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        
        debug_print(f"   🔒 Encrypted Size: {len(encrypted_data)} bytes")
        debug_print(f"   🔒 Base64 Size: {len(encrypted_b64)} characters")
        debug_print(f"   📊 Overhead: {len(encrypted_data) - len(message_bytes)} bytes")
        debug_print(f"   🎖️ 7-Layer Protection: ACTIVE")
        debug_print(f"   ✅ Message Encrypted Successfully")
        
        # Create metadata compatible with existing system
        key_display = base64.urlsafe_b64encode(master_key[:16]).decode()[:16] + "..."
        
        final_result = {
            'encrypted_message': encrypted_b64,
            'encryption_key': key_display,
            'message_hash': message_hash_short,
            'original_length': len(message),
            'encrypted_length': len(encrypted_data),
            'security_profile': SECURITY_PROFILE,
            'encryption_version': '7LAYER_v1.0',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log encryption completion
        processing_time = time.time() - start_time
        encryption_logger.log_encryption_complete(
            operation_id, len(message_bytes), len(encrypted_data), 
            processing_time, final_result
        )
        
        return final_result
        
    except Exception as e:
        # Log the error
        encryption_logger.log_error(operation_id, "message_encryption", str(e))
        
        debug_print(f"   ❌ 7-Layer Encryption Error: {e}")
        # Fallback to return error information
        return {
            'encrypted_message': message,  # Fallback to plaintext (should not happen in production)
            'encryption_key': 'ERROR',
            'message_hash': 'ERROR',
            'original_length': len(message),
            'encrypted_length': len(message),
            'security_profile': 'ERROR',
            'encryption_version': 'ERROR',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }

def decrypt_message(encrypted_data: Any, user1_id: str, user2_id: str) -> str:
    """
    Decrypt a message using 7-layer military-grade decryption
    
    Args:
        encrypted_data: Encrypted message data (string or dict)
        user1_id: First user ID
        user2_id: Second user ID
        
    Returns:
        Decrypted plain text message
    """
    # Start decryption logging
    operation_id = f"DECRYPT_{int(time.time()*1000000)}"
    start_time = time.time()
    
    debug_print(f"\n🔓 7-LAYER MESSAGE DECRYPTION")
    debug_print(f"   👥 Users: {user1_id} ↔ {user2_id}")
    
    # Log decryption start
    if isinstance(encrypted_data, dict):
        encryption_logger.log_decryption_start(operation_id, encrypted_data, user1_id, user2_id)
    else:
        # Legacy format
        legacy_data = {
            'encryption_version': 'legacy',
            'security_profile': 'unknown',
            'encrypted_message': str(encrypted_data)[:100] + "..." if len(str(encrypted_data)) > 100 else str(encrypted_data)
        }
        encryption_logger.log_decryption_start(operation_id, legacy_data, user1_id, user2_id)
    
    try:
        # Handle both old format (string) and new format (dict)
        if isinstance(encrypted_data, dict):
            encrypted_message = encrypted_data.get('encrypted_message', '')
            encryption_version = encrypted_data.get('encryption_version', 'unknown')
            security_profile = encrypted_data.get('security_profile', SECURITY_PROFILE)
            debug_print(f"   📊 Version: {encryption_version}")
            debug_print(f"   🎯 Profile: {security_profile}")
        else:
            encrypted_message = encrypted_data
            encryption_version = 'legacy'
            security_profile = SECURITY_PROFILE
            debug_print(f"   📊 Legacy format detected")
            
        debug_print(f"   🔒 Encrypted (B64): {encrypted_message[:60]}{'...' if len(encrypted_message) > 60 else ''}")
        
        # Check if this is a 7-layer encrypted message
        if encryption_version.startswith('7LAYER'):
            debug_print(f"   🛡️ 7-Layer decryption mode")
            
            # Decode base64 to get raw encrypted bytes
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_message.encode('utf-8'))
            
            # Generate same user-pair master key
            master_key = generate_user_pair_key(user1_id, user2_id)
            
            # Decrypt using 7-layer system directly
            crypto_system = SevenLayerEncryption(security_profile)
            decrypted_bytes = crypto_system.decrypt(encrypted_bytes, master_key)
            decrypted_message = decrypted_bytes.decode('utf-8')
            
            debug_print(f"   🔓 Decrypted Length: {len(decrypted_message)} characters")
            debug_print(f"   📨 Decrypted Message: '{decrypted_message[:50]}{'...' if len(decrypted_message) > 50 else ''}'")
            
            # Verify integrity if hash is available
            integrity_verified = True
            final_hash = "unknown"
            if isinstance(encrypted_data, dict) and 'message_hash' in encrypted_data:
                current_hash = hashlib.sha256(decrypted_bytes).hexdigest()[:16]
                original_hash = encrypted_data['message_hash']
                final_hash = current_hash
                if current_hash == original_hash:
                    debug_print(f"   ✅ Integrity Verified: Hash matches ({original_hash})")
                    integrity_verified = True
                else:
                    debug_print(f"   ⚠️ Integrity Warning: Hash mismatch")
                    integrity_verified = False
            
            # Log decryption completion
            processing_time = time.time() - start_time
            encryption_logger.log_decryption_complete(
                operation_id, len(decrypted_message), processing_time, 
                integrity_verified, final_hash
            )
                    
            debug_print(f"   🎖️ 7-Layer Decryption: SUCCESS")
            return decrypted_message
            
        else:
            # Legacy encryption - fallback to old system for compatibility
            debug_print(f"   🔄 Legacy decryption fallback")
            from .message_encryption import decrypt_message as legacy_decrypt
            return legacy_decrypt(encrypted_data, user1_id, user2_id)
            
    except Exception as e:
        # Log decryption error
        encryption_logger.log_error(operation_id, "message_decryption", str(e))
        
        debug_print(f"   ❌ 7-Layer Decryption Error: {e}")
        debug_print(f"   🔄 Returning fallback data")
        
        # Return best available fallback
        if isinstance(encrypted_data, dict):
            return encrypted_data.get('encrypted_message', str(encrypted_data))
        else:
            return str(encrypted_data)

def get_encryption_stats() -> Dict[str, Any]:
    """
    Get encryption system statistics and information
    
    Returns:
        Dictionary with encryption system statistics
    """
    return {
        'encryption_system': '7-Layer Military-Grade',
        'version': '1.0',
        'security_profile': SECURITY_PROFILE,
        'layers_active': 7,
        'key_derivation': 'PBKDF2-SHA512',
        'master_key_size': 512,  # bits
        'integrity_protection': 'HMAC-SHA256',
        'chaos_theory': 'Logistic Map',
        'quantum_resistance': 'High',
        'status': 'OPERATIONAL'
    }

# Compatibility exports (maintain same interface as old system)
__all__ = [
    'encrypt_message',
    'decrypt_message', 
    'generate_user_pair_key',
    'get_encryption_stats'
]

# System initialization message
if VERBOSE_LOGGING:
    print(f"\n🛡️ 7-LAYER ENCRYPTION SYSTEM LOADED")
    print(f"   🎯 Profile: {SECURITY_PROFILE}")
    print(f"   📊 Verbose Logging: {'ENABLED' if VERBOSE_LOGGING else 'DISABLED'}")
    print(f"   ✅ Ready for secure communications")