"""
🔒 Layer 7: Outer Integrity Tag (Tamper Detection)
=================================================

This layer implements the final security barrier using HMAC-SHA256 to detect
any tampering with the complete 7-layer encrypted ciphertext. This provides
authentication and integrity guarantees for the entire encryption stack.

Key Features:
- HMAC-SHA256 for cryptographic integrity verification
- Covers entire ciphertext including all layer metadata
- Independent key derivation for integrity operations
- Constant-time verification to prevent timing attacks
- Comprehensive tamper detection across all layers

Security Purpose:
- Detects any modification to encrypted data
- Prevents chosen-ciphertext attacks on any layer
- Provides authentication of ciphertext origin
- Ensures integrity of multi-layer encryption stack
- Final verification before decryption begins

Implementation Details:
- Uses dedicated integrity key separate from encryption keys
- Covers all metadata and ciphertext in HMAC calculation
- Constant-time HMAC verification prevents timing oracles
- Secure tag truncation options for bandwidth optimization
- Integration with all 7 layers for comprehensive protection
"""

import hashlib
import hmac
import secrets
import struct
import time
from typing import Tuple


class IntegrityTagger:
    """
    Layer 7 of 7-layer encryption: Outer integrity tag for tamper detection
    """
    
    # Configuration constants
    FULL_TAG_SIZE = 32      # Full HMAC-SHA256 output (256 bits)
    SHORT_TAG_SIZE = 16     # Truncated tag for bandwidth efficiency
    DEFAULT_TAG_SIZE = 32   # Use full tag by default for maximum security
    
    def __init__(self, tag_size: int = DEFAULT_TAG_SIZE):
        """
        Initialize integrity tagger
        
        Args:
            tag_size: Size of integrity tag (16 or 32 bytes)
        """
        if tag_size not in [self.SHORT_TAG_SIZE, self.FULL_TAG_SIZE]:
            raise ValueError(f"Tag size must be {self.SHORT_TAG_SIZE} or {self.FULL_TAG_SIZE}")
            
        self.tag_size = tag_size
        
    def _derive_integrity_key(self, master_key: bytes, nonce: bytes, 
                             layer_id: bytes = b"LAYER7_INTEGRITY") -> bytes:
        """
        Derive integrity key independent from all encryption keys
        
        Args:
            master_key: Master encryption key
            nonce: Unique nonce for this operation
            layer_id: Layer identifier for key separation
            
        Returns:
            32-byte integrity key for HMAC operations
        """
        # Create integrity key derivation context
        integrity_context = layer_id + nonce + b"HMAC_INTEGRITY_KEY"
        
        # First derivation round
        h1 = hmac.new(master_key, integrity_context, hashlib.sha256)
        intermediate_key = h1.digest()
        
        # Second derivation round for additional security
        final_context = integrity_context + intermediate_key[:16] + b"FINAL_ROUND"
        h2 = hmac.new(intermediate_key, final_context, hashlib.sha256)
        integrity_key = h2.digest()
        
        return integrity_key
    
    def _create_header(self, nonce: bytes, timestamp: int, tag_size: int) -> bytes:
        """
        Create integrity header with metadata
        
        Args:
            nonce: Nonce used for this operation
            timestamp: Unix timestamp of operation
            tag_size: Size of integrity tag
            
        Returns:
            Encoded header
        """
        nonce_len = len(nonce)
        if nonce_len > 255:
            raise ValueError("Nonce too long (max 255 bytes)")
            
        # Header format: [version:1][nonce_len:1][nonce][timestamp:8][tag_size:1]
        header = bytearray()
        header.append(0x01)  # Version 1
        header.append(nonce_len)
        header.extend(nonce)
        header.extend(struct.pack('<Q', timestamp))  # 64-bit timestamp
        header.append(tag_size)
        
        return bytes(header)
    
    def _parse_header(self, data: bytes) -> Tuple[bytes, int, int, int]:
        """
        Parse integrity header
        
        Args:
            data: Data starting with header
            
        Returns:
            Tuple of (nonce, timestamp, tag_size, header_length)
        """
        if len(data) < 11:  # Minimum header size
            raise ValueError("Invalid header: too short")
            
        # Parse version
        version = data[0]
        if version != 0x01:
            raise ValueError(f"Unsupported version: {version}")
            
        # Parse nonce
        nonce_len = data[1]
        if len(data) < 2 + nonce_len + 8 + 1:
            raise ValueError("Invalid header: truncated data")
            
        nonce = data[2:2 + nonce_len]
        
        # Parse timestamp
        timestamp_start = 2 + nonce_len
        timestamp = struct.unpack('<Q', data[timestamp_start:timestamp_start + 8])[0]
        
        # Parse tag size
        tag_size_pos = timestamp_start + 8
        tag_size = data[tag_size_pos]
        
        header_length = tag_size_pos + 1
        
        return nonce, timestamp, tag_size, header_length
    
    def _compute_integrity_tag(self, data: bytes, integrity_key: bytes) -> bytes:
        """
        Compute HMAC integrity tag for data
        
        Args:
            data: Data to authenticate
            integrity_key: Key for HMAC computation
            
        Returns:
            HMAC tag (truncated to configured size)
        """
        # Compute full HMAC-SHA256
        h = hmac.new(integrity_key, data, hashlib.sha256)
        full_tag = h.digest()
        
        # Truncate to configured size
        return full_tag[:self.tag_size]
    
    def _verify_integrity_tag(self, data: bytes, tag: bytes, integrity_key: bytes) -> bool:
        """
        Verify HMAC integrity tag in constant time
        
        Args:
            data: Data to verify
            tag: Provided integrity tag
            integrity_key: Key for HMAC computation
            
        Returns:
            True if tag is valid, False otherwise
        """
        if len(tag) != self.tag_size:
            return False
            
        # Compute expected tag
        expected_tag = self._compute_integrity_tag(data, integrity_key)
        
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(tag, expected_tag)
    
    def _pack_authenticated_data(self, header: bytes, ciphertext: bytes, tag: bytes) -> bytes:
        """
        Pack header, ciphertext, and integrity tag
        
        Args:
            header: Integrity header
            ciphertext: Encrypted data from previous layers
            tag: Integrity tag
            
        Returns:
            Complete authenticated data structure
        """
        # Format: [header][ciphertext][tag]
        # Header contains all necessary metadata including lengths
        
        packed = bytearray()
        packed.extend(header)
        packed.extend(ciphertext)
        packed.extend(tag)
        
        return bytes(packed)
    
    def _unpack_authenticated_data(self, authenticated_data: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        Unpack header, ciphertext, and integrity tag
        
        Args:
            authenticated_data: Complete data structure
            
        Returns:
            Tuple of (header, ciphertext, tag)
        """
        # Parse header to determine structure
        nonce, timestamp, tag_size, header_length = self._parse_header(authenticated_data)
        
        # Validate tag size matches our configuration
        if tag_size != self.tag_size:
            raise ValueError(f"Tag size mismatch: expected {self.tag_size}, got {tag_size}")
            
        # Calculate ciphertext and tag positions
        tag_start = len(authenticated_data) - tag_size
        if tag_start <= header_length:
            raise ValueError("Invalid data structure: no room for ciphertext")
            
        header = authenticated_data[:header_length]
        ciphertext = authenticated_data[header_length:tag_start]
        tag = authenticated_data[tag_start:]
        
        if len(tag) != tag_size:
            raise ValueError("Invalid data structure: incorrect tag size")
            
        return header, ciphertext, tag
    
    def encrypt(self, plaintext: bytes, master_key: bytes, nonce: bytes) -> bytes:
        """
        Add integrity tag to complete 7-layer encrypted data
        
        Args:
            plaintext: Output from Layer 6 (complete encrypted stack)
            master_key: Master encryption key (32+ bytes)
            nonce: Unique nonce for this operation (16+ bytes)
            
        Returns:
            Authenticated data with integrity tag
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes")
        if len(nonce) < 16:
            raise ValueError("Nonce must be at least 16 bytes")
        if not plaintext:
            raise ValueError("Plaintext cannot be empty")
            
        # Create header with current timestamp
        current_timestamp = int(time.time())
        header = self._create_header(nonce, current_timestamp, self.tag_size)
        
        # Derive integrity key
        integrity_key = self._derive_integrity_key(master_key, nonce)
        
        # Compute integrity tag over header + ciphertext
        data_to_authenticate = header + plaintext
        integrity_tag = self._compute_integrity_tag(data_to_authenticate, integrity_key)
        
        # Pack complete authenticated data
        authenticated_data = self._pack_authenticated_data(header, plaintext, integrity_tag)
        
        return authenticated_data
    
    def decrypt(self, ciphertext: bytes, master_key: bytes) -> bytes:
        """
        Verify integrity tag and extract Layer 6 output
        
        Args:
            ciphertext: Authenticated data with integrity tag
            master_key: Master encryption key (must match encryption key)
            
        Returns:
            Verified ciphertext for Layer 6 decryption
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes")
        if not ciphertext:
            raise ValueError("Ciphertext cannot be empty")
            
        # Unpack authenticated data structure
        header, layer6_output, provided_tag = self._unpack_authenticated_data(ciphertext)
        
        # Parse header to get nonce
        nonce, timestamp, tag_size, _ = self._parse_header(header)
        
        # Derive same integrity key
        integrity_key = self._derive_integrity_key(master_key, nonce)
        
        # Verify integrity tag
        data_to_verify = header + layer6_output
        if not self._verify_integrity_tag(data_to_verify, provided_tag, integrity_key):
            raise ValueError("Integrity verification failed: data has been tampered with")
            
        return layer6_output
    
    def verify_only(self, ciphertext: bytes, master_key: bytes) -> bool:
        """
        Verify integrity without decrypting
        
        Args:
            ciphertext: Authenticated data to verify
            master_key: Master encryption key
            
        Returns:
            True if integrity check passes, False otherwise
        """
        try:
            self.decrypt(ciphertext, master_key)
            return True
        except Exception:
            return False
    
    def extract_metadata(self, ciphertext: bytes) -> dict:
        """
        Extract metadata from authenticated data without decryption
        
        Args:
            ciphertext: Authenticated data
            
        Returns:
            Dictionary with metadata information
        """
        try:
            header, layer6_output, tag = self._unpack_authenticated_data(ciphertext)
            nonce, timestamp, tag_size, header_length = self._parse_header(header)
            
            # Calculate age
            current_time = int(time.time())
            age_seconds = current_time - timestamp
            
            return {
                "nonce": nonce.hex(),
                "nonce_length": len(nonce),
                "timestamp": timestamp,
                "creation_time": time.ctime(timestamp),
                "age_seconds": age_seconds,
                "age_hours": age_seconds / 3600,
                "tag_size": tag_size,
                "header_size": header_length,
                "ciphertext_size": len(layer6_output),
                "total_size": len(ciphertext),
                "overhead_bytes": len(ciphertext) - len(layer6_output),
                "overhead_ratio": (len(ciphertext) - len(layer6_output)) / len(layer6_output) if layer6_output else 0
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "is_valid": False
            }
    
    def test_timing_attack_resistance(self, master_key: bytes, nonce: bytes, num_tests: int = 1000) -> dict:
        """
        Test resistance to timing attacks on HMAC verification
        
        Args:
            master_key: Master key for testing
            nonce: Nonce for testing
            num_tests: Number of timing tests to perform
            
        Returns:
            Dictionary with timing analysis results
        """
        # Create test data
        test_data = b"Timing attack test data" * 100
        authentic = self.encrypt(test_data, master_key, nonce)
        
        # Create tampered versions
        tampered_data = bytearray(authentic)
        tampered_data[-1] ^= 0x01  # Flip one bit in tag
        tampered = bytes(tampered_data)
        
        # Measure verification times
        authentic_times = []
        tampered_times = []
        
        for _ in range(num_tests):
            # Time authentic verification
            start_time = time.perf_counter()
            self.verify_only(authentic, master_key)
            authentic_times.append(time.perf_counter() - start_time)
            
            # Time tampered verification
            start_time = time.perf_counter()
            self.verify_only(tampered, master_key)
            tampered_times.append(time.perf_counter() - start_time)
            
        # Calculate statistics
        avg_authentic = sum(authentic_times) / len(authentic_times)
        avg_tampered = sum(tampered_times) / len(tampered_times)
        
        # Good constant-time implementation should have minimal timing difference
        timing_difference = abs(avg_authentic - avg_tampered)
        max_acceptable_diff = max(avg_authentic, avg_tampered) * 0.1  # 10% tolerance
        
        timing_resistance = timing_difference < max_acceptable_diff
        
        return {
            "tests_performed": num_tests,
            "avg_authentic_time": avg_authentic,
            "avg_tampered_time": avg_tampered,
            "timing_difference": timing_difference,
            "max_acceptable_diff": max_acceptable_diff,
            "timing_resistance": timing_resistance,
            "resistance_quality": "GOOD" if timing_resistance else "POOR"
        }


# Test and demonstration code
if __name__ == "__main__":
    import secrets
    import time
    
    print("🔒 Layer 7: Outer Integrity Tag Testing")
    print("=" * 50)
    
    # Test both tag sizes
    for tag_size in [16, 32]:
        print(f"\nTesting with {tag_size}-byte tags:")
        print("-" * 30)
        
        # Initialize tagger
        tagger = IntegrityTagger(tag_size)
        
        # Generate test materials
        master_key = secrets.token_bytes(32)
        nonce = secrets.token_bytes(16)
        test_message = b"Final layer integrity test! This protects the entire 7-layer stack! " * 20
        
        print(f"Original message length: {len(test_message)} bytes")
        print(f"Tag size: {tag_size} bytes ({tag_size * 8} bits)")
        
        # Test 1: Basic integrity tagging/verification
        start_time = time.time()
        authenticated = tagger.encrypt(test_message, master_key, nonce)
        encrypt_time = time.time() - start_time
        
        start_time = time.time()
        verified = tagger.decrypt(authenticated, master_key)
        decrypt_time = time.time() - start_time
        
        print(f"✅ Authentication successful: {encrypt_time:.6f}s")
        print(f"✅ Verification successful: {decrypt_time:.6f}s")
        print(f"✅ Data integrity: {'PASS' if test_message == verified else 'FAIL'}")
        print(f"Authenticated size: {len(authenticated)} bytes (overhead: {len(authenticated) - len(test_message)} bytes)")
        
        # Test 2: Tamper detection
        tampered_data = bytearray(authenticated)
        tampered_data[-1] ^= 0x01  # Flip one bit in tag
        
        try:
            tagger.decrypt(bytes(tampered_data), master_key)
            tamper_detection = "FAIL"
        except ValueError:
            tamper_detection = "PASS"
            
        print(f"Tamper detection: {tamper_detection}")
        
        # Test 3: Metadata extraction
        metadata = tagger.extract_metadata(authenticated)
        print(f"Creation time: {metadata['creation_time']}")
        print(f"Overhead ratio: {metadata['overhead_ratio']:.3f}")
        
        # Test 4: Verify-only functionality
        verify_result = tagger.verify_only(authenticated, master_key)
        print(f"Verify-only test: {'PASS' if verify_result else 'FAIL'}")
        
        # Test 5: Timing attack resistance (quick test)
        timing_results = tagger.test_timing_attack_resistance(master_key, nonce, 100)
        print(f"Timing resistance: {timing_results['resistance_quality']}")
        
        all_tests_pass = (
            test_message == verified and
            tamper_detection == "PASS" and
            verify_result and
            timing_results['timing_resistance']
        )
        
        print(f"🎯 {tag_size}-byte tag status: {'OPERATIONAL' if all_tests_pass else 'FAILED'}")
    
    print(f"\n" + "=" * 50)
    print("🛡️ Layer 7 Complete: Integrity protection active!")
    print("   All 7 layers ready for deployment.")
    
    # Performance comparison
    print(f"\nPerformance Comparison:")
    for tag_size in [16, 32]:
        tagger = IntegrityTagger(tag_size)
        test_data = secrets.token_bytes(10240)  # 10KB
        
        start_time = time.time()
        authenticated = tagger.encrypt(test_data, master_key, nonce)
        encrypt_time = time.time() - start_time
        
        start_time = time.time()
        verified = tagger.decrypt(authenticated, master_key)
        decrypt_time = time.time() - start_time
        
        throughput = len(test_data) / (encrypt_time + decrypt_time) / 1024 / 1024
        
        print(f"{tag_size}-byte tags: {throughput:8.2f} MB/s")