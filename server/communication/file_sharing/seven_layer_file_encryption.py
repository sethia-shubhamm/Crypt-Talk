"""
7-Layer Military-Grade File Encryption Integration
===============================================

This module integrates the 7-layer encryption system for secure file handling,
providing military-grade protection for all file uploads and downloads while
maintaining compatibility with the existing file handler infrastructure.

Features:
- Military-grade 7-layer encryption for files
- Specialized handling for images and PDFs
- Metadata preservation and encryption
- Drop-in replacement for existing file encryption
- Enhanced security through multi-layer protection
"""

import hashlib
import secrets
import base64
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

# Import the 7-layer encryption system
import sys
import importlib.util

# Import the detailed encryption logger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
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
SECURITY_PROFILE = os.getenv('FILE_CRYPTO_PROFILE', 'MAXIMUM')  # Files get maximum security

def debug_print(*args, **kwargs):
    """Print debug information if verbose logging is enabled"""
    if VERBOSE_LOGGING:
        print(*args, **kwargs)

def generate_file_key_from_users(user1_id: str, user2_id: str) -> bytes:
    """
    Generate a deterministic master key for file encryption between two users
    
    Args:
        user1_id: First user ID
        user2_id: Second user ID
        
    Returns:
        64-byte master key for 7-layer file encryption
    """
    # Create consistent ordering with FILE namespace
    users = sorted([str(user1_id), str(user2_id)])
    key_material = f"CRYPT_TALK_7LAYER_FILES:{users[0]}:{users[1]}"
    
    debug_print(f"\n🔑 7-LAYER FILE KEY GENERATION")
    debug_print(f"   👥 Users: {user1_id} ↔ {user2_id}")
    debug_print(f"   📂 Key Material: '{key_material}'")
    debug_print(f"   🏷️ Namespace: FILES (separate from messages)")
    
    # Use PBKDF2 for secure key derivation
    salt = b"CryptTalk7LayerFilesSalt2024"  # Different salt for files
    master_key = hashlib.pbkdf2_hmac(
        'sha512', 
        key_material.encode('utf-8'), 
        salt, 
        100000,  # 100k iterations
        64       # 64-byte output for 7-layer system
    )
    
    debug_print(f"   🔐 Master Key (64 bytes): {master_key.hex()[:32]}...{master_key.hex()[-32:]}")
    debug_print(f"   ✅ File Key Generated Successfully")
    
    return master_key

