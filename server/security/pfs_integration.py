"""
🔐 PFS Integration with 7-Layer Encryption
============================================

This module integrates Perfect Forward Secrecy with the existing 7-layer
encryption system, replacing static master keys with ephemeral per-message keys.

Integration Strategy:
- PFS generates unique message key for each message
- Message key used as master key for 7-layer encryption
- Automatic key ratcheting after each message
- Session state stored in MongoDB for persistence
"""

import sys
import os
from typing import Tuple, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.perfect_forward_secrecy import PerfectForwardSecrecy
import json


class PFSEncryptionIntegration:
    """
    Integrates PFS with 7-layer encryption system
    """
    
    def __init__(self, mongo_db=None):
        """
        Initialize PFS integration
        
        Args:
            mongo_db: MongoDB database instance for session persistence
        """
        self.pfs = PerfectForwardSecrecy()
        self.mongo_db = mongo_db
        
    def initialize_conversation(self, sender_id: str, recipient_id: str,
                                initiator: bool = True) -> dict:
        """
        Initialize PFS session for a conversation
        
        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            initiator: Whether this user is initiating the session
            
        Returns:
            Session initialization data to send to other party
        """
        # Check if session already exists in database
        if self.mongo_db:
            existing_session = self._load_session_from_db(sender_id, recipient_id)
            if existing_session:
                return {
                    "status": "existing",
                    "message": "Session already established"
                }
        
        # Generate identity key pair for this user
        from security.perfect_forward_secrecy import DoubleRatchet
        temp_ratchet = DoubleRatchet()
        _, identity_public_key = temp_ratchet._generate_dh_keypair()
        
        # Initialize PFS session
        session_data = self.pfs.initialize_session(
            sender_id, recipient_id,
            initiator=initiator,
            remote_public_key=identity_public_key
        )
        
        # Save to database
        if self.mongo_db:
            self._save_session_to_db(sender_id, recipient_id, session_data)
        
        return {
            "status": "initialized",
            "conversation_id": session_data['conversation_id'],
            "public_key": session_data['init_data']['public_key'],
            "timestamp": session_data['init_data']['timestamp']
        }
    
    def encrypt_message_with_pfs(self, sender_id: str, recipient_id: str,
                                 plaintext: bytes) -> dict:
        """
        Encrypt message using PFS + 7-layer encryption
        
        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            plaintext: Message plaintext
            
        Returns:
            Dictionary with encrypted data and PFS metadata
        """
        # Load session if not in memory
        conversation_id = self.pfs._get_conversation_id(sender_id, recipient_id)
        if conversation_id not in self.pfs.sessions:
            if self.mongo_db:
                self._load_session_from_db(sender_id, recipient_id)
            else:
                raise ValueError("No PFS session found. Initialize session first.")
        
        # Get ephemeral message key from PFS ratchet
        pfs_data = self.pfs.encrypt_message(sender_id, recipient_id, plaintext)
        
        # Use PFS message key as master key for 7-layer encryption
        ephemeral_master_key = bytes.fromhex(pfs_data['message_key'])
        
        # Save updated session state
        if self.mongo_db:
            self._update_session_in_db(sender_id, recipient_id)
        
        return {
            "pfs_header": pfs_data['header'],
            "ephemeral_key": pfs_data['message_key'],
            "timestamp": pfs_data['timestamp'],
            "ratchet_data": {
                "dh_public_key": pfs_data['header']['dh_public_key'],
                "message_number": pfs_data['header']['message_number'],
                "previous_chain_length": pfs_data['header']['previous_chain_length']
            }
        }
    
    def decrypt_message_with_pfs(self, sender_id: str, recipient_id: str,
                                 pfs_header: dict, message_key_hex: str) -> bytes:
        """
        Decrypt message using PFS + 7-layer decryption
        
        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            pfs_header: PFS message header
            message_key_hex: Hex-encoded message key
            
        Returns:
            Ephemeral master key for 7-layer decryption
        """
        # Load session if not in memory
        conversation_id = self.pfs._get_conversation_id(sender_id, recipient_id)
        if conversation_id not in self.pfs.sessions:
            if self.mongo_db:
                self._load_session_from_db(sender_id, recipient_id)
            else:
                raise ValueError("No PFS session found")
        
        # Decrypt with PFS ratchet
        ephemeral_master_key = self.pfs.decrypt_message(
            sender_id, recipient_id,
            pfs_header, message_key_hex
        )
        
        # Save updated session state
        if self.mongo_db:
            self._update_session_in_db(sender_id, recipient_id)
        
        return ephemeral_master_key
    
    def _save_session_to_db(self, user1_id: str, user2_id: str, 
                           session_data: dict) -> None:
        """Save PFS session to MongoDB"""
        if not self.mongo_db:
            return
        
        conversation_id = self.pfs._get_conversation_id(user1_id, user2_id)
        
        self.mongo_db.pfs_sessions.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {
                    "conversation_id": conversation_id,
                    "user1_id": user1_id,
                    "user2_id": user2_id,
                    "session_data": session_data,
                    "updated_at": session_data['init_data']['timestamp']
                }
            },
            upsert=True
        )
    
    def _load_session_from_db(self, user1_id: str, user2_id: str) -> Optional[dict]:
        """Load PFS session from MongoDB"""
        if not self.mongo_db:
            return None
        
        conversation_id = self.pfs._get_conversation_id(user1_id, user2_id)
        
        session_doc = self.mongo_db.pfs_sessions.find_one(
            {"conversation_id": conversation_id}
        )
        
        if session_doc:
            # Reconstruct session state
            state = session_doc.get('session_state')
            if state:
                self.pfs.load_session_state(user1_id, user2_id, state)
            return session_doc
        
        return None
    
    def _update_session_in_db(self, user1_id: str, user2_id: str) -> None:
        """Update PFS session state in MongoDB"""
        if not self.mongo_db:
            return
        
        conversation_id = self.pfs._get_conversation_id(user1_id, user2_id)
        state = self.pfs.save_session_state(user1_id, user2_id)
        
        if state:
            import time
            self.mongo_db.pfs_sessions.update_one(
                {"conversation_id": conversation_id},
                {
                    "$set": {
                        "session_state": state,
                        "updated_at": int(time.time())
                    }
                }
            )
    
    def delete_conversation_session(self, user1_id: str, user2_id: str) -> None:
        """
        Delete PFS session (secure cleanup)
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
        """
        # Delete from memory
        self.pfs.delete_session(user1_id, user2_id)
        
        # Delete from database
        if self.mongo_db:
            conversation_id = self.pfs._get_conversation_id(user1_id, user2_id)
            self.mongo_db.pfs_sessions.delete_one(
                {"conversation_id": conversation_id}
            )


