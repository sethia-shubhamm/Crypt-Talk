"""
Socket.IO Handler Module for Crypt-Talk
Handles real-time communication events and user presence
"""

from flask_socketio import emit, join_room, leave_room
from flask import request
from ..encryption.message_encryption import encrypt_message

# Online users tracking
online_users = {}

def create_socketio_handlers(socketio):
    """Create Socket.IO event handlers"""
    
    @socketio.on('add-user')
    def handle_add_user(user_id):
        online_users[user_id] = request.sid
        join_room(user_id)
        print(f"User {user_id} connected with socket {request.sid}")
        emit('user-connected', {'userId': user_id}, broadcast=True)

    @socketio.on('send-msg')
    def handle_send_message(data):
        try:
            to_user = data.get('to')
            from_user = data.get('from')
            message = data.get('msg')
            
            # Encrypt the message for real-time transmission
            encrypted_message = encrypt_message(message, from_user, to_user)
            
            # Send encrypted message to recipient if online
            if to_user in online_users:
                # Decrypt message for real-time display (client expects decrypted)
                socketio.emit('msg-recieve', message, room=online_users[to_user])
                print(f"Message sent from {from_user} to {to_user}: {message}")
            else:
                print(f"User {to_user} is offline")
        
        except Exception as e:
            print(f"Error handling message: {e}")

    @socketio.on('disconnect')
    def handle_disconnect():
        # Remove user from online users
        user_to_remove = None
        for user_id, socket_id in online_users.items():
            if socket_id == request.sid:
                user_to_remove = user_id
                break
        
        if user_to_remove:
            del online_users[user_to_remove]
            emit('user-disconnected', {'userId': user_to_remove}, broadcast=True)
            print(f"User {user_to_remove} disconnected")

def get_online_users():
    """Get list of online users"""
    return online_users

def remove_user_from_online(user_id):
    """Remove user from online users (for logout)"""
    if user_id in online_users:
        del online_users[user_id]