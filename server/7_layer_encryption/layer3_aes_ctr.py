"""
🔒 Layer 3: AES-CTR (Independent Stream Layer)
==============================================

This layer implements an additional AES-CTR encryption layer that operates independently
from Layer 2, providing extra confidentiality through stream cipher semantics and
defense against multi-layer cryptanalysis.

Key Features:
- AES-256 in CTR (Counter) mode for stream encryption
- Independent key derivation from Layer 2
- Cryptographically secure counter initialization
- Stream-based encryption for any data size
- Perfect parallelization capability

Security Purpose:
- Additional encryption layer with different algorithm mode
- Protection against single-layer cryptanalysis
- Different attack surface from CBC mode in Layer 2
- Stream cipher properties for real-time encryption
- Counter mode provides semantic security

Implementation Details:
- Uses cryptography library's AES-CTR implementation
- Independent nonce and key derivation per layer
- Secure counter initialization to prevent reuse
- Constant-time operations for side-channel resistance
- Memory-efficient streaming for large data
"""

import hashlib
import secrets
import struct
from typing import Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class AESCTRLayer:
    """
    Layer 3 of 7-layer encryption: Independent AES-CTR stream encryption
    """
    
    def __init__(self):
        self.backend = default_backend()
        
    def _derive_ctr_key(self, master_key: bytes, nonce: bytes, layer_id: bytes = b"LAYER3_AESCTR") -> bytes:
        """
        Derive AES-CTR key independent from other layers
        
        Args:
            master_key: Master encryption key
            nonce: Unique nonce for this operation
            layer_id: Layer identifier for key separation
            
        Returns:
            32-byte AES-256 key for CTR mode
        """
        # Create layer-specific key derivation context
        context = layer_id + nonce + b"AES256_CTR_KEY"
        
        # Use SHA-256 for key derivation
        key_material = hashlib.sha256(master_key + context).digest()
        
        # Double hash for additional security margin
        derived_key = hashlib.sha256(key_material + context[:16]).digest()
        
        return derived_key
    
    def _generate_ctr_iv(self, master_key: bytes, nonce: bytes, layer_id: bytes = b"LAYER3_AESCTR") -> bytes:
        """
        Generate cryptographically secure IV for CTR mode
        
        Args:
            master_key: Master encryption key
            nonce: Unique nonce for this operation
            layer_id: Layer identifier for IV separation
            
        Returns:
            16-byte IV for AES-CTR (12 bytes nonce + 4 bytes counter start)
        """
        # Create IV derivation context
        iv_context = layer_id + nonce + b"CTR_IV_GENERATION"
        
        # Derive IV material from master key and context
        iv_material = hashlib.sha256(master_key + iv_context).digest()
        
        # Take first 12 bytes for CTR nonce, last 4 bytes for counter initialization
        ctr_nonce = iv_material[:12]
        
        # Initialize counter with derived value (not zero for additional security)
        counter_init = struct.unpack('<I', iv_material[12:16])[0]
        counter_bytes = struct.pack('<I', counter_init)
        
        # Combine nonce and counter for full 16-byte IV
        full_iv = ctr_nonce + counter_bytes
        
        return full_iv
    
    def _create_ctr_cipher(self, key: bytes, iv: bytes) -> Cipher:
        """
        Create AES-CTR cipher instance
        
        Args:
            key: 32-byte AES-256 key
            iv: 16-byte IV (12-byte nonce + 4-byte counter)
            
        Returns:
            Configured AES-CTR cipher
        """
        # Extract nonce and initial counter from IV
        nonce = iv[:12]
        initial_value = struct.unpack('<I', iv[12:16])[0]
        
        # Create CTR mode with specified nonce and initial counter
        ctr_mode = modes.CTR(nonce + struct.pack('<I', initial_value))
        
        # Create cipher with AES-256 algorithm
        algorithm = algorithms.AES(key)
        cipher = Cipher(algorithm, ctr_mode, backend=self.backend)
        
        return cipher
    
    def _pack_ctr_data(self, iv: bytes, ciphertext: bytes) -> bytes:
        """
        Pack IV and ciphertext into single data structure
        
        Args:
            iv: 16-byte initialization vector
            ciphertext: Encrypted data
            
        Returns:
            Packed data: [iv_length:1][iv][ciphertext_length:4][ciphertext]
        """
        iv_len = len(iv)
        ct_len = len(ciphertext)
        
        if iv_len != 16:
            raise ValueError("IV must be exactly 16 bytes for AES-CTR")
        if ct_len > 0xFFFFFFFF:
            raise ValueError("Ciphertext too large (max 4GB)")
            
        # Pack data with length prefixes
        packed = bytearray()
        packed.append(iv_len)  # 1 byte: IV length (should always be 16)
        packed.extend(iv)      # 16 bytes: IV data
        packed.extend(struct.pack('<I', ct_len))  # 4 bytes: ciphertext length
        packed.extend(ciphertext)  # Variable: encrypted data
        
        return bytes(packed)
    
    def _unpack_ctr_data(self, packed_data: bytes) -> Tuple[bytes, bytes]:
        """
        Unpack IV and ciphertext from data structure
        
        Args:
            packed_data: Packed data structure
            
        Returns:
            Tuple of (iv, ciphertext)
        """
        if len(packed_data) < 21:  # Minimum: 1 + 16 + 4 = 21 bytes
            raise ValueError("Invalid packed data: too short")
            
        # Extract IV
        iv_len = packed_data[0]
        if iv_len != 16:
            raise ValueError(f"Invalid IV length: expected 16, got {iv_len}")
            
        iv = packed_data[1:17]  # Always 16 bytes for AES
        
        # Extract ciphertext length
        ct_len = struct.unpack('<I', packed_data[17:21])[0]
        
        # Extract ciphertext
        if len(packed_data) < 21 + ct_len:
            raise ValueError("Invalid packed data: truncated ciphertext")
            
        ciphertext = packed_data[21:21 + ct_len]
        
        return iv, ciphertext
    
    def encrypt(self, plaintext: bytes, master_key: bytes, nonce: bytes) -> bytes:
        """
        Encrypt plaintext using AES-CTR stream encryption
        
        Args:
            plaintext: Data to encrypt
            master_key: Master encryption key (32+ bytes)
            nonce: Unique nonce for this operation (16+ bytes)
            
        Returns:
            Packed CTR encrypted data with IV
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes")
        if len(nonce) < 16:
            raise ValueError("Nonce must be at least 16 bytes")
        if not plaintext:
            raise ValueError("Plaintext cannot be empty")
            
        # Derive independent key for CTR layer
        ctr_key = self._derive_ctr_key(master_key, nonce)
        
        # Generate secure IV for CTR mode
        iv = self._generate_ctr_iv(master_key, nonce)
        
        # Create CTR cipher
        cipher = self._create_ctr_cipher(ctr_key, iv)
        encryptor = cipher.encryptor()
        
        # Encrypt data (CTR mode doesn't need padding)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        # Pack IV and ciphertext
        packed_result = self._pack_ctr_data(iv, ciphertext)
        
        return packed_result
    
    def decrypt(self, ciphertext: bytes, master_key: bytes, nonce: bytes) -> bytes:
        """
        Decrypt ciphertext using AES-CTR stream decryption
        
        Args:
            ciphertext: Packed CTR encrypted data
            master_key: Master encryption key (must match encryption key)
            nonce: Nonce used during encryption (must match)
            
        Returns:
            Decrypted plaintext
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes")
        if len(nonce) < 16:
            raise ValueError("Nonce must be at least 16 bytes")
        if not ciphertext:
            raise ValueError("Ciphertext cannot be empty")
            
        # Unpack IV and encrypted data
        iv, encrypted_data = self._unpack_ctr_data(ciphertext)
        
        # Derive same CTR key
        ctr_key = self._derive_ctr_key(master_key, nonce)
        
        # Create CTR cipher with same IV
        cipher = self._create_ctr_cipher(ctr_key, iv)
        decryptor = cipher.decryptor()
        
        # Decrypt data (CTR mode decryption is same as encryption)
        plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
        
        return plaintext
    
    def encrypt_stream(self, data_stream, master_key: bytes, nonce: bytes, chunk_size: int = 8192):
        """
        Encrypt data in streaming fashion for large files
        
        Args:
            data_stream: Iterable yielding data chunks
            master_key: Master encryption key (32+ bytes)
            nonce: Unique nonce for this operation (16+ bytes)
            chunk_size: Size of chunks to process
            
        Yields:
            Encrypted data chunks
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes")
        if len(nonce) < 16:
            raise ValueError("Nonce must be at least 16 bytes")
            
        # Derive key and IV
        ctr_key = self._derive_ctr_key(master_key, nonce)
        iv = self._generate_ctr_iv(master_key, nonce)
        
        # Create cipher
        cipher = self._create_ctr_cipher(ctr_key, iv)
        encryptor = cipher.encryptor()
        
        # Yield IV first
        yield self._pack_ctr_data(iv, b'')[:21]  # Just header with IV
        
        # Process data stream
        for chunk in data_stream:
            if chunk:
                encrypted_chunk = encryptor.update(chunk)
                yield encrypted_chunk
                
        # Finalize
        final_chunk = encryptor.finalize()
        if final_chunk:
            yield final_chunk
    
    def get_stream_info(self, ciphertext: bytes) -> dict:
        """
        Get information about CTR encrypted stream
        
        Args:
            ciphertext: Packed CTR encrypted data
            
        Returns:
            Dictionary with stream information
        """
        try:
            iv, encrypted_data = self._unpack_ctr_data(ciphertext)
            
            # Extract counter information from IV
            nonce = iv[:12]
            initial_counter = struct.unpack('<I', iv[12:16])[0]
            
            # Calculate stream statistics
            data_blocks = (len(encrypted_data) + 15) // 16  # 16-byte AES blocks
            
            return {
                "iv_length": len(iv),
                "nonce": nonce.hex(),
                "initial_counter": initial_counter,
                "data_length": len(encrypted_data),
                "aes_blocks": data_blocks,
                "overhead_bytes": len(ciphertext) - len(encrypted_data),
                "is_stream": True,
                "cipher_mode": "AES-256-CTR"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "is_valid": False
            }
    
    def verify_key_independence(self, master_key1: bytes, master_key2: bytes, nonce: bytes) -> dict:
        """
        Verify key independence between different master keys
        
        Args:
            master_key1: First master key
            master_key2: Second master key (should be different)
            nonce: Common nonce for testing
            
        Returns:
            Dictionary with independence test results
        """
        # Derive keys from both master keys
        key1 = self._derive_ctr_key(master_key1, nonce)
        key2 = self._derive_ctr_key(master_key2, nonce)
        
        # Calculate Hamming distance (bit differences)
        key_diff = sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(key1, key2))
        total_bits = len(key1) * 8
        
        # Good key derivation should have ~50% bit differences
        independence_ratio = key_diff / total_bits
        
        # Test IV independence
        iv1 = self._generate_ctr_iv(master_key1, nonce)
        iv2 = self._generate_ctr_iv(master_key2, nonce)
        
        iv_diff = sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(iv1, iv2))
        iv_bits = len(iv1) * 8
        iv_independence = iv_diff / iv_bits
        
        return {
            "key_hamming_distance": key_diff,
            "key_independence_ratio": independence_ratio,
            "key_independence_quality": "EXCELLENT" if 0.4 <= independence_ratio <= 0.6 else
                                      "GOOD" if 0.3 <= independence_ratio <= 0.7 else "POOR",
            "iv_hamming_distance": iv_diff,
            "iv_independence_ratio": iv_independence,
            "overall_independence": "PASS" if independence_ratio > 0.3 and iv_independence > 0.3 else "FAIL"
        }


# Test and demonstration code
if __name__ == "__main__":
    import secrets
    import time
    
    # Initialize layer
    ctr_layer = AESCTRLayer()
    
    print("🔒 Layer 3: AES-CTR Stream Testing")
    print("=" * 50)
    
    # Generate test materials
    master_key = secrets.token_bytes(32)
    nonce = secrets.token_bytes(16)
    test_message = b"This is a test message for AES-CTR stream encryption! " * 50
    
    print(f"Original message length: {len(test_message)} bytes")
    
    # Test 1: Basic encryption/decryption
    start_time = time.time()
    encrypted = ctr_layer.encrypt(test_message, master_key, nonce)
    encrypt_time = time.time() - start_time
    
    start_time = time.time()
    decrypted = ctr_layer.decrypt(encrypted, master_key, nonce)
    decrypt_time = time.time() - start_time
    
    print(f"✅ Encryption successful: {encrypt_time:.6f}s")
    print(f"✅ Decryption successful: {decrypt_time:.6f}s")
    print(f"✅ Data integrity: {'PASS' if test_message == decrypted else 'FAIL'}")
    print(f"Encrypted size: {len(encrypted)} bytes (overhead: {len(encrypted) - len(test_message)} bytes)")
    
    # Test 2: Stream information
    stream_info = ctr_layer.get_stream_info(encrypted)
    print(f"\nStream Information:")
    print(f"Cipher mode: {stream_info['cipher_mode']}")
    print(f"AES blocks: {stream_info['aes_blocks']}")
    print(f"Initial counter: {stream_info['initial_counter']}")
    print(f"Overhead: {stream_info['overhead_bytes']} bytes")
    
    # Test 3: Key independence
    master_key2 = secrets.token_bytes(32)
    independence = ctr_layer.verify_key_independence(master_key, master_key2, nonce)
    print(f"\nKey Independence Test:")
    print(f"Key independence: {independence['key_independence_ratio']:.3f} ({independence['key_independence_quality']})")
    print(f"IV independence: {independence['iv_independence_ratio']:.3f}")
    print(f"Overall result: {independence['overall_independence']}")
    
    # Test 4: Stream encryption for large data
    large_data = secrets.token_bytes(1024 * 1024)  # 1MB test
    
    start_time = time.time()
    encrypted_large = ctr_layer.encrypt(large_data, master_key, nonce)
    encrypt_time_large = time.time() - start_time
    
    start_time = time.time()
    decrypted_large = ctr_layer.decrypt(encrypted_large, master_key, nonce)
    decrypt_time_large = time.time() - start_time
    
    throughput = len(large_data) / (encrypt_time_large + decrypt_time_large) / 1024 / 1024
    print(f"\nPerformance Test (1MB):")
    print(f"Encryption: {encrypt_time_large:.3f}s")
    print(f"Decryption: {decrypt_time_large:.3f}s")
    print(f"Throughput: {throughput:.2f} MB/s")
    print(f"Large data integrity: {'PASS' if large_data == decrypted_large else 'FAIL'}")
    
    # Test 5: Different nonces produce different outputs
    nonce2 = secrets.token_bytes(16)
    encrypted2 = ctr_layer.encrypt(test_message, master_key, nonce2)
    
    # Same plaintext + key, different nonce should give different ciphertext
    nonce_independence = encrypted != encrypted2
    print(f"Nonce independence: {'PASS' if nonce_independence else 'FAIL'}")
    
    print(f"\n🎯 Layer 3 Status: {'OPERATIONAL' if all([test_message == decrypted, large_data == decrypted_large, nonce_independence, independence['overall_independence'] == 'PASS']) else 'FAILED'}")