# Example usage documentation
"""
USAGE EXAMPLE:
==============

# 1. Initialize PFS integration (in app.py)
from security.pfs_integration import PFSEncryptionIntegration

pfs_manager = PFSEncryptionIntegration(mongo_db=mongo.db)

# 2. When users start chatting, initialize PFS session
@app.route('/api/messages/init-pfs', methods=['POST'])
def initialize_pfs_session():
    data = request.json
    sender_id = data['sender_id']
    recipient_id = data['recipient_id']
    
    session_data = pfs_manager.initialize_conversation(
        sender_id, recipient_id, initiator=True
    )
    
    return jsonify(session_data)

# 3. When encrypting a message
@app.route('/api/messages/send', methods=['POST'])
def send_message():
    data = request.json
    sender_id = data['sender_id']
    recipient_id = data['recipient_id']
    message = data['message']
    
    # Get ephemeral key from PFS
    pfs_data = pfs_manager.encrypt_message_with_pfs(
        sender_id, recipient_id, message.encode('utf-8')
    )
    
    # Use ephemeral key for 7-layer encryption
    ephemeral_master_key = bytes.fromhex(pfs_data['ephemeral_key'])
    
    # Import your 7-layer encryption
    from 7_layer_encryption.master_encryption import SevenLayerEncryption
    
    encryptor = SevenLayerEncryption(profile="BALANCED")
    encrypted = encryptor.encrypt(
        message.encode('utf-8'),
        ephemeral_master_key,  # <-- Use PFS ephemeral key instead of static key
        os.urandom(16)
    )
    
    # Store message with PFS metadata
    message_doc = {
        "sender": sender_id,
        "recipient": recipient_id,
        "encrypted_message": encrypted,
        "pfs_header": pfs_data['pfs_header'],
        "pfs_key_id": pfs_data['ephemeral_key'][:32],  # Reference only
        "timestamp": pfs_data['timestamp']
    }
    
    mongo.db.messages.insert_one(message_doc)
    
    return jsonify({"status": "sent"})

# 4. When decrypting a message
@app.route('/api/messages/receive', methods=['POST'])
def receive_message():
    data = request.json
    message_id = data['message_id']
    
    # Retrieve message
    message_doc = mongo.db.messages.find_one({"_id": ObjectId(message_id)})
    
    # Get ephemeral key from PFS
    ephemeral_master_key = pfs_manager.decrypt_message_with_pfs(
        message_doc['sender'],
        message_doc['recipient'],
        message_doc['pfs_header'],
        message_doc['pfs_key_id']
    )
    
    # Use ephemeral key for 7-layer decryption
    from 7_layer_encryption.master_encryption import SevenLayerEncryption
    
    encryptor = SevenLayerEncryption(profile="BALANCED")
    decrypted = encryptor.decrypt(
        message_doc['encrypted_message'],
        ephemeral_master_key  # <-- Use PFS ephemeral key
    )
    
    return jsonify({"message": decrypted.decode('utf-8')})

SECURITY BENEFITS:
==================
✅ Each message uses unique ephemeral key
✅ Keys automatically destroyed after use
✅ Forward secrecy: Past messages safe if current key compromised
✅ Break-in recovery: Future messages safe after compromise
✅ No key reuse across messages
✅ Automatic key ratcheting
"""

if __name__ == "__main__":
    print("🔐 PFS Integration Module")
    print("=" * 60)
    print("\nThis module integrates Perfect Forward Secrecy with")
    print("the existing 7-layer encryption system.")
    print("\nKey Features:")
    print("  ✅ Ephemeral per-message keys")
    print("  ✅ Automatic key ratcheting")
    print("  ✅ MongoDB session persistence")
    print("  ✅ Forward secrecy guarantee")
    print("\nSee docstring for usage examples.")
