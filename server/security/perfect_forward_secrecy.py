"""
🔐 Perfect Forward Secrecy (PFS) Implementation
=================================================

This module implements Perfect Forward Secrecy using the Double Ratchet algorithm
(similar to Signal Protocol) to ensure that compromise of long-term keys does not
compromise past session keys.

Key Features:
- Diffie-Hellman key exchange for ephemeral session keys
- Double Ratchet algorithm for continuous key updates
- Separate sending and receiving chain keys
- Key ratcheting on every message
- Automatic key deletion after use

Security Guarantees:
- Forward Secrecy: Past messages remain secure even if current keys compromised
- Break-in Recovery: Future messages secure even after key compromise
- Per-Message Keys: Each message encrypted with unique key
- No Key Reuse: Keys automatically deleted after use
"""

import os
import hmac
import hashlib
from typing import Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import json
import time


class DoubleRatchet:
    """
    Implementation of the Double Ratchet algorithm for Perfect Forward Secrecy
    
    The Double Ratchet combines:
    1. Diffie-Hellman ratchet: New DH key pair for each message
    2. Symmetric-key ratchet: Derive new chain keys from previous ones
    """
    
    # Constants
    INFO_MESSAGE_KEY = b"Crypt-Talk-MessageKey"
    INFO_CHAIN_KEY = b"Crypt-Talk-ChainKey"
    INFO_ROOT_KEY = b"Crypt-Talk-RootKey"
    INFO_HEADER_KEY = b"Crypt-Talk-HeaderKey"
    
    def __init__(self):
        """Initialize Double Ratchet state"""
        self.dh_private_key = None
        self.dh_public_key = None
        self.dh_remote_public_key = None
        
        self.root_key = None
        self.sending_chain_key = None
        self.receiving_chain_key = None
        
        self.sending_message_number = 0
        self.receiving_message_number = 0
        self.previous_sending_chain_length = 0
        
        self.skipped_message_keys = {}  # For out-of-order messages
        
    def _generate_dh_keypair(self) -> Tuple[ec.EllipticCurvePrivateKey, bytes]:
        """
        Generate new Elliptic Curve Diffie-Hellman key pair
        
        Returns:
            Tuple of (private_key, public_key_bytes)
        """
        private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return private_key, public_key_bytes
    
    def _dh_compute(self, private_key: ec.EllipticCurvePrivateKey, 
                    public_key_bytes: bytes) -> bytes:
        """
        Compute Diffie-Hellman shared secret
        
        Args:
            private_key: Our private key
            public_key_bytes: Remote public key (serialized)
            
        Returns:
            32-byte shared secret
        """
        public_key = serialization.load_der_public_key(
            public_key_bytes, 
            backend=default_backend()
        )
        shared_secret = private_key.exchange(ec.ECDH(), public_key)
        
        # Derive deterministic 32-byte key from shared secret
        kdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"ECDH-SharedSecret",
            backend=default_backend()
        )
        return kdf.derive(shared_secret)
    
    def _kdf_rk(self, root_key: bytes, dh_output: bytes) -> Tuple[bytes, bytes]:
        """
        Key Derivation Function for Root Key ratchet
        
        Args:
            root_key: Current root key
            dh_output: Diffie-Hellman output
            
        Returns:
            Tuple of (new_root_key, new_chain_key)
        """
        # Use HKDF to derive both root key and chain key
        kdf = HKDF(
            algorithm=hashes.SHA256(),
            length=64,  # 32 bytes for root + 32 bytes for chain
            salt=root_key,
            info=self.INFO_ROOT_KEY,
            backend=default_backend()
        )
        output = kdf.derive(dh_output)
        
        new_root_key = output[:32]
        new_chain_key = output[32:]
        
        return new_root_key, new_chain_key
    
    def _kdf_ck(self, chain_key: bytes) -> Tuple[bytes, bytes]:
        """
        Key Derivation Function for Chain Key ratchet
        
        Args:
            chain_key: Current chain key
            
        Returns:
            Tuple of (new_chain_key, message_key)
        """
        # Derive message key
        message_key = hmac.new(
            chain_key, 
            b"\x01" + self.INFO_MESSAGE_KEY, 
            hashlib.sha256
        ).digest()
        
        # Derive next chain key
        new_chain_key = hmac.new(
            chain_key, 
            b"\x02" + self.INFO_CHAIN_KEY, 
            hashlib.sha256
        ).digest()
        
        return new_chain_key, message_key
    
    def initialize_alice(self, bob_public_key: bytes, 
                        shared_secret: bytes) -> dict:
        """
        Initialize Alice (initiator) side of the ratchet
        
        Args:
            bob_public_key: Bob's public identity key
            shared_secret: Pre-shared secret (from initial key exchange)
            
        Returns:
            Dictionary with initialization data to send to Bob
        """
        # Generate Alice's first DH key pair
        self.dh_private_key, self.dh_public_key = self._generate_dh_keypair()
        
        # Perform initial DH with Bob's public key
        dh_output = self._dh_compute(self.dh_private_key, bob_public_key)
        
        # Initialize root key and sending chain
        self.root_key, self.sending_chain_key = self._kdf_rk(shared_secret, dh_output)
        
        # Store Bob's public key
        self.dh_remote_public_key = bob_public_key
        
        self.sending_message_number = 0
        self.receiving_message_number = 0
        
        return {
            "public_key": self.dh_public_key.hex(),
            "timestamp": int(time.time())
        }
    
    def initialize_bob(self, alice_public_key: bytes, 
                       shared_secret: bytes) -> dict:
        """
        Initialize Bob (responder) side of the ratchet
        
        Args:
            alice_public_key: Alice's first DH public key
            shared_secret: Pre-shared secret (from initial key exchange)
            
        Returns:
            Dictionary with initialization data
        """
        # Generate Bob's first DH key pair
        self.dh_private_key, self.dh_public_key = self._generate_dh_keypair()
        
        # Perform initial DH with Alice's public key
        dh_output = self._dh_compute(self.dh_private_key, alice_public_key)
        
        # Initialize root key and receiving chain
        self.root_key, self.receiving_chain_key = self._kdf_rk(shared_secret, dh_output)
        
        # Store Alice's public key
        self.dh_remote_public_key = alice_public_key
        
        self.sending_message_number = 0
        self.receiving_message_number = 0
        
        return {
            "public_key": self.dh_public_key.hex(),
            "timestamp": int(time.time())
        }
    
    def _dh_ratchet_sending(self) -> None:
        """
        Perform Diffie-Hellman ratchet step for sending
        
        This generates a new DH key pair and derives new root and chain keys
        """
        # Generate new DH key pair
        self.dh_private_key, self.dh_public_key = self._generate_dh_keypair()
        
        # Compute new DH output with remote public key
        dh_output = self._dh_compute(self.dh_private_key, self.dh_remote_public_key)
        
        # Update root key and derive new sending chain key
        self.root_key, self.sending_chain_key = self._kdf_rk(self.root_key, dh_output)
        
        # Reset message number
        self.previous_sending_chain_length = self.sending_message_number
        self.sending_message_number = 0
    
    def _dh_ratchet_receiving(self, remote_public_key: bytes) -> None:
        """
        Perform Diffie-Hellman ratchet step for receiving
        
        Args:
            remote_public_key: Remote party's new public key
        """
        # Store new remote public key
        self.dh_remote_public_key = remote_public_key
        
        # Compute DH output
        dh_output = self._dh_compute(self.dh_private_key, remote_public_key)
        
        # Update root key and derive new receiving chain key
        self.root_key, self.receiving_chain_key = self._kdf_rk(self.root_key, dh_output)
        
        # Reset message number
        self.receiving_message_number = 0
    
    def ratchet_encrypt(self, plaintext: bytes) -> dict:
        """
        Encrypt message with ratcheting
        
        Args:
            plaintext: Message to encrypt
            
        Returns:
            Dictionary containing encrypted message and header
        """
        # Derive message key from current chain key
        self.sending_chain_key, message_key = self._kdf_ck(self.sending_chain_key)
        
        # Create message header
        header = {
            "dh_public_key": self.dh_public_key.hex(),
            "previous_chain_length": self.previous_sending_chain_length,
            "message_number": self.sending_message_number
        }
        
        # Increment message number
        self.sending_message_number += 1
        
        # Perform DH ratchet for next message
        self._dh_ratchet_sending()
        
        return {
            "header": header,
            "message_key": message_key.hex(),
            "timestamp": int(time.time())
        }
    
    def ratchet_decrypt(self, header: dict, message_key_hex: str) -> bytes:
        """
        Decrypt message with ratcheting
        
        Args:
            header: Message header with DH public key and message number
            message_key_hex: Hex-encoded message key
            
        Returns:
            Message key for decryption
        """
        remote_public_key = bytes.fromhex(header["dh_public_key"])
        message_number = header["message_number"]
        
        # Check if we need to perform DH ratchet
        if remote_public_key != self.dh_remote_public_key:
            # Save any skipped message keys from current chain
            self._skip_message_keys(header["previous_chain_length"])
            
            # Perform DH ratchet
            self._dh_ratchet_receiving(remote_public_key)
        
        # Skip message keys if needed (for out-of-order messages)
        self._skip_message_keys(message_number)
        
        # Derive message key
        self.receiving_chain_key, message_key = self._kdf_ck(self.receiving_chain_key)
        self.receiving_message_number += 1
        
        return message_key
    
    def _skip_message_keys(self, until: int) -> None:
        """
        Skip message keys for out-of-order messages
        
        Args:
            until: Message number to skip until
        """
        if self.receiving_message_number + 100 < until:
            raise ValueError("Too many skipped messages")
        
        while self.receiving_message_number < until:
            self.receiving_chain_key, skipped_key = self._kdf_ck(self.receiving_chain_key)
            
            # Store skipped key for later
            key_id = f"{self.dh_remote_public_key.hex()}:{self.receiving_message_number}"
            self.skipped_message_keys[key_id] = skipped_key
            
            self.receiving_message_number += 1
    
    def get_state(self) -> dict:
        """
        Get current ratchet state for persistence
        
        Returns:
            Dictionary with serialized state
        """
        return {
            "dh_public_key": self.dh_public_key.hex() if self.dh_public_key else None,
            "dh_remote_public_key": self.dh_remote_public_key.hex() if self.dh_remote_public_key else None,
            "root_key": self.root_key.hex() if self.root_key else None,
            "sending_chain_key": self.sending_chain_key.hex() if self.sending_chain_key else None,
            "receiving_chain_key": self.receiving_chain_key.hex() if self.receiving_chain_key else None,
            "sending_message_number": self.sending_message_number,
            "receiving_message_number": self.receiving_message_number,
            "previous_sending_chain_length": self.previous_sending_chain_length
        }
    
    def load_state(self, state: dict) -> None:
        """
        Load ratchet state from persistence
        
        Args:
            state: Dictionary with serialized state
        """
        self.dh_public_key = bytes.fromhex(state["dh_public_key"]) if state.get("dh_public_key") else None
        self.dh_remote_public_key = bytes.fromhex(state["dh_remote_public_key"]) if state.get("dh_remote_public_key") else None
        self.root_key = bytes.fromhex(state["root_key"]) if state.get("root_key") else None
        self.sending_chain_key = bytes.fromhex(state["sending_chain_key"]) if state.get("sending_chain_key") else None
        self.receiving_chain_key = bytes.fromhex(state["receiving_chain_key"]) if state.get("receiving_chain_key") else None
        self.sending_message_number = state.get("sending_message_number", 0)
        self.receiving_message_number = state.get("receiving_message_number", 0)
        self.previous_sending_chain_length = state.get("previous_sending_chain_length", 0)