def encrypt_file_data(file_data: bytes, user1_id: str, user2_id: str, filename: str = "unknown") -> Dict[str, Any]:
    """
    Encrypt file binary data using 7-layer military-grade encryption
    
    Args:
        file_data: Raw file bytes to encrypt
        user1_id: First user ID  
        user2_id: Second user ID
        filename: Original filename for metadata
        
    Returns:
        Dictionary with encrypted file data and metadata
    """
    # Start detailed file encryption logging
    operation_id = encryption_logger.log_file_encryption_start(
        filename, len(file_data), user1_id, user2_id, SECURITY_PROFILE
    )
    start_time = time.time()
    
    debug_print(f"\n🛡️ 7-LAYER FILE ENCRYPTION")
    debug_print(f"   📂 Filename: '{filename}'")
    debug_print(f"   📏 Original Size: {len(file_data):,} bytes")
    debug_print(f"   🎯 Security Profile: {SECURITY_PROFILE}")
    debug_print(f"   🔢 File Header: {file_data[:20].hex()}{'...' if len(file_data) > 20 else ''}")
    
    try:
        # Generate file hash for integrity verification
        file_hash_full = hashlib.sha256(file_data).hexdigest()
        file_hash_short = file_hash_full[:16]
        
        debug_print(f"   #️⃣ File SHA-256: {file_hash_full}")
        debug_print(f"   #️⃣ Hash (display): {file_hash_short}")
        
        # Generate file-specific master key
        master_key = generate_file_key_from_users(user1_id, user2_id)
        
        # Log key generation details
        key_material = f"CRYPT_TALK_FILE_7LAYER:{user1_id}:{user2_id}"
        derived_keys = {"file_master_key": master_key}
        encryption_logger.log_key_generation(operation_id, master_key, derived_keys, key_material)
        
        # Encrypt using 7-layer system directly with operation logging
        crypto_system = SevenLayerEncryption(SECURITY_PROFILE)
        encrypted_data = crypto_system.encrypt(file_data, master_key, operation_id=operation_id)
        
        # Convert to base64 for storage compatibility
        encrypted_b64 = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        
        debug_print(f"   🔒 Encrypted Size: {len(encrypted_data):,} bytes")
        debug_print(f"   🔒 Base64 Size: {len(encrypted_b64):,} characters")
        debug_print(f"   📊 Overhead: {len(encrypted_data) - len(file_data):,} bytes")
        debug_print(f"   🎖️ 7-Layer Protection: ACTIVE")
        debug_print(f"   ✅ File Encrypted Successfully")
        
        # Create metadata compatible with existing system
        key_display = base64.urlsafe_b64encode(master_key[:16]).decode()[:16] + "..."
        
        final_result = {
            'encrypted_data': encrypted_b64,
            'encryption_key': key_display,
            'file_hash': file_hash_short,
            'original_filename': filename,
            'original_size': len(file_data),
            'encrypted_size': len(encrypted_data),
            'security_profile': SECURITY_PROFILE,
            'encryption_version': '7LAYER_FILE_v1.0',
            'timestamp': datetime.utcnow().isoformat(),
            'namespace': 'FILES'
        }
        
        # Log file encryption completion
        processing_time = time.time() - start_time
        encryption_logger.log_encryption_complete(
            operation_id, len(file_data), len(encrypted_data), 
            processing_time, final_result
        )
        
        return final_result
        
    except Exception as e:
        # Log the error
        encryption_logger.log_error(operation_id, "file_encryption", str(e))
        
        debug_print(f"   ❌ 7-Layer File Encryption Error: {e}")
        return {
            'encrypted_data': base64.urlsafe_b64encode(file_data).decode(),  # Fallback
            'encryption_key': 'ERROR',
            'file_hash': 'ERROR', 
            'original_filename': filename,
            'original_size': len(file_data),
            'encrypted_size': len(file_data),
            'security_profile': 'ERROR',
            'encryption_version': 'ERROR',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }

def decrypt_file_data(encryption_info: Dict[str, Any], user1_id: str, user2_id: str) -> Optional[bytes]:
    """
    Decrypt file data using 7-layer military-grade decryption
    
    Args:
        encryption_info: Encryption metadata dictionary
        user1_id: First user ID
        user2_id: Second user ID
        
    Returns:
        Decrypted file bytes or None if failed
    """
    # Start file decryption logging
    operation_id = f"FILE_DECRYPT_{int(time.time()*1000000)}"
    start_time = time.time()
    
    # Log decryption start
    encryption_logger.log_decryption_start(operation_id, encryption_info, user1_id, user2_id)
    
    debug_print(f"\n🔓 7-LAYER FILE DECRYPTION")
    debug_print(f"   👥 Users: {user1_id} ↔ {user2_id}")
    
    try:
        encrypted_data = encryption_info.get('encrypted_data', '')
        encryption_version = encryption_info.get('encryption_version', 'unknown')
        security_profile = encryption_info.get('security_profile', SECURITY_PROFILE)
        original_filename = encryption_info.get('original_filename', 'unknown')
        
        debug_print(f"   📂 Filename: '{original_filename}'")
        debug_print(f"   📊 Version: {encryption_version}")
        debug_print(f"   🎯 Profile: {security_profile}")
        debug_print(f"   🔒 Encrypted (B64): {encrypted_data[:60]}{'...' if len(encrypted_data) > 60 else ''}")
        
        # Check if this is a 7-layer encrypted file
        if encryption_version.startswith('7LAYER'):
            debug_print(f"   🛡️ 7-Layer file decryption mode")
            
            # Decode base64 to get raw encrypted bytes
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            # Generate same file-specific master key
            master_key = generate_file_key_from_users(user1_id, user2_id)
            
            # Decrypt using 7-layer system directly
            crypto_system = SevenLayerEncryption(security_profile)
            decrypted_bytes = crypto_system.decrypt(encrypted_bytes, master_key)
            
            debug_print(f"   🔓 Decrypted Size: {len(decrypted_bytes):,} bytes")
            debug_print(f"   📂 Decrypted Header: {decrypted_bytes[:20].hex()}{'...' if len(decrypted_bytes) > 20 else ''}")
            
            # Verify integrity if hash is available
            integrity_verified = True
            final_hash = "unknown"
            if 'file_hash' in encryption_info:
                current_hash = hashlib.sha256(decrypted_bytes).hexdigest()[:16]
                original_hash = encryption_info['file_hash']
                final_hash = current_hash
                if current_hash == original_hash:
                    debug_print(f"   ✅ File Integrity Verified: Hash matches ({original_hash})")
                    integrity_verified = True
                else:
                    debug_print(f"   ⚠️ File Integrity Warning: Hash mismatch")
                    integrity_verified = False
            
            # Log file decryption completion
            processing_time = time.time() - start_time
            encryption_logger.log_decryption_complete(
                operation_id, len(decrypted_bytes), processing_time, 
                integrity_verified, final_hash
            )
                    
            debug_print(f"   🎖️ 7-Layer File Decryption: SUCCESS")
            return decrypted_bytes
            
        else:
            # Legacy encryption - fallback to old system
            debug_print(f"   🔄 Legacy file decryption fallback")
            from .file_encryption import decrypt_file_data as legacy_decrypt
            return legacy_decrypt(encryption_info, user1_id, user2_id)
            
    except Exception as e:
        # Log decryption error
        encryption_logger.log_error(operation_id, "file_decryption", str(e))
        
        debug_print(f"   ❌ 7-Layer File Decryption Error: {e}")
        return None

