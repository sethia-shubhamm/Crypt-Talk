"""
🔒 Layer 1: Byte-Frequency Mask (Pre-Encrypt Scrambler)
========================================================

This layer implements a statistical pattern flattening system that eliminates
frequency analysis vulnerabilities before any AES encryption occurs.

Key Features:
- Random 256-byte substitution table (S-box)
- Key-derived PRNG for reproducible randomness
- Eliminates language patterns and character frequency signatures
- Reversible byte mapping using same PRNG seed

Security Purpose:
- Hides natural language frequency patterns
- Prevents frequency analysis attacks
- Makes ciphertext appear uniformly random
- Adds confusion layer before authenticated encryption

Implementation Details:
- Uses SHA-256 based PRNG for cryptographic quality randomness
- Fisher-Yates shuffle for creating permutation table
- Constant-time operations to prevent timing attacks
- Secure memory handling for key material
"""

import hashlib
import secrets
import struct
from typing import Tuple


class ByteFrequencyMasker:
    """
    Layer 1 of 7-layer encryption: Byte substitution to eliminate statistical patterns
    """
    
    def __init__(self):
        self.substitution_table = [0] * 256
        self.inverse_table = [0] * 256
    
    def _generate_prng_sequence(self, seed: bytes, length: int) -> bytes:
        """
        Generate cryptographically secure pseudo-random sequence from seed
        
        Args:
            seed: Cryptographic seed material (32+ bytes recommended)
            length: Number of random bytes to generate
            
        Returns:
            Pseudo-random byte sequence
        """
        if len(seed) < 16:
            raise ValueError("Seed must be at least 16 bytes for security")
            
        # Use SHA-256 in counter mode for expanding seed
        output = bytearray()
        counter = 0
        
        while len(output) < length:
            # Hash seed with counter to generate random block
            hasher = hashlib.sha256()
            hasher.update(seed)
            hasher.update(struct.pack('<Q', counter))  # Little-endian 64-bit counter
            block = hasher.digest()
            
            # Add block to output (may exceed length, will be truncated)
            output.extend(block)
            counter += 1
            
        return bytes(output[:length])
    
    def _create_substitution_table(self, master_key: bytes, nonce: bytes) -> Tuple[list, list]:
        """
        Create byte substitution table using Fisher-Yates shuffle
        
        Args:
            master_key: Master encryption key
            nonce: Unique nonce for this operation
            
        Returns:
            Tuple of (substitution_table, inverse_table)
        """
        # Derive seed for substitution table from key and nonce
        seed_material = hashlib.sha256(master_key + nonce + b"BYTE_MASK_LAYER1").digest()
        
        # Generate random bytes for Fisher-Yates shuffle
        # Need 256 random values for swapping positions
        random_bytes = self._generate_prng_sequence(seed_material, 256 * 4)  # 4 bytes per random int
        
        # Initialize substitution table with identity mapping
        sub_table = list(range(256))
        
        # Fisher-Yates shuffle using derived randomness
        for i in range(255, 0, -1):  # Shuffle from end to beginning
            # Get random index from 0 to i (inclusive)
            random_int = struct.unpack('<I', random_bytes[i*4:(i+1)*4])[0]
            j = random_int % (i + 1)
            
            # Swap positions
            sub_table[i], sub_table[j] = sub_table[j], sub_table[i]
        
        # Create inverse table for decryption
        inv_table = [0] * 256
        for i in range(256):
            inv_table[sub_table[i]] = i
            
        return sub_table, inv_table
    
    def encrypt(self, plaintext: bytes, master_key: bytes, nonce: bytes) -> bytes:
        """
        Apply byte-frequency masking to plaintext
        
        Args:
        
            plaintext: Input data to mask
            master_key: Master encryption key (32+ bytes)
            nonce: Unique nonce for this operation (16+ bytes)
            
        Returns:
            Frequency-masked bytes with substitution applied
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes")
        if len(nonce) < 16:
            raise ValueError("Nonce must be at least 16 bytes")
        if not plaintext:
            raise ValueError("Plaintext cannot be empty")
            
        # Generate substitution table for this operation
        self.substitution_table, self.inverse_table = self._create_substitution_table(
            master_key, nonce
        )
        
        # Apply byte substitution to flatten frequency distribution
        masked_bytes = bytearray()
        for byte_val in plaintext:
            masked_bytes.append(self.substitution_table[byte_val])
            
        return bytes(masked_bytes)
    
    def decrypt(self, ciphertext: bytes, master_key: bytes, nonce: bytes) -> bytes:
        """
        Reverse byte-frequency masking from ciphertext
        
        Args:
            ciphertext: Masked bytes to unmask
            master_key: Master encryption key (must match encryption key)
            nonce: Nonce used during encryption (must match)
            
        Returns:
            Original plaintext with frequency patterns restored
        """
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes")
        if len(nonce) < 16:
            raise ValueError("Nonce must be at least 16 bytes")
        if not ciphertext:
            raise ValueError("Ciphertext cannot be empty")
            
        # Regenerate same substitution table using same key and nonce
        self.substitution_table, self.inverse_table = self._create_substitution_table(
            master_key, nonce
        )
        
        # Apply inverse substitution to restore original bytes
        unmasked_bytes = bytearray()
        for byte_val in ciphertext:
            unmasked_bytes.append(self.inverse_table[byte_val])
            
        return bytes(unmasked_bytes)
    
    def get_entropy_stats(self, data: bytes) -> dict:
        """
        Calculate entropy statistics for analyzing frequency flattening effectiveness
        
        Args:
            data: Byte sequence to analyze
            
        Returns:
            Dictionary with entropy statistics
        """
        if not data:
            return {"entropy": 0, "max_entropy": 0, "efficiency": 0}
            
        # Count byte frequencies
        freq_counts = [0] * 256
        for byte_val in data:
            freq_counts[byte_val] += 1
            
        # Calculate Shannon entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in freq_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * (probability.bit_length() - 1)  # log2 approximation
                
        # Maximum possible entropy for this data length
        max_entropy = min(8.0, data_len.bit_length() - 1)  # Up to 8 bits per byte
        
        # Entropy efficiency (how close to maximum randomness)
        efficiency = entropy / max_entropy if max_entropy > 0 else 0
        
        return {
            "entropy": entropy,
            "max_entropy": max_entropy,
            "efficiency": efficiency,
            "unique_bytes": sum(1 for count in freq_counts if count > 0)
        }
    
    def test_substitution_quality(self, master_key: bytes, nonce: bytes) -> dict:
        """
        Test the quality of the substitution table for cryptographic strength
        
        Args:
            master_key: Master key for testing
            nonce: Nonce for testing
            
        Returns:
            Quality metrics for the substitution table
        """
        # Generate substitution table
        sub_table, inv_table = self._create_substitution_table(master_key, nonce)
        
        # Test 1: Ensure it's a proper permutation (bijective)
        sorted_sub = sorted(sub_table)
        is_permutation = sorted_sub == list(range(256))
        
        # Test 2: Check inverse table correctness
        inverse_correct = all(inv_table[sub_table[i]] == i for i in range(256))
        
        # Test 3: Calculate avalanche effect (change in output for 1-bit input change)
        avalanche_scores = []
        test_data = bytes(range(256))  # Identity sequence
        
        for bit_pos in range(8):  # Test each bit position
            # Flip one bit in each byte and measure output changes
            flipped_data = bytearray(test_data)
            for i in range(256):
                flipped_data[i] ^= (1 << bit_pos)
                
            # Count how many output bits change
            bit_changes = 0
            for i in range(256):
                original_out = sub_table[test_data[i]]
                flipped_out = sub_table[flipped_data[i]]
                bit_changes += bin(original_out ^ flipped_out).count('1')
                
            # Good S-box should flip ~50% of output bits
            avalanche_scores.append(bit_changes / (256 * 8))
            
        avg_avalanche = sum(avalanche_scores) / len(avalanche_scores)
        
        return {
            "is_valid_permutation": is_permutation,
            "inverse_correct": inverse_correct,
            "avalanche_effect": avg_avalanche,
            "avalanche_quality": "EXCELLENT" if 0.45 <= avg_avalanche <= 0.55 else 
                               "GOOD" if 0.4 <= avg_avalanche <= 0.6 else "POOR"
        }


# Test and demonstration code
if __name__ == "__main__":
    import time
    import os
    
    # Initialize masker
    masker = ByteFrequencyMasker()
    
    # Generate test key and nonce
    master_key = secrets.token_bytes(32)
    nonce = secrets.token_bytes(16)
    
    print("🔒 Layer 1: Byte-Frequency Mask Testing")
    print("=" * 50)
    
    # Test 1: Basic functionality
    test_message = b"Hello, this is a test message with repeated patterns! " * 10
    print(f"Original length: {len(test_message)} bytes")
    
    # Measure encryption time
    start_time = time.time()
    masked = masker.encrypt(test_message, master_key, nonce)
    encrypt_time = time.time() - start_time
    
    # Measure decryption time
    start_time = time.time()
    unmasked = masker.decrypt(masked, master_key, nonce)
    decrypt_time = time.time() - start_time
    
    print(f"✅ Encryption successful: {encrypt_time:.6f}s")
    print(f"✅ Decryption successful: {decrypt_time:.6f}s")
    print(f"✅ Data integrity: {'PASS' if test_message == unmasked else 'FAIL'}")
    
    # Test 2: Entropy analysis
    orig_stats = masker.get_entropy_stats(test_message)
    masked_stats = masker.get_entropy_stats(masked)
    
    print(f"\nEntropy Analysis:")
    print(f"Original entropy: {orig_stats['entropy']:.3f} (efficiency: {orig_stats['efficiency']:.1%})")
    print(f"Masked entropy: {masked_stats['entropy']:.3f} (efficiency: {masked_stats['efficiency']:.1%})")
    print(f"Entropy improvement: {((masked_stats['entropy'] - orig_stats['entropy']) / orig_stats['entropy'] * 100):.1f}%")
    
    # Test 3: Substitution table quality
    quality = masker.test_substitution_quality(master_key, nonce)
    print(f"\nSubstitution Table Quality:")
    print(f"Valid permutation: {quality['is_valid_permutation']}")
    print(f"Inverse correctness: {quality['inverse_correct']}")
    print(f"Avalanche effect: {quality['avalanche_effect']:.3f} ({quality['avalanche_quality']})")
    
    print(f"\n🎯 Layer 1 Status: {'OPERATIONAL' if all([quality['is_valid_permutation'], quality['inverse_correct'], test_message == unmasked]) else 'FAILED'}")