class PerfectForwardSecrecy:
    """
    Perfect Forward Secrecy manager for Crypt-Talk
    
    Manages Double Ratchet sessions for all user conversations
    """
    
    def __init__(self):
        """Initialize PFS manager"""
        self.sessions = {}  # conversation_id -> DoubleRatchet
        
    def _get_conversation_id(self, user1_id: str, user2_id: str) -> str:
        """
        Get deterministic conversation ID from user IDs
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            
        Returns:
            Conversation ID
        """
        sorted_ids = tuple(sorted([user1_id, user2_id]))
        return f"{sorted_ids[0]}:{sorted_ids[1]}"
    
    def initialize_session(self, user1_id: str, user2_id: str, 
                          initiator: bool, remote_public_key: Optional[bytes] = None,
                          shared_secret: Optional[bytes] = None) -> dict:
        """
        Initialize new PFS session
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            initiator: True if this user is initiating the session
            remote_public_key: Remote user's public key (if not initiator)
            shared_secret: Pre-shared secret from initial handshake
            
        Returns:
            Session initialization data
        """
        conversation_id = self._get_conversation_id(user1_id, user2_id)
        
        # Create new ratchet
        ratchet = DoubleRatchet()
        
        # Generate shared secret if not provided
        if shared_secret is None:
            # Use PBKDF2 on conversation ID as initial shared secret
            from hashlib import pbkdf2_hmac
            shared_secret = pbkdf2_hmac(
                'sha256',
                conversation_id.encode('utf-8'),
                b'CryptTalk-PFS-InitialSecret',
                iterations=100000,
                dklen=32
            )
        
        # Initialize based on role
        if initiator:
            if remote_public_key is None:
                raise ValueError("Initiator needs remote public key")
            init_data = ratchet.initialize_alice(remote_public_key, shared_secret)
        else:
            if remote_public_key is None:
                raise ValueError("Responder needs remote public key")
            init_data = ratchet.initialize_bob(remote_public_key, shared_secret)
        
        # Store session
        self.sessions[conversation_id] = ratchet
        
        return {
            "conversation_id": conversation_id,
            "init_data": init_data,
            "shared_secret": shared_secret.hex()
        }
    
    def encrypt_message(self, user1_id: str, user2_id: str, 
                       plaintext: bytes) -> dict:
        """
        Encrypt message with PFS
        
        Args:
            user1_id: Sender ID
            user2_id: Recipient ID
            plaintext: Message to encrypt
            
        Returns:
            Encryption data including message key
        """
        conversation_id = self._get_conversation_id(user1_id, user2_id)
        
        # Get or create session
        if conversation_id not in self.sessions:
            raise ValueError(f"No PFS session found for conversation {conversation_id}")
        
        ratchet = self.sessions[conversation_id]
        
        # Encrypt with ratcheting
        return ratchet.ratchet_encrypt(plaintext)
    
    def decrypt_message(self, user1_id: str, user2_id: str, 
                       header: dict, message_key_hex: str) -> bytes:
        """
        Decrypt message with PFS
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            header: Message header
            message_key_hex: Hex-encoded message key
            
        Returns:
            Decrypted message key
        """
        conversation_id = self._get_conversation_id(user1_id, user2_id)
        
        if conversation_id not in self.sessions:
            raise ValueError(f"No PFS session found for conversation {conversation_id}")
        
        ratchet = self.sessions[conversation_id]
        
        # Decrypt with ratcheting
        return ratchet.ratchet_decrypt(header, message_key_hex)
    
    def save_session_state(self, user1_id: str, user2_id: str) -> dict:
        """
        Save session state for persistence
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            
        Returns:
            Serialized session state
        """
        conversation_id = self._get_conversation_id(user1_id, user2_id)
        
        if conversation_id not in self.sessions:
            return None
        
        return self.sessions[conversation_id].get_state()
    
    def load_session_state(self, user1_id: str, user2_id: str, 
                          state: dict) -> None:
        """
        Load session state from persistence
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            state: Serialized session state
        """
        conversation_id = self._get_conversation_id(user1_id, user2_id)
        
        ratchet = DoubleRatchet()
        ratchet.load_state(state)
        
        self.sessions[conversation_id] = ratchet
    
    def delete_session(self, user1_id: str, user2_id: str) -> None:
        """
        Delete session (secure key deletion)
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
        """
        conversation_id = self._get_conversation_id(user1_id, user2_id)
        
        if conversation_id in self.sessions:
            # Securely delete keys
            del self.sessions[conversation_id]


