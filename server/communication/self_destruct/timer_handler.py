"""
Self Destruct Timer Module                     # R                        # Remove the timer entry
                        self.mongo.db.conversation_timers.delete_one({"_id": timer_doc["_id"]})
                        
                        # Notify clients to clear local copies
                        if self.socketio:
                            self.socketio.emit('conversation-destroyed', {
                                'user1_id': str(user1_id),
                                'user2_id': str(user2_id),
                                'message_count': delete_result.deleted_count,
                                'file_count': file_delete_result.deleted_count
                            }, broadcast=True)
                        
                        print(f"🔥 CONVERSATION SELF-DESTRUCTED!")
                        print(f"   👥 Users: {user1_id} ↔ {user2_id}")
                        print(f"   💬 Deleted {delete_result.deleted_count} messages")
                        print(f"   📁 Deleted {file_delete_result.deleted_count} files")
                        print(f"   📡 Clients notified to clear local copies")found expired" message, only show actual deletion Crypt-Talk
Hand                        print(f"💥 CONVERSATION DESTROYED! {user1_id} ↔ {user2_id} ({delete_result.deleted_count} messages, {file_delete_result.deleted_count} files)")automatic message deletion based on us            # Only show when timer is first set for a conversation
            print(f"🔥 Timer set: {timer_minutes} minutes")r-set timers
"""

from flask import request, jsonify
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import threading
import time

class SelfDestructManager:
    def __init__(self, mongo):
        self.mongo = mongo
        self.active_timers = {}
        self.socketio = None
        self.start_cleanup_scheduler()
    
    def set_socketio(self, socketio):
        """Set socketio instance for real-time notifications"""
        self.socketio = socketio
    
    def start_cleanup_scheduler(self):
        """Start background thread for conversation cleanup"""
        def cleanup_expired_conversations():
            while True:
                try:
                    current_time = datetime.utcnow()
                    
                    # Find expired conversation timers
                    expired_timers = self.mongo.db.conversation_timers.find({
                        "expires_at": {"$lte": current_time}
                    })
                    
                    expired_list = list(expired_timers)
                    
                    # Only show message if there are expired timers
                    if len(expired_list) > 0:
                        print(f"� Found {len(expired_list)} expired conversation(s) to delete")
                    
                    for timer_doc in expired_list:
                        user1_id = timer_doc["user1_id"]
                        user2_id = timer_doc["user2_id"]
                        
                        # Delete ALL messages between these two users
                        delete_result = self.mongo.db.messages.delete_many({
                            "users": {"$all": [user1_id, user2_id]}
                        })
                        
                        # Delete ALL files between these two users
                        file_delete_result = self.mongo.db.files.delete_many({
                            "users": {"$all": [user1_id, user2_id]}
                        })
                        
                        # Remove the timer entry
                        self.mongo.db.conversation_timers.delete_one({"_id": timer_doc["_id"]})
                        
                        print(f"🔥 CONVERSATION SELF-DESTRUCTED!")
                        print(f"   👥 Users: {user1_id} ↔ {user2_id}")
                        print(f"   💬 Deleted {delete_result.deleted_count} messages")
                        print(f"   � Deleted {file_delete_result.deleted_count} files")
                    
                    # Sleep for 5 seconds before next check (faster for testing)
                    time.sleep(5)
                    
                except Exception as e:
                    print(f"Error in cleanup scheduler: {e}")
                    time.sleep(60)  # Wait longer on error
        
        # Start the cleanup thread
        cleanup_thread = threading.Thread(target=cleanup_expired_conversations, daemon=True)
        cleanup_thread.start()

