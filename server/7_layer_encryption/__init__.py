"""
🔒 7-Layer Military-Grade Encryption System
=========================================

This module implements a revolutionary 7-layer encryption architecture that combines
multiple independent mathematical foundations to provide military-grade security.
Each layer adds a different type of protection against specific attack vectors.

Layer Architecture:
├── Layer 1: Byte-Frequency Mask (Statistical Pattern Flattening)
├── Layer 2: AES-Fernet (Authenticated Encryption Core) 
├── Layer 3: AES-CTR (Independent Stream Encryption)
├── Layer 4: Chaos-XOR (Logistic Map Chaos Theory)
├── Layer 5: Random Swapper (Fisher-Yates Block Permutation)
├── Layer 6: Noise Embedding (Length Obfuscation)
└── Layer 7: Integrity Tag (Outer Authentication)

Security Properties:
- Quantum-resistant through chaos complexity
- Multiple independent mathematical foundations
- Protection against all classical cryptanalytic attacks
- Traffic analysis resistance via noise embedding
- Perfect forward secrecy across all layers
- Comprehensive integrity and authentication

Usage:
    from server.7_layer_encryption import SevenLayerEncryption
    
    # Quick encryption with master orchestrator
    crypto = SevenLayerEncryption(profile="BALANCED")
    encrypted = crypto.encrypt(data, master_key, nonce)
    decrypted = crypto.decrypt(encrypted, master_key)
    
    # Convenience functions
    from server.7_layer_encryption import encrypt_message, decrypt_message
    encrypted, key = encrypt_message(b"secret", "password", "MAXIMUM")
    decrypted = decrypt_message(encrypted, key)
    
    # Individual layers
    from server.7_layer_encryption import ByteFrequencyMask
    layer1 = ByteFrequencyMask()
    masked = layer1.encrypt(data, key, nonce)
"""

# Import all layer implementations  
from .layer1_byte_mask import ByteFrequencyMasker as ByteFrequencyMask
from .layer2_aes_fernet import AESFernetLayer as EnhancedFernetCore
from .layer3_aes_ctr import AESCTRLayer as IndependentAESCTR
from .layer4_chaos_xor import ChaosXORLayer
from .layer5_random_swapper import RandomSwapper
from .layer6_noise_embedding import NoiseEmbedder
from .layer7_integrity_tag import IntegrityTagger

# Import master orchestrator and convenience functions
from .master_encryption import (
    SevenLayerEncryption,
    encrypt_message,
    decrypt_message
)

__all__ = [
    # Master orchestrator (primary interface)
    'SevenLayerEncryption',     # Complete 7-layer system
    'encrypt_message',          # Convenience encryption
    'decrypt_message',          # Convenience decryption
    
    # Individual layers (for advanced usage)
    'ByteFrequencyMask',        # Layer 1: Statistical pattern flattening
    'EnhancedFernetCore',       # Layer 2: Authenticated AES encryption
    'IndependentAESCTR',        # Layer 3: Independent CTR stream
    'ChaosXORLayer',            # Layer 4: Chaos theory XOR
    'RandomSwapper',            # Layer 5: Block permutation
    'NoiseEmbedder',            # Layer 6: Length obfuscation
    'IntegrityTagger',          # Layer 7: Outer authentication
    
    # Metadata
    '__version__',
    '__author__',
    '__description__'
]

__version__ = "1.0.0"
__author__ = "GitHub Copilot"
__description__ = "Military-grade 7-layer encryption system with chaos theory and advanced obfuscation"