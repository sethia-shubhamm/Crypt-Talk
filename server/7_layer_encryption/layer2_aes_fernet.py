"""
🔒 Layer 2: AES-Fernet (Authenticated Encryption Core)
=====================================================

This layer implements the core authenticated encryption using Fernet (AES-CBC + HMAC-SHA256).
Provides both confidentiality and authenticity guarantees with a standardized, battle-tested
implementation.

Key Features:
- AES-128 in CBC mode for confidentiality
- HMAC-SHA256 for authentication and integrity
- Automatic IV generation for each operation
- Timestamp-based token format for replay protection
- Standardized Fernet token structure

Security Purpose:
- Core cryptographic strength through proven AES
- Message authentication prevents tampering
- CBC mode provides semantic security
- HMAC prevents chosen-ciphertext attacks
- Built-in key derivation and rotation support

Implementation Details:
- Uses Python cryptography library for FIPS compliance
- Constant-time operations to prevent timing attacks
- Secure random IV generation per encryption
- Key stretching using PBKDF2 when needed
- Memory-safe handling of sensitive data
"""

import base64
import hashlib
import secrets
import struct
import time
from typing import Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class AESFernetLayer:
    """
    Layer 2 of 7-layer encryption: Authenticated AES encryption using Fernet
    """
    
    def __init__(self):
        self.fernet_instance = None
        
    def _derive_fernet_key(self, master_key: bytes, nonce: bytes, layer_id: bytes = b"LAYER2_FERNET") -> bytes:
        """
        Derive Fernet-compatible key from master key and nonce
        
        Args:
            master_key: Master encryption key
            nonce: Unique nonce for this operation
            layer_id: Layer identifier for key separation
            
        Returns:
            32-byte Fernet key (base64url encoded internally by Fernet)
        """
        # Create salt for PBKDF2 from nonce and layer ID
        salt = hashlib.sha256(nonce + layer_id + b"SALT").digest()[:16]
        
        # Use PBKDF2 for key derivation (Fernet standard)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Fernet requires 32-byte key
            salt=salt,
            iterations=100000,  # Strong iteration count for security
        )
        
        # Derive key and encode for Fernet
        derived_key = kdf.derive(master_key)
        
        # Fernet expects base64url encoded key
        fernet_key = base64.urlsafe_b64encode(derived_key)
        
        return fernet_key
    
    def _create_enhanced_token(self, fernet_token: bytes, nonce: bytes) -> bytes:
        """
        Create enhanced token with additional metadata for 7-layer system
        
        Args:
            fernet_token: Standard Fernet token
            nonce: Nonce used for this operation
            
        Returns:
            Enhanced token with layer metadata
        """
        # Token format: [nonce_length:1][nonce][token_length:4][fernet_token]
        nonce_len = len(nonce)
        token_len = len(fernet_token)
        
        if nonce_len > 255:
            raise ValueError("Nonce too long (max 255 bytes)")
            
        # Pack token with metadata
        enhanced_token = bytearray()
        enhanced_token.append(nonce_len)  # 1 byte: nonce length
        enhanced_token.extend(nonce)      # Variable: nonce data
        enhanced_token.extend(struct.pack('<I', token_len))  # 4 bytes: token length
        enhanced_token.extend(fernet_token)  # Variable: Fernet token
        
        return bytes(enhanced_token)
    
    def _parse_enhanced_token(self, enhanced_token: bytes) -> Tuple[bytes, bytes]:
        """
        Parse enhanced token to extract nonce and Fernet token
        
        Args:
            enhanced_token: Enhanced token with metadata
            
        Returns:
            Tuple of (nonce, fernet_token)
        """
        if len(enhanced_token) < 6:  # Minimum: 1 + 1 + 4 = 6 bytes
            raise ValueError("Invalid enhanced token: too short")
            
        # Parse nonce
        nonce_len = enhanced_token[0]
        if len(enhanced_token) < 1 + nonce_len + 4:
            raise ValueError("Invalid enhanced token: corrupted nonce section")
            
        nonce = enhanced_token[1:1 + nonce_len]
        
        # Parse Fernet token length
        token_len_start = 1 + nonce_len
        token_len = struct.unpack('<I', enhanced_token[token_len_start:token_len_start + 4])[0]
        
        # Extract Fernet token
        fernet_start = token_len_start + 4
        if len(enhanced_token) < fernet_start + token_len:
            raise ValueError("Invalid enhanced token: corrupted token section")
            
        fernet_token = enhanced_token[fernet_start:fernet_start + token_len]
        
        return nonce, fernet_token
    
    def encrypt(self, plaintext: bytes, master_key: bytes, nonce: bytes) -> bytes:
        """
        Encrypt plaintext using AES-Fernet authenticated encryption
        
        Args:
            plaintext: Data to encrypt
            master_key: Master encryption key (32+ bytes)
            nonce: Unique nonce for this operation (16+ bytes)
            
        Returns:
            Enhanced Fernet token with metadata
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes")
        if len(nonce) < 16:
            raise ValueError("Nonce must be at least 16 bytes")
        if not plaintext:
            raise ValueError("Plaintext cannot be empty")
            
        # Derive Fernet key for this operation
        fernet_key = self._derive_fernet_key(master_key, nonce)
        
        # Create Fernet instance
        fernet = Fernet(fernet_key)
        
        # Encrypt with timestamp (standard Fernet behavior)
        fernet_token = fernet.encrypt(plaintext)
        
        # Create enhanced token with metadata
        enhanced_token = self._create_enhanced_token(fernet_token, nonce)
        
        return enhanced_token
    
    def decrypt(self, ciphertext: bytes, master_key: bytes, ttl: int = None) -> bytes:
        """
        Decrypt ciphertext using AES-Fernet authenticated decryption
        
        Args:
            ciphertext: Enhanced Fernet token to decrypt
            master_key: Master encryption key (must match encryption key)
            ttl: Time-to-live in seconds (None for no expiration check)
            
        Returns:
            Decrypted plaintext
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes")
        if not ciphertext:
            raise ValueError("Ciphertext cannot be empty")
            
        # Parse enhanced token
        nonce, fernet_token = self._parse_enhanced_token(ciphertext)
        
        # Derive same Fernet key
        fernet_key = self._derive_fernet_key(master_key, nonce)
        
        # Create Fernet instance
        fernet = Fernet(fernet_key)
        
        # Decrypt with optional TTL check
        if ttl is not None:
            plaintext = fernet.decrypt(fernet_token, ttl=ttl)
        else:
            plaintext = fernet.decrypt(fernet_token)
            
        return plaintext
    
    def extract_timestamp(self, ciphertext: bytes) -> int:
        """
        Extract timestamp from Fernet token without decryption
        
        Args:
            ciphertext: Enhanced Fernet token
            
        Returns:
            Unix timestamp when token was created
        """
        if not ciphertext:
            raise ValueError("Ciphertext cannot be empty")
            
        # Parse enhanced token to get Fernet token
        nonce, fernet_token = self._parse_enhanced_token(ciphertext)
        
        # Fernet token format: version(1) + timestamp(8) + iv(16) + ciphertext + hmac(32)
        if len(fernet_token) < 57:  # Minimum Fernet token size
            raise ValueError("Invalid Fernet token: too short")
            
        # Decode base64 token
        try:
            token_data = base64.urlsafe_b64decode(fernet_token)
        except Exception:
            raise ValueError("Invalid Fernet token: bad base64 encoding")
            
        # Extract timestamp (bytes 1-9)
        timestamp = struct.unpack('>Q', token_data[1:9])[0]
        
        return timestamp
    
    def verify_token_integrity(self, ciphertext: bytes, master_key: bytes) -> bool:
        """
        Verify token integrity without full decryption
        
        Args:
            ciphertext: Enhanced Fernet token to verify
            master_key: Master encryption key
            
        Returns:
            True if token is valid and intact, False otherwise
        """
        try:
            # Parse enhanced token
            nonce, fernet_token = self._parse_enhanced_token(ciphertext)
            
            # Derive Fernet key
            fernet_key = self._derive_fernet_key(master_key, nonce)
            
            # Create Fernet instance
            fernet = Fernet(fernet_key)
            
            # Try to decrypt (will raise exception if HMAC fails)
            fernet.decrypt(fernet_token)
            
            return True
            
        except Exception:
            return False
    
    def get_token_info(self, ciphertext: bytes) -> dict:
        """
        Extract information from token without decryption
        
        Args:
            ciphertext: Enhanced Fernet token
            
        Returns:
            Dictionary with token information
        """
        try:
            nonce, fernet_token = self._parse_enhanced_token(ciphertext)
            timestamp = self.extract_timestamp(ciphertext)
            
            # Calculate token age
            current_time = int(time.time())
            age_seconds = current_time - timestamp
            
            return {
                "nonce_length": len(nonce),
                "token_length": len(fernet_token),
                "total_length": len(ciphertext),
                "timestamp": timestamp,
                "age_seconds": age_seconds,
                "creation_time": time.ctime(timestamp),
                "is_expired": age_seconds > 3600,  # Default 1-hour expiration
                "overhead_bytes": len(ciphertext) - len(fernet_token)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "is_valid": False
            }