def create_self_destruct_routes(app, mongo):
    """Create Flask routes for self-destruct timer management"""
    
    # Initialize the self-destruct manager
    destruct_manager = SelfDestructManager(mongo)
    
    # Store socketio reference for notifications
    destruct_manager.socketio = None
    
    @app.route('/api/self-destruct/set-timer', methods=['POST'])
    def set_self_destruct_timer():
        try:
            data = request.get_json()
            user_id = data.get('userId')
            timer_minutes = data.get('timerMinutes')  # Can be None for "never"
            
            # Remove individual timer setting message
            
            # Update or create user's self-destruct preference
            user_settings = {
                "user_id": ObjectId(user_id),
                "self_destruct_timer": timer_minutes,  # None means never
                "updated_at": datetime.utcnow()
            }
            
            # Upsert user settings
            result = mongo.db.user_settings.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": user_settings},
                upsert=True
            )
            
            # Remove timer activation message
            
            timer_text = f"{timer_minutes} minutes" if timer_minutes else "Never"
            
            return jsonify({
                "status": True,
                "message": f"Self-destruct timer set to {timer_text}",
                "timer_minutes": timer_minutes
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/self-destruct/get-timer/<user_id>', methods=['GET'])
    def get_self_destruct_timer(user_id):
        try:
            user_settings = mongo.db.user_settings.find_one({"user_id": ObjectId(user_id)})
            
            timer_minutes = None
            if user_settings and "self_destruct_timer" in user_settings:
                timer_minutes = user_settings["self_destruct_timer"]
            
            return jsonify({
                "status": True,
                "timer": timer_minutes
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/self-destruct/conversation-info/<user1_id>/<user2_id>', methods=['GET'])
    def get_conversation_timer_info(user1_id, user2_id):
        try:
            # Ensure consistent ordering
            if user1_id > user2_id:
                user1_id, user2_id = user2_id, user1_id
            
            # Find active timer for this conversation
            timer_doc = mongo.db.conversation_timers.find_one({
                "user1_id": ObjectId(user1_id),
                "user2_id": ObjectId(user2_id)
            })
            
            if timer_doc:
                current_time = datetime.utcnow()
                time_remaining = timer_doc["expires_at"] - current_time
                
                return jsonify({
                    "status": True,
                    "has_timer": True,
                    "timer_minutes": timer_doc["timer_minutes"],
                    "expires_at": timer_doc["expires_at"].isoformat(),
                    "time_remaining_seconds": int(time_remaining.total_seconds()),
                    "last_message_at": timer_doc["last_message_at"].isoformat()
                })
            else:
                return jsonify({
                    "status": True,
                    "has_timer": False
                })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/self-destruct/cancel-conversation-timer/<user1_id>/<user2_id>', methods=['DELETE'])
    def cancel_conversation_timer(user1_id, user2_id):
        try:
            # Ensure consistent ordering
            if user1_id > user2_id:
                user1_id, user2_id = user2_id, user1_id
            
            # Remove the timer
            result = mongo.db.conversation_timers.delete_one({
                "user1_id": ObjectId(user1_id),
                "user2_id": ObjectId(user2_id)
            })
            
            # Remove cancellation message
            if result.deleted_count > 0:
                return jsonify({
                    "status": True,
                    "message": "Conversation timer cancelled"
                })
            else:
                return jsonify({
                    "status": False,
                    "message": "No active timer found"
                })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/self-destruct/debug/<user_id>', methods=['GET'])
    def debug_user_timer(user_id):
        try:
            # Get user settings
            user_settings = mongo.db.user_settings.find_one({"user_id": ObjectId(user_id)})
            
            # Get all conversation timers for this user
            timers = list(mongo.db.conversation_timers.find({
                "$or": [
                    {"user1_id": ObjectId(user_id)},
                    {"user2_id": ObjectId(user_id)}
                ]
            }))
            
            return jsonify({
                "status": True,
                "user_settings": user_settings,
                "active_timers": timers,
                "timer_count": len(timers)
            })
            
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/self-destruct/activate-timer', methods=['POST'])
    def activate_conversation_timer():
        """Activate timer for a specific conversation immediately"""
        try:
            data = request.get_json()
            from_user = data.get('fromUser')
            to_user = data.get('toUser')
            
            # Remove activation message
            
            # Create a dummy message to trigger timer creation
            dummy_message_data = {
                "users": [ObjectId(from_user), ObjectId(to_user)],
                "sender": ObjectId(from_user)
            }
            
            # Use the existing timer creation logic
            result_data = add_self_destruct_to_message(dummy_message_data, from_user, mongo)
            
            if result_data:
                return jsonify({
                    "status": True,
                    "message": "Conversation timer activated"
                })
            else:
                return jsonify({
                    "status": False,
                    "message": "No timer configured for user"
                })
            
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    # Return the manager instance for socketio connection
    return destruct_manager

def add_self_destruct_to_message(message_data, user_id, mongo):
    """Create or update conversation-level self-destruct timer"""
    try:
        # Get user's self-destruct settings
        user_settings = mongo.db.user_settings.find_one({"user_id": ObjectId(user_id)})
        
        if user_settings and user_settings.get("self_destruct_timer") is not None and user_settings.get("self_destruct_timer") > 0:
            timer_minutes = float(user_settings["self_destruct_timer"])  # Ensure it's a float
            expires_at = datetime.utcnow() + timedelta(minutes=timer_minutes)
            
            print(f"� Conversation will self-destruct in {timer_minutes} minutes at {expires_at.strftime('%H:%M:%S')}")
            
            # Get the two users in this conversation
            users = message_data["users"]
            user1_id = users[0]
            user2_id = users[1]
            
            # Ensure consistent ordering for conversation lookup
            if str(user1_id) > str(user2_id):
                user1_id, user2_id = user2_id, user1_id
            
            # Create or update conversation timer
            conversation_timer = {
                "user1_id": user1_id,
                "user2_id": user2_id,
                "timer_minutes": timer_minutes,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "last_message_at": datetime.utcnow()
            }
            
            # Upsert the conversation timer (update if exists, create if not)
            result = mongo.db.conversation_timers.update_one(
                {"user1_id": user1_id, "user2_id": user2_id},
                {"$set": conversation_timer},
                upsert=True
            )
            
            # Remove detailed confirmation message
    
    except Exception as e:
        pass  # Silent error handling
    
    return message_data