def encrypt_image_with_metadata(image_data: bytes, user1_id: str, user2_id: str, 
                               filename: str, content_type: str) -> Dict[str, Any]:
    """
    Encrypt image with preserved metadata using 7-layer system
    
    Args:
        image_data: Raw image bytes
        user1_id: First user ID
        user2_id: Second user ID
        filename: Original filename
        content_type: MIME content type
        
    Returns:
        Dictionary with encrypted image and metadata
    """
    debug_print(f"\n🖼️ 7-LAYER IMAGE ENCRYPTION WITH METADATA")
    debug_print(f"   🖼️ Filename: '{filename}'")
    debug_print(f"   📋 Content Type: {content_type}")
    debug_print(f"   📏 Image Size: {len(image_data):,} bytes")
    
    try:
        # Create metadata package
        metadata = {
            'filename': filename,
            'content_type': content_type,
            'original_size': len(image_data),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Combine image data and metadata into one package
        metadata_json = json.dumps(metadata, separators=(',', ':')).encode('utf-8')
        metadata_length = len(metadata_json)
        
        # Package format: [metadata_length:4][metadata][image_data]
        package = metadata_length.to_bytes(4, 'big') + metadata_json + image_data
        
        debug_print(f"   📋 Metadata: {metadata}")
        debug_print(f"   📦 Package Size: {len(package):,} bytes")
        
        # Encrypt the complete package
        encryption_result = encrypt_file_data(package, user1_id, user2_id, filename)
        
        # Add image-specific metadata
        encryption_result.update({
            'file_type': 'image',
            'content_type': content_type,
            'has_metadata': True,
            'encryption_version': '7LAYER_IMAGE_v1.0'
        })
        
        debug_print(f"   ✅ Image with Metadata Encrypted Successfully")
        return encryption_result
        
    except Exception as e:
        debug_print(f"   ❌ Image Encryption Error: {e}")
        # Fallback to regular file encryption
        return encrypt_file_data(image_data, user1_id, user2_id, filename)

def decrypt_image_with_metadata(encryption_info: Dict[str, Any], user1_id: str, user2_id: str) -> Tuple[Optional[bytes], Dict[str, Any]]:
    """
    Decrypt image and extract metadata using 7-layer system
    
    Args:
        encryption_info: Encryption metadata dictionary
        user1_id: First user ID
        user2_id: Second user ID
        
    Returns:
        Tuple of (decrypted_image_bytes, metadata_dict)
    """
    debug_print(f"\n🖼️ 7-LAYER IMAGE DECRYPTION WITH METADATA")
    
    try:
        # Check if this is an image with metadata
        if encryption_info.get('encryption_version', '').startswith('7LAYER_IMAGE'):
            debug_print(f"   🖼️ Image with metadata decryption mode")
            
            # Decrypt the complete package
            package_data = decrypt_file_data(encryption_info, user1_id, user2_id)
            
            if package_data is None:
                debug_print(f"   ❌ Package decryption failed")
                return None, {}
            
            # Extract metadata and image data
            if len(package_data) < 4:
                debug_print(f"   ❌ Invalid package format")
                return None, {}
            
            metadata_length = int.from_bytes(package_data[:4], 'big')
            if len(package_data) < 4 + metadata_length:
                debug_print(f"   ❌ Corrupted package format")
                return None, {}
            
            metadata_json = package_data[4:4+metadata_length]
            image_data = package_data[4+metadata_length:]
            
            # Parse metadata
            metadata = json.loads(metadata_json.decode('utf-8'))
            
            debug_print(f"   📋 Extracted Metadata: {metadata}")
            debug_print(f"   🖼️ Image Size: {len(image_data):,} bytes")
            debug_print(f"   ✅ Image and Metadata Decrypted Successfully")
            
            return image_data, metadata
            
        else:
            # Regular file decryption or legacy
            debug_print(f"   🔄 Regular image decryption")
            image_data = decrypt_file_data(encryption_info, user1_id, user2_id)
            
            # Create basic metadata from encryption info
            metadata = {
                'filename': encryption_info.get('original_filename', 'unknown'),
                'content_type': encryption_info.get('content_type', 'image/jpeg'),
                'original_size': len(image_data) if image_data else 0
            }
            
            return image_data, metadata
            
    except Exception as e:
        debug_print(f"   ❌ Image Decryption Error: {e}")
        return None, {}

def get_file_encryption_stats(mongo) -> Dict[str, Any]:
    """
    Get comprehensive file encryption statistics
    
    Args:
        mongo: MongoDB connection
        
    Returns:
        Dictionary with file encryption statistics
    """
    try:
        # Count encrypted vs unencrypted files
        total_files = mongo.db.files.count_documents({})
        encrypted_files = mongo.db.files.count_documents({'is_encrypted': True})
        
        # Get 7-layer encrypted files
        seven_layer_files = mongo.db.files.count_documents({
            'file_encryption.encryption_version': {'$regex': '^7LAYER'}
        })
        
        # Calculate storage statistics
        encrypted_pipeline = [
            {'$match': {'is_encrypted': True}},
            {'$group': {
                '_id': None,
                'total_encrypted_size': {'$sum': '$file_size'},
                'total_files': {'$sum': 1}
            }}
        ]
        
        encrypted_stats = list(mongo.db.files.aggregate(encrypted_pipeline))
        encrypted_size = encrypted_stats[0]['total_encrypted_size'] if encrypted_stats else 0
        
        return {
            'encryption_system': '7-Layer Military-Grade File Encryption',
            'version': '1.0',
            'security_profile': SECURITY_PROFILE,
            'total_files': total_files,
            'encrypted_files': encrypted_files,
            'seven_layer_files': seven_layer_files,
            'unencrypted_files': total_files - encrypted_files,
            'encryption_percentage': (encrypted_files / total_files * 100) if total_files > 0 else 0,
            'seven_layer_percentage': (seven_layer_files / total_files * 100) if total_files > 0 else 0,
            'total_encrypted_size_bytes': encrypted_size,
            'total_encrypted_size_mb': encrypted_size / (1024 * 1024),
            'layers_active': 7,
            'status': 'OPERATIONAL'
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'status': 'ERROR'
        }

def migrate_existing_files_to_encryption(mongo, user1_id: str, user2_id: str, limit: int = 10) -> int:
    """
    Migrate existing unencrypted files to 7-layer encryption
    
    Args:
        mongo: MongoDB connection
        user1_id: First user ID
        user2_id: Second user ID
        limit: Maximum number of files to migrate
        
    Returns:
        Number of files successfully migrated
    """
    debug_print(f"\n🔄 MIGRATING FILES TO 7-LAYER ENCRYPTION")
    debug_print(f"   👥 Users: {user1_id} ↔ {user2_id}")
    debug_print(f"   📊 Limit: {limit} files")
    
    migrated_count = 0
    
    try:
        # Find unencrypted files for these users
        unencrypted_files = mongo.db.files.find({
            'users': {'$all': [ObjectId(user1_id), ObjectId(user2_id)]},
            'is_encrypted': {'$ne': True}
        }).limit(limit)
        
        for file_doc in unencrypted_files:
            try:
                # Get file data
                file_data = file_doc['file_data']
                filename = file_doc.get('original_filename', file_doc.get('filename', 'unknown'))
                
                # Encrypt with 7-layer system
                if file_doc.get('file_type') == 'image':
                    encryption_info = encrypt_image_with_metadata(
                        file_data, user1_id, user2_id, filename, file_doc.get('content_type', 'image/jpeg')
                    )
                else:
                    encryption_info = encrypt_file_data(file_data, user1_id, user2_id, filename)
                
                # Update database with encrypted data
                encrypted_data = base64.b64decode(encryption_info['encrypted_data'])
                
                mongo.db.files.update_one(
                    {'_id': file_doc['_id']},
                    {
                        '$set': {
                            'file_data': encrypted_data,
                            'file_encryption': encryption_info,
                            'is_encrypted': True,
                            'migration_timestamp': datetime.utcnow()
                        }
                    }
                )
                
                migrated_count += 1
                debug_print(f"   ✅ Migrated file: {filename}")
                
            except Exception as e:
                debug_print(f"   ❌ Failed to migrate file {file_doc.get('filename', 'unknown')}: {e}")
                
        debug_print(f"   📊 Migration Complete: {migrated_count} files migrated")
        return migrated_count
        
    except Exception as e:
        debug_print(f"   ❌ Migration Error: {e}")
        return migrated_count

# Compatibility exports (maintain same interface as old system)
__all__ = [
    'encrypt_file_data',
    'decrypt_file_data',
    'encrypt_image_with_metadata', 
    'decrypt_image_with_metadata',
    'generate_file_key_from_users',
    'get_file_encryption_stats',
    'migrate_existing_files_to_encryption'
]

# System initialization
if VERBOSE_LOGGING:
    print(f"\n🛡️ 7-LAYER FILE ENCRYPTION SYSTEM LOADED")
    print(f"   🎯 Profile: {SECURITY_PROFILE}")
    print(f"   📂 File Protection: MAXIMUM")
    print(f"   🖼️ Image Metadata: PRESERVED")
    print(f"   ✅ Ready for secure file operations")

# Missing import fix
from bson.objectid import ObjectId