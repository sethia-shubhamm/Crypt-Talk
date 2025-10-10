"""
Message Handler Module for Crypt-Talk
Handles message storage, retrieval, and processing with encryption
"""

from flask import request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from ..encryption.seven_layer_integration import encrypt_message, decrypt_message
from ..self_destruct.timer_handler import add_self_destruct_to_message

def create_message_routes(app, mongo):
    """Create Flask routes for message handling"""
    
    @app.route('/api/messages/addmsg', methods=['POST'])
    def add_message():
        try:
            data = request.get_json()
            from_user = data.get('from')
            to_user = data.get('to')
            message = data.get('message')
            
            # Encrypt the message
            encryption_result = encrypt_message(message, from_user, to_user)
            
            # Store encrypted message with complete encryption metadata in database
            message_data = {
                "message": {
                    "text": encryption_result,  # Store full encryption result for 7-layer compatibility
                    "users": [ObjectId(from_user), ObjectId(to_user)]
                },
                "encryption_info": {
                    "key_preview": encryption_result.get('encryption_key', 'N/A'),
                    "message_hash": encryption_result.get('message_hash', 'N/A'),
                    "original_length": encryption_result.get('original_length', 0),
                    "encryption_version": encryption_result.get('encryption_version', '7LAYER_v1.0'),
                    "security_profile": encryption_result.get('security_profile', 'BALANCED')
                },
                "users": [ObjectId(from_user), ObjectId(to_user)],
                "sender": ObjectId(from_user),
                "createdAt": datetime.utcnow()
            }
            
            # Add self-destruct timer if user has one configured
            message_data = add_self_destruct_to_message(message_data, from_user, mongo)
            
            result = mongo.db.messages.insert_one(message_data)
            
            if result.inserted_id:
                return jsonify({"msg": "Message added successfully."})
            else:
                return jsonify({"msg": "Failed to add message to the database"})
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
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
                else:
                    # Text message - decrypt it
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
                # Handle both new format (dict) and old format (string)
                message_text = msg["message"]["text"]
                if isinstance(message_text, dict):
                    encrypted_preview = message_text.get('encrypted_message', '')[:50] + "..."
                else:
                    encrypted_preview = message_text[:50] + "..." if len(message_text) > 50 else message_text
                
                encryption_data.append({
                    "timestamp": msg["createdAt"].isoformat(),
                    "sender": str(msg["sender"]),
                    "encrypted_message": encrypted_preview,
                    "encryption_info": msg.get("encryption_info", {})
                })
            
            return jsonify({
                "messages_count": len(encryption_data),
                "encryption_data": encryption_data
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500