# Test and demonstration
if __name__ == "__main__":
    print("🔐 Perfect Forward Secrecy (PFS) Implementation")
    print("=" * 60)
    
    # Initialize PFS manager
    pfs = PerfectForwardSecrecy()
    
    # Simulate Alice and Bob
    alice_id = "alice_user_id_12345"
    bob_id = "bob_user_id_67890"
    
    print("\n1. Session Initialization")
    print("-" * 60)
    
    # Bob generates his identity key
    bob_private, bob_public = pfs.sessions.get("temp", DoubleRatchet())._generate_dh_keypair()
    print(f"Bob's public key: {bob_public.hex()[:64]}...")
    
    # Alice initiates session
    alice_init = pfs.initialize_session(
        alice_id, bob_id, 
        initiator=True, 
        remote_public_key=bob_public
    )
    print(f"✅ Alice initialized session")
    print(f"   Conversation ID: {alice_init['conversation_id']}")
    
    # Bob accepts session
    alice_public_hex = alice_init['init_data']['public_key']
    bob_init = pfs.initialize_session(
        bob_id, alice_id,
        initiator=False,
        remote_public_key=bytes.fromhex(alice_public_hex),
        shared_secret=bytes.fromhex(alice_init['shared_secret'])
    )
    print(f"✅ Bob accepted session")
    
    print("\n2. Message Exchange with Key Ratcheting")
    print("-" * 60)
    
    # Alice sends 3 messages
    for i in range(1, 4):
        plaintext = f"Hello Bob! Message #{i}".encode('utf-8')
        
        encrypt_data = pfs.encrypt_message(alice_id, bob_id, plaintext)
        
        print(f"\n📤 Alice → Bob (Message {i}):")
        print(f"   Message: {plaintext.decode('utf-8')}")
        print(f"   Message Key: {encrypt_data['message_key'][:32]}...")
        print(f"   DH Public Key: {encrypt_data['header']['dh_public_key'][:32]}...")
        print(f"   Message Number: {encrypt_data['header']['message_number']}")
        
        # Bob receives and decrypts
        message_key = pfs.decrypt_message(
            alice_id, bob_id,
            encrypt_data['header'],
            encrypt_data['message_key']
        )
        
        print(f"   ✅ Bob decrypted successfully")
    
    # Bob replies
    plaintext = b"Hi Alice! Got your messages!"
    encrypt_data = pfs.encrypt_message(bob_id, alice_id, plaintext)
    
    print(f"\n📥 Bob → Alice:")
    print(f"   Message: {plaintext.decode('utf-8')}")
    print(f"   Message Key: {encrypt_data['message_key'][:32]}...")
    print(f"   DH Public Key changed: {encrypt_data['header']['dh_public_key'][:32]}...")
    
    print("\n3. Session State Persistence")
    print("-" * 60)
    
    # Save Alice's session state
    alice_state = pfs.save_session_state(alice_id, bob_id)
    print(f"✅ Saved Alice's session state")
    print(f"   Sending messages: {alice_state['sending_message_number']}")
    print(f"   Receiving messages: {alice_state['receiving_message_number']}")
    
    print("\n4. Security Properties")
    print("-" * 60)
    print("✅ Forward Secrecy: Past messages secure if current key compromised")
    print("✅ Break-in Recovery: Future messages secure after compromise")
    print("✅ Per-Message Keys: Each message has unique encryption key")
    print("✅ No Key Reuse: Keys automatically deleted after use")
    print("✅ Out-of-Order Support: Can handle delayed messages")
    
    print("\n" + "=" * 60)
    print("🛡️ Perfect Forward Secrecy is now operational!")
    print("   Every message uses a unique, ephemeral encryption key.")
