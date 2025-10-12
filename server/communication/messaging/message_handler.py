"""
Message Handler Module for Crypt-Talk
Handles message storage, retrieval, and processing with encryption
"""

from flask import request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from ..encryption.message_encryption import encrypt_message, decrypt_message
from ..self_destruct.timer_handler import add_self_destruct_to_message

# Import steganography system
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'steganography'))

from seven_layer_stego import SevenLayerSteganography

# Create a custom crypto interface for steganography
class CryptoInterface:
    """Interface to connect steganography with the existing 7-layer encryption system"""
    def encrypt_message(self, message, user_pair):
        """Encrypt message using existing 7-layer system"""
        return encrypt_message(message, user_pair[0], user_pair[1])
    
    def decrypt_message(self, encrypted_data, user_pair):
        """Decrypt message using existing 7-layer system"""  
        return decrypt_message(encrypted_data, user_pair[0], user_pair[1])

# Initialize steganography system with 7-layer crypto
crypto_interface = CryptoInterface()
stego_system = SevenLayerSteganography(seven_layer_crypto=crypto_interface, verbose=True)

def create_message_routes(app, mongo):
    """Create Flask routes for message handling"""
    
    @app.route('/api/messages/addmsg', methods=['POST'])
    def add_message():
        try:
            data = request.get_json()
            from_user = data.get('from')
            to_user = data.get('to')
            message = data.get('message')
            
            # 🎭 AI STEGANOGRAPHY: ALL MESSAGES get 7-layer encryption + steganographic concealment
            print(f"\n🎭 AI STEGANOGRAPHIC MESSAGING SYSTEM")
            print(f"   📨 Processing ALL messages with steganography")
            print(f"   👥 Users: {from_user} → {to_user}")
            print(f"   📝 Original Message: '{message}'")
            print(f"   🤖 AI Feature: Automatic innocent text generation")
            
            # Determine text style based on message content for variety
            if any(word in message.lower() for word in ['weather', 'rain', 'sunny', 'cold', 'hot']):
                text_style = 'weather'
            elif any(word in message.lower() for word in ['food', 'eat', 'restaurant', 'dinner', 'lunch']):
                text_style = 'food'  
            elif any(word in message.lower() for word in ['tech', 'computer', 'phone', 'app', 'software']):
                text_style = 'technology'
            else:
                text_style = 'daily_life'  # Default
            
            print(f"   🎨 AI Selected Style: {text_style}")
            
            # Use steganography for ALL messages (7-layer encryption + steganographic concealment)
            stego_result = stego_system.hide_encrypted_message(
                message, (from_user, to_user), text_style
            )
            
            # Store steganographic message in database
            message_data = {
                "message": {
                    "text": stego_result['data'],  # The innocent text
                    "type": "steganographic", 
                    "original_message": message,
                    "text_style": stego_result['text_style'],
                    "users": [ObjectId(from_user), ObjectId(to_user)]
                },
                "stego_info": {
                    "original_length": stego_result['original_length'],
                    "stego_length": stego_result['stego_length'],
                    "expansion_ratio": stego_result['stego_length'] / stego_result['original_length'],
                    "timestamp": stego_result['timestamp'],
                    "ai_text_style": text_style
                },
                "users": [ObjectId(from_user), ObjectId(to_user)],
                "sender": ObjectId(from_user),
                "createdAt": datetime.utcnow()
            }
            
            print(f"   ✅ AI Steganographic message created!")
            print(f"   📄 Innocent text: {len(stego_result['data'])} chars")
            print(f"   📊 Concealment ratio: {stego_result['stego_length'] / stego_result['original_length']:.1f}x expansion")
            
            # Add self-destruct timer if user has one configured
            message_data = add_self_destruct_to_message(message_data, from_user, mongo)
            
            result = mongo.db.messages.insert_one(message_data)
            
            if result.inserted_id:
                return jsonify({
                    "msg": "AI Steganographic message added successfully.",
                    "ai_features": {
                        "encryption": "7-layer military-grade",
                        "steganography": "Innocent text concealment", 
                        "text_style": text_style,
                        "concealment_ratio": f"{stego_result['stego_length'] / stego_result['original_length']:.1f}x",
                        "innocent_text_length": stego_result['stego_length']
                    }
                })
            else:
                return jsonify({"msg": "Failed to add AI steganographic message to the database"})
        
        except Exception as e:
            print(f"   ❌ AI Steganographic processing failed: {e}")
            return jsonify({"msg": f"AI Steganography error: {str(e)}", "status": False}), 500
    
    # NOTE: Old separate steganographic route no longer needed - ALL messages are now AI steganographic
    
    # Legacy steganographic route (commented out - functionality moved to main addmsg route)
    # @app.route('/api/messages/addmsg-stego', methods=['POST']) 
    # def add_steganographic_message():
    #     # All functionality moved to main /api/messages/addmsg route
    #     pass
    #     # Old steganographic functionality removed - now integrated into main addmsg route
    
    @app.route('/api/messages/getmsg', methods=['POST'])
    def get_messages():
        try:
            data = request.get_json()
            from_user = data.get('from')
            to_user = data.get('to')
            
            # Get messages between two users
            messages = mongo.db.messages.find({
                "users": {
                    "$all": [ObjectId(from_user), ObjectId(to_user)]
                }
            }).sort("createdAt", 1)
            
            project_messages = []
            for msg in messages:
                if msg["message"].get("type") == "file":
                    # File message
                    project_messages.append({
                        "fromSelf": str(msg["sender"]) == from_user,
                        "type": "file",
                        "file_id": str(msg["message"]["file_id"]),
                        "filename": msg["message"]["filename"],
                        "original_filename": msg["message"]["original_filename"],
                        "file_type": msg["message"]["file_type"],
                        "file_size": msg["message"]["file_size"]
                    })
                elif msg["message"].get("type") == "steganographic":
                    # Steganographic message - extract and decrypt
                    try:
                        innocent_text = msg["message"]["text"]
                        decrypted_text = stego_system.reveal_hidden_message(innocent_text, (from_user, to_user))
                        
                        project_messages.append({
                            "fromSelf": str(msg["sender"]) == from_user,
                            "type": "steganographic",
                            "message": decrypted_text,
                            "innocent_text": innocent_text[:200] + "..." if len(innocent_text) > 200 else innocent_text,
                            "stego_info": msg.get("steganography_info", {})
                        })
                    except Exception as e:
                        # Fallback to showing innocent text if decryption fails
                        project_messages.append({
                            "fromSelf": str(msg["sender"]) == from_user,
                            "type": "text",
                            "message": f"[Steganographic message - decryption failed: {str(e)}]"
                        })
                else:
                    # Regular text message - decrypt it
                    decrypted_text = decrypt_message(msg["message"]["text"], from_user, to_user)
                    
                    project_messages.append({
                        "fromSelf": str(msg["sender"]) == from_user,
                        "type": "text",
                        "message": decrypted_text
                    })
            
            return jsonify(project_messages)
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/messages/encryption-info/<from_user>/<to_user>', methods=['GET'])
    def get_encryption_info(from_user, to_user):
        """Get encryption information for messages between two users"""
        try:
            # Get recent messages with encryption info
            messages = mongo.db.messages.find({
                "users": {
                    "$all": [ObjectId(from_user), ObjectId(to_user)]
                }
            }).sort("createdAt", -1).limit(10)
            
            encryption_data = []
            for msg in messages:
                encryption_data.append({
                    "timestamp": msg["createdAt"].isoformat(),
                    "sender": str(msg["sender"]),
                    "encrypted_message": msg["message"]["text"][:50] + "..." if len(msg["message"]["text"]) > 50 else msg["message"]["text"],
                    "encryption_info": msg.get("encryption_info", {})
                })
            
            return jsonify({
                "messages_count": len(encryption_data),
                "encryption_data": encryption_data
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500