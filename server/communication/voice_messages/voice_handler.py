import os
import uuid
import base64
from datetime import datetime, timedelta
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename
import mimetypes
from threading import Timer
import logging

class VoiceMessageHandler:
    def __init__(self, mongo):
        self.mongo = mongo
        self.voice_upload_folder = os.path.join(os.getcwd(), 'voice_uploads')
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit for voice messages
        self.allowed_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.webm', '.aac'}
        self.cleanup_timers = {}
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.voice_upload_folder, exist_ok=True)
        
        # Initialize cleanup for expired voice messages
        self._cleanup_expired_voices()
    
    def upload_voice_message(self):
        """Handle voice message upload with expiry timer"""
        try:
            # Check if file is present
            if 'voice' not in request.files:
                return jsonify({"status": False, "msg": "No voice file provided"}), 400
            
            file = request.files['voice']
            if file.filename == '':
                return jsonify({"status": False, "msg": "No voice file selected"}), 400
            
            # Get additional parameters
            from_user = request.form.get('from')
            to_user = request.form.get('to')
            expiry_minutes = int(request.form.get('expiry_minutes', 60))  # Default 1 hour
            
            if not from_user or not to_user:
                return jsonify({"status": False, "msg": "Sender and receiver required"}), 400
            
            # Validate file
            if not self._is_valid_voice_file(file):
                return jsonify({"status": False, "msg": "Invalid voice file format"}), 400
            
            if file.content_length and file.content_length > self.max_file_size:
                return jsonify({"status": False, "msg": "Voice file too large (max 50MB)"}), 400
            
            # Generate unique filename
            voice_id = str(uuid.uuid4())
            file_extension = os.path.splitext(secure_filename(file.filename))[1].lower()
            filename = f"{voice_id}{file_extension}"
            file_path = os.path.join(self.voice_upload_folder, filename)
            
            # Save file
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            
            # Calculate expiry time
            expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
            
            # Store voice message metadata in database
            voice_data = {
                "voice_id": voice_id,
                "filename": filename,
                "original_filename": secure_filename(file.filename),
                "file_path": file_path,
                "file_size": file_size,
                "mime_type": mimetypes.guess_type(filename)[0] or 'audio/mpeg',
                "from_user": from_user,
                "to_user": to_user,
                "uploaded_at": datetime.now(),
                "expiry_time": expiry_time,
                "expiry_minutes": expiry_minutes,
                "is_expired": False,
                "play_count": 0,
                "max_plays": request.form.get('max_plays', None)  # Optional play limit
            }
            
            self.mongo.db.voice_messages.insert_one(voice_data)
            
            # Set up auto-deletion timer
            self._schedule_voice_deletion(voice_id, expiry_time)
            
            return jsonify({
                "status": True,
                "voice_id": voice_id,
                "filename": secure_filename(file.filename),
                "file_size": file_size,
                "duration_minutes": expiry_minutes,
                "expiry_time": expiry_time.isoformat(),
                "msg": "Voice message uploaded successfully"
            })
            
        except Exception as e:
            logging.error(f"Voice upload error: {str(e)}")
            return jsonify({"status": False, "msg": f"Upload failed: {str(e)}"}), 500
    
    def download_voice_message(self, voice_id):
        """Download and play voice message"""
        try:
            # Find voice message in database
            voice_msg = self.mongo.db.voice_messages.find_one({"voice_id": voice_id})
            
            if not voice_msg:
                return jsonify({"status": False, "msg": "Voice message not found"}), 404
            
            if voice_msg.get('is_expired', False):
                return jsonify({"status": False, "msg": "Voice message has expired"}), 410
            
            # Check if file still exists
            if not os.path.exists(voice_msg['file_path']):
                # Mark as expired in database
                self.mongo.db.voice_messages.update_one(
                    {"voice_id": voice_id},
                    {"$set": {"is_expired": True}}
                )
                return jsonify({"status": False, "msg": "Voice message file not found"}), 404
            
            # Check play count limit if set
            max_plays = voice_msg.get('max_plays')
            current_plays = voice_msg.get('play_count', 0)
            
            if max_plays and current_plays >= max_plays:
                return jsonify({"status": False, "msg": "Voice message play limit reached"}), 410
            
            # Increment play count
            self.mongo.db.voice_messages.update_one(
                {"voice_id": voice_id},
                {"$inc": {"play_count": 1}}
            )
            
            # Return file
            return send_file(
                voice_msg['file_path'],
                mimetype=voice_msg['mime_type'],
                as_attachment=False,
                download_name=voice_msg['original_filename']
            )
            
        except Exception as e:
            logging.error(f"Voice download error: {str(e)}")
            return jsonify({"status": False, "msg": f"Download failed: {str(e)}"}), 500
    
    def get_voice_info(self, voice_id):
        """Get voice message information"""
        try:
            voice_msg = self.mongo.db.voice_messages.find_one(
                {"voice_id": voice_id},
                {"file_path": 0}  # Exclude file path from response
            )
            
            if not voice_msg:
                return jsonify({"status": False, "msg": "Voice message not found"}), 404
            
            # Convert ObjectId to string
            voice_msg['_id'] = str(voice_msg['_id'])
            
            # Add time remaining
            if not voice_msg.get('is_expired', False):
                expiry_time = voice_msg['expiry_time']
                time_remaining = expiry_time - datetime.now()
                voice_msg['time_remaining_minutes'] = max(0, int(time_remaining.total_seconds() / 60))
                voice_msg['is_expired'] = time_remaining.total_seconds() <= 0
            
            return jsonify({"status": True, "voice_message": voice_msg})
            
        except Exception as e:
            logging.error(f"Voice info error: {str(e)}")
            return jsonify({"status": False, "msg": f"Failed to get voice info: {str(e)}"}), 500
    
    def delete_voice_message(self, voice_id):
        """Delete voice message immediately"""
        try:
            voice_msg = self.mongo.db.voice_messages.find_one({"voice_id": voice_id})
            
            if not voice_msg:
                return jsonify({"status": False, "msg": "Voice message not found"}), 404
            
            # Delete file if exists
            if os.path.exists(voice_msg['file_path']):
                os.remove(voice_msg['file_path'])
            
            # Remove from database
            self.mongo.db.voice_messages.delete_one({"voice_id": voice_id})
            
            # Cancel cleanup timer if exists
            if voice_id in self.cleanup_timers:
                self.cleanup_timers[voice_id].cancel()
                del self.cleanup_timers[voice_id]
            
            return jsonify({"status": True, "msg": "Voice message deleted successfully"})
            
        except Exception as e:
            logging.error(f"Voice deletion error: {str(e)}")
            return jsonify({"status": False, "msg": f"Deletion failed: {str(e)}"}), 500
    
    def _is_valid_voice_file(self, file):
        """Check if uploaded file is a valid voice format"""
        if not file.filename:
            return False
        
        file_extension = os.path.splitext(secure_filename(file.filename))[1].lower()
        return file_extension in self.allowed_extensions
    
    def _schedule_voice_deletion(self, voice_id, expiry_time):
        """Schedule automatic deletion of voice message"""
        try:
            delay = (expiry_time - datetime.now()).total_seconds()
            
            if delay > 0:
                timer = Timer(delay, self._auto_delete_voice, args=[voice_id])
                timer.start()
                self.cleanup_timers[voice_id] = timer
                logging.info(f"Scheduled deletion for voice {voice_id} in {delay} seconds")
            else:
                # Already expired, delete immediately
                self._auto_delete_voice(voice_id)
                
        except Exception as e:
            logging.error(f"Error scheduling voice deletion: {str(e)}")
    
    def _auto_delete_voice(self, voice_id):
        """Automatically delete expired voice message"""
        try:
            voice_msg = self.mongo.db.voice_messages.find_one({"voice_id": voice_id})
            
            if voice_msg:
                # Delete file
                if os.path.exists(voice_msg['file_path']):
                    os.remove(voice_msg['file_path'])
                    logging.info(f"Deleted expired voice file: {voice_msg['file_path']}")
                
                # Mark as expired in database (keep metadata for reference)
                self.mongo.db.voice_messages.update_one(
                    {"voice_id": voice_id},
                    {"$set": {"is_expired": True, "expired_at": datetime.now()}}
                )
                
                logging.info(f"Voice message {voice_id} expired and deleted")
            
            # Clean up timer reference
            if voice_id in self.cleanup_timers:
                del self.cleanup_timers[voice_id]
                
        except Exception as e:
            logging.error(f"Error in auto-delete voice: {str(e)}")
    
    def _cleanup_expired_voices(self):
        """Clean up any voices that should have expired during server downtime"""
        try:
            expired_voices = self.mongo.db.voice_messages.find({
                "expiry_time": {"$lt": datetime.now()},
                "is_expired": False
            })
            
            for voice_msg in expired_voices:
                self._auto_delete_voice(voice_msg['voice_id'])
                
        except Exception as e:
            logging.error(f"Error in cleanup expired voices: {str(e)}")

def create_voice_routes(app, mongo):
    """Create voice message routes"""
    voice_handler = VoiceMessageHandler(mongo)
    
    @app.route('/api/voice/upload', methods=['POST'])
    def upload_voice():
        return voice_handler.upload_voice_message()
    
    @app.route('/api/voice/download/<voice_id>', methods=['GET'])
    def download_voice(voice_id):
        return voice_handler.download_voice_message(voice_id)
    
    @app.route('/api/voice/info/<voice_id>', methods=['GET'])
    def voice_info(voice_id):
        return voice_handler.get_voice_info(voice_id)
    
    @app.route('/api/voice/delete/<voice_id>', methods=['DELETE'])
    def delete_voice(voice_id):
        return voice_handler.delete_voice_message(voice_id)
    
    return voice_handler