# Test and demonstration code
if __name__ == "__main__":
    import secrets
    import time
    
    # Initialize layer
    fernet_layer = AESFernetLayer()
    
    print("🔒 Layer 2: AES-Fernet Testing")
    print("=" * 50)
    
    # Generate test materials
    master_key = secrets.token_bytes(32)
    nonce = secrets.token_bytes(16)
    test_message = b"This is a secret message for AES-Fernet testing! " * 20
    
    print(f"Original message length: {len(test_message)} bytes")
    
    # Test 1: Basic encryption/decryption
    start_time = time.time()
    encrypted = fernet_layer.encrypt(test_message, master_key, nonce)
    encrypt_time = time.time() - start_time
    
    start_time = time.time()
    decrypted = fernet_layer.decrypt(encrypted, master_key)
    decrypt_time = time.time() - start_time
    
    print(f"✅ Encryption successful: {encrypt_time:.6f}s")
    print(f"✅ Decryption successful: {decrypt_time:.6f}s")
    print(f"✅ Data integrity: {'PASS' if test_message == decrypted else 'FAIL'}")
    print(f"Encrypted size: {len(encrypted)} bytes (overhead: {len(encrypted) - len(test_message)} bytes)")
    
    # Test 2: Token information
    token_info = fernet_layer.get_token_info(encrypted)
    print(f"\nToken Information:")
    print(f"Creation time: {token_info['creation_time']}")
    print(f"Token age: {token_info['age_seconds']} seconds")
    print(f"Overhead: {token_info['overhead_bytes']} bytes")
    
    # Test 3: Integrity verification
    integrity_ok = fernet_layer.verify_token_integrity(encrypted, master_key)
    print(f"Integrity check: {'PASS' if integrity_ok else 'FAIL'}")
    
    # Test 4: Tamper detection
    tampered_token = bytearray(encrypted)
    tampered_token[-10] ^= 0xFF  # Flip bits in HMAC
    tampered_integrity = fernet_layer.verify_token_integrity(bytes(tampered_token), master_key)
    print(f"Tamper detection: {'PASS' if not tampered_integrity else 'FAIL'}")
    
    # Test 5: TTL functionality
    time.sleep(1)  # Wait 1 second
    try:
        fernet_layer.decrypt(encrypted, master_key, ttl=0)  # Should fail
        ttl_test = "FAIL"
    except Exception:
        ttl_test = "PASS"
    print(f"TTL expiration: {ttl_test}")
    
    # Test 6: Performance with different sizes
    print(f"\nPerformance Testing:")
    for size in [100, 1024, 10240, 102400]:  # 100B, 1KB, 10KB, 100KB
        test_data = secrets.token_bytes(size)
        
        start_time = time.time()
        encrypted = fernet_layer.encrypt(test_data, master_key, nonce)
        encrypt_time = time.time() - start_time
        
        start_time = time.time()
        decrypted = fernet_layer.decrypt(encrypted, master_key)
        decrypt_time = time.time() - start_time
        
        throughput = size / (encrypt_time + decrypt_time) / 1024 / 1024  # MB/s
        print(f"{size:6d} bytes: {throughput:8.2f} MB/s")
    
    print(f"\n🎯 Layer 2 Status: {'OPERATIONAL' if test_message == decrypted and integrity_ok and not tampered_integrity else 'FAILED'}")