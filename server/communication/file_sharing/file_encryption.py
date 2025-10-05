"""
File Encryption Module for Crypt-Talk
Handles encryption and decryption of files and images using Fernet (AES-128)
Uses the same key derivation as message encryption for consistency
"""

from cryptography.fernet import Fernet
import base64
import hashlib
import binascii
from datetime import datetime

def generate_file_key_from_users(user1_id, user2_id):
    """Generate a consistent encryption key for files between two users"""
    users = sorted([str(user1_id), str(user2_id)])
    key_string = f"FILE:{users[0]}:{users[1]}"  # Different namespace from messages
    
    print(f"\n🔑 FILE KEY GENERATION")
    print(f"   👥 Users: {user1_id} ↔ {user2_id}")
    print(f"   📂 Key String: '{key_string}'")
    print(f"   🔢 Key String (hex): {key_string.encode().hex()}")
    print(f"   🏷️ Namespace: FILE (separate from messages)")
    
    # Generate a key using SHA-256 and encode it for Fernet
    key_hash = hashlib.sha256(key_string.encode()).digest()
    key_b64 = base64.urlsafe_b64encode(key_hash)
    
    print(f"   #️⃣ SHA-256 Hash (raw): {key_hash.hex()}")
    print(f"   🔐 Fernet Key (B64): {key_b64.decode()}")
    print(f"   ✅ File Key Generated Successfully")
    
    return key_b64

def encrypt_file_data(file_data, user1_id, user2_id, filename="unknown"):
    """Encrypt file binary data between two users"""
    try:
        print(f"\n🔐 FILE ENCRYPTION PROCESS")
        print(f"   📂 Filename: '{filename}'")
        print(f"   📏 Original Size: {len(file_data):,} bytes")
        print(f"   🔢 File Header (hex): {file_data[:20].hex()}{'...' if len(file_data) > 20 else ''}")
        
        # Create file hash for integrity verification
        file_hash_full = hashlib.sha256(file_data).hexdigest()
        file_hash_short = file_hash_full[:16]
        
        print(f"   #️⃣ File SHA-256 Hash: {file_hash_full}")
        print(f"   #️⃣ Hash (short): {file_hash_short}")
        
        key = generate_file_key_from_users(user1_id, user2_id)
        fernet = Fernet(key)
        
        # Encrypt the binary file data
        encrypted_data = fernet.encrypt(file_data)
        encrypted_b64 = base64.urlsafe_b64encode(encrypted_data).decode()
        
        print(f"   🔒 Encrypted (raw bytes): {encrypted_data[:30].hex()}{'...' if len(encrypted_data) > 30 else ''}")
        print(f"   🔒 Encrypted (Base64): {encrypted_b64[:80]}{'...' if len(encrypted_b64) > 80 else ''}")
        print(f"   📊 Encryption Overhead: {len(encrypted_data) - len(file_data):,} bytes")
        print(f"   📈 Size Increase: {((len(encrypted_data) / len(file_data) - 1) * 100):.1f}%")
        
        # Store encryption metadata for debugging and verification
        encryption_info = {
            'encrypted_data': encrypted_b64,
            'file_hash': file_hash_short,
            'file_hash_full': file_hash_full,
            'original_size': len(file_data),
            'encrypted_size': len(encrypted_data),
            'encryption_key_preview': key.decode()[:16] + "...",
            'filename': filename,
            'is_encrypted': True,
            'encrypted_at': datetime.utcnow().isoformat()
        }
        
        print(f"   ✅ File Encrypted Successfully: {filename}")
        
        return encryption_info
        
    except Exception as e:
        print(f"   ❌ File Encryption Error: {e}")
        return None

