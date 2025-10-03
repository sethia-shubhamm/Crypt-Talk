"""
Message Handler Module for Crypt-Talk
Handles message storage, retrieval, and processing with encryption
"""

from flask import request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from ..encryption.message_encryption import encrypt_message, decrypt_message

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
            
            # Store encrypted message with encryption details in database
            message_data = {
                "message": {
                    "text": encryption_result['encrypted_message'],
                    "users": [ObjectId(from_user), ObjectId(to_user)]
                },
                "encryption_info": {
                    "key_preview": encryption_result['encryption_key'],
                    "message_hash": encryption_result['message_hash'],
                    "original_length": encryption_result['original_length']
                },
                "users": [ObjectId(from_user), ObjectId(to_user)],
                "sender": ObjectId(from_user),
                "createdAt": datetime.utcnow()
            }
            
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
                # Decrypt the message
                decrypted_text = decrypt_message(msg["message"]["text"], from_user, to_user)
                
                project_messages.append({
                    "fromSelf": str(msg["sender"]) == from_user,
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