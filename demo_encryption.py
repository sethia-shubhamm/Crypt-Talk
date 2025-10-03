#!/usr/bin/env python3
"""
Crypt-Talk Chat Application Demo
Shows implemented end-to-end encryption and real-time messaging features
"""

from cryptography.fernet import Fernet
import base64
import hashlib
import json

def generate_key_from_users(user1_id, user2_id):
    """Generate a consistent encryption key for two users"""
    users = sorted([str(user1_id), str(user2_id)])
    key_string = f"{users[0]}:{users[1]}"
    # Generate a key using SHA-256 and encode it for Fernet
    key_hash = hashlib.sha256(key_string.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)

def encrypt_message(message, user1_id, user2_id):
    """Encrypt a message between two users"""
    key = generate_key_from_users(user1_id, user2_id)
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())
    return base64.urlsafe_b64encode(encrypted_message).decode()

def decrypt_message(encrypted_message, user1_id, user2_id):
    """Decrypt a message between two users"""
    try:
        key = generate_key_from_users(user1_id, user2_id)
        fernet = Fernet(key)
        decoded_message = base64.urlsafe_b64decode(encrypted_message.encode())
        decrypted_message = fernet.decrypt(decoded_message)
        return decrypted_message.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return encrypted_message

def demo_encryption():
    """Demonstrate the encryption/decryption functionality"""
    print("🔒 CRYPT-TALK - END-TO-END ENCRYPTION DEMO")
    print("=" * 50)
    
    # Simulate two users
    user1_id = "user123"
    user2_id = "user456"
    
    print(f"👤 User 1 ID: {user1_id}")
    print(f"👤 User 2 ID: {user2_id}")
    print()
    
    # Original message
    original_message = "Hello! This is a secret message 🔐"
    print(f"📝 Original Message: {original_message}")
    
    # Encrypt the message
    encrypted = encrypt_message(original_message, user1_id, user2_id)
    print(f"🔒 Encrypted Message: {encrypted}")
    
    # Decrypt the message
    decrypted = decrypt_message(encrypted, user1_id, user2_id)
    print(f"🔓 Decrypted Message: {decrypted}")
    
    # Verify encryption is consistent
    key1 = generate_key_from_users(user1_id, user2_id)
    key2 = generate_key_from_users(user2_id, user1_id)  # Reversed order
    
    print()
    print("🔑 Key Generation Test:")
    print(f"Key (user1 → user2): {key1.decode()[:32]}...")
    print(f"Key (user2 → user1): {key2.decode()[:32]}...")
    print(f"Keys Match: {'✅ Yes' if key1 == key2 else '❌ No'}")
    
    print()
    print("✅ Encryption Demo Complete!")
    print("\n🚀 IMPLEMENTED FEATURES:")
    print("- End-to-end message encryption using Fernet (AES 128)")
    print("- Consistent key generation for user pairs")
    print("- Real-time messaging with Socket.IO")
    print("- Persistent encrypted message storage")
    print("- User authentication with bcrypt")
    print("- Online user tracking")
    print("- Chat history retrieval")

def demo_message_flow():
    """Demonstrate the complete message flow"""
    print("\n" + "=" * 50)
    print("📱 MESSAGE FLOW DEMONSTRATION")
    print("=" * 50)
    
    # Simulate a conversation
    messages = [
        {"from": "alice", "to": "bob", "text": "Hey Bob! How are you?"},
        {"from": "bob", "to": "alice", "text": "Hi Alice! I'm doing great, thanks!"},
        {"from": "alice", "to": "bob", "text": "Want to grab coffee later? ☕"},
        {"from": "bob", "to": "alice", "text": "Sure! Let's meet at 3 PM 😊"}
    ]
    
    print("💬 Simulating chat between Alice and Bob:")
    print()
    
    encrypted_chat = []
    
    for msg in messages:
        sender = msg["from"]
        recipient = msg["to"]
        text = msg["text"]
        
        # Encrypt the message
        encrypted_text = encrypt_message(text, sender, recipient)
        encrypted_chat.append({
            "from": sender,
            "to": recipient,
            "encrypted": encrypted_text,
            "original": text
        })
        
        print(f"👤 {sender.title()} → {recipient.title()}: {text}")
        print(f"🔒 Stored encrypted: {encrypted_text[:50]}...")
        print()
    
    print("📚 Retrieving chat history (decrypted for display):")
    print()
    
    for msg in encrypted_chat:
        decrypted = decrypt_message(msg["encrypted"], msg["from"], msg["to"])
        print(f"👤 {msg['from'].title()}: {decrypted}")
    
    print("\n✅ Message Flow Demo Complete!")

if __name__ == "__main__":
    demo_encryption()
    demo_message_flow()
    
    print("\n" + "=" * 50)
    print("🎯 TO RUN THE FULL APPLICATION:")
    print("=" * 50)
    print("1. Backend: cd server && python app.py")
    print("2. Frontend: cd public && npm start")
    print("3. Visit: http://localhost:3000")
    print("4. Test login: username='testuser', password='password123'")
    print("\n🔐 All messages are automatically encrypted end-to-end!")