def decrypt_file_data(encrypted_info, user1_id, user2_id):
    """Decrypt file binary data between two users"""
    try:
        print(f"\n🔓 FILE DECRYPTION PROCESS")
        print(f"   👥 Users: {user1_id} ↔ {user2_id}")
        
        # Handle both old format (direct string) and new format (dict)
        if isinstance(encrypted_info, dict):
            encrypted_data_b64 = encrypted_info.get('encrypted_data')
            original_hash = encrypted_info.get('file_hash', '')
            original_hash_full = encrypted_info.get('file_hash_full', '')
            filename = encrypted_info.get('filename', 'unknown')
            original_size = encrypted_info.get('original_size', 0)
            print(f"   📊 Metadata: filename='{filename}', original_size={original_size:,}")
        else:
            # Fallback for old format
            encrypted_data_b64 = encrypted_info
            original_hash = ''
            original_hash_full = ''
            filename = 'legacy'
            original_size = 0
            print(f"   📊 Legacy format (no metadata)")
            
        if not encrypted_data_b64:
            raise ValueError("No encrypted data found")
        
        print(f"   🔒 Encrypted (Base64): {encrypted_data_b64[:80]}{'...' if len(encrypted_data_b64) > 80 else ''}")
        
        # Decode Base64 to get raw encrypted bytes
        encrypted_data = base64.urlsafe_b64decode(encrypted_data_b64.encode())
        print(f"   🔒 Encrypted (raw bytes): {encrypted_data[:30].hex()}{'...' if len(encrypted_data) > 30 else ''}")
        print(f"   📏 Encrypted Size: {len(encrypted_data):,} bytes")
        
        key = generate_file_key_from_users(user1_id, user2_id)
        fernet = Fernet(key)
        
        # Decrypt
        decrypted_data = fernet.decrypt(encrypted_data)
        print(f"   🔓 Decrypted (raw bytes): {decrypted_data[:20].hex()}{'...' if len(decrypted_data) > 20 else ''}")
        print(f"   📁 Decrypted Size: {len(decrypted_data):,} bytes")
        
        # Verify integrity if hash is available
        if original_hash:
            current_hash_full = hashlib.sha256(decrypted_data).hexdigest()
            current_hash_short = current_hash_full[:16]
            
            print(f"   #️⃣ Current Hash: {current_hash_full}")
            print(f"   #️⃣ Expected Hash: {original_hash_full if original_hash_full else 'Not available'}")
            
            if current_hash_short == original_hash:
                print(f"   ✅ File Integrity Verified: Hash matches ({original_hash})")
            else:
                print(f"   ⚠️ File Integrity Warning: Hash mismatch")
                print(f"      Got: {current_hash_short}, Expected: {original_hash}")
        else:
            print(f"   ⏭️ Integrity check skipped (no hash available)")
        
        # Verify size if available
        if original_size > 0 and len(decrypted_data) == original_size:
            print(f"   ✅ Size Verification: {len(decrypted_data):,} bytes (matches expected)")
        elif original_size > 0:
            print(f"   ⚠️ Size Mismatch: Got {len(decrypted_data):,}, expected {original_size:,}")
        
        print(f"   ✅ File Decrypted Successfully: {filename}")
        
        return decrypted_data
        
    except Exception as e:
        print(f"   ❌ File Decryption Error: {e}")
        print(f"   🔄 Returning fallback data")
        # Return original data if decryption fails (for backward compatibility)
        if isinstance(encrypted_info, dict):
            return None
        else:
            return encrypted_info

def encrypt_image_with_metadata(image_data, user1_id, user2_id, filename, content_type):
    """Encrypt image with additional metadata preservation"""
    try:
        print(f"\n🖼️ IMAGE ENCRYPTION WITH METADATA")
        print(f"   🖼️ Image: '{filename}'")
        print(f"   🏷️ Content Type: {content_type}")
        print(f"   📏 Image Size: {len(image_data):,} bytes")
        print(f"   🔢 Image Header (hex): {image_data[:16].hex()}")
        
        # Create metadata header
        metadata = {
            'content_type': content_type,
            'filename': filename,
            'original_size': len(image_data)
        }
        
        print(f"   📋 Metadata: {metadata}")
        
        # Combine metadata and image data
        metadata_str = str(metadata).encode('utf-8')
        metadata_length = len(metadata_str).to_bytes(4, byteorder='big')
        combined_data = metadata_length + metadata_str + image_data
        
        print(f"   📦 Metadata Size: {len(metadata_str)} bytes")
        print(f"   📦 Combined Size: {len(combined_data):,} bytes")
        print(f"   🔢 Combined Header (hex): {combined_data[:20].hex()}...")
        
        # Encrypt the combined data
        encryption_result = encrypt_file_data(combined_data, user1_id, user2_id, filename)
        
        if encryption_result:
            encryption_result['has_metadata'] = True
            encryption_result['content_type'] = content_type
            encryption_result['metadata_size'] = len(metadata_str)
            print(f"   ✅ Image with Metadata Encrypted Successfully")
        else:
            print(f"   ❌ Image Encryption Failed")
            
        return encryption_result
        
    except Exception as e:
        print(f"   ❌ Image Encryption Error: {e}")
        return None

def decrypt_image_with_metadata(encrypted_info, user1_id, user2_id):
    """Decrypt image and extract metadata"""
    try:
        print(f"\n🖼️ IMAGE DECRYPTION WITH METADATA")
        
        # Decrypt the combined data
        combined_data = decrypt_file_data(encrypted_info, user1_id, user2_id)
        
        if combined_data is None:
            print(f"   ❌ Combined data decryption failed")
            return None, None
            
        print(f"   📦 Combined Data Size: {len(combined_data):,} bytes")
        print(f"   🔢 Combined Header (hex): {combined_data[:20].hex()}...")
        
        # Check if this has metadata
        if isinstance(encrypted_info, dict) and encrypted_info.get('has_metadata'):
            print(f"   📋 Processing image with metadata...")
            
            # Extract metadata length
            metadata_length = int.from_bytes(combined_data[:4], byteorder='big')
            print(f"   📏 Metadata Length: {metadata_length} bytes")
            
            # Extract metadata
            metadata_bytes = combined_data[4:4+metadata_length]
            metadata = eval(metadata_bytes.decode('utf-8'))  # Note: eval is safe here with controlled data
            print(f"   📋 Extracted Metadata: {metadata}")
            
            # Extract image data
            image_data = combined_data[4+metadata_length:]
            print(f"   🖼️ Image Data Size: {len(image_data):,} bytes")
            print(f"   � Image Header (hex): {image_data[:16].hex()}")
            
            # Verify image size matches metadata
            if len(image_data) == metadata.get('original_size', 0):
                print(f"   ✅ Image Size Verified: {len(image_data):,} bytes")
            else:
                print(f"   ⚠️ Image Size Mismatch: Got {len(image_data):,}, expected {metadata.get('original_size', 0):,}")
            
            print(f"   ✅ Image with Metadata Decrypted: {metadata['filename']}")
            return image_data, metadata
        else:
            print(f"   📋 No metadata found, treating as raw image")
            # No metadata, return as-is
            fallback_metadata = {'content_type': 'application/octet-stream', 'filename': 'unknown'}
            print(f"   📋 Fallback Metadata: {fallback_metadata}")
            return combined_data, fallback_metadata
            
    except Exception as e:
        print(f"   ❌ Image Decryption Error: {e}")
        return None, None

def get_file_encryption_stats(mongo):
    """Get statistics about file encryption in the database"""
    try:
        total_files = mongo.db.files.count_documents({})
        encrypted_files = mongo.db.files.count_documents({"file_encryption.is_encrypted": True})
        unencrypted_files = total_files - encrypted_files
        
        # Calculate storage sizes
        pipeline = [
            {"$group": {
                "_id": None,
                "total_size": {"$sum": "$file_size"},
                "encrypted_count": {"$sum": {"$cond": [{"$exists": ["$file_encryption.is_encrypted"]}, 1, 0]}}
            }}
        ]
        
        stats = list(mongo.db.files.aggregate(pipeline))
        total_size = stats[0]["total_size"] if stats else 0
        
        return {
            'total_files': total_files,
            'encrypted_files': encrypted_files,
            'unencrypted_files': unencrypted_files,
            'encryption_percentage': round((encrypted_files / total_files * 100) if total_files > 0 else 0, 2),
            'total_storage_bytes': total_size,
            'total_storage_mb': round(total_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        print(f"📊 Stats error: {e}")
        return {
            'total_files': 0,
            'encrypted_files': 0,
            'unencrypted_files': 0,
            'encryption_percentage': 0,
            'total_storage_bytes': 0,
            'total_storage_mb': 0
        }

def migrate_existing_files_to_encryption(mongo, user1_id, user2_id, limit=10):
    """Migrate unencrypted files to encrypted format (run once)"""
    try:
        # Find unencrypted files between these users
        unencrypted_files = mongo.db.files.find({
            "users": {"$all": [ObjectId(user1_id), ObjectId(user2_id)]},
            "file_encryption": {"$exists": False}
        }).limit(limit)
        
        migrated_count = 0
        
        for file_doc in unencrypted_files:
            try:
                file_data = file_doc['file_data']
                filename = file_doc.get('original_filename', 'unknown')
                
                # Encrypt the file
                if file_doc.get('file_type') == 'image':
                    encryption_info = encrypt_image_with_metadata(
                        file_data, user1_id, user2_id, filename, 
                        file_doc.get('content_type', 'image/jpeg')
                    )
                else:
                    encryption_info = encrypt_file_data(file_data, user1_id, user2_id, filename)
                
                if encryption_info:
                    # Update the document with encrypted data
                    mongo.db.files.update_one(
                        {"_id": file_doc["_id"]},
                        {
                            "$set": {
                                "file_data": base64.b64decode(encryption_info['encrypted_data']),
                                "file_encryption": encryption_info,
                                "is_encrypted": True,
                                "migrated_at": datetime.utcnow()
                            }
                        }
                    )
                    migrated_count += 1
                    print(f"🔄 Migrated: {filename}")
                    
            except Exception as e:
                print(f"🔄 Migration error for file {file_doc.get('_id')}: {e}")
                continue
        
        print(f"🔄 Migration complete: {migrated_count} files encrypted")
        return migrated_count
        
    except Exception as e:
        print(f"🔄 Migration error: {e}")
        return 0